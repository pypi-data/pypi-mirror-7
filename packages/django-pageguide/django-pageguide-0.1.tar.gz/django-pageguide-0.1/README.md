django-pageguide
================

Django integration with [pageguide](https://github.com/tracelytics/pageguide), an interactive guide for web page elements

Installation
============

Put the `pageguide` app In your `settings.py`:
----------------------------------------------

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',

        #.....................#

        'pageguide',
    )


Run the migrations:
-------------------

    >>> python manage.py syncdb --migrate


Create the pages into the admin interface
-----------------------------------------

Go to `/admin/pageguide/`


Integrate in your base template:
--------------------------------

* Into the top page:

    {% load pageguide_tags %}

    {% pageguide_css %}

* Into the bottom (near the `</body>` tag):

    {% pageguide %}

    {% pageguide_js %}


Development
===========

You can get the last bleeding edge version of django-pageguide by doing a clone
of its git repository

  git clone https://github.com/msaelices/django-pageguide.git
