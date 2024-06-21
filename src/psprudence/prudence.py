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
"""Prudence sensor."""

from typing import Any, Callable, Dict, Optional, Union

from psprudence.build_meth import build_func_handle


def default_alert_check(parent, val: Union[float, Any]) -> bool:
    """
    Default fallback for :py:attr:`psprudence.prudence.Prudence.alert_check`.

    Default val input is float. (floatable strings are passed as float)
    Shall be able to process output from
    :meth:`psprudence.prudence.Prudence.probe`

    Parameters
    -----------
    parent
        parent object handle
    val : Union[float, Any]
        current value

    Returns
    --------
    bool
        If alert should be called
    """
    if not isinstance(val, (int, float)):
        val = float(val)
    if parent.reverse:
        if val < parent._next_warn:
            parent._next_warn = parent.warn_res - min(val, parent._next_warn)
            return True
    else:
        if val > parent._next_warn:
            parent._next_warn = parent.warn_res + max(val, parent._next_warn)
            return True
    return False


def default_attempt_reset(parent, val: float):
    """
    Default fallback for :py:attr:`psprudence.prudence.Prudence.attempt_reset`

    Parameters
    -----------
    parent
        parent object handle
    val : float
        current value

    """
    direction = -1 if parent.reverse else 1
    if (direction * val) < (direction * parent.min_warn):
        parent._next_warn = parent.min_warn


class Prudence():
    """
    Prudence sensor.

    Parameters
    -----------
    alert : str
        Alert type string sent to notify

    min_warn : float
        Warnings start after this

    probe : Union[Callable, str]
        Probes the sensor.

        Callable
            Python function handle
        str
            - multi-line shell code-block
            - Path to file and the function that returns value as output
                - python: ``py: /path/to/pyfile:funcname:arg1:arg2:arg3``
                - shell-script: ``sh: /path/to/shfile:funcname:arg1:arg2:arg3``

        Returns
        ~~~~~~~~
        float
            value (float or float-string)
        ``True``
            process alert without value
        ``False``
            override and silence alert
        ``None``
            sensor gets disabled.

    units : str
        Units to display after value [default: '']
    warn_res : int
        Warnings are recorded on every increment of [default: 1]
    reverse : bool
        Direction of panic is reversed [default: False]
    enabled : bool
        This alert is enabled

    panic : Union[Callable[[], Any], str]
        Function to be called if value is actionable.

        Type is same as `probe`'s type (Callable, str)

    """

    def __init__(self, alert: str, min_warn: float,
                 probe: Union[Callable, str], **kwargs):
        self.alert: str = alert
        """Alert type string sent to notify."""

        self.min_warn: float = min_warn
        """Warnings start after this."""

        self.units: str = kwargs.get('units', '')
        """Units to display after value."""

        self.warn_res: float = kwargs.get('warn_res', 1.)
        """Warning resolution difference between consecutive warning values."""

        self.reverse: bool = kwargs.get('reverse', False)
        """Reversed direction of panic (alerts as value decreases)."""

        self.enabled: bool = kwargs.get('enabled', True)
        """This alert is enabled."""

        self._probe: Union[Callable[[], Optional[Union[bool, float, str]]],
                           str] = probe

        self._panic: Union[Callable[[], Any],
                           str] = kwargs.get('panic', lambda: None)

        self._alert_check: Union[Callable[[Any, Union[float, Any]], bool],
                                 str] = kwargs.get('alert_check',
                                                   default_alert_check)

        self._attempt_reset: Union[Callable[[Any, Union[float, Any]], Any],
                                   str] = kwargs.get('attempt_reset',
                                                     default_attempt_reset)

        self._next_warn = self.min_warn

    def __str__(self) -> str:
        direct = 'decreasing' if self.reverse else 'increasing'
        return f'Warn {self.alert} {direct} beyond {self.min_warn}{self.units}'

    @property
    def probe(self) -> Callable[[], Optional[Union[bool, Any]]]:
        """
        This callable is called to probe current value,
        alert text is its __str__ form.

        You may replace this property suitably.

        Returns
        --------
        Callable[[], Optional[Union[bool, Any]]]
            The callable must return following types.
                - ``None``: Probe failure.
                - ``True``: Send an alert without value.
                - ``False``: Do not sent alert.
                - Any value that can be interpreted as float,
                  alert is its __str__ rounded to 2 decimals.
                - Any value that can be processed by
                  :meth:`psprudence.prudence.Prudence.alert_check`.

        """
        if isinstance(self._probe, Callable):
            return self._probe
        self._probe = build_func_handle(self._probe, self.alert + ' probe')
        return self._probe

    @probe.setter
    def probe(self, callback: Callable[[], Any]):
        self._probe = callback

    @property
    def panic(self) -> Callable[[], Any]:
        """
        Function called if value is actionable

        Returns
        --------
        Callable[[], Any]
            Panic callable. Return value from callable is ignored.
        """
        # parse panic command
        if isinstance(self._panic, Callable):
            return self._panic
        self._panic = build_func_handle(self._panic, self.alert + ' panic')
        return self._panic

    @panic.setter
    def panic(self, callback: Callable[[], Any]):
        self._panic = callback

    @property
    def alert_check(self) -> Callable[[Any, Union[float, Any]], bool]:
        """
        Called to decide whether alert is to be signalled.

        Parameters
        -----------
        self
            This parent object is passed to the
            callable as the first positional argument
        val
            Current value is passed to callable as second argument


        Returns
        --------
        Callable[[Any, Union[float, Any]], bool]
            If alert should be called
        """
        if isinstance(self._alert_check, Callable):
            return self._alert_check
        self._alert_check = build_func_handle(self._alert_check,
                                              self.alert + ' alert_check')
        return self._alert_check

    @alert_check.setter
    def alert_check(self, callback: Callable[[Any, Union[float, Any]], bool]):
        self._alert_check = callback

    @property
    def attempt_reset(self) -> Callable[[Any, float], Any]:
        """
        Called to decide whether to reset next warning value.

        Parameters
        -----------
        self
            This parent object is passed to the
            callable as the first positional argument
        val
            current value is passed to the callable as second argument

         """
        if isinstance(self._attempt_reset, Callable):
            return self._attempt_reset
        self._attempt_reset = build_func_handle(self._attempt_reset,
                                                self.alert + ' attempt_reset')
        return self._attempt_reset

    @attempt_reset.setter
    def attempt_reset(self, callback: Callable[[Any, float], Any]):
        self._attempt_reset = callback

    def __repr__(self):
        kwargs = [
            f'{key}={getattr(self, key)}'
            for key in ('alert', 'units', 'min_warn', 'warn_res', 'reverse',
                        'enabled', 'probe', 'panic')
        ]
        return (str(self.__class__) + '(' + ', '.join(kwargs) + ')')

    def __call__(self,
                 val: Optional[Union[bool, Any]] = None) -> Optional[str]:
        """
        Recurrent call.

        Notifies
        -----------
        ``notify`` emergency multiple times and runs panic if `critical`

        Parameters
        -----------
        val : Union[bool, Any], optional
            [For Debugging only] supply custom value

        Returns
        --------
        str, optional
            Alert notification string.

        """
        if (not self.enabled) and (val is None):
            return
        if val is None:
            val = self.probe()
            if val is None:
                self.enabled = False
                return
            if val is False:
                return
            if val is True:
                self.panic()
                return f'</u>{self.alert}</u>: alert'
        try:
            val = float(val)
            if self.alert_check(self, val):
                self.panic()
                return f'<b>{self.alert}</b>: {val: 0.2f}{self.units}'
        except ValueError as err:
            if any('success' in arg for arg in err.args):
                print(f'{self.alert}:')
                print('Probe shell/os command did not print anything.')
                print('Disabling.')
                self.enabled = False
                return None
            if self.alert_check(self, val):
                self.panic()
                return f'<b>{self.alert}</b>: {val}{self.units}'
        self.attempt_reset(self, val)
        return


def create_alerts(config: Dict[str, Dict[str, Any]]) -> Dict[str, Prudence]:
    """
    Create alerts using :py:class:`psprudence.prudence.Prudence`

    Parameters
    -----------
    config : Dict[str, Dict[str, Any]]
        dict of kwargs for :py:class:`psprudence.prudence.Prudence`

    Returns
    --------
    Dict[str, Prudence]
        Callable prudence sensors
    """
    return {
        name: Prudence(**kwargs)
        for name, kwargs in config.items()
        if (name != 'global' and kwargs.get('enabled', True))
    }
