####################################################################################
################################# LIBRERIE E SETUP #################################
####################################################################################

import cv2 as cv
import datetime
import time
from requests import get, post
from secret import secret

#url del server di gcp
base_url = 'https://ccp-barcarsav.ew.r.appspot.com'


# Load the cascade
face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

# To capture video from webcam.
cap = cv.VideoCapture(0)
cap.set(2, 760)
last_check = 0
# To use a video file as input
#cap = cv.VideoCapture('filename.mp4')

####################################################################################
############################ FUNZIONAMENTO DEL SENSORE #############################
####################################################################################

while True:
    # Read and make up the frame
    _, img = cap.read()
    text = "Width: " + str(cap.get(3)) + " Height: " + str(cap.get(4))
    datet = str(datetime.datetime.now())
    frame = cv.putText(img, datet, (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv.LINE_AA)
    # Convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Detect the faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw the rectangle around each face
    for (x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Show Display
    cv.imshow('img', img)

####################################################################################
######################### CREAZIONE E INVIO FILE OUTPUT ############################
####################################################################################

    # Output Sensor every 5 seconds
    t = int(time.time())
    if t%5 == 0 and t != last_check:
        last_check = t
        #print(t)

        #text
        value = "Sensor 1 * {} * {} *".format(len(faces), datet)
        date = datet.split(" ")[0]
        all = datet[0:-7]
        hour = int(datet.split(" ")[1].split(":")[0])
        num = datet.replace(":", " ")[0:-7]
        nameimage = "frame {}.jpg".format(num)
        cv.imwrite(nameimage, img)
        files = {'file': open(nameimage, 'rb')}
        r = post(f'{base_url}/sensors/sensor1', data={'date': date, 'all': all, 'hour': hour,
                                                      'value': len(faces), 'secret': secret}, files=files)
        print('Done: {}'.format(value))
####################################################################################
############################## SPEGNIMENTO DEL SENSORE #############################
####################################################################################

    # Stop if 'escape' key is pressed
    k = cv.waitKey(30) & 0xff
    if k == 27:
        break

# Release the VideoCapture object
cap.release()
