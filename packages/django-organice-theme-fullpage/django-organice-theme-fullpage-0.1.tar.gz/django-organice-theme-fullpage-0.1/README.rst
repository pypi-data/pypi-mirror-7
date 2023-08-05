===============================
django Organice Full-Page Theme
===============================

A `django Organice`_ theme with full-page display as used by Organice.io

How To Use This Theme
=====================

#. Install this Django app along with ``django-organice``::

    pip install django-organice-theme-fullpage

#. Add ``organice_theme_fullpage`` to your ``INSTALLED_APPS``::

    'organice_theme_fullpage',
    'organice_theme',
    'organice',
    ...

How To Modify This Theme
========================

This theme depends on the base theme `django-organice-theme`_, the asset build process will re-use resources
from it.  Make sure you clone both repositories on the same directory level.  Your folder structure should look
something like this::

    .
    ├── django-organice-theme
    │   ├── organice_theme
    │   │   ├── static
    │   │   └── templates
    ├── django-organice-theme-fullpage
    │   ├── organice_theme_fullpage
    │   │   ├── static
    │   │   └── templates

Then, loop until you're happy:

- Add or adapt the style sheet (``.scss``), JavaScript (``.js``), and other files in ``organice_theme_fullpage/static/``.
- Run ``make assets`` in order to compile the Sass files to CSS, and combine and minify both CSS und JavaScript.
- Adapt the template files in ``organice_theme_fullpage/templates/``, and test the results on your development system.

*NOTE:* Themes that intend to override the base theme's styles and JavaScript must define the following two lines in
``templates/base.html``::

    {% block theme_css %}{% static 'css/styles.css' %}{% endblock theme_css %}
    {% block theme_js %}{% static 'js/scripts.js' %}{% endblock theme_js %}

Download and Contributions
==========================

Official repositories: (kept in sync)

#. Bitbucket: https://bitbucket.org/bittner/django-organice-theme-fullpage
#. GitHub: https://github.com/bittner/django-organice-theme-fullpage

Getting Help
============

- Documentation is available at http://docs.organice.io
- Questions? Please use StackOverflow_.  Tag your questions with ``django-organice``.
- Found a bug? Please use either the Bitbucket_ or GitHub_ issue tracker (you choose)


.. _`django Organice`: http://organice.io/
.. _`django-organice-theme`: https://pypi.python.org/pypi/django-organice-theme
.. _StackOverflow: http://stackoverflow.com/questions/tagged/django-organice
.. _Bitbucket: https://bitbucket.org/bittner/django-organice-theme-fullpage/issues
.. _GitHub: https://github.com/bittner/django-organice-theme-fullpage/issues
