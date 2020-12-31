## Dev Setup Instructions:

> Done in Python 3.6.9

First switch to a venv if needed. Next,

```
pip install -r requirements.txt
```

> Note: For Linux users you need to install:
> ```
> apt install libsm6 libxext6 libxrender-dev
> ```
> This is related to some display libraries.
> There is also a headless opencv-python library but we've not yet tested with that. 

Then install docker for easy usage of RabbitMQ.

Final minor changes:

1. Then change the BASE IP address/URL in files like:
the HTML files - ```templates/(index.html,search.html)```, ```tasks.py```
or just declare a constant in settings.py and use it. [Refer Here](https://stackoverflow.com/questions/33498328/how-to-define-constants-in-settings-py-and-access-them-in-views-function-in-djan)

2. Uncomment the csrf token ( line : 27 ) in index.html (For authorization)

> Note: Due to the fact that the video processing runs in the celery task worker, there were a lot of issues with tensorflow, keras and ImageAI version with the worker. So, a small error which was needed to be fixed for **Linux Users** is:
>
> Go to where the keras library is installed probably in the /usr/... to the keras/engine directory and in the ```saving.py``` file, go to lines around 1000 - 1015 inside the ```load_weights_from_hdf5_group()``` function and remove the ```.decode('utf-8')``` functions as they will cause errors in the celery worker.
>
> These errors have been fixed by keras in their later versions, but we are constrainted to use this.
---
Now, we can start running the setup.

First start the RabbitMQ docker container
```
docker run -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management
```

Go to the root Django directory and start the celery worker.

```
celery -A eyespy worker -l INFO
```

Next, do
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Finally, start the dev server:

```
python manage.py runserver
```