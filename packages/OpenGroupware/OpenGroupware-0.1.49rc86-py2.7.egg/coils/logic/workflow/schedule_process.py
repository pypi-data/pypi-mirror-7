#
# Copyright (c) 2010, 2012, 2013
# Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime import datetime
from coils.core import \
    AsyncronousCommand, \
    Route, \
    CoilsException, \
    Attachment
from coils.foundation import Parse_Value_To_UTCDateTime


class ScheduleProcess(AsyncronousCommand):
    __domain__ = "process"
    __operation__ = "schedule"

    @staticmethod
    def Take_Schedule_Entry_From_Dict(params):
        entry = {}
        #
        if params.get('type', None) == 'simple':
            entry['triggerType'] = 'simple'
            entry['date'] = \
                Parse_Value_To_UTCDateTime(
                    time_value=params.get('date', None),
                    default=datetime.utcnow())
        elif params.get('type', None) == 'interval':
            entry['triggerType'] = 'interval'
            entry['weeks'] = int(params.get('weeks', 0))
            entry['days'] = int(params.get('days', 0))
            entry['hours'] = int(params.get('hours', 0))
            entry['minutes'] = int(params.get('minutes', 0))
            entry['seconds'] = int(params.get('seconds', 0))
            entry['start'] = \
                Parse_Value_To_UTCDateTime(
                    time_value=params.get('start', None),
                    default=datetime.utcnow())
        elif params.get('type', None) == 'cron':
            # Crontab
            entry['triggerType'] = 'cron'
            entry['year'] = str(params.get('year', '*'))
            entry['month'] = str(params.get('month', '*'))
            entry['day'] = str(params.get('day', '*'))
            entry['weekday'] = str(params.get('weekday', '*'))
            entry['hour'] = str(params.get('hour', '*'))
            entry['minute'] = str(params.get('minute', '*'))

        return entry

    def parse_success_response(self, data):
        self.set_result(data['UUID'])

    def parse_failure_response(self, data):
        self.set_result(None)

    def parse_parameters(self, **params):
        AsyncronousCommand.parse_parameters(self, **params)

        self._args = {'xattrDict': {}, }

        context_id = int(params.get('context_id', self._ctx.account_id, ))
        if context_id not in self._ctx.context_ids:
            raise CoilsException(
                'Attempt to use unavailable contextId#{0}'.
                format(context_id, ))
        self._args['contextId'] = context_id

        self._args['priority'] = int(params.get('priority', 175))

        if 'repeat' in params:
            self._args['repeat'] = int(params['repeat'])

        # xattrDict
        if 'xattrs' in params:
            xattrs = params['xattrs']
            if isinstance(xattrs, dict):
                self._args['xattrDict'] = xattrs
            else:
                raise CoilsException(
                    'Specified xattrs must be in the form of a dict, '
                    ' got type "{0}"'.
                    format(type(xattrs), ))

        # Attachment (process input message)
        if 'attachment' in params:
            attachment = params['attachment']
            if isinstance(attachment, Attachment):
                self._args['attachmentUUID'] = attachment.uuid
            else:
                raise CoilsException(
                    'Attachment object is not an Attachment entity')
        elif 'attachmentUUID' in params:
            uuid = params['attachmentUUID']
            if isinstance(uuid, basestring):
                self._args['attachmentUUID'] = uuid
            else:
                raise CoilsException(
                    'Specified attachment UUID is not a string.')

        #
        # Route
        #
        route_id = route = None
        if 'route' in params:
            route = params.get('route')
            route_id = route.object_id
        elif 'route_id' in params:
            route_id = int(params.get('route_id'))
            route = self._ctx.run_command('route::get', id=route_id, )

        if isinstance(route, Route):
            self._args['routeId'] = route.object_id
        else:
            raise CoilsException(
                'Unable to access OGo#{0} [Route] in order to schedule '
                'process'.
                format(route_id, ))

        #
        # Get schedule parameters
        #
        self._args.update(
            ScheduleProcess.Take_Schedule_Entry_From_Dict(params)
        )

    def run(self):
        self.set_return_value(False)
        self.set_return_value(
            self.callout('coils.workflow.scheduler/schedule_job', self._args))
        self.wait()
