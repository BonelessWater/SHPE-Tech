import cv2
import mediapipe as mp
import time
import os
import subprocess
import winsound  # Built-in Windows module

# -------------------------------------------------------------------
# Import windows scripts
# -------------------------------------------------------------------
from windowsScripts import bluetooth

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
# Audio playback functions using winsound (WAV files only)
# -------------------------------------------------------------------
def play_start_audio():
    winsound.PlaySound("sfx/Startup.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

def play_stop_audio():
    winsound.PlaySound("sfx/Shutdown.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

# -------------------------------------------------------------------
# Main Script
# -------------------------------------------------------------------
def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    # Path to your .vbs file for swipe commands (adjust if needed)
    vbs_script_path = os.path.join("windowsScripts", "switch_app.vbs")

    # Set up video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    startup_mode = False  # Activated when the rock sign is detected.
    last_startup = time.time()

    # Swipe detection variables
    last_right_index_x = None
    last_swipe_time_right = 0
    last_left_index_x = None
    last_swipe_time_left = 0
    SWIPE_THRESHOLD = 50  # Pixels difference to consider a swipe.
    SWIPE_COOLDOWN = 1.0  # Seconds

    # Variable to track when B sign was first detected
    b_sign_start_time = None

    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame.")
                break

            # Mirror the view and get frame dimensions
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # Process the image with MediaPipe
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = hands.process(image_rgb)
            image_rgb.flags.writeable = True

            # Use the original camera feed as our background
            annotated_image = frame.copy()

            # For swipe detection
            current_right_index_x = None
            current_left_index_x = None

            # Flags for detecting L on each hand
            left_L_detected = False
            right_L_detected = False

            # List to store detected letters in this frame (optional, for other letters)
            detected_letters = []

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                    hand_label = hand_info.classification[0].label  # "Right" or "Left"

                    mp_drawing.draw_landmarks(
                        annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )

                    # --- Check for Rock Sign on the Right Hand (Startup Toggle) ---
                    if hand_label == "Right":
                        if not startup_mode and (time.time() - last_startup > 2):
                            if detect_rock(hand_landmarks.landmark, hand_label):
                                startup_mode = True
                                print("Rock sign detected: Now accepting sign commands.")
                                play_start_audio()  # Play start-up audio
                                last_startup = time.time()
                        elif startup_mode and (time.time() - last_startup > 2):
                            if detect_rock(hand_landmarks.landmark, hand_label):
                                startup_mode = False
                                print("Rock sign detected: Stopped accepting sign commands.")
                                play_stop_audio()  # Play stop audio
                                last_startup = time.time()

                    # --- Process letters only if startup_mode is active ---
                    if startup_mode:
                        letter = None
                        for key, detect_func in ENABLED_LETTERS.items():
                            if detect_func(hand_landmarks.landmark, hand_label):
                                letter = key
                                break
                        # Check "I" specifically if no other letter is detected
                        if letter is None and detect_I(hand_landmarks.landmark, hand_label):
                            letter = "I"

                        if letter:
                            detected_letters.append(letter)
                            # Annotate the detected letter on the video feed
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

                            # If the letter is "L", record which hand made it
                            if letter == "L":
                                if hand_label == "Left":
                                    left_L_detected = True
                                elif hand_label == "Right":
                                    right_L_detected = True

                            # For swipe detection, capture the index finger tip positions
                            if hand_label == "Right":
                                current_right_index_x = int(hand_landmarks.landmark[8].x * w)
                            else:
                                current_left_index_x = int(hand_landmarks.landmark[8].x * w)

            # --- Check if both hands made the L sign ---
            if left_L_detected and right_L_detected:
                print("Both hands L detected. Exiting...")
                play_stop_audio()
                break  # Exit the main loop

            # Display reminder if not in startup mode
            if not startup_mode:
                cv2.putText(annotated_image,
                            "Show ROCK SIGN to START",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            2,
                            cv2.LINE_AA)

            # --- B Sign Detection ---
            if startup_mode:
                if "B" in detected_letters:
                    if b_sign_start_time is None:
                        b_sign_start_time = time.time()  # Start timer when B is first seen
                    elif time.time() - b_sign_start_time >= 1.0:
                        print("B sign held for a second, running bluetooth_connect() and spotify_play()")
                        bluetooth.bluetooth_connect()
                        bluetooth.spotify_play()
                        b_sign_start_time = None
                else:
                    b_sign_start_time = None

            # --- Swipe Detection (Only if startup_mode is active) ---
            if startup_mode:
                current_time = time.time()
                # Right-hand swipe left => run reverse command
                if current_right_index_x is not None and last_right_index_x is not None:
                    delta_right = current_right_index_x - last_right_index_x
                    if delta_right < -SWIPE_THRESHOLD and (current_time - last_swipe_time_right > SWIPE_COOLDOWN):
                        print("Right hand index swipe left detected. Running reverse command...")
                        subprocess.run(["cscript", "//B", vbs_script_path, "/reverse"])
                        last_swipe_time_right = current_time
                        last_swipe_time_left = current_time  # Set cooldown for both swipes
                if current_right_index_x is not None:
                    last_right_index_x = current_right_index_x

                # Left-hand swipe right => run regular command
                if current_left_index_x is not None and last_left_index_x is not None:
                    delta_left = current_left_index_x - last_left_index_x
                    if delta_left > SWIPE_THRESHOLD and (current_time - last_swipe_time_left > SWIPE_COOLDOWN):
                        print("Left hand index swipe right detected. Running regular command...")
                        subprocess.run(["cscript", "//B", vbs_script_path])
                        last_swipe_time_left = current_time
                        last_swipe_time_right = current_time  # Set cooldown for both swipes
                if current_left_index_x is not None:
                    last_left_index_x = current_left_index_x

            # Show the annotated camera feed
            cv2.imshow("SHPEWorks", annotated_image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("x"):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
