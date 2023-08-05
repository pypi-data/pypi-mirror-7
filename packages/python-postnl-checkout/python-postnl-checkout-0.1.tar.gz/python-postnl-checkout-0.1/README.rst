python-postnl-checkout
======================

.. image:: https://secure.travis-ci.org/dokterbob/python-postnl-checkout.png?branch=master
    :target: http://travis-ci.org/dokterbob/python-postnl-checkout

.. image:: https://coveralls.io/repos/dokterbob/python-postnl-checkout/badge.png
    :target: https://coveralls.io/r/dokterbob/python-postnl-checkout

.. image:: https://landscape.io/github/dokterbob/python-postnl-checkout/master/landscape.png
   :target: https://landscape.io/github/dokterbob/python-postnl-checkout/master
   :alt: Code Health

.. image:: https://badge.fury.io/py/python-postnl-checkout.png
    :target: http://badge.fury.io/py/python-postnl-checkout

.. image:: https://pypip.in/d/python-postnl-checkout/badge.png
    :target: https://crate.io/packages/python-postnl-checkout?version=latest

What is it?
------------
PostNL checkout support for Python and Django.

Status
------
Early alpha. Don't use it, unless you're willing to fix issues.

Compatibility
-------------
Tested to work with Django 1.4, 1.5 and 1.6 and Python 2.7.

Requirements
-------------
Please refer to `requirements.txt <http://github.com/dokterbob/python-postnl-checkout/blob/master/requirements.txt>`_ for an updated list of required packages.

Django
------

Installation
************
1. `pip install -e git+https://github.com/dokterbob/python-postnl-checkout.git#egg=python-postnl-checkout`
2. Add `postnl_checkout.contrib.django_postnl_checkout` to `INSTALLED_APPS`.
3. Setup required settings `POSTNL_CHECKOUT_USERNAME`, `POSTNL_CHECKOUT_PASSWORD` and `POSTNL_CHECKOUT_WEBSHOP_ID` settings.

Settings
********

* `POSTNL_CHECKOUT_USERNAME`
* `POSTNL_CHECKOUT_PASSWORD`
* `POSTNL_CHECKOUT_WEBSHOP_ID`
* `POSTNL_CHECKOUT_ENVIRONMENT`
* `POSTNL_CHECKOUT_TIMEOUT`

Tests
==========
Tests for pull req's and the master branch are automatically run through
`Travis CI <http://travis-ci.org/dokterbob/python-postnl-checkout>`_.

License
=======
This application is released
under the GNU Affero General Public License version 3.
