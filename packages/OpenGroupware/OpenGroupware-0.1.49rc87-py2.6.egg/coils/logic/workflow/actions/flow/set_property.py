#
# Copyright (c) 2010, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core.logic import ActionCommand


class SetProcessPropertyAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "set-process-property"
    __aliases__ = ['setProcessPropertyAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        self._ctx.property_manager.set_property(
            entity=self.process,
            namespace=self._namespace,
            attribute=self._attribute,
            value=self._value,
        )

    def parse_action_parameters(self):
        self._namespace = self.process_label_substitutions(
            self.action_parameters.get(
                'namespace',
                'http://www.opengroupware.us/oie',
            )
        )
        self._attribute = self.process_label_substitutions(
            self.action_parameters.get('attribute')
        )
        self._value = self.process_label_substitutions(
            self.action_parameters.get('value')
        )

    def do_epilogue(self):
        pass
