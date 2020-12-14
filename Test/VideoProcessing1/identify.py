import os
import numpy as np
import cv2
import time as tm
import argparse
from imageai import Detection
from scipy.stats import itemfreq
import csv
from utils import *

execution_path = os.getcwd()
VID_PATH = "./trial2.mp4"
MODEL_PATH = "../Models/yolo-tiny.h5"
CONTINUITY_THRESHOLD = 8 #For cutting out boxes

MIN_SECONDS = 1 # (seconds) Minimum duration of a moving object
INTERVAL_BW_DIVISIONS = 5 # (seconds) For distributing moving objects over a duration to reduce overlapping.
GAP_BW_DIVISIONS = 1.5 #(seconds)
FRAMES_PER_DETECTION = 3

fgbg = cv2.createBackgroundSubtractorKNN()

detector = Detection.ObjectDetection()
detector.setModelTypeAsTinyYOLOv3()
detector.setModelPath(MODEL_PATH)
detector.loadModel()
custom_objects = detector.CustomObjects(car=True, motorcycle=True, person=True,  bicycle=True, bus=True, truck=True)

vid = cv2.VideoCapture(VID_PATH)
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
        print(ind//FRAMES_PER_DETECTION, end=' ', flush=True)
        all_conts.append(np.array(conts))
        all_types.append(types)
        masks.append(fgmask)
#         cv2.imshow('frame', detected_image_array)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
    ind += 1
masks = np.array(masks)
frames = np.array(frames)
print("--- %s seconds ---" % (tm.time() - start_time))
vid.release()
# cv2.destroyAllWindows()

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
print("Done", end=' ')

#Removing objects that occur for a very small duration

MIN_FRAMES = MIN_SECONDS*(fps//3)

moving_objs = [obj for obj in moving_objs if (obj.boxes[-1].time-obj.boxes[0].time)>=MIN_FRAMES]
print(len(moving_objs))

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
#             cv2.imwrite('./test/'+str(i)+'_'+str(g)+'.jpg', frames[rect.time, y:y+h, x:x+w])
        if(rect.type not in otype): otype[rect.type] = 0;
        otype[rect.type] += 1
        g += 1
    moving_objs[i].type = max(otype, key=otype.get)
    rect = boxes[mx_i]
    x,y,w,h = map(int, list(rect.coords))
    cv2.imwrite('./result/'+str(i)+'.jpg', frames[rect.time, y:y+h, x:x+w])
    ret,thresh = cv2.threshold(masks[rect.time],1,255,cv2.THRESH_BINARY)
    cv2.imwrite('./result/a'+str(i)+'.jpg', thresh[y:y+h, x:x+w])
    moving_objs[i].img = frames[rect.time, y:y+h, x:x+w]    
    moving_objs[i].mask = thresh[y:y+h, x:x+w]
    moving_objs[i].color = findColor(moving_objs[i].img, moving_objs[i].mask)

    
SECONDS_PER_3FRAME = FRAMES_PER_DETECTION/fps
with open('out.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for i,obj in enumerate(moving_objs):
        writer.writerow([i, obj.type, obj.color[0], obj.color[1], obj.color[2], 
                         obj.boxes[0].time*SECONDS_PER_3FRAME,
                         obj.boxes[-1].time*SECONDS_PER_3FRAME
                        ])