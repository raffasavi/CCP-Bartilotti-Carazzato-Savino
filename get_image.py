import cv2 as cv
import datetime
import time

i = 0
while True:
    cam = cv.VideoCapture(0)
    cam.set(3,1280)
    ret, img = cam.read()

    if ret:
        text = "Width: " + str(cam.get(3)) + " Height: " + str(cam.get(4))
        datet = str(datetime.datetime.now())
        frame = cv.putText(img, datet, (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 2, cv.LINE_AA)
        cv.imshow("Display window", img)
        cv.imwrite("frame {}.png".format(i), img)
        cv.destroyAllWindows()

    i = i + 1
    time.sleep(5)