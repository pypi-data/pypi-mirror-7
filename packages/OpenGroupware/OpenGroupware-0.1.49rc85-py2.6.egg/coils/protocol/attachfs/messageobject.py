#
# Copyright (c) 2011, 2013, 2014
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
from coils.core import BLOBManager
from coils.net import PathObject
from coils.net.ossf import MarshallOSSFChain


class MessageObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        self.entity = None
        self.request = None
        self.parameters = None
        PathObject.__init__(self, parent, **params)

    #
    # Method Handlers
    #

    def do_HEAD(self):
        mimetype = self.context.type_manager.get_mimetype(self.entity)
        self.request.simple_response(
            200,
            data=None,
            mimetype=mimetype,
            headers={
                'etag': self.entity.uuid,
                'Content-Length': str(self.entity.size),
            },
        )

    def do_GET(self):
        mimetype = self.context.tm.get_mimetype(self.entity)
        handle = self.context.run_command(
            'message::get-handle',
            uuid=self.entity.uuid,
        )
        handle, mimetype = MarshallOSSFChain(
            handle, mimetype, self.parameters,
        )
        self.log.debug(
            'MIME-Type after OSSF processing is {0}'.format(mimetype, )
        )
        self.context.commit()
        self.request.stream_response(
            200,
            stream=handle,
            mimetype=mimetype,
            headers={'etag': self.entity.uuid, },
        )
        BLOBManager.Close(handle)
