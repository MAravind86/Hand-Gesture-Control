import cv2
import numpy as np
import mediapipe as mp
import screen_brightness_control as sbc
from math import hypot
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class HandControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Gesture Control")
        self.root.geometry("900x600")
        self.root.configure(bg="#2C3E50")

        # User Instructions
        self.user_note = ttk.Label(root, text="CONTROL SYSTEM USING HAND GESTURE.",
                                   font=("Arial", 18), style="TLabel", wraplength=850, justify="center")
        self.user_note.pack(pady=10)

        self.video_label = ttk.Label(root)
        self.video_label.pack(padx=20, pady=20)

        # Create a stylish frame for volume and brightness
        self.control_frame = ttk.Frame(root, padding="20", style="TFrame")
        self.control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Brightness display
        self.brightness_label = ttk.Label(self.control_frame, text="Brightness: 0", font=("Arial", 14), style="TLabel")
        self.brightness_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # Volume display
        self.volume_label = ttk.Label(self.control_frame, text="Volume: 0", font=("Arial", 14), style="TLabel")
        self.volume_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        # Add a style for TFrame
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#34495E")
        self.style.configure("TLabel", background="#34495E", foreground="white")
        self.style.configure("TButton", background="#2980B9", foreground="white", padding="6 12")
        self.style.configure("TProgressbar", thickness=15, length=200, background="#3498DB")

        # Video capture setup
        self.cap = cv2.VideoCapture(0)

        # Audio and volume control setup
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        volRange = self.volume.GetVolumeRange()
        self.minVol, self.maxVol, _ = volRange

        # Hand tracking setup
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75,
            max_num_hands=2)

        self.draw = mp.solutions.drawing_utils

        self.update_video_feed()

        # Add user note below the camera
        self.user_instruction_note = ttk.Label(root, text="Place your left hand to control brightness and right hand to control volume.\nAdjust the distance between your fingers to modify these values.",
                                                font=("Arial", 12), style="TLabel", wraplength=850, justify="center", foreground="white", background="#2C3E50")
        self.user_instruction_note.pack(pady=10)

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = self.hands.process(frameRGB)

            left_landmark_list, right_landmark_list = self.get_left_right_landmarks(frame, processed)

            if left_landmark_list:
                left_distance = self.get_distance(frame, left_landmark_list)
                b_level = np.interp(left_distance, [50, 220], [0, 100])
                try:
                    sbc.set_brightness(int(b_level))
                except Exception as e:
                    print(f"Error setting brightness: {e}")
                self.brightness_label.config(text=f"Brightness: {int(b_level)}")

            if right_landmark_list:
                right_distance = self.get_distance(frame, right_landmark_list)
                vol = np.interp(right_distance, [50, 220], [self.minVol, self.maxVol])
                try:
                    self.volume.SetMasterVolumeLevel(vol, None)
                except Exception as e:
                    print(f"Error setting volume: {e}")
                self.volume_label.config(text=f"Volume: {int(np.interp(vol, [self.minVol, self.maxVol], [0, 100]))}")

            # Convert image to fit in Tkinter window
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = frame.resize((640, 480), Image.Resampling.LANCZOS)
            frame = ImageTk.PhotoImage(frame)
            self.video_label.img = frame
            self.video_label.configure(image=frame)

        self.root.after(10, self.update_video_feed)

    def get_left_right_landmarks(self, frame, processed):
        left_landmark_list = []
        right_landmark_list = []

        if processed.multi_hand_landmarks:
            if processed.multi_handedness:
                for i, hand_handedness in enumerate(processed.multi_handedness):
                    handedness = hand_handedness.classification[0].label
                    landmarks = processed.multi_hand_landmarks[i]
                    height, width, _ = frame.shape
                    if handedness == "Left":
                        left_landmark_list = [
                            [idx, int(landmarks.landmark[idx].x * width), int(landmarks.landmark[idx].y * height)]
                            for idx in [4, 8]
                        ]
                    elif handedness == "Right":
                        right_landmark_list = [
                            [idx, int(landmarks.landmark[idx].x * width), int(landmarks.landmark[idx].y * height)]
                            for idx in [4, 8]
                        ]
                    self.draw.draw_landmarks(frame, landmarks, self.mpHands.HAND_CONNECTIONS)

        return left_landmark_list, right_landmark_list

    def get_distance(self, frame, landmark_list):
        if len(landmark_list) < 2:
            return 0
        (x1, y1), (x2, y2) = (landmark_list[0][1], landmark_list[0][2]), (landmark_list[1][1], landmark_list[1][2])
        cv2.circle(frame, (x1, y1), 7, (0, 255, 0), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 7, (0, 255, 0), cv2.FILLED)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        return hypot(x2 - x1, y2 - y1)

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    app = HandControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

if __name__ == '__main__':
    main()
