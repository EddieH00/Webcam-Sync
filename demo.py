import cv2
import os
import numpy as np

if not os.path.exists('./captures/'):
    os.makedirs('./captures/')

folderNumber = 1
while os.path.exists('./captures/capture' + str(folderNumber)):
    folderNumber = folderNumber + 1
os.makedirs('./captures/capture' + str(folderNumber))

numberOfWebcams = 4
for i in range(numberOfWebcams):
    os.makedirs('./captures/capture' + str(folderNumber) + '/webcam' + str(i+1))


numberOfWebcams = 4
webcams = [cv2.VideoCapture(0)]*numberOfWebcams
webcams[1] = cv2.VideoCapture(1)
webcams[2] = cv2.VideoCapture(2)
webcams[3] = cv2.VideoCapture(3)

imageNumber = 1
while webcams[0].isOpened():
    ret1, frame1 = webcams[0].read()
    ret2, frame2 = webcams[1].read()
    ret3, frame3 = webcams[2].read()    
    ret4, frame4 = webcams[3].read()

    horizontal1 = np.concatenate((frame1, frame2), axis=1)
    horizontal2 = np.concatenate((frame3, frame4), axis=1)
    image = np.concatenate((horizontal1, horizontal2), axis = 0)
    cv2.imshow('webcams', image)
    
    cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam1/' + str(imageNumber)+ '.jpg', frame1)
    cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam2/' + str(imageNumber)+ '.jpg', frame2)
    cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam3/' + str(imageNumber)+ '.jpg', frame3)
    cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam4/' + str(imageNumber)+ '.jpg', frame4)

    imageNumber = imageNumber + 1
    
    if cv2.waitKey(1) & 0xFF ==ord('q'):
        break
    
webcams[0].release()
webcams[1].release()
webcams[2].release()
webcams[3].release()


    