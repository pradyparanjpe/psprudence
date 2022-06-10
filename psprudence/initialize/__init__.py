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
"""Initialize Platform"""

import platform

from psprudence import print
from psprudence.initialize.linux import LinuxPlatform
from psprudence.initialize.macos import MacPlatform
from psprudence.initialize.windows import WindowsPlatform


def init_call(**kwargs):
    """
    Initialize files for platforms
    """
    retcode = 0
    os_system = platform.system()
    if os_system == 'Linux':
        current_platform = LinuxPlatform()
    elif os_system == 'Darwin':
        current_platform = MacPlatform()
    elif os_system == 'Windows':
        current_platform = WindowsPlatform()
    else:
        print(
            'Only Linux, MacOS (Darwin) [and in future, Windows] are supported for init.',
            mark='err')
        raise NotImplementedError

    if kwargs.get('delete'):
        return current_platform.deinit()

    if not current_platform.is_initialized():
        retcode |= current_platform.generate()

    if kwargs.get('generate'):
        return retcode

    if kwargs.get('autostart'):
        return retcode | current_platform.enable_autostart()

    # default action is to enable service
    return retcode | current_platform.enable_service()
