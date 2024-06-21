####################
USER-CONFIGURATION
####################

Configuration file is in `yaml <https://yaml.org/spec/>`__
format.

********************************
Location of configuration files
********************************

A template configuration file is `generated <usage.html#initialize>`__ during `init` call.

Configuration may be specified at standard XDG locations:

User (XDG_CONFIG_HOME):
========================

This variable is generally set to ``$HOME/.config`` on unix-like
systems. Even if unset, we will still try the ``$HOME/.config``
directory.

*********************
Configuration format
*********************

Default (shipped) alerts are inherited. They may be disabled by setting ``enabled: false``.

Build alerts by defining configuration blocks.

Example:
==========

.. code-block:: yaml
  :caption: config.yml

     # Special case
     global:
       interval: 10  # float: monitor every # seconds
       persist: 5  # float: show alert for # seconds (0 => indefinitely)

     # disable shipped
     load15:
       enabled: false

     # new alert definition
     <alert name>:
       alert: <alert string>  # str
       min_warn: <minimum value to start alerts>  # float
       probe: py: /path/to/pyfile:pyprobe:arg1:arg2...  # returns value
       probe: os: /path/to/command  # prints value
       probe: sh: /path/to/sh_script.sh:shprobe:arg1:...  # prints value
       probe: |
         <command line 1>
         <command line 2>
         <command line n>  # prints value

       # optional
       units: '' <alert value units>  # str
       warn_res: 1. <next alert threshold increment>  # float
       reversed: false <?panic in reverse (decreasing) direction>  # bool
       enabled: true <?this alert is enabled>  # bool (default: true)
       alert_check: <callback checks if value is alarming>  # format same as probe, function's first argument shall be 'self'
       panic: <panic callback on actionable values> # format same as probe
       attempt_reset: <callback to reset alert threshold>  # format same as probe

.. note::
   If supplied {path} is not absolute, then, following prefix locations will be checked in order:
      - ``${XDG_DATA_HOME:-${HOME}/.local/share}/psprudence/{path}``
      - ``/usr/share/psprudence/{path}``
      - {shipped project root}/{path},

   The earliest found definition is loaded.

.. tip::
   Default alert definitions may be overridden by creating same function-names at more dominant prefixes:
      - ``${XDG_DATA_HOME:-${HOME}/.local/share}/psprudence``
      - ``/usr/share/psprudence``

   In files:
      - ``battery.py``
      - ``sensors.py``


.. todo::
   ``sh:`` and in-line declaration format are supported only for POSIX (Linux and MacOS)

   - future plan, ``ch:`` format for Windows batch scripts
   - future plan, in-line format for Windows
