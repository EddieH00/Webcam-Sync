import cv2
import numpy as np
from PIL import Image
import os

def extractFrames(video, folder):
    '''
    takes a video, creates a folder, and extract it's frames as jpg

    params
    video- str, path to video
    folder- str- path to output folder
    '''
    vidcap = cv2.VideoCapture(video)
    success,image = vidcap.read()
    count = 1
    path = folder
    if not os.path.exists(path):
        os.makedirs(path)

    while success:
        cv2.imwrite(path + str(count) + '.jpg', image)     # save frame as JPEG file      
        success,image = vidcap.read()
        count += 1


def addText(img):
    vOffset, hOffset = 50, 50
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    fontScale              = 1
    fontColor              = (0,255,255)
    thickness              = 2
    lineType               = cv2.LINE_4

    bottomLeftCornerOfText = (0+hOffset, 0 +vOffset)
    cv2.putText(img,'SIMULATION', bottomLeftCornerOfText, font, fontScale,fontColor,thickness,lineType)

    bottomLeftCornerOfText = (640 + hOffset,vOffset)
    cv2.putText(img,'OVERHEAD', bottomLeftCornerOfText, font, fontScale,fontColor,thickness,lineType)

    bottomLeftCornerOfText = (640 + 640+ hOffset,vOffset)
    cv2.putText(img,'TABLET', bottomLeftCornerOfText, font, fontScale,fontColor,thickness,lineType)

    bottomLeftCornerOfText = (hOffset, 480+vOffset)
    cv2.putText(img,'PROFILE', bottomLeftCornerOfText, font, fontScale,fontColor,thickness,lineType)

    bottomLeftCornerOfText = (640 + hOffset,480 +vOffset)
    cv2.putText(img,'FRONT', bottomLeftCornerOfText, font, fontScale,fontColor,thickness,lineType)

    bottomLeftCornerOfText = (640 + 640 + hOffset,  480 +vOffset)
    cv2.putText(img,'THERMAL', bottomLeftCornerOfText, font, fontScale,fontColor,thickness,lineType)

    return img


def createVideo(folder, fps, start=1, stop=0):
    '''
    creates a video from a collection of frames
    folder should have subfolders
    each subfolders should have frames as 1.jpg, 2.jpg ...

    param
    folder (str)- the location of the frames in form './folder/
    fps (int)- desired fps of the output
    start (int) = 1- desired first frame
    stop (int) = 0 desired last frame, set to 0 for no stopping frame
    '''
    if stop == 0:
        stop = len(os.listdir(folder+'webcam1_synced/'))-1

    image = np.zeros((960, 1920, 3), dtype='uint8')

    video_name = folder + 'video.mp4'

    width, height = 1920, 960
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    for frame in range(start, stop):
        print(str(int(frame/stop*100)) + ' percent done')
        jpg = Image.open(folder + 'webcam1_synced/' + str(frame) + '.jpg')
        image[0:480, 640:1280, :] = np.asarray(jpg)
        
        jpg = Image.open(folder + 'webcam2_synced/' + str(frame) + '.jpg')
        image[480:960, 640:1280, :] = np.asarray(jpg)
        
        jpg = Image.open(folder + 'webcam3_synced/' + str(frame) + '.jpg')
        image[480:960, 0:640, :] = np.asarray(jpg)
        
        jpg = Image.open(folder + 'webcam4_synced/' + str(frame) + '.jpg')
        image[0:480, 1280:1920, :] = np.asarray(jpg)

        jpg = Image.open(folder + 'seek_jpg_synced/' + str(frame) + '.jpg')
        image[480:960, 1280:1920, :] = np.asarray(jpg)

        jpg = Image.open(folder + 'simulator_synced/' + str(frame+33) + '.jpg')
        rescaled = cv2.resize(np.asarray(jpg), dsize=(640, 480))
        image[0:480, 0:640, :] = np.asarray(rescaled)

        image = addText(image)
        
        video.write(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    cv2.destroyAllWindows()
    video.release()

createVideo('./captures/Akshay_drive_new_2023-2-23_12-21/driving_synced/', 30, start=1, stop=0)
#extractFrames('./captures/Akshay_drive_new_2023-2-23_12-21/Presentation2.mp4', './captures/Akshay_drive_new_2023-2-23_12-21/driving/simulator/')