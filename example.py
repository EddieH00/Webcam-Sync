from threading import Thread
import cv2

class webcamThread(Thread):
    def __init__(self, webcamNumber):
        Thread.__init__(self)
        self.webcamNumber = webcamNumber
    def run(self):
        print("launching webcam " + str(self.webcamNumber) + "...")

def capture(webcamNumber):
    webcam = cv2.VideoCapture(webcamNumber)
    ret, frame = webcam.read()

    while webcam.isOpened():
        ret, frame = webcam.read()
        cv2.imshow('webcam ' + str(webcamNumber), frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

web1 = webcamThread(0)
web2 = webcamThread(1)

web1.start()
web2.start()