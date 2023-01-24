from threading import Thread, Condition
import cv2
import os
import time
import numpy as np

from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCamera,
    SeekFrame,
)

class Renderer:
    """Contains camera and image data required to render images to the screen."""

    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):
    """Async callback fired whenever a new frame is available.

    Parameters
    ----------
    _camera: SeekCamera
        Reference to the camera for which the new frame is available.
    camera_frame: SeekCameraFrame
        Reference to the class encapsulating the new frame (potentially
        in multiple formats).
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the renderer object.
    """

    # Acquire the condition variable and notify the main thread
    # that a new frame is ready to render. This is required since
    # all rendering done by OpenCV needs to happen on the main thread.
    with renderer.frame_condition:
        renderer.frame = camera_frame.thermography_float
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, _user_data):
    """Async callback fired whenever a camera event occurs.

    Parameters
    ----------
    camera: SeekCamera
        Reference to the camera on which an event occurred.
    event_type: SeekCameraManagerEvent
        Enumerated type indicating the type of event that occurred.
    event_status: Optional[SeekCameraError]
        Optional exception type. It will be a non-None derived instance of
        SeekCameraError if the event_type is SeekCameraManagerEvent.ERROR.
    _user_data: None
        User defined data passed to the callback. This can be anything
        but in this case it is None.
    """
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        # Open a new CSV file with the unique camera chip ID embedded.
        try:
            file = open("thermography-" + camera.chipid + ".csv", "w")
        except OSError as e:
            print("Failed to open file: %s" % str(e))
            return

        # Start streaming data and provide a custom callback to be called
        # every time a new frame is received.
        camera.register_frame_available_callback(on_frame, file)
        camera.capture_session_start(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        camera.capture_session_stop()

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return

#first item in each scenerio should be the name of the scenerio 
scenerioOne = ['Hands', 'wheel', 'lap', 'ipad', 'air']
scenerioTwo = ['Gaze', 'one', 'two', 'three', 'four', 'five', 'six', 'seven']
scenerios = [scenerioOne, scenerioTwo]


def createFolders():
    name = input('Enter Name: ')
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
        os.makedirs(subfolder + '/seek_jpg/')
        os.makedirs(subfolder+ '/seek_temperatures/')

    return scenerioNumber, currentFolder +'/'


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
        subfolder = currentFolder + '/' + scenerios[scenerioNumber-1][i]

        while webcam.isOpened():
            ret, frame = webcam.read()
            if ret is True:
                img[webcamNumber] = frame
                cv2.imwrite(subfolder + '/webcam' + str(webcamNumber+1) + '/' + str(imageNumber) + '.jpg', frame)

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

    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)
        scene = 1
        
        image = np.zeros((960, 1920, 3), dtype='uint8')
        imgt = np.zeros((156,206), dtype='uint8')
        while scene != len(scenerios[scenerioNumber-1]):
            print('Press q to finish recording ' + str(scenerios[scenerioNumber-1][scene]))
            while(1):
                
                with renderer.frame_condition:
                    if renderer.frame_condition.wait(150.0 / 1000.0):
                        imgt = renderer.frame.data

                imgc = cv2.applyColorMap(imgt, cv2.COLORMAP_JET)


                image[0:480, 0:640, :] = img[0]
                image[0:480, 640:1280, :] = img[1]
                imgt_rescaled = cv2.resize(imgc, dsize=(640, 480))
                image[0:480, 1280:, :] = imgt_rescaled[:,:,0:3]
                image[480:960, 320:960, :] = img[2]
                image[480:960, 960:1600, :] = img[3]
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

def calcFPS(folder):
    '''
    Parameters:
        folder: folder where frames are stored eg. './captures/'
    '''
    first = sorted(os.listdir(folder), key = len)[0]
    last = sorted(os.listdir(folder), key = len)[-1]
    firstTime = os.path.getmtime(folder + first)
    lastTime = os.path.getmtime(folder + last)
    fps = len(os.listdir(folder))/((lastTime - firstTime))
    return fps

def findFPS(folder):
    fps = [0] * 5
    ifps = [0] * 5
    for i in range(1, 5):
        subFolder = folder + 'webcam' + str(i) +'/'
        first = sorted(os.listdir(subFolder), key = len)[0]
        last = sorted(os.listdir(subFolder), key = len)[-1]
        firstTime = os.path.getmtime(subFolder + first)
        lastTime = os.path.getmtime(subFolder + last)
        fps[i-1] = len(os.listdir(subFolder))/((lastTime - firstTime))
        ifps[i-1] = 1/fps[i-1]
    
    return fps, ifps

def sync(scenerioNumber, currentFolder):
    for i in range(1, len(scenerios[0])):
        path = currentFolder + '/' + scenerios[scenerioNumber-1][i] +'/'
        avgLatency = calcAverageLatency(path)
        fps, avgDiff = findFPS(path)
        changed = [0, 0, 0, 0]
        for j in range(len(avgDiff)):
            path = path + 'webcam' + str(j+1) + '/'
            numberOfFrames = abs(round(avgLatency[j] / avgDiff[j]))
            if numberOfFrames != 0:
                changed[j] = 1
                #print('webcam ' + str(j + 1) + ' synced')
                for k in range(len(os.listdir(path))):
                    os.rename(path + str(k+1) + '.jpg', path + str(k+1-numberOfFrames) + '.jpg')
    return changed

def printFPS(folder, scenerioNumber):
    with open(folder + '/fps.txt', 'w') as f:
        for i in range(1, len(scenerios[scenerioNumber-1])):
            f.write('scenerio: ' + scenerios[scenerioNumber-1][i] + '\n')
            for cam in range(1, 5):
                path = folder + scenerios[scenerioNumber-1][i] +'/webcam' + str(cam) + '/'
                fps = calcFPS(path)
                f.write('webcam ' + str(cam) + ' fps: ' + str(fps) + '\n')
            path = folder + scenerios[scenerioNumber-1][i] + '/seek_jpg/'
            fps = calcFPS(path)
            f.write('seek fps: ' + str(fps) + '\n\n')

                
scenerioNumber, currentFolder = createFolders()
capture(scenerioNumber, currentFolder)
printFPS(currentFolder, scenerioNumber)