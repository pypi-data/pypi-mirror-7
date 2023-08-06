from __future__ import absolute_import

import json
import pickle

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .runtime_data import history_types_dict


class HistoryType(models.Model):
    namespace = models.CharField(max_length=64, verbose_name=_(u'namespace'))
    name = models.CharField(max_length=64, verbose_name=_(u'name'))

    def __unicode__(self):
        try:
            return unicode(history_types_dict[self.namespace][self.name]['label'])
        except KeyError:
            return u'obsolete history type: %s - %s' % (self.namespace, self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('history_type_list', [self.pk])

    class Meta:
        ordering = ('namespace', 'name')
        unique_together = ('namespace', 'name')
        verbose_name = _(u'history type')
        verbose_name_plural = _(u'history types')


class History(models.Model):
    datetime = models.DateTimeField(verbose_name=_(u'date time'))
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    history_type = models.ForeignKey(HistoryType, verbose_name=_(u'history type'))
    dictionary = models.TextField(verbose_name=_(u'dictionary'), blank=True)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.datetime, self.content_object, self.history_type)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.datetime = now()
        super(History, self).save(*args, **kwargs)

    def get_label(self):
        return history_types_dict[self.history_type.namespace][self.history_type.name]['label']

    def get_summary(self):
        return history_types_dict[self.history_type.namespace][self.history_type.name].get('summary', u'')

    def get_details(self):
        return history_types_dict[self.history_type.namespace][self.history_type.name].get('details', u'')

    def get_expressions(self):
        return history_types_dict[self.history_type.namespace][self.history_type.name].get('expressions', {})

    def get_processed_summary(self):
        return _process_history_text(self, self.get_summary())

    def get_processed_details(self):
        return _process_history_text(self, self.get_details())

    @models.permalink
    def get_absolute_url(self):
        return ('history_view', [self.pk])

    class Meta:
        ordering = ('-datetime',)
        verbose_name = _(u'history')
        verbose_name_plural = _(u'histories')


def _process_history_text(history, text):
    key_values = {
        'content_object': history.content_object,
        'datetime': history.datetime
    }

    loaded_dictionary = json.loads(history.dictionary)

    new_dict = {}
    for key, values in loaded_dictionary.items():
        value_type = pickle.loads(str(values['type']))
        if isinstance(value_type, models.base.ModelBase):
            for deserialized in serializers.deserialize('json', values['value']):
                new_dict[key] = deserialized.object
        elif isinstance(value_type, models.query.QuerySet):
            qs = []
            for deserialized in serializers.deserialize('json', values['value']):
                qs.append(deserialized.object)
            new_dict[key] = qs
        else:
            new_dict[key] = json.loads(values['value'])

    key_values.update(new_dict)
    expressions_dict = {}

    for key, value in history.get_expressions().items():
        try:
            expressions_dict[key] = eval(value, key_values.copy())
        except Exception as exception:
            expressions_dict[key] = exception

    key_values.update(expressions_dict)
    return text % key_values
