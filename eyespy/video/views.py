from django.shortcuts import render,HttpResponse,redirect
from .forms import Video_form
from .models import Video
from .tasks import process_video


def index(request):
    all_video = Video.objects.all()

    if request.method == "POST":
        form = Video_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            # form.save()
            # tm.sleep(20)
            file_name  = all_video[0].name
            task = process_video.delay(file_name)
            return render(request, 'index.html', {"form": form, "all": all_video, "task_id":task.task_id})
    else:
        form = Video_form()
        return render(request, 'index.html', {"form": form, "all": all_video, "task_id":"0"})