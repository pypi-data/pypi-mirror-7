.. image:: https://travis-ci.org/ambitioninc/gagrab.png
   :target: https://travis-ci.org/ambitioninc/gagrab

.. image:: https://coveralls.io/repos/ambitioninc/gagrab/badge.png?branch=develop
    :target: https://coveralls.io/r/ambitioninc/gagrab?branch=develop
.. image:: https://pypip.in/v/gagrab/badge.png
    :target: https://crate.io/packages/gagrab/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/gagrab/badge.png
    :target: https://crate.io/packages/gagrab/
    :alt: Number of PyPI downloads


gagrab
===============

The official Google Analytics API is very powerfull and
extensive. Sometimes, though, you just want to grab some data and have
it returned in a clean format.

.. code-block:: python

    from service_account_auth import AuthorizedService
    from gagrab import Grabber

    my_ga_service = AuthorizedService('my-project-555', 'analytics', 'v3')
    grabber = Grabber(my_ga_service)

    data = grabber.query(
        view='UA-000000-1',
        metrics=['sessions', 'pageviews'],
        dimensions=['browser', 'userAgeBracket']
        start_date='2014-07-01',
        end_date='2014-08-15',
    )



Installation
------------
To install the latest release, type::

    pip install gagrab

To install the latest code directly from source, type::

    pip install git+git://github.com/ambitioninc/gagrab.git

The ``gagrab.Grabber`` object requires a
``service_account_auth.AuthorizedService`` object during
initialization. Installation and setup instructions for
gclient-service-account-auth can be found on the github page
`https://github.com/ambitioninc/gclient-service-account-auth`.

Documentation
=============

Full documentation is available at http://gagrab.readthedocs.org

License
=======
MIT License (see LICENSE)
