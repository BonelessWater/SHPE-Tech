import cv2
import mediapipe as mp

# Initialize MediaPipe Hands and its drawing utilities.
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# --- Sign Language Detection Functions ---

def detect_A(landmarks):
    """
    Detects the letter 'A' (ASL):
    In ASL, "A" is typically a closed fist. Here we assume that means
    that the tips of the index, middle, ring, and pinky fingers are below their PIP joints.
    """
    return (
        landmarks[8].y > landmarks[6].y and  # Index finger bent
        landmarks[12].y > landmarks[10].y and  # Middle finger bent
        landmarks[16].y > landmarks[14].y and  # Ring finger bent
        landmarks[20].y > landmarks[18].y       # Pinky finger bent
    )

def detect_B(landmarks):
    """
    Detects the letter 'B' (ASL):
    In ASL, "B" is an open hand. We assume that means
    that the tips of the index, middle, ring, and pinky fingers are above their PIP joints.
    """
    return (
        landmarks[8].y < landmarks[6].y and  # Index finger extended
        landmarks[12].y < landmarks[10].y and  # Middle finger extended
        landmarks[16].y < landmarks[14].y and  # Ring finger extended
        landmarks[20].y < landmarks[18].y       # Pinky finger extended
    )

# Dictionary of enabled letters and their detection functions.
ENABLED_LETTERS = {
    "A": detect_A,
    "B": detect_B,
    # Add additional letters as needed, e.g.,
    # "C": detect_C,
}

# --- Main Video Processing Loop ---

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.7,
                    min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Flip the image horizontally for a mirror (selfie) view.
        frame = cv2.flip(frame, 1)

        # Convert BGR frame to RGB.
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False  # Optimize by marking the image as non-writeable

        # Process the frame to detect hands.
        results = hands.process(image_rgb)

        # Prepare image for annotation.
        image_rgb.flags.writeable = True
        annotated_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        detected_letter = None  # Store the detected letter for the current frame

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the hand landmarks on the image.
                mp_drawing.draw_landmarks(annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # For each enabled letter, check if its condition is met.
                for letter, detect_func in ENABLED_LETTERS.items():
                    if detect_func(hand_landmarks.landmark):
                        detected_letter = letter
                        break  # If one letter is detected, stop checking further.

                # Annotate the image and print the letter if detected.
                if detected_letter:
                    h, w, _ = annotated_image.shape
                    # Use the wrist landmark (index 0) as an anchor point.
                    wrist = hand_landmarks.landmark[0]
                    x, y = int(wrist.x * w), int(wrist.y * h)
                    cv2.putText(annotated_image, f"{detected_letter}", (x, y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    print(f"Detected letter: {detected_letter}")
                    # For this example, we process one hand at a time.
                    break

        # Show the annotated frame.
        cv2.imshow("Sign Language Detection", annotated_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
