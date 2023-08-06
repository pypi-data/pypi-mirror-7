#
# Copyright (c) 2009, 2012
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
import pprint
from sqlalchemy       import *
from coils.core       import *
from coils.core.logic import UpdateCommand
from command          import CompanyCommand

class UpdateCompany(UpdateCommand, CompanyCommand):

    def __init__(self):
        UpdateCommand.__init__(self)
        self.sd = ServerDefaultsManager()
        self._C_company_values = { }

    def parse_parameters(self, **params):
        UpdateCommand.parse_parameters(self, **params)

    def run(self):
        UpdateCommand.run(self)
        
        self._update_telephones()
        self._update_addresses()
        self._update_company_values()
        self._set_projects()
        self._set_access()
