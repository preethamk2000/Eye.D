# eye-dentify

Search for vehicles based on type, color and/or timestamps from several hours of CCTV footage with ease.

## Problem Statement

In a lot of situations (like theft, hit-and-run, smuggling) we would like to spot a paritcular vehicle based on some basic features from hours of CCTV footage. Watching hours of footage and identifying them is a tedious process.

Eye-dentify watches the footage for you and allows you to search for vehicles based on type, color and/or time it was spotted.

## Challenges faced 
- Trade-off between speed and accuracy : As we had decided to use YOLO for object detection, running the model for every frame would give high accuracy, but would slow down the proces. So, we decided to run the algorithm only for every 3 frames, so that we don't lose any object. Though some objects were spotted twice, no information was lost.
- Color Detection : Even after the objects were detected with bounding boxes from YOLO, color of the object couldn't be obtained through elementary methods as the background colors affected the result. So, we applied background subtraction and then k-means clustering on colors of pixels only on the contours found.