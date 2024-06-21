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
"""Initialize psprudence for MacOS."""

import subprocess
from functools import reduce
from pathlib import Path

from psprudence import print
from psprudence.initialize.generic import OperatingPlatform


class MacPlatform(OperatingPlatform):

    platform = 'Darwin'

    @property
    def svc_path(self) -> Path:
        return Path.home() / "Library/LaunchAgents/psprudence.plist"

    def is_svc_enabled(self) -> bool:
        sysd_units = subprocess.run(['launchd', 'bslist'],
                                    text=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        if sysd_units.stdout is None:
            raise ChildProcessError("launchd did not return expected output")
        enabled_svcs = sysd_units.stdout.readlines()
        return any("psprudence" in svc for svc in enabled_svcs)

    def enable_svc(self, revert: bool = False) -> int:
        try:
            return super().enable_svc(reverrt=revert)
        except NotImplementedError:
            return subprocess.call(
                ['launchd', 'unload' if revert else 'load', self.svc_path])
