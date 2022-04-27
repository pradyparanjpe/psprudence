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
"""Prudence sensor"""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict, Optional, Union

from psprudence import print
from psprudence.shell_comm import process_comm


class Prudence():
    """
    Prudence sensor

    Args:
        alert: Alert type string sent to notify
        units: Units to display after value [default: '']
        min_warn: Warnings start after this
        res_warn: Warnings are recorded on this increment [default: 1]
        reverse: Direction of panic is reversed [default: False]
        enabled: This alert is enabled
        probe_cmd:
            description:
                probes the sensor.
            formats:
                - python function handle (Callable)

                - path to file and the function that returns value (str):
                    - python: 'py: /path/to/pyfile:funcname:arg1:arg2:arg3'

                    - shell-script: 'sh: /path/to/shfile' (output is value)

                - multi-line shell code-block (str)

            returns:
                - value (float or float-string)
                - ``True``: process alert without value
                - ``False``: override and silence alert
                - ``None``: sensor gets disabled.

        panic:
            description:
                function to be called if value is actionable.

            format:
                same as `probe_cmd`'s format

            returns:
               all are ignored

    """

    def __init__(self, alert: str, min_warn: float,
                 probe_cmd: Union[Callable, str], **kwargs):

        self.enabled: bool = kwargs.get('enabled', True)
        """This alert is enabled"""

        if isinstance(probe_cmd, Callable):
            _probe = probe_cmd
        else:
            if probe_cmd[:4] == 'py: ':
                _probe = self._custom_py(probe_cmd[4:])
            else:
                if probe_cmd[:4] == 'sh: ':
                    shell_code = probe_cmd[4:]
                else:
                    shell_code = self._temp_code(probe_cmd)
                _probe = lambda: process_comm(
                    'sh', shell_code, fail_handle='report')

        if _probe is None:
            self.enabled = False
            print("Couldn't parse probe_cmd to create a callable probe",
                  mark='warn')
            return

        self.probe: Callable[[], Optional[Union[bool, float, str]]] = _probe
        """
        This callable is called to probe current value

        Replace this method suitably

        Returns:
            probe failure ``None``
            send an alert without value ``True``
            do not sent alert ``False``
        """

        panic: Optional[Union[Callable[[], Any],
                              str]] = kwargs.get('panic', None)
        if panic is None:
            self.panic: Optional[Callable[[], Any]] = None
            """If value is actionable, callback"""
        elif isinstance(panic, Callable):
            self.panic = panic
        else:
            if panic[:4] == 'py: ':
                self.panic = self._custom_py(panic[4:])
            else:
                if panic[:4] == 'sh: ':
                    shell_code = panic[4:]
                else:
                    shell_code = self._temp_code(panic)
                self.panic = lambda: process_comm(
                    'sh', shell_code, fail_handle='report')

        self.alert: str = alert
        """Alert type string sent to notify"""

        self.units: str = kwargs.get('units', '')
        """Units to display after value"""

        self.min_warn: float = min_warn
        """Warnings start after this"""

        self.res_warn: float = kwargs.get('res_warn', 1.)
        """Warnings are recorded on this increment"""

        self.reverse: bool = kwargs.get('reverse', False)
        """Reversed direction of panic (alerts as value decreses)"""

        self._next_warn = self.min_warn

    def __repr__(self):
        kwargs = [
            f'{key}={getattr(self, key)}'
            for key in ('alert', 'units', 'min_warn', 'res_warn')
        ]
        return (str(self.__class__) + '(' + ', '.join(kwargs) + ')')

    def __call__(self, val: Union[str, float] = None) -> Optional[str]:
        """
        Recurrent call

        Args:
            val: [For Debugging only] supply custom value

        Notifies:
            ``notify`` emergency multiple times and suspends if critical

        Returns:
            Whether alert was notified

        """
        if not (self.enabled or val):
            return
        if val is None:
            val = self.probe()
            if val is None:
                self.enabled = False
                return
            elif val is False:
                return
            elif val is True:
                if self.panic is not None:
                    self.panic()
                return f'</u>{self.alert}</u>: alert'
        val = float(val)
        if self.increment(val):
            if self.panic is not None:
                self.panic()
            return f'<b>{self.alert}</b>: {val: 0.2f}{self.units}'
        self.attempt_reset(val)
        return

    def _temp_code(self, cmd: str = None) -> str:
        """
        Create a callable call from shell scripts

        Args:
            cmd: List of commands.

        Return:
            A call function.
        """
        with NamedTemporaryFile('w', delete=False) as shell_script:
            print(cmd, file=shell_script, disabled=True)
            temp_script = shell_script.name
        print(temp_script)
        return temp_script

    @staticmethod
    def _custom_py(
            pyexec: str
    ) -> Optional[Callable[[], Optional[Union[bool, float]]]]:
        """Create a custom executable wrapper around supplied function"""
        pybase, pycall, *pyargs = pyexec.split(':')
        if '/' not in pybase:
            pybase = Path(__file__).parent / pybase
        pyfile = Path(pybase).with_suffix('.py').expanduser().resolve()
        if not (pyfile.is_file() or pyfile.with_suffix('.pyx').is_file()):
            # pyfile may be a pure python or compiled pyx (cython) module
            return
        try:
            _locals = {}
            exec_code = [
                'import sys', f'sys.path.append("{str(pyfile.parent)}")',
                f'from {pyfile.stem} import {pycall} as call'
            ]
            exec('\n'.join(exec_code), globals(), _locals)
            call: Callable[..., Optional[Union[bool, float]]] = _locals['call']
        except (FileNotFoundError, ModuleNotFoundError, ImportError):
            return
        return lambda: call(*pyargs)

    def increment(self, val: float) -> bool:
        """
        This method is called to decide whether alert is to be called out

        Replace this method suitably

        Args:
            val: current value

        Returns:
            if alert should be called
        """
        if self.reverse:
            if val < self._next_warn:
                self._next_warn = self.res_warn - min(val, self._next_warn)
                return True
        else:
            if val > self._next_warn:
                self._next_warn = self.res_warn + max(val, self._next_warn)
                return True
        return False

    def attempt_reset(self, val: float):
        """
        This method is called to decide whether to reset next warning value

        Replace this method suitably

        Args:
            val: current value

        """
        direction = -1 if self.reverse else 1
        if (direction * val) < (direction * self.min_warn):
            self._next_warn = self.min_warn


def create_alerts(config: Dict[str, Dict[str, Any]]) -> Dict[str, Prudence]:
    """
    Create alerts using :py:class:`psprudence.prudence.Prudence`

    Args:
        config: dict of kwargs for :py:class:`psprudence.prudence.Prudence`

    Returns:
        Callable prudence sensors
    """
    alerts = {}
    for name, kwargs in config.items():
        if name != 'global':
            sensor = Prudence(**kwargs)
            if sensor.enabled:
                alerts[name] = sensor
    return alerts
