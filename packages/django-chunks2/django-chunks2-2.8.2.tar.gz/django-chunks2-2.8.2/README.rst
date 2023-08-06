Django-Chunks2
==============

Installation:
-------------

1. Install using pip

.. code-block:: bash

    $ pip install django-chunks2

2. Add the ``chunks`` application to ``INSTALLED_APPS`` in your settings file (usually ``settings.py``)
3. Sync database (``./manage.py syncdb`` or ``./manage.py migrate``)
4. Use chunks on your templates

.. code-block:: html

    {% load chunks %}

    <html>
      <head>
        <title>Test</title>
      </head>
      <body>
        <h1>Blah blah blah</h1>
        <div id="sidebar">
            ...
        </div>
        <div id="left">
            {% chunk "home_page_left" %}
        </div>
        <div id="right">
            {% chunk "home_page_right" %}
        </div>
      </body>
    </html>
