# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

"""Tests for module :class:`stoqlib.database.runtime`"""

from stoqlib.database.exceptions import InterfaceError
from stoqlib.database.properties import UnicodeCol
from stoqlib.database.runtime import new_store
from stoqlib.domain.base import Domain
from stoqlib.domain.test.domaintest import DomainTest


class WillBeCommitted(Domain):
    __storm_table__ = 'will_be_committed'
    SQL_DROP = """DROP TABLE IF EXISTS will_be_committed;"""
    SQL_CREATE = """CREATE TABLE will_be_committed (
        id uuid PRIMARY KEY DEFAULT uuid_generate_v1(),
        test_var text,
        te_id bigint UNIQUE REFERENCES transaction_entry(id)
        );"""

    test_var = UnicodeCol()

    def __init__(self, *args, **kwargs):
        super(WillBeCommitted, self).__init__(*args, **kwargs)
        self.reset()

    def __storm_loaded__(self):
        super(WillBeCommitted, self).__storm_loaded__()
        self.reset()

    def reset(self):
        self.was_created = False
        self.was_updated = False
        self.was_deleted = False

        self.update_test_var_on_update = False
        self.on_update_called_count = 0

    def on_create(self):
        self.was_created = True

    def on_delete(self):
        self.was_deleted = True

    def on_update(self):
        self.was_updated = True

        if self.update_test_var_on_update:
            if self.on_update_called_count < 2:
                self.test_var = "%s+" % self.test_var

        self.on_update_called_count += 1


class StoqlibTransactionTest(DomainTest):

    def setUp(self):
        super(StoqlibTransactionTest, self).setUp()

        self.store.execute(''.join((WillBeCommitted.SQL_DROP,
                                    WillBeCommitted.SQL_CREATE)))
        self.store.commit()

    def test_dirty_flag(self):
        # Creating an object should set its dirty flag to True
        store = new_store()
        obj = WillBeCommitted(store=store)
        obj_id = obj.id
        store.commit()
        self.assertTrue(obj.te.dirty)

        # Reset the flag to test changing the object
        obj.te.dirty = False
        store.commit()
        store.close()

        # Get the same object from a new connection
        store = new_store()
        obj = store.get(WillBeCommitted, obj_id)

        # The flag must be False
        self.assertFalse(obj.te.dirty)

        # Changing the object and commiting should update the flag
        obj.test_var = u'asd'
        store.commit()
        self.assertTrue(obj.te.dirty)
        store.close()

    def test_rollback_to_savepoint(self):
        obj = WillBeCommitted(store=self.store, test_var=u'XXX')
        obj2 = WillBeCommitted(store=self.store, test_var=u'foo')
        self.assertEqual(obj.test_var, u'XXX')
        self.assertEqual(obj2.test_var, u'foo')

        self.store.savepoint('sp_1')
        obj.test_var = u'YYY'
        obj2.test_var = u'foo1'
        self.store.savepoint('sp_2')
        obj.test_var = u'ZZZ'
        self.store.savepoint('sp_3')
        obj.test_var = u'WWW'

        self.assertEqual(obj.test_var, u'WWW')

        # Test rollback to last savepoint
        self.store.rollback_to_savepoint('sp_3')
        self.assertEqual(obj.test_var, u'ZZZ')
        self.assertEqual(obj2.test_var, u'foo1')

        # Test rollback to a previous savepoint
        self.store.rollback_to_savepoint('sp_1')
        self.assertEqual(obj.test_var, u'XXX')
        self.assertEqual(obj2.test_var, u'foo')

        # Test rollback to an unknown savepoint
        self.assertRaises(ValueError, self.store.rollback_to_savepoint,
                          name='Not existing savepoint')

    def test_close(self):
        store = new_store()
        self.assertFalse(store.obsolete)
        store.close()
        self.assertTrue(store.obsolete)

        self.assertRaises(InterfaceError, store.close)
        self.assertRaises(InterfaceError, store.commit)
        self.assertRaises(InterfaceError, store.rollback)
        self.assertRaises(InterfaceError, store.fetch, None)
        self.assertRaises(InterfaceError, store.savepoint, 'XXX')
        self.assertRaises(InterfaceError, store.rollback_to_savepoint, 'XXX')

    def test_transaction_commit_hook(self):
        # Dummy will only be asserted for creation on the first commit.
        # After that it should pass all assert for nothing made.
        dummy_obj = WillBeCommitted(store=self.store,
                                    test_var=u'XXX')

        obj = WillBeCommitted(store=self.store,
                              test_var=u'AAA')
        # Test obj being created on database
        self.store.commit()
        self._assert_created(obj)
        self._assert_created(dummy_obj)
        obj.reset()
        dummy_obj.reset()

        # Test obj being updated on the same object it was created
        obj.test_var = u'BBB'
        self.store.commit()
        self._assert_updated(obj)
        self._assert_nothing_made(dummy_obj)
        obj.reset()

        # Test obj being modified inside on_update
        obj.test_var = u'CCC'
        obj.update_test_var_on_update = True
        self.store.commit()
        self._assert_updated(obj)
        self._assert_nothing_made(dummy_obj)
        obj.reset()

        obj = self.store.find(WillBeCommitted, id=obj.id).one()
        dummy_obj = self.store.find(WillBeCommitted, id=dummy_obj.id).one()
        # Test obj being commited without any modification
        self.store.commit()
        self._assert_nothing_made(obj)
        self._assert_nothing_made(dummy_obj)
        obj.reset()

        # Test obj being commited after modification.
        obj.test_var = u'DDD'
        self.store.commit()
        self._assert_updated(obj)
        self._assert_nothing_made(dummy_obj)
        obj.reset()

        obj = WillBeCommitted(store=self.store,
                              test_var=u'EEE')
        self.store.commit()
        obj.reset()
        # Test obj being deleted without any modification
        self.store.remove(obj)
        self.store.commit()
        self._assert_deleted(obj)
        self._assert_nothing_made(dummy_obj)
        obj.reset()

        obj = WillBeCommitted(store=self.store,
                              test_var=u'EEE')
        self.store.commit()
        obj.reset()
        # Test obj being deleted after modification
        obj.test_var = u'FFF'
        self.store.remove(obj)
        self.store.commit()
        self._assert_deleted(obj)
        self._assert_nothing_made(dummy_obj)
        obj.reset()

        # Test obj being deleted after creation
        obj = WillBeCommitted(store=self.store,
                              test_var=u'EEE')
        self.store.remove(obj)
        self.store.commit()
        self._assert_deleted(obj)
        self._assert_nothing_made(dummy_obj)
        obj.reset()

    #
    #  Private
    #

    def _assert_created(self, obj):
        self.assertTrue(obj.was_created)
        self.assertFalse(obj.was_updated)
        self.assertFalse(obj.was_deleted)
        self.assertEqual(obj.on_update_called_count, 0)

    def _assert_deleted(self, obj):
        self.assertFalse(obj.was_created)
        self.assertTrue(obj.was_deleted)
        self.assertFalse(obj.was_updated)
        self.assertEqual(obj.on_update_called_count, 0)

    def _assert_updated(self, obj):
        self.assertFalse(obj.was_created)
        self.assertFalse(obj.was_deleted)
        self.assertTrue(obj.was_updated)
        self.assertEqual(obj.on_update_called_count, 1)

    def _assert_nothing_made(self, obj):
        self.assertFalse(obj.was_updated)
        self.assertFalse(obj.was_deleted)
        self.assertFalse(obj.was_created)
        self.assertEqual(obj.on_update_called_count, 0)
