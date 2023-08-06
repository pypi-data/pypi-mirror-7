#
# Copyright (c) 2012, 2013
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
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from command import SSHAction


class SSHGetFileAction(ActionCommand, SSHAction):
    __domain__ = "action"
    __operation__ = "ssh-get-file"
    __aliases__ = ['sshGetFileAction', 'sshGetFile', ]
    mode = None

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._mimetype

    def parse_action_parameters(self):
        ActionCommand.parse_action_parameters(self)

        SSHAction.parse_action_parameters(self)

        self._filename = self.action_parameters.get('filePath', None)
        self._mimetype = self.action_parameters.get(
            'mimeType',
            'application/octet-stream',
        )

        if not self._filename:
            raise CoilsException(
                'No filename provided for sshGetFileAction action'
            )
        self._filename = self.process_label_substitutions(self._filename)

    def do_action(self):
        self.initialize_client()
        key_path, key_handle, = self.resolve_private_key()
        private_key = self.initialize_private_key(
            path=key_path,
            handle=key_handle,
            password=self._secret,
        )
        transport = self.initialize_transport(
            self._hostname,
            self._hostport, )
        if self.authenticate(
            transport=transport,
            username=self._username,
            private_key=private_key,
        ):
            self.get_file(
                transport=transport,
                path=self._filename,
                wfile=self.wfile, )
        else:
            raise CoilsException(
                'Unable to complete SSH authentication'
            )
        self.close_transport(transport=transport)
