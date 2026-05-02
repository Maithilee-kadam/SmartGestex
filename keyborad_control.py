import cv2
import mediapipe as mp
import pyautogui
import time
import math

# ---------------- WINDOW SETTINGS ---------------- #

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

key_w = 70
key_h = 60
gap = 15
start_y = 200

click_delay = 0.6

# ------------------------------------------------- #

pyautogui.FAILSAFE = False

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Normal Keys
keys = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
]

# Special Keys
special_keys = ["SPACE", "ENTER", "BACK", "CLEAR", "CAPS"]

caps = True
last_click_time = 0
key_positions = {}

cap = cv2.VideoCapture(0)

cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Virtual Keyboard", WINDOW_WIDTH, WINDOW_HEIGHT)

# ---------------- DRAW KEYBOARD ---------------- #

def draw_keyboard(img):

    global key_positions
    key_positions = {}

    # -------- Normal Keys -------- #
    for row_index, row in enumerate(keys):

        row_width = len(row) * key_w + (len(row) - 1) * gap
        start_x = (WINDOW_WIDTH - row_width) // 2

        for col_index, key in enumerate(row):

            x = start_x + col_index * (key_w + gap)
            y = start_y + row_index * (key_h + gap)

            key_positions[key] = (x, y, key_w, key_h)

            cv2.rectangle(img, (x, y), (x + key_w, y + key_h), (255, 0, 0), 2)
            cv2.putText(img, key, (x + 20, y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # -------- Special Keys -------- #
    special_y = start_y + 3 * (key_h + gap)
    special_w = 120

    total_special_width = len(special_keys) * special_w + (len(special_keys)-1) * gap
    start_x = (WINDOW_WIDTH - total_special_width) // 2

    for i, key in enumerate(special_keys):

        x = start_x + i * (special_w + gap)

        key_positions[key] = (x, special_y, special_w, key_h)

        cv2.rectangle(img, (x, special_y),
                      (x + special_w, special_y + key_h),
                      (0, 255, 0), 2)

        cv2.putText(img, key, (x + 10, special_y + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# ------------------------------------------------ #

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = cv2.resize(img, (WINDOW_WIDTH, WINDOW_HEIGHT))

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    draw_keyboard(img)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, c = img.shape

            # Index tip
            x1 = int(handLms.landmark[8].x * w)
            y1 = int(handLms.landmark[8].y * h)

            # Thumb tip
            x2 = int(handLms.landmark[4].x * w)
            y2 = int(handLms.landmark[4].y * h)

            cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)

            distance = math.hypot(x2 - x1, y2 - y1)

            if distance < 40:
                current_time = time.time()

                if current_time - last_click_time > click_delay:
                    last_click_time = current_time

                    for key, (x, y, w_box, h_box) in key_positions.items():
                        if x < x1 < x + w_box and y < y1 < y + h_box:

                            # -------- KEY ACTIONS -------- #

                            if key == "SPACE":
                                pyautogui.press("space")

                            elif key == "ENTER":
                                pyautogui.press("enter")

                            elif key == "BACK":
                                pyautogui.press("backspace")

                            elif key == "CLEAR":
                                pyautogui.hotkey("ctrl", "a")
                                pyautogui.press("delete")

                            elif key == "CAPS":
                                caps = not caps

                            else:
                                if caps:
                                    pyautogui.write(key)
                                else:
                                    pyautogui.write(key.lower())

    cv2.imshow("Virtual Keyboard", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
