import cv2
import mediapipe as mp
import numpy as np
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Configure Hand detector: tune for speed/accuracy
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Colors to cycle through (BGR)
COLORS = [
    (0, 0, 255),    # red
    (0, 255, 0),    # green
    (255, 0, 0),    # blue
    (0, 255, 255),  # yellow
    (255, 0, 255),  # magenta
    (255, 255, 255) # white
]

color_idx = 0
brush_radius = 8

# Drawing canvas
canvas = None

# Smoothing for pen location (exponential moving average)
smooth_x = None
smooth_y = None
SMOOTH_FACTOR = 0.35  # higher -> less smoothing (0..1)

# Pinch detection state & cooldown so color changes happen once per pinch
pinch_state = False        # currently pinched or not
last_pinch_time = 0.0
PINCH_COOLDOWN = 0.45     # seconds between allowed color changes

# Clear gesture: two-finger up threshold (index and middle above their lower joints)
# You can refine this later if needed.
cap = cv2.VideoCapture(0)
prev_time = time.time()

def normalized_distance(lm1, lm2, img_w, img_h):
    dx = (lm1.x - lm2.x) * img_w
    dy = (lm1.y - lm2.y) * img_h
    return np.hypot(dx, dy)

def fingers_up(landmarks):
    # returns list of booleans [thumb, index, middle, ring, pinky] whether finger is up
    tips_ids = [4, 8, 12, 16, 20]
    pip_ids = [3, 6, 10, 14, 18]  # approximate lower joint for each finger
    up = []
    for tip, pip in zip(tips_ids, pip_ids):
        up.append(landmarks[tip].y < landmarks[pip].y)  # lower y = higher on image
    return up

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to read frame from camera.")
        break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

    # Convert to RGB for mediapipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # draw UI: color indicator and FPS
    # small filled rectangle showing current color
    cv2.rectangle(frame, (10, 10), (60, 60), COLORS[color_idx], -1)
    cv2.putText(frame, f"Color #{color_idx+1}", (70, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

    # FPS
    now = time.time()
    fps = 1.0 / (now - prev_time) if now - prev_time > 0 else 0.0
    prev_time = now
    cv2.putText(frame, f"FPS: {int(fps)}", (w - 120, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        lm = hand.landmark  # list of normalized landmarks

        # draw hand skeleton lightly
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS,
                               mp_draw.DrawingSpec(color=(80,80,80), thickness=1, circle_radius=2),
                               mp_draw.DrawingSpec(color=(80,80,80), thickness=1))

        # Calculate absolute pixel position for index fingertip (id 8)
        idx_tip = lm[8]
        x = int(idx_tip.x * w)
        y = int(idx_tip.y * h)

        # initialize smoothing if first frame
        if smooth_x is None:
            smooth_x, smooth_y = x, y
        else:
            # EMA smoothing
            smooth_x = int((1 - SMOOTH_FACTOR) * smooth_x + SMOOTH_FACTOR * x)
            smooth_y = int((1 - SMOOTH_FACTOR) * smooth_y + SMOOTH_FACTOR * y)

        # Pinch detection between thumb tip(4) and index tip(8)
        thumb_tip = lm[4]
        idx_tip = lm[8]
        pinch_dist = normalized_distance(thumb_tip, idx_tip, w, h)

        # Use adaptive threshold based on frame diagonal
        diag = np.hypot(w, h)
        pinch_threshold = max(12.0, diag * 0.03)  # ~3% of diagonal, min 12 px

        # Edge-triggered pinch: trigger when we go from not-pinched -> pinched
        current_time = time.time()
        if pinch_dist < pinch_threshold:
            # currently pinch
            if not pinch_state and (current_time - last_pinch_time) > PINCH_COOLDOWN:
                # transition -> perform color change
                color_idx = (color_idx + 1) % len(COLORS)
                last_pinch_time = current_time
            pinch_state = True
            # visual indicator of pinch (small circle at thumb+index mid)
            mid_x = int((thumb_tip.x + idx_tip.x) / 2 * w)
            mid_y = int((thumb_tip.y + idx_tip.y) / 2 * h)
            cv2.circle(frame, (mid_x, mid_y), 12, (0, 255, 255), 2)
        else:
            pinch_state = False

        # Clear gesture: index and middle finger both up and separated (quick clear)
        up = fingers_up(lm)
        # require index and middle up and ring/pinky down to make it reliable
        if up[1] and up[2] and (not up[3]) and (not up[4]):
            # additional check: ensure index and middle are sufficiently apart (not pinch)
            dist_idx_mid = normalized_distance(lm[8], lm[12], w, h)
            if dist_idx_mid > diag * 0.05:
                # clear canvas
                canvas[:] = 0
                # small feedback text
                cv2.putText(frame, "Canvas Cleared", (w//2 - 120, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2, cv2.LINE_AA)

        # Draw to canvas when index finger is up (and not pinch) — pen-down when index finger extended and others not blocking
        if up[1] and not pinch_state:
            # draw circle onto canvas at smoothed coordinates
            cv2.circle(canvas, (smooth_x, smooth_y), brush_radius, COLORS[color_idx], -1)

        # Optionally show a small dot where tip is (raw)
        cv2.circle(frame, (smooth_x, smooth_y), 4, (255, 255, 255), -1)
    else:
        # no hand detected, reset smoothing to avoid jump when reappears next time
        smooth_x = None
        smooth_y = None
        pinch_state = False

    # Blend canvas and frame for display (preserve full canvas when drawing)
    blended = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

    # show also small preview of canvas only in corner (optional)
    small = cv2.resize(canvas, (160, 120))
    blended[ h - 130 : h - 10 , w - 170 : w - 10 ] = small

    cv2.imshow("Art Mode - Draw with Motion (press ESC to exit)", blended)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    # press 'c' to clear manually
    if key == ord('c'):
        canvas[:] = 0

cap.release()
cv2.destroyAllWindows()
