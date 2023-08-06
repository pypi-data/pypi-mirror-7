# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2011 Async Open Source <http://www.async.com.br>
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
##

"""Test for stoqlib.lib.pluginmanager module"""

import io

import mock
from zope.interface import implementer

from stoqlib.database.runtime import new_store
from stoqlib.domain.plugin import InstalledPlugin
from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.lib.interfaces import IPlugin, IPluginManager
from stoqlib.lib.pluginmanager import (PluginError, register_plugin,
                                       PluginManager, get_plugin_manager,
                                       PluginDescription)

plugin_desc = """
[Plugin]
Module=testplugin
Version=1
Name=Test plugin
Description=Test plugin description
Authors=Stoq Team <stoq-devel@async.com.br>
Copyright=Copyright © 2007 Async Open Source
Website=http://www.stoq.com.br/
"""


@implementer(IPlugin)
class _TestPlugin(object):

    name = u'test_plugin'

    def __init__(self):
        self.reset()

    def reset(self):
        self.was_activated = False
        self.had_migration_gotten = False

    #
    #  IPlugin
    #

    def activate(self):
        self.was_activated = True

    def get_migration(self):
        self.had_migration_gotten = True
        return None


class TestPluginDescription(DomainTest):

    @mock.patch('stoqlib.lib.pluginmanager.ZipFile')
    @mock.patch('stoqlib.lib.pluginmanager.is_zipfile')
    def test_constructor_is_egg(self, is_zipfile, ZipFile):
        ZipFile.return_value = mock.MagicMock()
        egg = ZipFile.return_value.__enter__.return_value
        egg.namelist.return_value = ['test.plugin']
        egg.open.return_value = io.BytesIO(plugin_desc)

        desc = PluginDescription('tmpfile', is_egg=True)

        is_zipfile.assert_called_once_with('tmpfile')
        self.assertEquals(desc.filename, 'test.plugin')
        self.assertEquals(desc.plugin_path, 'tmpfile')
        self.assertEquals(desc.long_name, 'Test plugin')


class TestPluginManager(DomainTest):

    def setUp(self):
        super(TestPluginManager, self).setUp()

        # Since the plugins are commited inside pluginmanager, try to remove
        # it first, or we will have problems if STOQLIB_TEST_QUICK is set.
        store = new_store()
        plugins = set(InstalledPlugin.get_plugin_names(store=self.store))
        expected = set([u'ecf', u'nfe', u'optical'])
        self.assertTrue(expected.issubset(plugins))
        test_plugin = store.find(InstalledPlugin,
                                 plugin_name=_TestPlugin.name).one()
        if test_plugin:
            store.remove(test_plugin)
            store.commit()
        store.close()

        self._manager = get_plugin_manager()
        self._register_test_plugin()

    #
    #  Tests
    #

    def test_get_plugin_manager(self):
        # PluginManager should be a singleton
        self.assertEqual(self._manager, get_plugin_manager())
        self.assertEqual(id(self._manager), id(get_plugin_manager()))

        # Just check if it really provides IPluginManager
        self.assertTrue(IPluginManager.providedBy(self._manager))
        self.assertTrue(isinstance(self._manager, PluginManager))

    def test_get_plugin(self):
        p_name = _TestPlugin.name

        # Test if _TestPlugin is available
        self.assertTrue(p_name in self._manager.available_plugins_names)

        # Test getting _TestPlugin
        plugin = self._manager.get_plugin(_TestPlugin.name)
        self.assertTrue(isinstance(plugin, _TestPlugin))
        self.assertTrue(IPlugin.providedBy(plugin))

        # Test getting an inexistent plugin
        self.assertRaises(PluginError, self._manager.get_plugin, '_null_')

    def test_register_plugin(self):
        p_name = _TestPlugin.name
        p_name_ = p_name

        # Simulates a new plugin and try registering on manager
        p_name_ += '_'
        _TestPlugin.name = p_name_
        self.assertFalse(p_name_ in self._manager.available_plugins_names)
        self._manager._plugin_descriptions[p_name_] = p_name_
        self._manager.register_plugin(_TestPlugin())
        _TestPlugin.name = p_name
        self.assertTrue(p_name_ in self._manager.available_plugins_names)
        self.assertTrue(p_name_ in self._manager._plugins)

        # Simulates a new plugin and try registering using register_plugin
        p_name_ += '_'
        _TestPlugin.name = p_name_
        self.assertFalse(p_name_ in self._manager.available_plugins_names)
        self._manager._plugin_descriptions[p_name_] = p_name_
        register_plugin(_TestPlugin)
        _TestPlugin.name = p_name
        self.assertTrue(p_name_ in self._manager.available_plugins_names)
        self.assertTrue(p_name_ in self._manager._plugins)

        # Try to register to invalid plugins
        self.assertRaises(TypeError, self._manager.register_plugin, object())
        self.assertRaises(TypeError, register_plugin, object)

    def test_install_plugin(self):
        p_name = _TestPlugin.name
        plugin = self._manager.get_plugin(p_name)

        # Plugin should not be installed yet
        self.assertFalse(p_name in self._manager.installed_plugins_names)
        self.assertFalse(plugin.had_migration_gotten)
        self.assertFalse(self._manager.is_installed(p_name))

        self._manager.install_plugin(p_name)
        self.assertTrue(plugin.had_migration_gotten)
        self.assertFalse(plugin.was_activated)
        self.assertTrue(self._manager.is_installed(p_name))
        plugin.reset()

        # Test if _TestPlugin is installed
        self.assertTrue(p_name in self._manager.installed_plugins_names)

    def test_activate_plugin(self):
        p_name = _TestPlugin.name
        plugin = self._manager.get_plugin(p_name)

        # Plugin should not be active
        self.assertFalse(self._manager.is_active(p_name))
        self.assertFalse(plugin.was_activated)
        self.assertFalse(self._manager.is_active(p_name))

        self._manager.activate_plugin(p_name)
        self.assertTrue(plugin.was_activated)
        self.assertFalse(plugin.had_migration_gotten)
        self.assertTrue(self._manager.is_active(p_name))
        plugin.reset()

        # Test if plugin got activated on manager
        self.assertTrue(self._manager.is_active(p_name))

        # Test trying to activate again
        self.assertRaises(PluginError, self._manager.activate_plugin, p_name)
        self.assertTrue(self._manager.is_active(p_name))

    def test_activate_installed_plugins(self):
        available_plugins_names = set(['a_', 'b_', 'c_', 'd_'])
        installed_plugins_names = set(['b_', 'c_', 'e_'])
        should_be_called = (available_plugins_names &
                            installed_plugins_names)
        names_called = []

        _available = PluginManager.available_plugins_names
        PluginManager.available_plugins_names = available_plugins_names
        _installed = PluginManager.installed_plugins_names
        PluginManager.installed_plugins_names = installed_plugins_names
        _activate = PluginManager.activate_plugin
        PluginManager.activate_plugin = lambda s, n: names_called.append(n)

        self._manager.activate_installed_plugins()

        # Test if some plugin was called twice
        for name_called in names_called:
            self.assertEqual(names_called.count(name_called), 1)

        # Test if all plugins that should be installed were
        self.assertEqual(len(set(names_called) ^ should_be_called), 0)

        PluginManager.installed_plugins_names = _installed
        PluginManager.available_plugins_names = _available
        PluginManager.activate_plugin = _activate

    #
    #  Private
    #

    def _register_test_plugin(self):
        # Workaround to register _TestPlugin since is not really a plugin
        self._manager._plugin_descriptions[_TestPlugin.name] = None
        register_plugin(_TestPlugin)
