from rest_framework import serializers

from localization.models import Language


class LanguageSerializer(serializers.ModelSerializer):
    flag_url = serializers.SerializerMethodField()

    class Meta:
        model = Language
        fields = [
            "id",
            "code",
            "name_native",
            "flag_url",
            "is_active",
            "is_default",
            "sort_order",
        ]

    def get_flag_url(self, obj):
        if not obj.flag:
            return None
        request = self.context.get("request")
        url = obj.flag.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
