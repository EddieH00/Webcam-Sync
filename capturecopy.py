from threading import currentThread
import cv2
import os
import time
import numpy as np

numberOfWebcams = 4
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

#currently capture is fixed at 4 webcams
#opens 4 webcams. Saves the frames and displays the live stream.
#input is the folder number it is capturing to
def capture(scenerioNumber, currentFolder):
    print('webcams are loading, this could take a minute...')
    webcam1 = cv2.VideoCapture(0)
    webcam2 = cv2.VideoCapture(1)
    webcam3 = cv2.VideoCapture(2)
    webcam4 = cv2.VideoCapture(3)
    
    
    #junk frames
    ret1, frame1 = webcam1.read()
    ret2, frame2 = webcam2.read()
    ret3, frame3 = webcam3.read()    
    ret4, frame4 = webcam4.read()


    for i in range(1, len(scenerios[scenerioNumber-1])):
        imageNumber = 1
        print('recording ' + scenerios[scenerioNumber-1][i] + '... press q to stop')
        while webcam1.isOpened():

            subFolder = currentFolder + '/' + scenerios[scenerioNumber-1][i]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out1 = cv2.VideoWriter(subFolder + '/webcam1/cap.avi', fourcc, 30.0, (640, 480))
            out2 = cv2.VideoWriter(subFolder + '/webcam2/cap.avi', fourcc, 30.0, (640, 480))
            out3 = cv2.VideoWriter(subFolder + '/webcam3/cap.avi', fourcc, 30.0, (640, 480))
            out4 = cv2.VideoWriter(subFolder + '/webcam4/cap.avi', fourcc, 30.0, (640, 480))

            ret1, frame1 = webcam1.read()
            out1.write(frame1)

            ret2, frame2 = webcam2.read()
            out2.write(frame2)

            ret3, frame3 = webcam3.read()
            out3.write(frame3)

            ret4, frame4 = webcam4.read()
            out4.write(frame4)

            horizontal1 = np.concatenate((frame1, frame2), axis=1)
            horizontal2 = np.concatenate((frame3, frame4), axis=1)
            image = np.concatenate((horizontal1, horizontal2), axis = 0)
            cv2.imshow('webcams', image)

            imageNumber = imageNumber + 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

        input("Recording done, press Enter to continue...")



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

def calcAvgLatency(path):
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
    
def printLatency(scenerioNumber, currentFolder):
    for i in range(1, len(scenerios[0])):
        path = currentFolder + '/' + scenerios[scenerioNumber-1][i] +'/'    
        latency = calcAvgLatency(path)
        for i in range(len(latency)):
            latency[i] = round(latency[i], 3)
            print('latency of webcam ' + str(i + 1) + ' relative to webcam ' +str(numberOfWebcams) +': '  + format(latency[i], '.3f') +' s')


def calcAvgDiff(path):
    avgDiff = [0]*numberOfWebcams
    for i in range(numberOfWebcams):
        webcamPath = path + 'webcam' +str(i+1) + '/'
        first = sorted(os.listdir(webcamPath), key = len)[0]
        last = sorted(os.listdir(webcamPath), key = len)[-1]
        avgDiff[i] = os.path.getmtime(webcamPath + last) - os.path.getmtime(webcamPath + first)
        avgDiff[i] = avgDiff[i]/len(os.listdir(webcamPath))
    return avgDiff

def printFPS(scenerioNumber, currentFolder):
    for i in range(1, len(scenerios[scenerioNumber-1])):
        path = currentFolder + '/' + scenerios[scenerioNumber-1][i] + '/'
        avgDiff = calcAvgDiff(path)
        for i in range(len(avgDiff)):
            print('Webcam ' + str(i+1) + ': ' + format(1/avgDiff[i], '.3f') +' fps')

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


###Main
scenerioNumber, currentFolder = createFolders()
capture(scenerioNumber, currentFolder)
printLatency(scenerioNumber, currentFolder)
printFPS(scenerioNumber, currentFolder)
sync(scenerioNumber, currentFolder)
printLatency(scenerioNumber, currentFolder)