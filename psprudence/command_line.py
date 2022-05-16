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
"""Command line inputs"""

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from argcomplete import autocomplete

from psprudence import __version__


def _cli() -> ArgumentParser:
    """
    Parser for autodoc
    """
    config_file = Path(__file__).parent / 'config.yml'
    description = '''
    Peripherial Signal Prudence:
    Monitor peripherals and signal alert values for prudent action.
    Configuration: "${XDG_CONFIG_HOME:-${HOME}/.config}/psprudence/config.yml"
    ''' + f'''Default: {config_file}
    '''
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=description)
    parser.add_argument('--debug',
                        action='store_true',
                        help='Print debugging output')
    parser.add_argument('-i',
                        '--interval',
                        type=float,
                        default=10,
                        help='update interval in seconds')
    parser.add_argument('-d',
                        '--disable',
                        type=str,
                        nargs='*',
                        default=[],
                        help='disable monitoring peripherals')
    parser.add_argument('-c',
                        '--config',
                        dest='custom',
                        type=Path,
                        default=None,
                        help='custom configuration file path')
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s ' + ' '.join(
            (__version__, 'form', str(Path(__file__).resolve().parent),
             f'(python {sys.version_info.major}.{sys.version_info.minor})')))

    # python bash/zsh completion
    autocomplete(parser)
    return parser


def cli() -> dict:
    """
    Command line arguments
    """
    parser = _cli()
    return vars(parser.parse_args())
