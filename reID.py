import random
import string
import numpy as np
import math

class Object:
    _id_counter = 1  # Class variable to keep track of the ID counter
     
     
    def __init__(self, bbox) :
        self.bbox = bbox
        #self.initial_time = time
        #self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.id = Object._id_counter
        Object._id_counter += 1
        self.detected_this_frame = False
        self.not_detected_for = 0
        self.new = True
    
    def update(self, bbox, time):
        self.bbox = bbox
        self.not_detected_for = 0
        self.detected_this_frame = True
        #self.time = time

    def increase_undetected_time(self):
        self.not_detected_for += 1

    def get_bbox(self):
        return self.bbox
    
    def get_undetected_time(self):
        return self.not_detected_for
    
    def get_detected_this_frame(self):
        if self.detected_this_frame or self.new:
            self.detected_this_frame = False
            self.new = False
            return True
        else:
            return False
        
    def get_id(self):
        return self.id
    
    def set_hsv(self, hsv):
        self.hsv = hsv

    def get_hsv(self):
        return self.hsv
    
    

class ReID:
    def __init__(self, time_threshold = 500):
        self.objects = []
        self.waiting_objects = []
        self.time_threshold = time_threshold
        self.object_count = 0
        self.thresholds = [.375, .375, .375 * 2, .375 * 2.75, .375, .375] #dX, dY, dW, dH, dCX, dCY
        self.threshold_total = [.375, .375, .375 * 2, .375 * 2.75, .375, .375]

    #Add newly tracked object to the ReID list
    def add(self, bbox) : 
        object = Object(bbox)
        self.objects.append(object)
        return object

    #Add undetected object to the waiting list to be reidentified later
    def to_waiting(self, object) :
        self.waiting_objects.append(object)
        self.objects.remove(object)

    #Add reidentified object to the detected list
    def to_detected(self, object) :
        self.objects.append(object)
        self.waiting_objects.remove(object)

    def get_objects(self):
        return self.objects
    
    def get_waiting_objects(self):
        return self.waiting_objects
    
    def get_time_threshold(self):
        return self.time_threshold
    
    def remove(self, object):
        self.waiting_objects.remove(object)

    def update_thresholds(self, newThresholds):
        self.object_count += 1
       # dX, dY, dW, dH, dCX, dCY = newThresholds
        self.threshold_total = [x + y for x, y in zip(self.threshold_total, newThresholds)]
        self.thresholds = [x / self.object_count for x in self.threshold_total]

        #self.thresholds[0] = (dX + self.thresholds[0]) / self.object_count
        #self.thresholds[1] = (dY + self.thresholds[1]) / self.object_count
        #self.thresholds[2] = (dW + self.thresholds[2]) / self.object_count
        #self.thresholds[3] = (dH + self.thresholds[3]) / self.object_count
        #self.thresholds[4] = (dCX + self.thresholds[4]) / self.object_count
        #self.thresholds[5] = (dCY + self.thresholds[5]) / self.object_count




def convert_coordinates(bbox):
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1
    return x1, y1, w, h

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        

def isSameObject(reid, obj, bbox, hsvThreshold = 50) :

    bbox1 = obj.get_bbox()
    bbox2 = bbox


    #Bounding box coordinates
    x1, y1, w1, h1 = convert_coordinates(bbox1[:4])
    x2, y2, w2, h2 = convert_coordinates(bbox2[:4])

    #Change in size
    dX = abs(x1 - x2) / max(w1, w2)
    dY = abs(y1 - y2) / max(h1, h2)
    dW = abs(w1 - w2) / w1
    dH = abs(h1 - h2) / h1

    dXNonAbs = (x1 - x2) / max(w1, w2)
    dYNonAbs = (y1 - y2) / max(h1, h2)
    dWNonAbs = (w1 - w2) / w1
    dHNonAbs = (h1 - h2) / h1

    #Center of bounding boxes
    cx1 = x1 + w1/2
    cy1 = y1 + h1/2
    cx2 = x2 + w2/2
    cy2 = y2 + h2/2

    #Change in location
    dCX = abs(cx1 - cx2) / max(w1, w2)
    dCY = abs(cy1 - cy2) / max(h1, h2)

    dCXNonAbs = (cx1 - cx2) / max(w1, w2)
    dCYNonAbs = (cy1 - cy2) / max(h1, h2)
  
    #compare color features
    #dist = np.linalg.norm(compareHSV - obj.get_hsv())

    #increase color threshold if object is not detected for a long time
    if obj.get_undetected_time() > 2:
        hsvThreshold = 100

    
    if (dX <= reid.thresholds[0] and dY <= reid.thresholds[1] and dW <= reid.thresholds[2] and dH <= reid.thresholds[3] and dCX <= reid.thresholds[4] and dCY <= reid.thresholds[5]) :
        reid.update_thresholds([dXNonAbs + reid.thresholds[0], dYNonAbs + reid.thresholds[1], dWNonAbs + reid.thresholds[2], dHNonAbs + reid.thresholds[3], dCXNonAbs + reid.thresholds[4], dCYNonAbs + reid.thresholds[5]])
        return True
    else:
        return False
    #return (dX <= threshold and dY <= threshold and dW <= threshold * 2 and dH <= threshold * 2.75 and dCX <= threshold and dCY <= threshold)

