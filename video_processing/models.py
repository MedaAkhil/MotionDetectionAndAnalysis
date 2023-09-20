from django.db import models

class ProcessedVideo(models.Model):
    title = models.CharField(max_length=255)
    video = models.FileField(upload_to='videos/')
    plot = models.ImageField(upload_to='plots/')
