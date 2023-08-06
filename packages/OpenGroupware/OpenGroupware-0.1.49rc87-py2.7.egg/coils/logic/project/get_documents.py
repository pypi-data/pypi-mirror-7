#!/usr/bin/python
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetProjectDocuments(GetCommand):
    __domain__ = "project"
    __operation__ = "get-documents"

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if 'id' in params:
            self.project_id = long( params[ 'id' ] )
        elif 'project' in params:
            self.project_id = params[ 'project' ].object_id
        elif 'object' in params:
            self.project_id = params[ 'object' ].object_id
        else:
            raise CoilsException( 'No project or project id provided to project::get-documents' )

    def run(self, **params):
        self.set_multiple_result_mode( )
        query = self._ctx.db_session( ).\
                          query( Document ).\
                          filter( Document.project_id == self.project_id )
        self.set_return_value( query.all( ) )

