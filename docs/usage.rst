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

.. _init:

Initialize
====================

Following actions are performed by `init` sub-command.

- Generate a service (auto-start) entry.
- Create a configuration file as described `here <configure.html>`__.
- Optionally, erase the auto-start / service entry.

Standard init
-----------------

- Set a service to auto-start psprudence on start-up

  - Linux: Systemd

    - Incompatible with :ref:`autostart<linux autostart>`.

  - MacOS: Launchd
  - Windows: nssm

.. tabs::

   .. tab:: direct call

      .. code-block:: shell
         :caption: autostart entry

            psprudence init
         
   .. tab:: module import

      .. code-block:: shell
         :caption: autostart entry

            python -m psprudence init
         

Generate Desktop and Service Files (Linux)
------------------------------------------------

- Create desktop and service files.

.. tabs::

   .. tab:: direct call

      .. code-block:: shell
         :caption: generate files

            psprudence init -g

   .. tab:: module import

      .. code-block:: shell
         :caption: generate files

            python -m psprudence init -g


.. _linux autostart:

Autostart Background (Linux)
----------------------------------

- Create a desktop file and link it for autostart.

  - Use this only if you start your window manager from an empty tty.
  - This is incompatible with systemd service,
    that is `WantedBy` graphical-session.target.

    - If you don't understand, you probably don't want to use this.

.. tabs:: 

   .. tab:: direct call

      .. code-block:: shell
         :caption: autostart entry

            psprudence init -a

   .. tab:: module import

      .. code-block:: shell
         :caption: autostart entry

            python -m psprudence init -a


Deinitialize
--------------

- Remove files, unset services

.. tabs::

   .. tab:: direct call

      .. code-block:: shell
         :caption: unset services and desktop entries

             psprudence init -d

   .. tab:: module import

      .. code-block:: shell
         :caption: unset services and desktop entries

            python -m psprudence init -d

Invoke Manually
=============

*Useful for debugging.*

If service (auto-start) entry is generated, psprudence will start automatically after login.
Manual invocation is rarely needed. Nevertheless, psprudence monitor may be initiated from shell (command-prompt)

.. tabs::

   .. tab:: direct call

      .. code-block:: shell
         :caption: monitor manually

            psprudence

   .. tab:: monitor manually

      .. code-block:: shell
         :caption: monitor manually

            python -m psprudence
