=====================
Django Request Logger
=====================

What is it?
===========

This Django app adds extra fields to log records emitted
by the standard Python logging. Currently these include:

* username - Username of the currently logged in Django user, if any. If no
  user is logged in the value is "_" (distinct from empty string, which means
  that the information is not available).
* client_ip - IP address of the client browser, obtained from REMOTE_ADDR and
  HTTP_X_FORWARDED_FOR.
* absolute_url - the absolute URL of the current request, including the query
  string.
* raw_post_data - the raw POST data for the current request, if any.

These fields are then available to be used in your logging formatter (see
example below). They are also visible in Django Sentry as additional data (if
you have Django Sentry installed).


How do I use it?
================

1. Install the package in the usual way ("setup.py install" or "pip install")
2. Add 'django_request_logger' to your INSTALLED_APPS
3. Add 'django_request_logger.middleware.StoreRequestMiddleware' to your
   MIDDLEWARE_CLASSES
4. Change your logging formatter to include one or more of the above fields
   (see example).


How does it work?
=================

When the package is imported it configures a logging Filter, which modifies
every LogRecord to add the above fields. This filter is automatically added to
every logging Handler that was configured in the settings.LOGGING dictionary.
It gets the Django HttpRequest object from a thread-local variable, which is
stored on every request by the middleware class (StoreRequestMiddleware).


Sample configuration
====================

In settings.py::

    MIDDLEWARE_CLASSES = (
        ...
        'django_request_logger.middleware.StoreRequestMiddleware',
    )

    INSTALLED_APPS = (
        ...
        'django_request_logger',
    )

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                # Include the Django username and client IP for every message
                'format': '[%(levelname)-8s %(asctime)s] {%(username)s} {%(client_ip)s} %(name)s: %(message)s',
            },
        },
        'handlers': {
            # Include the default Django email handler for errors
            # This is what you'd get without configuring logging at all.
            'mail_admins': {
                'class': 'django.utils.log.AdminEmailHandler',
                'level': 'ERROR',
                'include_html': True,
            },
            # Log to a text file that can be rotated by logrotate
            'logfile': {
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'default',
                'filename': '/var/log/django/myapp.log'
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django': {
                'handlers': ['logfile'],
                'level': 'ERROR',
                'propagate': False,
            },
            'myapp': {
                'handlers': ['logfile'],
                'level': 'DEBUG',
                'propogate': False
            },
        },
    }