# Eye-dentify

Search for vehicles based on type, color and/or timestamps from several hours of CCTV footage with ease.

## Object Detection

We have used the *imageai* library for implementing the YOLO algorithm to retrieve bounding boxes from the image. The *yolo-tiny* pre-trained model has been used to save computation time. The model is run only for every 3 frames (as it takes approximately 0.5 seconds for each detection when run on CPU). A sample output for a frame is shown below. 

<p align="center"><img src="./images/imageai.jpg" width="70%"> </p>

## Object Tracking

The centroid tracking algorithm has been employed to track objects from the bounding boxes returned by the YOLO model. The algorithm basically maps each box in the current frame with some box from the previous frame if they are close enough and the older box is recent enough, or creates a new object. We also filter out noise by removing objects which was tracked for less than a second. The example below shows an object being tracked.

<p align="center"><img src="./images/track.gif" width="70%"> </p>

As the object is tracked, we have a lot of boxes for an object. The box with the maximum area is considered as the key image for that object.

## Color Dectection

In order to first isolate the object from it's key image, we apply background subtraction on the video and find contours. We then apply *k-means clustering* on the colors of pixels present only inside the contour to find the most dense colors with just two clusters. Since all the cars have a dark portion of a windshield and tyres, from the two color-centers obtained, the lighter one is chosen. Some results of color detection are shown below :

<p align="center"><img src="./images/color1.jpg" width="70%"> </p>
<p align="center"><img src="./images/color2.jpg" width="70%"> </p>

## Sample Result