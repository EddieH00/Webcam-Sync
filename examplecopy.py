from threading import Thread
import cv2
import os
import time
import numpy as np


#first item in each scenerio should be the name of the scenerio 
scenerioOne = ['Hands', 'wheel', 'lap', 'ipad', 'air']
scenerioTwo = ['Gaze', 'one', 'two', 'three', 'four', 'five', 'six', 'seven']
scenerios = [scenerioOne, scenerioTwo]


#creates folder structure
#captures > capture1 > webcam1, webcam2 etc.
#returns the folder number eg. captures > capture9 returns 9
def createFolders():
    print('Enter Name: ')
    name = input()
    print('Select Scenerio: ')
    for i in range(len(scenerios)):
        print('Enter ' + str(i + 1) +' for ' + scenerios[i][0])
    scenerioNumber = int(input())

    if not os.path.exists('./captures/'):
        os.makedirs('./captures/')

    timeInfo = time.localtime()
    timeFormat = str(timeInfo[0]) + '-' + str(timeInfo[1]) + '-'  + str(timeInfo[2]) + '_' + str(timeInfo[3]) + '-'  + str(timeInfo[4]) 
    currentFolder = name + '_' + scenerios[scenerioNumber-1][0] + '_' + timeFormat
    currentFolder = './captures/' + currentFolder

    os.makedirs(currentFolder)
    for i in range(1, len(scenerios[scenerioNumber-1])):
        subfolder = currentFolder + '/' + scenerios[scenerioNumber-1][i]
        os.makedirs(subfolder)
        for j in range(1, 5):
            os.makedirs(subfolder + '/webcam' + str(j))

    return scenerioNumber, currentFolder


class webcamThread(Thread):
    def __init__(self, webcamNumber, scenerioNumber, currentFolder):
        Thread.__init__(self)
        self.webcamNumber = webcamNumber
        self.scenerioNumber = scenerioNumber
        self.currentFolder = currentFolder
    def run(self):
        camCapture(self.webcamNumber, self.scenerioNumber, self.currentFolder)


def camCapture(webcamNumber, scenerioNumber, currentFolder):
    webcam = cv2.VideoCapture(webcamNumber)
    ret, frame = webcam.read()

    for i in range(1, len(scenerios[scenerioNumber-1])):
        imageNumber = 1
        subfolder = currentFolder + '/' + scenerios[scenerioNumber-1][webcamNumber]

        while webcam.isOpened():
            ret, frame = webcam.read()
            img[webcamNumber] = frame
            cv2.imwrite(subfolder + '/webcam' + str(webcamNumber) + '/' + str(imageNumber) + '.jpg', frame)
            imageNumber += 1

            if pauseThreads == True:
                break
        
        while pauseThreads == True:
            pass


def capture(scenerioNumber, currentFolder):
    global img
    img = np.zeros((4, 480, 640, 3), dtype='uint8')


    global pauseThreads
    pauseThreads = False

    web1 = webcamThread(0, scenerioNumber, currentFolder)
    web2 = webcamThread(1, scenerioNumber, currentFolder)
    web3 = webcamThread(2, scenerioNumber, currentFolder)
    web4 = webcamThread(3, scenerioNumber, currentFolder)

    web1.start()
    web2.start()
    web3.start()
    web4.start()

    while not img[0].any():
        pass
    
    scene = 1
    while scene != len(scenerios[scenerioNumber-1]):
        print('Press q to finish recording ' + str(scenerios[scenerioNumber-1][scene]))
        while(1):
            horizontal1 = np.concatenate((img[0], img[1]), axis=1)
            horizontal2 = np.concatenate((img[2], img[3]), axis=1)
            image = np.concatenate((horizontal1, horizontal2), axis = 0)
            cv2.imshow('webcams', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                pauseThreads = True
                scene += 1
                break
                
        if scene == len(scenerios[scenerioNumber-1]):
            input("Press Enter to finish")
            pauseThreads = False
        else:
            input("Press Enter to record " + scenerios[scenerioNumber-1][scene])
            pauseThreads = False


#finds which webcam has the latest timestamp for 1.jpg
#eg. if webcam 1 has 1.jpg at 12:00:01
#and webcam 2 has 1.jpg at 12:00:02 
#the function will return 2
def lastWebcamToRecord(folder):
    last = 1
    lastTimeStamp = os.path.getmtime(folder + 'webcam' + str(last) + '/1.jpg')
    for i in range(2, 5):
        if os.path.getmtime(folder + 'webcam' + str(i) + '/1.jpg') >= lastTimeStamp:
            last = i
            lastTimeStamp = os.path.getmtime(folder + 'webcam' + str(i) + '/' + '1.jpg')
    return last


#finds which webcam has the earliest recorded last frame
#eg if webcam 1 ends at 9.jpg at 12:00:01
#and webcam 2 ends at 7.jph at 12:00:02
#function will return timestamp 12:00:01
def firstWebcamToStop(folder):
    webcamPath = folder + 'webcam1/'
    lastIndex = sorted(os.listdir(webcamPath), key = len)[-1]
    firstTimeStamp = os.path.getmtime(webcamPath + lastIndex)
    for i in range(2, 5):
        webcamPath = folder + 'webcam' + str(i) + '/'
        index = sorted(os.listdir(webcamPath), key = len)[-1]
        timeStamp = os.path.getmtime(webcamPath + index)
        if timeStamp < firstTimeStamp:
            firstTimeStamp = timeStamp

    return firstTimeStamp

#input a given timestamp in os.path.getmtime format
#the function returns the frame in the folder that was captured
#closest to that time
#this function just searches linearly, it can definately be optimized with search algorithms
def closestFrameToTime(folder, time, webcamNumber):
    subFolder = folder + 'webcam' + str(webcamNumber) +'/'
    lastIndex = sorted(os.listdir(subFolder), key = len)[-1]
    lastIndex = int(lastIndex[:-4])
    closest = 1
    closestDiff = abs(os.path.getmtime(subFolder + str(closest) + '.jpg') - time)
    for i in range(lastIndex + 1):
        diff = abs(os.path.getmtime(subFolder + str(closest) + '.jpg') - time)
        if diff < closestDiff:
            closest = i
            closestDiff = diff
    return closest


def calcAverageLatency(folder):
    referenceWebcam = lastWebcamToRecord(folder)
    lastFrame = closestFrameToTime(firstWebcamToStop(folder))
    latency = [0] * 4
    for i in range(1, lastFrame + 1):
        for j in range(1, 5):
            referenceTime = os.path.getmtime(folder + 'webcam' + str(referenceWebcam) +'/' + str(i) + '.jpg')
            webTime = os.path.getmtime(folder + 'webcam' + str(j) +'/' + str(i) + '.jpg')
            latency[j] = latency[j] + (webTime - referenceTime)
    latency = latency / lastFrame
    return latency

def findFPS(folder):
    fps = [0] * 4
    for i in range(1, 5):
        subFolder = folder + 'webcam' + str(i) + +'/'
        first = sorted(os.listdir(subFolder), key = len)[0]
        last = sorted(os.listdir(subFolder), key = len)[-1]
        firstTime = os.path.getmtime(subFolder + first)
        lastTime = os.path.getmtime(subFolder + last)
        fps[i] = len(os.listdir(subFolder))/((lastTime - firstTime)/1000)
    return fps


scenerioNumber, currentFolder = createFolders()
capture(scenerioNumber, currentFolder)
print(findFPS(currentFolder + '/one/'))
