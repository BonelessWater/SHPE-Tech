import cv2
import mediapipe as mp
import time
import sys
import os
import subprocess
import math

# -------------------------------------------------------------------
# Resource path helper for PyInstaller one-file executables
# -------------------------------------------------------------------
def resource_path(relative_path):
    """
    Get the absolute path to a resource, whether running as a script or as a bundled EXE.
    """
    if getattr(sys, "_MEIPASS", False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

from ASL import *

# -------------------------------------------------------------------
# Map Letters to Their Detection Functions
# -------------------------------------------------------------------
ENABLED_LETTERS = {
    "A": detect_A,
    "B": detect_B,
    "C": detect_C,
    "L": detect_L,
    "Y": detect_Y,
    "W": detect_W,
}

# -------------------------------------------------------------------
# Main Script
# -------------------------------------------------------------------
def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    # This is the path to your .vbs file. We'll use it for swipe commands.
    # On Windows, cscript is typically available by default.
    vbs_script_path = resource_path(os.path.join("windowsScripts", "switch_app.vbs"))

    # Set up video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    # Use startup_mode to toggle sign command acceptance.
    startup_mode = False  # Activated when the rock sign is detected.

    # Swipe detection variables
    last_right_index_x = None
    last_swipe_time_right = 0
    last_left_index_x = None
    last_swipe_time_left = 0
    SWIPE_THRESHOLD = 50  # Pixels difference to consider a swipe.
    SWIPE_COOLDOWN = 1.0  # Seconds

    last_startup = time.time()

    # Create a Hands object with MediaPipe
    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        while True:

            left_finger_gun = False
            right_finger_gun = False

            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame.")
                break

            # Mirror the view
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # Convert to RGB for MediaPipe
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = hands.process(image_rgb)
            image_rgb.flags.writeable = True

            annotated_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            current_right_index_x = None
            current_left_index_x = None

            # Check for hands
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                    hand_label = hand_info.classification[0].label  # "Right" or "Left"

                    mp_drawing.draw_landmarks(
                        annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )

                    # --- Check for Rock Sign on the Right Hand (Startup Toggle) ---
                    if hand_label == "Right":
                        # If not in startup_mode, check if user does rock sign to enable
                        if not startup_mode and (time.time() - last_startup > 2):
                            if detect_rock(hand_landmarks.landmark, hand_label):
                                startup_mode = True
                                print("Rock sign detected: Now accepting sign commands.")
                                cv2.putText(annotated_image,
                                            "STARTUP SIGN DETECTED",
                                            (10, 70),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            1,
                                            (255, 0, 0),
                                            2,
                                            cv2.LINE_AA)
                                last_startup = time.time()

                        # If in startup_mode, check if user does rock sign again to disable
                        elif startup_mode and (time.time() - last_startup > 2):
                            if detect_rock(hand_landmarks.landmark, hand_label):
                                startup_mode = False
                                print("Rock sign detected: Stopped accepting sign commands.")
                                cv2.putText(annotated_image,
                                            "STARTUP SIGN DETECTED",
                                            (10, 70),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            1,
                                            (255, 0, 0),
                                            2,
                                            cv2.LINE_AA)
                                last_startup = time.time()

                    # --- Process letters only if startup_mode is active ---
                    if startup_mode:
                        letter = None
                        # Check each letter detection function
                        for key, detect_func in ENABLED_LETTERS.items():
                            if detect_func(hand_landmarks.landmark, hand_label):
                                letter = key
                                break
                        # Check "I" specifically (like your original code)
                        if letter is None and detect_I(hand_landmarks.landmark, hand_label):
                            letter = "I"

                        # If we detected a letter, annotate
                        if letter:
                            wrist = hand_landmarks.landmark[0]
                            x_pos = int(wrist.x * w)
                            y_pos = int(wrist.y * h)
                            cv2.putText(annotated_image,
                                        f"{letter} ({hand_label})",
                                        (x_pos, y_pos - 20),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        1,
                                        (0, 255, 0),
                                        2,
                                        cv2.LINE_AA)

                            # For swipe detection, capture index finger tip positions
                            if hand_label == "Right":
                                current_right_index_x = int(hand_landmarks.landmark[8].x * w)
                            else:
                                current_left_index_x = int(hand_landmarks.landmark[8].x * w)

            # If not in startup_mode, show a reminder
            if not startup_mode:
                cv2.putText(annotated_image,
                            "Show ROCK SIGN to START",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            2,
                            cv2.LINE_AA)
            
            if left_finger_gun and right_finger_gun:
                print("Both hands are making the L sign gesture. Exiting...")

                # Force break
                cap.release()
                cv2.destroyAllWindows()    
                break 

            # -------------------------------------------------------------------
            # Swipe Detection (Only if startup_mode is active)
            # -------------------------------------------------------------------
            if startup_mode:
                current_time = time.time()
                # Right-hand swipe left => run reverse command
                if current_right_index_x is not None and last_right_index_x is not None:
                    delta_right = current_right_index_x - last_right_index_x
                    if delta_right < -SWIPE_THRESHOLD and (current_time - last_swipe_time_right > SWIPE_COOLDOWN):
                        print("Right hand index swipe left detected. Running reverse command...")
                        # Use subprocess.run to avoid console pop-up
                        subprocess.run(["cscript", "//B", vbs_script_path, "/reverse"])
                        last_swipe_time_right = current_time
                if current_right_index_x is not None:
                    last_right_index_x = current_right_index_x

                # Left-hand swipe right => run normal command
                if current_left_index_x is not None and last_left_index_x is not None:
                    delta_left = current_left_index_x - last_left_index_x
                    if delta_left > SWIPE_THRESHOLD and (current_time - last_swipe_time_left > SWIPE_COOLDOWN):
                        print("Left hand index swipe right detected. Running regular command...")
                        subprocess.run(["cscript", "//B", vbs_script_path])
                        last_swipe_time_left = current_time
                if current_left_index_x is not None:
                    last_left_index_x = current_left_index_x

            # -------------------------------------------------------------------
            # Show the annotated image
            # -------------------------------------------------------------------
            cv2.imshow("SHPEWorks", annotated_image)

            # Also allow closing if the user presses 'x' on the keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord("x"):
                # Force break
                cap.release()
                cv2.destroyAllWindows()    
                break      

    cap.release()
    cv2.destroyAllWindows()

# -------------------------------------------------------------------
# Run the main function
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
