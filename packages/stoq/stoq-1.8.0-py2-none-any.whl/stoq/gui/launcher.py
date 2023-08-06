# -*- Mode: Python; coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2011-2013 Async Open Source <http://www.async.com.br>
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
""" Application to launcher other application.  """

import operator

import gtk
from kiwi.component import get_utility
from stoqlib.api import api
from stoqlib.lib.interfaces import IApplicationDescriptions
from stoqlib.lib.translation import locale_sorted, stoqlib_gettext

from stoq.gui.shell.shellapp import ShellApp
from stoq.lib.applist import Application

_ = stoqlib_gettext

(COL_LABEL,
 COL_PIXBUF,
 COL_APP) = range(3)


class LauncherApp(ShellApp):

    gladefile = "launcher"

    app_title = "Stoq"

    #
    # ShellApp
    #

    def create_ui(self):
        self.model.set_sort_column_id(COL_LABEL, gtk.SORT_ASCENDING)
        self.iconview.set_markup_column(COL_LABEL)
        self.iconview.set_pixbuf_column(COL_PIXBUF)
        if hasattr(self.iconview, "set_item_orientation"):
            self.iconview.set_item_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.iconview.set_item_width(300)
        self.iconview.set_selection_mode(gtk.SELECTION_BROWSE)
        self.iconview.set_spacing(10)

        for app in self._get_available_applications():
            pixbuf = self.get_toplevel().render_icon(app.icon, gtk.ICON_SIZE_DIALOG)
            text = '<b>%s</b>\n<small>%s</small>' % (
                api.escape(app.fullname),
                api.escape(app.description))
            self.model.append([text, pixbuf, app])

        # FIXME: last opened application
        if len(self.model):
            self.iconview.select_path(self.model[0].path)
            self.iconview.grab_focus()
        self.iconview_vbox.show()

    def activate(self, refresh=True):
        # Menu
        self.window.ChangePassword.set_visible(True)
        self.window.SignOut.set_visible(True)
        self.window.Close.set_sensitive(False)
        self.window.Quit.set_visible(True)
        self.window.Print.set_sensitive(False)
        self.window.Print.set_visible(False)
        self.window.ExportSpreadSheet.set_visible(False)
        self.window.ExportSpreadSheet.set_sensitive(False)

        # Toolbar
        self.window.set_new_menu_sensitive(True)
        self.window.NewToolItem.set_tooltip(_("Open a new window"))
        self.window.SearchToolItem.set_tooltip("")
        self.window.SearchToolItem.set_sensitive(False)

    def deactivate(self):
        self.iconview_vbox.hide()

    def setup_focus(self):
        self.iconview.grab_focus()

    def new_activate(self):
        self.window.new_window()

    def _get_app_by_name(self, app_name):
        for row in self.model:
            if row[COL_APP].name == app_name:
                return row[COL_APP]

    def _get_available_applications(self):
        user = api.get_current_user(self.store)

        permissions = {}
        for settings in user.profile.profile_settings:
            permissions[settings.app_dir_name] = settings.has_permission

        descriptions = get_utility(IApplicationDescriptions).get_descriptions()

        available_applications = []

        # sorting by app_full_name
        for name, full, icon, descr in locale_sorted(
            descriptions, key=operator.itemgetter(1)):
            # FIXME:
            # if name in self._hidden_apps:
            #    continue
            # and name not in self._blocked_apps:
            if permissions.get(name):
                available_applications.append(
                    Application(name, full, icon, descr))

        return available_applications

    #
    # Callbacks
    #

    def on_iconview__item_activated(self, iconview, path):
        self.window.hide_app(empty=True)
        app = self.model[path][COL_APP]
        self.window.run_application(app.name)
