#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

from darknet import darknet

import AppState

import iothub_client
# pylint: disable=E0611
# Disabling linting that is not supported by Pylint for C extensions such as iothub_client. See issue https://github.com/PyCQA/pylint/issues/1955 
from iothub_client import (IoTHubMessage)

import cv2
#import cv2.cv as cv
import numpy as np
import time
import os
import json
from datetime import datetime

yolocfg  = r'yolo/yolov3-tiny.cfg'
yoloweight = r'yolo/yolov3-tiny.weights'
classesFile = r'yolo/coco.names'
dataFile = r'yolo/coco.data'

encoding = 'utf-8'


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
        self.lastMessageSentTime = datetime.now()

        # Read class names from text file
        print("   - Setting Classes")
        with open(classesFile, 'r') as f:
            self.classLabels = [line.strip() for line in f.readlines()]

        # Generate colors for different classes
        print("   - Setting Colors")
        self.colors = np.random.uniform(0, 255, size=(len(self.classLabels), 3))

        # Read pre-trained model and config file
        print("   - Loading Model and Config")
        darknet.performDetect( configPath = yolocfg, weightPath = yoloweight, metaPath= dataFile, initOnly= True )

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
        label = '%s:%s' % (class_id, label)
        color = self.colors[self.classLabels.index(class_id)]

        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, self.fontThickness)

        cv2.rectangle(image, (x, y), (w, h), color, self.fontThickness)

        # draw text inside the bounding box
        cv2.putText(image, label, (x + self.fontThickness + 2, y + labelSize[1] + baseLine + self.fontThickness + 2), cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, color, self.fontThickness)

    def runInference(self, frame, frameW, frameH, confidenceLevel):
        try:

            detections = darknet.detect(darknet.netMain, darknet.metaMain, frame, confidenceLevel)

            countsByClassId = {};

            for detection in detections:
              
                classLabel = detection[0]
                classID = str(detection[0], encoding)
                confidence = detection[1]

                if confidence > confidenceLevel:

                    if classID not in countsByClassId:
                        countsByClassId[classID] = 1
                    else:
                        countsByClassId[classID] = countsByClassId[classID] + 1

                    bounds = detection[2]
                    
                    xEntent = int(bounds[2])
                    yExtent = int(bounds[3])
                    # Coordinates are around the center
                    xCoord = int(bounds[0] - bounds[2]/2)
                    yCoord = int(bounds[1] - bounds[3]/2)

                    self.__draw_rect(frame, classID, confidence, xCoord, yCoord, xCoord + xEntent, yCoord + yExtent)

            if len(countsByClassId) > 0 and (datetime.now() - self.lastMessageSentTime).total_seconds() >= 1 :
                strMessage = json.dumps(countsByClassId)
                message = IoTHubMessage(strMessage)
                AppState.HubManager.send_event_to_output("output1", message, 0)
                self.lastMessageSentTime=datetime.now()

        except Exception as e:
            print("Exception during AI Inference")
            print(e)