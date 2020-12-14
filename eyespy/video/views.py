from django.shortcuts import render,HttpResponse,redirect
from .forms import Video_form
from .models import Video
import pandas as pd
from time import sleep
import time as tm
import os, argparse, csv
import numpy as np
# import cv2
from .tasks import video_process
# from imageai import Detection
# from scipy.stats import itemfreq
# from IPython.core.display import HTML

def index(request):
    all_video = Video.objects.all()

    if request.method == "POST":
        form = Video_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            # tm.sleep(20)
            # task = go_to_sleep.delay(10)
            # video_process()
            # return HttpResponse("<h1> Uploaded successfully! </h1>" + task.task_id);
            task = video_process.delay("summa")
            # return HttpResponse("Done")
            # return render(request, 'index.html', {"form": form, "all": all_video, "done":1})
            return render(request, 'index.html', {"form": form, "all": all_video, "task_id":task.task_id})
    else:
        form = Video_form()
        return render(request, 'index.html', {"form": form, "all": all_video, "task_id":"0"})



def search(request):
    # f = open("demofile2.txt", "w")
    # f.write("Now the file has more content!")
    # f.close()
    df = pd.read_csv("media/out.csv",index_col=False,names=['id','Vehicle Type','B','G','R',"Entry","Exit","Image URL"])
    # df.columns = ['id','type','R','G','B',"Entry","Exit"]
    df.drop('id', axis=1, inplace=True)
    df = df.to_html(escape=False, render_links=True)
    # df = HTML(df).data
    # return HttpResponse(df)
    return render(request,'search.html',{"data":df})
    # return HttpResponse("Done!")
