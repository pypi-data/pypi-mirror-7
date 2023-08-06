#
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
#
from render_object import as_integer, as_string, as_datetime, render_object


PROC_STATE_LABEL = {'Q': 'queued',
                    'R': 'running',
                    'F': 'failed',
                    'C': 'completed',
                    'P': 'parked',
                    'I': 'initialized',
                    'Z': 'zombie',
                    'X': 'canceled', }


def render_process(entity, detail, ctx, favorite_ids=None):
    '''
        '_OBJECTLINKS': [],
         '_PROPERTIES': [],
         'objectId':
         'entityName': 'Route',
         'name':       'XrefrType4DuplicateErrorReport',
         'created':    ,
         'modified':   ,
         'version':    ,
         'ownerObjectId': 10100
         'routeObjectId':
         'priority'


    '''

    p = {
        'entityName':             'Process',
        'objectId':               entity.object_id,
        'GUID':                   as_string(entity.uuid),
        'ownerObjectId':          as_integer(entity.owner_id),
        'routeObjectId':          as_integer(entity.route_id),
        'created':                as_datetime(entity.created),
        'modified':               as_datetime(entity.modified),
        'completed':              as_datetime(entity.completed),
        'parked':                 as_datetime(entity.parked),
        'started':                as_datetime(entity.started),
        'version':                as_integer(entity.version),
        'inputMessageUUID':       as_string(entity.input_message),
        'outputMessageUUID':      as_string(entity.output_message),
        'taskObjectId':           as_integer(entity.task_id),
        'priority':               as_integer(entity.priority),
    }

    # Comment (process log)
    if (detail & 2048):
        # Allow retrieval of the process log to fail
        try:
            comment = ctx.run_command('process::get-log', process=entity)
            if (comment is None):
                p['comment'] = '(Unavailable)'
            else:
                p['comment'] = comment
        except Exception, e:
            p['comment'] = '(Unavailable)'

    # State
    p['state'] = PROC_STATE_LABEL.get(entity.state, 'unknown')

    # Route name
    if entity.route is None:
        p['routeName'] = ''
    else:
        p['routeName'] = as_string(entity.route.name)

    # FLAGS
    flags = []
    if (entity.owner_id == ctx.account_id):
        flags.append('OWNER')
    rights = ctx.access_manager.access_rights(entity)
    if 'w' in rights:
        flags.extend(['WRITE', 'READ', 'LIST', 'VIEW', 'EXECUTE', ])
    else:
        flags.append('READONLY')
        if 'r' in rights:
            flags.extend(['READ', 'LIST', 'VIEW', 'EXECUTE', ])
        elif 'v' in rights:
            flags.extend(['LIST', 'VIEW', 'EXECUTE', ])
        elif 'l' in rights:
            flags.extend(['LIST', ])
    if ('d' in rights) or ('w' in rights):
        flags.append('DELETE')
    p['FLAGS'] = flags

    # Messages
    p['_MESSAGES'] = []
    for message in ctx.run_command('process::get-messages', process=entity, ):
        p['_MESSAGES'].append(
            {'entityName': 'message',
             'processObjectId': entity.object_id,
             'uuid': as_string(message.uuid),
             'scope': as_string(message.scope),
             'mimetype': as_string(message.mimetype),
             'size': as_integer(message.size),
             'label': as_string(message.label),
             'version': as_integer(message.version),
             'created': as_datetime(message.created),
             'modified': as_datetime(message.modified), })

    return render_object(p, entity, detail, ctx)
