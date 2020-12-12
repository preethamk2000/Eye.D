from django.conf import settings
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from time import sleep

@shared_task(bind=True)
def go_to_sleep(self, duration):
    progress_recorder = ProgressRecorder(self)
    for i in range(duration):
        sleep(1)
        progress_recorder.set_progress(i + 1, duration, f'On iteration {i}')
    return 'Done'

# @shared_task(bind=True)
# def video_processing(self, filename):
#     media_url = settings.MEDIA_URL
#     path_to_user_folder = media_url + "/video/20" + filename + ".mp4"