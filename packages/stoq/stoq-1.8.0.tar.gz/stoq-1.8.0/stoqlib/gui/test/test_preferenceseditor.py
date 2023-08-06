# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 Async Open Source <http://www.async.com.br>
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

import mock

from stoqlib.api import api
from stoqlib.gui.editors.preferenceseditor import PreferencesEditor
from stoqlib.gui.test.uitestutils import GUITest


class TestPreferencesEditor(GUITest):
    @mock.patch('stoqlib.gui.editors.preferenceseditor.gio.app_info_get_default_for_type')
    def test_show(self, app_info):
        # stoq.gui.application sets this default style, but if we run this test
        # isolated, it will fail
        api.user_settings.set('toolbar-style', 'both-horizontal')

        app_info.return_value = None
        editor = PreferencesEditor(self.store)
        editor.language.select_item_by_data(None)
        self.check_editor(editor, 'editor-preferences-show')
