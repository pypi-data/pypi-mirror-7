django-elasticfilter
====================

Create Django forms that perform ElasticSearch queries and filters.

Installing
----------

Install using pip::

    pip install django-elasticfilter

Using
-----

The filter forms are standard Django forms, with some small extensions.
They inherit from `elasticfilter.filterform.FilterForm`.
Fields to search and filter on are declared as fields on the form,
which should inherit from `elasticfilter.fields.BaseField`:

.. code:: python

    from elasticfilter.filterform import FilterForm
    from elasticfilter.fields import Query, Filter

    class MyFilterForm(FilterForm):

        class FilterFormMeta:
            s = S().get_es(**ES_SETTINGS)\
                .indexes('my-index')\
                .doctypes('my-doctype')

        match = Query(required=False, fields=['_all', '_partial'])
        type = Filter(field='type')


Custom queries and filters
~~~~~~~~~~~~~~~~~~~~~~~~~~

The provided ``Query`` and ``Filter`` classes are very basic.
Writing custom ``Query`` and ``Filter`` classes is quite simple.
For example, to filter results based upon the ``ContentType`` of the model:

.. code:: python

    from django import forms
    from django.db.models import get_models
    from elasticfilter.filterform import FilterForm
    from elasticfilter.fields import Filter

    class ContentTypeFilter(Filter, forms.ChoiceField):
        required = False

        def __init__(self, models=None, **kwargs):
            if models is None:
                models = get_models()

            self.choice_map = dict((model._meta.model_name, model)
                                   for model in models)

            choices = [(key, model.get_verbose_name())
                       for key, model in self.choice_map.items()]
            kwargs.setdefault('choices', choices)
            super(ContentTypeFilter, self).__init__(**kwargs)

        def search(self, s, name, data):
            value = data.get(name, None)
            if not value:
                return s

            field = self.field or name
            content_type = ContentType.objects.get_for_model(self.choice_map[value])
            return s.filter(F(**{field: content_type.pk}))

    class MyFilterForm(FilterForm):
        content_type = ContentTypeFilter()
