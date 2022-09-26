import cv2
import os
import numpy as np

def createFolders():
    if not os.path.exists('./captures/'):
        os.makedirs('./captures/')

    folderNumber = 1
    while os.path.exists('./captures/capture' + str(folderNumber)):
        folderNumber = folderNumber + 1
    os.makedirs('./captures/capture' + str(folderNumber))

    for i in range(numberOfWebcams):
        os.makedirs('./captures/capture' + str(folderNumber) + '/webcam' + str(i+1))

    return folderNumber

#currently capture is fixed at 4 webcams
def capture(folderNumber):
    numberOfWebcams = 4
    webcam1 = cv2.VideoCapture(0)
    webcam2 = cv2.VideoCapture(1)
    webcam3 = cv2.VideoCapture(2)
    webcam4 = cv2.VideoCapture(3)

    imageNumber = 1
    while webcam1.isOpened():
        ret1, frame1 = webcam1.read()
        ret2, frame2 = webcam2.read()
        ret3, frame3 = webcam3.read()    
        ret4, frame4 = webcam4.read()

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

def findLatestWebcam(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    latestWebcam = 1
    latestTimeStamp = os.path.getctime(path + 'webcam' + str(latestWebcam) + '/1.jpg')
    for i in range(2, numberOfWebcams + 1):
        if os.path.getctime(path + 'webcam' + str(i) + '/1.jpg') >= latestTimeStamp:
            latestWebcam = i
            latestTimeStamp = os.path.getctime(path + 'webcam' + str(i) + '/' + '1.jpg')
    return latestWebcam, latestTimeStamp

def findFirstWebcam(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    firstWebcam = 1
    firstTimeStamp = os.path.getctime(path + 'webcam' + str(firstWebcam) + '/1.jpg')
    for i in range(2, numberOfWebcams + 1):
        if os.path.getctime(path + 'webcam' + str(i) + '/1.jpg') <= firstTimeStamp:
            firstWebcam = i
            firstTimeStamp = os.path.getctime(path + 'webcam' + str(i) + '/' + '1.jpg')
    return firstWebcam, firstTimeStamp


def calcLatency(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    firstWebcam, firstTimeStamp = findFirstWebcam(folderNumber)
    latency = [0]*numberOfWebcams
    for i in range(numberOfWebcams):
        latency[i] = os.path.getctime(path+ 'webcam' + str(i+1) + '/' + '1.jpg') - firstTimeStamp

    return latency


def sync():
    print('done')


