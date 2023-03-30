import os
import shutil
def createGlobalList(folder):
    '''
    takes a folder of images and returns a list of their timestamps

    params
    folder is a string in format './captures/eddie/hands/webcam1/
    
    returns timestamps
    timestamps is a sorted folder of ints
    '''
    timestamps = []
    for file in os.listdir(folder):
        timestamps.append(int(file[:-4]))
    timestamps.sort()

    return timestamps



from bisect import bisect_left
def getClosestFrame(timestamps, timestamp):
    '''
    finds the closest time in timestamps to timestamp
    needs timestamps to be global and sorted

    params
    timestamp- int, time in time.time_ns()

    return
    closest timestamp in int
    '''
    pos = bisect_left(timestamps, timestamp)
    if pos == 0:
        return timestamps[0]
    if pos == len(timestamps):
        return timestamps[-1]
    before = timestamps[pos - 1]
    after = timestamps[pos]
    if after - timestamp < timestamp - before:
        return after
    else:
        return before




def sync(folder, start, end, fps):
    '''
    takes a folder of sequences and creates a synchronized copy

    params
    folder- str, form of './captures/participantOne/ 
    folder should have subfolders eg. /participantOne/ ls [driving/, simulator/, speaking/]
    start- desired sync start time in the form of time.time_ns()
    end- desired end time in the form of time.time_ns()
    fps- desired frame rate to be synced at
    '''

    for subFolder in os.listdir(folder):
    #subFolder are ./folder/air or ./folder/hands
        syncedFolder = folder + subFolder + '_synced'
        if not os.path.exists(syncedFolder):
            os.makedirs(syncedFolder)
        
        #syncedCams = []
        for camSubFolder in os.listdir(folder+subFolder):
            currentFolder = folder + subFolder +'/' +camSubFolder +'/'
            currentSyncFolder = syncedFolder +'/' +camSubFolder +'_synced/'

            #camFolders are the webcam capture folders
            #syncedCams.append(camSubFolder +'_synced')
            if not os.path.exists(currentSyncFolder):
                os.makedirs(currentSyncFolder)

            increment = (1/fps)*1000000000
            frameNumber = 1
            #creates a global list called timestamps that is a list of all the frames in the folder
            timestamps = createGlobalList(currentFolder)
            cur = start
            while cur < end:
                frame = getClosestFrame(timestamps, cur)
                
                orig = currentFolder + str(frame) + '.jpg'
                dest = currentSyncFolder + str(frameNumber) + '.jpg'
                shutil.copy(orig, dest)

                frameNumber += 1
                cur += increment

def changeFPS(folder, newLast, newFolder):
    if not os.path.exists(newFolder):
        os.makedirs(newFolder)
    lastImage = sorted(os.listdir(folder), key = len)[-1]
    lastImage = int(lastImage[:-4])
    print(lastImage)
    iterate = lastImage / newLast
    current = 1
    counter = 1
    while counter <= newLast:
        orig = folder + str(int(round(current))) + '.jpg'
        dest = newFolder + str(counter) + '.jpg'
        shutil.copy(orig, dest)

        counter += 1
        current += iterate
        print(current)
    return 0

#print(calcFPS('./captures/Akshay_drive_new_2023-2-23_12-21/driving/webcam4'))
#sync("./captures/Akshay_drive_new_2023-2-23_12-21/", 1677184118188668600, 1677184118188668600+120.714*1000000000, 30.01061344 )
#folder = './captures/Akshay_drive_new_2023-2-23_12-21_2/driving/webcam1/'
#timestamps = createGlobalList(folder)
changeFPS('./captures/Akshay_drive_new_2023-2-23_12-21/driving/simulator/', 3623, './captures/Akshay_drive_new_2023-2-23_12-21/driving_synced/simulator_synced/')