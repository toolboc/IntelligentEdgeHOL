# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
import sys
import time
import json

import iothub_client
# pylint: disable=E0611
# Disabling linting that is not supported by Pylint for C extensions such as iothub_client. See issue https://github.com/PyCQA/pylint/issues/1955 
from iothub_client import (IoTHubModuleClient, IoTHubClientError, IoTHubError,
                           IoTHubMessage, IoTHubMessageDispositionResult,
                           IoTHubTransportProvider)

import VideoCapture
from VideoCapture import VideoCapture

def send_to_Hub_callback(strMessage):
    message = IoTHubMessage(bytearray(strMessage, 'utf8'))
    print("\r\nsend_to_Hub_callback()")
    print("   - message  : %s" & message)
    hubManager.send_event_to_output("output1", message, 0)

# Callback received when the message that we're forwarding is processed.
def send_confirmation_callback(message, result, user_context):
    print("\r\nsend_confirmation_callback()")
    print("   - result  : %s" % result)

def device_twin_callback(update_state, payload, user_context):
    global hubManager
    global videoCapture

    if (("%s"%(update_state)) == "PARTIAL"):
        jsonData = json.loads(payload)
    else:
        jsonData = json.loads(payload).get('desired')

    print("\r\ndevice_twin_callback()")
    print("   - status  : %s" % update_state )
    print("   - payload : \r\n%s" % json.dumps(jsonData, indent=4))

    if "ConfidenceLevel" in jsonData:
        print("   - ConfidenceLevel : " + str(jsonData['ConfidenceLevel']))
        videoCapture.confidenceLevel = float(jsonData['ConfidenceLevel'])

    if "VerboseMode" in jsonData:
        print("   - Verbose         : " + str(jsonData['VerboseMode']))
        if jsonData['VerboseMode'] == 0:
            videoCapture.verbose = False
        else:
            videoCapture.verbose = True

    if "Inference" in jsonData:
        print("   - Inference       : " + str(jsonData['Inference']))
        if jsonData['Inference'] == 0:
            videoCapture.inference = False
        else:
            videoCapture.inference = True

    if "VideoSource" in jsonData:
        strUrl = str(jsonData['VideoSource'])
        print("   - VideoSource     : " + strUrl)
        if strUrl.lower() != videoCapture.videoPath.lower() and strUrl != "":
            videoCapture.setVideoSource(strUrl)

    device_twin_send_reported(hubManager)

def device_twin_send_reported(hubManager):
    global videoCapture

    jsonTemplate = "{\"ConfidenceLevel\": \"%s\",\"VerboseMode\": %d,\"Inference\": %d, \"VideoSource\":\"%s\"}"

    strUrl = videoCapture.videoPath

    jsonData = jsonTemplate % (
        str(videoCapture.confidenceLevel),
        videoCapture.verbose,
        videoCapture.inference,
        strUrl)

    print("\r\ndevice_twin_send_reported()")
    print("   - payload : \r\n%s" % json.dumps(jsonData, indent=4))

    hubManager.send_reported_state(jsonData, len(jsonData), 1002)

def send_reported_state_callback(status_code, user_context):
    print("\r\nsend_reported_state_callback()")
    print("   - status_code : [%d]" % (status_code) )

class HubManager(object):

    def __init__(
            self,
            messageTimeout,
            protocol,
            verbose):

        # Communicate with the Edge Hub

        self.messageTimeout = messageTimeout
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        self.client.set_option("messageTimeout", self.messageTimeout)
        self.client.set_option("product_info","edge-yolo-capture")
        if verbose:
            self.client.set_option("logtrace", 1)#enables MQTT logging

        self.client.set_module_twin_callback(
            device_twin_callback, None)

    def send_reported_state(self, reported_state, size, user_context):
        self.client.send_reported_state(
            reported_state, size,
            send_reported_state_callback, user_context)

    def send_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(outputQueueName, event, send_confirmation_callback, send_context)

def main(
        videoPath ="",
        verbose = False,
        videoWidth = 0,
        videoHeight = 0,
        fontScale = 1.0,
        inference = False,
        confidenceLevel = 0.8
        ):

    global hubManager
    global videoCapture

    try:
        print("\nPython %s\n" % sys.version )
        print("Yolo Capture Azure IoT Edge Module. Press Ctrl-C to exit." )

        with VideoCapture(videoPath, 
                         verbose,
                         videoWidth,
                         videoHeight,
                         fontScale,
                         inference,
                         confidenceLevel) as videoCapture:

            try:
                hubManager = HubManager(10000, IoTHubTransportProvider.MQTT, False)
            except IoTHubError as iothub_error:
                print("Unexpected error %s from IoTHub" % iothub_error )
                return

            videoCapture.start()

    except KeyboardInterrupt:
        print("Camera capture module stopped" )


def __convertStringToBool(env):
    if env in ['True', 'TRUE', '1', 'y', 'YES', 'Y', 'Yes']:
        return True
    elif env in ['False', 'FALSE', '0', 'n', 'NO', 'N', 'No']:
        return False
    else:
        raise ValueError('Could not convert string to bool.')

if __name__ == '__main__':
    try:
        VIDEO_PATH = os.environ['VIDEO_PATH']
        VERBOSE = __convertStringToBool(os.getenv('VERBOSE', 'False'))
        VIDEO_WIDTH = int(os.getenv('VIDEO_WIDTH', 0))
        VIDEO_HEIGHT = int(os.getenv('VIDEO_HEIGHT',0))
        FONT_SCALE = os.getenv('FONT_SCALE', 1)
        INFERENCE = __convertStringToBool(os.getenv('INFERENCE', 'False'))
        CONFIDENCE_LEVEL = float(os.getenv('CONFIDENCE_LEVEL', "0.8"))

    except ValueError as error:
        print(error )
        sys.exit(1)

    main(VIDEO_PATH, VERBOSE, VIDEO_WIDTH, VIDEO_HEIGHT, FONT_SCALE, INFERENCE, CONFIDENCE_LEVEL)



