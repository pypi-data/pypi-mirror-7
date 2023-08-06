#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core          import *
from coils.core.logic    import ActionCommand

class WaitAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "wait"
    __aliases__   = [ 'waitAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        message = self._ctx.run_command('message::get', process=self.process,
                                                        label=self._wait_for)
        self.log.debug('Message retrieval in wait returned {0}'.format(message))
        if (message is None):
            self._continue = False
            self._proceed  = False

    def parse_action_parameters(self):
        self._wait_for = self.action_parameters.get('waitForLabel', 'InputMessage')
        pass

    def do_epilogue(self):
        pass