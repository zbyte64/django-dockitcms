.. image:: https://secure.travis-ci.org/zbyte64/django-dockitcms.png?branch=master
   :target: http://travis-ci.org/zbyte64/django-dockitcms

Introduction
============

CMS written using django-dockit.

Demo Site: http://dockitcmsdemo.herokuapp.com/
Demo Site Code: https://github.com/zbyte64/dockitcmsdemo

--------
Features
--------

* Document based CMS
* Create collections, indexes, and views in an admin or API
* Integrates with hyperadmin
* Configurable plugins (mixins)


Installation
============

------------
Requirements
------------

* Python 2.6 or later
* Django 1.3 or later
* django-dockit: https://github.com/webcube/django-dockit
* django-hyperadmin: https://github.com/webcube/django-hyperadmin
* django-hyperadmin-dockitresource: https://github.com/webcube/django-hyperadmin-dockitresource
* django-hyperadmin-client: https://github.com/webcube/django-hyperadmin-client


--------
Settings
--------

Put 'dockitcms' and 'dockitcms.widgetblock' into your ``INSTALLED_APPS`` section of your settings file.

Add the following middleware: 'dockitcms.middleware.DefaultScopeMiddleware'

Set the following in your settings file::

    SCOPE_PROCESSORS = [
        'dockitcms.widgetblock.scope_processors.widgets',
        'dockitcms.widgetblock.scope_processors.modelwidgets',
    ]

