#######
USAGE
#######

**********
SYNOPSIS
**********

.. argparse::
   :ref: psprudence.command_line._cli
   :prog: psprudence

**************
Instructions
**************

User configuration
====================

- Create a configuration file as directed `here <configure.html>`__.

Autostart Background
========================

Create a file and place it at
``${XDG_CONFIG_HOME:-${HOME}/.config}/autostart/psprudence.desktop``

.. code-block:: ini
   :caption: ${XDG_CONFIG_HOME:-${HOME}/.config}/autostart/psprudence.desktop

      [Desktop Entry]
      Encoding=UTF-8
      Type=Application
      Terminal=false
      Name=PSPrudence
      GenericName=System health monitor
      Exec=python3 -m psprudence
      Comment=Monitor peripherals and send signal for prudent action
      StartupNotify=false
      X-GNOME-Autostart-Delay=10
