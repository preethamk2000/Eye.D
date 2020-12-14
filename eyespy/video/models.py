from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to="video")
    
    def __str__(self):
        return self.title