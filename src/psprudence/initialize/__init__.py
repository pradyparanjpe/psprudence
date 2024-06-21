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
from psprudence.initialize.generic import OperatingPlatform
from psprudence.initialize.linux import LinuxPlatform
from psprudence.initialize.macos import MacPlatform
from psprudence.initialize.windows import WindowsPlatform


def _os_plat() -> OperatingPlatform:
    """Discover and initialize a handle for the operating system platform."""
    platform_h = {
        'Linux': LinuxPlatform,
        'Darwin': MacPlatform,
        'Windows': WindowsPlatform
    }.get(platform.system())
    if platform_h is None:
        print('Only Linux, MacOS (Darwin) and Windows are supported for init.',
              mark='err')
        raise NotImplementedError
    return platform_h()


def init_call(**kwargs) -> int:
    """Initialize /de-initialize auto-start and services"""
    current_platform = _os_plat()
    if kwargs.get('delete'):
        return current_platform.init(revert=True)

    retcode = 0
    retcode |= current_platform.init()
    if kwargs.get('generate'):
        return retcode

    if kwargs.get('autostart'):
        if kwargs.get('force'):
            current_platform.enable_svc(revert=True)
        return retcode | current_platform.enable_autostart()

    # default action is to enable service
    if kwargs.get('force') and isinstance(current_platform, LinuxPlatform):
        current_platform.enable_autostart(revert=True)
    return retcode | current_platform.enable_svc()
