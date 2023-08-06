# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime import datetime
import pytz, time, json
from coils.foundation    import *
from coils.core          import *
from coils.net           import *
from coils.core.omphalos import *

from apis import get_horde_api

class Root(PathObject, Protocol):
    __pattern__   = '^horde$'
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def is_public(self):
        return False

    def get_name(self):
        return 'jsonrpc'

    def do_POST(self):

        def encode(o):
            print type(o), o
            if (isinstance(o, datetime)):
                return  o.strftime('%Y-%m-%d')
            raise TypeError()

        mimetype = self.request.headers.get('Content-Type', None)
        if (mimetype == 'application/json'):
            start = time.time()
            payload = self.request.get_request_payload()
            try:
                print payload
                values = json.loads(payload)
            except:
                raise CoilsException('Unable to parse JSON content.')
            if (isinstance(values, dict)):
                start = time.time()
                if ('method' in values):
                    # TODO: check version
                    self.log.info(values)
                    method      = 'api_{0}'.format(values['method'].replace('.', '_').strip().lower())
                    response_id = values.get('id', None)
                    parameters  = values.get('params', [])
                    print method
                    api = get_horde_api(method.split('_')[1], context=self.context)
                    api.log = self.context.log
                    if (hasattr(api, method)):
                        try:
                            result = getattr(api, method)(parameters)
                        except Exception, e:
                            self.log.exception(e)
                            response =  { 'result':  None,
                                          'version': '1.1',
                                          'error':   str(e),
                                          'id':      response_id }
                            if (self.context.amq_available):
                                end = time.time()
                                self.context.send(None,
                                                  'coils.administrator/performance_log',
                                                  { 'lname': 'horde',
                                                    'oname': values['method'].strip().lower(),
                                                    'runtime': (end - start),
                                                    'error': True } )
                        else:
                            if (self.context.amq_available):
                                end = time.time()
                                self.context.send(None,
                                                  'coils.administrator/performance_log',
                                                  { 'lname': 'horde',
                                                    'oname': values['method'].strip().lower(),
                                                    'runtime': (end - start),
                                                    'error': False } )
                            response =  { 'result':   result,
                                          'version':  '1.1',
                                          'error':    None,
                                          'id':      response_id }
                    else:
                        self.log.error('Request for non-implmented JSON-RPC API {0}'.format(method))
                        response =  { 'result':   None,
                                      'version':  '1.1',
                                      'error':    'JSON-RPC API implements no such method as {0}'.format(method),
                                      'id':       response_id }
                    try:
                        response = json.dumps(response, default=encode)
                    except:
                        raise CoilsException('Unable to represent response as JSON content.')
                    self.request.simple_response(200, data=response,
                                                      mimetype='application/json')
                else:
                    raise CoilsException('No RPC method specified in request')
            else:
                raise CoilsException('JSON content does not represent a criterion dictionary')
        else:
            raise CoilsException('Unexpected Content-Type; must be application/json')
