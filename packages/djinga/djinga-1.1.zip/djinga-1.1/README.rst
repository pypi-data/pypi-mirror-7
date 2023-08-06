djinga
======

|copyright| 2014 Thomas Khyn

Unobtrusive jinja2 integration in Django

Freely inspired from django-jinja_ and django-jinja2_, as none of them met all
my expectations!


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
   The file extensions for templates that should be rendered with Django's
   internal template engine.

   Defaults to ``('html', 'htm', 'jjhtml', 'jjhtm')``

JINJA2_JJ_EXTS
   The file extensions for templates that should be rendered with Jinja2.

   Defaults to ``('jjhtml', 'jjhtm')``

JINJA2_CONDITION
   A function taking as sole argument the path of the template file and
   returning True if the file should be rendered with Jinja2. Defaults to a
   function returning True if the extension is in JINJA2_JJ_EXTS

JINJA2_EXTENSIONS
   The extensions to be loaded by jinja2. Some extensions are shipped with
   djinga under ``djinga.ext.*``

JINJA2_ENV_ARGS
   The jinja2 environment's constructor keyword arguments as a dictionary.

JINJA2_GLOBALS
   The jinja2 globals as a dictionary.

JINJA2_FILTERS
   The jinja2 filters as a dictionary.


Extensions and template tags
----------------------------

Built-in Jinja2 extensions
..........................

Djinga comes with several Jinja2 extensions

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
   Provides a ``{% django %}{% enddjango %}`` tag to include django template
   language in a jinja2 template. For this tag to work, the
   ``django.core.context_processors.request`` context processor must be
   enabled.

djinga.ext.url
   Provides a tag for URL reversing, similar to the django templates one.

Other Jinja2 extensions
.......................

djinga.ext.htmlcompress.HTMLCompress / SelectiveHTMLCompress
   |copyright| 2011 Armin Ronacher.
   Eliminates useless whitespace at template compilation time without extra
   overhead.

Django template tags
....................

The following tags are available in any django template explicitly loading
``djinga_tags`` using the ``{% load djinga_tags %}`` statement.

extends
   Overrides the standard ``{% extends %}`` tag and enables it to refer to
   jinja2 files as well as normal django template files. While the template
   engine for the current file remains Django's one, the template engine for
   the extended file can be either Jinja2 or Django, depending on the file
   extension (in JINJA2_DJ_EXTS or JINJA2_JJ_EXTS)


Management command
------------------

Djinga overrides the Django core management command ``makemessages`` to include
the specific Jinja2 translation tags and ensure the strings marked for
translation in Jinja2 templates appear in the translations dictionary.


.. |copyright| unicode:: 0xA9

.. _django-jinja: https://github.com/niwibe/django-jinja
.. _django-jinja2: https://github.com/yuchant/django-jinja2
