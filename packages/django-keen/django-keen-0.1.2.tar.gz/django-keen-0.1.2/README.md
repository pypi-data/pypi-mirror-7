===========
django-keen
===========

Simple wrapper around the official keen.io client.::

    #!/usr/bin/env python

    from dkeen import add_event

    add_event("user_subscribed", {"name": user.username})


Installation
=========

    pip install django-keen

Configuration
-------------
put this in your django settings file

    KEEN_PROJECT_ID = ""
    KEEN_WRITE_KEY = ""
    KEEN_READ_KEY = ""
    KEEN_CELERY = False

Note: Calls to keen.io are blocking (you have to wait for a response). If you have a running celery installation, set KEEN_CELERY to True. All calls to add_event or add_events will be called in a task to prevent the blocking.

