#!/usr/bin/env python
# Copyright (c) 2011, 2012, 2013, 2014
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
import base64
import hashlib
from datetime import datetime, timedelta
from coils.core import \
    CoilsException, \
    NotImplementedException, \
    CoilsUnreachableCode, \
    Route, \
    Process, \
    Collection, \
    Contact, \
    Enterprise, \
    CTag, \
    Team, \
    Project, \
    PropertyManager
from coils.foundation import \
    OGO_ROLE_WORKFLOW_DEVELOPERS, \
    OGO_ROLE_DATA_MANAGER, \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_HELPDESK, \
    OGO_ROLE_WORKFLOW_ADMIN
from eofilter import process_eo_filter
from schedule import \
    render_workflow_schedule, \
    render_workflow_schedule_entry, \
    parse_workflow_schedule_entry

#  WARN: the code references a COILS_TIMEZONES, but that is never initialized


def Caseless_Get(dict_, key_):
    if key_ in dict_:
        value = dict_[key_]
    else:
        for key, value in dict_.items():
            if key_.lower() == key.lower():
                value = dict_[key]
                break
        else:
            value = None
    return value


class ZOGIAPI(object):

    def __init__(self, context):
        self.context = context

    def process_eo_filter(self, results_in, filter_string):
        return process_eo_filter(results_in, filter_string)

    #
    # getObjectById methods
    #

    def get_accounts_by_ids(self, ids):
        # TODO: Implement
        return list()

    def get_appointments_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('appointment::get',
                                     ids=ids,
                                     orm_hints=('zogi', detail_level, ))
        return x

    def get_contacts_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('contact::get', ids=ids, )
        return x

    def get_collections_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('collection::get', ids=ids, )
        return x

    def get_documents_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('document::get', ids=ids, )
        return x

    def get_enterprises_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('enterprise::get', ids=ids, )
        return x

    def get_folders_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('folder::get', ids=ids, )
        return x

    def get_processs_by_ids(self, ids, detail_level=0):
        # Yes, "processs" has an extra "s", that is not a typo
        x = self.context.run_command('process::get', ids=ids, )
        return x

    def get_projects_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('project::get',
                                     ids=ids,
                                     orm_hints=('zogi', detail_level, ), )
        return x

    def get_resources_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('resource::get', ids=ids, )
        return x

    def get_routes_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('route::get', ids=ids, )
        return x

    def get_routegroups_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('routegroup::get', ids=ids, )
        return x

    def get_tasks_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('task::get',
                                     ids=ids,
                                     orm_hints=('zogi', detail_level, ), )
        return x

    def get_teams_by_ids(self, ids, detail_level=0):
        x = self.context.run_command('team::get', ids=ids, )
        return x

    def get_unknowns_by_ids(self, ids, detail_level=0):
        # TODO: Implement
        return list()
        x = list()
        for object_id in ids:
            x.append({'entityName': 'Unknown',
                      'objectId': object_id, })
        return x

    # searchForObjects methods

    def search_account(self, criteria, flags, detail_level=0):
        # TODO: Implement
        raise 'Not Implemented'

    def search_appointment(self, criteria, flags, detail_level=0):
        '''
        TODO: extend the zOGI API to include support for startDate +
        timespan (in days?)
        '''
        params = {}
        # appointmentType (kinds of appointments)
        if 'appointmentType' in criteria:
            params['kinds'] = criteria['appointmentType']
        # startDate
        if 'startDate' in criteria:
            x = criteria['startDate']
            if (isinstance(x, basestring)):
                if (len(x) == 10):
                    x = datetime.strptime(x, '%Y-%m-%d')
                    x = x + timedelta(days=1) - timedelta(minutes=1)
                elif (len(x) == 16):
                    x = datetime.strptime(x, '%Y-%m-%d %H:%M')
            params['start'] = x
        # endDate
        if 'endDate' in criteria:
            x = criteria['endDate']
            if (isinstance(x, basestring)):
                if (len(x) == 10):
                    x = datetime.strptime(x, '%Y-%m-%d')
                    x = x + timedelta(days=1) - timedelta(minutes=1)
                elif (len(x) == 16):
                    x = datetime.strptime(x, '%Y-%m-%d %H:%M')
            params['end'] = x
        # Clean up participants value if one provided
        # This is turned into a list of integers (presumed object-ids)
        # The appointment::get-range command will take care of the
        # internal ugliness of converting the object ids of resources
        # into resource names.
        if 'participants' in criteria:
            parts = criteria['participants']
            if (isinstance(parts, int)):
                parts = [parts, ]
            elif (isinstance(parts, basestring)):
                r = list()
                for part in parts.split(','):
                    r.append(int(part.strip()))
                parts = r
            elif (isinstance(parts, list)):
                r = list()
                for part in parts:
                    r.append(int(part))
                parts = r
            else:
                raise CoilsException(
                    'Unable to parse participants value for search request.')
            params['participants'] = parts
        return self.context.run_command('appointment::get-range', **params)

    def polish_company_search_params(self, criteria, flags):
        # Used by _search_contact and _search_enterprise

        revolve = flags.get('revolve', False)
        if isinstance(revolve, basestring):
            revolve = revolve.upper()
            if revolve == 'YES':
                revolve = True
            else:
                revolve = False
        elif isinstance(revolve, bool):
            pass
        else:
            raise CoilsException(
                'Revolve value of type {0} not understood'.
                format(type(revolve), ))

        params = {'limit': int(flags.get('limit', 150)),
                  'revolve': revolve, }

        if 'scope' in flags:
            params['contexts'] = [int(flags['scope']), ]

        if (isinstance(criteria, list)):
            params['criteria'] = criteria
        elif (isinstance(criteria, dict)):
            params['criteria'] = [criteria]
        else:
            raise CoilsException('Unable to comprehend criteria')

        return params

    def search_collection(self, criteria, flags, detail_level=0):
        if (isinstance(criteria, basestring)):
            if criteria.strip().lower() == 'list':
                return self.context.run_command('collection::list',
                                                properties=[Collection, ], )
            else:
                raise CoilsException(
                    'Unknown string set-name in Collection Search')
        # Normal Search
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('collection::search', **params)

    def search_contact(self, criteria, flags, detail_level=0):
        params = self.polish_company_search_params(criteria, flags)
        params['orm_hints'] = ('zogi', detail_level, )
        return self.context.run_command('contact::search', **params)

    def search_enterprise(self, criteria, flags, detail_level=0):
        params = self.polish_company_search_params(criteria, flags)
        params['orm_hints'] = ('zogi', detail_level, )
        return self.context.run_command('enterprise::search', **params)

    def search_process(self, criteria, flags, detail_level=0):
        # TODO: Implement!
        if (isinstance(criteria, basestring)):
            if criteria.strip().lower() == 'list':
                return self.context.run_command('process::list',
                                                properties=[Process, ], )
            else:
                raise CoilsException(
                    'Unknown string set-name in Process Search')
        # Normal Search
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('process::search', **params)

    def search_project(self, criteria, flags, detail_level=0):
        '''
        TODO: Implement zOGI-ness
        Supported keys: kind, name, number, objectId, ownerObjectId, and
        placeHolder. If a conjunction is specified (either "AND" or "OR") then
        the name and number keys are compared fuzzy, otherwise all keys must
        match exactly [AND].
        '''
        if isinstance(criteria, basestring):
            if criteria == 'list':
                return self.context.run_command('account::get-projects')
            else:
                return list()
        query = list()
        if ('conjunction' in criteria):
            expression = 'ILIKE'
            conjunction = criteria['conjunction']
        else:
            expression = 'EQUALS'
            conjunction = 'AND'
        for key in (
            'kind', 'name', 'number', 'objectid', 'ownerobjectid',
            'placeholder',
        ):
            value = Caseless_Get(criteria, key)
            if value:
                if (expression == 'EQUALS') and isinstance(value, basestring):
                    value = value
                else:
                    value = '%{0}%'.format(value)
                query.append({'conjunction': conjunction,
                              'expression': expression,
                              'key': key,
                              'value': value, })
        return self.context.run_command('project::search',
                                        criteria=query,
                                        limit=flags.get('limit', None), )

    def search_resource(self, criteria, flags, detail_level=0):
        # Implemented: Implement "All Search", no criteria
        # Implemented: Implement "Exact Search", name or criteria
        # Implemented: "Fuzzy Search", indicated by any conjunction in criteria
        if (len(criteria) == 0):
            # All Search
            return self.context.run_command('resource::get')
        elif (isinstance(criteria, dict)):
            # Transform legacy zOGI search into a criteria search
            x = list()
            if ('conjunction' in criteria):
                conjunction = criteria['conjunction'].upper()
                expression = 'ILIKE'
                del criteria['conjunction']
            else:
                conjunction = 'AND'
                expression = 'EQUALS'
            for k in criteria:
                if (expression == 'ILIKE'):
                    value = '%{0}%'.format(criteria[k])
                else:
                    value = criteria[k]
                x.append({'key': k,
                          'value': value,
                          'expression': expression,
                          'conjunction': conjunction, })
            return self.context.run_command('resource::search', criteria=x)
        elif (isinstance(criteria, list)):
            # Assume the search is a well-formed criteria server
            # WARN: This feature is not supported by legacy/Obj-C zOGI
            return self.context.run_command('resource::search',
                                            criteria=criteria, )

    def search_route(self, criteria, flags, detail_level=0):
        # TODO: Implement!
        if (isinstance(criteria, basestring)):
            if criteria.strip().lower() == 'list':
                tmp = self.context.run_command('route::list',
                                               properties=[Route, ], )
                return tmp
            else:
                raise CoilsException('Unknown string set-name in Route Search')
        # Normal Search
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('route::search', **params)

    def search_lock(self, criteria, flags, detail_level=0):
        if isinstance(criteria, dict):
            object_id = int(criteria.get('targetObjectId', 0))
            if object_id:
                entity = self.context.type_manager.get_entity(object_id)
                if entity:
                    '''
                    TODO: allow operations and exclusivity to be specified
                    in the search criteria
                    '''
                    return self.context.lock_manager.locks_on(
                        entity, all_locks=True, )
            return []
        else:
            raise CoilsException('Lock search criteria must be a dictionary')

    def search_file(self, criteria, flags, detail_level=0):
        return self.search_document(
            criteria, flags, detail_level=detail_level, )

    def search_folder(self, criteria, flags, detail_level=0):
        params = self.polish_company_search_params(criteria, flags)
        params['orm_hints'] = ('zogi', detail_level, )
        return self.context.run_command(
            'folder::search', **params
        )

    def search_document(self, criteria, flags, detail_level=0):
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('document::search', **params)

    def search_task(self, criteria, flags, detail_level=0):
        result = []
        hints = ('zogi', detail_level, )
        if (isinstance(criteria, basestring)):
            if (criteria == 'archived'):
                return self.context.run_command('task::get-archived',
                                                orm_hints=hints, )
            elif (criteria == 'delegated'):
                return self.context.run_command('task::get-delegated',
                                                orm_hints=hints, )
            elif (criteria == 'todo'):
                return self.context.run_command('task::get-todo',
                                                orm_hints=hints, )
            elif (criteria == 'assigned'):
                return self.context.run_command('task::get-assigned',
                                                orm_hints=hints, )
            elif (criteria == 'current'):
                return self.context.run_command('task::get-current',
                                                orm_hints=hints, )
        elif (isinstance(criteria, list)):
            # TODO: verify criteria is something like a valid search criteria
            limit = flags.get('limit', 150)
            result = self.context.run_command('task::search',
                                              criteria=criteria,
                                              limit=limit,
                                              orm_hints=hints)
            return result
        raise CoilsException('Invalid search critieria')

    def search_time(self, criteria, flags, detail_level=0):
        utctime = self.context.get_utctime()
        usertime = self.context.get_localtime()
        is_dst = 0
        if (usertime.dst().seconds > 0):
            is_dst = 1
        return [{'entityName': 'time',
                 'gmtTime': utctime,
                 'isDST': is_dst,
                 'offsetFromGMT': self.context.get_offset_from(utctime),
                 'offsetTimeZone': self.context.get_timezone().zone,
                 'userTime': usertime, }, ]

    def search_timezone(self, criteria, flags, detail_level=0):
        raise NotImplementedException()
        '''
        result = [ ]
        utctime = self.context.get_utctime()
        for tz_def in COILS_TIMEZONES:
            tz = pytz.timezone(tz_def['code'])
            is_dst = 0
            if (tz.dst(utctime).seconds > 0):
                is_dst = 1
            result.append(
                {'abbreviation': tz_def['abbreviation'],
                 'description': tz_def['description'],
                 'entityName': 'timeZone',
                 'isCurrentlyDST': is_dst,
                 'offsetFromGMT':
                    as_integer((86400 - tz.utcoffset(utctime).seconds) * -1),
                'serverDateTime': utctime.astimezone(tz)})
            result.append(render_timezone(tz_def['code'], self.context))
        return result
        '''

    def search_team(self, criteria, flags, detail_level=0):
        # TODO: Implement "All" query
        # TODO: Implement "Mine" query
        if (criteria == 'all'):
            return self.context.run_command('team::get')
        elif (criteria == 'mine'):
            return self.context.run_command(
                'team::get', member_id=self.context.account_id, )
        raise NotImplementedException()

    # putObject methods

    def put_assignment(self, payload, flags):
        '''
        {'entityName': 'assignment',
                  'objectId': 92220,
                  'sourceEntityName': 'Team',
                  'sourceObjectId': 92180,
                  'targetEntityName': 'Contact',
                  'targetObjectId': 23330},

        Lookup the kind of sourceObjectId to determine the nature
        of the assignment.
        '''
        source_id = long(payload.get('sourceObjectId', 0))
        target_id = long(payload.get('targetObjectId', 0))
        if (not target_id) or (not source_id):
            pass

        source = self.context.type_manager.get_entity(source_id)
        target = self.context.type_manager.get_entity(target_id)
        if source is None or target is None:
            # TODO: raise error
            pass
        result = None
        if isinstance(source, Team) and isinstance(target, Contact):
            # assign contact to team
            result = self.context.run_command(
                'account::join-team', account=target, team=source, )
        elif isinstance(source, Enterprise) and isinstance(target, Contact):
            # TODO: Ticket#137
            result = self.context.run_command(
                'company::assign', source=source, target=target, )
        elif isinstance(source, Project) and isinstance(target, Contact):
            # TODO: Ticket#138
            result = self.context.run_command(
                'project::assign-contact', project=source, contact=target, )
        elif isinstance(source, Project) and isinstance(target, Enterprise):
            # TODO: Ticket#139
            result = self.context.run_command(
                'project::assign-enterprise',
                project=source, enterprise=target, )
        elif isinstance(source, Project) and isinstance(target, Team):
            # TODO: Ticket#140
            result = self.context.run_command(
                'project::assign-team', project=source, team=target, )
        if result:
            return source
        raise NotImplementedException(
            'Cannot assign {0} to  {1}'.format(target, source, )
        )

    def put_account(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_acl(self, payload, flags):
        object_id = Caseless_Get(payload, 'parentObjectId')
        context_id = Caseless_Get(payload, 'targetObjectId')
        operations = Caseless_Get(payload, 'operations')
        direction = Caseless_Get(payload, 'action')
        if not operations:
            operations = ''
        if not direction:
            direction = 'allowed'
        if direction not in ('allowed', 'denied'):
            raise CoilsException(
                'ACL "action" must be either "allowed" or "denied".')
        target = self.context.type_manager.get_entity(object_id)
        if target:
            self.context.run_command('object::set-acl',
                                     object=target,
                                     context_id=context_id,
                                     permissions=operations,
                                     action=direction, )
            return target
        raise CoilsException(
            'objectId#{0} not available for operation.'.
            format(object_id, ))

    def put_appointment(self, payload, flags):
        object_id = Caseless_Get(payload, 'objectId')
        if isinstance(object_id, basestring):
            object_id = int(object_id)
        if object_id:
            appointment = self.context.run_command('appointment::set',
                                                   values=payload,
                                                   id=object_id, )
        else:
            appointment = self.context.run_command('appointment::new',
                                                   values=payload, )
        return appointment

    def delete_assignment(self, payload, flags):
        '''
            { 'entityName': 'assignment',
              'objectId': 92220,
              'sourceEntityName': 'Team',
              'sourceObjectId': 92180,
              'targetEntityName': 'Contact',
              'targetObjectId': 23330 },

        Lookup the kind of sourceObjectId to determine the nature of
        the assignment.
        '''
        source_id = long(payload.get('sourceObjectId', 0))
        target_id = long(payload.get('targetObjectId', 0))
        if (not target_id) or (not source_id):
            pass

        source = self.context.type_manager.get_entity(source_id)
        target = self.context.type_manager.get_entity(target_id)
        if source is None or target is None:
            # TODO: raise error
            pass
        result = None
        if isinstance(source, Team) and isinstance(target, Contact):
            # unassign contact from team
            result = self.context.run_command(
                'account::leave-team', account=target, team=source, )
        elif isinstance(source, Enterprise) and isinstance(target, Contact):
            # TODO: ticket#142
            result = self.context.run_command(
                'company::unassign', source=source, target=target, )
        elif isinstance(source, Project) and isinstance(target, Contact):
            # TODO: ticket#145
            result = self.context.run_command(
                'project::unassign-contact', project=source, contact=target, )
        elif isinstance(source, Project) and isinstance(target, Enterprise):
            # TODO: ticket#143
            result = self.context.run_command(
                'project::unassign-enterprise',
                project=source, enterprise=target, )
        elif isinstance(source, Project) and isinstance(target, Team):
            # TODO: Ticket#144
            result = self.context.run_command('project::unassign-team',
                                              project=source,
                                              team=target, )
        if result:
            return True
        raise NotImplementedException(
            'Cannot unassign {0} from  {1}'.format(target, source, ))

    def put_collectionassignment(self, payload, flags):
        assigned_object_id = int(Caseless_Get(payload, 'assignedObjectId'))
        if assigned_object_id:
            entity = self.context.type_manager.get_entity(assigned_object_id)
            if entity:
                collection_id = \
                    int(Caseless_Get(payload, 'collectionObjectId'))
                collection = self.context.run_command('collection::get',
                                                      id=collection_id, )
                if collection and entity:
                    self.context.run_command('object::assign-to-collection',
                                             entity=entity,
                                             collection=collection, )
                    return collection
                else:
                    raise CoilsException(
                        'putObject of a collectionAssignment must '
                        'specify an existing collection')
        else:
            # TODO: raise exception
            return None

    def put_companyassignment(self, payload, flags):
        '''
        Process a putObject({companyAssignment})
        '''
        source_object_id = int(Caseless_Get(payload, 'sourceObjectId'))
        target_object_id = int(Caseless_Get(payload, 'targetObjectId'))
        if source_object_id and target_object_id:
            source = self.context.tm.get_entity(source_object_id)
            if source:
                target = self.context.tm.get_entity(target_object_id)
                if target:
                    return self.context.run_command('company::assign',
                                                    source=source,
                                                    target=target, )
                else:
                    raise CoilsException(
                        'Specified target entity "{0}" cannot be marshalled'.
                        format(target_object_id, ))
            else:
                raise CoilsException(
                    'Specified source entity "{0}" cannot be marshalled'.
                    format(source_object_id, ))
        else:
            raise CoilsException(
                'Incomplete payload; both a source and a target id must '
                'be specified')

    def delete_collectionassignment(self, payload, flags):
        """Delete a collectionAssignment entity."""

        if isinstance(payload, int):
            object_id = payload
        elif isinstance(payload, basestring):
            object_id = int(payload)
        elif isinstance(payload, dict):
            object_id = Caseless_Get(payload, 'objectId')
            if not object_id:
                collection_id = Caseless_Get(payload, 'collectionObjectId')
                assigned_id = Caseless_Get(payload, 'assignedObjectId')
                if collection_id and assigned_id:
                    collection = self.context.run_command(
                        'collection::get', id=collection_id,
                    )
                    if collection:
                        self.context.run_command(
                            'collection::delete-assignment',
                            collection=collection,
                            assigned_id=assigned_id,
                        )
                        return True
                    else:
                        raise CoilsException(
                            'CollectionId#{0} not available'.
                            format(collection_id, )
                        )
                else:
                    raise CoilsException(
                        'Both collectionObjectId and assignedObjectId '
                        'must be specified.'
                    )
        else:
            raise CoilsException('Unable to comprehend payload')
        result = self.context.run_command(
            'collection::get-assignment', id=object_id,
        )
        if (object_id in result):
            collection, entity = result[object_id]
            if (collection is not None) and (entity is not None):
                result = self.context.run_command(
                    'collection::delete-assignment',
                    collection=collection,
                    entity=entity,
                )
                return result
        return False

    def delete_contact(self, object_id, flags):
        contact = self.context.run_command('contact::get', id=object_id)
        if (contact is not None):
            return self.context.run_command('contact::delete', object=contact)
        return False

    def put_collection(self, payload, flags):
        object_id = Caseless_Get(payload, 'objectId')
        if (object_id == 0):
            collection = self.context.run_command('collection::new',
                                                  values=payload, )
        else:
            collection = self.context.run_command('collection::set',
                                                  values=payload,
                                                  id=object_id, )
        return collection

    def put_contact(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            contact = self.context.run_command('contact::new',
                                               values=payload, )
        else:
            contact = self.context.run_command('contact::set',
                                               values=payload,
                                               id=object_id, )
        return contact

    def delete_appointment(self, object_id, flags):
        object_id = long(object_id)
        if object_id:
            if 'deleteCycle' in flags:
                return self.context.run_command(
                    'appointment::delete', id=object_id, all=True,
                )
            else:
                return self.context.run_command(
                    'appointment::delete', id=object_id, all=False,
                )
            return True
        return False

    def delete_collection(self, object_id, flags):
        object_id = int(object_id)
        if (object_id):
            self.context.run_command('collection::delete', id=object_id)
            return True
        return False

    def put_defaults(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_file(self, payload, flags):
        return self.put_document(payload, flags)

    def put_document(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            document = self.context.run_command('document::new',
                                                values=payload, )
        else:
            document = self.context.run_command('document::get',
                                                id=object_id, )
            if document:
                document = self.context.run_command('document::set',
                                                    values=payload,
                                                    object=document, )
            else:
                raise CoilsException(
                    'Unable to marshall requested documentId#{0} for update'.
                    format(object_id))
        return document

    def delete_file(self, object_id, flags):
        return self.delete_document(object_id, flags)

    def delete_document(self, object_id, flags):
        '''
        Delete the specified document (file) object
        '''
        if self.context.run_command('document::delete', id=object_id, ):
            return True
        return False

    def delete_enterprise(self, object_id, flags):
        enterprise = self.context.run_command('enterprise::get',
                                              id=object_id, )
        if (enterprise is not None):
            return self.context.run_command('enterprise::delete',
                                            object=enterprise, )
        return False

    def put_enterprise(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            enterprise = self.context.run_command('enterprise::new',
                                                  values=payload, )
        else:
            enterprise = self.context.run_command('enterprise::set',
                                                  values=payload,
                                                  id=object_id, )
        return enterprise

    def put_lock(self, payload, flags):
        ''' { 'targetObjectId': opts.objectid,
              'token': 'asdklfasdkjlfasdlkjfadsf',
              'entityName': 'lock',
              'targetObjectId': opts.contextid,
              'action': 'denied',
              'operations': 'wdlvx' } '''
        object_id = int(payload['targetObjectId'])
        if object_id:
            entity = self.context.type_manager.get_entity(object_id)
            if entity:
                operations = payload.get('operations', 'w').lower()
                duration = int(payload.get('duration', 3600))
                result, lock = self.context.lock_manager.lock(
                    entity,
                    duration=duration,
                    data=None,
                    delete=True
                    if 'd' in operations else False,
                    write=True
                    if 'w' in operations else False,
                    run=True
                    if 'x' in operations else False,
                    exclusive=True
                    if payload.get('exclusive', 'NO').upper() == 'YES'
                    else False,
                )
                if result:
                    return lock
        return None

    def delete_lock(self, payload, flags):
        object_id = int(payload.get('targetObjectId', 0))
        if object_id:
            entity = self.context.type_manager.get_entity(object_id)
            if entity:
                if self.context.lock_manager.unlock(entity):
                    return True
        return None

    def delete_route(self, payload, flags):
        """
        Delete the specified route.
        """
        if isinstance(payload, long) or isinstance(payload, int):
            object_id = payload
        elif isinstance(payload, dict):
            object_id = Caseless_Get(payload, 'objectId')
        elif isinstance(payload, basestring):
            object_id = long(payload)
        else:
            raise CoilsException(
                'Incorrect type of {0} provided to delete method'.
                format(type(payload), ))

        route = self.context.run_command('route::get', id=object_id, )
        if route:
            return self.context.run_command('route::delete', object=route, )

        return False

    def delete_routegroup(self, payload, flags):
        """
        Delete the specified route group.
        """
        if isinstance(payload, long) or isinstance(payload, int):
            object_id = long(payload)
        elif isinstance(payload, dict):
            object_id = long(Caseless_Get(payload, 'objectId'))
        elif isinstance(payload, basestring):
            object_id = long(payload)
        else:
            raise CoilsException(
                'Incorrect type of {0} provided to delete method'.
                format(type(payload), ))

        group = self.context.run_command('routegroup::get', id=object_id, )
        if group:
            return self.context.run_command('routegroup::delete',
                                            object=group, )

        return False

    def put_folder(self, payload, flags):
        object_id = long(payload.get('objectId', 0))
        # TODO: Implement
        if (object_id == 0):
            folder = self.context.run_command('folder::new', values=payload)
        else:
            folder = self.context.run_command('folder::set',
                                              values=payload,
                                              id=object_id, )
        return folder

    def put_note(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_message(self, payload, flags):
        process_id = Caseless_Get(payload, 'processid')
        if not process_id:
            process_id = Caseless_Get(payload, 'processobjectid')
        if process_id:
            process = self.context.run_command('process::get', pid=process_id)
            if process:
                # Process exists, create message
                data = Caseless_Get(payload, 'data')
                if data:
                    data = base64.decodestring(payload['data'])
                else:
                    data = ''
                mimetype = Caseless_Get(payload, 'mimetype')
                if not mimetype:
                    mimetype = u'application/octet-stream'
                message = self.context.run_command(
                    'message::new',
                    process=process,
                    mimetype=mimetype,
                    label=Caseless_Get(payload, None),
                    data=data, )
                self.context.commit()
                '''
                Message commit'd to database - request process start
                A process start signal is always implied by message creation -
                in this manner the creation of a message may bring a process
                out of a parked state [if this is not the message the process
                was waiting for it will return itself to a parked state]
                '''
                self.context.run_command('process::start', process=process)
                return message
            else:
                # TODO: Raise exception
                pass
        else:
            # TODO: Raise exception
            pass

    def put_objectlink(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_objectproperty(self, payload, flags):
        """
        Create or update an objectProperty entity.  The entity must contain
        a parentobjectid and either a propertyName or a namespace +
        attribute (composite).
        """

        if not isinstance(payload, dict):
            raise CoilsException(
                'Unanticipated payload type of "{0}"'.format(type(payload), )
            )

        object_id = Caseless_Get(payload, 'parentobjectid')
        if not object_id:
            raise CoilsException(
                'ObjectProperty format invalid, no "parentObjectId" attribute')

        property_name = Caseless_Get(payload, 'propertyName')
        if property_name:
            namespace, attribute = \
                PropertyManager.Parse_Property_Name(property_name)
        else:
            namespace = Caseless_Get(payload, 'namespace')
            attribute = Caseless_Get(payload, 'attribute')

        if namespace and attribute:
            entity = self.context.type_manager.get_entity(object_id)
            if entity:
                value = Caseless_Get(payload, 'value')
                self.context.property_manager.set_property(
                    entity, namespace, attribute, value,
                )
                return entity
            else:
                raise CoilsException(
                    'Entity objectId#{0} unavailable.'.format(object_id, ))
        elif not namespace and not attribute:
            raise CoilsException(
                'ObjectProperty format invalid, no "namespace" and '
                '"attribute" attributes')
        elif not namespace:
            raise CoilsException(
                'ObjectProperty format invalid, no "namespace" attribute')
        elif not attribute:
            raise CoilsException(
                'ObjectProperty format invalid, no "attribute" attributes')
        else:
            raise CoilsUnreachableCode()

    def delete_objectproperty(self, payload, flags):
        """
        Delete an objectProperty entity.  The entity must contain a
        parentobjectid and either a propertyName or namespace + attribute
        (composite).
        """
        object_id = Caseless_Get(payload, 'parentobjectid')
        entity = self.context.type_manager.get_entity(object_id)
        if entity:
            property_name = Caseless_Get(payload, 'propertyName')
            if property_name:
                namespace, attribute = \
                    PropertyManager.Parse_Property_Name(property_name)
            else:
                namespace = Caseless_Get(payload, 'namespace')
                attribute = Caseless_Get(payload, 'attribute')
            if namespace and attribute:
                self.context.property_manager.delete_property(
                    entity, namespace, attribute, )
                return True
            else:
                raise CoilsException('ObjectProperty format invalid')
        else:
            raise CoilsException(
                'Entity objectId#{0} unavailable.'.
                format(object_id, ))

    def put_participantstatus(self, payload, flags):
        """
        Update a participants status in an appointment entity.

        Example payload: { 'comment': 'My very very very very long comment',
                           'objectId': 10621,
                           'rsvp': 1,
                           'status': 'TENTATIVE',
                           'entityName': 'ParticipantStatus' }

        If not specified the default status is NEEDS-ACTION and the rsvp and
        comment values will default to NULL.  A full representation of the
        appointment is returned upon success.
        """
        # The objectId is the objectId of THE APPOINTMENT, participantStatus is
        # unique in that it is a write-only entity.
        self.context.begin()
        object_id = int(payload['objectId'])
        self.context.run_command('participant::set',
                                 appointment_id=object_id,
                                 participant_id=self.context.account_id,
                                 status=payload.get('status', 'NEEDS-ACTION'),
                                 comment=payload.get('comment', None),
                                 rsvp=payload.get('rsvp',    None), )
        self.context.flush()
        appointment = \
            self.context.run_command('appointment::get', id=object_id, )
        return appointment

    def delete_process(self, object_id, flags):
        """
        Delete a workflow process.
        """
        process = self.context.run_command('process::get', id=object_id)
        if (process is not None):
            result = self.context.run_command('process::delete',
                                              object=process, )
            return result
        return False

    def put_process(self, payload, flags):
        """
        Create a workflow process
        """

        def get_priority(data, process):
            if 'priority' in data:
                priority = data['priority']
            elif process:
                priority = process.priority
            else:
                priority = 250
            return priority

        object_id = int(payload.get('objectId', 0))
        # determine if a request to queue has been made
        if payload.get('state', 'I') == 'Q':
            queue = True
        else:
            queue = False

        # Create or update?
        if object_id:
            process = self.context('process:get', pid=object_id)
            if process:
                payload['priority'] = get_priority(payload, None)
            else:
                # TODO: Fail gracefully, somehow?
                pass
            process = self.context('process::set',
                                   object=process,
                                   values=payload, )
        else:
            # alsy set state to I, don't let the client send us bogus states
            payload['state'] = 'I'
            payload['priority'] = get_priority(payload, None)
            '''
            get mimetype of the input from the payload, then remove
            that attribute
            '''
            mimetype = payload.get('mimetype', 'application/octet-stream')
            if 'mimetype' in payload:
                del payload['mimetype']
            # get the data from the payload, base64 decode it
            if 'data' in payload:
                data = base64.decodestring(payload['data'])
                payload['data'] = data
            else:
                payload['data'] = ''
            process = self.context.run_command('process::new',
                                               values=payload,
                                               mimetype=mimetype, )
            self.context.commit()
            if process and queue:
                self.context.run_command('process::start', process=process)
        return process

    def put_project(self, payload, flags):
        """
        Create or update a project entity.
        """
        object_id = Caseless_Get(payload, 'objectid')
        if object_id:
            project = self.context.run_command('project::set',
                                               values=payload,
                                               id=object_id, )
        else:
            project = self.context.run_command('project::new', values=payload)
        return project

    def put_resource(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_route(self, payload, flags):

        if 'markup' in payload:
            if payload['markup'].startswith('=='):
                payload['markup'] = base64.b64decode(payload['markup'])

        # Get the objectId, if any. Not providing an objectId implies creation.
        object_id = int(payload.get('objectId', 0))
        if object_id:
            route = self.context.run_command('route::get', id=object_id, )
            if not route:
                raise CoilsException(
                    'Unable to marshall OGo#{0} [Route] for update.'.
                    format(object_id, ))
            else:
                # Update
                route = self.context.run_command('route::set',
                                                 object=route,
                                                 values=payload, )
        else:
            # Create
            route = self.context.run_command('route::new', values=payload, )

        return route

    def put_routegroup(self, payload, flags):
        # Get the objectId, if any. Not providing an objectId implies creation.
        object_id = long(payload.get('objectId', 0))
        if object_id:
            group = self.context.run_command('routegroup::get', id=object_id, )
            if not group:
                raise CoilsException(
                    'Unable to marshall OGo#{0} [RouteGroup] for update.'.
                    format(object_id, ))
            else:
                # Update
                group = self.context.run_command('routegroup::set',
                                                 object=group,
                                                 values=payload, )
        else:
            # Create
            group = self.context.run_command('routegroup::new',
                                             values=payload, )

        return group

    def delete_scheduleentry(self, payload, flags):
        if isinstance(payload, dict):
            uuid = Caseless_Get(payload, 'uuid')
        elif isinstance(payload, basestring):
            uuid = payload
        else:
            raise CoilsException(
                'Payload for zOGI.delete_scheduleentry not understood'
            )
        self.context.run_command(
            'process::unschedule',
            uuid=uuid,
            raise_error=True,
        )
        return True

    def put_task(self, payload, flags):
        """
        Create or update a Task entity
        """
        object_id = int(payload.get('objectId', 0))
        if (object_id == 0):
            task = self.context.run_command('task::new', values=payload)
        else:
            task = self.context.run_command(
                'task::set',
                values=payload,
                id=object_id,
            )
        return task

    def put_tasknotation(self, payload, flags):
        """
        Perform an action on a task by create a task comment / notation.
        """
        object_id = int(payload.get('taskObjectId'))
        task = self.context.run_command('task::comment',
                                        values=payload,
                                        id=object_id, )
        return task

    def delete_task(self, object_id, flags):
        """
        Delete a task.
        """
        return self.context.run_command('task::delete', id=object_id)

    def delete_team(self, object_id, flags):
        """
        Delete a team.
        """
        return self.context.run_command('team::delete', id=object_id, )

    def put_team(self, payload, flags):
        '''
        Create or update a team entity.
        '''
        object_id = long(payload.get('objectId', 0))
        if object_id:
            team = self.context.run_command('team::set',
                                            values=payload,
                                            id=object_id, )
        else:
            team = self.context.run_command('team::new', values=payload, )
        return team

    def put_scheduleentry(self, payload, flags):
        # TODO: Complete Implementation
        args = parse_workflow_schedule_entry(payload, context=self.context, )
        job_id = self.context.run_command('process::schedule', **args)
        if job_id:
            schedule = self.context.run_command('workflow::get-schedule',
                                                raise_error=True,
                                                timeout=60, )
            if schedule:
                job = [x for x in schedule if x['UUID'] == job_id]
                if job:
                    # Got the scheduled job, send it back to the client
                    return render_workflow_schedule_entry(job[0])
                else:
                    # Can we get here?  Did the job already fire and expire
                    return {'entityName': 'Unknown', }
            else:
                # Can we get here?  No response?
                return {'entityName': 'Unknown', }
        else:
            # Can we get here?  An exception must have happened
            return {'entityName': 'Unknown', }

    def get_tombstone(self, object_id, flags):
        """
        Retrieve the tombstone of an object.  If no tombstone exists then an
        unknown entity is returned.  Note that all the security descriptions
        are lost when an object is deleted, so a user can potentially see that
        and object did previously exist that they could not have seen when it
        did exist.
        """
        object_id = int(object_id)
        audit_entry = self.context.run_command('object::get-tombstone',
                                               id=object_id, )
        if audit_entry:
            if audit_entry.actor is None:
                actor_text = None
            else:
                actor_text = audit_entry.actor.login
            return {'entityName': 'Tombstone',
                    'actor': actor_text,
                    'eventTime': audit_entry.datetime,
                    'actorObjectId': audit_entry.actor_id,
                    'deletedObjectId': audit_entry.context_id,
                    'message': audit_entry.message, }
        return {'entityName': 'Unknown'}

    def search_scheduleentry(self, criteria, flags, detail_level=0):
        """
        Returns the contents of the workflow schedule.
        """
        x = self.context.run_command('workflow::get-schedule',
                                     raise_error=True,
                                     timeout=60, )
        return render_workflow_schedule(x)

    def list_tasks(self, list_set):
        """
        Return a list of tasks.  Supported list sets are 'archived'
        and 'current'
        """
        if list_set == 'archived':
            tasks = self.context.run_command('task::get-archived')
        else:
            tasks = self.context.run_command('task::get-current')
        result = []
        for task in tasks:
            result.append({'objectId': task.object_id,
                           'entityName': task.__entityName__,
                           'displayName': task.get_display_name(),
                           'version': task.version, })
        return result

    def list_projects(self, list_set):
        """
        Return a list of projects.  Only list set supported is all available
        projects.
        """
        projects = self.context.run_command('account::get-projects')
        result = []
        for project in projects:
            result.append({'objectId': project.object_id,
                           'entityName': project.__entityName__,
                           'displayName': project.get_display_name(),
                           'internalName': project.number,
                           'parentObjectId':
                           project.parent_id if project.parent_id else 0,
                           'version': project.version, })
        return result

    def list_contacts(self, list_set):
        """
        Return a list of contacts.  Only currently supported list set
        is "users" which returns all contacts that are also accounts.
        """
        if list_set == 'users':
            contacts = self.context.run_command('account::get-all')
        else:
            contacts = []
        result = []
        for contact in contacts:
            result.append({'objectId': contact.object_id,
                           'entityName': 'Contact',
                           'displayName': contact.get_display_name(),
                           'version': contact.version,
                           'login': contact.login, })
        return result

    def list_principals(self):
        """
        Return a list of all accounts and teams that exist on the server.
        Clients may use this list action to get a list of 'principals' that
        exist on the server;  these ids can be used for owner ship,
        executor status, permissions, etc...
        """
        class NullResult(object):

            @property
            def string_value(self):
                return ''

        null = NullResult()

        result = []

        contacts = self.context.run_command('account::get-all',
                                            orm_hints=('zogi', 8, ), )
        for contact in contacts:
            email = contact.company_values.get('email1', null).string_value
            result.append(
                {'objectId': contact.object_id,
                 'entityName': 'Contact',
                 'displayName': contact.get_display_name(),
                 'version': contact.version if contact.version else 0,
                 'login': contact.login,
                 'email': email if email else '', })

        for team in self.context.run_command('team::get'):
            result.append(
                {'objectId': team.object_id,
                 'entityName': 'Team',
                 'displayName': team.get_display_name(),
                 'version': team.version if team.version else 0,
                 'login': team.number,
                 'email': team.email if team.email else '', }, )

        return result

    def list_teams(self, list_set):
        """
        Return a list of teams; currently it always returns all
        defined teams, no list set functionality is implemented.
        You can get pretty much the same thing from searchForObjects.
        """
        result = list()
        for team in self.context.run_command('team::get'):
            result.append(
                {'objectId': team.object_id,
                 'entityName': 'Team',
                 'displayName': team.get_display_name(),
                 'version': team.version, },
            )
        return result

    def get_object_versions_by_id(self, ids):
        '''
        TODO: Implement
        Result: [{'entityName': 'Appointment', 'version': [''],
                  'objectId': 29420},
                 {'entityName': 'Enterprise', 'version': [3],
                  'objectId': 21060},
                 {'entityName': 'Contact', 'version': [7],
                  'objectId': 10120}, ]
        http://code.google.com/p/zogi/wiki/getObjectVersionsById
        '''
        index = self.context.type_manager.group_ids_by_type(ids)
        result = []
        for key, object_ids in index.items:
            if key == 'Unknown':
                for object_id in object_ids:
                    result.append(
                        {'entityName': 'Unknown',
                         'version': [''],
                         'objectId': object_id, },
                    )
            else:
                x = getattr(self, 'get_%ss_by_ids' % key.lower())(index[key])
                if (x is None):
                    self.context.log.debug('result of Logic was None')
                else:
                    for entity in x:
                        result.append(
                            {'entityName': x.__entityName__,
                             'version': [x.version],
                             'objectId': x.object_id, },
                        )
        return result

    def list_objects_by_type(self, kind, list_name):
        entity_name = kind.lower()
        if hasattr(self, 'list_{0}s'.format(entity_name)):
            method = getattr(self, 'list_{0}s'.format(entity_name))
            return method(list_name)
        else:
            raise NotImplementedException(
                'Cannot list objects of type {0}'.format(kind, ))

    def get_performance(self, category):
        if isinstance(category, basestring):
            data = self.context.run_command('admin::get-performance-log',
                                            lname=category, )
            result = []
            '''
            Results must be a list, outer dictionaries are too confusing,
            so we flatten the performance results into a list moving the
            key into the value
            '''
            for key, value in data.items():
                value['command'] = key
                result.append(value)
            return result
        return []

    def ps(self):
        return self.context.run_command('workflow::get-process-list')

    def get_anchor(self, anchor):
        """
        Return a useful syncronization anchor for the specified anchor label.

        :param anchor: The label of the requested anchor.  This anchor must
            be one of task, appointment, contact, team, project, todo,
            delegated, archived, current, or assigned.
        """
        anchor = anchor.lower()

        ANCHOR_MAP = {
            'task': 'Job',
            'appointment': 'Date',
            'contact': 'Person',
            'team': 'Team',
        }

        def get_ctag_for_entity(context, kind):
            db = context.db_session()
            query = db.query(CTag).filter(CTag.entity == kind)
            ctags = query.all()
            if ctags:
                return ctags[0].ctag
            return '0'

        def generate_anchor_from_collection(collection):
            m = hashlib.sha512()
            for entry in collection:
                if hasattr(entry, 'version'):
                    m.update('{0}:{1};'.
                             format(entry.object_id, entry.version, ))
                else:
                    m.update('{0}:{1};'.format(entry.object_id, ))
            return m.hexdigest()

        if anchor in ANCHOR_MAP:
            return get_ctag_for_entity(self.context, ANCHOR_MAP[anchor])

        if anchor == 'archived':
            return generate_anchor_from_collection(
                self.context.run_command('task::get-archived')
            )
        elif anchor == 'delegated':
            return generate_anchor_from_collection(
                self.context.run_command('task::get-delegated')
            )
        elif anchor == 'todo':
            return generate_anchor_from_collection(
                self.context.run_command('task::get-todo')
            )
        elif anchor == 'assigned':
            return generate_anchor_from_collection(
                self.context.run_command('task::get-assigned')
            )
        elif anchor == 'current':
            return generate_anchor_from_collection(
                self.context.run_command('task::get-current')
            )
        elif anchor == 'project':
            return generate_anchor_from_collection(
                self.context.run_command('account::get-projects')
            )

        # TODO: Add anchor "personal" for personal calendar view
        # TODO: Add anchor "overview" for overview calendar view
        # TODO: Add anchor "favorite" for all favorite entities
        # TODO: Add anchor "process" for workflow processes

        raise CoilsException(
            'Request for unknown anchor "{0}"'.format(anchor, )
        )
