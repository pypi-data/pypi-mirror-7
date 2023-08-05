======================
django-quiet-runserver
======================

A quieter version of the default Django ``runserver``.

The default ``runserver`` prints out a *lot* of information,
and not all of it is useful.
This packages removes most of the information printed,
leaving only the important stuff:

- Requests to some static assets are not logged
- ``304 Not Modified`` requests are not logged
- Timestamps are no longer included. Most of the time, these are noise
- The common response types ``GET`` and ``POST``
  are abbreviated to ``G`` and ``P``
- ``GET`` query strings are logged on a separate, slightly indented line,
  allowing for easy differentiation.


Example::

    200 G /
    200 G /static/styles.css
    200 G /search/
      ?q=foo&sort=date
    200 G /item/123/
    301 P /item/123/
    200 G /item/123/

Installing
----------

Install this package::

    pip install djangoquietrunserver

Include it in your ``INSTALLED_APPS``::

    INSTALLED_APPS += (
        'djangoquietrunserver',
    )

Using
-----

Use ``runserver--`` instead of ``runserver``::

    python manage.py runserver--

Monkey patching
~~~~~~~~~~~~~~~

If you do not want to use ``runserver--``, you can monkey patch Django so that
the default ``runserver`` will use the quieter logging by adding the following
lines to your ``manage.py``, just after the ``import sys`` line::

    import djangoquietrunserver.monkeypatch
    djangoquietrunserver.monkeypatch()
