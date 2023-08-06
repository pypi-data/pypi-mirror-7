===========
pytest-mock
===========

This plugin installs a ``mock`` fixture which is a thin-wrapper around the patching API 
provided by the excellent `mock <http://pypi.python.org/pypi/mock>`_ package,
but with the benefit of not having to worry about undoing patches at the end
of a test:

.. code-block:: python


    def test_unix_fs(mock):
        mock.patch('os.remove')
        UnixFS.rm('file')
        os.remove.assert_called_once_with('file')

|version| |downloads| |ci| |coverage|

.. |version| image:: http://img.shields.io/pypi/v/pytest-mock.png
  :target: https://crate.io/packages/pytest-mock

.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-mock.png
  :target: https://crate.io/packages/pytest-mock

.. |ci| image:: http://img.shields.io/travis/nicoddemus/pytest-mock.png
  :target: https://travis-ci.org/nicoddemus/pytest-mock

.. |coverage| image:: http://img.shields.io/coveralls/nicoddemus/pytest-mock.png
  :target: https://coveralls.io/r/nicoddemus/pytest-mock


Usage
=====

The ``mock`` fixture has the same API as 
`mock.patch <http://www.voidspace.org.uk/python/mock/patch.html#patch-decorators>`_, 
supporting the same arguments:

.. code-block:: python

    def test_foo(mock):
        # all valid calls
        mock.patch('os.remove')
        mock.patch.object(os, 'listdir', autospec=True)
        mocked = mock.patch('os.path.isfile')

The supported methods are:

* ``mock.patch``: see http://www.voidspace.org.uk/python/mock/patch.html#patch.
* ``mock.patch.object``: see http://www.voidspace.org.uk/python/mock/patch.html#patch-object.
* ``mock.patch.multiple``: see http://www.voidspace.org.uk/python/mock/patch.html#patch-multiple.
* ``mock.patch.dict``: see http://www.voidspace.org.uk/python/mock/patch.html#patch-dict.
* ``mock.stopall()``: stops all active patches at this point.


Requirements
============

* Python 2.6+, Python 3.2+
* pytest
* mock (for Python < 3.3)


Install
=======

Install using `pip <http://pip-installer.org/>`_:

.. code-block:: console

    $ pip install pytest-mock


Why bother with a plugin?
=========================

There are a number of different ``patch`` usages in the standard ``mock`` API, 
but IMHO they don't scale very well when you have a more than one or two 
patches to apply.

It may lead to an excessive nesting of ``with`` statements, breaking the flow
of the test:

.. code-block:: python

    import mock

    def test_unix_fs():
        with mock.patch('os.remove'):
            UnixFS.rm('file')
            os.remove.assert_called_once_with('file')

            with mock.patch('os.listdir'):
                assert UnixFS.ls('dir') == expected
                # ...

        with mock.patch('shutil.copy'):
            UnixFS.cp('src', 'dst')
            # ...


One can use ``patch`` as a decorator to improve the flow of the test:

.. code-block:: python

    @mock.patch('os.remove')
    @mock.patch('os.listdir')
    @mock.patch('shutil.copy')
    def test_unix_fs(mocked_copy, mocked_listdir, mocked_remove):
        UnixFS.rm('file')
        os.remove.assert_called_once_with('file')

        assert UnixFS.ls('dir') == expected
        # ...

        UnixFS.cp('src', 'dst')
        # ...

But this poses a few disadvantages:        

- test functions must receive the mock objects as parameter, even if you don't plan to 
  access them directly; also, order depends on the order of the decorated ``patch`` 
  functions;
- receiving the mocks as parameters doesn't mix nicely with pytest's approach of
  naming fixtures as parameters, or ``pytest.mark.parametrize``;
- you can't easily undo the mocking during the test execution;


