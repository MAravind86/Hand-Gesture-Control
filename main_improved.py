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
import os

class ImprovedHandControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Hand Gesture Control System")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a2e")
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main container
        self.main_container = ttk.Frame(root, style="Main.TFrame")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Enhanced styling
        self.setup_styles()
        
        # Create header
        self.create_header()
        
        # Create video frame
        self.create_video_frame()
        
        # Create control panel
        self.create_control_panel()
        
        # Create status bar
        self.create_status_bar()

        # Video capture setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Audio and volume control setup
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        volRange = self.volume.GetVolumeRange()
        self.minVol, self.maxVol, _ = volRange

        # Hand tracking setup with improved parameters
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8,
            max_num_hands=2)

        self.draw = mp.solutions.drawing_utils
        self.draw_styles = mp.solutions.drawing_styles

        # Control variables
        self.brightness_value = 0
        self.volume_value = 0
        self.left_hand_detected = False
        self.right_hand_detected = False
        
        # Smoothing variables
        self.brightness_smooth = 0
        self.volume_smooth = 0
        self.smoothing_factor = 0.3
        
        # Freeze control variables
        self.brightness_frozen = False
        self.volume_frozen = False
        self.frozen_brightness = 0
        self.frozen_volume = 0

        # Bind keyboard shortcuts
        self.root.bind('<Key>', self.handle_keypress)
        self.root.focus_set()

        self.update_video_feed()

    def check_gesture_controls(self, left_hand_landmarks, right_hand_landmarks):
        """Check for gesture-based freeze/unfreeze controls"""
        # Check left hand gestures (for brightness control)
        if left_hand_landmarks:
            if self.detect_freeze_gesture(left_hand_landmarks):
                if not self.brightness_frozen:
                    self.freeze_brightness()
                    self.show_gesture_feedback("Left hand: FREEZE BRIGHTNESS", "green")
            elif self.detect_release_gesture(left_hand_landmarks):
                if self.brightness_frozen:
                    self.unfreeze_brightness()
                    self.show_gesture_feedback("Left hand: RELEASE BRIGHTNESS", "blue")
            elif self.detect_reset_gesture(left_hand_landmarks):
                self.reset_controls()
                self.show_gesture_feedback("Left hand: RESET ALL", "red")

        # Check right hand gestures (for volume control)
        if right_hand_landmarks:
            if self.detect_freeze_gesture(right_hand_landmarks):
                if not self.volume_frozen:
                    self.freeze_volume()
                    self.show_gesture_feedback("Right hand: FREEZE VOLUME", "green")
            elif self.detect_release_gesture(right_hand_landmarks):
                if self.volume_frozen:
                    self.unfreeze_volume()
                    self.show_gesture_feedback("Right hand: RELEASE VOLUME", "blue")
            elif self.detect_reset_gesture(right_hand_landmarks):
                self.reset_controls()
                self.show_gesture_feedback("Right hand: RESET ALL", "red")

    def show_gesture_feedback(self, message, color):
        """Show temporary feedback for gesture detection"""
        # Create a temporary feedback label
        feedback_label = ttk.Label(self.root, text=message, 
                                 font=("Segoe UI", 14, "bold"),
                                 foreground=color,
                                 background="#1a1a2e")
        feedback_label.place(relx=0.5, rely=0.3, anchor="center")
        
        # Remove the feedback after 2 seconds
        self.root.after(2000, feedback_label.destroy)

    def setup_styles(self):
        """Setup enhanced ttk styles"""
        self.style = ttk.Style()
        
        # Configure styles
        self.style.configure("Main.TFrame", background="#1a1a2e", borderwidth=0, relief="flat")
        self.style.configure("Header.TFrame", background="#16213e", borderwidth=0, relief="flat")
        self.style.configure("Video.TFrame", background="#0f3460", borderwidth=0, relief="flat")
        self.style.configure("Control.TFrame", background="#16213e", borderwidth=0, relief="flat")
        self.style.configure("Status.TFrame", background="#533483", borderwidth=0, relief="flat")
        
        self.style.configure("Title.TLabel", 
                           background="#16213e", 
                           foreground="#e94560", 
                           font=("Segoe UI", 20, "bold"),
                           borderwidth=0, relief="flat")
        
        self.style.configure("Subtitle.TLabel", 
                           background="#16213e", 
                           foreground="#ffffff", 
                           font=("Segoe UI", 12),
                           borderwidth=0, relief="flat")
        
        self.style.configure("Control.TLabel", 
                           background="#16213e", 
                           foreground="#ffffff", 
                           font=("Segoe UI", 14, "bold"),
                           borderwidth=0, relief="flat")
        
        self.style.configure("Value.TLabel", 
                           background="#16213e", 
                           foreground="#00ff88", 
                           font=("Segoe UI", 16, "bold"),
                           borderwidth=0, relief="flat")
        
        self.style.configure("Status.TLabel", 
                           background="#533483", 
                           foreground="#ffffff", 
                           font=("Segoe UI", 10),
                           borderwidth=0, relief="flat")
        
        self.style.configure("Modern.TButton", 
                           background="#34495e", 
                           foreground="#ffffff", 
                           font=("Segoe UI", 14, "bold"),
                           padding="15 8",
                           borderwidth=2,
                           relief="raised")
        
        self.style.map("Modern.TButton",
                      background=[('active', '#e74c3c'), ('pressed', '#c0392b')],
                      foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
        
        # Progress bar style
        self.style.configure("Brightness.Horizontal.TProgressbar", 
                           troughcolor="#2d3748", 
                           background="#00ff88", 
                           thickness=20)
        
        self.style.configure("Volume.Horizontal.TProgressbar", 
                           troughcolor="#2d3748", 
                           background="#ff6b6b", 
                           thickness=20)

    def create_header(self):
        """Create enhanced header"""
        header_frame = ttk.Frame(self.main_container, style="Header.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        title_label = ttk.Label(header_frame, 
                               text="🎮 Advanced Hand Gesture Control System", 
                               style="Title.TLabel")
        title_label.pack(pady=5)
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Use your thumb and index finger to control brightness and volume", 
                                  style="Subtitle.TLabel")
        subtitle_label.pack(pady=2)

    def create_video_frame(self):
        """Create video display frame"""
        video_frame = ttk.Frame(self.main_container, style="Video.TFrame")
        video_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.pack(padx=5, pady=5)

    def create_control_panel(self):
        """Create enhanced control panel"""
        control_frame = ttk.Frame(self.main_container, style="Control.TFrame")
        control_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        
        # Configure grid
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Brightness control
        brightness_frame = ttk.Frame(control_frame, style="Control.TFrame")
        brightness_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        brightness_icon = ttk.Label(brightness_frame, text="💡", font=("Segoe UI", 20))
        brightness_icon.grid(row=0, column=0, padx=5, pady=2)
        
        brightness_label = ttk.Label(brightness_frame, text="Brightness", style="Control.TLabel")
        brightness_label.grid(row=0, column=1, padx=5, pady=2)
        
        self.brightness_value_label = ttk.Label(brightness_frame, text="0%", style="Value.TLabel")
        self.brightness_value_label.grid(row=0, column=2, padx=5, pady=2)
        
        self.brightness_bar = ttk.Progressbar(brightness_frame, 
                                            orient="horizontal", 
                                            length=250, 
                                            mode="determinate", 
                                            style="Brightness.Horizontal.TProgressbar")
        self.brightness_bar.grid(row=1, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        
        # Volume control
        volume_frame = ttk.Frame(control_frame, style="Control.TFrame")
        volume_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        volume_icon = ttk.Label(volume_frame, text="🔊", font=("Segoe UI", 20))
        volume_icon.grid(row=0, column=0, padx=5, pady=2)
        
        volume_label = ttk.Label(volume_frame, text="Volume", style="Control.TLabel")
        volume_label.grid(row=0, column=1, padx=5, pady=2)
        
        self.volume_value_label = ttk.Label(volume_frame, text="0%", style="Value.TLabel")
        self.volume_value_label.grid(row=0, column=2, padx=5, pady=2)
        
        self.volume_bar = ttk.Progressbar(volume_frame, 
                                        orient="horizontal", 
                                        length=250, 
                                        mode="determinate", 
                                        style="Volume.Horizontal.TProgressbar")
        self.volume_bar.grid(row=1, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        
        # Control buttons frame - All buttons in one line
        buttons_frame = ttk.Frame(control_frame, style="Control.TFrame")
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        # All buttons in one row with blue styling
        self.freeze_all_button = tk.Button(buttons_frame, text="🔒 Freeze All (F)", command=self.toggle_freeze, 
                                         bg="#3498db", fg="white", font=("Segoe UI", 12, "bold"),
                                         relief="raised", bd=2, padx=10, pady=5,
                                         activebackground="#2980b9", activeforeground="white")
        self.freeze_all_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.freeze_brightness_button = tk.Button(buttons_frame, text="🔒 Freeze Brightness (B)", command=self.toggle_brightness_freeze,
                                                bg="#3498db", fg="white", font=("Segoe UI", 12, "bold"),
                                                relief="raised", bd=2, padx=10, pady=5,
                                                activebackground="#2980b9", activeforeground="white")
        self.freeze_brightness_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.freeze_volume_button = tk.Button(buttons_frame, text="🔒 Freeze Volume (V)", command=self.toggle_volume_freeze,
                                            bg="#3498db", fg="white", font=("Segoe UI", 12, "bold"),
                                            relief="raised", bd=2, padx=10, pady=5,
                                            activebackground="#2980b9", activeforeground="white")
        self.freeze_volume_button.grid(row=0, column=2, padx=5, pady=5)
        
        reset_button = tk.Button(buttons_frame, text="🔄 Reset (R)", command=self.reset_controls,
                               bg="#3498db", fg="white", font=("Segoe UI", 12, "bold"),
                               relief="raised", bd=2, padx=10, pady=5,
                               activebackground="#2980b9", activeforeground="white")
        reset_button.grid(row=0, column=3, padx=5, pady=5)
        
        exit_button = tk.Button(buttons_frame, text="❌ Exit Application", command=self.close,
                              bg="#3498db", fg="white", font=("Segoe UI", 12, "bold"),
                              relief="raised", bd=2, padx=10, pady=5,
                              activebackground="#2980b9", activeforeground="white")
        exit_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Add gesture instructions in two rows
        instruction_frame = ttk.Frame(control_frame, style="Control.TFrame")
        instruction_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        # First row - Gesture controls
        gesture_frame = ttk.Frame(instruction_frame, style="Control.TFrame")
        gesture_frame.pack(pady=2)
        
        gesture_text = "🎮 GESTURE CONTROLS: • Thumb + Index: Control brightness/volume • Closed Fist: Freeze control • Four Fingers: Release freeze • Thumbs Up: Reset all"
        gesture_label = ttk.Label(gesture_frame, text=gesture_text, 
                                font=("Segoe UI", 12, "bold"), 
                                foreground="#00ff88", 
                                background="#16213e",
                                justify="center")
        gesture_label.pack()
        
        # Second row - Keyboard controls
        keyboard_frame = ttk.Frame(instruction_frame, style="Control.TFrame")
        keyboard_frame.pack(pady=2)
        
        keyboard_text = "⌨️ KEYBOARD: F=Freeze All • B=Freeze Brightness • V=Freeze Volume • R=Reset"
        keyboard_label = ttk.Label(keyboard_frame, text=keyboard_text, 
                                 font=("Segoe UI", 12, "bold"), 
                                 foreground="#ff6b6b", 
                                 background="#16213e",
                                 justify="center")
        keyboard_label.pack()

    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.main_container, style="Status.TFrame")
        status_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready - Place your hands in front of the camera", style="Status.TLabel")
        self.status_label.pack(pady=5)

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = self.hands.process(frameRGB)

            left_landmark_list, right_landmark_list, left_hand_landmarks, right_hand_landmarks = self.get_left_right_landmarks(frame, processed)

            # Check for gesture-based controls
            self.check_gesture_controls(left_hand_landmarks, right_hand_landmarks)

            # Update status
            self.update_status(left_landmark_list, right_landmark_list)

            if left_landmark_list and not self.brightness_frozen:
                left_distance = self.get_distance(frame, left_landmark_list)
                b_level = np.interp(left_distance, [30, 200], [0, 100])
                b_level = np.clip(b_level, 0, 100)
                
                # Apply smoothing
                self.brightness_smooth = self.brightness_smooth * (1 - self.smoothing_factor) + b_level * self.smoothing_factor
                
                try:
                    sbc.set_brightness(int(self.brightness_smooth))
                except Exception as e:
                    print(f"Error setting brightness: {e}")
                
                self.brightness_value = int(self.brightness_smooth)
                self.brightness_value_label.config(text=f"{self.brightness_value}%")
                self.brightness_bar['value'] = self.brightness_value
            elif self.brightness_frozen:
                # Use frozen value
                self.brightness_value = self.frozen_brightness
                self.brightness_value_label.config(text=f"{self.brightness_value}% (FROZEN)")
                self.brightness_bar['value'] = self.brightness_value

            if right_landmark_list and not self.volume_frozen:
                right_distance = self.get_distance(frame, right_landmark_list)
                vol = np.interp(right_distance, [30, 200], [self.minVol, self.maxVol])
                vol = np.clip(vol, self.minVol, self.maxVol)
                
                # Apply smoothing
                vol_percent = np.interp(vol, [self.minVol, self.maxVol], [0, 100])
                self.volume_smooth = self.volume_smooth * (1 - self.smoothing_factor) + vol_percent * self.smoothing_factor
                
                try:
                    self.volume.SetMasterVolumeLevel(vol, None)
                except Exception as e:
                    print(f"Error setting volume: {e}")
                
                self.volume_value = int(self.volume_smooth)
                self.volume_value_label.config(text=f"{self.volume_value}%")
                self.volume_bar['value'] = self.volume_value
            elif self.volume_frozen:
                # Use frozen value
                self.volume_value = self.frozen_volume
                self.volume_value_label.config(text=f"{self.volume_value}% (FROZEN)")
                self.volume_bar['value'] = self.volume_value

            # Convert image to fit in Tkinter window
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = frame.resize((1200, 900), Image.Resampling.LANCZOS)
            frame = ImageTk.PhotoImage(frame)
            self.video_label.img = frame
            self.video_label.configure(image=frame)

        self.root.after(10, self.update_video_feed)

    def get_left_right_landmarks(self, frame, processed):
        left_landmark_list = []
        right_landmark_list = []
        left_hand_landmarks = None
        right_hand_landmarks = None

        if processed.multi_hand_landmarks:
            if processed.multi_handedness:
                for i, hand_handedness in enumerate(processed.multi_handedness):
                    handedness = hand_handedness.classification[0].label
                    landmarks = processed.multi_hand_landmarks[i]
                    height, width, _ = frame.shape
                    
                    if handedness == "Left":
                        left_hand_landmarks = landmarks
                        left_landmark_list = [
                            [idx, int(landmarks.landmark[idx].x * width), int(landmarks.landmark[idx].y * height)]
                            for idx in [4, 8]  # Thumb tip and index finger tip
                        ]
                    elif handedness == "Right":
                        right_hand_landmarks = landmarks
                        right_landmark_list = [
                            [idx, int(landmarks.landmark[idx].x * width), int(landmarks.landmark[idx].y * height)]
                            for idx in [4, 8]  # Thumb tip and index finger tip
                        ]
                    
                    # Draw hand landmarks with enhanced styling
                    self.draw.draw_landmarks(
                        frame, 
                        landmarks, 
                        self.mpHands.HAND_CONNECTIONS,
                        self.draw_styles.get_default_hand_landmarks_style(),
                        self.draw_styles.get_default_hand_connections_style()
                    )

        return left_landmark_list, right_landmark_list, left_hand_landmarks, right_hand_landmarks

    def detect_freeze_gesture(self, landmarks):
        """Detect freeze gesture: closed fist (all fingers closed)"""
        if landmarks is None:
            return False
        
        # Get finger tip and pip landmarks
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        finger_pips = [6, 10, 14, 18]  # Index, middle, ring, pinky pips
        
        # Check if all fingers are closed (tip below pip)
        all_closed = True
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
                all_closed = False
                break
        
        return all_closed

    def detect_release_gesture(self, landmarks):
        """Detect release gesture: four fingers extended (index, middle, ring, pinky)"""
        if landmarks is None:
            return False
        
        # Get finger tip and pip landmarks for four fingers (excluding thumb)
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        finger_pips = [6, 10, 14, 18]  # Index, middle, ring, pinky pips
        
        # Check if exactly four fingers are extended (tip above pip)
        extended_count = 0
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
                extended_count += 1
        
        # Check if thumb is closed (thumb tip below thumb pip)
        thumb_closed = landmarks.landmark[4].y > landmarks.landmark[3].y
        
        return extended_count == 4 and thumb_closed

    def detect_reset_gesture(self, landmarks):
        """Detect reset gesture: thumbs up (thumb extended, others closed)"""
        if landmarks is None:
            return False
        
        # Check if thumb is extended (thumb tip above thumb pip)
        thumb_extended = landmarks.landmark[4].y < landmarks.landmark[3].y
        
        # Check if other fingers are closed
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        finger_pips = [6, 10, 14, 18]  # Index, middle, ring, pinky pips
        
        others_closed = True
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
                others_closed = False
                break
        
        return thumb_extended and others_closed

    def get_distance(self, frame, landmark_list):
        if len(landmark_list) < 2:
            return 0
        (x1, y1), (x2, y2) = (landmark_list[0][1], landmark_list[0][2]), (landmark_list[1][1], landmark_list[1][2])
        
        # Draw enhanced circles and line
        cv2.circle(frame, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(frame, (x1, y1), 15, (0, 255, 0), 2)
        cv2.circle(frame, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 15, (0, 255, 0), 2)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        return hypot(x2 - x1, y2 - y1)

    def update_freeze_buttons(self):
        """Update freeze button text based on current state"""
        if self.brightness_frozen and self.volume_frozen:
            self.freeze_all_button.config(text="🔓 Unfreeze All (F)")
        else:
            self.freeze_all_button.config(text="🔒 Freeze All (F)")
            
        if self.brightness_frozen:
            self.freeze_brightness_button.config(text="🔓 Unfreeze Brightness (B)")
        else:
            self.freeze_brightness_button.config(text="🔒 Freeze Brightness (B)")
            
        if self.volume_frozen:
            self.freeze_volume_button.config(text="🔓 Unfreeze Volume (V)")
        else:
            self.freeze_volume_button.config(text="🔒 Freeze Volume (V)")

    def update_status_text(self):
        """Update status bar with comprehensive info"""
        status_text = "Ready - "
        
        # Add freeze status
        if self.brightness_frozen or self.volume_frozen:
            status_text += "🔒 "
            if self.brightness_frozen:
                status_text += f"Brightness frozen at {self.frozen_brightness}% "
            if self.volume_frozen:
                status_text += f"Volume frozen at {self.frozen_volume}% "
            status_text += "| "
        
        # Add hand detection status
        if self.left_hand_detected:
            status_text += "Left hand detected (brightness control) "
        if self.right_hand_detected:
            status_text += "Right hand detected (volume control) "
        
        if not self.left_hand_detected and not self.right_hand_detected:
            status_text += "No hands detected - Place your hands in front of the camera"
        
        self.status_label.config(text=status_text)

    def update_status(self, left_landmarks, right_landmarks):
        """Update status bar with hand detection info"""
        self.left_hand_detected = left_landmarks is not None and len(left_landmarks) > 0
        self.right_hand_detected = right_landmarks is not None and len(right_landmarks) > 0
        self.update_status_text()

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()

    def handle_keypress(self, event):
        """Handle keyboard shortcuts"""
        if event.char.lower() == 'f':
            self.toggle_freeze()
        elif event.char.lower() == 'b':
            self.toggle_brightness_freeze()
        elif event.char.lower() == 'v':
            self.toggle_volume_freeze()
        elif event.char.lower() == 'r':
            self.reset_controls()

    def toggle_freeze(self):
        """Toggle freeze for both brightness and volume"""
        if self.brightness_frozen and self.volume_frozen:
            self.unfreeze_all()
        else:
            self.freeze_all()

    def toggle_brightness_freeze(self):
        """Toggle freeze for brightness only"""
        if self.brightness_frozen:
            self.unfreeze_brightness()
        else:
            self.freeze_brightness()

    def toggle_volume_freeze(self):
        """Toggle freeze for volume only"""
        if self.volume_frozen:
            self.unfreeze_volume()
        else:
            self.freeze_volume()

    def freeze_all(self):
        """Freeze both brightness and volume controls"""
        self.freeze_brightness()
        self.freeze_volume()

    def unfreeze_all(self):
        """Unfreeze both brightness and volume controls"""
        self.unfreeze_brightness()
        self.unfreeze_volume()

    def freeze_brightness(self):
        """Freeze brightness control"""
        self.brightness_frozen = True
        self.frozen_brightness = self.brightness_value
        self.update_freeze_buttons()
        self.update_status_text()

    def unfreeze_brightness(self):
        """Unfreeze brightness control"""
        self.brightness_frozen = False
        self.update_freeze_buttons()
        self.update_status_text()

    def freeze_volume(self):
        """Freeze volume control"""
        self.volume_frozen = True
        self.frozen_volume = self.volume_value
        self.update_freeze_buttons()
        self.update_status_text()

    def unfreeze_volume(self):
        """Unfreeze volume control"""
        self.volume_frozen = False
        self.update_freeze_buttons()
        self.update_status_text()

    def reset_controls(self):
        """Reset both controls to 0"""
        self.brightness_value = 0
        self.volume_value = 0
        self.brightness_smooth = 0
        self.volume_smooth = 0
        try:
            sbc.set_brightness(0)
            self.volume.SetMasterVolumeLevel(self.minVol, None)
        except Exception as e:
            print(f"Error resetting controls: {e}")
        self.update_status_text()

def main():
    root = tk.Tk()
    app = ImprovedHandControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

if __name__ == '__main__':
    main() 