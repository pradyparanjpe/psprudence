####################
USER-CONFIGURATION
####################

Configuration file is in `yaml <https://yaml.org/spec/>`__
format.

********************************
Location of configuration files
********************************

Configuration may be specified at the following locations:

User (XDG_CONFIG_HOME):
========================

This variable is generally set to ``$HOME/.config`` on unix-like
systems. Even if unset, we will still try the ``$HOME/.config``
directory.

*********************
Configuration format
*********************

Build alerts by defining configuration blocks
Following objects are accepted:

Example:
==========

.. code-block:: yaml
  :caption: ${HOME}/.config/psprudence/config.yml

     # Special case
     global:
       interval: 10  # float: monitor every # seconds
       persist: 5  # float: show alert for # seconds (0 => indefinitely)

     <alert name>:
       alert: <alert string>  # str
       units: <alert value units>  # str
       min_warn: <minimum value to start alerts>  # float
       res_warn: <alert every increment of>  # float
       probe: py: /abs/path/to/pyfile:pyprobe:arg1:arg2...  # returns value
       probe: sh: /abs/path/to/shell_script.sh  # prints value
       probe: |
         <command line 1>
         <command line 2>
         <command line n>  # prints value
       # optional
       panic: <panic callback on actionable values> # format same as probe
       reversed: false <?panic in reverse (decreasing) direction>  # bool
       enabled: true <?this alert is enabled>  # bool
