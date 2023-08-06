xlwings - Make Excel Fly!
=========================

xlwings is a `BSD-licensed <http://opensource.org/licenses/BSD-3-Clause>`_ Python library that makes it easy to call
Python from Excel and vice versa:

* Interact with Excel from Python using a syntax that is close to VBA yet Pythonic.
* Replace your VBA macros with Python code and still pass around your workbooks as easy as before.

xlwings fully supports NumPy arrays and Pandas DataFrames. Currently, it only works on Windows.

.. note:: xlwings is currently in an early stage.
   The API might change in backward incompatible ways.


Interact with Excel from Python
-------------------------------

Writing some values to Excel and adding a chart is as easy as:

.. code-block:: python

    >>> from xlwings import Workbook, Range, Chart
    >>> wb = Workbook()  # Creates a connection with a new workbook
    >>> Range('A1').value = ['Foo 1', 'Foo 2', 'Foo 3', 'Foo 4']
    >>> Range('A2').value = [10, 20, 30, 40]
    >>> Range('A1').table.value  # Read the whole table back
    [[u'Foo 1', u'Foo 2', u'Foo 3', u'Foo 4'], [10.0, 20.0, 30.0, 40.0]]
    >>> chart = Chart().add()
    >>> chart.set_source_data(Range('A1').table)


Call Python from Excel
----------------------

If, for example, you want to fill your spreadsheet with standard normally distributed random numbers, your VBA code is
just one line:

.. code-block:: vb.net

    Sub RandomNumbers()
        RunPython ("import mymodule; mymodule.rand_numbers()")
    End Sub

This essentially hands over control to ``mymodule.py``:

.. code-block:: python

    import numpy as np
    from xlwings import Workbook, Range

    wb = Workbook()  # Creates a reference to the calling Excel file

    def rand_numbers():
        """ produces standard normally distributed random numbers with shape (n,n)"""
        n = Range('Sheet1', 'B1').value
        rand_num = np.random.randn(n, n)
        Range('Sheet1', 'C3').value = rand_num


To make this run, just import de VBA module ``xlwings.bas`` in the VBA editor. It can be found in the directory of
your ``xlwings`` installation.

Easy deployment
---------------

Deployment is really the part where xlwings shines:

* Just zip-up your Spreadsheet with your Python code and the ``xlwings.py`` file and send it around. The receiver only
  needs to have an installation of Python with `pywin32 <http://sourceforge.net/projects/pywin32/>`_ (and obviously
  all the other packages you're using).
* There is no need to install any Excel add-in.
* If this still sounds too complicated, just freeze your Python code into an executable and use
  ``RunFrozenPython`` instead of ``RunPython``. This gives you a standalone version of your Spreadsheet tool without any
  dependencies.


Installation
------------

The easiest way to install xlwings is via pip::

    pip install xlwings


Alternatively it can be installed from source. From within the ``xlwings`` directory, execute::

    python setup.py install


Links
-----

* Homepage: http://xlwings.org
* Documentation: http://docs.xlwings.org
* Source Code: http://github.com/zoomeranalytics/xlwings


