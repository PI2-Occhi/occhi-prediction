from distutils.command.build import build
import cv2 as cv
import numpy as np
import prediction_module as m
import time
import json_builder as jb
from mqtt import publish, connect_mqtt

def image_processing(path):
    
    # Variables
    COUNTER = 0
    TOTAL_BLINKS = 0
    SEQUENCE_BLINKS = 0
    CLOSED_EYES_FRAME = 3

    # variables for frame rate.
    FRAME_COUNTER = 0
    START_TIME = time.time()
    LAST_BLINK_MOMENT = START_TIME
    LAST_COMMAND = 0
    FPS = 0
    MOVE = False
    LAST_STATE = []
    COMMANDS_JSON = {}

    client = connect_mqtt()

    while True:
        FRAME_COUNTER += 1
        while True:
            with open(path, 'rb') as f:
                check_chars = f.read()[-2:]
                if check_chars == b'\xff\xd9':
                    break
        frame = cv.imread(path)

        try:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            grayFrame = frame#cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            
            image, face = m.faceDetector(frame, grayFrame, False)
            if face is not None:

                # calling landmarks detector funciton.
                image, PointList = m.faceLandmakDetector(frame, grayFrame, face, False)
                
                RightEyePoint = PointList[36:42]
                LeftEyePoint = PointList[42:48]
                leftRatio, topMid, bottomMid = m.blinkDetector(LeftEyePoint)
                rightRatio, rTop, rBottom = m.blinkDetector(RightEyePoint)

                blinkRatio = (leftRatio + rightRatio)/2

                mask, pos, color = m.EyeTracking(frame, grayFrame, RightEyePoint)
                maskleft, leftPos, leftColor = m.EyeTracking(
                    frame, grayFrame, LeftEyePoint)

                if blinkRatio > 4:
                    COUNTER += 1
                else:
                    TOTAL_BLINKS, SEQUENCE_BLINKS, COUNTER, LAST_BLINK_MOMENT, LAST_COMMAND, MOVE = m.blinkCounter(TOTAL_BLINKS, SEQUENCE_BLINKS, LAST_BLINK_MOMENT, COUNTER, LAST_COMMAND, MOVE, COUNTER > CLOSED_EYES_FRAME)
                    COMMANDS = {
                        2: 'STOP MOVEMENT' if not MOVE else 'START MOVEMENT',
                        3: '180 DEGRESS MOVEMENT',
                        4: 'REVERSE MOVEMENT'
                    }
                    if LAST_COMMAND in COMMANDS.keys():
                        if [COMMANDS[LAST_COMMAND], pos, leftPos] != LAST_STATE:
                            COMMANDS_JSON = jb.build_json(COMMANDS[LAST_COMMAND], pos, leftPos)
                            #publish json on mqqt channel
                            publish(client, COMMANDS_JSON)
                        LAST_STATE = [COMMANDS[LAST_COMMAND], pos, leftPos]

                # showing the frame on the screen
                #cv.imshow('Frame', image)
                
            SECONDS = time.time() - START_TIME
            # calculating the frame rate
            FPS = FRAME_COUNTER/SECONDS
            

            key = cv.waitKey(1)

            # if q is pressed on keyboard: quit
            if key == ord('q'):
                break
        except:
            ...