#
# Copyright (c) 2009, 2010, 2011, 2012. 2013, 2014
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
from datetime import datetime
import pytz
import time
from coils.core import CoilsException
from coils.net import ZOGIAPI, Protocol
from coils.core.omphalos import \
    Render, \
    render_account, \
    disassociate_omphalos_representation

ZOGI_DEFAULT_SEARCH_LIMIT = 150


class API(Protocol):
    __pattern__ = '^RPC2$'
    __namespace__ = 'zogi'
    __xmlrpc__ = True

    def __init__(self, context):
        self.context = context
        self.context.log.debug('zOGI API Handler Marshalled')
        self.api = ZOGIAPI(self.context)

    #
    # Public API
    #

    def getAuditEntries(self, floor):
        # TODO: Implement
        return list()

    def getFavoritesByType(self, kind, detail):
        kind = kind.lower()
        if (kind in ['contact', 'enterprise', 'project']):
            x = self.context.run_command('{0}::get-favorite'.format(kind))
            if (len(x) > 0):
                result = Render.Results(x, detail, self.context)
                return result
        return list()

    def unflagFavorites(self, ids):
        # TODO: Implement
        # ids may be an array of IDs or a CSV string of IDs
        # What is the return value of this very rarely used function?
        return None

    def flagFavorites(self, ids):
        # TODO: Implement
        # ids may be an array of IDs or a CSV string of IDs
        # What is the return value of this very rarely used function?
        return None

    def getLoginAccount(self, detail=65535):
        # Status: Implemeted
        # http://code.google.com/p/zogi/wiki/getLoginAccount
        account = self.context.run_command('account::get')
        defaults = self.context.run_command('account::get-defaults')
        return render_account(account, defaults, detail, self.context)

    def getObjectById(self, object_id, detail_level, flags={}, ):
        # Status: Implemented
        # 'objectId=%d level=%d' % (object_id, detail_level)
        if not detail_level:
            detail_level = 0
        kind = self.context.type_manager.get_type(object_id)
        if kind == 'Unknown':
            return {'entityName': 'Unknown', 'objectId': object_id, }
        method = 'get_{0}s_by_ids'.format(kind.lower(), )
        if hasattr(self.api, method):
            x = getattr(self.api, method)([object_id, ], )
            if ((x is not None) and (len(x) == 1)):
                result = Render.Result(x[0], detail_level, self.context, )
            else:
                result = {'entityName': 'Unknown', 'objectId': object_id, }
        else:
            result = {'entityName': 'Unknown', 'objectId': object_id, }
        return result

    def getObjectsById(self, object_ids, detail_level, flags={}):
        # Status: Implemented
        result = list()
        index = self.context.type_manager.group_ids_by_type(object_ids)
        for key in index.keys():
            method = 'get_{0}s_by_ids'.format(key.lower())
            if hasattr(self.api, method):
                x = getattr(self.api, method)(index[key], )
                if x:
                    self.context.log.debug(
                        'retrieved {0} {1} objects'.format(len(x), key, )
                    )
                    result.extend(x)
            else:
                self.context.log.debug(
                    'zOGI API does not support targetted kind "{0}"'.
                    format(key, )
                )
        result = Render.Results(result, detail_level, self.context, )
        return result

    def getNotifications(self, start, end):
        # TODO: Implement
        # http://code.google.com/p/zogi/wiki/getNotifications
        return list()

    def getObjectVersionsById(self, ids):
        return self.api.get_object_versions_by_id(ids)

    def listObjectsByType(self, kind, list_name):
        return self.api.list_objects_by_type(kind, list_name)

    def listPrincipals(self):
        return self.api.list_principals()

    def getAnchor(self, anchor):
        """
        Return the specified sychronization anchor
        """
        return self.api.get_anchor(anchor)

    def getTombstone(self, object_id):
        """
        Return the tombstone of the specified object, if any
        """
        return self.api.get_tombstone(object_id, {})

    def getSchedule(self):
        """
        Return the contents of the workflow schedule.
        """
        return self.api.get_schedule()

    def getTypeOfObject(self, object_id):
        """
        Returns a string identifying the type of the specified object.
        If the object is not available an "Unknown" is returned.
        :param object_id: ObjectId of an entity
        """
        object_id = int(object_id)
        return self.context.type_manager.get_type(object_id)

    def putObject(self, payload):
        '''
        Method for creating or updating a server entity.
        :param payload: An Omphalos representation of the entity.
        '''

        def process_put_object_payload(context, api, payload):
            if not isinstance(payload, dict):
                raise CoilsException(
                    'Unanticipated putObject payload type "{0}"'.
                    format(type(payload), )
                )

            if payload.has_key('entityName'):
                entity_name = payload['entityName'].lower()

            if payload.has_key('_FLAGS'):
                flags = payload['_FLAGS']
                '''
                if FLAGS is a string zOGI assumes it is a CSV so it splits it
                into the list
                '''
                if isinstance(flags, basestring):
                    flags = flags.split(',')
            else:
                flags = list()

            '''
            if the client is using associative Omphalos it needs to be
            disassociated
            '''
            if context.user_agent_description['omphalos']['associativeLists']:
                payload = disassociate_omphalos_representation(payload)

            return getattr(
                self.api, 'put_{0}'.format(entity_name, )
            )(payload, flags, )

        result = None
        if isinstance(payload, list):
            for tmp in payload:
                result = process_put_object_payload(
                    self.context, self.api, tmp,
                )
        else:
            result = process_put_object_payload(
                self.context, self.api, payload,
            )

        if result:
            # it worked, so commit
            self.context.commit()

        if not isinstance(result, dict):
            # Render the result into an Omphalos dictionary
            result = Render.Result(result, 65535, self.context, )

        return result

    def deleteObject(self, payload, flags={}):

        object_id = None
        entity_kind = None

        if (isinstance(payload, int) or isinstance(payload, basestring)):
            try:
                object_id = int(payload)
            except:
                raise CoilsException(
                    'Specified objectId "{0}" is not numeric.'.
                    format(object_id, )
                )
        elif isinstance(payload, dict):
            if 'objectId' in payload:
                object_id = payload.get('objectId')
                try:
                    object_id = int(object_id)
                except:
                    raise CoilsException(
                        'Specified objectId "{0}" is not numeric.'.
                        format(object_id, )
                    )
            else:
                entity_kind = payload.get('entityName', None, )
                if not entity_kind:
                    raise CoilsException(
                        'Neither entityName or objectId specified in '
                        'deleteObject request'
                    )
                entity_kind = entity_kind.lower()
        else:
            raise CoilsException(
                'Unexpected parameter type "{0}" provided to deleteObject'.
                format(type(payload), )
            )

        if object_id:
            entity_kind = self.context.type_manager.get_type(object_id)
            if entity_kind:
                entity_kind = entity_kind.lower()
            else:
                raise CoilsException(
                    'Cannot determine entity type for OGo#{0}'.
                    format(object_id, )
                )
            x = getattr(
                self.api, 'delete_{0}'.format(entity_kind, )
            )(object_id, flags, )
        else:
            x = getattr(
                self.api, 'delete_{0}'.format(entity_kind, )
            )(payload, flags, )

        if x is None:
            return False
        self.context.commit()
        return x

    def searchForObjects(self, kind, criteria, detail, flags=None):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/searchForObjects
        # Set-up default flags

        effective_flags = {
            'limit':  100,
            'revolve': False,
            'filter': None,
            'sudo': None,
        }
        '''
        If flags were provided by the call read those overtop our default flags
        '''
        if isinstance(flags, dict):
            effective_flags.update(flags)
            if effective_flags['revolve'] == 'YES':
                effective_flags['revolve'] = True
            else:
                effective_flags['revolve'] = False

        # SUDO to a different context, if requested
        if isinstance(effective_flags['sudo'], basestring):
            context_ids = [
                int(x.strip()) for x in effective_flags['sudo'].split(',')
            ]
            self.context.su(context_ids=context_ids, go_anon=True, )
            self.context.log.debug(
                'Operational context changed by SU operation to {0}'.
                format(self.context.context_ids, ))

        # Do Search

        start = time.time()
        x = getattr(self.api,
                    'search_{0}'.format(kind.lower()))(criteria,
                                                       effective_flags,
                                                       detail_level=detail)
        self.context.log.info(
            'searchForObjects search command consumed {0}s'.
            format(time.time() - start))
        # Process results of search
        result = []
        start = time.time()
        if x:
            result.extend(
                Render.Results(
                    [y for y in x if hasattr(y, '__entityName__')],
                    detail,
                    self.context))
            result.extend([y for y in x if not hasattr(y, '__entityName__')])
        self.context.log.info(
            'Rendering searchForObjects results consumed {0}s'.
            format(time.time() - start, ))
        self.context.log.info(
            'searchForObjects returning {0} entities'.
            format(len(result)))
        result = self.api.process_eo_filter(result, effective_flags['filter'])
        return result
