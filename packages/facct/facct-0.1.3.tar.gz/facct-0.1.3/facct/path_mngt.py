#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Eric F <efigue> Figerson
# Author(s):
#   Eric F <eric.foss@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

appli_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

def get_dev_path():
    return os.path.join(os.path.dirname(__file__), '..')

def get_root_app():
    package_path = os.path.dirname(__file__)
    if os.path.exists(os.path.join(package_path, 'data')):
        return package_path
    return get_dev_path()

def get_share_dir():
    return os.path.join(get_root_app(), 'locale')
