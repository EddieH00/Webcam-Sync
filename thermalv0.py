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
        renderer.frame = camera_frame.color_argb8888
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
        camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

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

    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)
        scene = 1
        
        image = np.zeros(960, 1920, 3)
        while scene != len(scenerios[scenerioNumber-1]):
            print('Press q to finish recording ' + str(scenerios[scenerioNumber-1][scene]))
            while(1):

                with renderer.frame_condition:
                    if renderer.frame_condition.wait(150.0 / 1000.0):
                        imgt = renderer.frame.data

                image[0:480, 0:640, :] = img[0]
                image[0:480, 640:1280, :] = img[1]
                image[480:960, 320:960, :] = img[2]
                image[480:960, 960:1280, :] = img[3]
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


scenerioNumber, currentFolder = createFolders()
capture(scenerioNumber, currentFolder)