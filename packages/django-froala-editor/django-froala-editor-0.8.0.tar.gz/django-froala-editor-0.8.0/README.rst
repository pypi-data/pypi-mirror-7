======================
django-froala-editor
======================

django-froala-editor package helps integrate `Froala WYSIWYG editor <http://editor.froala.com/>`_ with Django.


Getting started
====================

1. Install the package::

    pip install git+git://github.com/xtranophilist/django-froala-editor.git

OR

Add the directory `froala_editor` from this repo to your Python path.

2. Add ``froala_editor`` to INSTALLED_APPS in ``settings.py``.

3. Add the following line to ``urlpatterns`` in your application's ``urls.py``.


.. code-block:: python

    url(r'^froala_editor/', include('froala_editor.urls')),

Skip this url inclusion if you don't want image upload inside WYSIWYG editor. Images from URLs can still be embedded.

Usage
==============

.. code-block:: python

    from django.db import models
    from froala_editor.fields import FroalaField

    class Page(models.Model):
        content = FroalaField()

`FroalaField` uses `froala_editor.widgets.FroalaEditor` as its widget. You may directly use this widget with any of your forms.py:

.. code-block:: python

    from django import forms
    from froala_editor.widgets import FroalaEditor

    class PageForm(forms.ModelForm):
        content = models.TextField(widget=FroalaEditor)


Usage outside admin
^^^^^^^^^^^^^^^^^^^^^^

When used outside the Django admin, the media files are to be manually included in the template. Inside the <head> section or before the form is rendered, include:

.. code-block:: python

    {{ form.media }}

OR:

.. code-block:: python

    <link href="{{STATIC_URL}}froala_editor/css/font-awesome.min.css" type="text/css" media="all" rel="stylesheet" />
    <link href="{{STATIC_URL}}froala_editor/css/froala_editor.min.css" type="text/css" media="all" rel="stylesheet" />
    <script type="text/javascript" src="{{STATIC_URL}}froala_editor/js/jquery.min.js"></script>
    <script type="text/javascript" src="{{STATIC_URL}}froala_editor/js/froala_editor.min.js"></script>


If your template already uses jQuery (v1.10.2+ required), include:

.. code-block:: python

    <link href="{{STATIC_URL}}froala_editor/css/font-awesome.min.css" type="text/css" media="all" rel="stylesheet" />
    <link href="{{STATIC_URL}}froala_editor/css/froala_editor.min.css" type="text/css" media="all" rel="stylesheet" />
    <script type="text/javascript" src="{{STATIC_URL}}froala_editor/js/froala_editor.min.js"></script>



Options
==============

Froala Editor provides several options for customizing the editor. See http://editor.froala.com/docs for all available options.
You can provide a dictionary of these options as `FROALA_EDITOR_OPTIONS` setting in `settings.py`. These options would then be used for all instances of the WYSIWYG editor in the project.

Options for individual field can also be provided via FroalaField or FroalEditor class. This overrides any options set via `FROALA_EDITOR_OPTIONS`.:

.. code-block:: python

    from django.db import models
    from froala_editor.fields import FroalaField

    class Page(models.Model):
        content = FroalaField(options={
            'inlineMode': True,
        })

.. code-block:: python

    from django import forms
    from froala_editor.widgets import FroalaEditor

    class PageForm(forms.ModelForm):
        content = forms.TextField(widget=FroalaEditor(options={
            'inlineMode': True,
        }        ))

You can use ``FROALA_UPLOAD_PATH`` setting in ``settings.py`` to change the path where uploaded files are stored within the ``MEDIA_ROOT``. By default, ``uploads/froala_editor/images`` is used for storing uploaded images.


License
===============

This package is available under BSD License.
However, Froala editor is free only for non-commercial projects. For other uses, see http://editor.froala.com/download for licensing.