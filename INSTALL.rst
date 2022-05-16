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




`pspman <https://gitlab.com/pradyparanjpe/pspman>`__
=====================================================

(Linux only)

For automated management: updates, etc


Install
--------

.. code-block:: sh

   pspman -s -i https://gitlab.com/pradyparanjpe/psprudence.git



Update
-------

.. code-block:: sh

    pspman


*That's all.*


Uninstall
----------

Remove installation:

.. code-block:: sh

    pspman -s -d psprudence
