import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import winsound

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(2, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

# Variables for hold and double-tap detection
last_length = None
hold_start_time = None
hold_duration = 2
tap_count = 0
tap_threshold = 25
tap_time = None
double_tap_interval = 0.5
fingers_were_apart = True  # Add this line!

paused = False 

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 2, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 2, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 2, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        # --- Hold Detection --- 
        if not paused:
            if last_length is not None and abs(length - last_length) <= 3:
                if hold_start_time is None:
                    hold_start_time = time.time()
                elif time.time() - hold_start_time >= hold_duration:
                    print("Position held for 2 seconds. Pausing.")
                    winsound.Beep(500, 1000)  # 440Hz beep for 100ms (pause)
                    paused = True
                    hold_start_time = None
            else:
                hold_start_time = None
        last_length = length

        # --- Double-Tap Detection ---
        if length < tap_threshold:
            if fingers_were_apart and tap_time is not None and time.time() - tap_time <= double_tap_interval:
                tap_count += 1
                if tap_count >= 2:
                    print("Double tap detected! Resuming.")
                    winsound.Beep(750, 500)   # 880Hz beep for 50ms 
                    winsound.Beep(880, 500)   # 880Hz beep for 50ms (unpause)
                    paused = False
                    tap_count = 0
                tap_time = None  
            else:
                tap_time = time.time()
            fingers_were_apart = False  # Fingers are now together
        else:
            fingers_were_apart = True  # Fingers are apart 

        # --- Volume Control (only if not paused) ---
        if not paused:
            vol = np.interp(length, [30, 200], [minVol, maxVol])
            volBar = np.interp(length, [30, 200], [400, 150])
            volPer = np.interp(length, [30, 200], [0, 100])
            # print(f"volume: {vol}")
            volume.SetMasterVolumeLevel(vol, None)

        # --- Visual Feedback --- 
        if length < 30:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
        if length > 200:
            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 120), 2)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 120), cv2.FILLED)
        cv2.putText(img, f"Volume Level: {int(volPer)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 200, 0), 2)

        if paused:
            cv2.putText(img, "Paused", (40, 110), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    # --- FPS Display ---
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)



# import cv2
# import time
# import numpy as np
# import HandTrackingModule as htm
# import math

# from ctypes import cast, POINTER
# from comtypes import CLSCTX_ALL
# from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# wCam, hCam = 640, 480 #dimensions of camera window


# cap = cv2.VideoCapture(0)
# cap.set(2, wCam)
# cap.set(4, hCam)
# pTime = 0

# detector = htm.handDetector(detectionCon=0.7)


# #to control system volume

# devices = AudioUtilities.GetSpeakers()
# interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
# volume = cast(interface, POINTER(IAudioEndpointVolume))
# #volume.GetMute()
# #volume.GetMasterVolumeLevel()
# volRange = volume.GetVolumeRange()
# print(volRange) #(-74.0, 0.0, 1.0)
# # volume.SetMasterVolumeLevel(0, None) #-20 sets the volume to 26, 0 sets it to 100

# minVol = volRange[0]
# maxVol = volRange[1]
# vol = 0
# volBar = 400
# volPer = 0


# while True:
#     success, img = cap.read()
#     img = detector.findHands(img)
#     lmList = detector.findPosition(img, draw=False)
#     if len(lmList) != 0:
#         # print(lmList[4], lmList[8]) #tip of thumb and tip of index finger

#         x1, y1 = lmList[4][1], lmList[4][2]
#         x2, y2 = lmList[8][1], lmList[8][2]
#         cx, cy = (x1+x2)//2, (y1+y2)//2

#         cv2.circle(img,(x1,y1), 15, (255,0,0), cv2.FILLED)
#         cv2.circle(img,(x2,y2), 15, (255,0,0), cv2.FILLED)
#         cv2.line(img,(x1,y1), (x2,y2), (255,0,255), 3)
#         cv2.circle(img,(cx,cy), 15, (255,0,0), cv2.FILLED)

#         length = math.hypot(x2-x1,y2-y1)
#         # print(f'length: {length}')

#         # Hand range 30-200 with right hand
#         # volume range -74 -> 0

#         vol = np.interp(length, [30,200], [minVol, maxVol])
#         volBar = np.interp(length, [30,200], [400, 150])
#         volPer = np.interp(length, [30,200], [0, 100])
#         print(f"volume: {vol}")
#         volume.SetMasterVolumeLevel(vol,None)

#         if length < 30:
#             cv2.circle(img,(cx,cy), 15, (0,255,0), cv2.FILLED)
#         if length > 200:
#             cv2.circle(img,(x1,y1), 15, (0,255,0), cv2.FILLED)
#             cv2.circle(img,(x2,y2), 15, (0,255,0), cv2.FILLED)


#         cv2.rectangle(img, (50,150), (85,400), (0,0,120), 2)
#         cv2.rectangle(img, (50,int(volBar)), (85,400), (0,0,120), cv2.FILLED)

#         cv2.putText(img, f"Volume Level: {int(volPer)} %", (40,450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,200,0), 2)

#     cTime = time.time()
#     fps = 1/(cTime-pTime)
#     pTime = cTime

#     cv2.putText(img, f"FPS: {int(fps)}", (40,70), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
    

#     cv2.imshow("Img", img)
#     cv2.waitKey(1)
    