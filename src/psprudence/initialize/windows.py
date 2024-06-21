#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2022 Pradyumna Paranjape
#
# This file is part of psprudence.
#
# psprudence is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either versioa 3 of the License, or
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
from pathlib import Path

from psprudence import print, project_root
from psprudence.initialize.generic import OperatingPlatform


class WindowsPlatform(OperatingPlatform):

    platform = "Windows"

    def is_svc_generated(self) -> bool:
        print("Windows doesn't require service file", mark='info')
        return True

    def is_svc_enabled(self) -> bool:
        sysd_units = subprocess.run(
            ['sc', 'queryex', 'type=service', 'state=all'],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if sysd_units.stdout is None:
            raise ChildProcessError("'sc' did not return expected output.")
        enabled_svcs = sysd_units.stdout.readlines()
        if any("psprudence" in svc for svc in enabled_svcs):
            return True
        return False

    def generate_svc(self, revert=True) -> int:
        if revert:
            self.enable_svc(revert=revert)
        return 0

    def enable_svc(self, revert: bool = False) -> int:
        try:
            return super().enable_svc(revert=revert)
        except NotImplementedError:
            if revert:
                return subprocess.call(
                    ['nssm.exe', 'remove', 'psprudence', 'confirm'])
            install_err = subprocess.call([
                'nssm.exe', 'install', 'psprudence', sys.executable, '-m',
                str(project_root)
            ])
            set_err = subprocess.call(
                ['nssm.exe', 'set', 'psprudence', 'AppDirectory',
                 Path.home()])
            return install_err | set_err
