django-static-underscore-i18n
=================

.. image:: https://travis-ci.org/cubicova17/django-static-underscore-i18n.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/zyegfryed/django-static-underscore-i18n

A Django app that provides helper for compiling underscore templates to static
files with i18 support.

Overview
--------

This repo an project is forked from ``django-statici18n`` 
`github.com/zyegfryed/django-statici18n`_ to tackle the problem of compiling of Underscore templates to single static js file.
The original code was generating static js files for translations.

This app is intended to make life easier when you want to work with your Underscore templates and translate them with Django default i18n module (no js ``gettext``). If you are using Underscore templates you can have project directory like::

   <project_directory>/
       ...
       locale/
       +- en/
       +- fr/
       templates/
       +- underscore/
          |
          +- popup.html
       +- modals/
       +- include/
       +- main.html

and your ``popup.html`` can look like::

     <div>
         {% trans "Hello" %} <% username %>
     </div>

and you want to render it in something like Backbone::

    PopupView = Backbone.View.extend({
        template: _.template(popup_variable_name),
    });

to do this you need to compile your .html template to be available in js with ``popup_variable_name``. Moreover if you have multiple templates, you can bundle them int single js file and serve it via CDN or nginx ommiting django.

With ``django-static-underscore-i18n`` you can do this by following. Declare dictionary mapping between html files and js variable names::

    STATIC_UNDERSCORE_TEMPLATES = {'popup_variable_name': 'underscore/popup.html', ... , }

and run  ``python manage.py compilejsunderscorei18n`` which will bundle your html templates into one js file for each locale supporting i18 ``{% trans %}`` tags.

.. _javascript_catalog view: https://docs.djangoproject.com/en/1.6/topics/i18n/translation/#module-django.views.i18n
.. _adding an overhead: https://docs.djangoproject.com/en/1.6/topics/i18n/translation/#note-on-performance
.. _github.com/zyegfryed/django-statici18n: https://github.com/zyegfryed/django-statici18n

Installation
------------

1. Use your favorite Python packaging tool to install ``django-staticunderscorei18n``
   from `PyPI`_, e.g.::

    pip install django-staticunderscorei18n

2. Add ``'staticunderscorei18n'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = [
        # ...
        'staticunderscorei18n',
    ]

3. Once you have edited your underscore .html templates or `translated`_ and `compiled`_ your messages, use the
   ``compilejsunderscorei18n`` management command::

    python manage.py compilejsunderscorei18n

4. Check that the ``django.core.context_processors.i18n`` context processor is added to your
   ``TEMPLATE_CONTEXT_PROCESSORS`` setting - should have already been set by
   Django. This is needed to resolve request.LANGUAGE_CODE variable during compilation phase::

    TEMPLATE_CONTEXT_PROCESSORS = (
      # ...
      'django.core.context_processors.i18n',
    )

and you should have ``FileSystemFinder`` and ``AppDirectoriesFinder`` to be available::

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',     
        )

5. Edit your template(s) and insert .js files those were compiled. Good practice is to serve static files without django server (you can you nginx for that):

 .. code-block:: html+django

    <script src="{{ STATIC_URL }}jsunderscorei18n/{{ LANGUAGE_CODE }}/underscore_templates.js"></script>

.. note::

    By default, the generated catalogs are stored to ``STATIC_ROOT/jsunderscorei18n``.
    You can modify the output path and more options by tweaking
    ``django-staticunderscorei18n`` settings.

.. _PyPI: http://pypi.python.org/pypi/django-staticunderscorei18n
.. _translated: https://docs.djangoproject.com/en/1.6/topics/i18n/translation/#message-files
.. _compiled: https://docs.djangoproject.com/en/1.6/topics/i18n/translation/#compiling-message-files


