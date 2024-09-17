import math
from utils.scaleCoordinates import scale_coords

def intersect(gazePoint, boundingBoxes, graph):

    #iterate through all bounding boxes for this frame
    boxNum = 0
    for box in boundingBoxes:
        #get bounding box coordinates
        x1 = box[0] 
        y1 = box[1]
        x2 = box[2]
        y2 = box[3]

        center = [(x1+x2)/2, (y1+y2)/2]

        #convert to floats
        x1 = float(x1)
        x2 = float(x2)
        y1 = float(y1)
        y2 = float(y2)

        #iterate through all gaze point for this frame
        for x, y in zip(gazePoint.x, gazePoint.y):
            x, y = scale_coords(x, y, (3840, 1920), (5760, 2880))

            #check if gaze point is within bounding box
            if x1 < x and x < x2:
                if y1 < y and y < y2:
                    print("Intersection found at: " + str(x) + ", " + str(y))
                    print("Box ID: " + str(box["id"]))
                    distanceFromCenter = math.dist((x,y), center)
                   # print("BBox coords: " + str(x1) + " " + str(y1) +  " " +  str(x2) + " " + str(y2))
                   # print("Center" + str(center))
                   # print("Distance from center: " + str(distanceFromCenter))
                    graph.update(gazePoint.time, str(box["id"]))

        #next bounding box
        boxNum += 1

    print("Time: " + str(gazePoint.time))
                    

    
    