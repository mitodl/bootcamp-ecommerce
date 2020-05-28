"""CMS serializers"""
from rest_framework import serializers

from cms import models
from cms.templatetags.image_version_url import image_version_url


class BootcampRunPageSerializer(serializers.ModelSerializer):
    """BootcampRunPage serializer"""

    thumbnail_image_src = serializers.SerializerMethodField()

    def get_thumbnail_image_src(self, bootcamp_run_page):
        """Gets the versioned image source URL for the page's thumbnail image"""
        return (
            None
            if not bootcamp_run_page.thumbnail_image
            else image_version_url(bootcamp_run_page.thumbnail_image, "fill-132x132")
        )

    class Meta:
        model = models.BootcampRunPage
        fields = ["description", "subhead", "thumbnail_image_src"]
