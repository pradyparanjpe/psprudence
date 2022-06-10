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
"""Initialize psprudence for platform"""

import platform
import sys
from os import environ
from pathlib import Path
from typing import Dict

from psprudence import project_root


class OperatingPlatform():
    """
    Generic Operating System platform

    Currently supports:
        - [X] Linux: Tested
        - [X] MacOS: Untested
        - [X] Windows: Untested
    """

    def __init__(self):
        if environ.get('USER') == 'root':
            raise PermissionError('Do not run as Root')

    @property
    def os_name(self) -> str:
        """
        platform name
        """
        return platform.system()

    @property
    def replacements(self) -> Dict[str, str]:
        """
        platform-specific replacements
        """
        return {
            '___pythonpath___': ':'.join(sys.path),
            '___python_exec___': sys.executable,
            '___icon___': str(project_root.resolve() / 'data/exclaim.jpg'),
            '___psprudence_path___': str(project_root)
        }

    @property
    def service_path(self) -> Path:
        """
        Infer path to register services file

        Returns:
            Path of services file

        Raises:
            NotADirectoryError
        """
        return NotImplemented

    @property
    def autostart_path(self) -> Path:
        """
        Infer path to autostart file.

        Implemented only for Linux

        Returns:
            Path to autostart .desktop file

        """
        return NotImplemented

    @property
    def app_path(self) -> Path:
        """
        Infer path to write .desktop file

        Implemented only for Linux

        Returns:
            Path to .desktop file
        """
        return NotImplemented

    @property
    def app_file_content(self) -> str:
        """
        Generate content for app file

        Implemented only for Linux

        Returns:
            content

        """
        return NotImplemented

    @property
    def service_file_content(self) -> str:
        """
        Generate content for systemd/macos service file

        Args:
            os_name: name of os

        Returns:
            content

        """
        return NotImplemented

    def is_initialized(self) -> bool:
        """
        Returns:
            Whether service and app files are generated
        """
        if self.service_path.is_file():
            return True
        return False

    def is_autostart_enabled(self) -> bool:
        """
        Implemented only for Linux

        Returns:
            Is autostart linked?
        """
        return NotImplemented

    def is_service_enabled(self) -> bool:
        """
        Returns:
            ``True`` if psprudence service is registered.

        Raises:
            ChildProcessError: Child Process threw error
        """
        return NotImplemented

    def generate(self) -> int:
        """
        Initialize service and optionally app files

        Returns:
            exit code: failure 64: + service = 1, app = 2 combined bitwise
        """
        return NotImplemented

    def enable_service(self) -> int:
        """
        Enable service (systemd/launchd) for psprudence at startup

        Returns:
            exit code: failure 64: + service = 1, app = 2 combined bitwise
                or subprocess call return value
        """
        return NotImplemented

    def disable_service(self) -> int:
        """
        Disable service (systemd/launchd) for psprudence

        Returns:
            exit code: failure 64: + service = 1, app = 2 combined bitwise
                or subprocess call return value
        """
        return NotImplemented

    def enable_autostart(self) -> int:
        """
        Register autostart for psprudence with os.

        Implemented only for Linux

        Returns:
            exit code: failure 64: + service = 1, app = 2 combined bitwise
        """
        return NotImplemented

    def deinit(self) -> int:
        """
        delete the application, service files

        Returns:
            exit code

        Raises:
            PermissionError: User is root
        """
        for path in self.service_path, self.app_path, self.autostart_path:
            if path is not NotImplemented:
                path.unlink(missing_ok=True)
        self.disable_service()
        return 0
