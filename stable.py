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



def on_event(camera, event_type, event_status, renderer):
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
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the Renderer object.
    """
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return

        # Claim the renderer.
        # This is required in case of multiple cameras.
        renderer.busy = True
        renderer.camera = camera

        # Indicate the first frame has not come in yet.
        # This is required to properly resize the rendering window.
        renderer.first_frame = True

        # Set a custom color palette.
        # Other options can set in a similar fashion.
        camera.color_palette = SeekCameraColorPalette.TYRIAN

        # Start imaging and provide a custom callback to be called
        # every time a new frame is received.
        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        # Check that the camera disconnecting is one actually associated with
        # the renderer. This is required in case of multiple cameras.
        if renderer.camera == camera:
            # Stop imaging and reset all the renderer state.
            camera.capture_session_stop()
            renderer.camera = None
            renderer.frame = None
            renderer.busy = False

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return

#first item in each scenerio should be the name of the scenerio 
hands = ['hands wheel', 'hands lap', 'hands ipad', 'hands air']
gazeone = ['gaze straight', 'gaze left mirror', 'gaze right mirror', ' gaze rearview mirror']
gazetwo = ['gaze left window', 'gaze right window', 'gaze ipad']
scenerios = hands + gazeone + gazetwo

def createFolders():
    name = input('Enter Name: ')

    if not os.path.exists('./captures/'):
        os.makedirs('./captures/')

    timeInfo = time.localtime()
    timeFormat = str(timeInfo[0]) + '-' + str(timeInfo[1]) + '-'  + str(timeInfo[2]) + '_' + str(timeInfo[3]) + '-'  + str(timeInfo[4]) 
    currentFolder = name + '_' + timeFormat
    currentFolder = './captures/' + currentFolder

    os.makedirs(currentFolder)
    for i in range(len(scenerios)):
        subfolder = currentFolder + '/' + scenerios[i]
        os.makedirs(subfolder)
        for j in range(1, 5):
            os.makedirs(subfolder + '/webcam' + str(j))
        os.makedirs(subfolder + '/seek_jpg/')
        os.makedirs(subfolder+ '/seek_temperatures/')

    return currentFolder


class webcamThread(Thread):
    def __init__(self, webcamNumber, currentFolder):
        Thread.__init__(self)
        self.webcamNumber = webcamNumber
        self.currentFolder = currentFolder
    def run(self):
        camCapture(self.webcamNumber, self.currentFolder)

def camCapture(webcamNumber, currentFolder):
    webcam = cv2.VideoCapture(webcamNumber)
    ret, frame = webcam.read()
    img[webcamNumber] = frame

    print('webcam ' + str(webcamNumber) + ' ready')
    while start is False:
        pass

    for i in range(len(scenerios)):
        imageNumber = 1
        subfolder = currentFolder + '/' + scenerios[i]

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

def timer():
    global pauseThreads
    for i in range(len(scenerios)):
        time.sleep(10)
        pauseThreads = True
        while pauseThreads is True:
            pass

def capture(currentFolder):
    global img
    img = np.zeros((4, 480, 640, 3), dtype='uint8')

    global pauseThreads
    global start
    start = False
    pauseThreads = False

    web1 = webcamThread(0, currentFolder)
    web2 = webcamThread(1, currentFolder)
    web3 = webcamThread(2, currentFolder)
    web4 = webcamThread(3, currentFolder)
    timerThread = Thread(target=timer)

    web1.start()
    web2.start()
    web3.start()
    web4.start()

    print('webcams are loading up... get ready for: ' + scenerios[0])

    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)
        scene = 0
        image = np.zeros((960, 1920, 3), dtype='uint8')
        imgtemps = np.zeros((156,206), dtype='uint8')
        
        while not (img[0].any() and img[1].any() and img[2].any() and img[3].any()):
            pass
    
        start = True
        timerThread.start()
        while scene != len(scenerios):
            tempNumber = 1
            while(1):
                
                with renderer.frame_condition:
                    if renderer.frame_condition.wait(150.0 / 1000.0):
                        imgtemps = renderer.frame.data
                        file = open(currentFolder + '/' + scenerios[scene] + '/seek_temperatures/' + str(tempNumber) + '.csv', 'w')
                        np.savetxt(file, imgtemps, fmt="%.1f")
                        imgu8 = ((imgtemps-10)*256/40).astype(np.uint8)
                        imgjpg = cv2.applyColorMap(imgu8, cv2.COLORMAP_JET)
                        imgt_rescaled = cv2.resize(imgjpg, dsize=(640, 480))
                        cv2.imwrite(currentFolder + '/' + scenerios[scene] + '/seek_jpg/' + str(tempNumber) + '.jpg', imgt_rescaled)
                        image[0:480, 1280:, :] = imgt_rescaled[:,:,0:3]
                        tempNumber = tempNumber + 1


                image[0:480, 0:640, :] = img[0]
                image[0:480, 640:1280, :] = img[1]

                image[480:960, 320:960, :] = img[2]
                image[480:960, 960:1600, :] = img[3]

                cv2.imshow('webcams', image)
                cv2.setWindowProperty('webcams', cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)
                
                if pauseThreads is True:
                    cv2.destroyAllWindows()
                    scene += 1
                    break
                    
            if scene == len(scenerios):
                input("Press Enter to finish")
                pauseThreads = False
            else:
                input("Press Enter to record " + scenerios[scene])
                pauseThreads = False

#print(scenerios)
currentFolder = createFolders()
capture(currentFolder)
#opencv2 on top
#automatically q quit
#timer 10 seconds
#playback laggy? idk
#don't stop between hands and gaze