#
# Copyright (c) 2011, 2014
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
import shutil
from subprocess import Popen, PIPE
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from coils.foundation.api.printing import LPR


class PrintToLPRAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "print-to-lpr"
    __aliases__ = ['printToLPR', 'printToLPRAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/postscript'

    def do_action(self):

        # Message Size Check
        if self.input_message.size < self._minimum_job_size:
            if self._job_size_violation_policy == 'ERROR':
                raise CoilsException(
                    'Requested message to print "{0}" is too small @ {1}'
                    'octetes, error policy is "{2}" so workflow process will'
                    'abend. Minimum job size is {3} octets.'.
                    format(
                        self.input_message.label,
                        self.input_message.size,
                        self._job_size_violation_policy,
                        self._minimum_job_size,
                    )
                )
            elif self._job_size_violation_policy == 'PASS':
                self.log_message(
                    'Requested print message "{0}" too small @ {1} octets,'
                    'error policy is "{2}" so performing no action.'.
                    format(
                        self.input_message.label,
                        self.input_message.size,
                        self._job_size_violation_policy,
                    ),
                    category='info',
                )
                return

        # Document Type Conversion
        if (self._convert == 'YES'):
            if (self.input_message.mimetype == 'application/pdf'):
                converter = Popen(
                    ['/usr/bin/pdftops', '-', '-', ],
                    stdin=PIPE,
                    stdout=self._wfile,
                )
                (converter_in, converter_out, ) = \
                    (converter.stdin, converter.stdout, )
                shutil.copyfileobj(self._rfile, converter_in)
                converter_in.close()
            elif (self.input_message.mimetype == 'application/postscript'):
                # For a postscript file we just copy it straight though
                shutil.copyfileobj(self._rfile, self._wfile)
            else:
                raise CoilsException(
                    'Unsupported input MIME type of "{0}"'.
                    format(self.input_message.mimetype, )
                )
        else:
            shutil.copyfileobj(self._rfile, self._wfile)
        self._wfile.flush()
        self._wfile.seek(0)

        # Submit to print queue
        lpr = LPR(self._server, user=self._ctx.login)
        lpr.connect()
        lpr.send_stream(
            self._queue,
            self.input_message.uuid,
            self._wfile,
            job_name=self._job_name,
        )
        lpr.close()

    def parse_action_parameters(self):
        self._server = \
            self.action_parameters.get('serverName', 'localhost')

        self._job_name = \
            self.process_label_substitutions(
                self.action_parameters.get('jobName', None, )
            )

        self._queue = \
            self.process_label_substitutions(
                self.action_parameters.get('printerName', '')
            )

        self._convert = \
            self.process_label_substitutions(
                self.action_parameters.get('typeConvert', 'YES')
            )

        self._minimum_job_size = \
            long(
                self.process_label_substitutions(
                    self.action_parameters.get('minimumJobSize', '3')
                )
            )

        self._job_size_violation_policy = \
            self.process_label_substitutions(
                self.action_parameters.get('jobSizeViolationPolicy', 'ERROR')
            ).upper()
        if self._job_size_violation_policy not in ('ERROR', 'PASS', ):
            raise CoilsException(
                'Unknown job size violation policy of "{0}"'
                .format(self._job_size_violation_policy, )
            )

    def do_epilogue(self):
        pass
