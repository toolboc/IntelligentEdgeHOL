#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

import cv2
import numpy as np
import requests
import time
import json
import os

import ImageServer
from ImageServer import ImageServer
import VideoStream
from VideoStream import VideoStream
'''***********************************************************
Step-10 : Uncomment Start
***********************************************************'''
# import YoloInference
# from YoloInference import YoloInference
'''***********************************************************
Step-10 : Uncomment End
***********************************************************'''

class VideoCapture(object):

    def __init__(
            self,
            videoPath = "",
            verbose = True,
            videoW = 0,
            videoH = 0,
            fontScale = 1.0,
            inference = True,
            confidenceLevel = 0.5):

        self.videoPath = videoPath
        self.verbose = verbose
        self.videoW = videoW
        self.videoH = videoH
        self.inference = inference
        self.confidenceLevel = confidenceLevel
        self.useStream = False
        self.useMovieFile = False
        self.frameCount = 0
        self.vStream = None
        self.vCapture = None
        self.displayFrame = None
        self.fontScale = float(fontScale)
        self.captureInProgress = False

        print("VideoCapture::__init__()")
        print("OpenCV Version : %s" % (cv2.__version__))
        print("===============================================================")
        print("Initialising Video Capture with the following parameters: ")
        print("   - Video path      : " + self.videoPath)
        print("   - Video width     : " + str(self.videoW))
        print("   - Video height    : " + str(self.videoH))
        print("   - Font Scale      : " + str(self.fontScale))
        print("   - Inference?      : " + str(self.inference))
        print("   - ConficenceLevel : " + str(self.confidenceLevel))
        print("")

        self.imageServer = ImageServer(80, self)
        self.imageServer.start()
        '''***********************************************************
        Step-10 : Uncomment Start
        ***********************************************************'''
        # self.yoloInference = YoloInference(self.fontScale)
        '''***********************************************************
        Step-10 : Uncomment End
        ***********************************************************'''

    def __IsCaptureDev(self, videoPath):
        try: 
            return '/dev/video' in videoPath.lower()
        except ValueError:
            return False

    def __IsRtsp(self, videoPath):
        try:
            return 'rtsp:' in videoPath.lower()
        except ValueError:
            return False

    def __IsYoutube(self, videoPath):
        try:
            return 'www.youtube.com' in videoPath.lower()
        except ValueError:
            return False

    def __enter__(self):

        if self.verbose:
            print("videoCapture::__enter__()")

        self.setVideoSource(self.videoPath)

        return self

    def setVideoSource(self, newVideoPath):

        if self.captureInProgress:
            self.captureInProgress = False
            time.sleep(1.0)
            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None
            elif self.vStream:
                self.vStream.stop()
                self.vStream = None

        if self.__IsRtsp(newVideoPath):
            print("\r\n===> RTSP Video Source")

            self.useStream = True
            self.useMovieFile = False
            self.videoPath = newVideoPath

            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.vStream = VideoStream(newVideoPath).start()
            # Needed to load at least one frame into the VideoStream class
            time.sleep(1.0)
            self.captureInProgress = True

        elif self.__IsYoutube(newVideoPath):
            print("\r\n===> YouTube Video Source")
            self.useStream = False
            self.useMovieFile = True
            # This is video file
            self.downloadVideo(newVideoPath)
            self.videoPath = newVideoPath
            if self.vCapture.isOpened():
                self.captureInProgress = True
            else:
                print("===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")

        elif self.__IsCaptureDev(newVideoPath):
            print("===> Webcam Video Source")
            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.videoPath = newVideoPath
            self.useMovieFile = False
            self.useStream = False
            self.vCapture = cv2.VideoCapture(newVideoPath)
            if self.vCapture.isOpened():
                self.captureInProgress = True
            else:
                print("===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")
        else:
            print("===========================\r\nWARNING : No Video Source\r\n===========================\r\n")
            self.useStream = False
            self.useYouTube = False
            self.vCapture = None
            self.vStream = None
        return self

    def downloadVideo(self, videoUrl):
        if self.captureInProgress:
            bRestartCapture = True
            time.sleep(1.0)
            if self.vCapture:
                print("Relase vCapture")
                self.vCapture.release()
                self.vCapture = None
        else:
            bRestartCapture = False

        if os.path.isfile('/app/video.mp4'):
            os.remove("/app/video.mp4")

        print("Start downloading video")
        os.system("youtube-dl -o /app/video.mp4 -f mp4 " + videoUrl)
        print("Download Complete")
        self.vCapture = cv2.VideoCapture("/app/video.mp4")
        time.sleep(1.0)
        self.frameCount = int(self.vCapture.get(cv2.CAP_PROP_FRAME_COUNT))

        if bRestartCapture:
            self.captureInProgress = True

    def get_display_frame(self):
        return self.displayFrame

    def start(self):
        while True:
            if self.captureInProgress:
                self.__Run__()

            if not self.captureInProgress:
                time.sleep(1.0)

    def __Run__(self):

        print("===============================================================")
        print("videoCapture::__Run__()")
        print("   - Stream          : " + str(self.useStream))
        print("   - useMovieFile    : " + str(self.useMovieFile))

        cameraH = 0
        cameraW = 0
        frameH = 0
        frameW = 0

        if self.useStream and self.vStream:
            cameraH = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cameraW = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        elif self.useStream == False and self.vCapture:
            cameraH = int(self.vCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cameraW = int(self.vCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        else:
            print("Error : No Video Source")
            return
           
        if self.videoW != 0 and self.videoH != 0 and self.videoH != cameraH and self.videoW != cameraW:
            needResizeFrame = True
            frameH = self.videoH
            frameW = self.videoW
        else:
            needResizeFrame = False
            frameH = cameraH
            frameW = cameraW

        if needResizeFrame:
            print("Original frame size  : " + str(cameraW) + "x" + str(cameraH))
            print("     New frame size  : " + str(frameW) + "x" + str(frameH))
            print("             Resize  : " + str(needResizeFrame))
        else:
            print("Camera frame size    : " + str(cameraW) + "x" + str(cameraH))
            print("       frame size    : " + str(frameW) + "x" + str(frameH))

        # Check camera's FPS
        if self.useStream:
            cameraFPS = int(self.vStream.stream.get(cv2.CAP_PROP_FPS))
        else:
            cameraFPS = int(self.vCapture.get(cv2.CAP_PROP_FPS))

        if cameraFPS == 0:
            print("Error : Could not get FPS")
            return

        print("Frame rate (FPS)     : " + str(cameraFPS))

        currentFPS = cameraFPS
        perFrameTimeInMs = 1000 / cameraFPS

        while True:

            # Get current time before we capture a frame
            tFrameStart = time.time()

            if not self.captureInProgress:
                break

            if self.useMovieFile:
                currentFrame = int(self.vCapture.get(cv2.CAP_PROP_POS_FRAMES))
                if currentFrame >= self.frameCount:
                    self.vCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            try:
                # Read a frame
                if self.useStream:
                    frame = self.vStream.read()
                else:
                    frame = self.vCapture.read()[1]
            except:
                print("ERROR : Exception during capturing")

            # Rezie frame if flagged
            if needResizeFrame:
                frame = cv2.resize(frame, (self.videoW, self.videoH))

            # Run Object Detection
            '''***********************************************************
            Step-10 : Uncomment Start
            ***********************************************************'''
            # if self.inference:
            #     self.yoloInference.runInference(frame, frameW, frameH, self.confidenceLevel, self.verbose)
            '''***********************************************************
            Step-10 : Uncomment Start
            ***********************************************************'''

            # Calculate FPS
            timeElapsedInMs = (time.time() - tFrameStart) * 1000
            currentFPS = 1000.0 / timeElapsedInMs

            if (currentFPS > cameraFPS):
                # Cannot go faster than Camera's FPS
                currentFPS = cameraFPS

            # Add FPS Text to the frame
            cv2.putText( frame, "FPS " + str(round(currentFPS, 1)), (10, int(30 * self.fontScale)), cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, (0,0,255), 2)

            self.displayFrame = cv2.imencode( '.jpg', frame )[1].tobytes()

            timeElapsedInMs = (time.time() - tFrameStart) * 1000

            if (1000 / cameraFPS) > timeElapsedInMs:
                # This is faster than image source (e.g. camera) can feed.  
                waitTimeBetweenFrames = perFrameTimeInMs - timeElapsedInMs
                #if self.verbose:
                    #print("  Wait time between frames :" + str(int(waitTimeBetweenFrames)))
                time.sleep(waitTimeBetweenFrames/1000.0)

    def __exit__(self, exception_type, exception_value, traceback):

        if self.vCapture:
            self.vCapture.release()

        self.imageServer.close()
        cv2.destroyAllWindows()
