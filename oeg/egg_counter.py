import cv2 
import logging
# from matplotlib import pyplot as plt 
import numpy as np

class EggCounter():
    def __init__(self):
        logging.info('EggCounter::__init__')

    def find_stick(self, img):
        # equalize
        if False:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb) 
            img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
            img = cv2.cvtColor(img, cv2.COLOR_YCrCb2BGR) 

        # 
        img_ = img.copy()
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # from BGR to HSV
        img = cv2.blur(img, (5,5)) # We can have some funny regions if not
        img = cv2.Canny(img,40,45)
        for i in range(5):
            img = cv2.dilate(img, np.ones((10, 10), np.uint8)) 
            img = cv2.erode(img, np.ones((11, 11), np.uint8)) 
        img = cv2.blur(img, (15,15)) # We can have some funny regions if not
        _, img = cv2.threshold(img, 200,255,cv2.THRESH_BINARY)
        
        x,y,w,h = cv2.boundingRect(img) # Not robust to isolated detection
        # img = cv2.rectangle(img_,(x,y),(x+w,y+h),(255,0,0),3)
        img_stick = img_[y:y+h, x:x+w]

        return img_stick, (x,y,w,h)

    def count_eggs_single_thresh(self, img_stick, threshValue):
        src = img_stick.copy()
        outlines = img_stick.copy()

        # estimate parameters from stick width
        stick_width_px = src.shape[1]
        egg_length_px = 0.006 * stick_width_px
        minEggRadius = egg_length_px * .8
        maxEggRadius = egg_length_px * 3
        maxEggCluster = egg_length_px * 5

        logging.debug("stick width (px): %d" % stick_width_px)
        logging.debug("stick is approx 15mm wide, egg is approx .5mm long")
        logging.debug("egg length (px): %d " % egg_length_px)
        logging.debug("params: %d, %d, %d " % (minEggRadius, maxEggRadius, maxEggCluster))

        
        # TRANSFORMATIONS
        # Source to Grayscale
        gray = cv2.cvtColor(src, cv2.COLOR_RGBA2GRAY)

        # Grayscale to Threshold (binary, not adaptive)
        _, threshold = cv2.threshold(gray, threshValue, 255, cv2.THRESH_BINARY)

        # Threshold to Dilate [and erode](create new matrix that can be written upon and anchor point (center))
        dilate = cv2.dilate(threshold, np.ones((3, 3), np.uint8))

        # DRAW CONTOURS
        # Create matrices to hold contour counts
        # Find contours
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # CALCULATE SINGLE EGGS AND CLUSTERS
        # Initialize and/or reset single and cluster arrays, counts, and area placeholders for computation
        detectedObjectsArray = []
        singlesArray = []
        clustersArray = []
        singlesCount = 0
        clustersCount = 0
        singlesTotalArea = 0
        clustersTotalArea = 0

        # Define colors for contour object detection (boxes) and contour overlay (green=small, blue=single-egg, red=cluster)
        contoursColor = [255, 255, 255]
        green = [0, 225, 0, 255]
        blue = [0, 0, 225, 200]
        red = [255, 0, 0, 200]
        grayColor = [200, 200, 200]
        color_cyan = [0, 255, 255]
        minEggArea = np.pi * (minEggRadius * minEggRadius)
        maxEggArea = np.pi * (maxEggRadius * maxEggRadius)
        maxClusterArea = np.pi * (maxEggCluster * maxEggCluster)

        cv2.circle(outlines, (20, 20), int(minEggRadius), blue, 2, cv2.LINE_AA, 0)
        cv2.circle(outlines, (40, 20), int(maxEggRadius), red, 2, cv2.LINE_AA, 0)
        cv2.circle(outlines, (60, 20), int(maxEggCluster), grayColor, 2, cv2.LINE_AA, 0)

        # Main loop
        # Max 1000 eggs here
        disp = False
        dispRemote = True
        contoursObject = []
        # print(threshValue, len(contours))
        contoursKept = []
        for i in range(np.minimum(2500, len(contours))): 
            contoursObject.append(cv2.contourArea(contours[i]))
            # print(np.array(contoursObject))
            contourMax = np.max(np.array(contoursObject))
            if contourMax != cv2.contourArea(contours[i]):
                # Draw contours and bounding boxes for all objects detected from 'contours' matrix
                cnt = contours[i]
                rect_x, rect_y, rect_w, rect_h  = cv2.boundingRect(cnt)
                objects = cv2.drawContours(dilate, contours, i, contoursColor, 1, 8, hierarchy, 100)
                point1 = [rect_x - 5, rect_y - 5]
                point2 = [rect_x + rect_w + 5, rect_y + rect_h + 5]
                
                if disp:
                    if (hierarchy[0, i, 0] == -1 or hierarchy[0, i, 1] == -1 or hierarchy[0, i, 2] == -1 or hierarchy[0, i, 3] == -1):
                        cv2.rectangle(objects, point1, point2, green, 1, cv2.LINE_AA, 0)
                    else:
                        cv2.rectangle(objects, point1, point2, green, 3, cv2.LINE_AA, 0)

                # Create matrix for points of objects for all objects, even if not calculated immediately (until individual boxes invoked)
                boundingBoxes = src[rect_y:rect_y+rect_h, rect_x:rect_x+rect_w]
                detectedObjectsArray.append(boundingBoxes)
                
                # filter contours by shape, fit an ellipse (not always possible) to discard some contours
                if len(contours[i]) > 4:
                    ((x,y), (a,b), theta) = cv2.fitEllipse(contours[i])
                    # outlines = cv2.ellipse(outlines, ((x,y), (a,b), theta), color_cyan, 1)
                    if b <= a*2:
                        continue

                # filter remaining contours by area
                if cv2.contourArea(contours[i]) <= minEggArea: 
                    if disp: outlines = cv2.drawContours(outlines, contours, i, green, -1, cv2.LINE_8, hierarchy, 0)

                elif cv2.contourArea(contours[i]) > minEggArea and cv2.contourArea(contours[i]) <= maxEggArea:
                    if disp: outlines = cv2.drawContours(outlines, contours, i, blue, -1, cv2.LINE_8, hierarchy, 0)
                    if dispRemote: contoursKept.append(contours[i].tolist())
                    singlesArray.append(cv2.contourArea(contours[i]))
                    singlesCount += 1

                elif cv2.contourArea(contours[i]) > maxEggArea and cv2.contourArea(contours[i]) <= maxClusterArea:
                    if disp: outlines = cv2.drawContours(outlines, contours, i, red, -1, cv2.LINE_8, hierarchy, 0)
                    if dispRemote: contoursKept.append(contours[i].tolist())
                    clustersArray.append(cv2.contourArea(contours[i]))
                    clustersCount += 1
                else:
                    if disp: outlines = cv2.drawContours(outlines, contours, i, grayColor, -1, cv2.LINE_8, hierarchy, 0)

        
        # CALCULATIONS
        # Use array counts to calculate single size averages, single size area, cluster average, and cluster area
        for i in range(len(singlesArray)): 
            singlesTotalArea += singlesArray[i]
        
        singlesAvg = 1
        if len(singlesArray)  > 0:
            singlesAvg = 1. * singlesTotalArea / len(singlesArray) 

        if np.isnan(singlesAvg): singlesAvg = 0

        # Calculate cluster area if not zero, append to total cluster area of image
        if clustersCount != 0:
            for i in range(len(clustersArray)):
                clustersTotalArea += clustersArray[i]
    
        # Calculate and convert to output formats
        if singlesAvg > 0:
            singlesCalculated = 1. * clustersTotalArea / singlesAvg
            if np.isnan(singlesCalculated): singlesCalculated = 0

        if clustersCount > 0:
            avgClusterArea = 1. * clustersTotalArea / clustersCount
            if np.isnan(avgClusterArea): avgClusterArea = 0

        if singlesAvg > 0 and clustersCount > 0:
            avgEggsPerCluster = 1. * avgClusterArea / singlesAvg
            if np.isnan(avgEggsPerCluster): avgEggsPerCluster = 0

        totalEggs = singlesCount + singlesCalculated



        return {
            # 'outlines': outlines,
            'eggsSingle': singlesCount,
            'eggsInClusters': singlesCalculated,
            'eggsTotal': int(totalEggs),
            'contoursKept': contoursKept,
            'threshValue': threshValue
        }

    def count_eggs(self, img_stick):
        threshValues = range(30, 100, 2)
        rets = []

        # run computation for each threshold
        
        for threshValue in threshValues:
            print(threshValue, end=" ", flush=True)
            rets.append(self.count_eggs_single_thresh(img_stick, threshValue))
        
        # find most stable region
        std_min = 1000
        std_min_index = -1
        stds = []
        cnts = []
        for i in range(2, len(threshValues)-2, 1):
            std = np.std([ret["eggsTotal"] for ret in rets[i-2:i+3]])
            stds.append(std)
            cnts.append(str(threshValues[i]) + ":"+ str(int(rets[i]["eggsTotal"])))
            if std < std_min:
                std_min = std 
                std_min_index = i
        # plt.plot(cnts, stds)
        # plt.show()
        return {
            'outlines': rets[std_min_index]["outlines"], # np.hstack([rets[i]["outlines"] for i in range(len(rets))]),
            'eggsSingle': rets[std_min_index]["eggsSingle"],
            'eggsInClusters': rets[std_min_index]["eggsInClusters"],
            'eggsTotal': rets[std_min_index]["eggsTotal"],
            'threshValue': threshValues[std_min_index]
        } 