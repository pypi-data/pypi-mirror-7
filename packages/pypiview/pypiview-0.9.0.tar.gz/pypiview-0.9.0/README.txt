PYPIView
#########

**PYPIView** package provides a simple class to plot the number of downloads of a Pypi package (or several). The download counting is perfomed by the `vanity <https://pypi.python.org/pypi/vanity/2.0.3>`_ package. The plotting is performed with the  `Pandas <http://pandas.pydata.org/>`_ package.

Installation
==============

::

    pip install pypiview

Usage
========

::

    from pypiview import PYPIView
    p = PYPIView("requests")
    p.plot(logy=True)


.. image:: example.png


See the documentation for details.

