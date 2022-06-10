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
"""Initialize psprudence for Linux"""

import subprocess
from functools import reduce
from os import environ
from pathlib import Path

from psprudence import print
from psprudence.initialize.generic import OperatingPlatform


class LinuxPlatform(OperatingPlatform):
    """
    Linux Platform initialization
    """

    def __init__(self):
        super().__init__()
        assert self.os_name == "Linux"

    @property
    def service_path(self) -> Path:
        xdg_config_dirs = environ.get('XDG_CONFIG_DIRS', '').split(':')
        xdg_config_dirs.insert(0, environ.get('XDG_CONFIG_HOME', ''))
        xdg_config_dirs.append(str(Path.home() / '.config'))
        while '' in xdg_config_dirs:
            xdg_config_dirs.remove('')
        for xdg_config_home in xdg_config_dirs:
            app_dir = Path(xdg_config_home) / "systemd/user"
            if app_dir.is_dir():
                # found a path
                return app_dir / "psprudence.service"
        print("Could not locate service files directory.", mark='err')
        raise NotADirectoryError

    @property
    def autostart_path(self) -> Path:
        return (self.service_path.parent.parent.parent /
                'autostart/psprudence.desktop')

    @property
    def app_path(self) -> Path:
        xdg_data_dirs = environ.get('XDG_DATA_DIRS', '').split(':')
        xdg_data_dirs.insert(0, environ.get('XDG_DATA_HOME', ''))
        xdg_data_dirs.append(str(Path.home() / '.local/share'))
        while '' in xdg_data_dirs:
            xdg_data_dirs.remove('')
        for xdg_data_home in xdg_data_dirs:
            app_dir = Path(xdg_data_home) / 'applications'
            if app_dir.is_dir():
                # found a path
                return app_dir / 'psprudence.desktop'
        print("Couldn't locate applications directory.", mark='err')
        raise NotADirectoryError

    @property
    def app_file_content(self) -> str:
        df_template = (Path(__file__).parent /
                       'psprudence.desktop').read_text()
        return reduce(lambda x, y: x.replace(y[0], y[1]),
                      self.replacements.items(), df_template)

    @property
    def service_file_content(self) -> str:
        service_templ = (Path(__file__).parent /
                         'psprudence.service').read_text()
        return reduce(lambda x, y: x.replace(y[0], y[1]),
                      self.replacements.items(), service_templ)

    def is_initialized(self) -> bool:
        if self.service_path.is_file() and self.app_path.is_file():
            return True
        return False

    def is_autostart_enabled(self) -> bool:
        return self.autostart_path.is_file()

    def is_service_enabled(self) -> bool:
        sysd_units = subprocess.Popen(
            ['systemctl', '--user', 'list-unit-files'],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if sysd_units.stdout is None:
            raise ChildProcessError("Systemd did not return expected output")
        enabled_services = sysd_units.stdout.readlines()
        if any((all(lookup in service for lookup in ("psprudence", "enabled")))
               for service in enabled_services):
            return True
        return False

    def generate(self) -> int:
        if self.app_path.is_file():
            print('App file is already created.', mark='info')
        else:
            with open(self.app_path, 'w') as df_handle:
                df_handle.write(self.app_file_content)

        if self.service_path.is_file():
            print('Service file is already created.', mark='info')
        else:
            self.service_path.write_text(self.service_file_content)
        return 0

    def enable_service(self) -> int:
        if self.is_service_enabled():
            print('Service is already enabled.', mark='info')
            return 0
        if self.is_autostart_enabled():
            print('Autostart is already set.', mark='err')
            return 66
        return subprocess.call(
            ['systemctl', '--user', 'enable', '--now', 'psprudence.service'])

    def disable_service(self) -> int:
        if not self.is_service_enabled():
            print('Service is not enabled.', mark='info')
            return 0
        return subprocess.call(
            ['systemctl', '--user', 'disable', '--now', 'psprudence.service'])

    def enable_autostart(self) -> int:
        if self.is_service_enabled():
            print('Systemd service is enabled.', mark='err')
            return 65
        if self.is_autostart_enabled():
            print('Autostart file is already linked.', mark='info')
            return 0
        self.autostart_path.symlink_to(self.app_path)
        return 0
