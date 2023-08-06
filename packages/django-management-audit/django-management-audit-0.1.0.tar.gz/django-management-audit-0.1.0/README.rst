=============================
django-management-audit
=============================

.. image:: https://badge.fury.io/py/django-management-audit.png
    :target: https://badge.fury.io/py/django-management-audit

.. image:: https://travis-ci.org/hiisi13/django-management-audit.png?branch=master
    :target: https://travis-ci.org/hiisi13/django-management-audit

.. image:: https://coveralls.io/repos/hiisi13/django-management-audit/badge.png?branch=master
    :target: https://coveralls.io/r/hiisi13/django-management-audit?branch=master

Audit your app's management command calls with a single line of code. Logs command name and start/end timestamps on every run.


Quickstart
----------

* Install django-south-central::

    pip install django-management-audit

* Create database table for audit records::

    python manage.py syncdb

Usage
--------

* Modify your manage.py file to import audit installer and run it::

    from management_audit import install

    install(['your_app_name',])
    
* Optionally supply exclusion list of commands that you don't want to audit::

    install(['your_app_name',], ['command_to_ignore',])
    
* When commands from your apps will be run, **django-management-audit** will create a database record for each run which includes command's name and start/end timestamps.

TODO
--------

* Log command parameters in addition to name and timestamps.

* Create admin UI to browse audit records.

* Add inclusion list as opposite to exlusion list (verify if that's a use case at all)
