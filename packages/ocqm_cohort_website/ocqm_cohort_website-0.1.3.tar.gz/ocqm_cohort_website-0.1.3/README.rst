OCQM Cohort Website
===================

A tool to build a static website for OCQM cohorts. Part of our research server that we offer OCQM clients. See http://www.ocqm.org/

Installation
------------

To use locally create a new virtual environment::

    virtualenv -p python3.4

And install the package::

    pip install ocqm_cohort_website

Usage
-----

To see how it looks like just run::

    ocqm-cohort-website demo

And open http://localhost:8000

To create your own site run in an empty folder::

    ocqm-cohort-website init

And start editing the `cohort.yml` file. To see your changes run::

    ocqm-cohort-website build --serve

And have a look at http://localhost:8000 again.

Tests
-----

To run the tests install tox::

    pip install tox

And run it::

    tox

ocqm_cohort_website works with python 2.7 and python 3.3+

Current Build Status
~~~~~~~~~~~~~~~~~~~~
|Build Status|

.. |Build Status| image:: https://secure.travis-ci.org/seantis/ocqm_cohort_website.png
   :target: http://travis-ci.org/seantis/ocqm_cohort_website

Translations
------------

To add a new language::

    python setup.py init_catalog -l <locale>

e.g.::

    python setup.py init_catalog -l it

To update the catalog::

    python setup.py update_catalog

The mo files are automatically compiled at runtime.

License
-------

ocqm_cohort_website is licensed under MIT. See LICENSE file.
