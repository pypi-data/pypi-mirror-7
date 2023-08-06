=================================
django-ckeditor-filebrowser-filer
=================================

.. image:: https://badge.fury.io/py/django-ckeditor-filebrowser-filer.png
    :target: https://badge.fury.io/py/django-ckeditor-filebrowser-filer

A django-filer based CKEditor filebrowser

Documentation
-------------

A CKEditor filebrowser based on `django-filer`_

Origin code is taken from `django-ckeditor-filer`_

.. _django-filer: https://pypi.python.org/pypi/django-filer
.. _django-ckeditor-filer: https://github.com/ikresoft/django-ckeditor-filer/

Quickstart
----------

Install django-ckeditor-filebrowser-filer::

    pip install django-ckeditor-filebrowser-filer

Then add it to INSTALLED_APPS along with its dependencies::

    'filer',
    'cmsplugin_filer_image',
    'ckeditor_filebrowser_filer',

Add `ckeditor_filebrowser_filer` to urlconf::

    url(r'^filebrowser_filer/', include('ckeditor_filebrowser_filer.urls')),

Add `FilerImage` button to you CKEditor configuration.
