django-select2-forms
====================

**django-select2-forms** is a project that makes available Django form fields that
use the [Select2 javascript plugin](http://ivaynberg.github.com/select2/). It was
created by developers at [The Atlantic](http://www.theatlantic.com/).

* [Installation](#installation)
* [Usage](#usage)
   * [select2.fields.ForeignKey examples](#select2fieldsforeignkey-examples)
   * [select2.fields.ManyToManyField examples](#select2fieldsmanyomanyfield-examples)
   * [form field example](#form-field-example)
* [API Documentation](#api-documentation)
* [License](#license)

Installation
------------

The recommended way to install is with pip:

    pip install django-select2-forms

or, to install with pip from source:

        pip install -e git+git://github.com/theatlantic/django-select2-forms.git#egg=django-select2-forms

If the source is already checked out, use setuptools:

        python setup.py develop

Configuration
-------------

`django-select2-forms` serves static assets using [django.contrib.staticfiles](https://docs.djangoproject.com/en/1.5/howto/static-files/), and so requires that `"select2"` be added to your settings' `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    # ...
    'select2',
)
```

([django-staticfiles](http://django-staticfiles.readthedocs.org/en/latest/) should also work for Django <= 1.2).

To use django-select2-forms' ajax support, `'select2.urls'` must be included in your urls.py `urlpatterns`:

```python
urlpatterns = patterns('',
    # ...
    url(r'^select2/', include('select2.urls')),
)
```

Usage
-----

The simplest way to use `django-select2-forms` is to use `select2.fields.ForeignKey` and `select2.fields.ManyToManyField` in place of `django.db.models.ForeignKey` and `django.db.models.ManyToManyField`, respectively. These fields extend their django equivalents and take the same arguments, along with extra optional keyword arguments.

#### select2.fields.ForeignKey examples

In the following two examples, an "entry" is associated with only one author. The example below does not use ajax, but instead performs autocomplete filtering on the client-side using the `<option>` elements (the labels of which are drawn from `Author.__unicode__()`) in an html `<select>`.

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Entry(models.Model):
    author = select2.fields.ForeignKey(Author,
        overlay="Choose an author...")
```

This more advanced example autocompletes via ajax using the `Author.name` field and limits the autocomplete search to `Author.objects.filter(active=True)`

```python
class Author(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField()

class Entry(models.Model):
    author = select2.fields.ForeignKey(Author,
        limit_choices_to=models.Q(active=True),
        ajax=True,
        search_field='name',
        overlay="Choose an author...",
        js_options={
            'quiet_millis': 200,
        })
```

#### select2.fields.ManyToManyField examples

In the following basic example, entries can have more than one author. This
example does not do author name lookup via ajax, but populates `<option>` elements in a `<select>` with `Author.__unicode__()` for labels.

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Entry(models.Model):
    authors = select2.fields.ManyToManyField(Author)
```

The following "kitchen sink" example allows authors to be ordered, and uses ajax to autocomplete on two variants of an author's name.

```python
from django.db import models
from django.db.models import Q
import select2.fields
import select2.models

class Author(models.Model):
    name = models.CharField(max_length=100)
    alt_name = models.CharField(max_length=100, blank=True, null=True)

class EntryAuthors(select2.models.SortableThroughModel):
    """
    A custom m2m through table, with a `position` field for sorting.

    This allows us to store and retrieve an ordered list of authors for an entry.
    """
    entry = models.ForeignKey('Entry')
    author = models.ForeignKey(Author)
    position = models.PositiveSmallIntegerField()

class Entry(models.Model):
    categories = select2.fields.ManyToManyField(Author,
        through='EntryAuthors',
        ajax=True,
        search_field=lambda q: Q(name__icontains=q) | Q(alt_name__icontains=q),
        sort_field='position',
        js_options={'quiet_millis': 200})
```

#### form field example

If you don't need to use the ajax features of `django-select2-forms` it is possible to use select2 on django forms without modifying your models. The select2 formfields exist in the `select2.fields` module and have the same class names as their standard django counterparts (`ChoiceField`, `MultipleChoiceField`, `ModelChoiceField`, `ModelMultipleChoiceField`). Here is the first `ForeignKey` example above, done with django formfields.

```python
class AuthorManager(models.Manager):
    def as_choices(self):
        for author in self.all():
            yield (author.pk, unicode(author))


class Author(models.Model):
    name = models.CharField(max_length=100)
    objects = AuthorManager()

    def __unicode__(self):
        return self.name


class Entry(models.Model):
    author = models.ForeignKey(Author)


class EntryForm(forms.ModelForm):
    author = select2.fields.ChoiceField(
            choices=Author.objects.as_choices(),
            overlay="Choose an author...")

    class Meta:
        model = Entry
```

API Documentation
-----------------

#### class select2.fields.ForeignKey(to, **kwargs)

<b>`select2.fields.ForeignKey`</b> takes the following keywords arguments:

##### overlay

The placeholder text that will be displayed on an empty select2 field.

##### ajax = False

Calling `select2.fields.ForeignKey` with `ajax = True` causes select2 to populate the autocomplete results using ajax. This argument defaults to `False`.
The ajax loading mechanism uses urls predefined for model retrieval. Simply include the supplied `select2.urls` into your URL mappings to enable the loading URLs.

##### search_field

`search_field` is the field name on the related model that should be searched for the ajax autocomplete. This field is required if `ajax = True`. `search_field` can also be a callable which takes the search string as an argument and returns a `django.db.models.Q` object. 


##### case_sensitive = False

If `ajax=True` and `search_field` is a string, determines whether the autocomplete lookup uses `%(search_field)s__icontains` or `%(search_field)s__contains` when filtering the results. The default is to perform case insensitive lookups.

##### js_options = {}

A dict that is passed as options to `jQuery.fn.select2()` in javascript.

#### class select2.fields.ManyToManyField(to, **kwargs)

`select2.fields.ManyToManyField` takes all the same arguments as `select2.fields.ForeignKey`. It takes the following keyword arguments in addition.

##### sort_field

The field name on the `select2.models.SortableThroughModel` class to use when storing sort position on save. See the "kitchen sink" example above to see how this is used.


License
-------
The django code is licensed under the
[Simplified BSD License](http://opensource.org/licenses/BSD-2-Clause) and
is copyright The Atlantic Media Company. View the `LICENSE` file under the
root directory for complete license and copyright information.

The Select2 javascript library included is licensed under the
[Apache Software Foundation License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
View the file `select2/static/select2/select2/LICENSE` for complete license
and copyright information about the Select2 javascript library.
