# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2012 Async Open Source
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
##

import glob
import os
import site

from kiwi.environ import Library

__all__ = ['library']


def _get_external_plugins_paths():
    import stoqlib
    # This is the dir containing stoq/kiwi/stoqdrivers/etc
    checkout = os.path.dirname(
        os.path.dirname(os.path.dirname(stoqlib.__file__)))

    # If there's n foobar plugin on the checkout, it will expand to find:
    #     CHECKOUT/<git_repository>/foobar/foobar.plugin
    for filename in glob.iglob(os.path.join(checkout, '*', '*', '*.plugin')):
        # In the example above, the path here is expected to be on
        # <git_repository>, not on <git_repository>/foobar/
        yield os.path.dirname(os.path.dirname(filename))


library = Library('stoq', root='..' + os.sep + '..')
if library.uninstalled:
    library.add_global_resource('csv', 'data/csv')
    library.add_global_resource('docs', '.')
    library.add_global_resource('glade', 'data/glade')
    library.add_global_resource('html', 'data/html')
    library.add_global_resource('misc', 'data/misc')
    library.add_global_resource('pixmaps', 'data/pixmaps')
    library.add_global_resource('sql', 'data/sql')
    library.add_global_resource('template', 'data/template')
    library.add_global_resource('uixml', 'data/uixml')
    library.add_resource('plugin', 'plugins')
    for dirname in _get_external_plugins_paths():
        library.add_resource('plugin', dirname)
    externals = os.path.join(library.get_root(), 'external')
else:
    # root = $prefix/lib/pythonX.Y/site-packages
    # We want $prefix/lib/stoqlib, eg ../../stoqlib
    externals = os.path.join(library.prefix, 'lib', 'stoqlib')

library.set_application_domain('stoq')
site.addsitedir(externals)
library.enable_translation(domain="stoq")
