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
        probe:
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
                same as `probe`'s format

            returns:
               all are ignored

    """

    def __init__(self, alert: str, min_warn: float,
                 probe: Union[Callable, str], **kwargs):
        self.alert: str = alert
        """Alert type string sent to notify"""

        self.units: str = kwargs.get('units', '')
        """Units to display after value"""

        self.min_warn: float = min_warn
        """Warnings start after this"""

        self.res_warn: float = kwargs.get('res_warn', 1.)
        """Warnings are recorded on this increment"""

        self.reverse: bool = kwargs.get('reverse', False)
        """Reversed direction of panic (alerts as value decreases)"""

        self.enabled: bool = kwargs.get('enabled', True)
        """This alert is enabled"""

        self._panic: Union[Callable[[], Any],
                           str] = kwargs.get('panic', lambda: None)

        self._probe: Union[Callable[[], Optional[Union[bool, float, str]]],
                           str] = probe

        self._next_warn = self.min_warn

    @property
    def probe(self) -> Callable[[], Any]:
        """
        This callable is called to probe current value

        Replace this method suitably

        Returns:
            probe failure ``None``
            send an alert without value ``True``
            do not sent alert ``False``
        """
        if isinstance(self._probe, Callable):
            return self._probe
        if self._probe[:4] == 'py: ':
            self._probe = self._custom_py(self._probe[4:])
        else:
            if self._probe[:4] == 'sh: ':
                # already a file
                shell_code = self._probe[4:]
            else:
                # generate a panic temp-file
                shell_code = self._temp_code(self._probe)
            self._probe = lambda: process_comm(
                'sh', shell_code, fail_handle='report')
        return self._probe

    @probe.setter
    def probe(self, callback: Callable[[], Any]):
        self._probe = callback

    @property
    def panic(self) -> Callable[[], Any]:
        """Function called if value is actionable"""
        # parse panic command
        if isinstance(self._panic, Callable):
            return self._panic
        if self._panic[:4] == 'py: ':
            self._panic = self._custom_py(self._panic[4:])
        else:
            if self._panic[:4] == 'sh: ':
                # already a file
                shell_code = self._panic[4:]
            else:
                # generate a panic temp-file
                shell_code = self._temp_code(self._panic)
            self._panic = lambda: process_comm(
                'sh', shell_code, fail_handle='report')
        return self._panic

    @panic.setter
    def panic(self, callback: Callable[[], Any]):
        self._panic = callback

    def __repr__(self):
        kwargs = [
            f'{key}={getattr(self, key)}'
            for key in ('alert', 'units', 'min_warn', 'res_warn', 'reverse',
                        'enabled', 'probe', 'panic')
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
        if (not self.enabled) and (val is None):
            return
        if val is None:
            val = self.probe()
            if val is None:
                self.enabled = False
                return
            elif val is False:
                return
            elif val is True:
                self.panic()
                return f'</u>{self.alert}</u>: alert'
        val = float(val)
        if self.increment(val):
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
        return temp_script

    def _custom_py(self,
                   pyexec: str) -> Callable[[], Optional[Union[bool, float]]]:
        """Create a custom executable wrapper around supplied function"""
        pybase, pycall, *pyargs = pyexec.split(':')
        if '/' not in pybase:
            pybase = Path(__file__).parent / pybase
        pyfile = Path(pybase).with_suffix('.py').expanduser().resolve()
        if not (pyfile.is_file() or pyfile.with_suffix('.pyx').is_file()):
            # pyfile may be a pure python or compiled pyx (cython) module
            print(f'Error creating py-callable for {self.alert}', mark='err')
            print(f'No such python file ({pyfile}x?)', mark='err')
            return lambda: None
        try:
            _locals = {}
            exec_code = [
                'import sys', f'sys.path.append("{str(pyfile.parent)}")',
                f'from {pyfile.stem} import {pycall} as call'
            ]
            exec('\n'.join(exec_code), globals(), _locals)
            call: Callable[..., Optional[Union[bool, float]]] = _locals['call']

        except (FileNotFoundError, ModuleNotFoundError, ImportError) as err:
            print(f'Error creating py-callable for {self.alert}', mark='err')
            print(err)
            return lambda: None
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
    return {
        name: Prudence(**kwargs)
        for name, kwargs in config.items()
        if (name != 'global' and kwargs.get('enabled', True))
    }
