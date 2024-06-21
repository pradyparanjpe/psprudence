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
Build methods form configuration.

Configuration strings may be of following formats

- path to file and/or the function that returns value:
    - python: 'py: /absolute/path/to/py_file:func_name:arg1:arg2:...'
    - shell: 'sh: /absolute/path/to/sh_file:func_name:arg1:arg2:...'
    - system call: 'os: /absolute/path/to/executable:arg1:arg2:...'

- multi-line shell code-block (str)

Python functions must return appropriate values for respective functions.
Shell functions must print values in string format.
OS calls must be direct executables that print values in string format.
"""

import platform
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable, Dict, List, Optional, Union

from xdgpspconf import DataDisc

from psprudence import print
from psprudence.shell_comm import process_comm

DATA_PATHS = DataDisc(project='psprudence', shipped=Path(__file__)).get_loc()


def _temp_code(cmd: str, name_base: str = '') -> Path:
    """
    Create a callable call from shell scripts.

    Parameters
    -----------
    cmd : str
        List of commands
    name_base : str
        base for temporary file

    Return
    -------
    Path
        A call function.
    """
    name_base = '_'.join(['psprudence', *name_base.split(' ')])
    with NamedTemporaryFile('w', delete=False,
                            prefix=name_base) as shell_script:
        temp_script = Path(shell_script.name)
        temp_script.write_text(cmd)

    return temp_script


def _source_file(base: Union[str, Path],
                 exts: Optional[List[str]] = None) -> Path:
    """
    Check if source file exists.

    Returns
    --------
    Path
        Existing file path with extension

    Raises
    -------
    FileNotFoundError
    """
    exts = exts or ['']

    prefix_paths = [Path()] if Path(base).is_absolute() else DATA_PATHS

    for data_path in prefix_paths:
        srcbase = data_path / base
        for ext in exts:
            src_file = srcbase.with_suffix(ext)
            if src_file.is_file():
                return src_file
        if srcbase.is_file():
            return srcbase
    print(f'No such source file ({base}.{exts})', mark='err')
    print(f'Searched locations:')
    print(prefix_paths, mark='list', iterate=True)
    print(f'Possible solution: supply absolute path.', mark='act')
    raise FileNotFoundError


def build_py_handle(srcstr: str,
                    util: str = 'UNKNOWN') -> Callable[..., Optional[str]]:
    """
    Parse string and return python function handle

    Parameters
    -----------
    srcstr : str
        py: /absolute/path/to/py_file:func_name:arg1:arg2:...
    util : str
        name object that uses this constructor (used to elaborate debug)

    Returns
    --------
    Callable
        Handle to callable function

    Raises
    --------
    FileNotFoundError
    ModuleNotFoundError
    ImportError
    """
    pybase, pycall, *pyargs = srcstr[4:].split(':')

    try:
        pyfile = _source_file(pybase, ['.py', '.pyx'])
        _locals = {}
        exec_code = [
            'import sys', f'sys.path.append("{str(pyfile.parent)}")',
            f'from {pyfile.stem} import {pycall} as call'
        ]
        exec('\n'.join(exec_code), globals(), _locals)
        call: Callable[..., Optional[str]] = _locals['call']

        def pyfunc(*args, **kwargs):
            return call(*pyargs, *args, **kwargs)

        pyfunc.__doc__ = '\n'.join((f'Python function: {util}', '',
                                    (call.__doc__
                                     or 'No __doc__ in call function')))

        return pyfunc

    except (FileNotFoundError, ModuleNotFoundError, ImportError) as err:
        print(f'Error creating py-callable handle for {util}', mark='err')
        raise err


def build_sh_handle(srcstr: str,
                    util: str = 'UNKNOWN') -> Callable[..., Optional[str]]:
    """
    Parse string and return shell file handle for function call

    sh_file is sourced. Its output is ignored.

    Parameter
    ----------
    srcstr : str
        sh: /absolute/path/to/sh_file:func_name:arg1:arg2:...
    util : str
        name object that uses this constructor (used to elaborate debug)

    Returns
    --------
    Callable[..., Optional[str]]
        Handle to callable function

    Raises
    -------
    FileNotFoundError
    ModuleNotFoundError
    ImportError
    """
    shbase, shcall, *shargs = srcstr[4:].split(':')

    try:
        shfile = _source_file(shbase, ['.sh'])

    except (FileNotFoundError, ModuleNotFoundError, ImportError) as err:
        print(f'Error creating sh-callable handle for {util}', mark='err')
        raise err

    caller_wrapper = '\n'.join([
        '#!/usr/bin/env sh', '# -*- coding: utf-8; mode: shell-script; -*-',
        f'. {shfile}', f'{shcall} $@'
    ])
    func_file = _temp_code(caller_wrapper, shcall)

    def shfunc(*args):
        return process_comm('sh',
                            str(func_file),
                            *shargs,
                            *args,
                            fail_handle='report')

    shfunc.__doc__ = f"""Shell function wrapper: {util}"""

    return shfunc


def build_ch_handle(srcstr: str,
                    util: str = 'UNKNOWN') -> Callable[..., Optional[str]]:
    """
    THIS IS NOT YET IMPLEMENTED

    Parse string and return BAT file handle for function call.
    Batch file is sourced. Its output is ignored.

    Parameters
    -----------
    srcstr : str
        ch: /absolute/path/to/ch_file.bat:func_name:arg1:arg2:...
    util : str
        name object that uses this constructor (used to elaborate debug)

    Returns
    --------
    Callable[..., Optional[str]]
        Handle to callable function

    Raises
    -------
    NotImplementedError
    FileNotFoundError
    ModuleNotFoundError
    ImportError
    """
    print(srcstr, mark='err')
    print(util, mark='err')
    raise NotImplementedError(
        'Batch script function declarations are planned for future.\n' +
        'You may try supplying pre-defined scripts in the format ``os: ...``')


def build_otf_handle(srcstr: str,
                     util: str = 'UNKNOWN') -> Callable[..., Optional[str]]:
    """
    Parse string and return shell file handle generated on the fly

    Parameters
    -----------
    srcstr : str
        executable string that prints value at the end
    util : str
        name object that uses this constructor (used to elaborate debug)

    Returns
    --------
    Callable[..., Optional[str]]
        Handle to callable function

    Raises
    -------
    FileNotFoundError
    ModuleNotFoundError
    ImportError
    NotImplementtedError
    """
    if platform.system() == "Windows":
        raise NotImplementedError(
            'Windows on the fly script is in future plan')

    caller_wrapper = '\n'.join([
        '#!/usr/bin/env sh', '# -*- coding: utf-8; mode: shell-script; -*-',
        srcstr
    ])
    func_file = _temp_code(caller_wrapper, f'otf_{util}_call')

    def otffunc(*args):
        return process_comm('sh', str(func_file), *args, fail_handle='report')

    otffunc.__doc__ = f"""On The Fly Function handle: {util}"""
    return otffunc


def build_os_handle(srcstr: str,
                    util: str = 'UNKNOWN') -> Callable[..., Optional[str]]:
    """
    Parse string and return handle for os file call.


    The file is assumed to be executable. It is called directly.
    Interpreter MUST be declared at the beginning of the file.


    Parameters
    -----------
        srcstr : str
            os: /absolute/path/to/os_file:func_name:arg1:arg2:...
        util : str
            name object that uses this constructor (used to elaborate debug)

    Returns
    --------
    Callable[..., Optional[str]]
        Handle to callable function

    Raises
    -------
    FileNotFoundError
    ModuleNotFoundError
    ImportError
    """
    osbase, *osargs = srcstr[4:].split(':')

    try:
        osfile = _source_file(osbase)

    except (FileNotFoundError, ModuleNotFoundError, ImportError) as err:
        print(f'Error creating os-callable handle for {util}', mark='err')
        raise err

    def osfunc(*args):
        return process_comm(str(osfile), *osargs, *args, fail_handle='report')

    osfunc.__doc__ = f"""OS command caller: {util}"""

    return osfunc


def build_func_handle(srcstr: str,
                      util: str = 'UNKNOWN') -> Callable[..., Optional[str]]:
    """
    Parse source string to generate a function handle

    Parameters
    -----------
    srcstr : str
        source-string to parse (may begin with py: , os: , sh: )
    util : str
        name object that uses this constructor (used to elaborate debug)

    Returns
    --------
    Callable
    """
    sub_funcs: Dict[str, Callable[..., Optional[str]]] = {
        'py: ': build_py_handle,
        'os: ': build_os_handle,
        'sh: ': build_sh_handle,
        'ch: ': build_ch_handle,
        'default': build_otf_handle
    }
    builder = sub_funcs.get(srcstr[:4], build_otf_handle)
    return builder(srcstr, util)
