from django.db import models
from django.conf import settings
from django.utils import timezone


class GeneralTestResult(models.Model):
    
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='general_test_results')

    predicted_disorder = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    suggestions = models.JSONField(blank=True, null=True)

    video_url = models.URLField(blank=True)

    answers = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else 'Guest'
        return f"Test Result for {username} - {self.predicted_disorder}"
