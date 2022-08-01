import cv2 
import logging
# from matplotlib import pyplot as plt 
import numpy as np

class EggCounter():
    def __init__(self):
        logging.info('EggCounter::__init__')

    def find_stick(self, img):
        disp = False # setting to True creates intermediate debug displays 

        # convert to HSV
        img_ = img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # from BGR to HSV
        if disp:
            img = img.copy()
            cv2.imwrite("ws/fs-1-hsv.jpg", img[:, :, 0] / 255)

        # detect edges
        img = cv2.blur(img, (5,5)) # we can have some funny regions if not
        img = cv2.Canny(img,40,45)
        if disp:
            cv2.imwrite("ws/fs-2-canny.jpg", img)

        # morph close
        for i in range(5):
            img = cv2.dilate(img, np.ones((10, 10), np.uint8)) 
            img = cv2.erode(img, np.ones((11, 11), np.uint8)) 
        if disp:
            cv2.imwrite("ws/fs-3-morph-close.jpg", img)
        
        # threshold
        img = cv2.blur(img, (15,15)) 
        _, img = cv2.threshold(img, 200,255,cv2.THRESH_BINARY)
        if disp:
            cv2.imwrite("ws/fs-4-thresh.jpg", img)
        
        # take bounding rect
        x,y,w,h = cv2.boundingRect(img) 
        img = cv2.rectangle(img_,(x,y),(x+w,y+h),(255,0,0),3)
        if disp:
            cv2.imwrite("ws/fs-5-rect.jpg", img)

        # crop
        img_stick = img_[y:y+h, x:x+w]
        if disp:
            cv2.imwrite("ws/fs-6-done.jpg", img_stick)

        return img_stick, (x,y,w,h)

    def count_eggs_single_thresh(self, img_stick, thresh_value):
        disp = False # setting to True creates intermediate debug displays 

        # create working copies
        src = img_stick.copy()
        outlines = img_stick.copy()
        if disp:
            cv2.imwrite("ws/ec-0-start.jpg", img_stick)


        # estimate parameters from stick width
        stick_width_px = src.shape[1]
        egg_length_px = 0.006 * stick_width_px
        min_egg_radius = egg_length_px * 1
        max_egg_radius = egg_length_px * 3
        max_egg_cluster_radius = egg_length_px * 12
        min_egg_area = np.pi * (min_egg_radius * min_egg_radius)
        max_egg_area = np.pi * (max_egg_radius * max_egg_radius)
        max_egg_cluster_area = np.pi * (max_egg_cluster_radius * max_egg_cluster_radius)

        # transform to gray scale
        gray = cv2.cvtColor(src, cv2.COLOR_RGBA2GRAY)

        # threshold
        _, threshold = cv2.threshold(gray, thresh_value, 255, cv2.THRESH_BINARY)
        if disp:
            cv2.imwrite("ws/ec-1-threshold.jpg", threshold)

        # find contours
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # colors for debug
        contours_color = [255, 0, 0]
        green = [0, 225, 0, 255]
        blue = [0, 0, 225, 200]
        red = [255, 0, 0, 200]
        gray_color = [200, 200, 200]

        if disp:
            cv2.circle(outlines, (20, 20), int(min_egg_radius), blue, 2, cv2.LINE_AA, 0)
            cv2.circle(outlines, (40, 20), int(max_egg_radius), red, 2, cv2.LINE_AA, 0)
            cv2.circle(outlines, (60, 20), int(max_egg_cluster_radius), gray_color, 2, cv2.LINE_AA, 0)

        dispRemote = True
        if disp:
            img_contours = img_stick.copy()
            img_contours_selected = img_stick.copy()

        # prepare mask for average value computation within contours
        mask = np.zeros(img_stick.shape[:2], np.uint8)

        # prepare arrays for egg candidates and detections
        singles_array = []
        clusters_array = []
        contours_object = []
        contours_kept = []
        singles_count = 0
        clusters_count = 0
        singles_total_area = 0
        clusters_total_area = 0
        
        # loop through all candidates
        for i in range(np.minimum(10000, len(contours))): 

            if disp:
                cv2.drawContours(img_contours, contours, i, contours_color, 1, 8, hierarchy, 100)

            # compute mean inside contour and discard if bigger than threshold
            cv2.drawContours(mask, contours, i, 255, -1)
            mean = cv2.mean(img_stick, mask=mask)
            mask = np.zeros(img_stick.shape[:2], np.uint8)
            if np.mean(mean[:3]) >= thresh_value :
                continue
            if disp:
                cv2.drawContours(img_contours_selected, contours, i, contours_color, 1, 8, hierarchy, 100)
                 
            contours_object.append(cv2.contourArea(contours[i]))
            contourMax = np.max(np.array(contours_object))
            if contourMax != cv2.contourArea(contours[i]):
                # draw contours 
                cnt = contours[i]
                rect_x, rect_y, rect_w, rect_h  = cv2.boundingRect(cnt)
                objects = cv2.drawContours(threshold, contours, i, contours_color, 1, 8, hierarchy, 100)
                
                if disp:
                    point1 = [rect_x - 5, rect_y - 5]   
                    point2 = [rect_x + rect_w + 5, rect_y + rect_h + 5]
                    if (hierarchy[0, i, 0] == -1 or hierarchy[0, i, 1] == -1 or hierarchy[0, i, 2] == -1 or hierarchy[0, i, 3] == -1):
                        cv2.rectangle(objects, point1, point2, green, 1, cv2.LINE_AA, 0)
                    else:
                        cv2.rectangle(objects, point1, point2, green, 3, cv2.LINE_AA, 0)
                
                # filter contours by shape, fit an ellipse (not always possible) to discard some candidates
                if len(contours[i]) > 4:
                    ((x,y), (a,b), theta) = cv2.fitEllipse(contours[i])
                    if b <= a*2:
                        continue

                # filter remaining contours by area
                if cv2.contourArea(contours[i]) <= min_egg_area: 
                    if disp: outlines = cv2.drawContours(outlines, contours, i, green, -1, cv2.LINE_8, hierarchy, 0)

                elif cv2.contourArea(contours[i]) > min_egg_area and cv2.contourArea(contours[i]) <= max_egg_area:
                    if disp: outlines = cv2.drawContours(outlines, contours, i, blue, -1, cv2.LINE_8, hierarchy, 0)
                    if dispRemote: contours_kept.append(contours[i].tolist())
                    singles_array.append(cv2.contourArea(contours[i]))
                    singles_count += 1

                elif cv2.contourArea(contours[i]) > max_egg_area and cv2.contourArea(contours[i]) <= max_egg_cluster_area:
                    if disp: outlines = cv2.drawContours(outlines, contours, i, red, -1, cv2.LINE_8, hierarchy, 0)
                    if dispRemote: contours_kept.append(contours[i].tolist())
                    clusters_array.append(cv2.contourArea(contours[i]))
                    clusters_count += 1
                else:
                    # if we're here, it seems the candidate is kept
                    if disp: outlines = cv2.drawContours(outlines, contours, i, gray_color, -1, cv2.LINE_8, hierarchy, 0)

        
        # final computations, use counts to calculate average single egg area, cluster area
        # this part is a modification of a part of MECVision
        for i in range(len(singles_array)): 
            singles_total_area += singles_array[i]
        
        singles_avg_area = 1
        if len(singles_array)  > 0:
            singles_avg_area = 1. * singles_total_area / len(singles_array) 
        if np.isnan(singles_avg_area): singles_avg_area = 0

        # calculate cluster area if not zero, append to total cluster area of image
        if clusters_count != 0:
            for i in range(len(clusters_array)):
                clusters_total_area += clusters_array[i]
    
        # calculate and convert to output formats
        if singles_avg_area > 0:
            singles_calculated = 1. * clusters_total_area / singles_avg_area
            if np.isnan(singles_calculated): singles_calculated = 0

        total_eggs = singles_count + singles_calculated

        if disp:
            cv2.imwrite("ws/ec-2-contours.jpg", img_contours)
            cv2.imwrite("ws/ec-3-contours-sel.jpg", img_contours_selected)
            cv2.imwrite("ws/ec-4-outlines.jpg", outlines)

        return {
            # 'outlines': outlines,
            'eggsSingle': singles_count,
            'eggsInClusters': singles_calculated,
            'eggsTotal': int(total_eggs),
            'contoursKept': contours_kept,
            'threshValue': thresh_value
        }

    def count_eggs(self, img_stick):
        # deprecated method to count eggs using a sweeping threshold 
        thresh_values = range(30, 100, 2)
        rets = []

        # run computation for each threshold
        for thresh_value in thresh_values:
            print(thresh_value, end=" ", flush=True)
            rets.append(self.count_eggs_single_thresh(img_stick, thresh_value))
        
        # find most stable region
        std_min = 1000
        std_min_index = -1
        stds = []
        cnts = []
        for i in range(2, len(thresh_values)-2, 1):
            std = np.std([ret["eggsTotal"] for ret in rets[i-2:i+3]])
            stds.append(std)
            cnts.append(str(thresh_values[i]) + ":"+ str(int(rets[i]["eggsTotal"])))
            if std < std_min:
                std_min = std 
                std_min_index = i
                
        return {
            'outlines': rets[std_min_index]["outlines"], # np.hstack([rets[i]["outlines"] for i in range(len(rets))]),
            'eggsSingle': rets[std_min_index]["eggsSingle"],
            'eggsInClusters': rets[std_min_index]["eggsInClusters"],
            'eggsTotal': rets[std_min_index]["eggsTotal"],
            'threshValue': thresh_values[std_min_index]
        } 