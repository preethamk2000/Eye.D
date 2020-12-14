# Eye.D

Search for moving objects based on type, color and/or timestamps from several hours of CCTV footage with ease.

## Problem Statement

>Inspired from this [project](https://github.com/eonr/cctv-recap).

In a lot of situations (like theft, hit-and-run, smuggling) we would like to spot a particular vehicle based on some basic features from hours of CCTV footage. Watching hours of footage and identifying them is a tedious process and there aren't a lot of easily configurable **open-source** solutions avaliable out there which have a decent front-end with search options, so we developed Eye.D.

Eye.D watches the footage for you and allows you to search for vehicles based on type, color and/or the time range it was spotted via a dynamic front-end.

## Challenges faced 
- Trade-off between speed and accuracy : As we had decided to use YOLO for object detection, running the model for every frame would give high accuracy, but would slow down the proces. So, we decided to run the algorithm only for every 3 frames, so that we don't lose any object. Though some objects were spotted twice, no information was lost.
- Color Detection : Even after the objects were detected with bounding boxes from YOLO, color of the object couldn't be obtained through elementary methods as the background colors affected the result. So, we applied background subtraction and then k-means clustering on colors of pixels only on the contours found.
- Asynchronous function calls for executing our model was needed since it is a time consuming process for proper updation of progress bar in the front-end. We used Celery and RabbitMQ for the message queue handling, but tensorflow functions caused a lot of problems. After a lot of searching, and experimenting with lot of stuff with packages and versions, we finally downgraded the tensorflow to version ```1.4.0``` and finally made it work.