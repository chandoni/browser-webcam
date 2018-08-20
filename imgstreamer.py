#!/usr/bin/env python
import numpy as np
import cv2
import os
import sys
import asyncio
import websockets
import threading

def readimgsize(im_filename):
    f = open(im_filename, 'rb') # read bytes...
    f.seek(0, os.SEEK_END) # (offset[, whence])
    fileSize = f.tell() # return position of the read pointer within the file
    print(fileSize)
    f.seek(0, os.SEEK_SET)
    buffer = f.read(fileSize) # read fileSize number of bytes into buffer
    return buffer

def recognizeFace(im):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        im = cv2.rectangle(im,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = im[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    cv2.imwrite('img-cap.jpg', im, [int(cv2.IMWRITE_JPEG_QUALITY), 60])


###################################################################################################3

face_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.5/dist-packages/cv2/data/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.5/dist-packages/cv2/data/haarcascade_eye.xml')
rec_face = True
cam = cv2.VideoCapture(0)

async def sendimage(websocket, path):
    fps = 30
    while True:
        retval, frame = cam.read()
        if retval != True:
            raise ValueError("Can't read frame")

        cv2.imwrite('img-cap.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60]) # write image and set quality

        if (rec_face == True):
            img = cv2.imread('img-cap.jpg')
            recognizeFace(img)

        imgbytes = readimgsize('img-cap.jpg') # read the newly rewritten image into bytes

        await websocket.send(imgbytes) # send the bytes of the newly captured image
        await asyncio.sleep(1 / fps)

start_server = websockets.serve(sendimage, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
