=======
canclón
=======

Template name resolution for Django class-based views

------------
Introduction
------------

*Canclón* is a local name for the horned screamer, `Anhima cornuta`_. This is a group of `class-based views`_ for Django_. The simple flexibility and DRYness_ of this group of classes is comparable to that of horned screamer's horn_.

.. _`Anhima cornuta`: https://en.wikipedia.org/wiki/Horned_screamer
.. _`class-based views`: https://docs.djangoproject.com/en/dev/topics/class-based-views/
.. _Django: http://djangoproject.com/
.. _DRYness: http://en.wikipedia.org/wiki/Don't_repeat_yourself
.. _horn: https://www.youtube.com/watch?v=1esf6WNdvso

Django's default method for template name resolution has a couple of not-so-niceties for more advanced developers, such as default template suffixes appended with an underscore (yay for dashes) and an assumption of HTML files (you might want to include other extension, such as ``.jade``). This project gives you the flexibility of having everybody need to stick to a set of standards, or as well phase slowly into a standard by permitting more template names to be selected.

Warning:

    Including this functionality in your project makes template name resolution DRYier and more flexible but a bit slower.

---------------
Getting started
---------------

You first need pip_ installed. Also, you might want a virtualenv_ (which will usually give you a scoped pip, too).

.. _pip: https://pypi.python.org/pypi/pip
.. _virtualenv: http://virtualenv.readthedocs.org/en/latest/

Use the command::

To install the latest official release, use::

    pip install django-canclon

To install the latest version, use::

    pip install git+git://github.com/jleeothon/canclon.git

Voilà, instalation finished.

-------
Options
-------

``template_flags`` are variable names that are set to ``True`` for your template. **More insight into the usefulness of this, later**.

``template_suffixes`` are usually actions associated with the model for which the template will serve, e.g. `list`, `edit`, ``confirm-delete``.

``template_suffix_joints`` is the separators between a model and a suffix. The default is a singleton (a 1-tuple) with a dash (``tuple('-')``).

``template_extensions`` is the list of file extensions to look for, the default is a singleton of `'html'`. You can include other formats such as ``.jade``.

Based on suffixes, suffix joints and extensions, a list of all posible combinations is returned. They take the form ``1/234.5``, where:

- 1 is the app label
- 2 is the model name
- 3 is separator (joint)
- 4 is the suffix
- 5 is the file extension

When a suffix is a null string, the separator and suffix are omitted.

---------------
Troubleshooting
---------------

If you stumble upon any crash or bug:

1. don't use my software ☆⌒(＞。≪)
2. file a bug in the "issues" section （〃・ω・〃）

---------------------
Enhancement proposals
---------------------

If Django could receive a lazy object for ``get_template_names`` instead of a pre-evaluated iterable, this implementation would be both more time-efficient and space-efficient.
