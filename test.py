import os
folderNumber = 6
numberOfWebcams = 4

###synchronization
#finds which webcam has the latest creation time
path = './captures/capture'+ str(folderNumber) + '/'
latest = 1
latestTimeStamp = os.path.getmtime(path + 'webcam' + str(latest) + '/' + '1.jpg')
for i in range(2, numberOfWebcams + 1):
    if os.path.getmtime(path + 'webcam' + str(i) + '/' + '1.jpg') >= latestTimeStamp:
        latest = i
        latestTimeStamp = os.path.getmtime(path + 'webcam' + str(i) + '/' + '1.jpg')

print(latest)
print(latestTimeStamp)

#finds the closest starting point
closestTimeStamps = [0]*numberOfWebcams
for i in range(1, numberOfWebcams+ 1):
    if i != latest:
        imageNumber = 1
        timeStamp = os.path.getmtime(path + 'webcam' + str(i) + '/' + str(imageNumber) + '.jpg')
        distance = abs(latestTimeStamp - timeStamp)
        while 1:
            if newDistance < distance:
                distance = newDistance
            else:
                break

                        imageNumber = imageNumber + 1
            timeStamp = os.path.getmtime(path + 'webcam' + str(i) + '/' + str(imageNumber) + '.jpg')
            newDistance = abs(latestTimeStamp - timeStamp)