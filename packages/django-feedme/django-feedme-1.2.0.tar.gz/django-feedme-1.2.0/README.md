Django Feed Me
==============

[![Build Status](https://travis-ci.org/dstegelman/django-feedme.png?branch=master)](https://travis-ci.org/dstegelman/django-feedme)
[![Pypi Version](https://pypip.in/v/django-feedme/badge.png)](https://crate.io/packages/django-feedme/)


Django Feed Me is a replacement for Google Reader.  It keeps track of your feeds, fetches the RSS feeds
and parses them in an easy to read interface.  This is currently in development.  The app works as POC using the Django
Admin.  A separate interface for adding feeds is coming down in the pipeline.

![image](http://cl.ly/image/0j2z0y0K1e2e/Screen%20Shot%202013-04-27%20at%209.54.10%20AM.png)

Installation
------------

To install FeedMe simply:

    pip install django-feedme

Add ``feedme`` to your installed apps.  Add route a url to ``feedme.urls``

Make sure to syncdb or migrate the app:

    python manage.py syncdb
    python manage.py migrate


If you want to use Celery for fetching (Recommended) then add:

    FEED_UPDATE_CELERY = True

to your settings file.  Make sure you've installed and configured Celery properly.  The syntax used should be good
for both Celery 2 and 3.

This app bundles static and works out of the box with django static files.  If you aren't collecting static
you'll need to copy the static directory to where ever you serve static from.

You need to provide a login view that Feedme can use to provide a login link when the user isn't logged in.  This is
referenced as ``auth_login`` by name.

    url(r'^something/$', your.login.view, name='auth_login')

You will also need to provide a LOGIN_URL as well.

Dependencies
------------

As of FeedMe 1.0 feedme requires Django 1.5 and above.

Feedme also requires the use of the django-bootstrap-static library for some static files.  It is bundled in setup.py so by installing this package
it should already be downloaded to your machine.  In order to have the bootstrap files picked up by your static files hanlder, you'll need to add
```bootstrap``` to installed apps.  This will alow Django's static files to pick up the boostrap files.


Celery Beat
-----------

To make use of the Celery beat schedule to automatically update feeds at given intervals, open your settings file and
enter something like the following:

    import datetime


    CELERYBEAT_SCHEDULE = {
        "feed-updates": {
            "task": "update_all_feeds",
            "schedule": datetime.timedelta(hours=1),
            },
        }

More documentation for Celery can be found at the CeleryProject.

Feedme Digest
-------------

You can enable the daily email digest of new feed items by setting up the from email setting
and enabling the Celery Beat task.::


    FEEDME_FROM_EMAIL = 'test@email.com'


and add the Task::

    import datetime


    CELERYBEAT_SCHEDULE = {
        "feedme-digest": {
        "task": "send_digest",
        "schedule": crontab(minute=0, hour=0),
            },
        }


Contributions
-------------

Please place all bug reports in Github Issues.  Pull requests are welcome and encouraged!!


Documentation
-------------

This document and more formal documentation at http://django-feedme.readthedocs.org/en/latest/


Additional Planned Features
---------------------------

* Add and manage feeds from the front end (rather than Django Admin)
* Look and Feel updates
* Tests

Questions/Comments/Hate Mail?
-----------------------------

Drop an issue in Github and I'll be sure to find it.
