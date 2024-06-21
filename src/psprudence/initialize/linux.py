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
"""
Initialize psprudence for Linux.

In addition to generic initialization faculties, Linux additionally has
``${XDG_DATA_HOME:-${HOME}/.local/share}/applications/psprudence.desktop``,
which can be autostarted by symlinking from
``${XDG_CONFIG_HOME:-${HOME}/.config}/autostart/psprudence.desktop``.
"""

import shutil
import subprocess
from functools import reduce
from pathlib import Path

from psprudence import print, project_root
from psprudence.initialize.generic import OperatingPlatform
from xdgpspconf import ConfDisc, DataDisc

CONF_DISC = ConfDisc('psprudence')  # deliberately avoid shipped
DATA_DISC = DataDisc('psprudence')  # deliberately avoid shipped


class LinuxPlatform(OperatingPlatform):

    platform = 'Linux'

    @property
    def svc_path(self) -> Path:
        configs = CONF_DISC.get_loc(permargs={'mode': 'w'})
        for conf in configs:
            svc_dir = conf.parents[1] / 'systemd/user'
            if svc_dir.is_dir():
                # found a path
                return svc_dir / "psprudence.service"
        new_svc = configs[0].parents[1] / 'systemd/user'
        new_svc.mkdir(parents=True, exist_ok=True)
        return new_svc

    @property
    def app_path(self) -> Path:
        """Inferred path to write .desktop file."""
        data_locs = DATA_DISC.get_loc(permargs={'mode': 'w'})
        for data_dir in data_locs:
            app_dir = data_dir / 'applications'
            if app_dir.is_dir():
                # found a path
                return app_dir / "psprudence.desktop"
        new_app_dir = data_locs[0] / 'applications'
        new_app_dir.mkdir(parents=True, exist_ok=True)
        return new_app_dir / 'psprudence.desktop'

    @property
    def app_file_content(self) -> str:
        """Content for app file."""
        df_template = (Path(__file__).parent /
                       'psprudence.desktop').read_text()
        return reduce(lambda x, y: x.replace(y[0], y[1]),
                      self.replacements.items(), df_template)

    @property
    def autostart_path(self) -> Path:
        """Inferred path to autostart file."""
        return (self.svc_path.parents[2] / 'autostart/psprudence.desktop')

    def is_local_alerts_touched(self) -> bool:
        return (self.local_alerts_path.is_file()
                and self.local_alerts_path.with_suffix('.sh').is_file())

    def is_app_generated(self) -> bool:
        """
        Returns
        --------
        bool
            Is .desktop app file generated?
        """
        return self.app_path.is_file()

    def is_svc_enabled(self) -> bool:
        sysd_enabled = subprocess.run(
            ['systemctl', '--user', 'is-enabled', 'psprudence'],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if sysd_enabled.stdout is None:
            raise ChildProcessError("Systemd did not return expected output.")
        return 'enabled' in sysd_enabled.stdout

    def is_autostart_enabled(self) -> bool:
        """
        Returns
        -------
        bool
            Is autostart linked?
        """
        return self.autostart_path.is_file()

    def is_initialized(self) -> bool:
        """
        Returns
        -------
        bool
            Are (service **or app**) and local_alerts files generated?
        """

        return (self.is_local_alerts_touched() and self.is_configured()
                and (self.is_svc_generated() or self.is_app_generated()))

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
        retcode = super().copy_local_alerts(revert=revert)
        if revert:
            self.local_alerts_path.with_suffix('.sh').unlink(missing_ok=True)
            return retcode
        shutil.copy((project_root / 'initialize/local_alerts.sh'),
                    self.local_alerts_path.with_suffix('.sh'),
                    follow_symlinks=True)
        return retcode

    def generate_app(self, revert: bool = False) -> int:
        """
        Generate .desktop app file.

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
            self.enable_autostart(revert=True)
            self.app_path.unlink(missing_ok=True)
            return 0
        if self.is_app_generated():
            print('Application desktop file is already created.', mark='info')
            return 8
        self.app_path.write_text(self.app_file_content)
        return 0

    def enable_svc(self, revert: bool = False) -> int:
        # Must conflict with Autostart
        if not revert and self.is_autostart_enabled():
            print('Autostart [conflicting] is already set.', mark='err')
            return 4

        try:
            return super().enable_svc(revert=revert)
        except NotImplementedError:
            return subprocess.call([
                'systemctl', '--user', 'disable' if revert else 'enable',
                '--now', 'psprudence.service'
            ])

    def enable_autostart(self, revert: bool = False) -> int:
        """
        Register autostart for psprudence with os.

        Parameters
        ----------
        revert : bool
            undo previous generation (disable it as well)

        Returns
        -------
        int
            exit code: failure 64: + service = 1, app = 2 combined bitwise
        """
        if revert:
            if not self.is_autostart_enabled():
                print('Autostart is not enabled.', mark='info')
                return 8
            self.autostart_path.unlink(missing_ok=True)
            return 0

        # Must conflict with systemd service
        if self.is_svc_enabled():
            print('Systemd service [conflicting] is enabled.', mark='err')
            return 8

        if self.is_autostart_enabled():
            print('Autostart is already linked.', mark='info')
            return 8
        self.generate_app(revert=revert)
        self.autostart_path.symlink_to(self.app_path)
        return 0

    def init(self, revert: bool = False):
        return super().init(revert=revert) | self.generate_app(revert=revert)
