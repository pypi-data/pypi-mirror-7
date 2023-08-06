#
# Copyright (c) 2009, 2011, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from coils.net import DAVFolder, Protocol, EmptyFolder
from coils.core import \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_WORKFLOW_ADMIN, \
    OGO_ROLE_WORKFLOW_DEVELOPERS, \
    AuthenticatedContext

# DAV content providers
from groupware import \
    RootContactFolder, \
    CalendarFolder, \
    AccountsFolder, \
    TeamsFolder, \
    TasksFolder, \
    FavoritesFolder, \
    ProjectsFolder, \
    CabinetsFolder, \
    CollectionsFolder, \
    DocumentsFolder

from workflow import WorkflowFolder

DAV_ROOT_FOLDERS = {
    'Contacts': 'RootContactFolder',
    'Projects': 'ProjectsFolder',
    'Calendar': 'CalendarFolder',
    'Journal': 'EmptyFolder',
    'Collections': 'CollectionsFolder',
    'Cabinets': 'CabinetsFolder',
    'Users': 'AccountsFolder',
    'Tasks': 'TasksFolder',
    'Teams': 'TeamsFolder',
    'Favorites': 'FavoritesFolder',
    'Workflow': 'WorkflowFolder', }


class DAVRoot(DAVFolder, Protocol):
    '''The root of the DAV hierarchy.'''
    __pattern__ = ['^dav$', '^DAV$', ]
    __namespace__ = None
    __xmlrpc__ = False

    def __init__(self, parent, **params):
        DAVFolder.__init__(self, parent, 'dav', **params)
        DAVFolder.Root = self
        self.root = self

    def get_name(self):
        return 'dav'

    def _load_contents(self):
        self.init_context()
        for key in DAV_ROOT_FOLDERS.keys():
            classname = DAV_ROOT_FOLDERS[key]
            classclass = eval(classname)
            self.insert_child(
                key,
                classclass(
                    self,
                    key,
                    parameters=self.parameters,
                    request=self.request,
                    context=self.context,
                )
            )
        if (
            self.context.has_role(OGO_ROLE_SYSTEM_ADMIN) or
            self.context.has_role(OGO_ROLE_WORKFLOW_ADMIN) or
            self.context.has_role(OGO_ROLE_WORKFLOW_DEVELOPERS)
        ):
            project = self.context.run_command('project::get', id=7000, )
            if project:
                folder = self.context.run_command(
                    'project::get-root-folder',
                    project=project, )
                if folder:
                    self.insert_child(
                        'Administration',
                        DocumentsFolder(
                            self,
                            'Administration',
                            parameters=self.parameters,
                            request=self.request,
                            entity=folder,
                            context=self.context,
                        )
                    )
        return True

    def get_property_caldav_calendar_home_set(self):
        '''
        RFC4791 :
        urls = [
            self.request.user_agent.get_appropriate_href(
                '/dav/Calendar/Overview'),
            self.request.user_agent.get_appropriate_href(
                '/dav/Calendar/Personal') ]
        return u''.join(
            [  '<D:href>{0}</D:href>'.format(url) for url in urls ])
        '''
        url = self.get_appropriate_href('/dav/Calendar')
        return '<D:href>{0}</D:href>'.format(url)

    def get_property_caldav_calendar_user_address_set(self):
        '''
        RFC4791 : 9.2.3
        '''
        if isinstance(self.context, AuthenticatedContext):
            tmp = [self.context.account_object.get_company_value('email1'),
                   self.context.account_object.get_company_value('email2'),
                   self.context.account_object.get_company_value('email3'), ]
            tmp = [x.string_value for x in tmp if x]
            tmp = ['<D:href>mailto:{0}</D:href>'.
                   format(x.strip()) for x in tmp if x]
            return ''.join(tmp)
        return None

    def get_property_carddav_addressbook_home_set(self):
        return u'<D:href>/dav/Contacts</D:href>'
