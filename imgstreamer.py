import cv2
import os
import sys
import asyncio
import websockets
import threading

cam = cv2.VideoCapture(0)

def readimgsize(im_filename):
    f = open(im_filename, 'rb') # read bytes...
    f.seek(0, os.SEEK_END) # (offset[, whence])
    fileSize = f.tell() # return position of the read pointer within the file
    #print(fileSize)
    f.seek(0, os.SEEK_SET)
    buffer = f.read(fileSize) # read fileSize number of bytes into buffer
    return buffer

async def sendimage(websocket, path):
    fps = 80
    #idx = 0    this was also for version 1
    while True:
        retval, frame = cam.read()
        if retval != True:
            raise ValueError("Can't read frame")

        cv2.imwrite('img-cap.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40]) # write image and set quality
        imgbytes = readimgsize('img-cap.jpg') # read the newly rewritten image into bytes

        # this section was for version 1 and only swapped between two images on the webpage
        #if idx == 0:
        #    imgbytes = readimgsize('cracked300x300.jpg')
        #    idx = 1
        #else:
        #    imgbytes = readimgsize('moby300x300.jpg')
        #    idx = 0

        await websocket.send(imgbytes) # send the bytes of the newly captured image
        await asyncio.sleep(1 / fps)

start_server = websockets.serve(sendimage, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
