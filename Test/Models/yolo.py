from imageai import Detection
import os

execution_path = os.getcwd()

detector = Detection.ObjectDetection()
detector.setModelTypeAsTinyYOLOv3()
detector.setModelPath("./yolo-tiny.h5")
detector.loadModel()

custom_objects = detector.CustomObjects(car=True, motorcycle=True, person=True,  bicycle=True, bus=True, truck=True)
detections = detector.detectCustomObjectsFromImage(custom_objects=custom_objects, input_image=os.path.join(execution_path , "test2.jpg"), output_image_path=os.path.join(execution_path , "image3custom.jpg"), minimum_percentage_probability=30)

for eachObject in detections:
    print(eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] )
    print("--------------------------------")