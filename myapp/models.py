from django.db import models
from django.contrib.auth.models import User

class GeneralTestResult(models.Model):
    #if the user is guest, user field will be null

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    predicted_disorder = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    suggestions = models.JSONField(blank=True, null=True)
    video_url = models.URLField(blank=True)
    answers = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test Result for {self.user.username if self.user else 'Guest'} - {self.predict_disorder}"
    