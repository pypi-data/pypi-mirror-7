djinga
======

|copyright| 2014 Thomas Khyn

Unobtrusive jinja2 integration in Django

Freely inspired from django-jinja_ and django-jinja2_, as none of them met all
my expectations!


Compatible with django 1.4 to 1.7 and relevant python versions (2.7 to 3.4).


Usage
-----

- Install djinga using the method of your choice
- Add 'djinga' to your INSTALLED_APPS
- Change the TEMPLATE_LOADERS settings to::

   TEMPLATE_LOADERS = (
      'djinga.loaders.FileSystemLoader',
      'djinga.loaders.AppLoader',
   )

- Add the relevant `settings`_ for jinja2


How it works
------------

By default, a template will be rendered using Django's built-in template engine
if it has a .html, .htm, .djhtml or .djhtm file extension. If it has a .jjhtml
or .jjhtm file extension, it will be rendered by Jinja2, using the setting
values provided in django's setting module.


Settings
--------

JINJA2_DJ_EXTS
   A list or tuple of file extensions (with or without the leading dot) for
   templates that should be rendered with Django's internal template engine.

   Defaults to ``('html', 'htm', 'jjhtml', 'jjhtm')``

JINJA2_JJ_EXTS
   A list or tuple of the file extensions (with or without the leading dot) for
   templates that should be rendered with Jinja2.

   Defaults to ``('jjhtml', 'jjhtm')``

JINJA2_CONDITION
   A function taking as sole argument the path of the template file and
   returning True if the file should be rendered with Jinja2. Defaults to a
   function returning True if the extension is in JINJA2_JJ_EXTS

JINJA2_EXTENSIONS
   A tuple or list of extensions to be loaded by jinja2 (as python objects or
   paths to the python objects). `Some extensions`_ are shipped with
   djinga under ``djinga.ext.*``.

JINJA2_ENV_ARGS
   The jinja2 environment's constructor keyword arguments as a dictionary.

JINJA2_GLOBALS
   The jinja2 globals as a dictionary.

JINJA2_FILTERS
   The jinja2 filters as a dictionary.

JINJA2_LOAD_FROM
   A tuple or list of module paths to load globals and filters from. This
   advantageously complements or replaces ``JINJA_GLOBALS`` and
   ``JINJA2_FILTERS``. See `Adding globals and filters`_ for details.

Jinja2 extensions
-----------------

Djinga comes with several Jinja2 extensions:

djinga.ext.static
   Provides a ``{% static 'path' %}`` tag to refer to Django's staticfiles
   directory

djinga.ext.css
   Provides a ``{% css 'rel/path/to/file.css' %}`` tag that generates a
   HTML link element refering to the css file located at a relative path in
   a css directory. The css directory's path can be defined relatively to
   Django's staticfiles directory through the setting JINJA2_STATIC_CSS

djinga.ext.js
   Same as djinga.ext.css but generates a HTML script element refering to a
   javascript file. The js directory's relative path can be set through the
   setting JINJA2_STATIC_JS

djinga.ext.media
   Simply concatenates django's MEDIA_URL to the argument provided

djinga.ext.django
   From `a PR on coffin`_.
   Provides a ``{% django %}{% enddjango %}`` tag to include django template
   language in a jinja2 template. For this tag to work, the
   ``django.core.context_processors.request`` context processor must be
   enabled.

djinga.ext.csrf_token
   From coffin_
   Provides a Django-like ``{% csrf_token %}`` tag.

djinga.ext.url
   Provides a tag for URL reversing, similar to the django templates one.

djinga.ext.htmlcompress.HTMLCompress / SelectiveHTMLCompress
   Based on `Armin Ronacher's version`_.
   Eliminates useless whitespace at template compilation time without extra
   overhead.

Django template tags
--------------------

The following tags are available in any django template explicitly loading
``djinga_tags`` using the ``{% load djinga_tags %}`` statement.

extends
   Overrides the standard ``{% extends %}`` tag and enables it to refer to
   jinja2 files as well as normal django template files. While the template
   engine for the current file remains Django's one, the template engine for
   the extended file can be either Jinja2 or Django, depending on the file
   extension (in JINJA2_DJ_EXTS or JINJA2_JJ_EXTS)



Adding globals and filters
--------------------------

A straightforward way to add globals and filters and make them available from
your Jinja2 templates is to add them to the ``JINJA2_GLOBALS`` or the
``JINJA2_FILTERS`` in the settings module.

However, this is not always convenient nor possible (import loops), and djinga
therefore provides a way to ease this process, through the ``jj_global`` and
``jj_filter`` decorators in combination with the ``JINJA2_LOAD_FROM`` setting.

Basically, the decorators mark the functions as Jinja2 globals or filters,
while the setting (a list of module paths) indicates djinga where to look for
them.

A short example is better than long explanations, so here we go.

This::

   [my_app/my_module.py]
   from djinga.register import jj_filter, jj_global

   @jj_global
   def my_tag(*args, **kw):
      pass

   @jj_filter
   def my_filter(*args, **kw)
      pass

   [settings.py]
   JINJA2_LOAD_FROM = (
      'my_app.my_module',
   )

is equivalent to this::

   [my_app/my_module.py]
   def my_tag(*args):
      pass

   def my_filter(*args, **kw)
      pass

   [settings.py]
   from my_module import my_tag, my_filter
   JINJA2_GLOBALS = {'my_tag': my_tag}
   JINJA2_FILTERS = {'my_filter': my_filter}

...with the significant advantage of not requiring a possibly issue-prone
``import`` statement in the ``settings`` module.

The ``jj_global`` and ``jj_filter`` decorators are compatible with any of the
`Jinja2 built-in decorators`_. They do not affect the behavior nor the
signature of the decorated function, so you can use it normally (as a normal
Django template tag or filter, for example).

The collected globals and filters are appended to the ones already specified
in ``JINJA2_GLOBALS`` and ``JINJA2_FILTERS``.


``makemesssages`` management command
------------------------------------

Adapted from coffin_.

Djinga overrides the Django ``makemessages`` core management command to include
the specific Jinja2 translation tags and ensure the strings marked for
translation in Jinja2 templates appear in the translations dictionary.


.. |copyright| unicode:: 0xA9

.. _django-jinja: https://github.com/niwibe/django-jinja
.. _django-jinja2: https://github.com/yuchant/django-jinja2
.. _`Some extensions`: `Jinja2 extensions`_
.. _`a PR on coffin`: https://github.com/coffin/coffin/pull/12/files?short_path=88b99bb#diff-e511b022f54e135b99f896c8fb355067R131
.. _coffin: https://github.com/coffin/coffin/pull/12/files?short_path=88b99bb
.. _`Armin Ronacher's version`: https://github.com/mitsuhiko/jinja2-htmlcompress/blob/master/jinja2htmlcompress.py
.. _`Jinja2 built-in decorators`: http://jinja.pocoo.org/docs/api/#utilities
