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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprudence. If not, see <https://www.gnu.org/licenses/>.
#
"""
Initialize psprudence for platform [Generic].

Currently supported
--------------------
- **Linux**: Tested
- **MacOS**: Untested
- **Windows**: Untested
"""

import platform
import shutil
import sys
from functools import reduce
from os import environ
from pathlib import Path
from typing import Dict

from psprudence import print, project_root
from xdgpspconf import ConfDisc, DataDisc

CONF_DISC = ConfDisc('psprudence')  # deliberately avoid shipped
DATA_DISC = DataDisc('psprudence')  # deliberately avoid shipped


class OperatingPlatform():
    """Initializer handle for generic platform (Operating System)."""

    platform = 'Unidentified'
    """Platform (Operating system)"""

    def __init__(self):
        os_name = platform.system()
        if os_name != self.platform:
            raise OSError(f'Bad platform: {os_name}')

        if environ.get('USER') == 'root':
            raise PermissionError('Do not run as Root')

    @property
    def replacements(self) -> Dict[str, str]:
        """Platform-specific replacements."""
        return {
            '___pythonpath___': ':'.join(sys.path),
            '___python_exec___': sys.executable,
            '___icon___': str(project_root.resolve() / 'data/exclaim.jpg'),
            '___psprudence_path___': str(project_root)
        }

    @property
    def local_alerts_path(self) -> Path:
        """
        Path (without extensions) to local functions.

        These files are `visible` to PSPrudence.
        """
        return DATA_DISC.get_loc(permargs={'mode': 'w'})[0] / 'local_alerts.py'

    @property
    def config_path(self) -> Path:
        """Inferred path to configuration file."""
        configs = CONF_DISC.get_loc(permargs={'mode': 'w'})
        if configs:
            return configs[0]
        # not yet initialized
        print("Could not locate configuration files directory.", mark='err')
        raise NotADirectoryError

    @property
    def svc_path(self) -> Path:
        """Inferred path to register services file."""
        return NotImplementedError

    @property
    def svc_file_content(self) -> str:
        """Content for systemd/macos service file."""
        if self.platform not in ('Linux', 'Darwin'):
            return NotImplementedError
        template = 'psprudence.' + {
            'Linux': 'service',
            'Darwin': 'plist'
        }.get(self.platform)
        svc_templ = (Path(__file__).parent / template).read_text()
        return reduce(lambda x, y: x.replace(y[0], y[1]),
                      self.replacements.items(), svc_templ)

    def is_local_alerts_touched(self) -> bool:
        """
        Returns
        -------
        bool
            Is local-alerts file copied?
        """
        return self.local_alerts_path.is_file()

    def is_configured(self) -> bool:
        """
        Returns
        -------
        bool
            Are service and app files generated?
        """
        return self.config_path.is_file()

    def is_svc_generated(self) -> bool:
        """
        Returns
        --------
        bool
            Is service file generated?
        """
        return self.svc_path.is_file()

    def is_svc_enabled(self) -> bool:
        """
        Returns
        -------
        bool
            Is psprudence service registered?

        Raises
        ------
        ChildProcessError
            Child Process threw error
        """
        return NotImplementedError

    def is_initialized(self) -> bool:
        """
        TODO: DROP

        Returns
        -------
        bool
            files generated and configured
        """
        return (self.is_local_alerts_touched() and self.is_configured()
                and self.is_svc_generated())

    def copy_local_alerts(self, revert: bool = True) -> int:
        """
        Copy local alerts to *visible* location.

        Parameters
        ----------
        revert : bool
            undo previous generation

        Returns
        --------
        int
            1 for failure
        """
        if revert:
            self.local_alerts_path.unlink(missing_ok=True)
            return 0
        if self.is_local_alerts_touched():
            print("Local alerts' file is already created.", mark='info')
            return 1
        shutil.copy((project_root / 'initialize/local_alerts.py'),
                    self.local_alerts_path,
                    follow_symlinks=True)

        return 0

    def configure(self, revert: bool = False) -> int:
        """
        Generate user's configuration and files.

        Parameters
        ----------
        revert : bool
            undo previous configuration

        Returns
        -------
        int
            exit code
        """
        if revert:
            self.config_path.unlink(missing_ok=True)
            return 0
        if self.is_configured():
            print('User configuration file is already created.', mark='info')
            return 2
        shutil.copy(project_root / 'initialize/config.yml',
                    self.config_path,
                    follow_symlinks=True)

        return 0

    def generate_svc(self, revert: bool = False):
        """
        Generate service file.

        Parameters
        ----------
        revert : bool
            undo previous generation (disable it as well)

        Returns
        -------
        int
            1 for failure
        """
        if revert:
            self.enable_svc(revert=True)
            self.svc_path.unlink(missing_ok=True)
            return 0
        if self.is_svc_generated():
            print('Service file is already created.', mark='info')
            return 4
        self.svc_path.write_text(self.svc_file_content)
        return 0

    def enable_svc(self, revert: bool = False) -> int:
        """
        Enable service (systemd/launchd) for psprudence at startup

        Parameters
        ----------
        revert : bool
            disable it instead

        Returns
        -------
        int
            exit code: failure 64: + service = 1, app = 2 combined bitwise
                or subprocess call return value
        """
        if revert:
            if not self.is_svc_enabled():
                print('Service is not enabled.', mark='info')
                return 4
            raise NotImplementedError
        if self.is_svc_enabled():
            print('Service is already enabled.', mark='info')
            return 4
        self.generate_svc()
        raise NotImplementedError

    def init(self, revert: bool = False) -> int:
        """
        Delete the application, service files

        Parameters
        ----------
        revert : bool
            undo initialization

        Returns
        -------
        int
            exit code

        Raises
        ------
        PermissionError
            User is root
        """
        return (self.copy_local_alerts(revert=revert)
                | self.configure(revert=revert)
                | self.generate_svc(revert=revert))
