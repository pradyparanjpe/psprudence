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
"""Initialize desktop files (Currently only for Linux)"""

import platform
from os import environ
from pathlib import Path

from psprudence import print


def generate_desktop(os_name: str) -> str:
    """
    Generate content for desktop file

    Args:
        os_name: name of os

    Returns:
        content

    Raises:
        NotImplementedError: not Linux
    """
    if os_name != 'linux':
        print('init is currently supported only for Linux.', mark='err')
        raise NotImplementedError
    iconfile = Path(__file__).parent / 'exclaim.jpg'
    df_template = (Path(__file__).parent / 'psprudence.desktop').read_text()
    return df_template + f"\nIcon={iconfile}"


def app_path(os_name: str) -> Path:
    """
    Infer path to write .desktop file

    Args:
        os_name: name of os

    Returns:
        Path to .desktop file

    Raises:
        NotADirectoryError: couldn't locate applications directory
        NotImplementedError: not Linux
    """
    if os_name != 'linux':
        print('init is currently supported only for Linux.', mark='err')
        raise NotImplementedError
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
    raise NotADirectoryError


def autostart_path(os_name: str) -> Path:
    """
    Infer path to autostart file

    Args:
        os_name: name of os

    Returns:
        Path to autostart .desktop file

    Raises:
        NotADirectoryError: couldn't locate autostart directory
        NotImplementedError: not Linux
    """
    if os_name != 'linux':
        print('autostart is currently supported only for Linux.', mark='err')
        raise NotImplementedError
    xdg_config_dirs = environ.get('XDG_CONFIG_DIRS', '').split(':')
    xdg_config_dirs.insert(0, environ.get('XDG_CONFIG_HOME', ''))
    xdg_config_dirs.append(str(Path.home() / '.config'))
    while '' in xdg_config_dirs:
        xdg_config_dirs.remove('')
    for xdg_config_home in xdg_config_dirs:
        app_dir = Path(xdg_config_home) / 'autostart'
        if app_dir.is_dir():
            # found a path
            return app_dir / 'psprudence.desktop'
    raise NotADirectoryError


def deinit(*df_paths: Path) -> int:
    """
    delete the .desktop files

    Args:
        autostart: link desktop file to autostart

    Returns:
        exit code

    Raises:
        PermissionError: User is root
    """
    for path in df_paths:
        path.unlink(missing_ok=True)
    return 0


def initialize(**kwargs) -> int:
    """
    Initialize an .desktop file

    Args:
        autostart: link desktop file to autostart

    Returns:
        exit code

    Raises:
        PermissionError: User is root
    """
    # TODO cross-platform
    if environ.get('USER') == 'root':
        raise PermissionError('Do not run as Root')
    os_name = platform.system().lower()
    df_content = generate_desktop(os_name)
    df_path = app_path(os_name)
    as_path = autostart_path(os_name)
    if kwargs.get('delete'):
        return deinit(df_path, as_path)
    if df_path.is_file():
        print('Desktop file is already created.', mark='info')
    else:
        with open(df_path, 'w') as df_handle:
            df_handle.write(df_content)
    if kwargs.get('autostart'):
        if as_path.is_file():
            print('Autostart file is already linked.', mark='info')
        else:
            as_path.symlink_to(df_path)
    return 0
