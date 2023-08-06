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
# THE SOFTWARE.
#
from coils.core           import *
from coils.net            import PathObject

class CSSPage(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def get_content_handle(self):

        project = self.context.run_command( 'project::get', id=7000 )
        if project:
            document = self.context.run_command( 'project::get-path', path='/Wiki/default.css',
                                                                      access_check=False,
                                                                      project=project )
            if document:
                handle = self.context.run_command( 'document::get-handle', id=document.object_id )
                return document.checksum, handle
        return None, None

    #
    # Method Handlers
    #

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        return self

    def do_HEAD(self):
        checksum, handle = self.get_content_handle( )
        if handle:
            self.request.stream_response( 204, data=None, mimetype='text/css',
                                               headers={ 'etag': checksum } )
            return
        raise NoSuchPathException( 'No style sheet available' )

    def do_GET(self):
        # TODO: Check for locks!
        # TODO: What if the document doesn't report a mime-type?
        checksum, handle = self.get_content_handle( )
        if handle:
            self.request.stream_response( 200, stream=handle, mimetype='text/css',
                                               headers={ 'etag': checksum } )
            BLOBManager.Close(handle)
            return
        raise NoSuchPathException( 'No style sheet available' )
