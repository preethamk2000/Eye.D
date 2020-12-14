from django.shortcuts import render,HttpResponse,redirect
from .forms import Video_form
from .models import Video
import pandas as pd
from time import sleep
import time as tm
import os, argparse, csv
import numpy as np
import cv2
from .tasks import video_process
# from imageai import Detection
# from scipy.stats import itemfreq
# from IPython.core.display import HTML

no_of_frames = [760,30]

filename = "trial1.mp4"

def index(request):
    all_video = Video.objects.all()
    if request.method == "POST":
        form = Video_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            # filename = request.POST["title"]
            # tm.sleep(20)
            # task = go_to_sleep.delay(10)
            # video_process()
            # return HttpResponse("<h1> Uploaded successfully! </h1>" + task.task_id);
            task = video_process.delay("filename",no_of_frames)
            # return HttpResponse("Done")
            # return render(request, 'index.html', {"form": form, "all": all_video, "done":1})
            return render(request, 'index.html', {"form": form, "all": all_video, "task_id":task.task_id, "file":filename})
    else:
        form = Video_form()
        return render(request, 'index.html', {"form": form, "all": all_video, "task_id":"0", "file":filename})



def search(request):
    # filename = request.GET["filename"]
    # VID_PATH = "media/video/"+filename
    # vid = cv2.VideoCapture(VID_PATH)
    # fps = int(vid.get(cv2.CAP_PROP_FPS))
    # length = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    df = pd.read_csv("media/out.csv",index_col=False,names=['id','Vehicle Type','B','G','R',"Entry","Exit","Image URL"])
    df.drop('id', axis=1, inplace=True)
    # df = df.to_html(escape=False, render_links=True)

    # df = HTML(df).data
    # return HttpResponse(df)
    df = create_table(df)
    return render(request,'search.html',{"data":df, "frames":no_of_frames[0], "fps":no_of_frames[1]})
    # return HttpResponse("Done!")

def closest_colour(requested_colour):
    x = dict([('ffffff','White'),('000000','Black'),('646464','Silver'),('d75656','Red'),('3d66e0','Blue'),('3e19a42','Peach'),
         ('ffff40','Yellow'),('04a500','Green'),('ff8c00','Orange')])
    min_colours = {}
    for key, name in x.items():
        temp = [key[i:i+2] for i in range(0, len(key), 2)]
        r_c = int(temp[0],16)
        g_c = int(temp[1],16)
        b_c = int(temp[2],16)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    closest_name = closest_colour(requested_colour)
    return closest_name

def create_table(df):
    res ='<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th></th>\n      <th>Vehicle Type</th>\n      <th>Start</th>\n      <th>End</th>\n      <th>Color</th>\n  <th>Color Name</th>\n      <th>Preview</th>\n    </tr>\n  </thead>\n  <tbody>\n'
    for i in range(len(df)):
        res = res + '\t<tr>\n'
        res = res+'\t\t<td>'+str(i)+'</td>\n'
        res = res+'\t\t<td>'+(df.loc[i,'Vehicle Type'])+'</td>\n'    
    #     res = res+'\t\t<td>'+(df.loc[i,'Vehicle Type'])+'</td>\n'
        res = res+'\t\t<td>'+str( round(df.loc[i,'Entry'],2)) +'</td>\n'
        res = res+'\t\t<td>'+str( round(df.loc[i,'Exit'],2)) +'</td>\n'
        r = df.loc[i, 'R']     
        g = df.loc[i, 'G']
        b = df.loc[i, 'B']

        if r>(g+15) and r>(b+15) and (g<200 and b<200) and (2*r-g-b)>30 :
            r=r+24
            g=g-10
            b=b-10
        if g>(b+15) and g>(r+15) and (b<200 and r<200) and (2*g-b-r)>30 :
            g=g+24
            r=r-10
            b=b-10
        if b>(r+15) and b>(g+15) and (r<200 and g<200) and (2*b-r-g)>30 :
            b=b+24
            g=g-10
            r=r-10
        cc = str(r) + ',' + str(g) + ',' + str(b)
    #     print(cc)
        res = res + '<td><div style="width: 50px;height: 50px;background-color:rgb('+cc+'); border: solid black 3px; border-radius: 30px;"></div></td>\n'
        res = res + '\t\t<td>'+ get_colour_name((r,g,b)) + '</td>\n'
        res = res+'\t\t<td><img src=\'/media/result/'+str(i)+'.jpg\'></img></td>\n'
        res = res + '\t</tr>\n'
    res = res + '</tbody> </table> \n'
    return res