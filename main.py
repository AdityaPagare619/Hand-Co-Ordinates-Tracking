import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
from time import sleep
import numpy as np
from tkinter import filedialog
import threading
import pyautogui
import time
from PIL import Image, ImageTk

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=1, maxHands=2)

recording = False
output_filename = "AirRecorder"

def start_recording():
    global recording, output_filename
    recording = True
    output_filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])

    if not output_filename:
        recording = False
        return

    countdown_thread = threading.Thread(target=countdown)
    countdown_thread.start()

def countdown():
    global recording, output_filename
    for i in range(3, 0, -1):
        print(f"Recording starts in {i}")
        time.sleep(1)

    screen_resolution = (1920, 1080)
    fps = 30.0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_filename, fourcc, fps, screen_resolution)

    while recording:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        video_writer.write(frame)
        frame = cv2.resize(frame, (800, 400))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        cvzone.cornerRect(img, (50, 50, 200, 100), 20, rt=0)
        cv2.putText(img, "Start Recording", (60, 120), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        cv2.imshow("Air Interface", img)
        cv2.waitKey(20)

# Main loop
while True:
    success, img = cap.read()
    img = detector.findHands(img)

    # Get hand landmarks
    lmList, _ = detector.findPosition(img)

    # Check if lmList is not empty before accessing landmarks
    if lmList:
        try:
            # Accessing landmarks (for example, landmark of the first point)
            x1, y1 = lmList[0][1], lmList[0][2]
            print(f"Landmark 1: ({x1}, {y1})")

            # Draw landmarks on the image
            detector.drawAll(img)

            # Check if the hand is in the region of the "Start Recording" button
            if 50 < x1 < 250 and 50 < y1 < 150:
                cv2.rectangle(img, (50, 50), (250, 150), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, "Start Recording", (60, 120), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
                l, _, _ = detector.findDistance(8, 12, img, draw=False)

                # when clicked
                if l < 30:
                    if not recording:
                        start_recording()
        except IndexError as e:
            # Handle the case where there are landmarks, but the index is out of range
            print(f"Error accessing landmarks: {e}")
            print("Full lmList:", lmList)
    else:
        # Handle the case where no hand is detected
        print("No hand detected")

    cv2.imshow("Air Interface", img)

    # Check for the "Q" key press
    key = cv2.waitKey(1)
    if key == ord('Q') or key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
