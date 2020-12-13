#!/usr/bin/env python
# coding: utf-8

# # EyeSpy

# In[ ]:


import os
import numpy as np
import cv2
import time as tm
import argparse
from imageai import Detection
from scipy.stats import itemfreq
import csv


execution_path = os.getcwd()
VID_PATH = './demos/trial1.mp4'
CONTINUITY_THRESHOLD = 8 #For cutting out boxes

MIN_SECONDS = 1 # (seconds) Minimum duration of a moving object
INTERVAL_BW_DIVISIONS = 5 # (seconds) For distributing moving objects over a duration to reduce overlapping.
GAP_BW_DIVISIONS = 1.5 #(seconds)
FRAMES_PER_DETECTION = 3


fgbg = cv2.createBackgroundSubtractorKNN()

detector = Detection.ObjectDetection()
detector.setModelTypeAsTinyYOLOv3()
detector.setModelPath("./yolo-tiny.h5")
detector.loadModel()
custom_objects = detector.CustomObjects(car=True, motorcycle=True, person=True,  bicycle=True, bus=True, truck=True)


# ## Detection on video

def videoAnalyze(video_url):
    vid = cv2.VideoCapture(video_url)
    fps = int(vid.get(cv2.CAP_PROP_FPS))
    frames = []
    masks = []
    ind = 0
    start_time = tm.time()
    all_conts = []
    all_types = []
    avg2 = None
    while(vid.isOpened()):
        
        # Background Extraction
        if(avg2 != None): cv2.accumulateWeighted(frame, avg2, 0.01)
        ret,frame = vid.read()
        if(not ret): break;
        
        if(avg2): avg2 = np.float32(frame)
        fgmask = fgbg.apply(frame)
        
        # Running detection for every FRAMES_PER_DETECTION
        if(ind%FRAMES_PER_DETECTION == 0):
            frames.append(frame)
            detected_image_array, detections = detector.detectCustomObjectsFromImage(
                input_type="array",
                output_type='array',
                custom_objects=custom_objects,
                input_image=frame, 
                minimum_percentage_probability=50
            )
            types = []; conts = []
            for eachObject in detections:
                rect = eachObject["box_points"]
                conts.append(np.array([rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]]))
                types.append(eachObject["name"])
            print(ind//FRAMES_PER_DETECTION, end=' ')
            all_conts.append(np.array(conts))
            all_types.append(types)
            masks.append(fgmask)
            # cv2.imshow('frame', fgmask)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        ind += 1
    masks = np.array(masks)
    frames = np.array(frames)
    print("--- %s seconds ---" % (tm.time() - start_time))
    vid.release()
    cv2.destroyAllWindows()


    # ## Object tracking 
    #old - boxes in the previous frame
    #new - boxes in the current frame


    moving_objs = []

    for curr_time, new_boxes in enumerate(all_conts): #iterating over frames
        if len(new_boxes) != 0: #if not empty
            new_assocs = [None]*len(new_boxes) #all new boxes initially are not associated with any moving_objs
            obj_coords = np.array([obj.last_coords() for obj in moving_objs if obj.age(curr_time)<CONTINUITY_THRESHOLD])
            unexp_idx = -1 #index of unexpired obj in moving_objs
            for obj_idx, obj in enumerate(moving_objs):
                if obj.age(curr_time) < CONTINUITY_THRESHOLD: #checking only unexpired objects
                    unexp_idx += 1
                    nearest_new, dst1 = get_nearest(obj.last_coords(), new_boxes) #nearest box to obj
                    nearest_obj, dst = get_nearest(new_boxes[nearest_new], obj_coords) #nearest obj to box

                    if nearest_obj==unexp_idx: #both closest to each-other
                        #associate
                        if(dst < 100):
                            new_assocs[nearest_new] = obj_idx
        
        
        for new_idx, new_coords in enumerate(new_boxes):
            new_assoc = new_assocs[new_idx]
            new_box = box(new_coords, curr_time, all_types[curr_time][new_idx])

            if new_assoc is not None: 
                #associate new box to moving_obj
                moving_objs[new_assoc].add_box(new_box)
            else: 
                #add a fresh, new moving_obj to moving_objs
                new_moving_obj = moving_obj(new_box)
                moving_objs.append(new_moving_obj)
    print("Done")


    #Removing objects that occur for a very small duration

    MIN_FRAMES = MIN_SECONDS*(fps//3)

    moving_objs = [obj for obj in moving_objs if (obj.boxes[-1].time-obj.boxes[0].time)>=MIN_FRAMES]
    len(moving_objs)


    # ## Displaying result for an object

    # In[ ]:


    # IND = 27
    # boxes = moving_objs[IND].boxes
    # outv = frames.copy()
    # for rect in boxes:
    #     x,y,w,h = map(int, list(rect.coords))
    #     cv2.rectangle(outv[rect.time], (x,y), (x+w,y+h), (0,255,0), 2)
    # out = cv2.VideoWriter('out_summary.avi',cv2.VideoWriter_fourcc(*'DIVX'), 30, (800,480))
    # for frame in outv:
    #     cv2.imshow('Video summary',frame)
    #     out.write(frame)
    #     tm.sleep(0.01)
    #     if cv2.waitKey(1) & 0xFF == ord("q"):
    #         break
    # #     tm.sleep(1/30) #TODO: FPS
    # out.release()
    # cv2.destroyAllWindows()


    # ## Color Detection

    # In[ ]:


    # Viewing contours detected
    # for frame in masks:
    #     ret,thresh1 = cv2.threshold(frame,1,255,cv2.THRESH_BINARY)
    #     cv2.imshow('frame', thresh1)
    #     tm.sleep(0.01)
    #     if cv2.waitKey(1) & 0xFF == ord("q"):
    #         break
    # cv2.destroyAllWindows()


    # ### Testing findColor for an image

    # In[ ]:


    # IND = 1
    # img = cv2.imread("./result/"+str(IND)+".jpg")
    # mask = cv2.imread("./result/a"+str(IND)+".jpg",0)
    # showImg(img)

    # color = findColor(img, mask)
    # showColor(color)


    # ## Exporting output

    # In[ ]:
    for i,obj in enumerate(moving_objs):
        boxes = obj.boxes
        g = 0
        mx = 0
        otype = {}
        for rect in boxes:
            x,y,w,h = map(int, list(rect.coords))
            area = w*h
            if(area > mx):
                mx = area
                mx_i = g
                cv2.imwrite('./test/'+str(i)+'_'+str(g)+'.jpg', frames[rect.time, y:y+h, x:x+w])
            if(rect.type not in otype): otype[rect.type] = 0;
            otype[rect.type] += 1
            g += 1
    moving_objs[i].type = max(otype, key=otype.get)
    rect = boxes[mx_i]
    x,y,w,h = map(int, list(rect.coords))
    # cv2.imwrite('./result/'+str(i)+'.jpg', frames[rect.time, y:y+h, x:x+w])
    ret,thresh = cv2.threshold(masks[rect.time],1,255,cv2.THRESH_BINARY)
    # cv2.imwrite('./result/a'+str(i)+'.jpg', thresh[y:y+h, x:x+w])
    moving_objs[i].img = frames[rect.time, y:y+h, x:x+w]    
    moving_objs[i].mask = thresh[y:y+h, x:x+w]
    moving_objs[i].color = findColor(moving_objs[i].img, moving_objs[i].mask)

    SECONDS_PER_3FRAME = 3/fps
    with open('out.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for i,obj in enumerate(moving_objs):
            writer.writerow([i, obj.type, str(obj.color), 
                         obj.boxes[0].time*SECONDS_PER_3FRAME,
                         obj.boxes[-1].time*SECONDS_PER_3FRAME
                        ])

def showImg(img):
    cv2.imshow("frame",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()  

def showColor(c):
    color = np.ones((100,100,3))
    for i in range(3):
        color[:,:,i] = color[:,:,i]*(c[i])/255
    showImg(color)


# In[ ]:


def findColor(img, mask):
    car = []
    X,Y,_ = img.shape
    for x in range(X):
        for y in range(Y):
            if(not mask[x,y]): continue;
            car.append(img[x,y,:])
    car = np.float32(np.array(car))

    # number of clusters
    n_colors=2

    #number of iterations
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)

    #initialising centroid
    flags = cv2.KMEANS_RANDOM_CENTERS

    #applying k-means to detect prominant color in the image
    _, labels, centroids = cv2.kmeans(car, n_colors, None, criteria, 10, flags)

    # i = np.argmax(np.unique(labels, return_counts=True)[1])
    i = np.argmax(np.sum(centroids, 1))
    return(centroids[i])

def get_centres(p1):
    return np.transpose(np.array([p1[:,0] + p1[:,2]/2, p1[:,1] + p1[:,3]/2]))


# In[ ]:


def distance(p1, p2):
    p1 = np.expand_dims(p1, 0)
    if p2.ndim==1:
        p2 = np.expand_dims(p2, 0)
        
    c1 = get_centres(p1)
    c2 = get_centres(p2)
    return np.linalg.norm(c1 - c2, axis=1)

def get_nearest(p1, points):
    """returns index of the point in *points* that is closest to p1"""
    return np.argmin(distance(p1, points)), np.min(distance(p1, points))


class box:
    def __init__(self, coords, time, otype):
        self.coords = coords #coordinates
        self.time   = time #nth frame/time
        self.type   = otype
        
class moving_obj:
    def __init__(self, starting_box):
        self.boxes = [starting_box]
        self.type = None
        self.img = None
        self.mask = None
        self.color = None
        
    def add_box(self, box):
        self.boxes.append(box)
    
    def last_coords(self):
        return self.boxes[-1].coords
    
    def age(self, curr_time):
        last_time = self.boxes[-1].time
        return curr_time - last_time   


videoAnalyze('trial1.mp4')