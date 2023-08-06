#
# Copyright (c) 2011, 2012
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
import copy

EMBEDDED_TEST_STRING = 'SHAZAM-TEST_STRING'

DEFAULT_USER_AGENT = '148c9d0d669648ed8b8ed0292df478fd'

USER_AGENTS = {

    # Default / Base User Agent Definition
    '148c9d0d669648ed8b8ed0292df478fd':
       { 'name':      'default',
         'patterns':   [],
         'sessionsEnabled': False,
         'webdav':     { 'quoteDAVHref':      False,
                         'filenameAsDisplayName': False,  # Use the filename as the display name, for clients that confuse the two
                         'showProjectContactsFolder': True, # Enable/Disable showing the Contacts folder in a Project folder
                         'showProjectEnterprisesFolder': True, # Enable/Disable showing the Enterprise folder in a Project folder
                         'showProjectTasksFolder': True, # Enable/Disable showing the Tasks folder in a Project folder
                         'showProjectProjectsFolder': True, # Enable/Disable showing the Projects (sub-projects) folder in a Project folder
                         'showProjectDocumentsFolder': True, # Enable/Disable showing the Documents folder in a Project folder
                         'showProjectNotesFolder': True, # Enable/Disable showing the Notes folder in a Project folder
                         'showProjectVersionsFolder': False, # Enable/Disable showing the Versions folder in a Project folder
                         'folderContentType': 'unix/httpd-directory', # Mime-type for a collection/folder
                         'escapeGETs':            False,
                         'supports301':           True, # Does the client respond correctly to 301 responses
                         'supportsLocation':      True, # Does the client respond correct to Location: headers
                         'supportsMEMOs':         False, # Does the client properly handle Memo (VJOURNAL) objects
                         'absoluteHrefs':         False, # Does the client require HREF values to be absolute
                         'portInAbsoluteHref':    False, # Does the client recognize port numbers in absolute HREFs
                         'hideLockRoot':          False,
                         'principalURL':          None,  # A NULL value leaves it at the default value for the bundle
                         'showContactsAllFolder':   True,  # Enable/Disable the All Contacts folder
                         'showContactsUsersFolder': True,  # Enable/Disable the Users folder under Contacts
                         'defaultPropeties':
                             [ ( u'name',             u'DAV:',                           u'webdav', 'D:name' ),
                               ( u'href',             u'DAV:',                           u'webdav', 'D:href' ),
                               ( u'getcontenttype',   u'DAV:',                           u'webdav', 'D:getcontenttype' ),
                               ( u'contentclass',     u'DAV:',                           u'webdav', 'D:contentclass' ),
                               ( u'getlastmodified',  u'DAV:',                           u'webdav', 'D:getlastmodified' ),
                               ( u'getcontentlength', u'DAV:',                           u'webdav', 'D:getcontentlength' ),
                               ( u'iscollection',     u'DAV:',                           u'webdav', 'D:iscollection' ),
                               ( u'displayname',      u'DAV:',                           u'webdav', 'D:displayname' ),
                               ( u'getctag',          u'urn:ietf:params:xml:ns:caldav', u'caldav', 'C:getctag' ),
                               ( u'resourcetype',     u'DAV:',                           u'webdav', 'D:resourcetype' ) ],
                        'defaultNamespaces': { 'A': 'http://apache.org/dav/props/',
                                               'B': 'http://icewarp.com/ns/',
                                               'C': 'urn:ietf:params:xml:ns:caldav',
                                               'D': 'DAV:',
                                               'E': 'urn:ietf:params:xml:ns:carddav',
                                               'G': 'http://groupdav.org/' } },
         'jsonrpc':    { },
         'xmlrpc':     { 'allowNone': False, },
         'vcard':       { 'setVoiceAttrInTel': True,
                          'setCoilsTypeInTel': True,
                          'telTypeMap': { '10_fax':         { 'types': ['fax','work'],    'voice': False  },
                                          '01_tel':         { 'types': ['work', 'pref' ], 'voice': True   },
                                          '03_tel_funk':    { 'types': ['cell'],          'voice': True   },
                                          '05_tel_private': { 'types': ['home'],          'voice': True,  },
                                          '30_pager':       { 'types': [ 'pager' ],       'voice': False  } },
                          'setCoilsTypeInAdr': True, # Encode the OGo address type in VCARD ADR properties
                          'adrTypeMap': { 'private':        { 'types': [ 'home' ] },
                                          'mailing':        { 'types': [ 'work', 'pref' ] },
                                          'bill':           { 'types': [ 'work', 'pref' ] },
                                          'shipto':         { 'types': [ 'work' ] } },
                          'includeObjectPropertes': False, # Encode the OGo object properties in VCARDs
                          'includeCoilsXAttributes': False, # Encode the OGo company values in VCARDs
                          'includeCompanyValues': False, # Encode the OGo company values in VCARDs
                        },
         'icalendar':  { 'includeAttachments': False,  # includeAttachments: False, inline, link
                       },
         'omphalos':   { 'associativeLists': False, # Use associate lists in Omphalos responses
                       }
       },

     # GNOME Evolution
    '2f398cabd700444ca54e132b20b50aa0':
       { 'name':      'GNOME Evolution',
         'patterns':   ['evolution'],
         'webdav':     { 'escapeGETs':         False,
                         'supports301':        True,
                         'supportsLocation':   False,
                         'supportsMEMOs':      True,  # Yay!  Evolution supports VJOURNAL!
                         'absoluteHrefs':      False,
                       },
         'jsonrpc':    { }, # Evolution does not use JSOn-RPC
         'xmlrpc':     { }, # Evolution does not use XML-RPC
         'vard':       { 'setVoiceAttrInTel': True,
                         'setCoilsTypeInTel': True,
                         'setCoilsTypeInAdr': True },
         'icalendar':  { 'includeAttachments': 'inline', # Awesome!  Evolution supports iCalendar attachments!
                       }
       },
    # Cadaver
    '5609426bff6641d0b8d273dd706e7386':
       { 'name':      'Cadaver',
         'patterns':   ['cadaver'],
         'webdav':     { 'escapeGETs':         False,
                         'supports301':        False,
                         'supportsLocation':   False,
                         'supportsMEMOs':      True,
                         'absoluteHrefs':      False,
                         '': 'inline' },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vard':       { 'setVoiceAttrInTel': True,
                         'setCoilsTypeInTel': True,
                         'setCoilsTypeInAdr': True },
         'icalendar':  { 'includeAttachments': False,
                       }
       },  # Enc Cadaver 5609426bff6641d0b8d273dd706e7386

    # JGroupDAV (Used by Funambol GroupDAV Connection from BionicMessage.net
    'ecd0eda8f8b244109c7672ac4a630187':
       { 'name':      'JGroupDAV',
         'patterns':   ['bionicmessage.net jgroupdav'],
         'webdav':     { 'escapeGETs':       True,
                         'supports301':      False,
                         'supportsLocation': False,
                         'supportsMEMOs':    True,
                         'absoluteHrefs':    False },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vard':       { },
         'icalendar':  { } },

    # Mozilla / Firefox
    'ecd0eda8f8b244109c7672ac4a630187':
       { 'name':      'Mozilla',
         'patterns':   ['mozilla'],
         'webdav':     { 'supports301':      False,
                         'supportsLocation': False },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vard':       { },
         'icalendar':  { } },

    # Microsoft WebDAV MiniRedirector
    'b6fb2c8a632148728d364b3d49dfe2dd':
       { 'name':      'Microsoft WebDAV MiniRedirector',
         'patterns':   ['microsoft-webdav-miniredir'],
         'webdav':     { 'folderContentType': 'text/html',
                         'escapeGETs':         False,
                         'supports301':        False,
                         'supportsLocation':   False,
                         'supportsMEMOs':      False,
                         'absoluteHrefs':      True,
                         'portInAbsoluteHref': False,
                         'hideLockRoot':       True,
                         'defaultPropeties':
                             [ ( u'href',             u'DAV:',                          u'webdav', 'D:href' ),
                               ( u'getcontenttype',   u'DAV:',                          u'webdav', 'D:getcontenttype' ),
                               ( u'getlastmodified',  u'DAV:',                          u'webdav', 'D:getlastmodified' ),
                               ( u'creationdate',     u'DAV:',                          u'webdav', 'D:creationdate' ),
                               ( u'displayname',      u'DAV:',                          u'webdav', 'D:displayname' ),
                               ( u'getcontentlength', u'DAV:',                          u'webdav', 'D:getcontentlength' ),
                               ( u'executable',       u'http://apache.org/dav/props/', u'apache', 'A:executable' ),
                               ( u'resourcetype',     u'DAV:',                          u'webdav', 'D:resourcetype' ) ], },
#                        'defaultNamespaces': { 'A': 'http://apache.org/dav/props/',
#                                               'D': 'DAV:' } },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vard':       { },
         'icalendar':  { } },

    # Microsoft Data Access
    'e9556b2aad474923a52315d9bffbf124':
       { 'name':      'Microsoft Data Access',
         'patterns':   ['microsoft data access internet publishing'],
         'webdav':     { 'folderContentType': 'text/html',
                         'escapeGETs':         True,
                         'supports301':        False,
                         'supportsLocation':   False,
                         'supportsMEMOs':      False,
                         'absoluteHrefs':      True,
                         'portInAbsoluteHref': False,
                         'hideLockRoot':       True,
                         'defaultPropeties':
                             [ ( u'href',             u'DAV:',                          u'webdav', 'D:href' ),
                               ( u'getcontenttype',   u'DAV:',                          u'webdav', 'D:getcontenttype' ),
                               ( u'getlastmodified',  u'DAV:',                          u'webdav', 'D:getlastmodified' ),
                               ( u'creationdate',     u'DAV:',                          u'webdav', 'D:creationdate' ),
                               ( u'displayname',      u'DAV:',                          u'webdav', 'D:displayname' ),
                               ( u'getcontentlength', u'DAV:',                          u'webdav', 'D:getcontentlength' ),
                               ( u'executable',       u'http://apache.org/dav/props/',  u'webdav', 'A:executable' ),
                               ( u'resourcetype',     u'DAV:',                          u'webdav', 'D:resourcetype' ) ], },
#                        'defaultNamespaces': { 'A': 'http://apache.org/dav/props/',
#                                               'D': 'DAV:' }  },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vard':       { },
         'icalendar':  { } },

    # Curl
    '4879e0253828479aaff784e4c52b23ad':
       { 'name':      'Curl',
         'patterns':   ['curl'],
         'sessionsEnabled': True,
         'webdav':     {
                         'escapeGETs':       True,
                         'supports301':      False,
                         'supportsLocation': False,
                         'supportsMEMOs':    True,
                         'absoluteHrefs':    False },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vard':       { 'includeCoilsXAttributes': True, },
         'icalendar':  { } },

    # GNOME Virtual File System
    '1ce39e9fc8c2416986f56667ee6320d5':
       { 'name':      'GNOME Virtual File-System',
         'patterns':   ['gvfs'],
         'sessionsEnabled': True,
         'webdav':     {
                         'escapeGETs':       True,
                         'supports301':      False,
                         'supportsLocation': False,
                         'supportsMEMOs':    False,
                         'absoluteHrefs':    False },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vard':       { 'includeCoilsXAttributes': True, },
         'icalendar':  { } },

    # User agent definition for testing purposes
    '9d2eb441-921b-4436-b0b9-771348f8ce44':
       { 'name':       'Test User Agent',
         'patterns':   [ 'testtesttest' ],
         'webdav':     {
                         'escapeGETs':       True,
                         'supports301':      False,
                         'supportsLocation': False,
                         'supportsMEMOs':    True,
                         'absoluteHrefs':    False },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vcard':      { 'HIDDENVALUEFORTESTING': EMBEDDED_TEST_STRING,  # DO NOT MODIFY!
                         'setVoiceAttrInTel': False,
                         'setCoilsTypeInTel': False,
                         'telTypeMap': { '10_fax':         { 'types': ['fax','work'],    'voice': False  },
                                         '01_tel':         { 'types': ['work', 'pref' ], 'voice': True   },
                                         '03_tel_funk':    { 'types': ['cell'],          'voice': True   },
                                         '05_tel_private': { 'types': ['home'],          'voice': True,  },
                                         '30_pager':       { 'types': [ 'pager' ],       'voice': False  } },
                         'setCoilsTypeInAdr': False,
                         'adrTypeMap': { 'private':        { 'types': [ 'home' ] },
                                         'mailing':        { 'types': [ 'work', 'pref' ] },
                                         'bill':           { 'types': [ 'work', 'pref' ] },
                                         'shipto':         { 'types': [ 'work' ] } },
                         'includeObjectPropertes':  False,
                         'includeCoilsXAttributes': True,
                         'includeCompanyValues':    False },
         'icalendar':  { } },

    # CardDAV Sync For Android
    '11e687c2-4cea-4464-a31c-5d9f97f8c6f4':
       { 'name':       'CardDAV-Sync for Android',
         'patterns':   [ 'carddav-sync for android', 'carddav-sync (android)' ],
         'webdav':     {
                         'escapeGETs':            True,
                         'supports301':           False,
                         'supportsLocation':      False,
                         'supportsMEMOs':         False,
                         'absoluteHrefs':         False,
                         'principalURL':          '/dav/Contacts/',
                         'showContactsAllFolder': False },
         'jsonrpc':    { },
         'xmlrpc':     { },
         'vcard':      { 'setVoiceAttrInTel': False,
                         'setCoilsTypeInTel': False,
                         'setCoilsTypeInAdr': False,
                         'includeObjectPropertes':  False,
                         'includeCoilsXAttributes': False,
                         'includeCompanyValues':    False },
         'icalendar':  { }
       },

    # WebDAV Nav Android
    # http://www.schimera.com/webdav/
    'ee208564d36048f3a4579d160972689a':
       { 'name':       'WebDAV Nav Android',
         'patterns':   [ 'webdav nav android', ],
         'webdav':     {
                         'showProjectContactsFolder':    False, # Enable/Disable showing the Contacts folder in a Project folder
                         'showProjectEnterprisesFolder': False, # Enable/Disable showing the Enterprise folder in a Project folder
                         'showProjectTasksFolder':       False, # Enable/Disable showing the Tasks folder in a Project folder
                         'showProjectProjectsFolder':    True,  # Enable/Disable showing the Projects (sub-projects) folder in a Project folder
                         'showProjectDocumentsFolder':   True,  # Enable/Disable showing the Documents folder in a Project folder
                         'showProjectNotesFolder':       False, # Enable/Disable showing the Notes folder in a Project folder
                         'showProjectVersionsFolder':    False, # Enable/Disable showing the Versions folder in a Project folder
                         'escapeGETs':            True,
                         'supports301':           False,
                         'supportsLocation':      False,
                         'supportsMEMOs':         False,
                         'absoluteHrefs':         False,
                         'principalURL':          '/dav/Contacts/',
                         'showContactsAllFolder': False },
       },

    # PHP Web Client - Use associative lists in zOGI / Omphalos responses
    '1dcddeea-c5c6-4076-a0e5-4bf933114b86':
       { 'name':       'PHP Web Client (Use Associative Lists)',
         'patterns':   [ 'simple-rpcclient', 'pear xml_rpc' ],
         'omphalos':   { 'associativeLists': True },
         'xmlrpc':     { 'allowNone': False, },
       },

    # Android WebDAV File Manager
    #   http://shigadroid.web.fc2.com/
    'b9020396-85ae-4e47-9bc7-b67d62e88fb7':
       { 'name':       'Android WebDAV File Manager',
         'patterns':   [ 'apache-httpclient' ],
         'webdav':     { 'showProjectContactsFolder':    False,
                         'showProjectEnterprisesFolder': False,
                         'showProjectTasksFolder':       False, }
       },

    # WDFS Fuse Client
    '5aa42c91decc46e49e1c81ddc8aa74ce':
       { 'name':      'WDFS',
         'patterns':   [ 'wdfs' ],
         'webdav':     { 'quoteDAVHref':             True,
                         'filenameAsDisplayName':        True,  # Use the filename as the display name, for clients that confuse the two
                         'showProjectContactsFolder':    False, # Enable/Disable showing the Contacts folder in a Project folder
                         'showProjectEnterprisesFolder': False, # Enable/Disable showing the Enterprise folder in a Project folder
                         'showProjectTasksFolder':       False, # Enable/Disable showing the Tasks folder in a Project folder
                         'showProjectProjectsFolder':    True, # Enable/Disable showing the Projects (sub-projects) folder in a Project folder
                         'showProjectDocumentsFolder':   True, # Enable/Disable showing the Documents folder in a Project folder
                         'showProjectNotesFolder':       True, # Enable/Disable showing the Notes folder in a Project folder
                         'showProjectVersionsFolder':    False, # Enable/Disable showing the Versions folder in a Project folder
                         'folderContentType': 'unix/httpd-directory', # Mime-type for a collection/folder
                         'escapeGETs':            False,
                         'supports301':           True, # Does the client respond correctly to 301 responses
                         'supportsLocation':      True, # Does the client respond correct to Location: headers
                         'supportsMEMOs':         False, # Does the client properly handle Memo (VJOURNAL) objects
                         'absoluteHrefs':         False, # Does the client require HREF values to be absolute
                         'portInAbsoluteHref':    False, # Does the client recognize port numbers in absolute HREFs
                         'hideLockRoot':          False,
                         'principalURL':          None,  # A NULL value leaves it at the default value for the bundle
                         'showContactsAllFolder':   False,  # Enable/Disable the All Contacts folder
                         'showContactsUsersFolder': True,  # Enable/Disable the Users folder under Contacts
                         'defaultPropeties':
                             [ ( u'name',             u'DAV:',                           u'webdav', 'D:name' ),
                               ( u'href',             u'DAV:',                           u'webdav', 'D:href' ),
                               ( u'getcontenttype',   u'DAV:',                           u'webdav', 'D:getcontenttype' ),
                               ( u'contentclass',     u'DAV:',                           u'webdav', 'D:contentclass' ),
                               ( u'getlastmodified',  u'DAV:',                           u'webdav', 'D:getlastmodified' ),
                               ( u'getcontentlength', u'DAV:',                           u'webdav', 'D:getcontentlength' ),
                               ( u'iscollection',     u'DAV:',                           u'webdav', 'D:iscollection' ),
                               ( u'displayname',      u'DAV:',                           u'webdav', 'D:displayname' ),
                               ( u'getctag',          u'urn:ietf:params:xml:ns:caldav', u'caldav', 'C:getctag' ),
                               ( u'resourcetype',     u'DAV:',                           u'webdav', 'D:resourcetype' ) ],
                        'defaultNamespaces': { 'A': 'http://apache.org/dav/props/',
                                               'B': 'http://icewarp.com/ns/',
                                               'C': 'urn:ietf:params:xml:ns:caldav',
                                               'D': 'DAV:',
                                               'E': 'urn:ietf:params:xml:ns:carddav',
                                               'G': 'http://groupdav.org/' } },
         'vcard':       { 'setVoiceAttrInTel': True,
                          'setCoilsTypeInTel': True,
                          'telTypeMap': { '10_fax':         { 'types': ['fax','work'],    'voice': False  },
                                          '01_tel':         { 'types': ['work', 'pref' ], 'voice': True   },
                                          '03_tel_funk':    { 'types': ['cell'],          'voice': True   },
                                          '05_tel_private': { 'types': ['home'],          'voice': True,  },
                                          '30_pager':       { 'types': [ 'pager' ],       'voice': False  } },
                          'setCoilsTypeInAdr': True, # Encode the OGo address type in VCARD ADR properties
                          'adrTypeMap': { 'private':        { 'types': [ 'home' ] },
                                          'mailing':        { 'types': [ 'work', 'pref' ] },
                                          'bill':           { 'types': [ 'work', 'pref' ] },
                                          'shipto':         { 'types': [ 'work' ] } },
                          'includeObjectPropertes': True, # Encode the OGo object properties in VCARDs
                          'includeCoilsXAttributes': True, # Encode the OGo company values in VCARDs
                          'includeCompanyValues': True, # Encode the OGo company values in VCARDs
                        },
         'icalendar':  { 'includeAttachments': True,  # includeAttachments: False, inline, link
                       },
       },

    # Cadaver WebDAV Client
    '1666f6b2cfab46e0993657cf7f7df8ef':
       { 'name':      'Cadaver',
         'patterns':   [ 'cadaver', ],
         'webdav':     { 'quoteDAVHref':             True,
                         'filenameAsDisplayName':        True,  # Use the filename as the display name, for clients that confuse the two
                         'showProjectContactsFolder':    False, # Enable/Disable showing the Contacts folder in a Project folder
                         'showProjectEnterprisesFolder': False, # Enable/Disable showing the Enterprise folder in a Project folder
                         'showProjectTasksFolder':       False, # Enable/Disable showing the Tasks folder in a Project folder
                         'showProjectProjectsFolder':    True, # Enable/Disable showing the Projects (sub-projects) folder in a Project folder
                         'showProjectDocumentsFolder':   True, # Enable/Disable showing the Documents folder in a Project folder
                         'showProjectNotesFolder':       True, # Enable/Disable showing the Notes folder in a Project folder
                         'showProjectVersionsFolder':    False, # Enable/Disable showing the Versions folder in a Project folder
                         'folderContentType': 'unix/httpd-directory', # Mime-type for a collection/folder
                         'escapeGETs':            False,
                         'supports301':           True, # Does the client respond correctly to 301 responses
                         'supportsLocation':      True, # Does the client respond correct to Location: headers
                         'supportsMEMOs':         False, # Does the client properly handle Memo (VJOURNAL) objects
                         'absoluteHrefs':         False, # Does the client require HREF values to be absolute
                         'portInAbsoluteHref':    False, # Does the client recognize port numbers in absolute HREFs
                         'hideLockRoot':          False,
                         'principalURL':          None,  # A NULL value leaves it at the default value for the bundle
                         'showContactsAllFolder':   False,  # Enable/Disable the All Contacts folder
                         'showContactsUsersFolder': True,  # Enable/Disable the Users folder under Contacts
                         'defaultPropeties':
                             [ ( u'name',             u'DAV:',                           u'webdav', 'D:name' ),
                               ( u'href',             u'DAV:',                           u'webdav', 'D:href' ),
                               ( u'getcontenttype',   u'DAV:',                           u'webdav', 'D:getcontenttype' ),
                               ( u'contentclass',     u'DAV:',                           u'webdav', 'D:contentclass' ),
                               ( u'getlastmodified',  u'DAV:',                           u'webdav', 'D:getlastmodified' ),
                               ( u'getcontentlength', u'DAV:',                           u'webdav', 'D:getcontentlength' ),
                               ( u'iscollection',     u'DAV:',                           u'webdav', 'D:iscollection' ),
                               ( u'displayname',      u'DAV:',                           u'webdav', 'D:displayname' ),
                               ( u'getctag',          u'urn:ietf:params:xml:ns:caldav', u'caldav', 'C:getctag' ),
                               ( u'resourcetype',     u'DAV:',                           u'webdav', 'D:resourcetype' ) ],
                        'defaultNamespaces': { 'A': 'http://apache.org/dav/props/',
                                               'B': 'http://icewarp.com/ns/',
                                               'C': 'urn:ietf:params:xml:ns:caldav',
                                               'D': 'DAV:',
                                               'E': 'urn:ietf:params:xml:ns:carddav',
                                               'G': 'http://groupdav.org/' } },
         'vcard':       { 'setVoiceAttrInTel': True,
                          'setCoilsTypeInTel': True,
                          'telTypeMap': { '10_fax':         { 'types': ['fax','work'],    'voice': False  },
                                          '01_tel':         { 'types': ['work', 'pref' ], 'voice': True   },
                                          '03_tel_funk':    { 'types': ['cell'],          'voice': True   },
                                          '05_tel_private': { 'types': ['home'],          'voice': True,  },
                                          '30_pager':       { 'types': [ 'pager' ],       'voice': False  } },
                          'setCoilsTypeInAdr': True, # Encode the OGo address type in VCARD ADR properties
                          'adrTypeMap': { 'private':        { 'types': [ 'home' ] },
                                          'mailing':        { 'types': [ 'work', 'pref' ] },
                                          'bill':           { 'types': [ 'work', 'pref' ] },
                                          'shipto':         { 'types': [ 'work' ] } },
                          'includeObjectPropertes': True, # Encode the OGo object properties in VCARDs
                          'includeCoilsXAttributes': True, # Encode the OGo company values in VCARDs
                          'includeCompanyValues': True, # Encode the OGo company values in VCARDs
                        },
         'icalendar':  { 'includeAttachments': True,  # includeAttachments: False, inline, link
                       },
       },
    }


def lookup_user_agent(agent_string):
    '''
    Return tuple of user agent + dictionary of the clients features and bugs.
    '''

    def recursive_update(source, target, domain=None):
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict):
                    if (domain == 'webdav' and
                        key in ('defaultNamespaces')):
                        # DO *NOT* COMPOSE THESE VALUES, REPLACE THE DEFAULT COMPLETELY
                        #   -> webdav -> defaultNamespaces
                        target[key] = source[key]
                    else:
                        # Subordinate dictionary, copy that
                        recursive_update(value, target[key], domain=key)
                else:
                    # Replace the value
                    target[key] = value
            else:
                # Add the value [actually this should never happen in this case]
                # Defined user agents are only supposed to substitute/overlay default values
                target[key] = value

    if agent_string is None:
        return DEFAULT_USER_AGENT, USER_AGENTS[DEFAULT_USER_AGENT]

    parts = agent_string.split('/')
    if len(parts) > 1:
        agent_name    = parts[0].lower()
        agent_version = parts[1].lower()
    else:
        agent_name = parts[0].lower()
        agent_version = 'Unknown'

    agent = None
    if agent_name in USER_AGENTS:
        # If the agent_name ends up as one of the Agent Id UUIDs we take that one
        # This is an unlikely event but allows Coils-only clients to exactly specify the desired behavior
        agent = agent_name
    else:
        for agent_id, agent_data in USER_AGENTS.items():
            for pattern in agent_data[ 'patterns' ]:
                if agent_name.startswith(pattern):
                    agent = agent_id
                    break
            if agent:
                break
        else:
            return DEFAULT_USER_AGENT, USER_AGENTS[DEFAULT_USER_AGENT]

    agent_id   = agent
    # Start with a copy of the default user agent and then overlay the settings
    # from the matching user agent.
    agent_data = copy.deepcopy( USER_AGENTS[ DEFAULT_USER_AGENT ] )
    recursive_update( USER_AGENTS[ agent_id ], agent_data )
    return agent_id, agent_data
