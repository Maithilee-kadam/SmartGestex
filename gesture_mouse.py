import cv2
import mediapipe as mp
import pyautogui
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ======================
# Initialize Volume Control
# ======================

try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    vol_range = volume.GetVolumeRange()
    min_vol, max_vol = vol_range[0], vol_range[1]
except:
    print("Audio control not available")
    volume = None
    min_vol = max_vol = 0


# ======================
# Initialize MediaPipe
# ======================

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# Screen size
screen_w, screen_h = pyautogui.size()

# State flags
left_click = False
right_click = False
double_click = False
scroll_start_y = None


# ======================
# Start Camera
# ======================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera not detected")
    exit()

print("Gesture Mouse Started - Press ESC to exit")


# ======================
# Main Loop
# ======================

while True:

    success, img = cap.read()

    if not success:
        continue

    img = cv2.flip(img, 1)

    h, w, _ = img.shape

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            lm = hand_landmarks.landmark

            # Finger coordinates
            thumb_x, thumb_y = int(lm[4].x * w), int(lm[4].y * h)
            index_x, index_y = int(lm[8].x * w), int(lm[8].y * h)
            middle_x, middle_y = int(lm[12].x * w), int(lm[12].y * h)
            ring_x, ring_y = int(lm[16].x * w), int(lm[16].y * h)

            # Cursor movement
            screen_x = int(lm[8].x * screen_w)
            screen_y = int(lm[8].y * screen_h)

            pyautogui.moveTo(screen_x, screen_y, duration=0.01)

            # Distances
            dist_thumb_index = math.hypot(thumb_x - index_x, thumb_y - index_y)
            dist_thumb_middle = math.hypot(thumb_x - middle_x, thumb_y - middle_y)
            dist_thumb_ring = math.hypot(thumb_x - ring_x, thumb_y - ring_y)
            dist_index_middle = math.hypot(index_x - middle_x, index_y - middle_y)

            gesture_text = ""

            # LEFT CLICK
            if dist_thumb_index < 35:
                if not left_click:
                    pyautogui.click()
                    left_click = True
                    gesture_text = "Left Click"
            else:
                left_click = False

            # RIGHT CLICK
            if dist_thumb_middle < 35:
                if not right_click:
                    pyautogui.rightClick()
                    right_click = True
                    gesture_text = "Right Click"
            else:
                right_click = False

            # DOUBLE CLICK
            if dist_thumb_ring < 35:
                if not double_click:
                    pyautogui.doubleClick()
                    double_click = True
                    gesture_text = "Double Click"
            else:
                double_click = False

            # VOLUME CONTROL
            if volume:

                vol_dist = math.hypot(thumb_x - index_x, thumb_y - index_y)

                vol = min_vol + (vol_dist - 20) / 130 * (max_vol - min_vol)

                vol = max(min(vol, max_vol), min_vol)

                volume.SetMasterVolumeLevel(vol, None)

                gesture_text = "Volume Control"

            # SCROLL CONTROL
            if dist_index_middle < 35:

                if scroll_start_y is None:

                    scroll_start_y = index_y

                else:

                    scroll_diff = index_y - scroll_start_y

                    if abs(scroll_diff) > 20:

                        if scroll_diff > 0:

                            pyautogui.scroll(-100)

                            gesture_text = "Scroll Down"

                        else:

                            pyautogui.scroll(100)

                            gesture_text = "Scroll Up"

                        scroll_start_y = index_y

            else:

                scroll_start_y = None

            # Show gesture text
            if gesture_text:

                cv2.putText(img, gesture_text, (30, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 3)

    cv2.imshow("Gesture Mouse Control", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()

print("Gesture Mouse Closed Successfully")