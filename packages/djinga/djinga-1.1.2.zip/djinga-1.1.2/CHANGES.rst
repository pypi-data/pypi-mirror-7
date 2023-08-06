Changes
=======

1.1.2 (2014-08-15)
------------------

Bugfixes:

- extensions package import issues
- JINJA2_[DJ]J_EXTS handling:
   * an exception is raised if the value is not a list or tuple
   * file extensions tolerate leading dot
   * clarified documentation
- issues with Python 3

Documentation:

- added previously missing doc relative to jj_global and jj_filter decorators
  and JINJA2_FROM_MODULE setting value


1.1.1 (2014-08-06)
------------------

- Compatibility with Django 1.4 to 1.7
- Compatibility with Python 2.6 to 3.4 (depending on django version)


1.1 (2014-07-20)
----------------

- Added ``csrf_token`` extension (from coffin)
- Added warning when request context processor is not enabled and
  ``{% django %}`` is used
- Filters and globals can now be imported from any module


1.0 (2014-03-19)
----------------

- Birth!
- Available extensions: HtmlCompress and static files (static, css, js)
- makemessages override from coffin
- automatic selection of template engine
