#
# Copyright (c) 2013
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
#
from render_object import *


def render_routegroup(entity, detail, ctx, favorite_ids=None):
    '''
        '_OBJECTLINKS': [],
        '_PROPERTIES': [],
        'comment': '',
        'entityName': 'RouteGroup',
        'name':       'XrefrType4DuplicateErrorReport',
        'created':    ,
        'modified':   ,
        'version':    ,
        'ownerObjectId': 10100,
        '''

    r = {
        'entityName':    'RouteGroup',
        'objectId':      entity.object_id,
        'name':          as_string(entity.name),
        'comment':       as_string(entity.comment),
        'ownerObjectId': as_integer(entity.owner_id),
        'created':       as_datetime(entity.created),
        'modified':      as_datetime(entity.modified),
        'version':       as_integer(entity.version),
    }

    # FLAGS
    flags = []
    rights = ctx.access_manager.access_rights(entity)
    if entity.owner_id == ctx.account_id:
        flags.append('OWNER')
    if 'w' in rights:
        flags.append('WRITE')
    if entity.routes:
        flags.append('NOTEMPTY')
    else:
        flags.append('EMPTY')
        if 'd' in rights:
            flags.append('DELETE')
    r['FLAGS'] = flags

    return render_object(r, entity, detail, ctx)
