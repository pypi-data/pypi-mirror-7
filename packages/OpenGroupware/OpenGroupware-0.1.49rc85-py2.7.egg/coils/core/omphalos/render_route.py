#
# Copyright (c) 2010, 2013, 2014
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
# THE SOFTWARE
#
from render_object import as_integer, as_datetime, as_string, render_object


def render_route(entity, detail, ctx, favorite_ids=None):
    '''
        '_OBJECTLINKS': [],
        '_PROPERTIES': [],
        'comment': '',
        'entityName': 'Route',
        'name':       'XrefrType4DuplicateErrorReport',
        'created':    ,
        'modified':   ,
        'version':    ,
        'ownerObjectId': 10100,
        'routeGroupObjectId': 12345,
        '''
    r = {
        'entityName':         'Route',
        'objectId':           entity.object_id,
        'name':               as_string(entity.name),
        'comment':            as_string(entity.comment),
        'ownerObjectId':      as_integer(entity.owner_id),
        'created':            as_datetime(entity.created),
        'modified':           as_datetime(entity.modified),
        'version':            as_integer(entity.version),
        'routeGroupObjectId': as_integer(entity.group_id),
        'isSingleton':        as_integer(entity.is_singleton),
    }

    # FLAGS
    flags = []
    if (entity.owner_id == ctx.account_id):
        flags.append('SELF')
    rights = ctx.access_manager.access_rights(entity)
    if 'r' in rights:
        flags.append('READ')
    if 'p' in rights:
        flags.extend('POST')
    if set('rp').intersection(rights):
        flags.extend('EXECUTE')
    if 'w' in rights:
        flags.extend(('WRITE', 'DELETE', ))
    elif 'd' in rights:
        flags.append('DELETE')
    else:
        flags.append('READONLY')
    r['FLAGS'] = flags
    return render_object(r, entity, detail, ctx)
