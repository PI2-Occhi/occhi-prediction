from distutils.command.build import build
import cv2 as cv
import numpy as np
import prediction_module as m
import time
import json_builder as jb
from mqtt import publish, connect_mqtt
from skimage import io

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

    #camera = cv.VideoCapture(0)
    #width = camera.get(cv.CAP_PROP_FRAME_WIDTH)

    #mqqt client
    file = cv.VideoCapture(path)
    client = connect_mqtt()
    print(path)
    while True:
        FRAME_COUNTER += 1
        while True:
            try:
                frame = cv.imread(path)
                io.imread(path)
                break
            except:
                ...
        try:
            grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            #height, width = grayFrame.shape
            #circleCenter = (int(width/2), 50)
            # calling the face detector funciton
            image, face = m.faceDetector(frame, grayFrame, False)
            if face is not None:

                # calling landmarks detector funciton.
                image, PointList = m.faceLandmakDetector(frame, grayFrame, face, False)

                # cv.putText(frame, f'FPS: {round(FPS,1)}',
                #         (460, 20), m.fonts, 0.7, m.YELLOW, 2)
                RightEyePoint = PointList[36:42]
                LeftEyePoint = PointList[42:48]
                leftRatio, topMid, bottomMid = m.blinkDetector(LeftEyePoint)
                rightRatio, rTop, rBottom = m.blinkDetector(RightEyePoint)
                # cv.circle(image, topMid, 2, m.YELLOW, -1)
                # cv.circle(image, bottomMid, 2, m.YELLOW, -1)

                blinkRatio = (leftRatio + rightRatio)/2
                # cv.circle(image, circleCenter, (int(blinkRatio*4.3)), m.CHOCOLATE, -1)
                # cv.circle(image, circleCenter, (int(blinkRatio*3.2)), m.CYAN, 2)
                # cv.circle(image, circleCenter, (int(blinkRatio*2)), m.GREEN, 3)

                
                # for p in LeftEyePoint:
                #     cv.circle(image, p, 3, m.MAGENTA, 1)
                mask, pos, color = m.EyeTracking(frame, grayFrame, RightEyePoint)
                maskleft, leftPos, leftColor = m.EyeTracking(
                    frame, grayFrame, LeftEyePoint)

                if blinkRatio > 4:
                    COUNTER += 1
                    # cv.putText(image, f'Blink', (70, 50),
                    #         m.fonts, 0.8, m.LIGHT_BLUE, 2)
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
                        # cv.putText(image, COMMANDS[LAST_COMMAND], (230, 75), m.fonts, 0.5, m.BLACK, 2)
                        LAST_STATE = [COMMANDS[LAST_COMMAND], pos, leftPos]
                # cv.putText(image, f'Last blink count: {LAST_COMMAND}', (230, 17),
                #         m.fonts, 0.5, m.ORANGE, 2)
                # cv.putText(image, f'{"MOVE" if MOVE else "STOP"}', (230, 40), m.fonts, 0.5, m.LIGHT_RED if not MOVE else m.LIGHT_GREEN, 2)

                # draw background as line where we put text.
                # cv.line(image, (30, 90), (100, 90), color[0], 30)
                # cv.line(image, (25, 50), (135, 50), m.WHITE, 30)
                # cv.line(image, (int(width-150), 50), (int(width-45), 50), m.WHITE, 30)
                # cv.line(image, (int(width-140), 90),
                #         (int(width-60), 90), leftColor[0], 30)

                # # writing text on above line
                # cv.putText(image, f'{pos}', (35, 95), m.fonts, 0.6, color[1], 2)
                # cv.putText(image, f'{leftPos}', (int(width-140), 95),
                #         m.fonts, 0.6, leftColor[1], 2)
                # cv.putText(image, f'Right Eye', (35, 55), m.fonts, 0.6, color[1], 2)
                # cv.putText(image, f'Left Eye', (int(width-145), 55),
                #         m.fonts, 0.6, leftColor[1], 2)

                # showing the frame on the screen
                cv.imshow('Frame', image)
            else:
                cv.imshow('Frame', frame)
                
            SECONDS = time.time() - START_TIME
            # calculating the frame rate
            FPS = FRAME_COUNTER/SECONDS
            

            key = cv.waitKey(1)

            # if q is pressed on keyboard: quit
            if key == ord('q'):
                break
        except:
            ...
    # closing the camera
    # camera.release()
    
    cv.destroyAllWindows()
