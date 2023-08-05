Introduction
============

django-fs-email-helper is the Django-related reusable app provides the ability to send multipart emails and store them in a database.

The distinctive feature of this app is storing sent emails in database. It means that you have ability to check each sent email from admin interface.


Installation
============

1. Install ``django-fs-email-helper`` using ``pip``::

    $ pip install django-fs-email-helper

2. Add the ``'email_helper'`` application to the ``INSTALLED_APPS`` setting of your Django project ``settings.py`` file::

    INSTALLED_APPS = (
        ...
        'email_helper',
        ...
    )


Usage
=====

Just import ``send_email`` function and use it::

    from email_helper import send_email
    send_email('from_email@example.com', 'to_email@example.com', 'email_helper/email_template.html', {})
    send_email('from_email@example.com', ['to_email_1@example.com', 'to_email_2@example.com'], 'email_helper/email_template.html', {})


Credits
=======

`Fogstream <http://fogstream.ru>`_
