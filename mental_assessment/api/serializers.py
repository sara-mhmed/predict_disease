from rest_framework import serializers
from ..models import GeneralTestResult

class GeneralTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralTestResult
        fields = [
            "id", "user", "predicted_disorder", "description",
            "suggestions", "video_url", "answers", "created_at"
        ]
        read_only_fields = ["id", "created_at", "user"]
