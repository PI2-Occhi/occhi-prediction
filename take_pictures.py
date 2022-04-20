import cv2
from time import sleep

cam = cv2.VideoCapture(0)


img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imwrite('webcam.jpg', frame)

cam.release()