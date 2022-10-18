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
def capture(folderNumber, percentResolution):
    numberOfWebcams = 4
    print('opening webcams... this could take a minute or two')
    webcam1 = cv2.VideoCapture(0)
    webcam2 = cv2.VideoCapture(1)
    webcam3 = cv2.VideoCapture(2)
    webcam4 = cv2.VideoCapture(3)

    #junk frames
    ret1, frame1 = webcam1.read()
    ret2, frame2 = webcam2.read()
    ret3, frame3 = webcam3.read()    
    ret4, frame4 = webcam4.read()
    resH = int(frame1.shape[0]*percentResolution)
    resW = int(frame1.shape[1]*percentResolution)

    imageNumber = 1
    print('recording at ' + str(resW) + 'x' + str(resH) + ' resolution, press q to stop...')
    while webcam1.isOpened():
        ret1, frame1 = webcam1.read()
        frame1 = cv2.resize(frame1, (resW, resH))
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam1/' + str(imageNumber)+ '.jpg', frame1)

        ret2, frame2 = webcam2.read()
        frame2 = cv2.resize(frame2, (resW, resH))
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam2/' + str(imageNumber)+ '.jpg', frame2)

        ret3, frame3 = webcam3.read()    
        frame3 = cv2.resize(frame3, (resW, resH))
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam3/' + str(imageNumber)+ '.jpg', frame3)

        ret4, frame4 = webcam4.read()
        frame4 = cv2.resize(frame4, (resW, resH))
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam4/' + str(imageNumber)+ '.jpg', frame4)

        horizontal1 = np.concatenate((frame1, frame2), axis=1)
        horizontal2 = np.concatenate((frame3, frame4), axis=1)
        image = np.concatenate((horizontal1, horizontal2), axis = 0)
        cv2.imshow('webcams', image)
        
        imageNumber = imageNumber + 1
        
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            print('recording done')
            break


##this function looks at the first frame from all four webcams, and determines which image was produced last
#input is the folder number it is searching through
#output is the webcam number that is last, and the time stamp the image was produced at
def findLatestWebcam(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    latestWebcam = 1
    latestTimeStamp = os.path.getmtime(path + 'webcam' + str(latestWebcam) + '/1.jpg')
    for i in range(2, numberOfWebcams + 1):
        if os.path.getmtime(path + 'webcam' + str(i) + '/1.jpg') >= latestTimeStamp:
            latestWebcam = i
            latestTimeStamp = os.path.getmtime(path + 'webcam' + str(i) + '/' + '1.jpg')
    return latestWebcam, latestTimeStamp

def findFirstWebcam(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    firstWebcam = 1
    firstTimeStamp = os.path.getmtime(path + 'webcam' + str(firstWebcam) + '/1.jpg')
    for i in range(2, numberOfWebcams + 1):
        if os.path.getmtime(path + 'webcam' + str(i) + '/1.jpg') <= firstTimeStamp:
            firstWebcam = i
            firstTimeStamp = os.path.getmtime(path + 'webcam' + str(i) + '/' + '1.jpg')
    return firstWebcam, firstTimeStamp

def calcAvgLatency(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    #lastWebcam, lastTimeStamp = findLatestWebcam(folderNumber)
    latency = [0]*numberOfWebcams
    for i in range(numberOfWebcams):
        webcamPath = path + 'webcam' + str(i+1) + '/'
        lastIndex = sorted(os.listdir(webcamPath), key = len)[-1]
        lastIndex = int(lastIndex[:-4])
        for j in range(lastIndex):
            lastWebcamPath = path + 'webcam4' + '/' + str(j+ 1) +'.jpg'
            latency[i] = latency[i] + os.path.getmtime(webcamPath + str(j+1) + '.jpg') - os.path.getmtime(lastWebcamPath)
        latency[i] = latency[i] / lastIndex
    
    return latency 
    
def printLatency(folderNumber):
    latency = calcAvgLatency(folderNumber)
    for i in range(len(latency)):
        latency[i] = round(latency[i], 3)
        print('latency of webcam ' + str(i + 1) + ' relative to webcam ' +str(numberOfWebcams) +': '  + format(latency[i], '.3f') +' s')


def calcAvgDiff(folderNumber):
    path = './captures/capture'+ str(folderNumber) + '/'
    avgDiff = [0]*numberOfWebcams
    for i in range(numberOfWebcams):
        webcamPath = path + 'webcam' +str(i+1) + '/'
        first = sorted(os.listdir(webcamPath), key = len)[0]
        last = sorted(os.listdir(webcamPath), key = len)[-1]
        avgDiff[i] = os.path.getmtime(webcamPath + last) - os.path.getmtime(webcamPath + first)
        avgDiff[i] = avgDiff[i]/len(os.listdir(webcamPath))
    return avgDiff

def printFPS(folderNumber):
    avgDiff = calcAvgDiff(folderNumber)
    for i in range(len(avgDiff)):
        print('Webcam 1: ' + format(1/avgDiff[i], '.3f') +' fps')

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

def captureTest(folderNumber):
    numberOfWebcams = 4
    print('opening webcams... this could take a minute or two')
    webcam1 = cv2.VideoCapture(0)


    imageNumber = 1
    print('recording, press q to stop...')
    while webcam1.isOpened():
        ret1, frame1 = webcam1.read()
        cv2.imwrite('./captures/capture' + str(folderNumber) + '/webcam1/' + str(imageNumber)+ '.jpg', frame1)


        cv2.imshow('webcams', frame1)
        
        imageNumber = imageNumber + 1
        
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            break

###Main
folderNumber = createFolders()
capture(folderNumber, 0.5)
printLatency(folderNumber)
printFPS(folderNumber)
sync(folderNumber)
printLatency(folderNumber)

#subject name
#date time yearmonthday
#scenerio list
#subcategories list
#