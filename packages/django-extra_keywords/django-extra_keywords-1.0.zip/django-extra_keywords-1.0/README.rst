Extra keywords for Django
=========================

|copyright| 2014 Thomas Khyn

About
-----

The django ``makemessage`` management command parses the code of an application
to generate .pot and .po files, provided the strings to be translated are
called by the gettext-like functions (gettext, ugettext, ngettext,
ugettext_lazy, etc.) or the ``_`` alias.

However, it is quite common to use other aliases than ``_``, for example for
lazy translation, where ``_l`` can be used.

Django does not provide a way to specify other aliases that may be used for
translation strings. This plugin fills this gap, without having to patch the
django code itself.

Usage
-----

Simply add ``'extra_keywords'`` to your INSTALLED_APPS after having installed
the package with the method of your choice. Note that it does not make any
sense to have this application installed in production.

Once it is installed, you may for example run::

   manage.py makemessages [...] --extra-keywords=_l [...]

so that ``_l('to translate')`` is recognised and 'to translate' is
added to the locale dictionnary.

.. |copyright| unicode:: 0xA9
