yarg(1) -- A semi hard Cornish cheese, also queries PyPI
========================================================

.. image:: https://img.shields.io/travis/kura/yarg.svg?style=flat

.. image:: https://img.shields.io/coveralls/kura/yarg.svg?style=flat

.. image:: https://pypip.in/version/yarg/badge.svg?style=flat

.. image:: https://pypip.in/download/yarg/badge.svg?style=flat

.. image:: https://pypip.in/py_versions/yarg/badge.svg?style=flat

.. image:: https://pypip.in/implementation/yarg/badge.svg?style=flat

.. image:: https://pypip.in/status/yarg/badge.svg?style=flat

.. image:: https://pypip.in/wheel/yarg/badge.svg?style=flat

.. image:: https://pypip.in/license/yarg/badge.svg?style=flat

Yarg is a PyPI client.

.. code-block:: python

    >>> import yarg
    >>> package = yarg.get("yarg")
    >>> package.name
    u'yarg'
    >>> package.author
    Author(name=u'Kura', email=u'kura@kura.io')

Full documentation is at <https://yarg.readthedocs.org>.


Release History
===============

0.1.2 (2014-08-08)
------------------

Bug fixes
~~~~~~~~~

- `yarg.get` will now raise an Exception for errors **including**
  300 and above. Previously on raised for above 300.
- Fix an issue on Python 3.X and PyPy3 where `HTTPError` was using
  a method that was removed in Python 3.
- Added dictionary key lookups for **home_page**, **bugtrack_url**
  and **docs_url**. Causes KeyError exceptions if they were not
  returned by PyPI.

Other
~~~~~

- More test coverage.

0.1.1 (2014-08-08)
------------------

API changes
~~~~~~~~~~~

- New `Package` property `has_wheel`.
- New `Package` property `has_egg`.
- New `Package` property `has_source`.
- New `Package` property `python_versions`.
- New `Package` property `python_implementations`.
- Added `HTTPError` to `yarg.__init__` for easier access.
- Added `json2package` to `yarg.__init__` to expose it for use.

0.1.0 (2014-08-08)
------------------

- Initial release


