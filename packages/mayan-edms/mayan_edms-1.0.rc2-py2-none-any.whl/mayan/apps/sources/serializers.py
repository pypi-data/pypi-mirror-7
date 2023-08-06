from __future__ import absolute_import

import logging

from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import StagingFolder

logger = logging.getLogger(__name__)


class StagingFolderFileSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('get_url')
    image_url = serializers.SerializerMethodField('get_image_url')
    filename = serializers.CharField(max_length=255)

    def get_url(self, obj):
        return reverse('stagingfolderfile-detail', args=[obj.staging_folder.pk, obj.encoded_filename], request=self.context.get('request'))

    def get_image_url(self, obj):
        return reverse('stagingfolderfile-image-view', args=[obj.staging_folder.pk, obj.encoded_filename], request=self.context.get('request'))


class StagingFolderSerializer(serializers.HyperlinkedModelSerializer):
    files = serializers.SerializerMethodField('get_files')

    def get_files(self, obj):
        try:
            return [StagingFolderFileSerializer(entry, context=self.context).data for entry in obj.get_files()]
        except Exception as exception:
            logger.error('unhandled exception: %s' % exception)
            return []

    class Meta:
        model = StagingFolder


class StagingSourceFileImageSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = serializers.CharField()
