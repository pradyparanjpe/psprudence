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
"""Initialize psprudence for MacOS"""

import subprocess
from functools import reduce
from pathlib import Path

from psprudence import print
from psprudence.initialize.generic import OperatingPlatform


class MacPlatform(OperatingPlatform):

    def __init__(self):
        super().__init__()
        assert self.os_name == "Darwin"

    @property
    def service_path(self) -> Path:
        return Path.home() / "Library/LaunchAgents/psprudence.plist"

    @property
    def service_file_content(self) -> str:
        service_templ = (Path(__file__).parent /
                         'psprudence.plist').read_text()
        return reduce(lambda x, y: x.replace(y[0], y[1]),
                      self.replacements.items(), service_templ)

    def is_initialized(self) -> bool:
        if self.service_path.is_file():
            return True
        return False

    def is_service_enabled(self) -> bool:
        sysd_units = subprocess.Popen(['launchd', 'bslist'],
                                      text=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        if sysd_units.stdout is None:
            raise ChildProcessError("launchd did not return expected output")
        enabled_services = sysd_units.stdout.readlines()
        if any((all(lookup in service for lookup in ("psprudence", )))
               for service in enabled_services):
            return True
        return False

    def generate(self) -> int:
        if self.service_path.is_file():
            print('Service file is already created.', mark='info')
        else:
            self.service_path.write_text(self.service_file_content)
        return 0

    def enable_service(self) -> int:
        self.generate()
        if self.is_service_enabled():
            print('Service is already enabled.', mark='info')
            return 0
        return subprocess.call(['launchd', 'load', self.service_path])

    def disable_service(self) -> int:
        if not self.is_service_enabled():
            print('Service is not enabled.', mark='info')
            return 0
        return subprocess.call(['launchd', 'unload', self.service_path])
