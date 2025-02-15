import cv2
import mediapipe as mp
import math

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
    """
    Letter A: A closed fist.
    All four fingers (index, middle, ring, pinky) are bent.
    """
    return (landmarks[8].y > landmarks[6].y and
            landmarks[12].y > landmarks[10].y and
            landmarks[16].y > landmarks[14].y and
            landmarks[20].y > landmarks[18].y)

def detect_B(landmarks):
    """
    Letter B: An open, flat hand.
    All four fingers (index, middle, ring, pinky) are extended.
    """
    return (landmarks[8].y < landmarks[6].y and
            landmarks[12].y < landmarks[10].y and
            landmarks[16].y < landmarks[14].y and
            landmarks[20].y < landmarks[18].y)

def detect_C(landmarks):
    """
    Letter C: The hand forms a curved shape.
    Heuristics:
      - The distance between the index fingertip (8) and pinky fingertip (20)
        should be a moderate fraction of the hand size.
      - The fingers should not be fully extended (as in B) nor fully bent (as in A).
    """
    hsize = hand_size(landmarks)
    idx_pinky = distance(landmarks[8], landmarks[20])
    if not (0.6 * hsize < idx_pinky < 0.9 * hsize):
        return False
    return (moderate_extension(landmarks, 8, 6, hsize) and
            moderate_extension(landmarks, 12, 10, hsize) and
            moderate_extension(landmarks, 16, 14, hsize) and
            moderate_extension(landmarks, 20, 18, hsize))

def detect_L(landmarks):
    """
    Letter L: Index finger and thumb form an L while the other fingers are bent.
    """
    index_extended = landmarks[8].y < landmarks[6].y
    # For the thumb, we use a simple heuristic.
    thumb_extended = landmarks[4].x > landmarks[2].x  # This assumes a right hand in a mirrored view.
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    pinky_bent = landmarks[20].y > landmarks[18].y
    return index_extended and thumb_extended and middle_bent and ring_bent and pinky_bent

def detect_Y(landmarks):
    """
    Letter Y: Thumb and pinky are extended while index, middle, and ring are bent.
    """
    thumb_extended = landmarks[4].x > landmarks[2].x  # heuristic for thumb extension
    pinky_extended = landmarks[20].y < landmarks[18].y
    index_bent = landmarks[8].y > landmarks[6].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    return thumb_extended and pinky_extended and index_bent and middle_bent and ring_bent

def detect_I(landmarks):
    """
    Letter I: Only the pinky is extended.
    """
    pinky_extended = landmarks[20].y < landmarks[18].y
    index_bent = landmarks[8].y > landmarks[6].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    thumb_bent = landmarks[4].y > landmarks[2].y
    return pinky_extended and index_bent and middle_bent and ring_bent and thumb_bent

def detect_W(landmarks):
    """
    Letter W: Index, middle, and ring fingers are extended while thumb and pinky are bent.
    """
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
    "I": detect_I,
    "W": detect_W,
}

# -------------------------
# Main Video Loop
# -------------------------

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.7,
                    min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Flip the image horizontally for a mirror view.
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB.
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Process the image and detect hand landmarks.
        results = hands.process(image_rgb)

        # Prepare image for annotation.
        image_rgb.flags.writeable = True
        annotated_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        detected_letter = None  # Will hold the detected letter (if any)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks.
                mp_drawing.draw_landmarks(
                    annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                # Check each enabled letter.
                for letter, detect_func in ENABLED_LETTERS.items():
                    if detect_func(hand_landmarks.landmark):
                        detected_letter = letter
                        break  # Report only one letter per hand for now.

                if detected_letter:
                    h, w, _ = annotated_image.shape
                    # Use the wrist (landmark 0) as an anchor for the text.
                    wrist = hand_landmarks.landmark[0]
                    x, y = int(wrist.x * w), int(wrist.y * h)
                    cv2.putText(
                        annotated_image,
                        f"{detected_letter}",
                        (x, y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA
                    )
                    print(f"Detected letter: {detected_letter}")
                    # Process only one hand per frame for this example.
                    break

        cv2.imshow("ASL Letter Detection", annotated_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
