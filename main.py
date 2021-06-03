import cv2
import mediapipe as mp
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

class handDetector():
    def __init__(self,mode=False,maxHands=2,detectionCon=0.5,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands= mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands,self.detectionCon,self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        
    
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,handLms,self.mpHands.HAND_CONNECTIONS)
        return img
                
    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h,w,c=img.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                lmList.append([id,cx,cy])
                if draw:
                    cv2.circle(img,(cx,cy),1,(255,0,255),cv2.FILLED)
        return lmList

def main():
    pTime=0
    cTime=0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    # volume.GetMute()
    # volume.GetMasterVolumeLevel()
    volRange = volume.GetVolumeRange()
    maxVol = volRange[1]
    minVol = volRange[0]

    
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            x1,y1=lmList[4][1],lmList[4][2]
            x2,y2=lmList[8][1],lmList[8][2]
            cx,cy = (x1+x2)//2, (y1+y2)//2

            cv2.circle(img, (x1,y1), 8, (255,0,255),cv2.FILLED)
            cv2.circle(img, (x2,y2), 8, (255,0,255),cv2.FILLED)
            
            ##Center Point
            # cv2.circle(img, (cx,cy), 8, (255,0,255),cv2.FILLED)
            cv2.line(img, (x1,y1), (x2,y2), (255,0,255),3)

            length = math.hypot(x2-x2,y2-y1)


            #handrange = 5 - 65
            #volrange = -63.5 - 0

            vol = np.interp(length,[5,65],[minVol,maxVol])
            volume.SetMasterVolumeLevel(vol, None)
            print(vol)


        cTime= time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img,str(int(fps)),(10,70),cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255),3)

        cv2.imshow("Image",img)
        cv2.waitKey(1)












if __name__ == "__main__":
    main()