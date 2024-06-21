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
from typing import Optional

from desktop_notifier import DesktopNotifier

from psprudence import print, project_root
from psprudence.errors import CommandError

DEFAULT_NOTIFICATION = DesktopNotifier(app_name='PSPrudence',
                                       app_icon=project_root.resolve() /
                                       'data/exclaim.jpg')
"""Default Notification."""


def process_comm(*cmd: str,
                 timeout: int = None,
                 fail_handle: str = 'fail',
                 **kwargs) -> Optional[str]:
    """
    Generic process definition and communication.
    Raw actions, outputs, errors are displayed
    when the parent program is called with
    the environment variable ``DEBUG`` = ``True``

    Parameters
    -----------
    *cmd : str
        ``list(cmd)`` is passed to :func:`subprocess.Popen` as first argument
    timeout : int, optional
        communicatoin timeout. If -1, the command is not communicated
    fail_handle : {fail,nag,report,ignore}
        - fail: raises CommandError
        - nag: Returns None, prints stderr
        - report: returns None, but hides stderr
        - ignore: returns stdout, despite error (default behaviour)
    **kwargs
        all are passed to ``subprocess.Popen``

    Returns
    --------
    str
        stdout from command's communication
    ``None``
        if stderr with 'fail == False'

    Raises
    -------
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


def notify(info: str = 'alert', timeout: Optional[float] = 5) -> None:
    """
    Notify alert.

    Parameters
    -----------
    info : str
        Information to notify
    timeout : int
        Remove notification after seconds. [0 => permament]

    Returns
    --------
    ``None``

    """
    DEFAULT_NOTIFICATION.send_sync(title='Alert',
                                   message=info,
                                   timeout=(timeout * 1000 if timeout else -1))
