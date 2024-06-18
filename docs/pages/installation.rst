Installation
============

PyPI (stable) version
---------------------

Mcproto is available on `PyPI <https://pypi.org/project/mcproto/>`_, and can be installed trivially with:

.. code-block:: bash

    python3 -m pip install mcproto

This will install the latest stable (released) version. This is generally what you'll want to do.

Latest (git) version
--------------------

Alternatively, you may want to install the latest available version, which is what you currently see in the ``main``
git branch. Although this method will actually work for any branch with a pretty straightforward change. This kind of
installation should only be done when testing new features, and it's likely you'll encounter bugs.

That said, since mcproto is still in development, changes can often be made pretty quickly, and it can sometimes take a
while for these changes to carry over to PyPI. So if you really want to try out that latest feature, this is the method
you'll want.

.. code-block:: bash

    python3 -m pip install 'mcproto@git+https://github.com/py-mine/mcproto@main'
