#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy import and_
from coils.foundation import apply_orm_hints_to_query
from coils.core import Command, Task


class GetDelegatedList(Command):
    __domain__ = "task"
    __operation__ = "get-delegated"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

    def run(self, **params):
        self.disable_access_check()
        db = self._ctx.db_session()
        query = db.query(Task).\
            filter(and_(Task.owner_id.in_(self._ctx.context_ids),
                        Task.state != '30_archived',
                        Task.executor_id != self._ctx.account_id))
        query = apply_orm_hints_to_query(query, Task, self.orm_hints)
        data = query.all()
        if (self.access_check):
            data = self._ctx.access_manager.filter_by_access('r', data)
        self.log.debug('%d tasks in result' % len(data))
        self._result = data
        return
