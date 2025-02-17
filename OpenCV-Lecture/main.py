import cv2
import mediapipe as mp
import math
import os
import time

# Initialize MediaPipe Hands and drawing utilities.
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# -------------------------
# Helper Functions
# -------------------------

def distance(lm1, lm2):
    """Compute Euclidean distance between two landmarks (which have .x and .y attributes)."""
    return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

def hand_size(landmarks):
    """Define a rough hand size as the distance from the wrist (landmark 0) to the middle fingertip (landmark 12)."""
    return distance(landmarks[0], landmarks[12])

def moderate_extension(landmarks, tip_idx, pip_idx, hsize):
    """
    Compute the vertical difference (extension) between a finger's pip and tip.
    Return True if the extension (normalized by hand size) is in a moderate range.
    (For a 'C' shape the fingers are neither fully extended nor tightly bent.)
    """
    ext = (landmarks[pip_idx].y - landmarks[tip_idx].y)
    ratio = ext / hsize
    return 0.05 < ratio < 0.15

# -------------------------
# ASL Letter Detection Functions
# -------------------------

def detect_A(landmarks):
    """Letter A: A closed fist."""
    return (landmarks[8].y > landmarks[6].y and
            landmarks[12].y > landmarks[10].y and
            landmarks[16].y > landmarks[14].y and
            landmarks[20].y > landmarks[18].y)

def detect_B(landmarks):
    """Letter B: An open, flat hand."""
    return (landmarks[8].y < landmarks[6].y and
            landmarks[12].y < landmarks[10].y and
            landmarks[16].y < landmarks[14].y and
            landmarks[20].y < landmarks[18].y)

def detect_C(landmarks):
    """Letter C: The hand forms a curved shape."""
    hsize = hand_size(landmarks)
    idx_pinky = distance(landmarks[8], landmarks[20])
    if not (0.6 * hsize < idx_pinky < 0.9 * hsize):
        return False
    return (moderate_extension(landmarks, 8, 6, hsize) and
            moderate_extension(landmarks, 12, 10, hsize) and
            moderate_extension(landmarks, 16, 14, hsize) and
            moderate_extension(landmarks, 20, 18, hsize))

def detect_L(landmarks):
    """Letter L: Index finger and thumb form an L while the other fingers are bent."""
    index_extended = landmarks[8].y < landmarks[6].y
    thumb_extended = landmarks[4].x > landmarks[2].x  # Assumes a right hand in a mirrored view.
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    pinky_bent = landmarks[20].y > landmarks[18].y
    return index_extended and thumb_extended and middle_bent and ring_bent and pinky_bent

def detect_Y(landmarks):
    """Letter Y: Thumb and pinky are extended while index, middle, and ring are bent."""
    thumb_extended = landmarks[4].x > landmarks[2].x  # heuristic for thumb extension
    pinky_extended = landmarks[20].y < landmarks[18].y
    index_bent = landmarks[8].y > landmarks[6].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    return thumb_extended and pinky_extended and index_bent and middle_bent and ring_bent

def detect_I(landmarks, handedness="Right"):
    """Letter I: Only the pinky is extended."""
    pinky_extended = landmarks[20].y < landmarks[18].y
    index_bent = landmarks[8].y > landmarks[6].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    if handedness == "Right":
        thumb_bent = landmarks[4].x > landmarks[2].x
    else:
        thumb_bent = landmarks[4].x < landmarks[2].x
    return pinky_extended and index_bent and middle_bent and ring_bent and thumb_bent

def detect_W(landmarks):
    """Letter W: Index, middle, and ring fingers are extended while thumb and pinky are bent."""
    index_extended = landmarks[8].y < landmarks[6].y
    middle_extended = landmarks[12].y < landmarks[10].y
    ring_extended = landmarks[16].y < landmarks[14].y
    thumb_bent = landmarks[4].y > landmarks[2].y
    pinky_bent = landmarks[20].y > landmarks[18].y
    return index_extended and middle_extended and ring_extended and thumb_bent and pinky_bent

# Map each letter to its detection function.
ENABLED_LETTERS = {
    "A": detect_A,
    "B": detect_B,
    "C": detect_C,
    "L": detect_L,
    "Y": detect_Y,
    "W": detect_W,
    # "I" is handled separately below.
}

# -------------------------
# Main Video Loop
# -------------------------

cap = cv2.VideoCapture(0)

# Variables for startup command detection (using right hand)
# The expected sequence is: B -> A -> B, each held for at least 1 second.
startup_state = 0  # 0: waiting for B, 1: waiting for A, 2: waiting for second B
startup_start_time = None  # Time when the current gesture started being held.

# Variables for swipe detection using index finger (if needed later)
last_right_index_x = None
last_left_index_x = None
last_swipe_time_right = 0
last_swipe_time_left = 0
SWIPE_THRESHOLD = 50  # pixels
SWIPE_COOLDOWN = 1.0  # seconds

with mp_hands.Hands(min_detection_confidence=0.7,
                    min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        frame = cv2.flip(frame, 1)  # Mirror view
        h, w, _ = frame.shape

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = hands.process(image_rgb)
        image_rgb.flags.writeable = True
        annotated_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        detected_letter_right = None  # For right-hand gesture detection
        current_right_index_x = None

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = hand_info.classification[0].label  # "Right" or "Left"
                mp_drawing.draw_landmarks(
                    annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                # Determine the letter.
                letter = None
                for key, detect_func in ENABLED_LETTERS.items():
                    if detect_func(hand_landmarks.landmark):
                        letter = key
                        break
                if letter is None and detect_I(hand_landmarks.landmark, handedness=hand_label):
                    letter = "I"

                if letter:
                    wrist = hand_landmarks.landmark[0]
                    x = int(wrist.x * w)
                    y = int(wrist.y * h)
                    cv2.putText(annotated_image,
                                f"{letter} ({hand_label})",
                                (x, y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2,
                                cv2.LINE_AA)
                    # For startup command detection, we only use the right hand.
                    if hand_label == "Right":
                        detected_letter_right = letter
                        # Use index finger tip (landmark 8) for more precise movement tracking if needed.
                        current_right_index_x = int(hand_landmarks.landmark[8].x * w)

        # --- Startup Command Detection (Right Hand Only) ---
        # Expected sequence: B -> A -> B, each held for at least 1 second.
        expected_sequence = ["B", "A", "B"]
        current_time = time.time()

        if detected_letter_right is not None:
            # If the current letter matches the expected letter for the current state:
            if detected_letter_right == expected_sequence[startup_state]:
                # If we haven't started timing yet for this gesture, do so.
                if startup_start_time is None:
                    startup_start_time = current_time
                # Check if the letter has been held for at least 1 second.
                elif current_time - startup_start_time >= 1.0:
                    startup_state += 1
                    startup_start_time = current_time  # reset timer for next gesture
                    print(f"Startup gesture {expected_sequence[startup_state-1]} held for 1 second. State advanced to {startup_state}.")
            else:
                # If a different letter is detected, reset the state machine.
                if startup_state != 0:
                    print("Startup sequence interrupted. Resetting startup command state.")
                startup_state = 0
                startup_start_time = None
        else:
            # If no right-hand letter detected, reset the startup state.
            startup_state = 0
            startup_start_time = None

        # If the sequence is complete, execute the startup command.
        if startup_state >= 3:
            print("Startup sequence complete. Executing startup command...")
            # Execute your startup command. Adjust the command as needed.
            #os.system("cscript windowsScripts/startup_command.vbs")
            # Reset the startup state.
            startup_state = 0
            startup_start_time = None

        cv2.imshow("ASL Letter Detection", annotated_image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("x"):
            break

cap.release()
cv2.destroyAllWindows()
