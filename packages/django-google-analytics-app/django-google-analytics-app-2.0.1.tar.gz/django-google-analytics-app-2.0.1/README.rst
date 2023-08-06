Django Google Analytics
=======================
**Django Google Analytics brings the power of server side/non-js Google Analytics to your Django projects**

.. contents:: Contents
    :depth: 3

Installation
------------

#. Install or add ``django-google-analytics`` to your Python path.
#. Add ``google_analytics`` to you ``INSTALLED_APPS`` setting.
#. Add URL include to your project's ``urls.py`` file::

    (r'^djga/', include('google_analytics.urls')),

#. Specify a Google Analytics `tracking code <https://support.google.com/analytics/bin/answer.py?hl=en&answer=1008080>`_, i.e.::

    GOOGLE_ANALYTICS = {
        'google_analytics_id': 'xxx',
    }

   where ``xxx`` is your tracking code.

#. If you intend tracking through middleware and Celery remember to `install Celery and run its worker process <http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>`_.

Usage
-----

There are two ways to add tracking to your pages.

1. HTML tag
***********

Using ``<img/>`` and sticking it in your ``base.html``::

    {% load google_analytics_tags %}
    <div style="display:none">
        <img src="{% google_analytics %}" width="0" height="0" />
    </div>

2. Middleware + Celery
**********************

Using Django's middleware, you can process every request and use Celery to make the request to Google Analytics::

    MIDDLEWARE_CLASSES = (
        'google_analytics.middleware.GoogleAnalyticsMiddleware',
    )

You have to add ``google_analytics`` to your ``CELERY_IMPORTS``::

    CELERY_IMPORTS = ('google_analytics.tasks')

You can also specify paths that will be excluded when tracking::

    GOOGLE_ANALYTICS_IGNORE_PATH = ['/health/', ]

