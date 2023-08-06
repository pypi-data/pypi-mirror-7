|travis| |coveralls| |pypi| |downloads|

Django Freshdesk
================

Single Sign-On functionallity between Django and Freshdesk.

The Freshdesk documentation for Single Sign-On is located at

https://support.freshdesk.com/support/articles/31166-single-sign-on-remote-authentication-in


How to use
==========

Get the code
------------

Getting the code for the latest stable release using pip: ::

   $ pip install django-freshdesk

You can also download the source and run: ::

      $ python setup.py install

Add the application to the project settings
-------------------------------------------

Make sure that .django.contrib.auth' is installed and then add register 'freshdesk'
in the 'INSTALLED_APPS' section of your project's settings. ::

    INSTALLED_APPS = (
        ...
        'django.contrib.auth',
        'freshdesk',
    )


Setup the settings variables
----------------------------

You must specify two settings variables in your settings module.

* The URL of your support page, will either a subdomain in freshdesk.com or your own domain (using a CNAME record)::

    FRESHDESK_URL = 'http://yourcompany.freshdesk.com/'

* The shared secret you get from Freshdesk when setting up Simple SSO::

    FRESHDESK_SECRET_KEY = '098f6bcd4621d373cade4e832627b4f6'


Register the urls
----------------_

Add the application urls to your urlconf::

    urlpatterns = patterns('',
        ...
        url(r'^login/sso/', include('freshdesk.urls')),
    )


Requirements
============

* Python 2.7, 3.2, 3.3 or 3.4
* Django >= 1.5


Bugs and requests
=================

If you have found a bug or or you have a ny request, please use the issue tracker on GitHub.

https://github.com/ThatGreenSpace/django-freshdesk/issues


License
=======

You can use this under BSD. See `LICENSE
<LICENSE>`_ file for details.


.. |travis| image:: https://secure.travis-ci.org/ThatGreenSpace/django-freshdesk.png?branch=master
    :target: https://travis-ci.org/ThatGreenSpace/django-freshdesk
.. |coveralls| image:: https://coveralls.io/repos/ThatGreenSpace/django-freshdesk/badge.png?branch=master
    :target: https://coveralls.io/r/ThatGreenSpace/django-freshdesk?branch=master
.. |pypi| image:: https://badge.fury.io/py/django-freshdesk.png
    :target: http://badge.fury.io/py/django-freshdesk
.. |downloads| image:: https://pypip.in/d/django-freshdesk/badge.png
    :target: https://crate.io/packages/django-freshdesk?version=latest




History
=======

0.1.0
-----

* Initial application


