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
Functions that return of current values (float) of various sensors.

This file may be used as template to define custom sensor probes
"""

import psutil


def cpu():
    """CPU usage."""
    return psutil.cpu_percent()


def load(minutes: str = '1'):
    """
    CPU load.

    Parameters
    -----------
    minutes : {1, 5, 15}
        minutes average [1, 5, 15]
    """
    segment = {'1': 0, '5': 1, '15': 2}.get(str(minutes), 0)
    return psutil.getloadavg()[segment] * 100 / psutil.cpu_count()


def temperature():
    "Core temperature."
    return psutil.sensors_temperatures()['coretemp'][0].current


def memory():
    "RAM usage."
    return psutil.virtual_memory().percent
