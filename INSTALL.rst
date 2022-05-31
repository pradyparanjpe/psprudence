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

Initialize (Linux)
======================

Desktop Entry
-----------------

- Create a desktop entry.

.. tabbed:: direct call

   .. code-block:: shell
      :caption: desktop entry

         psprudence init

.. tabbed:: module import

   .. code-block:: shell
      :caption: desktop entry

         python -m psprudence init


Autostart Background
-----------------------

- Create an autostart link.

.. tabbed:: direct call

   .. code-block:: shell
      :caption: autostart entry

         psprudence init -a

.. tabbed:: module import

   .. code-block:: shell
      :caption: autostart entry

         python -m psprudence init -a

Remove desktop entries
-------------------------

- Create an autostart link.

.. tabbed:: direct call

   .. code-block:: shell
      :caption: delete entries

          psprudence init -d

.. tabbed:: module import

   .. code-block:: shell
      :caption: delete entries

         python -m psprudence init -d
