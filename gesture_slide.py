import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# For debounce (to avoid repeating actions)
last_action_time = 0
cooldown = 1  # seconds

def count_fingers(hand_landmarks):
    """Returns number of fingers up."""
    tips = [4, 8, 12, 16, 20]  
    fingers = []

    # Thumb
    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0] - 2].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other 4 fingers
    for tip in tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers), fingers


def main():
    global last_action_time

    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Flip horizontally
        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            finger_count, fingers = count_fingers(hand)

            now = time.time()

            # === Gesture Conditions ===
            if now - last_action_time > cooldown:

                # 5 fingers → Start PPT
                if finger_count == 5:
                    pyautogui.press("f5")
                    print("START Presentation")
                    last_action_time = now

                # 0 fingers → Stop PPT
                elif finger_count == 0:
                    pyautogui.press("esc")
                    print("STOP Presentation")
                    last_action_time = now

                # 1 finger → Next Slide
                elif fingers[1] == 1 and sum(fingers) == 1:
                    pyautogui.press("right")
                    print("Next Slide")
                    last_action_time = now

                # 2 fingers → Previous Slide
                elif fingers[1] == 1 and fingers[2] == 1 and sum(fingers) == 2:
                    pyautogui.press("left")
                    print("Previous Slide")
                    last_action_time = now

        cv2.putText(frame, "5 fingers: Start | 0: Stop | 1: Next | 2: Previous",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.imshow("Slide Gesture Control (Q to Quit)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

