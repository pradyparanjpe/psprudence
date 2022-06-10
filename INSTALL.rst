***************
Prerequisites
***************

- Python3
- pip

********
Install
********

pip
====
Preferred method

Install
--------

.. tabbed:: pip

   .. code-block:: sh
      :caption: install

      pip install --index-url "https://www.gitlab.com/api/v4/projects/35710384/packages/pypi/simple" psprudence



.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip install --index-url "https://www.gitlab.com/api/v4/projects/35710384/packages/pypi/simple" psprudence

Update
-------

.. tabbed:: pip

   .. code-block:: sh
      :caption: install

      pip install -U --index-url "https://www.gitlab.com/api/v4/projects/35710384/packages/pypi/simple" psprudence


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip install --index-url "https://www.gitlab.com/api/v4/projects/35710384/packages/pypi/simple" psprudence


Uninstall
----------

.. tabbed:: pip

   .. code-block:: sh
      :caption: uninstall

      pip uninstall psprudence


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip uninstall psprudence

Initialize
======================

Set Service
-----------------

- Set a service to autostart psprudence on start-up
  - Linux: Systemd
    - Incompatible with :ref:`Autostart Background (Linux)<autostart>`.
  - MacOS: Launchd
  - Windows: nssm

.. tabbed:: direct call

   .. code-block:: shell
      :caption: autostart entry

         psprudence init

.. tabbed:: module import

   .. code-block:: shell
      :caption: autostart entry

         python -m psprudence init


Generate Desktop and Service Files (Linux)
---------------------------------------------

- Create desktop and service files.

.. tabbed:: direct call

   .. code-block:: shell
      :caption: generate files

         psprudence init -g

.. tabbed:: module import

   .. code-block:: shell
      :caption: generate files

         python -m psprudence init -g


Autostart Background (Linux)
----------------------------------

- Create a desktop file and link it for autostart.
  - Use this only if you start your window manager from an empty tty.
  - This is incompatible with systemd service, that is `WantedBy` graphical.target.
    - If you don't understand, you probably don't want to use this.

.. tabbed:: direct call

   .. code-block:: shell
      :caption: autostart entry

         psprudence init -a

.. tabbed:: module import

   .. code-block:: shell
      :caption: autostart entry

         python -m psprudence init -a


Deinitialize
--------------

- Remove files, unset services

.. tabbed:: direct call

   .. code-block:: shell
      :caption: unset services and desktop entries

          psprudence init -d

.. tabbed:: module import

   .. code-block:: shell
      :caption: unset services and desktop entries

         python -m psprudence init -d
