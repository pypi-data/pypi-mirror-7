Django APSara Process Module
============================

.. image:: https://travis-ci.org/bitmazk/django-aps-process.png?branch=master   
   :target: https://travis-ci.org/bitmazk/django-aps-process

.. image:: https://coveralls.io/repos/bitmazk/django-aps-process/badge.png 
   :target: https://coveralls.io/r/bitmazk/django-aps-process

The Process module for django-apsara.

Installation
------------

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-aps-process.git#egg=aps_process

Add ``aps_process`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'aps_process',
    )

Add the ``aps_process`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^aps-process/', include('aps_process.urls')),
    )

Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate aps_process


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-aps-process
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    fab test  # Run the tests and check coverage
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
