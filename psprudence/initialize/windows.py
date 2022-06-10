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
"""Initialize psprudence for Windows"""

import subprocess
import sys
from functools import reduce
from pathlib import Path

from psprudence import print, project_root
from psprudence.initialize.generic import OperatingPlatform


class WindowsPlatform(OperatingPlatform):

    def __init__(self):
        super().__init__()
        assert self.os_name == "Windows"

    def is_service_enabled(self) -> bool:
        sysd_units = subprocess.Popen(
            ['sc', 'queryex', 'type=service', 'state=all'],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if sysd_units.stdout is None:
            raise ChildProcessError("'sc' did not return expected output")
        enabled_services = sysd_units.stdout.readlines()
        if any((all(lookup in service for lookup in ("psprudence", )))
               for service in enabled_services):
            return True
        return False

    def enable_service(self) -> int:
        self.generate()
        if self.is_service_enabled():
            print('Service is already enabled.', mark='info')
            return 0
        install_err = subprocess.call([
            'nssm.exe', 'install', 'psprudence', sys.executable, '-m',
            str(project_root)
        ])
        set_err = subprocess.call(
            ['nssm.exe', 'set', 'psprudence', 'AppDirectory',
             Path.home()])
        return install_err | set_err

    def disable_service(self) -> int:
        if not self.is_service_enabled():
            print('Service is not enabled.', mark='info')
            return 0
        return subprocess.call(['nssm.exe', 'remove', 'psprudence', 'confirm'])
