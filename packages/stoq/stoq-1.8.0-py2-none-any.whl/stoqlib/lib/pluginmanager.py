# -*- Mode: Python; coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

import glob
import logging
import os
import sys
from zipfile import ZipFile, is_zipfile

from kiwi.desktopparser import DesktopParser
from kiwi.component import get_utility, provide_utility
from zope.interface import implementer

from stoqlib.database.runtime import get_default_store, new_store
from stoqlib.database.exceptions import SQLError
from stoqlib.domain.plugin import InstalledPlugin
from stoqlib.lib.message import error
from stoqlib.lib.kiwilibrary import library
from stoqlib.lib.interfaces import IPlugin, IPluginManager
from stoqlib.lib.osutils import get_system_locale
from stoqlib.lib.settings import get_settings

log = logging.getLogger(__name__)


class PluginError(Exception):
    pass


class PluginDescription(object):
    def __init__(self, filename, is_egg=False):
        config = DesktopParser()
        if is_egg:
            self.plugin_path = filename
            msg = "%s is not a valid egg file" % filename
            assert is_zipfile(filename), msg
            with ZipFile(filename, "r") as egg:
                filename = [f for f in egg.namelist()
                            if f.endswith('plugin')][0]
                plugin_file = egg.open(filename)
                config.readfp(plugin_file)
        else:
            plugin_path = os.path.dirname(os.path.dirname(filename))
            self.plugin_path = plugin_path
            config.read(filename)

        self.name = unicode(os.path.basename(filename).split('.')[0])
        self.entry = config.get('Plugin', 'Module')
        self.filename = filename

        settings = get_settings()
        lang = settings.get('user-locale', None)
        if not lang:
            lang = get_system_locale()

        self.long_name = config.get_locale('Plugin', 'Name', lang)
        self.description = config.get_locale('Plugin', 'Description', lang)

    @property
    def dirname(self):
        return os.path.dirname(self.filename)


@implementer(IPluginManager)
class PluginManager(object):
    """A class responsible for administrating plugins

    This class is responsible for administrating plugins, like,
    controlling which one is available/installed/actived or not.
    @important: Never instantialize this class. Always use
    """

    def __init__(self):
        self._plugins = {}
        self._active_plugins = {}
        self._plugin_descriptions = {}

        self._read_plugin_descriptions()

    #
    # Properties
    #

    @property
    def available_plugins_names(self):
        """A list of names of all available plugins"""
        return list(self._plugin_descriptions.keys())

    @property
    def installed_plugins_names(self):
        """A list of names of all installed plugins"""
        default_store = get_default_store()
        return [p.plugin_name for p in default_store.find(InstalledPlugin)]

    @property
    def active_plugins_names(self):
        """A list of names of all active plugins"""
        return list(self._active_plugins.keys())

    #
    # Private
    #

    def _read_plugin_descriptions(self):
        for path in library.get_resource_paths('plugin'):
            for filename in glob.iglob(os.path.join(path, '*', '*.plugin')):
                self._register_plugin_description(filename)
            for filename in glob.iglob(os.path.join(path, '*.egg')):
                self._register_plugin_description(filename, is_egg=True)

    def _register_plugin_description(self, filename, is_egg=False):
        desc = PluginDescription(filename, is_egg)
        self._plugin_descriptions[desc.name] = desc

    def _import_plugin(self, plugin_desc):
        log.info("Loading plugin %s" % (plugin_desc.name, ))
        plugin_path = plugin_desc.plugin_path
        if plugin_path not in sys.path:
            sys.path.append(plugin_path)

        # FIXME: Use setuptools entry points when we can
        __import__(os.path.basename(plugin_desc.dirname), globals(), locals(),
                   [plugin_desc.entry])

        assert plugin_desc.name in self._plugins

    #
    # Public API
    #

    def get_plugin(self, plugin_name):
        """Returns a plugin by it's name

        :param plugin_name: the plugin's name
        :returns: the :class:`IPlugin` implementation of the plugin
        """
        if not plugin_name in self._plugin_descriptions:
            raise PluginError("%s plugin not found" % (plugin_name, ))

        if not plugin_name in self._plugins:
            self._import_plugin(self._plugin_descriptions[plugin_name])

        return self._plugins[plugin_name]

    def get_description_by_name(self, plugin_name):
        """Returns the plugin's description given a plugin's name

        :returns: the :class:`PluginDescription` for the plugin
        """
        return self._plugin_descriptions.get(plugin_name)

    def register_plugin(self, plugin):
        """Registers a plugin on manager

        This needs to be called by every plugin, or else, the manager
        won't know it's existence. It's usually a good idea to
        use :class:`register_plugin` function on plugin code, so the
        plugin will be registered as soon as it's module gets read
        by python.

        :param plugin: the :class:`IPlugin` implementation of the plugin
        """
        if not IPlugin.providedBy(plugin):
            raise TypeError("The object %s does not implement IPlugin "
                            "interface" % (plugin, ))
        self._plugins[plugin.name] = plugin

        if library.uninstalled:
            gladedir = os.path.join('plugins', plugin.name, 'glade')
            if os.path.exists(gladedir):
                library.add_global_resource('glade', gladedir)

    def activate_plugin(self, plugin_name):
        """Activates a plugin

        This will activate the C{plugin}, calling it's C{activate}
        method and possibly doing some extra logic (e.g. logging).

        :param important: Always activate a plugin using this method because
          the manager keeps track of all active plugins. Else you
          probably will activate the same plugin twice, and that
          probably won't be good :)

        :param plugin: the :class:`IPlugin` implementation of the plugin
        """
        if self.is_active(plugin_name):
            raise PluginError("Plugin %s is already active" % (plugin_name, ))

        plugin = self.get_plugin(plugin_name)
        log.info("Activating plugin %s" % (plugin_name, ))
        plugin.activate()
        self._active_plugins[plugin_name] = plugin

    def install_plugin(self, plugin_name):
        """Install and enable a plugin

        @important: Calling this makes a plugin installed, but, it's
            your responsability to activate it!

        :param plugin: the :class:`IPlugin` implementation of the plugin
        """
        # Try to get the plugin first. If it was't registered yet,
        # PluginError will be raised.
        plugin = self.get_plugin(plugin_name)

        if plugin_name in self.installed_plugins_names:
            raise PluginError("Plugin %s is already enabled."
                              % (plugin_name, ))

        store = new_store()
        InstalledPlugin(store=store,
                        plugin_name=plugin_name,
                        plugin_version=0)
        store.commit(close=True)

        migration = plugin.get_migration()
        if migration:
            try:
                migration.apply_all_patches()
            except SQLError as e:
                # This means a lock could not be obtained. Warn user about this
                # and let stoq restart, that the schema will be upgraded
                # correctly
                error('Não foi possível terminar a instalação do plugin. '
                      'Por favor reinicie todas as instancias do Stoq que '
                      'estiver executando (%s)' % (e, ))

    def activate_installed_plugins(self):
        """Activate all installed plugins

        A helper method to activate all installed plugins in just one
        call, without having to get and activate one by one.
        """
        # FIXME: Get intersection to avoid trying to activate a plugin that
        #        isn't available. We should do something to remove such ones.
        for plugin_name in (set(self.installed_plugins_names) &
                            set(self.available_plugins_names)):
            self.activate_plugin(plugin_name)

    def is_active(self, plugin_name):
        """Returns if a plugin with a certain name is active or not.

        :returns: True if the given plugin name is active, False otherwise.
        """
        return plugin_name in self.active_plugins_names

    def is_installed(self, plugin_name):
        """Returns if a plugin with a certain name is installed or not

        :returns: True if the given plugin name is active, False otherwise.
        """
        return plugin_name in self.installed_plugins_names


def register_plugin(plugin_class):
    """Registers a plugin on IPluginManager

    Just a convenience function that can be added at the end of each
    plugin class definition to register it on manager.

    :param plugin_class: class to register, must implement :class:`IPlugin`
    """
    manager = get_plugin_manager()
    manager.register_plugin(plugin_class())


def get_plugin_manager():
    """Provides and returns the plugin manager

    @attention: Try to always use this instead of getting the utillity
        by hand, as that could not have been provided before.

    :returns: an :class:`PluginManager` instance
    """
    manager = get_utility(IPluginManager, None)
    if not manager:
        manager = PluginManager()
        provide_utility(IPluginManager, manager)

    return manager
