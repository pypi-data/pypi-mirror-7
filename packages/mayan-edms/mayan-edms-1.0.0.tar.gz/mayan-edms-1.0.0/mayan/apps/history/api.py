from __future__ import absolute_import

import json
import pickle

from django.db import models
from django.core import serializers

from .models import HistoryType, History
from .runtime_data import history_types_dict


def register_history_type(history_type_dict):
    namespace = history_type_dict['namespace']
    name = history_type_dict['name']

    # Runtime
    history_types_dict.setdefault(namespace, {})
    history_types_dict[namespace][name] = {
        'label': history_type_dict['label'],
        'summary': history_type_dict.get('summary', u''),
        'details': history_type_dict.get('details', u''),
        'expressions': history_type_dict.get('expressions', {}),
    }


def create_history(history_type_dict, source_object=None, data=None):
    history_type, created = HistoryType.objects.get_or_create(namespace=history_type_dict['namespace'], name=history_type_dict['name'])

    new_history = History(history_type=history_type)
    if source_object:
        new_history.content_object = source_object
    if data:
        new_dict = {}
        for key, value in data.items():
            new_dict[key] = {}
            if isinstance(value, models.Model):
                new_dict[key]['value'] = serializers.serialize('json', [value])
            elif isinstance(value, models.query.QuerySet):
                new_dict[key]['value'] = serializers.serialize('json', value)
            else:
                new_dict[key]['value'] = json.dumps(value)
            new_dict[key]['type'] = pickle.dumps(type(value))

        new_history.dictionary = json.dumps(new_dict)
    new_history.save()
