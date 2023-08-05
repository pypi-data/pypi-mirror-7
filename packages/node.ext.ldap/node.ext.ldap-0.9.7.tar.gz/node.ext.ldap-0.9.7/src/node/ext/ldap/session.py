# -*- coding: utf-8 -*-
import ldap
from . import (
    BASE,
    LDAPConnector,
    LDAPCommunicator,
)
from .base import testLDAPConnectivity


class LDAPSession(object):
    """LDAP Session binds always.

    all strings must be utf8 encoded!
    """

    def __init__(self, props):
        self._props = props
        connector = LDAPConnector(props=props)
        self._communicator = LDAPCommunicator(connector)

    def checkServerProperties(self):
        """Test if connection can be established.
        """
        res = testLDAPConnectivity(props=self._props)
        if res == 'success':
            return (True, 'OK')
        else:
            return (False, res)

    def _get_baseDN(self):
        baseDN = self._communicator.baseDN
        return baseDN

    def _set_baseDN(self, baseDN):
        """baseDN must be utf8-encoded.
        """
        self._communicator.baseDN = baseDN

    baseDN = property(_get_baseDN, _set_baseDN)

    def ensure_connection(self):
        """If LDAP directory is down, bind again and retry given function.

        XXX: * Improve retry logic
             * Extend LDAPSession object to handle Fallback server(s)
        """
        if self._communicator._con is None:
            self._communicator.bind()

    def search(self, queryFilter='(objectClass=*)', scope=BASE, baseDN=None,
               force_reload=False, attrlist=None, attrsonly=0,
               page_size=None, cookie=None):
        if queryFilter in ('', u'', None):
            # It makes no sense to really pass these to LDAP, therefore, we
            # interpret them as "don't filter" which in LDAP terms is
            # '(objectClass=*)'
            queryFilter = '(objectClass=*)'
        self.ensure_connection()
        res = self._communicator.search(queryFilter, scope, baseDN,
                                        force_reload, attrlist, attrsonly,
                                        page_size, cookie)
        if page_size:
            res, cookie = res
        # ActiveDirectory returns entries with dn None, which can be ignored
        res = filter(lambda x: x[0] is not None, res)
        if page_size:
            return res, cookie
        return res

    def add(self, dn, data):
        self.ensure_connection()
        self._communicator.add(dn, data)

    def authenticate(self, dn, pw):
        """Verify credentials, but don't rebind the session to that user
        """
        # Let's bypass connector/communicator until they are sorted out
        con = ldap.initialize(self._props.uri)
        try:
            con.simple_bind_s(dn, pw)
        except ldap.INVALID_CREDENTIALS:
            return False
        else:
            return True

    def modify(self, dn, data, replace=False):
        """Modify an existing entry in the directory.

        dn
            Modification DN

        #data
        #    either list of 3 tuples (look at
        #    node.ext.ldap.base.LDAPCommunicator.modify for details), or
        #    a dictionary representing the entry or parts of the entry.
        #    XXX: dicts not yet

        replace
            if set to True, replace entry at DN entirely with data.
        """
        self.ensure_connection()
        result = self._communicator.modify(dn, data)
        return result

    def delete(self, dn):
        self._communicator.delete(dn)

    def passwd(self, userdn, oldpw, newpw):
        self.ensure_connection()
        result = self._communicator.passwd(userdn, oldpw, newpw)
        return result

    def unbind(self):
        self._communicator.unbind()
