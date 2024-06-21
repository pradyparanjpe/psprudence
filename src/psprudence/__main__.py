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
"""Command-line EntryPoint."""

import platform
from os import environ
from pathlib import Path
from time import sleep
from typing import Dict, Optional, Sequence

from xdgpspconf import ConfDisc

from psprudence import print
from psprudence.command_line import cli
from psprudence.initialize import init_call
from psprudence.prudence import Prudence, create_alerts
from psprudence.shell_comm import notify


def read_configs(custom: Optional[Path] = None):
    """
    Combine configurations.

    Args
    -----
    custom : path, optional
        Custom configuration location
    """
    configs = list(
        ConfDisc('psprudence', __file__).read_config(custom=custom).values())
    config = {}
    for vals in reversed(configs):
        for alert in vals:
            if alert in config:
                config[alert].update(vals[alert])
            else:
                config[alert] = vals[alert]
    return config


def main_loop(interval: float = 0,
              disable: Sequence[str] = '',
              debug: bool = False,
              custom: Optional[Path] = None) -> int:
    """
    Main monitoring loop

    Parameters
    -----------
    interval : float
        Update interval
    disable : Sequence[str]
        disable alerts
    debug : bool
        print debugging output
    custom : Path, optional
        custom configuration

    Returns
    --------
    int
        exit code
    """
    config = read_configs(custom)

    persist: int = config.get('global', {'persist': 5})['persist']
    if not interval:
        interval = config.get('global', {'interval': 10.})['interval']

    # filter
    peripherals: Dict[str, Prudence] = {
        name: alert
        for name, alert in create_alerts(config).items() if name not in disable
    }

    if debug:
        print(config, mark='bug', iterate=True)
        print('disabled:', mark='bug', pref='off', pref_s='>', iterate=True)
        print(disable,
              mark='bug',
              pref='off',
              pref_s='>',
              iterate=True,
              indent=1)
        print(f'interval: {interval}', mark='bug')

    try:
        # It is bad to use a "while true loop"
        # The following loop runs for almost 70 years if interval is 1 second
        for _ in range(0x7fffffff):
            alert = []
            for name, mon in peripherals.items():
                mon_alert = mon()
                if debug:
                    print(name, 'enabled' * mon.enabled, mon_alert, mark='bug')
                if mon_alert is not None:
                    alert.append(mon_alert)
            if alert:
                notify('\n'.join(alert), timeout=persist)
            sleep(interval)
    except (KeyboardInterrupt, InterruptedError):
        print("Caught interrupt, quitting safely.", mark=1)
        return 0


def main() -> int:
    cliargs = cli()
    if cliargs.get('call', 'monitor') == 'init':
        return init_call(**cliargs)
    if platform.system() == 'Linux' and not environ.get('DISPLAY'):
        print('PSPrudent needs graphical interface.', mark='err')
        return 1
    if 'call' in cliargs:
        del cliargs['call']
    return main_loop(**cliargs)


if __name__ == '__main__':
    main()
