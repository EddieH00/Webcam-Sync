from threading import Thread, Condition
import cv2
import os
import time
import numpy as np
import pyaudio
import wave
import random
import string
import keyboard
import pygetwindow as gw
import pyautogui

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
input_device = 4

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
    #print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        print("Thermal camera ready...")
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

#returns in format [./currentfolder/one/, ./currentfolder/two/, ./currentfolder/]
def createFolders():
    name = input('Enter participant name: ')
    if not os.path.exists('./captures/'):
        os.makedirs('./captures/')
    timeInfo = time.localtime()
    timeFormat = str(timeInfo[0]) + '-' + str(timeInfo[1]) + '-'  + str(timeInfo[2]) + '_' + str(timeInfo[3]) + '-'  + str(timeInfo[4]) 
    currentFolder = name + '_' + timeFormat
    currentFolder = './captures/' + currentFolder +'/'
    os.makedirs(currentFolder)

    folders = ['enterSimulator/','driving/']
    for i in range(len(folders)):
        subfolder = currentFolder + folders[i]
        os.makedirs(subfolder)
        for j in range(1, 5):
            os.makedirs(subfolder + 'webcam' + str(j))
        os.makedirs(subfolder + 'seek_jpg/')
        os.makedirs(subfolder+ 'seek_temperatures/')
    folders = [currentFolder+x for x in folders]
    folders.append(currentFolder)
    return folders


#webcamThread captures a webcam to the folder and then closes
class webcamThread(Thread):
    def __init__(self, webcamNumber, folder):
        Thread.__init__(self)
        self.webcamNumber = webcamNumber
        self.folder = folder
    def run(self):
        camCapture(self.webcamNumber, self.folder)
def camCapture(webcamNumber, folder):
    webcam = cv2.VideoCapture(webcamNumber)
    ret, frame = webcam.read()
    img[webcamNumber] = frame

    print('webcam ' + str(webcamNumber + 1) + ' ready')
    
    #start is a global variable to stop one webcam from recording if the others are not ready
    if start is False:
        while start is False:
            pass

    while webcam.isOpened():
        ret, frame = webcam.read()
        if ret is True:
            img[webcamNumber] = frame
            imgName = str(time.time_ns()) +'.jpg'
            cv2.imwrite(folder +'webcam' + str(webcamNumber+1) + '/' + imgName, frame)

        #stop recording is a global variable used to control the webcam threads
        if stopRecording == True:
            break



def record():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    #for a specific device number add: input_device_index = input_device
    #no device number uses windows default

    frames = []
    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        print("Done recording")
    except Exception as e:
        print(str(e))

    sample_width = p.get_sample_size(FORMAT)

    stream.stop_stream()
    stream.close()
    p.terminate()

    return sample_width, frames


def record_to_file(file_path):
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(CHANNELS)
    sample_width, frames = record()
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def capture(folders):
    #img is a global np array to capture all webcam footage
    global img
    global stopRecording
    global start

     #for loop to record enter simulator, and driving capture   
    for recordingRound in range(2):
        img = np.zeros((4, 480, 640, 3), dtype='uint8')
        start = False
        stopRecording = False

        web1 = webcamThread(0, folders[recordingRound])
        web2 = webcamThread(1, folders[recordingRound])
        web3 = webcamThread(2, folders[recordingRound])
        web4 = webcamThread(3, folders[recordingRound])

        web1.start()
        web2.start()
        web3.start()
        web4.start()

        print('please wait for the webcams to open...')
        with SeekCameraManager(SeekCameraIOType.USB) as manager:
            # Start listening for events.
            renderer = Renderer()
            manager.register_event_callback(on_event, renderer)
            image = np.zeros((960, 1920, 3), dtype='uint8')
            imgtemps = np.zeros((156,206), dtype='uint8')
            
            #this line waits for all the webcams to load an image to proceed
            while not (img[0].any() and img[1].any() and img[2].any() and img[3].any()):
                pass

            print('webcams ready. After the cameras open, click on the window, and then press \'q\' to stop recording')
            input("Press Enter to start recording")

            start = True
            while(1):
                with renderer.frame_condition:
                    if renderer.frame_condition.wait(150.0 / 1000.0):
                        imgtemps = renderer.frame.data
                        capTime = time.time_ns()
                        imgName = str(capTime) +'.jpg'
                        file = open(folders[recordingRound] + 'seek_temperatures/' + str(capTime) + '.csv', 'w')
                        np.savetxt(file, imgtemps, fmt="%.1f")
                        imgu8 = ((imgtemps-10)*256/40).astype(np.uint8)
                        imgjpg = cv2.applyColorMap(imgu8, cv2.COLORMAP_JET)
                        imgt_rescaled = cv2.resize(imgjpg, dsize=(640, 480))
                        cv2.imwrite(folders[recordingRound] + 'seek_jpg/' + imgName, imgt_rescaled)
                        image[0:480, 1280:, :] = imgt_rescaled[:,:,0:3]

                image[0:480, 0:640, :] = img[0]
                image[0:480, 640:1280, :] = img[1]

                image[480:960, 320:960, :] = img[2]
                image[480:960, 960:1600, :] = img[3]

                cv2.imshow('webcams', image)
                cv2.setWindowProperty('webcams', cv2.WND_PROP_TOPMOST, 1)

                if cv2.waitKey(1) & 0xFF == ord('q'):                
                    cv2.destroyAllWindows()
                    stopRecording = True #closes all the threads
                    break

            if recordingRound == 0: #if this is the first iteration, record audio
                print("Recording done.")
                input("Press Enter to start recording audio")
                print("Microphone is activated, recording...")
                print('Press Ctrl+C to stop the recording')
                res = folders[-1] +'audio'
                record_to_file(res + '.wav')
                print("Audio recording done! Result written to " + str(res) + ".wav")


folders = createFolders()
capture(folders)

#######################################################################
#bugs:
#0 the audio is not recording properly still.
#Things I've tried:
#a few different sampling rates and channel combinations. These seem  to change the length of the recording which is... weird
#using different device numbers that correspond to differnt API's (MME, Directsound, WASAPI, ASIO)
#using no device number to use windows default and matching the settings 48000 hz, 2 channels 16 bit
#
#1. when capture folder is empty, the webcams open and then the program ends without capturing. Unable to replicate
#2. there are white bars on webcam images. This appeared one day without changes to the code. Unknown cause
#2a. update: they are gone now. But you can see how it looked in the capture folder. Gave me a damn heart attack, idk if they will com eback
#3. Press q to close the cv2 window
#3a. normal way is just cv2.waitKey(0) & 0xFF
#       problem with this is that the lab technician needs to click on the cv2 window before pressing q works
#3b. I changed it to  "if keyboard.is_pressed('q'):"
#       this works when runnign from vscode terminal. However when running it from a .bat script, it causes problems.
#       pressing q does not close unless you click the window first




#source: https://roytuts.com/python-voice-recording-through-microphone-for-arbitrary-time-using-pyaudio/
