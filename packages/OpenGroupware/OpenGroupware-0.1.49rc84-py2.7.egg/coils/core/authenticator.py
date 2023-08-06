# Copyright (c) 2009, 2012, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import logging
import hashlib
from exception import AuthenticationException
from coils.foundation import Contact, ServerDefaultsManager, Backend
from sqlalchemy import and_


class Authenticator(object):
    # TODO: Support some reasonable kind of cache (a class cache is worthless)
    _hosts = None
    _debug = None

    def __init__(self, metadata, options, password_cache=None):
        self.log = logging.getLogger('authenticator')
        self.account = None

        self.password_cache = password_cache
        if password_cache is not None:
            self.password_cache = password_cache
            self.log.debug(
                'Password cache of {0} entries provided to authenticator {1}'.
                format(len(password_cache), self, )
            )
        else:
            self.log.debug(
                'Authenticator {0} was not provided with a password cache.'.
                format(self, )
            )

        self.set_metadata(metadata)
        self.set_options(options)
        if (self.login is not None):
            self.log.debug('login detected, trying authentication')
            if (self.options.get('stripDomain', False)):
                self.set_login(self.login.split('\\')[-1:][0])
            # Issue#102 : Support for the LSUseLowercaseLogin default
            if (self.options.get('lowerLogin', False)):
                self.set_login(self.login.lower())
            # Issue#101: Support "AllowSpacesInLogin" default
            if (self.options.get('allowSpaces', False)):
                pass
            else:
                self.set_login(self.login.replace(' ', ''))

        # Call the authenticate method
        if (self.login is not None):
            self.authenticate()
        else:
            self.log.debug('No credentials, not attempting authentication')
            raise AuthenticationException(
                'No credentials, not attempting authentication'
            )

    def cache_successful_credentials(self, username, credential):

        if self.password_cache is None or not credential:
            return

        salt = "1Ha7"
        secret_hash = hashlib.md5(
            '{0}:{1}'.format(salt, credential)
        ).hexdigest()
        self.password_cache[username] = secret_hash

        return

    def check_cached_credentials(self, username, credential):

        if self.password_cache is None or not credential:
            return False

        salt = "1Ha7"
        secret_hash = hashlib.md5(
            '{0}:{1}'.format(salt, credential, )
        ).hexdigest()

        if self.password_cache.get(username, None) == secret_hash:
            return True

        return False

    def revoke_cached_credentials(self, username):
        if self.password_cache is None or username is None:
            return

        try:
            del self.password_cache[username]
        except KeyError:
            pass

        return

    @property
    def debugging_enabled(self):
        if (Authenticator._debug is None):
            if (
                ServerDefaultsManager().
                bool_for_default('LSAuthDebugEnabled')
            ):
                Authenticator._debug = True
            else:
                Authenticator._debug = False
        return Authenticator._debug

    def set_options(self, options):
        self._options = options

    @property
    def options(self):
        return self._options

    def set_metadata(self, metadata):
        self._metadata = metadata

    @property
    def metadata(self):
        return self._metadata

    @property
    def login(self):
        return self.metadata['authentication'].get('login', None)

    def set_login(self, login):
        self._metadata['authentication']['login'] = login

    @property
    def secret(self):
        return self.metadata['authentication'].get('secret', None)

    def authenticate(self):
        ''' Perform token based authentication that should ALWAYS work
            regardless of identification/authentication backend.
            TODO: Implement token based authentication, see OGo/J '''
        # NOTE: This is the method that child classes want to override
        # WARN: Currently we only support BASIC (aka PLAIN), but someday....
        if self._check_tokens():
            return True
        if self._check_trusted_hosts():
            return True
        self.account = self.get_login()
        return False

    def _check_tokens(self):
        # TODO: Implement
        # How does OGo/J do this?
        if (self.debugging_enabled):
            self.log.warn("Tokens authentication not implemented.")
        return False

    def _check_trusted_hosts(self):
        if ('connection' in self.metadata):
            if (self.debugging_enabled):
                self.log.debug('Checking Trusted Host authentication.')
            # Context is for a network connected client
            connection = self.metadata.get('connection')
            if (self.debugging_enabled):
                self.log.debug(
                    'Client connection from {0}'.
                    format(connection.get('client_address'))
                )
            if (
                (connection.get('client_address').lower() in
                 self.options.get('trustedHosts', [])) and
                ('claimstobe' in self.metadata['authentication'])
            ):
                self.set_login(self.metadata['authentication']['claimstobe'])
                self.account = self.get_login()
                self.log.info(
                    'Trusted Host authentication as "{0}" (objectId#{1}) '
                    'from remote "{2}" approved.'.format(
                        self.account.login,
                        self.account.object_id,
                        connection.get('client_address')
                    )
                )
                return True
            else:
                if (self.debugging_enabled):
                    self.log.debug(
                        'Trusted Host autentication denied from {0}'.
                        format(
                            connection.get('client_address'),
                        )
                    )
        return False

    def get_login(self):
        # TODO: Can we do something short of loading the entire contact entity?
        if (self.debugging_enabled):
            self.log.debug(
                'Checking database for login "{0}".'.format(self.login, )
            )
        db = Backend.db_session()
        query = db.query(Contact).\
            filter(
                and_(
                    Contact.login == self.login,
                    Contact.is_account == 1,
                    Contact.status != 'archived',
                )
            ).enable_eagerloads(False)
        data = query.all()
        if (len(data) > 1):
            self.log.error(
                'Multiple accounts match login {0); database '
                'integrity suspect.'.format(self.login, )
            )
            raise AuthenticationException(
                'Multiple accounts match login; database integrity suspect.'
            )
        elif (len(data) == 0):
            if (self.debugging_enabled):
                self.log.debug('No such account as {0}.'.format(self.login))
            result = self.provision_login()
            if (result is None):
                if (self.debugging_enabled):
                    self.log.debug(
                        'Unable to auto-provision for login {0}.'.
                        format(self.login, )
                    )
                raise AuthenticationException(
                    'No such account as {0}.'.format(self.login)
                )
            return result
        elif (len(data) == 1):
            if (self.debugging_enabled):
                self.log.debug(
                    'Found account for login "{0}".'.format(self.login)
                )
            return data[0]
        else:
            raise AuthenticationException(
                'Undefined authentication error - contact developers.'
            )

    def provision_login(self):
        '''
        Authenticators can override this method to support auto-provisioning of
        user accounts.  If the account cannot be auto-provsioned this method
        should return None; if the authenticator does not support provisioning
        just return None.
        '''
        return None

    def authenticated_id(self):
        if (self.account is not None):
            return self.account.object_id
        return -1

    def authenticated_login(self):
        if (self.account is not None):
            return self.account.login
        return None
