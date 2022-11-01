import os
import time
import cv2

scenerioOne = ['Scenerio One', 'one', 'two', 'three', 'four']
scenerioTwo = ['Scenerio Two', 'one', 'two', 'three', 'four']
scenerioThree = ['Scenerio Three', 'one', 'two', 'three', 'four']
scenerioFour = ['Scenerio Four', 'one', 'two', 'three', 'four']
scenerios = [scenerioOne, scenerioTwo, scenerioThree, scenerioFour]

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
for i in range(1, len(scenerios[0])):
    subfolder = currentFolder + '/' + scenerios[scenerioNumber-1][i]
    os.makedirs(subfolder)
    for j in range(1, 5):
        os.makedirs(subfolder + '/webcam' + str(j))

webcam1 = cv2.VideoCapture(0)
webcam2 = cv2.VideoCapture(1)
webcam3 = cv2.VideoCapture(2)
webcam4 = cv2.VideoCapture(3)

#junk frames
ret1, frame1 = webcam1.read()
ret2, frame2 = webcam2.read()
ret3, frame3 = webcam3.read()    
ret4, frame4 = webcam4.read()

imageNumber = 1

for i in range(1, len(scenerios[0])):
    while(1):
        print('recording... press space to stop')
        subfolder = currentFolder + '/' + scenerios[scenerioNumber-1][i]
        ret1, frame1 = webcam1.read()
        cv2.imwrite(subfolder + '/webcam1' + str(imageNumber) + '.jpg', frame1)

        ret2, frame2 = webcam2.read()
        cv2.imwrite(subfolder + '/webcam2/' + str(imageNumber) + '.jpg', frame2)

        ret3, frame3 = webcam3.read()
        cv2.imwrite(subfolder + '/webcam3' + str(imageNumber) + '.jpg', frame3)

        ret1, frame4 = webcam4.read()
        cv2.imwrite(subfolder + '/webcam4' + str(imageNumber) + '.jpg', frame4)

        if cv2.waitKey(1) & 0xFF ==ord(' '):
            print('recording scene done, press space to continue')
            break

    while(1):
        if cv2.waitKey(1) & 0xFF ==ord(' '):
            break


