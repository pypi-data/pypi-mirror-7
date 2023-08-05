==========
Groundwork
==========

Groundwork is a small set of a template tags and filters that simplifies
working with Zurb Foundation. Many common django components like paginators,
messages, and forms can be used natively with this package. These components
get wrapped in nice pretty Foundation goodness.

Naming Note
-----------
This package was called Groundwork instead of Foundation to avoid collision
with other packages of that name (or similar). It also symbolizes the simplicity
of the tools this package provides. Like Foundation itself, this package just
provides you with the groundwork needed to make sexy web apps. It is not
intended to be an entire framework or provide programmtic equivalences to all
the foundation components.


Quick Start
-----------
1. Install Groundwork using pip::

    pip install django-groundwork

2. Add "groundwork" to your INSTALLED_APPS like so::

    INSTALLED_APPS = (
        ...
        'groundwork',
    )

3. Include the groundwork URLConf in your project urls.py like so::

    url(r'^goundwork/', include('groundwork.url')),

4. Start your development server and navigate to localhost:8000/groundwork to 
   see an example foundation page.

5. You can remove the URLConf from step 2 when you want, it is not needed to
   use this package, it just provides a new example.

References
----------
Github: https://github.com/dummerbd/django-groundwork

PyPI: https://pypi.python.org/pypi/django-groundwork

This package was inspired by: https://github.com/amarsahinovic/django-zurb-foundation
