import cv2
import os
import numpy as np

numberOfWebcams = 4

#creates folder structure
#captures > capture1 > webcam1, webcam2 etc.
#returns the folder number eg. captures > capture9 returns 9
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
#opens 4 webcams. Saves the frames and displays the live stream.
#input is the folder number it is capturing to
def capture(folderNumber):
    numberOfWebcams = 4
    print('opening webcams... this could take a minute or two')
    webcam1 = cv2.VideoCapture(0)
    webcam2 = cv2.VideoCapture(1)
    webcam3 = cv2.VideoCapture(2)
    webcam4 = cv2.VideoCapture(3)

    imageNumber = 1
    print('recording, press q to stop...')
    while webcam1.isOpened():
        ret1, frame1 = webcam1.read()
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam1/' + str(imageNumber)+ '.jpg', frame1)

        ret2, frame2 = webcam2.read()
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam2/' + str(imageNumber)+ '.jpg', frame2)

        ret3, frame3 = webcam3.read()    
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam3/' + str(imageNumber)+ '.jpg', frame3)

        ret4, frame4 = webcam4.read()
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam4/' + str(imageNumber)+ '.jpg', frame4)

        horizontal1 = np.concatenate((frame1, frame2), axis=1)
        horizontal2 = np.concatenate((frame3, frame4), axis=1)
        image = np.concatenate((horizontal1, horizontal2), axis = 0)
        cv2.imshow('webcams', image)
        
        imageNumber = imageNumber + 1
        
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            break


##this function looks at the first frame from all four webcams, and determines which image was produced last
#input is the folder number it is searching through
#output is the webcam number that is last, and the time stamp the image was produced at
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

def calcAvgLatency(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    firstWebcam, firstTimeStamp = findLatestWebcam(folderNumber)
    latency = [0]*numberOfWebcams
    for i in range(numberOfWebcams):
        webcamPath = path+ 'webcam' + str(i+1) + '/'
        lastIndex = sorted(os.listdir(webcamPath), key = len)[-1]
        lastIndex = int(lastIndex[:-4])
        for j in range(lastIndex):
            firstWebcamPath = path + 'webcam' + str(firstWebcam) + '/' + str(j+ 1) +'.jpg'
            latency[i] = latency[i] + os.path.getctime(webcamPath + str(j+1) + '.jpg') - os.path.getctime(firstWebcamPath)
        latency[i] = latency[i] / len(os.listdir(webcamPath))
    
    for i in range(numberOfWebcams):
        latency[i] = round(latency[i], 3)
    return latency

def calcAvgDiff(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    avgDiff = [0]*numberOfWebcams
    for i in range(numberOfWebcams):
        webcamPath = path + 'webcam' +str(i+1) + '/'
        first = sorted(os.listdir(webcamPath), key = len)[0]
        last = sorted(os.listdir(webcamPath), key = len)[-1]
        avgDiff[i] = os.path.getctime(webcamPath + last) - os.path.getctime(webcamPath + first)
        avgDiff[i] = avgDiff[i]/len(os.listdir(webcamPath))
    return avgDiff

def sync(folderNumber):
    avgLatency = calcAvgLatency(folderNumber)
    avgDiff = calcAvgDiff(folderNumber)
    changed = [0, 0, 0, 0]
    for i in range(len(avgDiff)):
        path = './captures/capture'+ str(folderNumber) + '/webcam' + str(i+1) + '/'
        numberOfFrames = abs(round(avgLatency[i] / avgDiff[i]))
        if numberOfFrames != 0:
            changed[i] = 1
            print('webcam ' + str(i + 1) + ' synced')
            for j in range(len(os.listdir(path))):
                os.rename(path + str(j+1) + '.jpg', path + str(j+1-numberOfFrames) + '.jpg')
    return changed


###Main
folderNumber = createFolders()
capture(folderNumber)
print('recording done')
latency = calcAvgLatency(folderNumber)
print('latency of webcams relative to webcam 4: ' + str(latency[0]) +'s, ' + str(latency[1]) +'s, ' + str(latency[2]) +'s, ' + str(latency[3]) +'s,')
avgDiff = calcAvgDiff(folderNumber)
print('webcams captured at: ' + str(round(1/avgDiff[0], 2)) + 'fps, ' + str(round(1/avgDiff[1], 2)) + 'fps, ' + str(round(1/avgDiff[2], 2)) + 'fps, ' + str(round(1/avgDiff[3], 2)) + 'fps')
sync(folderNumber)
latency = calcAvgLatency(folderNumber)
print('new latencies relative to webcam 4: ' + str(latency[0]) +'s, ' + str(latency[1]) +'s, ' + str(latency[2]) +'s, ' + str(latency[3]) +'s,')