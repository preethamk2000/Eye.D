import numpy as np
import cv2

def get_centres(p1):
    return np.transpose(np.array([p1[:,0] + p1[:,2]/2, p1[:,1] + p1[:,3]/2]))

def distance(p1, p2):
    p1 = np.expand_dims(p1, 0)
    if p2.ndim==1:
        p2 = np.expand_dims(p2, 0)
        
    c1 = get_centres(p1)
    c2 = get_centres(p2)
    return np.linalg.norm(c1 - c2, axis=1)

def get_nearest(p1, points):
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
    
def showImg(img):
    cv2.imshow("frame",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()  

def showColor(c):
    color = np.ones((100,100,3))
    for i in range(3):
        color[:,:,i] = color[:,:,i]*(c[i])/255
    showImg(color)

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