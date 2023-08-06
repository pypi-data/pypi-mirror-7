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

Canclón's ``TemplateNameResolverMixin`` allows you to calculate the template name for a class-based view using:

- The class-based view's ``model`` name, automatically calculated.
- A list of suffixes, e.g. your Create view could be "product-create.html", "product-edit.html" or "product-form.html".
- A list of separators, i.e. take "product-create.html" or "product_create.html".
- A list of extensions, i.e. "html", "jade".

Warning:

    You will override Django's template name resolution method.

---------------
Installation
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

-----
Usage
-----

Extend ``canclon.TemplateNameResolverMixin`` to your class to enable functionality.

Override the class' ``template_suffixes``, ``template_suffix_separators`` and ``template_extensions``::

    class ProductCreateView(TemplateNameResolverMixin, CreateView):
        template_suffixes = ('create', 'editing', 'form')
        template_suffix_separators = ('-', '_')
        template_extensions = ('html', 'jade')

The default separator is a dash (``'-'``) and de default extension is ``html``.

You can also set the default separators and extensions in your ``settings.py``::

    # settings.py

    template_suffix_separators = ('-*-',) # feeling fancy in this project
    template_extensions = ('jade',)

..

    **Warning!** Not overriding template_suffixes will result in no template name candidates being produced.


Based on suffixes, suffix joints and extensions, a list of all posible combinations is returned. They take the form ``1/234.5``, where:

- 1 is the app label
- 2 is the model name
- 3 is separator (joint)
- 4 is the suffix
- 5 is the file extension

When a suffix is an empty string, the separator and suffix are omitted.

---------------
Recommendations
---------------

For any new category of class-based views, e.g. a "Search" view, create a custom inheritable class to avoid repeating the suffix and separator everywhere. As such, TemplateNameResolverMixin will be your class' "grandparent".

For single custom class-based views, inherit direct from TemplateNameResolverMixin.

Don't use too many suffixes, extensions or separators, as this will make resolution slower.

---------------
Troubleshooting
---------------

If you stumble upon bug, file a bug in the "issues" section. If possible, helping track and solve the bug would be cool.

---------------------
Enhancement proposals
---------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Support "atoms" apart from iterables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using ``template_suffixes`` = '-' instead of ``('-',)`` may be nice.

~~~~~~~~~~~~~~~
Lazy evaluation
~~~~~~~~~~~~~~~

Not exactly like I can do anything about it.

If Django could receive a lazy object for ``get_template_names`` instead of a pre-evaluated iterable, this implementation would be both more time-efficient and space-efficient in best and average scenarios.
