#
# Copyright (c) 2009, 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy import *
from coils.core import *
from keymap import COILS_COLLECTION_ASSIGNMENT_KEYMAP, COILS_COLLECTION_KEYMAP
from command import CollectionAssignmentFlyWeight


class SetAssignments(Command):
    __domain__ = "collection"
    __operation__ = "set-assignments"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        ## The collection in question
        self.collection = params.get('collection', None)

        ## Add these entities
        self.insert = params.get('insert',     None)

        ## Sync to this membership
        self.update = params.get('update',     None)

    def check_parameters(self):
        if (self.collection is None):
            raise CoilsException('No collection provided to set-assignments')

    def check_run_permissions(self):
        # Requires either WRITE OR ADMIN OR BOTH INSERT AND DELETE-ITEM (t)
        rights = self._ctx.access_manager.access_rights(self.collection, )
        if (
            (not set('wa').intersection(rights)) or
            (
                not
                (
                    set('i').intersection(rights) and
                    set('t').intersection(rights)
                )
            )
        ):
            raise AccessForbiddenException(
                'Insufficient access to {0}'.
                format(self.collection, )
            )

    def get_max_key(self):
        max_key = 0
        for assignment in self.collection.assignments:
            if (assignment.sort_key > max_key):
                max_key = assignment.sort_key
        return max_key

    def delete_assignments_by_id(self, ids):
        db = self._ctx.db_session()
        counter = 0
        query = db.query(CollectionAssignment).\
            filter(
                and_(
                    CollectionAssignment.collection_id == self.collection.object_id,
                    CollectionAssignment.assigned_id.in_(ids)
                )
            )
        for x in query.all():
            self._ctx.audit_at_commit(
                self.collection.object_id,
                '05_changed',
                'Removed OGo#{0} [{1}] from collection'.
                format(x.object_id, x.entity_name, )
            )
            self._ctx.audit_at_commit(
                x.object_id,
                '10_commented',
                'Removed from collection OGo#{0}'.
                format(self.collection.object_id, )
            )
            db.delete(x)
            counter += 1
        return counter

    def get_assignments(self):
        db = self._ctx.db_session()
        query = db.query(CollectionAssignment).\
            filter(
                CollectionAssignment.collection_id == self.collection.object_id
            )
        return query.all()

    def get_assigned_ids(self):
        return [x.assigned_id for x in self.get_assignments()]

    def _form_assignments(self, assignments):
        if (isinstance(assignments, list)):
            return [CollectionAssignmentFlyWeight(assignment, ctx=self._ctx, )
                    for assignment in assignments]
        else:
            raise CoilsException('Provided membership must be a list')

    def run(self):
        db = self._ctx.db_session()
        self.check_parameters()
        max_key = self.get_max_key()
        assigned_ids = self.get_assigned_ids()
        if self.insert:
            inserts = self._form_assignments(self.insert)
            counter = 0
            insert_ids = [x.object_id for x in inserts]
            for assignment in inserts:
                if assignment.object_id not in assigned_ids:
                    assigned_ids.append(assignment.object_id)
                    counter += 1
                    x = CollectionAssignment()
                    x.collection_id = self.collection.object_id
                    x.assigned_id = assignment.object_id
                    x.entity_name = assignment.entity_name
                    if assignment.sort_key is None:
                        max_key += 1
                        x.sort_key = max_key
                    else:
                        x.sort_key = assignment.sort_key
                    self._ctx.audit_at_commit(
                        self.collection.object_id,
                        '05_changed',
                        'Assigned OGo#{0} [{1}] to OGo#{2} [Collection]'.
                        format(x.assigned_id, x.entity_name, x.collection_id, )
                    )
                    db.add(x)
            self._result = (counter, 0, 0)
            return
        elif self.update is not None:
            '''
            UPDATE mode, sync the collection assignments to be those in the
            provided list; that list may be Omphalos dictionaries of entities,
            ORM entity objects, or object ids
            '''

            stats = [0, 0, 0, ]

            if (not isinstance(self.update, list)):
                raise CoilsException(
                    'Update value must be a list, received type "{0}"'.
                    format(type(self.update), )
                )

            if not self.update:
                # Short circuit - delete all assignments
                counter = 0
                for x in self.get_assignments():
                    db.delete(x)
                    stats[2] += 1
                self._result = stats
                # END
                return

            # Perform update sync

            meta = {}
            for update in self._form_assignments(self.update):
                meta[update.object_id] = update

            removes = self.get_assigned_ids()
            # UPDATE: Update Loop
            for x in self.get_assignments():
                if (x.assigned_id in meta):
                    if (meta[x.assigned_id].sort_key is not None):
                        x.sort_key = meta[x.assigned_id].sort_key
                    # Existing assignment updated, remove from meta
                    del meta[x.assigned_id]
                    # Remove this id from the ids to be removed
                    removes.remove(x.assigned_id)
                    stats[1] += 1

            # INSERT: what items were not removed from meta in the update loop
            for assigned_id, assignment in meta.iteritems():
                '''
                TODO: Filter out dis-allowed kinds, they must all be
                first-class proper entities
                '''
                z = CollectionAssignment()
                z.collection_id = self.collection.object_id
                z.assigned_id = assignment.object_id
                z.entity_name = assignment.entity_name
                if assignment.sort_key:
                    z.sort_key = assignment.sort_key
                else:
                    max_key += 1
                    z.sort_key = max_key
                self._ctx.audit_at_commit(
                    self.collection.object_id,
                    '10_commented',
                    'Assigned OGo#{0} [{1}] to collection OGo#{2}'.
                    format(z.assigned_id,
                           z.entity_name,
                           z.collection_id, )
                )
                db.add(z)
                stats[0] += 1

            # DELETE: Purge expired assignments
            if (len(removes) > 0):
                stats[2] = self.delete_assignments_by_id(removes)
            self._result = stats
            return
        else:
            raise CoilsException(
                'No appropriate mode for this collection::set-assignments'
            )
