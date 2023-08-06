'''This package contains base classes for wrappers that hide to the Appy
   developer the real classes used by the underlying web framework.'''

# ------------------------------------------------------------------------------
import os, os.path, mimetypes
import appy.pod
from appy.gen import Field, Search, Ref, String, WorkflowAnonymous
from appy.gen.indexer import defaultIndexes
from appy.gen.utils import createObject
from appy.px import Px
from appy.shared.utils import getOsTempFolder, executeCommand, \
                              normalizeString, sequenceTypes
from appy.shared.xml_parser import XmlMarshaller
from appy.shared.csv_parser import CsvMarshaller

# ------------------------------------------------------------------------------
class AbstractWrapper(object):
    '''Any real Appy-managed Zope object has a companion object that is an
       instance of this class.'''

    # Buttons for going to next/previous objects if this one is among bunch of
    # referenced or searched objects. currentNumber starts with 1.
    pxNavigateSiblings = Px('''
     <div if="req.get('nav', None)" var2="ni=ztool.getNavigationInfo(inPopup)">
      <!-- Go to the source URL (search or referred object) -->
      <a if="not inPopup and ni.sourceUrl" href=":ni.sourceUrl"><img
         var="gotoSource=_('goto_source');
              goBack=ni.backText and ('%s - %s' % (ni.backText, gotoSource)) \
                     or gotoSource"
         src=":url('gotoSource')" title=":goBack"/></a>

      <!-- Go to the first or previous page -->
      <a if="ni.firstUrl" href=":ni.firstUrl"><img title=":_('goto_first')"
         src=":url('arrowsLeft')"/></a><a
         if="ni.previousUrl" href=":ni.previousUrl"><img
         title=":_('goto_previous')" src=":url('arrowLeft')"/></a>

      <!-- Explain which element is currently shown -->
      <span class="discreet"> 
       <x>:ni.currentNumber</x> <b>//</b> 
       <x>:ni.totalNumber</x> </span>

      <!-- Go to the next or last page -->
      <a if="ni.nextUrl" href=":ni.nextUrl"><img title=":_('goto_next')"
         src=":url('arrowRight')"/></a><a
         if="ni.lastUrl" href=":ni.lastUrl"><img title=":_('goto_last')"
         src=":url('arrowsRight')"/></a>
     </div>''')

    pxNavigationStrip = Px('''
     <table width="100%">
      <tr>
       <!-- Breadcrumb -->
       <td var="sup=zobj.getSupBreadCrumb();
                breadcrumb=zobj.getBreadCrumb(inPopup=inPopup);
                sub=zobj.getSubBreadCrumb()" class="breadcrumb">
        <x if="sup">::sup</x>
        <x for="bc in breadcrumb" var2="nb=loop.bc.nb">
         <img if="nb != 0" src=":url('to')"/>
         <!-- Display only the title of the current object -->
         <span if="nb == len(breadcrumb)-1">:bc.title</span>
         <!-- Display a link for parent objects -->
         <a if="nb != len(breadcrumb)-1" href=":bc.url">:bc.title</a>
        </x>
        <x if="sub">::sub</x>
       </td>
       <!-- Object navigation -->
       <td align=":dright">:obj.pxNavigateSiblings</td>
      </tr>
     </table>
     <!-- Object phases and pages -->
     <x var="phases=zobj.getAppyPhases()"
        if="phases and zobj.mayNavigate()">:phases[0].pxAllPhases</x>''')

    # The template PX for all pages.
    pxTemplate = Px('''
     <html var="ztool=tool.o;                   user=tool.user;
                obj=obj or ztool.getHomeObject();
                zobj=obj and obj.o or None;
                isAnon=user.login=='anon';      app=ztool.getApp();
                appFolder=app.data;             url = ztool.getIncludeUrl;
                appName=ztool.getAppName();     _=ztool.translate;
                req=ztool.REQUEST;              resp=req.RESPONSE;
                dummy=setattr(req, 'pxContext', _ctx_);
                lang=ztool.getUserLanguage();   q=ztool.quote;
                layoutType=ztool.getLayoutType();
                inPopup=req.get('popup') == '1';
                showPortlet=not inPopup and ztool.showPortlet(obj, layoutType);
                dir=ztool.getLanguageDirection(lang);
                cfg=ztool.getProductConfig(True);
                dleft=(dir == 'ltr') and 'left' or 'right';
                dright=(dir == 'ltr') and 'right' or 'left';
                x=resp.setHeader('Content-type', ztool.xhtmlEncoding);
                x=resp.setHeader('Expires', 'Thu, 11 Dec 1975 12:05:00 GMT+2');
                x=resp.setHeader('Content-Language', lang)"
           dir=":ztool.getLanguageDirection(lang)">
     <head>
      <title>:_('app_name')</title>
      <link rel="icon" type="image/x-icon" href="/favicon.ico"/>
      <x for="name in ztool.getGlobalCssJs(dir)">
       <link if="name.endswith('.css')" rel="stylesheet" type="text/css"
             href=":url(name)"/>
       <script if="name.endswith('.js')" type="text/javascript"
               src=":url(name)"></script>
      </x>
     </head>
     <body style=":(cfg.skin == 'wide') and 'margin:0' or ''">
      <!-- Google Analytics stuff, if enabled -->
      <script var="gaCode=ztool.getGoogleAnalyticsCode()" if="gaCode"
              type="text/javascript">:gaCode</script>

      <!-- Popup for confirming an action -->
      <div id="confirmActionPopup" class="popup">
       <form id="confirmActionForm" method="post">
        <div align="center">
         <p id="appyConfirmText"></p>
         <input type="hidden" name="actionType"/>
         <input type="hidden" name="action"/>
         <div id="commentArea" align=":dleft"><br/>
          <span class="discreet">:_('workflow_comment')</span>
          <textarea name="comment" cols="30" rows="3"></textarea>
          <br/>
         </div><br/>
         <input type="button" onclick="doConfirm()" value=":_('yes')"/>
         <input type="button" onclick="closePopup('confirmActionPopup')"
               value=":_('no')"/>
        </div>
       </form>
      </div>

      <!-- Popup for uploading a file in a pod field -->
      <div id="uploadPopup" class="popup" align="center">
       <form id="uploadForm" name="uploadForm" enctype="multipart/form-data"
             method="post" action=":ztool.absolute_url() + '/doPod'">
        <input type="hidden" name="objectUid"/>
        <input type="hidden" name="fieldName"/>
        <input type="hidden" name="template"/>
        <input type="hidden" name="podFormat"/>
        <input type="hidden" name="action" value="upload"/>
        <input type="file" name="uploadedFile"/><br/><br/>
        <input type="submit" value=":_('object_save')"/>
        <input type="button" onclick="closePopup('uploadPopup')"
               value=":_('object_cancel')"/>
       </form>
      </div>

      <!-- Popup for reinitializing the password -->
      <div id="askPasswordReinitPopup" class="popup"
           if="isAnon and ztool.showForgotPassword()">
       <form id="askPasswordReinitForm" method="post"
             action=":ztool.absolute_url() + '/askPasswordReinit'">
        <div align="center">
         <p>:_('app_login')</p>
         <input type="text" size="35" name="login" id="login" value=""/>
         <br/><br/>
         <input type="button" onclick="doAskPasswordReinit()"
                value=":_('ask_password_reinit')"/>
         <input type="button" onclick="closePopup('askPasswordReinitPopup')"
                value=":_('object_cancel')"/>
        </div>
       </form>
      </div>

      <!-- Popup for displaying an error message (~JS alert()) -->
      <div id="alertPopup" class="popup">
       <img src=":url('warningBig')" align=":dleft" style="margin-right: 10px"/>
       <p id="appyAlertText" style="margin-bottom: 15px"></p>
       <div align="center">
        <input type="button" onclick="closePopup('alertPopup')"
               value=":_('appy_ok')"/>
       </div>
      </div>

      <!-- Popup containing the Appy iframe -->
      <div id="iframePopup" class="popup" if="not inPopup"
           style="background-color: #fbfbfb">
       <img align=":dright" src=":url('close')" class="clickable"
            onclick="closePopup('iframePopup')"/>
       <iframe id="appyIFrame" name="appyIFrame" frameborder="0"></iframe>
      </div>

      <table class=":(cfg.skin == 'wide') and 'mainWide main' or 'main'"
             align="center" cellpadding="0">
       <tr class="top" if="not inPopup">
        <!-- Top banner -->
        <td var="bannerName=(dir == 'ltr') and 'banner' or 'bannerrtl'"
            style=":url(bannerName, bg=True) + '; background-repeat:no-repeat;\
                   position:relative'">
         <!-- Logo (transparent clickable zone by default) -->
         <div align=":dleft" style="position: absolute"><a href="/">
          <img src=":url('logo')"/></a></div>

         <!-- Top links -->
         <div style="margin-top: 4px" align=":dright">
          <!-- Custom links -->
          <x>:tool.pxLinks</x>

          <!-- Top-level pages -->
          <a for="page in tool.pages" class="pageLink"
             href=":page.url">:page.title</a>

          <!-- Connect link if discreet login -->
          <a if="isAnon and cfg.discreetLogin" id="loginLink" name="loginLink"
             onclick="showLoginForm()"
             class="pageLink clickable">:_('app_connect')</a>

          <!-- Language selector -->
          <select if="ztool.showLanguageSelector()" class="pageLink"
                  var2="languages=ztool.getLanguages();
                       defaultLanguage=languages[0]"
                  onchange=":'switchLanguage(this,%s)' % q(ztool.getSiteUrl())">
           <option for="lg in languages" value=":lg"
                   selected=":lang == lg">:ztool.getLanguageName(lg)</option>
          </select>
         </div>
        </td>
       </tr>

       <!-- The message strip -->
       <tr height="0px">
        <td><div style="position:relative">:tool.pxMessage</div></td>
       </tr>

       <!-- The user strip -->
       <tr height=":cfg.discreetLogin and '5px' or '28px'" if="not inPopup">
        <td>
         <table class="userStrip">
          <tr>
           <!-- The user login form for anonymous users -->
           <td align="center"
               if="isAnon and ('/temp_folder/' not in req['ACTUAL_URL'])">
            <form id="loginForm" name="loginForm" method="post" class="login"
                  action=":tool.url + '/performLogin'">
             <input type="hidden" name="js_enabled" id="js_enabled" value="0"/>
             <input type="hidden" name="cookies_enabled" id="cookies_enabled"
                    value=""/>
             <input type="hidden" name="login_name" id="login_name" value=""/>
             <input type="hidden" name="pwd_empty" id="pwd_empty" value="0"/>
             <!-- Login fields directly shown or not depending on
                  discreetLogin. -->
             <span id="loginFields" name="loginFields"
                   style=":cfg.discreetLogin and 'display:none' or \
                           'display:block'">
              <span class="userStripText">:_('app_login')</span>
              <input type="text" name="__ac_name" id="__ac_name" value=""
                     style="width: 142px"/>&nbsp;
              <span class="userStripText">:_('app_password')</span>
              <input type="password" name="__ac_password" id="__ac_password"
                     style="width: 142px"/>
              <input type="submit" name="submit" onclick="setLoginVars()"
                     var="label=_('app_connect')" value=":label" alt=":label"/>
              <!-- Forgot password? -->
              <a if="ztool.showForgotPassword()"
                 href="javascript: openPopup('askPasswordReinitPopup')"
                 class="lostPassword">:_('forgot_password')</a>
             </span>
            </form>
           </td>

           <!-- User info and controls for authenticated users -->
           <td if="not isAnon">
            <table class="buttons" width="99%">
             <tr>
              <td>
               <!-- Config -->
               <a if="user.has_role('Manager')" href=":tool.url"
                  title=":_('%sTool' % appName)">
                <img src=":url('appyConfig.gif')"/></a>
               <!-- Additional icons -->
               <x>:tool.pxIcons</x>
               <!-- Log out -->
               <a href=":tool.url + '/performLogout'" title=":_('app_logout')">
                <img src=":url('logout.gif')"/></a>
              </td>
              <td class="userStripText" var="userInfo=ztool.getUserLine()"
                  align=":dright">
               <span>:userInfo[0]</span>
               <a if="userInfo[1]"
                  href=":userInfo[1]"><img src=":url('edit')"/></a>
              </td>
             </tr>
            </table>
           </td>
          </tr>
         </table>
        </td>
       </tr>
       <tr valign="top">
        <td>
         <table width="100%" height="100%" cellpadding="0" cellspacing="0">
          <tr valign="top">
           <!-- The portlet -->
           <td if="showPortlet" class="portlet">:tool.pxPortlet</td>
           <td class="content">
            <table cellpadding="0" cellspacing="0" width="100%">
             <!-- Navigation strip -->
              <tr if="zobj and (layoutType != 'edit')"
                  height="26px"><td>:obj.pxNavigationStrip</td>
              </tr>
              <!-- Page content -->
              <tr><td>:content</td></tr>
            </table>
           </td>
          </tr>
         </table>
        </td>
       </tr>
       <!-- Footer -->
       <tr height="26px" if="not inPopup"><td>:tool.pxFooter</td></tr>
      </table>
     </body>
    </html>''', prologue=Px.xhtmlPrologue)

    # --------------------------------------------------------------------------
    # PXs for rendering graphical elements tied to a given object
    # --------------------------------------------------------------------------

    # This PX displays an object's history.
    pxHistory = Px('''
     <x var="startNumber=req.get('startNumber', 0);
             startNumber=int(startNumber);
             batchSize=int(req.get('maxPerPage', 5));
             historyInfo=zobj.getHistory(startNumber,batchSize=batchSize)"
        if="historyInfo.events"
        var2="objs=historyInfo.events;
              totalNumber=historyInfo.totalNumber;
              batchNumber=len(objs);
              ajaxHookId='appyHistory';
              navBaseCall='askObjectHistory(%s,%s,%d,**v**)' % \
                (q(ajaxHookId), q(zobj.absolute_url()), batchSize)">

      <!-- Navigate between history pages -->
      <x>:tool.pxNavigate</x>
      <!-- History -->
      <table width="100%" class="history">
       <tr>
        <th align=":dleft">:_('object_action')</th>
        <th align=":dleft">:_('object_author')</th>
        <th align=":dleft">:_('action_date')</th>
        <th align=":dleft">:_('action_comment')</th>
       </tr>
       <tr for="event in objs"
           var2="rhComments=event.get('comments', None);
                 state=event.get('review_state', None);
                 action=event['action'];
                 isDataChange=action == '_datachange_'"
           class=":loop.event.odd and 'even' or 'odd'" valign="top">
        <td if="isDataChange">
         <x>:_('data_change')</x>
         <img if="user.has_role('Manager')" class="clickable"
              src=":url('delete')"
              onclick=":'onDeleteEvent(%s,%s)' % \
                        (q(zobj.id), q(event['time']))"/>
        </td>
        <td if="not isDataChange">:_(zobj.getWorkflowLabel(action))</td>
        <td var="actorId=event.get('actor')">
         <x if="not actorId">?</x>
         <x if="actorId">:ztool.getUserName(actorId)</x>
        </td>
        <td>:ztool.formatDate(event['time'], withHour=True)</td>
        <td if="not isDataChange">
         <x if="rhComments">::zobj.formatText(rhComments)</x>
         <x if="not rhComments">-</x>
        </td>
        <td if="isDataChange">
         <!-- Display the previous values of the fields whose value were
              modified in this change. -->
         <table class="appyChanges" width="100%">
          <tr>
           <th align=":dleft" width="30%">:_('modified_field')</th>
           <th align=":dleft" width="70%">:_('previous_value')</th>
          </tr>
          <tr for="change in event['changes'].items()" valign="top"
              var2="field=zobj.getAppyType(change[0])">
           <td>::_(field.labelId)</td>
           <td>::change[1][0]</td>
          </tr>
         </table>
        </td>
       </tr>
      </table>
     </x>''')

    pxTransitions = Px('''
     <form var="transitions=targetObj.getTransitions()" if="transitions"
           var2="formId='trigger_%s' % targetObj.id" method="post"
           id=":formId" action=":targetObj.absolute_url() + '/do'">
      <input type="hidden" name="action" value="Trigger"/>
      <input type="hidden" name="transition"/>
      <!-- Input field for storing the comment coming from the popup -->
      <textarea id="comment" name="comment" cols="30" rows="3"
                style="display:none"></textarea>
      <table cellpadding="0" cellspacing="0">
       <tr valign="middle">
        <td align=":dright" for="transition in transitions">
         <!-- Render a transition or a group of transitions. -->
         <x if="transition.type == 'transition'">:transition.pxView</x>
         <x if="transition.type == 'group'"
            var2="uiGroup=transition">:uiGroup.px</x>
        </td>
       </tr>
      </table>
     </form>''')

    # Displays header information about an object: title, workflow-related info,
    # history...
    pxHeader = Px('''
     <div if="not zobj.isTemporary()"
          var2="hasHistory=zobj.hasHistory();
                historyMaxPerPage=req.get('maxPerPage', 5);
                historyExpanded=req.get('appyHistory','collapsed')=='expanded';
                creator=zobj.Creator()">
      <table width="100%" class="summary" cellpadding="0" cellspacing="0">
       <tr>
        <td colspan="2" class="by">
         <!-- Plus/minus icon for accessing history -->
         <x if="hasHistory">
          <img class="clickable" onclick="toggleCookie('appyHistory')"
             src=":historyExpanded and url('collapse.gif') or url('expand.gif')"
             align=":dleft" id="appyHistory_img" style="padding-right:4px"/>
          <x>:_('object_history')</x> &mdash;
         </x>

         <!-- Creator and last modification date -->
         <x>:_('object_created_by')</x> <x>:ztool.getUserName(creator)</x>
         
         <!-- Creation and last modification dates -->
         <x>:_('object_created_on')</x>
         <x var="creationDate=zobj.Created();
                 modificationDate=zobj.Modified()">
          <x>:ztool.formatDate(creationDate, withHour=True)</x>
          <x if="modificationDate != creationDate">&mdash;
           <x>:_('object_modified_on')</x>
           <x>:ztool.formatDate(modificationDate, withHour=True)</x>
          </x>
         </x>

         <!-- State -->
         <x if="zobj.showState()">&mdash;
          <x>:_('workflow_state')</x> : <b>:_(zobj.getWorkflowLabel())</b>
         </x>
        </td>
       </tr>

       <!-- Object history -->
       <tr if="hasHistory">
        <td colspan="2">
         <span id="appyHistory"
               style=":historyExpanded and 'display:block' or 'display:none'">
          <div var="ajaxHookId=zobj.id + '_history'" id=":ajaxHookId">
           <script type="text/javascript">::'askObjectHistory(%s,%s,%d,0)' % \
             (q(ajaxHookId), q(zobj.absolute_url()), \
              historyMaxPerPage)</script>
          </div>
         </span>
        </td>
       </tr>
      </table>
     </div>''')

    # Shows the range of buttons (next, previous, save,...) and the workflow
    # transitions for a given object.
    pxButtons = Px('''
     <table cellpadding="2" cellspacing="0" style="margin-top: 7px"
            var="previousPage=phaseObj.getPreviousPage(page)[0];
                 nextPage=phaseObj.getNextPage(page)[0];
                 isEdit=layoutType == 'edit';
                 mayAct=not isEdit and zobj.mayAct();
                 pageInfo=phaseObj.pagesInfo[page]">
      <tr valign="top">
       <!-- Refresh -->
       <td if="zobj.isDebug()">
        <a href=":zobj.getUrl(mode=layoutType, page=page, refresh='yes', \
                              inPopup=inPopup)">
         <img title="Refresh" style="vertical-align:top" src=":url('refresh')"/>
        </a>
       </td>
       <!-- Previous -->
       <td if="previousPage and pageInfo.showPrevious"
           var2="label=_('page_previous');
                 buttonWidth=ztool.getButtonWidth(label)">
        <!-- Button on the edit page -->
        <x if="isEdit">
         <input type="button" class="button" value=":label"
                onClick="submitAppyForm('previous')"
                style=":'%s; %s' % (url('previous', bg=True), buttonWidth)"/>
         <input type="hidden" name="previousPage" value=":previousPage"/>
        </x>
        <!-- Button on the view page -->
        <input if="not isEdit" type="button" class="button" value=":label"
               style=":'%s; %s' % (url('previous', bg=True), buttonWidth)"
               onclick=":'goto(%s)' % q(zobj.getUrl(page=previousPage, \
                                                    inPopup=inPopup))"/>
       </td>

       <!-- Save -->
       <td if="isEdit and pageInfo.showSave">
        <input type="button" class="button" onClick="submitAppyForm('save')"
               var="label=_('object_save')" value=":label"
               style=":'%s; %s' % (url('save', bg=True), \
                                   ztool.getButtonWidth(label))" />
       </td>
       <!-- Cancel -->
       <td if="isEdit and pageInfo.showCancel">
        <input type="button" class="button" onClick="submitAppyForm('cancel')"
               var="label=_('object_cancel')" value=":label"
               style=":'%s; %s' % (url('cancel', bg=True), \
                                   ztool.getButtonWidth(label))"/>
       </td>
       <td if="not isEdit"
           var2="locked=zobj.isLocked(user, page);
                 editable=pageInfo.showOnEdit and pageInfo.showEdit and \
                          mayAct and zobj.mayEdit()">

        <!-- Edit -->
        <input type="button" class="button" if="editable and not locked"
               var="label=_('object_edit')" value=":label"
               style=":'%s; %s' % (url('edit', bg=True), \
                                   ztool.getButtonWidth(label))"
               onclick=":'goto(%s)' % q(zobj.getUrl(mode='edit', page=page, \
                                                    inPopup=inPopup))"/>

        <!-- Locked -->
        <a if="editable and locked">
         <img style="cursor: help"
              var="lockDate=ztool.formatDate(locked[1]);
                   lockMap={'user':ztool.getUserName(locked[0]), \
                            'date':lockDate};
                   lockMsg=_('page_locked', mapping=lockMap)"
              src=":url('lockedBig')" title=":lockMsg"/></a>
        <a if="editable and locked and user.has_role('Manager')">
         <img class="clickable" title=":_('page_unlock')"
              src=":url('unlockBig')"
              onclick=":'onUnlockPage(%s,%s)' % (q(zobj.id), q(page))"/></a>
       </td>

       <!-- Next -->
       <td if="nextPage and pageInfo.showNext"
           var2="label=_('page_next');
                 buttonWidth=ztool.getButtonWidth(label)">
        <!-- Button on the edit page -->
        <x if="isEdit">
         <input type="button" class="button" onClick="submitAppyForm('next')"
                style=":'%s; %s' % (url('next', bg=True), buttonWidth)"
                value=":label"/>
         <input type="hidden" name="nextPage" value=":nextPage"/>
        </x>
        <!-- Button on the view page -->
        <input if="not isEdit" type="button" class="button" value=":label"
               style=":'%s; %s' % (url('next', bg=True), buttonWidth)"
               onclick=":'goto(%s)' % q(zobj.getUrl(page=nextPage, \
                                                    inPopup=inPopup))"/>
       </td>

       <!-- Workflow transitions -->
       <td var="targetObj=zobj; buttonsMode='normal'"
           if="mayAct and \
               targetObj.showTransitions(layoutType)">:obj.pxTransitions</td>
      </tr>
     </table>''')

    # Displays the fields of a given page for a given object.
    pxFields = Px('''
     <table width=":layout.width">
      <tr for="field in groupedFields">
       <td if="field.type == 'group'">:field.pxView</td>
       <td if="field.type != 'group'">:field.pxRender</td>
      </tr>
     </table>''')

    pxView = Px('''
     <x var="x=zobj.mayView(raiseError=True);
             errors=req.get('errors', {});
             layout=zobj.getPageLayout(layoutType);
             phaseObj=zobj.getAppyPhases(currentOnly=True, layoutType='view');
             phase=phaseObj.name;
             cssJs={};
             page=req.get('page',None) or zobj.getDefaultViewPage();
             x=zobj.removeMyLock(user, page);
             groupedFields=zobj.getGroupedFields(layoutType, page,cssJs=cssJs)">
      <x>:tool.pxPagePrologue</x>
      <x var="tagId='pageLayout'; tagName=''; tagCss='';
              layoutTarget=obj">:tool.pxLayoutedObject</x>
      <x>:tool.pxPageBottom</x>
     </x>''', template=pxTemplate, hook='content')

    pxEdit = Px('''
     <x var="x=zobj.mayEdit(raiseError=True, permOnly=zobj.isTemporary());
             errors=req.get('errors', {});
             layout=zobj.getPageLayout(layoutType);
             cssJs={};
             phaseObj=zobj.getAppyPhases(currentOnly=True, \
                                         layoutType=layoutType);
             phase=phaseObj.name;
             page=req.get('page', None) or zobj.getDefaultEditPage();
             x=zobj.setLock(user, page);
             confirmMsg=req.get('confirmMsg', None);
             groupedFields=zobj.getGroupedFields(layoutType,page, cssJs=cssJs)">
      <x>:tool.pxPagePrologue</x>
      <!-- Warn the user that the form should be left via buttons -->
      <script type="text/javascript">protectAppyForm()</script>
      <form id="appyForm" name="appyForm" method="post"
            enctype="multipart/form-data" action=":zobj.absolute_url()+'/do'">
       <input type="hidden" name="action" value="Update"/>
       <input type="hidden" name="button" value=""/>
       <input type="hidden" name="popup" value=":inPopup and '1' or '0'"/>
       <input type="hidden" name="page" value=":page"/>
       <input type="hidden" name="nav" value=":req.get('nav', None)"/>
       <input type="hidden" name="confirmed" value="False"/>
       <x var="tagId='pageLayout'; tagName=''; tagCss='';
               layoutTarget=obj">:tool.pxLayoutedObject</x>
      </form>
      <script type="text/javascript"
              if="confirmMsg">::'askConfirm(%s,%s,%s)' % \
             (q('script'), q('postConfirmedEditForm()'), q(confirmMsg))</script>
      <x>:tool.pxPageBottom</x>
     </x>''', template=pxTemplate, hook='content')

    # PX called via asynchronous requests from the browser. Keys "Expires" and
    # "CacheControl" are used to prevent IE to cache returned pages (which is
    # the default IE behaviour with Ajax requests).
    pxAjax = Px('''
     <x var="zobj=obj.o;    ztool=tool.o;    user=tool.user;
             isAnon=user.login == 'anon';    app=ztool.getApp();
             appFolder=app.data;             url = ztool.getIncludeUrl;
             appName=ztool.getAppName();     _=ztool.translate;
             req=ztool.REQUEST;              resp=req.RESPONSE;
             dummy=setattr(req, 'pxContext', _ctx_);
             lang=ztool.getUserLanguage();   q=ztool.quote;
             action=req.get('action', None);
             px=req['px'].split(':');
             inPopup=req.get('popup') == '1';
             className=(len(px) == 3) and px[0] or None;
             field=className and zobj.getAppyType(px[1], className) or None;
             field=(len(px) == 2) and zobj.getAppyType(px[0]) or field;
             dir=ztool.getLanguageDirection(lang);
             dleft=(dir == 'ltr') and 'left' or 'right';
             dright=(dir == 'ltr') and 'right' or 'left';
             x=resp.setHeader('Content-type', ztool.xhtmlEncoding);
             x=resp.setHeader('Expires', 'Thu, 11 Dec 1975 12:05:00 GMT+2');
             x=resp.setHeader('Content-Language', lang);
             x=resp.setHeader('CacheControl', 'no-cache')">

      <!-- If an action is defined, execute it on p_zobj or on p_field. -->
      <x if="action and not field" var2="x=getattr(zobj, action)()"></x>
      <x if="action and field" var2="x=getattr(field, action)(zobj)"></x>

      <!-- Then, call the PX on p_obj or on p_field. -->
      <x if="not field">:getattr(obj, px[0])</x>
      <x if="field">:getattr(field, px[-1])</x>
     </x>''')

    # --------------------------------------------------------------------------
    # Class methods
    # --------------------------------------------------------------------------
    @classmethod
    def _getParentAttr(klass, attr):
        '''Gets value of p_attr on p_klass base classes (if this attr exists).
           Scan base classes in the reverse order as Python does. Used by
           classmethod m_getWorkflow below. Scanning base classes in reverse
           order allows user-defined elements to override default Appy
           elements.'''
        i = len(klass.__bases__) - 1
        res = None
        while i >= 0:
            res = getattr(klass.__bases__[i], attr, None)
            if res: return res
            i -= 1

    @classmethod
    def getWorkflow(klass):
        '''Returns the workflow tied to p_klass.'''
        res = klass._getParentAttr('workflow')
        # Return a default workflow if no workflow was found.
        if not res: res = WorkflowAnonymous
        return res

    @classmethod
    def getIndexes(klass, includeDefaults=True):
        '''Returns a dict whose keys are the names of the indexes that are
           applicable to instances of this class, and whose values are the
           (Zope) types of those indexes.'''
        # Start with the standard indexes applicable for any Appy class.
        if includeDefaults:
            res = defaultIndexes.copy()
        else:
            res = {}
        # Add the indexed fields found on this class
        for field in klass.__fields__:
            if not field.indexed or (field.name == 'title'): continue
            n = field.name
            indexName = 'get%s%s' % (n[0].upper(), n[1:])
            res[indexName] = field.getIndexType()
        return res

    # --------------------------------------------------------------------------
    # Instance methods
    # --------------------------------------------------------------------------
    def __init__(self, o): self.__dict__['o'] = o
    def appy(self): return self

    def __setattr__(self, name, value):
        appyType = self.o.getAppyType(name)
        if not appyType:
            raise 'Attribute "%s" does not exist.' % name
        appyType.store(self.o, value)

    def __getattribute__(self, name):
        '''Gets the attribute named p_name. Lot of cheating here.'''
        if name == 'o': return object.__getattribute__(self, name)
        elif name == 'tool': return self.o.getTool().appy()
        elif name == 'request':
            # The request may not be present, ie if we are at Zope startup.
            res = getattr(self.o, 'REQUEST', None)
            if res != None: return res
            return self.o.getProductConfig().fakeRequest
        elif name == 'session': return self.o.REQUEST.SESSION
        elif name == 'typeName': return self.__class__.__bases__[-1].__name__
        elif name == 'id': return self.o.id
        elif name == 'uid': return self.o.id
        elif name == 'klass': return self.__class__.__bases__[-1]
        elif name == 'created': return self.o.created
        elif name == 'creator': return self.o.creator
        elif name == 'modified': return self.o.modified
        elif name == 'url': return self.o.absolute_url()
        elif name == 'state': return self.o.State()
        elif name == 'stateLabel':
            return self.o.translate(self.o.getWorkflowLabel())
        elif name == 'history':
            o = self.o
            key = o.workflow_history.keys()[0]
            return o.workflow_history[key]
        elif name == 'user': return self.o.getTool().getUser()
        elif name == 'fields': return self.o.getAllAppyTypes()
        elif name == 'siteUrl': return self.o.getTool().getSiteUrl()
        # Now, let's try to return a real attribute.
        res = object.__getattribute__(self, name)
        # If we got an Appy field, return its value for this object
        if isinstance(res, Field):
            o = self.o
            if isinstance(res, Ref):
                return res.getValue(o, noListIfSingleObj=True)
            else:
                return res.getValue(o)
        return res

    def __repr__(self):
        return '<%s at %s>' % (self.klass.__name__, id(self))

    def __cmp__(self, other):
        if other: return cmp(self.o, other.o)
        return 1

    def _getCustomMethod(self, methodName):
        '''See docstring of _callCustom below.'''
        if len(self.__class__.__bases__) > 1:
            # There is a custom user class
            custom = self.__class__.__bases__[-1]
            if custom.__dict__.has_key(methodName):
                return custom.__dict__[methodName]

    def _callCustom(self, methodName, *args, **kwargs):
        '''This wrapper implements some methods like "validate" and "onEdit".
           If the user has defined its own wrapper, its methods will not be
           called. So this method allows, from the methods here, to call the
           user versions.'''
        custom = self._getCustomMethod(methodName)
        if custom: return custom(self, *args, **kwargs)

    def getField(self, name): return self.o.getAppyType(name)
    def getLabel(self, name, type='field'):
        '''Gets the translated label of field named p_name. If p_type is
           "workflow", p_name denotes a workflow state or transition, not a
           field.'''
        o = self.o
        if type == 'field': return o.translate(o.getAppyType(name).labelId)
        elif type == 'workflow': return o.translate(o.getWorkflowLabel(name))

    def isEmpty(self, name):
        '''Returns True if value of field p_name is considered as being
           empty.'''
        obj = self.o
        if hasattr(obj.aq_base, name):
            field = obj.getAppyType(name)
            return field.isEmptyValue(getattr(obj, name))
        return True

    def link(self, fieldName, obj):
        '''This method links p_obj (which can be a list of objects) to this one
           through reference field p_fieldName.'''
        return self.getField(fieldName).linkObject(self.o, obj)

    def unlink(self, fieldName, obj):
        '''This method unlinks p_obj (which can be a list of objects) from this
           one through reference field p_fieldName.'''
        return self.getField(fieldName).unlinkObject(self.o, obj)

    def sort(self, fieldName, sortKey='title', reverse=False):
        '''Sorts referred elements linked to p_self via p_fieldName according
           to a given p_sortKey which must be an attribute set on referred
           objects ("title", by default).'''
        refs = getattr(self.o, fieldName, None)
        if not refs: return
        tool = self.tool
        # refs is a PersistentList: param "key" is not available. So perform the
        # sort on the real list and then indicate that the persistent list has
        # changed (the ZODB way).
        refs.data.sort(key=lambda x: getattr(tool.getObject(x), sortKey),
                       reverse=reverse)
        refs._p_changed = 1

    def create(self, fieldNameOrClass, noSecurity=False, **kwargs):
        '''If p_fieldNameOrClass is the name of a field, this method allows to
           create an object and link it to the current one (self) through
           reference field named p_fieldName.
           If p_fieldNameOrClass is a class from the gen-application, it must
           correspond to a root class and this method allows to create a
           root object in the application folder.'''
        isField = isinstance(fieldNameOrClass, basestring)
        tool = self.tool.o
        # Determine the class of the object to create
        if isField:
            fieldName = fieldNameOrClass
            appyType = self.o.getAppyType(fieldName)
            portalType = tool.getPortalType(appyType.klass)
        else:
            klass = fieldNameOrClass
            portalType = tool.getPortalType(klass)
        # Determine object id
        if kwargs.has_key('id'):
            objId = kwargs['id']
            del kwargs['id']
        else:
            objId = tool.generateUid(portalType)
        # Determine if object must be created from external data
        externalData = None
        if kwargs.has_key('_data'):
            externalData = kwargs['_data']
            del kwargs['_data']
        # Where must I create the object?
        if not isField:
            folder = tool.getPath('/data')
        else:
            folder = self.o.getCreateFolder()
            if not noSecurity:
                # Check that the user can edit this field.
                appyType.checkAdd(self.o)
        # Create the object
        zopeObj = createObject(folder, objId, portalType, tool.getAppName(),
                               noSecurity=noSecurity)
        appyObj = zopeObj.appy()
        # Set object attributes
        for attrName, attrValue in kwargs.iteritems():
            setattr(appyObj, attrName, attrValue)
        if isField:
            # Link the object to this one
            appyType.linkObject(self.o, zopeObj)
        # Call custom initialization
        if externalData: param = externalData
        else: param = True
        if hasattr(appyObj, 'onEdit'): appyObj.onEdit(param)
        zopeObj.reindex()
        return appyObj

    def freeze(self, fieldName, template=None, format='pdf', noSecurity=True,
               freezeOdtOnError=True):
        '''This method freezes the content of pod field named p_fieldName, for
           the given p_template (several templates can be given in
           podField.template), in the given p_format ("pdf" by default).'''
        field = self.o.getAppyType(fieldName)
        if field.type!= 'Pod': raise Exception('Cannot freeze non-Pod field.')
        return field.freeze(self, template, format, noSecurity=noSecurity,
                            freezeOdtOnError=freezeOdtOnError)

    def unfreeze(self, fieldName, template=None, format='pdf', noSecurity=True):
        '''This method unfreezes a pod field.'''
        field = self.o.getAppyType(fieldName)
        if field.type!= 'Pod': raise Exception('Cannot unfreeze non-Pod field.')
        field.unfreeze(self, template, format, noSecurity=noSecurity)

    def delete(self):
        '''Deletes myself.'''
        self.o.delete()

    def translate(self, label, mapping={}, domain=None, language=None,
                  format='html'):
        '''Check documentation of self.o.translate.'''
        return self.o.translate(label, mapping, domain, language=language,
                                format=format)

    def do(self, name, comment='', doAction=True, doNotify=True, doHistory=True,
           noSecurity=False):
        '''Triggers on p_self a transition named p_name programmatically.'''
        o = self.o
        wf = o.getWorkflow()
        tr = getattr(wf, name, None)
        if not tr or (tr.__class__.__name__ != 'Transition'):
            raise Exception('Transition "%s" not found.' % name)
        return tr.trigger(name, o, wf, comment, doAction=doAction,
                          doNotify=doNotify, doHistory=doHistory, doSay=False,
                          noSecurity=noSecurity)

    def log(self, message, type='info'): return self.o.log(message, type)
    def say(self, message, type='info'): return self.o.say(message, type)

    def normalize(self, s, usage='fileName'):
        '''Returns a version of string p_s whose special chars have been
           replaced with normal chars.'''
        return normalizeString(s, usage)

    def search(self, klass, sortBy='', sortOrder='asc', maxResults=None,
               noSecurity=False, **fields):
        '''Searches objects of p_klass. p_sortBy must be the name of an indexed
           field (declared with indexed=True); p_sortOrder can be "asc"
           (ascending, the defaut) or "desc" (descending); every param in
           p_fields must take the name of an indexed field and take a possible
           value of this field. You can optionally specify a maximum number of
           results in p_maxResults. If p_noSecurity is specified, you get all
           objects, even if the logged user does not have the permission to
           view it.'''
        # Find the content type corresponding to p_klass
        tool = self.tool.o
        contentType = tool.getPortalType(klass)
        # Create the Search object
        search = Search('customSearch', sortBy=sortBy, sortOrder=sortOrder,
                        **fields)
        if not maxResults:
            maxResults = 'NO_LIMIT'
            # If I let maxResults=None, only a subset of the results will be
            # returned by method executeResult.
        res = tool.executeQuery(contentType, search=search,
                                maxResults=maxResults, noSecurity=noSecurity)
        return [o.appy() for o in res.objects]

    def search1(self, *args, **kwargs):
        '''Identical to m_search above, but returns a single result (if any).'''
        res = self.search(*args, **kwargs)
        if res: return res[0]

    def count(self, klass, noSecurity=False, **fields):
        '''Identical to m_search above, but returns the number of objects that
           match the search instead of returning the objects themselves. Use
           this method instead of writing len(self.search(...)).'''
        tool = self.tool.o
        contentType = tool.getPortalType(klass)
        search = Search('customSearch', **fields)
        res = tool.executeQuery(contentType, search=search, brainsOnly=True,
                                noSecurity=noSecurity)
        if res: return res._len # It is a LazyMap instance
        else: return 0

    def countRefs(self, fieldName):
        '''Counts the number of objects linked to this one via Ref field
           p_fieldName.'''
        uids = getattr(self.o.aq_base, fieldName, None)
        if not uids: return 0
        return len(uids)

    def compute(self, klass, sortBy='', maxResults=None, context=None,
                expression=None, noSecurity=False, **fields):
        '''This method, like m_search and m_count above, performs a query on
           objects of p_klass. But in this case, instead of returning a list of
           matching objects (like m_search) or counting elements (like p_count),
           it evaluates, on every matching object, a Python p_expression (which
           may be an expression or a statement), and returns, if needed, a
           result. The result may be initialized through parameter p_context.
           p_expression is evaluated with 2 variables in its context: "obj"
           which is the currently walked object, instance of p_klass, and "ctx",
           which is the context as initialized (or not) by p_context. p_context
           may be used as
              (1) a variable or instance that is updated on every call to
                  produce a result;
              (2) an input variable or instance;
              (3) both.

           The method returns p_context, modified or not by evaluation of
           p_expression on every matching object.

           When you need to perform an action or computation on a lot of
           objects, use this method instead of doing things like
           
                    "for obj in self.search(MyClass,...)"
           '''
        tool = self.tool.o
        contentType = tool.getPortalType(klass)
        search = Search('customSearch', sortBy=sortBy, **fields)
        # Initialize the context variable "ctx"
        ctx = context
        for brain in tool.executeQuery(contentType, search=search, \
                 brainsOnly=True, maxResults=maxResults, noSecurity=noSecurity):
            # Get the Appy object from the brain
            if noSecurity: method = '_unrestrictedGetObject'
            else: method = 'getObject'
            exec 'obj = brain.%s().appy()' % method
            exec expression
        return ctx

    def reindex(self, fields=None, unindex=False):
        '''Asks a direct object reindexing. In most cases you don't have to
           reindex objects "manually" with this method. When an object is
           modified after some user action has been performed, Appy reindexes
           this object automatically. But if your code modifies other objects,
           Appy may not know that they must be reindexed, too. So use this
           method in those cases.
        '''
        if fields:
            # Get names of indexes from field names.
            indexes = [Search.getIndexName(name) for name in fields]
        else:
            indexes = None
        self.o.reindex(indexes=indexes, unindex=unindex)

    def export(self, at='string', format='xml', include=None, exclude=None):
        '''Creates an "exportable" version of this object. p_format is "xml" by
           default, but can also be "csv". If p_format is:
           * "xml", if p_at is "string", this method returns the XML version,
                    without the XML prologue. Else, (a) if not p_at, the XML
                    will be exported on disk, in the OS temp folder, with an
                    ugly name; (b) else, it will be exported at path p_at.
           * "csv", if p_at is "string", this method returns the CSV data as a
                    string. If p_at is an opened file handler, the CSV line will
                    be appended in it.
           If p_include is given, only fields whose names are in it will be
           included. p_exclude, if given, contains names of fields that will
           not be included in the result.
        '''
        if format == 'xml':
            # Todo: take p_include and p_exclude into account.
            # Determine where to put the result
            toDisk = (at != 'string')
            if toDisk and not at:
                at = getOsTempFolder() + '/' + self.o.id + '.xml'
            # Create the XML version of the object
            marshaller = XmlMarshaller(cdata=True, dumpUnicode=True,
                                       dumpXmlPrologue=toDisk,
                                       rootTag=self.klass.__name__)
            xml = marshaller.marshall(self.o, objectType='appy')
            # Produce the desired result
            if toDisk:
                f = file(at, 'w')
                f.write(xml.encode('utf-8'))
                f.close()
                return at
            else:
                return xml
        elif format == 'csv':
            if isinstance(at, basestring):
                marshaller = CsvMarshaller(include=include, exclude=exclude)
                return marshaller.marshall(self)
            else:
                marshaller = CsvMarshaller(at, include=include, exclude=exclude)
                marshaller.marshall(self)

    def historize(self, data):
        '''This method allows to add "manually" a "data-change" event into the
           object's history. Indeed, data changes are "automatically" recorded
           only when an object is edited through the edit form, not when a
           setter is called from the code.

           p_data must be a dictionary whose keys are field names (strings) and
           whose values are the previous field values.'''
        self.o.addDataChange(data)

    def getLastEvent(self, transition, notBefore=None):
        '''Gets, from the object history, the last occurrence of transition
           named p_transition. p_transition can be a list of names: in this
           case, it returns the most recent occurrence of those transitions. If
           p_notBefore is given, it corresponds to a kind of start transition
           for the search: we will not search in the history preceding the last
           occurrence of this transition.'''
        history = self.history
        i = len(history)-1
        while i >= 0:
            event = history[i]
            if notBefore and (event['action'] == notBefore): return
            if isinstance(transition, basestring):
                condition = event['action'] == transition
            else:
                condition = event['action'] in transition
            if condition: return event
            i -= 1

    def formatText(self, text, format='html'):
        '''Produces a representation of p_text into the desired p_format, which
           is 'html' by default.'''
        return self.o.formatText(text, format)

    def listStates(self):
        '''Lists the possible states for this object.'''
        res = []
        o = self.o
        workflow = o.getWorkflow()
        for name in dir(workflow):
            if getattr(workflow, name).__class__.__name__ != 'State': continue
            res.append((name, o.translate(o.getWorkflowLabel(name))))
        return res

    def path(self, name):
        '''Returns the absolute file name of file stored in File field p_nnamed
           p_name.'''
        v = getattr(self, name)
        if v: return v.getFilePath(self)

    def getIndexOf(self, name, obj):
        '''Returns, as an integer starting at 0, the position of p_obj within
           objects linked to p_self via field p_name.'''
        o = self.o
        return o.getAppyType(name).getIndexOf(o, obj.uid)

    def allows(self, permission, raiseError=False):
        '''Check doc @Mixin.allows.'''
        return self.o.allows(permission, raiseError=raiseError)

    def resetLocalRoles(self):
        '''Removes all local roles defined on this object, excepted local role
           Owner, granted to the item creator.'''
        from persistent.mapping import PersistentMapping
        localRoles = PersistentMapping({ self.o.creator: ['Owner'] })
        self.o.__ac_local_roles__ = localRoles
        return localRoles
# ------------------------------------------------------------------------------
