from django.db import models
import os
import time


def update_filename(instance, filename):
    path = "video/"
    format = instance.title + str(time.time())[0:12].replace('.','') + '.mp4'
    return os.path.join(path, format)

class Video(models.Model):
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to=update_filename)
    frames = models.IntegerField(default=0) 
    fps = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title