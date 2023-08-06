yarg(1) -- A semi hard Cornish cheese, also queries PyPI
========================================================

.. image:: http://img.shields.io/travis/kura/yarg.svg?style=flat

.. image:: http://img.shields.io/coveralls/kura/yarg.svg?style=flat

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


