#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2022 Pradyumna Paranjape
#
# This file is part of psprudence.
#
# psprudence is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprudence is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprudence. If not, see <https://www.gnu.org/licenses/>.
#
"""Initialization command line"""

import platform
from argparse import ArgumentParser


def init_parser() -> ArgumentParser:
    init = ArgumentParser(
        description='Initialize psprudence, set autolaunch service.')
    init.set_defaults(autostart=False)
    init.set_defaults(force=False)
    init.add_argument('-g',
                      '--generate',
                      action='store_true',
                      help='Only generate units and files for autolaunch.')
    if platform.system() == 'Linux':
        init.add_argument(
            '-a',
            '--autostart',
            action='store_true',
            help='Add app to autostart. INCOMPATIBLE with systemd service.')
        init.add_argument('--force',
                          action='store_true',
                          help='Replace conflicting.')
    init.add_argument('-d',
                      '--delete',
                      action='store_true',
                      help='Remove psprudence autolaunch.')
    init.set_defaults(call='init')
    return init
