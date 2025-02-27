import math

# -------------------------------------------------------------------
# Custom Rock Sign (Startup Toggle)
# -------------------------------------------------------------------
def detect_rock(landmarks, handedness):
    """
    Rock sign: Index + Pinky extended; Middle + Ring bent; Thumb tucked.
    """
    index_extended = landmarks[8].y < landmarks[6].y
    pinky_extended = landmarks[20].y < landmarks[18].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    thumb_bent = is_thumb_bent(landmarks, handedness)
    return index_extended and pinky_extended and middle_bent and ring_bent and thumb_bent

# -------------------------
# ASL Signs
# -------------------------

def detect_A(landmarks, handedness=None):
    """
    Letter A: A closed fist.
    All four fingers (index, middle, ring, pinky) are bent.
    """
    return (landmarks[8].y > landmarks[6].y and
            landmarks[12].y > landmarks[10].y and
            landmarks[16].y > landmarks[14].y and
            landmarks[20].y > landmarks[18].y)

def detect_B(landmarks, handedness=None):
    """
    Letter B: An open, flat hand.
    All four fingers (index, middle, ring, pinky) are extended.
    """
    return (landmarks[8].y < landmarks[6].y and
            landmarks[12].y < landmarks[10].y and
            landmarks[16].y < landmarks[14].y and
            landmarks[20].y < landmarks[18].y)

def detect_C(landmarks, handedness=None):
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

def detect_L(landmarks, handedness):
    """
    Letter L: Index finger and thumb form an L while the other fingers are bent.
    """
    index_extended = landmarks[8].y < landmarks[6].y
    thumb_extended = is_thumb_extended(landmarks, handedness)
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    pinky_bent = landmarks[20].y > landmarks[18].y
    return index_extended and thumb_extended and middle_bent and ring_bent and pinky_bent

def detect_Y(landmarks, handedness):
    """
    Letter Y: Thumb and pinky are extended while index, middle, and ring are bent.
    """
    thumb_extended = is_thumb_extended(landmarks, handedness)
    pinky_extended = landmarks[20].y < landmarks[18].y
    index_bent = landmarks[8].y > landmarks[6].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    return thumb_extended and pinky_extended and index_bent and middle_bent and ring_bent

def detect_I(landmarks, handedness):
    """
    Letter I: Only the pinky is extended.
    """
    pinky_extended = landmarks[20].y < landmarks[18].y
    index_bent = landmarks[8].y > landmarks[6].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    thumb_bent = is_thumb_bent(landmarks, handedness)
    return pinky_extended and index_bent and middle_bent and ring_bent and thumb_bent

def detect_W(landmarks, handedness):
    """
    Letter W: Index, middle, and ring fingers are extended while thumb and pinky are bent.
    """
    index_extended = landmarks[8].y < landmarks[6].y
    middle_extended = landmarks[12].y < landmarks[10].y
    ring_extended = landmarks[16].y < landmarks[14].y
    thumb_bent = is_thumb_bent(landmarks, handedness)
    pinky_bent = landmarks[20].y > landmarks[18].y
    return index_extended and middle_extended and ring_extended and thumb_bent and pinky_bent


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

def is_palm_away(landmarks, hand_label):
    """
    Determine if the hand is palm away (back of hand facing camera) or palm in.
    For a right hand, if index finger MCP (landmark 5) x-coordinate is greater than
    pinky MCP (landmark 17) x-coordinate, we assume the palm is away.
    For a left hand, the condition is reversed.
    """
    if hand_label == "Right":
        return landmarks[5].x > landmarks[17].x
    else:
        return landmarks[5].x < landmarks[17].x

def is_thumb_extended(landmarks, hand_label):
    """
    Check if the thumb is extended, taking into account hand orientation.
    For a right hand:
      - If palm is away: thumb is extended if thumb tip (landmark 4) x > thumb MCP (landmark 2) x.
      - If palm is in: thumb is extended if thumb tip x < thumb MCP x.
    For a left hand, the logic is reversed.
    """
    if hand_label == "Right":
        if is_palm_away(landmarks, hand_label):
            return landmarks[4].x > landmarks[2].x
        else:
            return landmarks[4].x < landmarks[2].x
    else:
        if is_palm_away(landmarks, hand_label):
            return landmarks[4].x < landmarks[2].x
        else:
            return landmarks[4].x > landmarks[2].x

def is_thumb_bent(landmarks, hand_label):
    """Define thumb as bent if it is not extended."""
    return not is_thumb_extended(landmarks, hand_label)

def angle_between_points(A, B, C):
    """
    Calculate the angle at point B, given three points A, B, C.
    Each is a MediaPipe landmark with .x, .y, .z.
    Returns the angle in degrees, from 0 to 180.
    """
    # Convert to vectors BA and BC
    BA = (A.x - B.x, A.y - B.y, A.z - B.z)
    BC = (C.x - B.x, C.y - B.y, C.z - B.z)
    
    # Dot product and magnitudes
    dot = BA[0]*BC[0] + BA[1]*BC[1] + BA[2]*BC[2]
    magBA = math.sqrt(BA[0]**2 + BA[1]**2 + BA[2]**2)
    magBC = math.sqrt(BC[0]**2 + BC[1]**2 + BC[2]**2)
    
    # Avoid division by zero
    if magBA == 0 or magBC == 0:
        return 0
    
    # Cosine of the angle
    cos_angle = dot / (magBA * magBC)
    # Numerical stability
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    # Convert to degrees
    angle = math.degrees(math.acos(cos_angle))
    return angle

