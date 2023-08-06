# Copyright (c) 2010, 2013
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
from coils.core import ServerDefaultsManager
from render_object import *


PRINTABLE_MIME_TYPES = None


def render_file(entity, detail, ctx, favorite_ids=None):
    """ {'attachment':
            '/var/lib/opengroupware.org/documents/844500/142400/14247521.xls',
         'creation': <DateTime '20100420T21:16:02' at 7f972fdc7ea8>,
         'creatorObjectId': 54720,
         'entityName': 'File',
         'fileSize': 604160,
         'fileType': 'xls',
         'filename': 'HAV fix 0410',
         'folderObjectId': 844520,
         'lastModified': <DateTime '20100420T21:16:02' at 7f972fdc7e60>,
         'objectId': 14247521,
         'ownerObjectId': 54720,
         'projectObjectId': 844500,
         'status': 'released',
         'title': 'v616 FK fix 0410',
         'version': 1} """

    global PRINTABLE_MIME_TYPES

    if PRINTABLE_MIME_TYPES is None:
        PRINTABLE_MIME_TYPES = \
            ServerDefaultsManager().default_as_list('IPPPrintableMIMETypes')

    mimetype = ctx.type_manager.get_mimetype(entity)

    blob = {'entityName':      'File',
            'creation':        as_datetime(entity.created),
            'creatorObjectId': as_integer(entity.creator_id),
            'fileSize':        as_integer(entity.file_size),
            'fileType':        as_string(entity.extension),
            'filename':        as_string(entity.name),
            'folderObjectId':  as_integer(entity.folder_id),
            'lastModified':    as_datetime(entity.modified),
            'objectId':        as_integer(entity.object_id),
            'ownerObjectId':   as_integer(entity.owner_id),
            'projectObjectId': as_integer(entity.project_id),
            'status':          as_string(entity.status),
            'title':           as_string(entity.abstract),
            'mimetype':        as_string(mimetype),
            'version':         as_integer(entity.version), }
    '''

    blob = { 'entityName':      'File',
             'creation':        as_datetime( entity.created ),
             'creatorObjectId': entity.creator_id,
             'fileSize':        entity.file_size,
             'fileType':        entity.extension,
             'filename':        entity.name,
             'folderObjectId':  entity.folder_id,
             'lastModified':    as_datetime( entity.modified ),
             'objectId':        entity.object_id,
             'ownerObjectId':   entity.owner_id,
             'projectObjectId': entity.project_id,
             'status':          entity.status,
             'title':           entity.abstract,
             'mimetype':        mimetype,
             'version':         entity.version, }
    '''

    # FLAGS
    flags = []
    rights = ctx.access_manager.access_rights(entity)
    if 'w' in rights:
        flags.append('WRITE')
    else:
        flags.append('READONLY')
    if ctx.account_id == entity.owner_id:
        flags.append('OWNER')
    if mimetype in PRINTABLE_MIME_TYPES:
        flags.append('IPPPRINTABLE')

    prop = ctx.property_manager.get_property(
        entity,
        '57c7fc84-3cea-417d-af54-b659eb87a046',
        'damaged')
    if prop:
        if prop.get_string_value() == 'YES':
            flags.append('DAMAGED')

    blob['FLAGS'] = flags

    return render_object(blob, entity, detail, ctx)


def render_folder(entity, detail, ctx, favorite_ids=None):
    """ { 'creation': <DateTime '20100414T13:01:13' at 7f972f740c68>,
          'creatorObjectId': 10100,
          'entityName': 'Folder',
          'folderObjectId': 844520,
          'objectId': 14216643,
          'ownerObjectId': 10100,
          'projectObjectId': 844500,
          'title': '201004'} """

    folder = {'entityName': 'Folder',
              'creation': as_datetime(entity.created),
              'creatorObjectId': as_integer(entity.creator_id),
              'folderObjectId': as_integer(entity.folder_id),
              'objectId': as_integer(entity.object_id),
              'ownerObjectId': as_integer(entity.owner_id),
              'projectObjectId': as_integer(entity.project_id),
              'childrenCount': as_integer(entity.children),
              'title': as_string(entity.name), }

    if (detail & 16384):
        folder['_CONTENTS'] = []
        contents = ctx.run_command('folder::ls', id=entity.object_id)
        for obj in contents:
            if (obj.__entityName__ == 'Document'):
                folder['_CONTENTS'].append(render_file(obj, 0, ctx))
            elif (obj.__entityName__ == 'Folder'):
                folder['_CONTENTS'].append(render_folder(obj, 0, ctx))

    # FLAGS
    flags = []
    rights = ctx.access_manager.access_rights(entity)
    ## READ permissions
    if 'r' in rights:
        flags.extend(('READ', 'LIST', 'VIEW', ))
    else:
        if 'l' in rights:
            flags.append('LIST')
        if 'v' in rights:
            flags.append('VIEW')
    ## WRITE permissions
    if 'w' in rights:
        flags.extend(('WRITE', 'INSERT', 'DELETE', ))
    else:
        if 'd' in rights:
            flags.append('DELETE')
        if 'i' in rights:
            flags.append('INSERT')
    if 'a' in rights:
        flags.append('ADMIN')
    if ctx.account_id == entity.owner_id:
        flags.append('OWNER')
    folder['FLAGS'] = flags

    return render_object(folder, entity, detail, ctx)
