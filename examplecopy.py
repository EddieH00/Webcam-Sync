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


def lastWebcamToRecord(folder):
    


scenerioNumber, currentFolder = createFolders()
capture(scenerioNumber, currentFolder)
