Django Pluggable FileBrowser
============================

**Media-Management with theme support**.

The Django Pluggable FileBrowser is an extension to the `Django <http://www.djangoproject.com>`_ administration interface in order to:

* browse directories on your server and upload/delete/edit/rename files.
* include images/documents to your models/database using the ``FileBrowseField``.
* select images/documents with TinyMCE.

Requirements
------------

Django Pluggable FileBrowser 3.5 requires

* Django (1.4/1.5/1.6) (http://www.djangoproject.com)
* Pillow (https://github.com/python-imaging/Pillow)

Differences from upstream
-------------------------

Django Pluggable Filebrowser is a fork of `Django Filebrowser <https://github.com/sehmaschine/django-filebrowser>`_ with the aim to make the Admin interfaces and Upload frontends choosable and easy changable.
Currently only Django stock admin interface and Grappelli (2.4, 2.5) are supported out of the box. But adding own interfaces is straightforward.

Further plans include support for pluggable upload frontends and django-xadmin support.

The project can be used as a drop in replacement for Django Filebrowser.

Installation
------------

Stable:

    pip install django-pluggable-filebrowser

Development:

    pip install -e git+git@github.com:jinzo/django-pluggable-filebrowser.git#egg=django-pluggable-filebrowser

Documentation
-------------

Build it from the sources.

Translation
-----------

You can help with translating upstream project at:
https://www.transifex.com/projects/p/django-filebrowser/

Releases
--------

* FileBrowser 3.5.7 (Development Version, not yet released, see Branch Stable/3.5.x)
* FileBrowser 3.5.6 (April 16th, 2014): Compatible with Django 1.4/1.5/1.6

Older versions are availabe at GitHub, but are not supported anymore.
