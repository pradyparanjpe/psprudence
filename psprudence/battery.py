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
"""Battery Handles (special case)"""

from typing import Optional, Union

import psutil

from psprudence.shell_comm import notify, process_comm


def charge() -> Optional[Union[int, bool]]:
    """Probe function for battery"""
    battery = psutil.sensors_battery()
    if battery is None:
        return None
    if not battery.power_plugged:
        return False
    return battery.percent


def discharge() -> Optional[Union[int, bool]]:
    """Probe function for battery"""
    battery = psutil.sensors_battery()
    if battery is None:
        return None
    if battery.power_plugged:
        return False
    return battery.percent


def panic(suspend_at: str = '10'):
    """
    Battery Actions.

    Args:
        suspend_at: minutes remaining when computer should suspend

    Notifies:
        ``notify`` emergency multiple times and suspends if critical
    """
    battery = psutil.sensors_battery()
    if battery is None:
        return
    if battery.power_plugged:
        return
    time_left = battery.secsleft / 60  # minutes
    suspend = float(suspend_at)
    print(f'{time_left=}', f'{suspend=}')
    if time_left < suspend:
        process_comm('systemctl', 'suspend', timeout=-1, fail_handle='notify')
    elif time_left < suspend * 2:
        notify('Battery Too Low Suspending Session...', timeout=suspend)
