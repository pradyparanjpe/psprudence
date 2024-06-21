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
"""PSPrudence's defined errors"""


class PSPrudenceError(Exception):
    """Base error for psprudence(Exception)."""

    def __init__(self, *args):
        super(Exception, self).__init__(*args)


class CommandError(PSPrudenceError):
    """
    Base class for subprocess failure.

    Parameters
    -----------
        cmd : list
            command passed to shell for execution
        err : str
            stderr received from shell after failure

    """

    def __init__(self, cmd: list, err: str = None) -> None:
        super().__init__(
            self, f"""
        Command Passed for execution:
        {cmd}

        STDERR from command:
        {err}
        """)


class CMDValueError(ValueError, PSPrudenceError):
    """Bad command value."""
