from threading import Thread
import cv2
import os
import time
import numpy as np

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
        print("launching webcam " + str(self.webcamNumber) + "...")
        camCapture(self.webcamNumber, self.scenerioNumber, self.currentFolder)
def camCapture(webcamNumber, scenerioNumber, currentFolder):
    webcam = cv2.VideoCapture(webcamNumber)
    ret, frame = webcam.read()
    subfolder = currentFolder + '/' + scenerios[scenerioNumber-1][webcamNumber]
    imageNumber = 1

    while webcam.isOpened():
        ret, frame = webcam.read()
        cv2.imwrite(subfolder + '/webcam' + str(webcamNumber) + '/' + str(imageNumber) + '.jpg', frame)
        cv2.imshow('webcam ' + str(webcamNumber), frame)
        imageNumber += 1
        
#finds the lowest final capture number
#eg. if webcam1 records 1.jpg, 2.jpg... 89.jpg
#and webcam 2 records 1.jpg, 2.jpg... 88.jpg
#this function will return 88
def findLowestLastCapture(path):
    webcamPath = path + 'webcam1/'
    lowestIndex = sorted(os.listdir(webcamPath), key = len)[-1]
    lowestIndex = int(lastIndex[:-4])
    for i in range(1, 4):
        webcamPath = path + 'webcam' + str(i + 1) + '/'
        lastIndex = sorted(os.listdir(webcamPath), key = len)[-1]
        lastIndex = int(lastIndex[:-4])
        lowestIndex = min(lowestIndex, lastIndex)
    return lowestIndex
    
def calcAvgLatency(path):
    latency = [0]*4
    lastImage = findLowestLastCapture(path)
    for i in range(4):
        webcamPath = path + 'webcam' + str(i+1) + '/'
        for j in range(lastImage):
            lastWebcamPath = path + 'webcam4' + '/' + str(j+ 1) +'.jpg'
            latency[i] = latency[i] + os.path.getmtime(webcamPath + str(j+1) + '.jpg') - os.path.getmtime(lastWebcamPath)
        latency[i] = latency[i] / lastImage


def calcAvgDiff(path):
    avgDiff = [0]*4
    first = '0.jpg'
    last = str(findLowestLastCapture(path)) + '.jpg'
    for i in range(4):
        webcamPath = path + 'webcam' + str(i+1) + '/'
        avgDiff[i] = os.path.getmtime(webcamPath + last) - os.path.getmtime(webcamPath + first)
        avgDiff[i] = avgDiff[i]/len(os.listdir(webcamPath))
    return avgDiff


def sync(scenerioNumber, currentFolder):
    for i in range(1, len(scenerios[0])):
        path = currentFolder + '/' + scenerios[scenerioNumber-1][i] +'/'
        avgLatency = calcAvgLatency(path)
        avgDiff = calcAvgDiff(path)
        changed = [0, 0, 0, 0]
        for i in range(len(avgDiff)):
            path = path + 'webcam' + str(i+1) + '/'
            numberOfFrames = abs(round(avgLatency[i] / avgDiff[i]))
            if numberOfFrames != 0:
                changed[i] = 1
                print('webcam ' + str(i + 1) + ' synced')
                for j in range(len(os.listdir(path))):
                    os.rename(path + str(j+1) + '.jpg', path + str(j+1-numberOfFrames) + '.jpg')
    return changed





def capture(scenerioNumber, currentFolder):
    web1 = webcamThread(0, scenerioNumber, currentFolder)
    web2 = webcamThread(1, scenerioNumber, currentFolder)
    web3 = webcamThread(2, scenerioNumber, currentFolder)
    web4 = webcamThread(3, scenerioNumber, currentFolder)

    web1.start()
    web2.start()
    web3.start()
    web4.start()

scenerioNumber, currentFolder = createFolders()
capture(scenerioNumber, currentFolder)
sync(scenerioNumber, currentFolder)