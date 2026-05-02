"""
voice_control.py
Voice-controlled desktop assistant (Windows-focused)
"""

import speech_recognition as sr
import subprocess
import os
import sys
import time
import webbrowser
import shutil
import pyautogui
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass


# -------------------------
# Open functions
# -------------------------

def open_vscode():
    if shutil.which("code"):
        subprocess.Popen(["code"])
        print("Launched VS Code")

def open_notepad():
    subprocess.Popen(["notepad.exe"])
    print("Opened Notepad")

def open_calculator():
    subprocess.Popen(["calc.exe"])
    print("Opened Calculator")

def open_browser():
    webbrowser.open("https://www.google.com")
    print("Opened Browser")

def open_chrome_youtube():
    try:
        subprocess.Popen(["chrome","https://youtube.com"])
    except:
        webbrowser.open("https://youtube.com")

def open_this_pc():
    subprocess.Popen(["explorer","shell:MyComputerFolder"])

def open_c_drive():
    subprocess.Popen(["explorer","C:\\"])

def open_folder(name):

    if "downloads" in name:
        path = os.path.join(os.path.expanduser("~"),"Downloads")

    elif "desktop" in name:
        path = os.path.join(os.path.expanduser("~"),"Desktop")

    else:
        path = os.path.expanduser(name)

    subprocess.Popen(["explorer",path])

def open_camera():
    subprocess.Popen(["start","microsoft.windows.camera:"],shell=True)


# -------------------------
# Close functions
# -------------------------

def close_notepad():
    subprocess.run(["taskkill","/IM","notepad.exe","/F"])

def close_vscode():
    subprocess.run(["taskkill","/IM","Code.exe","/F"])

def close_calculator():
    subprocess.run(["taskkill","/IM","Calculator.exe","/F"])
    subprocess.run(["taskkill","/IM","calc.exe","/F"])

def close_browser():
    subprocess.run(["taskkill","/IM","chrome.exe","/F"])
    subprocess.run(["taskkill","/IM","msedge.exe","/F"])


# -------------------------
# Window controls
# -------------------------

def close_window():
    pyautogui.hotkey('alt','f4')

def minimize_window():
    pyautogui.hotkey('win','down')

def maximize_window():
    pyautogui.hotkey('win','up')


# -------------------------
# Mouse control
# -------------------------

def parse_and_move_mouse(command):

    w,h = pyautogui.size()

    if "center" in command:
        pyautogui.moveTo(w//2,h//2)

    if "up" in command:
        pyautogui.moveRel(0,-100)

    if "down" in command:
        pyautogui.moveRel(0,100)

    if "left" in command:
        pyautogui.moveRel(-100,0)

    if "right" in command:
        pyautogui.moveRel(100,0)


def click_mouse(command):

    if "double" in command:
        pyautogui.doubleClick()

    elif "right" in command:
        pyautogui.click(button='right')

    else:
        pyautogui.click()


def scroll_mouse(command):

    if "up" in command:
        pyautogui.scroll(100)

    elif "down" in command:
        pyautogui.scroll(-100)


# -------------------------
# Voice typing
# -------------------------

def voice_typing_mode(recognizer,mic):

    print("Voice typing started")

    while True:

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio).lower()
            print("Typed:",text)

        except:
            continue

        if "stop typing" in text:
            print("Voice typing stopped")
            break

        pyautogui.write(text+" ")


# -------------------------
# Voice Save Function
# -------------------------

def save_file_with_voice(recognizer,mic):

    print("What should be the file name?")

    try:

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        filename = recognizer.recognize_google(audio).lower()

        print("File name:",filename)

        filename = filename.replace(" ","_")

        pyautogui.hotkey("ctrl","s")
        time.sleep(1)

        pyautogui.write(filename + ".txt")
        time.sleep(0.5)

        pyautogui.press("enter")

        print("File saved as",filename)

    except Exception as e:
        print("Could not get file name:",e)


# -------------------------
# Help menu
# -------------------------

def print_help():

    print("""
Commands you can say:

open notepad
open calculator
open browser
open vscode
open downloads
open desktop

close notepad
close calculator
close browser

start typing
stop typing

move mouse up/down/left/right
left click
right click
double click
scroll up
scroll down

save file

stop
""")


# -------------------------
# Main Voice Loop
# -------------------------

def main():

    r = sr.Recognizer()
    mic = sr.Microphone()

    print("Voice controller active. Say help to list commands.")

    while True:

        try:

            with mic as source:

                r.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = r.listen(source)

            command = r.recognize_google(audio).lower()

            print("You said:",command)


            # Open commands
            if "open vscode" in command:
                open_vscode()

            elif "open notepad" in command:
                open_notepad()

            elif "open calculator" in command:
                open_calculator()

            elif "open browser" in command:
                open_browser()

            elif "open chrome youtube" in command:
                open_chrome_youtube()

            elif "open this pc" in command:
                open_this_pc()

            elif "open c drive" in command:
                open_c_drive()

            elif "open downloads" in command:
                open_folder("downloads")

            elif "open desktop" in command:
                open_folder("desktop")

            elif "open camera" in command:
                open_camera()


            # Close commands
            elif "close notepad" in command:
                close_notepad()

            elif "close vscode" in command:
                close_vscode()

            elif "close calculator" in command:
                close_calculator()

            elif "close browser" in command:
                close_browser()


            # Window controls
            elif "close window" in command:
                close_window()

            elif "minimize window" in command:
                minimize_window()

            elif "maximize window" in command:
                maximize_window()


            # Mouse control
            elif "move mouse" in command:
                parse_and_move_mouse(command)

            elif "click" in command:
                click_mouse(command)

            elif "scroll" in command:
                scroll_mouse(command)


            # Save file
            elif "save file" in command or "save document" in command or command.strip()=="save":
                save_file_with_voice(r,mic)


            # Voice typing
            elif "start typing" in command:
                voice_typing_mode(r,mic)


            elif "help" in command:
                print_help()

            elif command in ("stop","exit","quit"):
                break

            else:
                print("Command not recognized")

        except Exception as e:
            print("Error:",e)


if __name__ == "__main__":
    main()