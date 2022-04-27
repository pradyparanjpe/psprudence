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
"""Shell functions"""

import os
import subprocess
from pathlib import Path
from typing import Optional

import dbus

from psprudence import print
from psprudence.errors import CommandError


def process_comm(*cmd: str,
                 timeout: int = None,
                 fail_handle: str = 'fail',
                 **kwargs) -> Optional[str]:
    """
    Generic process definition and communication.
    Raw actions, outputs, errors are displayed
    when the parent program is called with
    the environment variable ``DEBUG`` = ``True``

    Args:
        *cmd: list(cmd) is passed to subprocess.Popen as first argument
        timeout: communicatoin timeout. If -1, 'communicate' isn't called
        fail_handle: {fail,nag,report,ignore}
            * fail: raises CommandError
            * nag: Returns None, prints stderr
            * report: returns None, but hides stderr
            * ignore: returns stdout, despite error (default behaviour)
        **kwargs: all are passed to ``subprocess.Popen``

    Returns:
        stdout from command's communication
        ``None`` if stderr with 'fail == False'

    Raises:
        CommandError

    """
    cmd_l = list(cmd)
    if timeout is not None and timeout < 0:
        process = subprocess.Popen(cmd_l, **kwargs)  # DONT: *cmd_l here
        return None
    process = subprocess.Popen(cmd_l,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True,
                               **kwargs)
    stdout, stderr = process.communicate(timeout=timeout)
    if os.environ.get('DEBUG', False):
        print(cmd_l, mark='act')
        print(stdout, mark='bug')
        print(stderr, mark='err')
        print("returncode:", process.returncode, mark='err')
    if process.returncode != 0:
        if fail_handle == 'fail':
            raise CommandError(cmd_l, stderr)
        if fail_handle in ('report', 'nag'):
            if fail_handle == 'nag':
                print(stderr, mark=4)
            return None
    return stdout or 'success'


def notify(info: str = 'alert', timeout: float = 5) -> None:
    """
    Notify alert

    Args:
        info: str = information to notify
        timeout: int = remove notification after seconds. [0 => permament]
        send_args: arguments passed to notify command

    Returns:
        ``None``

    """
    icon_p = Path(__file__).parent.joinpath('exclaim.jpg').resolve()
    if not icon_p.is_file():
        icon = ''
    else:
        icon = str(icon_p)
    timeout *= 1000  # milliseconds
    notify_interface = dbus.Interface(
        object=dbus.SessionBus().get_object('org.freedesktop.Notifications',
                                            '/org/freedesktop/Notifications'),
        dbus_interface='org.freedesktop.Notifications')
    notify_interface.Notify('PSPrudence', 0, str(icon), 'Alert(s)', info, [],
                            {'urgency': 1}, int(timeout))
    return None
