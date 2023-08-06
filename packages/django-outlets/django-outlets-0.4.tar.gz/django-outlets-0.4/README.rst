Django Outlets
==============

A reusable Django app that allows you to manage and display your stores.

If you e.g. have different outlets, where you sell your products and those
scattered across the world's surface, you can provide easy access to the
customer about where they can find them.

The app includes simple management of countries and outlets and a google map
integration. For integration into the great ``django-cms``, see `cmsplugin-django-outlets <https://github.com/bitmazk/cmsplugin-django-outlets>`_.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-outlets

    # optional if you want cms integration
    pip install cmsplugin-django-outlets

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-outlets.git#egg=outlets

Add ``outlets`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'outlets',
        # again just if you want cms integration add the following
        'cmsplugin_outlets',
    )

Add the ``outlets`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^outlets/', include('outlets.urls')),
    )

Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate outlets
    # and another optional line. You guessed it. Only if you require it to work
    # in django-cms.
    ./manage.py migrate cmsplugin_outlets

Usage
-----

If you want to use the map, that comes with the default tempalte and you
override the template, keep in mind to to hook up the Google maps API and the
django-outlets ``googlemap_outlets.js`` inside the template if you haven't
added it globally already.

.. code-block:: html

    {% load static %}

    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false&language=en"></script>
    <script type="text/javascript" src="{% static "django_libs/js/maps.js" %}"></script>
    <script type="text/javascript" src="{% static "outlets/js/googlemap_outlets.js" %}"></script>

Check the Google API docs for further information
https://developers.google.com/maps/documentation/javascript/tutorial?hl=de

To be able to display your outlets on the map, every ``Outlet`` needs to have
the ``lat`` and ``lon`` field set properly.

To customize the info boxes, that appear, when you click on the map markers,
you can override the template at ``outlets/outlet_map_marker.html``.

When customizing the ``outlets/outlet_list.html`` template, please note the
comments inside the template.


CMS3 integration
----------------

If you installed and added the ``cmsplugin-django-outlets`` app as described
above, you can go ahead and create a page with the "Outlets Apphook" to it.

That's it.

For more details on apphooks refer to the django-cms v3.x documentation itself.


Template tags
-------------

get_outlet_countries
++++++++++++++++++++

This tag loads all outlet countries from within a template.

Example:

.. code-block:: html

    {% load outlets_tags %}

    {% get_outlet_countries as countries %}

    <p>Visit our outlets in:</p>
    <ul>
        {% for country in countries}
            <li><a href="{{ country.get_absolute_url }}">{{ country.name }}</a></li>
        {% endfor %}
    </ul>



Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-outlets
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
