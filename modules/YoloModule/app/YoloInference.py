#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

import cv2
#import cv2.cv as cv
import numpy as np
import time
import os

yolocfg  = r'yolo/yolov3-tiny.cfg'
yoloweight = r'yolo/yolov3-tiny.weights'
classesFile = r'yolo/coco.names'

class YoloInference(object):

    def __init__(
            self,
            fontScale = 1.0):

        print("YoloInference::__init__()")
        print("===============================================================")
        print("Initialising Yolo Inference with the following parameters: ")
        print("")

        self.classLabels = None
        self.colors = None
        self.nmsThreshold = 0.35
        self.fontScale = float(fontScale)
        self.fontThickness = 2
        self.net = None
        self.rgb = True
        self.verbose = False

        # Read class names from text file
        print("   - Setting Classes")
        with open(classesFile, 'r') as f:
            self.classLabels = [line.strip() for line in f.readlines()]

        # Generate colors for different classes
        print("   - Setting Colors")
        self.colors = np.random.uniform(0, 255, size=(len(self.classLabels), 3))

        # Read pre-trained model and config file
        print("   - Loading Model and Config")
        self.net = cv2.dnn.readNetFromDarknet( yolocfg, yoloweight )

    def __get_output_layers(self, net):
        layerNames = net.getLayerNames()
        output_layer = [layerNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layer

    def __draw_rect(self, image, class_id, confidence, x, y, w, h):

        if self.verbose:
            print("draw_rect x :" + str(x))
            print("draw_rect x :" + str(y))
            print("draw_rect w :" + str(w))
            print("draw_rect h :" + str(h))

        label = '%.2f' % confidence
        label = '%s:%s' % (self.classLabels[class_id], label)
        color = self.colors[class_id]

        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, self.fontThickness)

        cv2.rectangle(image, (x, y), (w, h), color, self.fontThickness)

        # draw text inside the bounding box
        cv2.putText(image, label, (x + self.fontThickness + 2, y + labelSize[1] + baseLine + self.fontThickness + 2), cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, color, self.fontThickness)

    def runInference(self, frame, frameW, frameH, confidenceLevel):
        try:
            # Create input blob
            blob = cv2.dnn.blobFromImage(frame, 1.0/255.0, (416, 416), (0,0,0), True, crop=False)

            # Set input blob for the network
            self.net.setInput(blob)

            # Run inference
            outputs = self.net.forward(self.__get_output_layers(self.net))

            # Initialize arrays
            boxes = []
            confidences = []
            classIDs = []

            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    classID = np.argmax(scores) 
                    confidence = scores[classID]
                    classLabel = self.classLabels[classID]

                    if confidence > confidenceLevel:

                        if self.verbose:
                            print( "Class Label : %s Confidence %f" % (classLabel, confidence))

                        centerX = int(detection[0] * frameW)
                        centerY = int(detection[1] * frameH)
                        rectWidth  = int(detection[2] * frameW)
                        rectHeight = int(detection[3] * frameH)

                        left = int(max((centerX - (rectWidth  / 2)), 5))
                        top  = int(max((centerY - (rectHeight / 2)), 5))

                        if rectHeight + top > frameH:
                            rectHeight = frameH - top - 5

                        if rectWidth + left > frameW:
                            rectWidth = frameW - left - 5

                        boxes.append([left, top, rectWidth, rectHeight])
                        confidences.append(float(confidence))
                        classIDs.append(classID)
        
            idxs = cv2.dnn.NMSBoxes(boxes, confidences, confidenceLevel, self.nmsThreshold)

            for i in idxs:
                i = i[0]
                box = boxes[i]
                # Get the bounding box coordinates
                x = box[0]
                y = box[1]
                w = box[2]
                h = box[3]
        
                # draw a bounding box rectangle and label on the image
                self.__draw_rect(frame, classIDs[i], confidences[i], x, y, x + w, y + h)

        except:
            print("Exception during AI Inference")

                
