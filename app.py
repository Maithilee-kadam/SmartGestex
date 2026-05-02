import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys


# ---------------- GET BASE DIRECTORY ---------------- #

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


# ---------------- RUN SCRIPT FUNCTION ---------------- #

def run_script(script_name):

    base_dir = get_base_dir()

    py_path = os.path.join(base_dir, script_name)

    if not os.path.exists(py_path):
        messagebox.showerror("Error", f"{script_name} not found in folder.")
        return

    try:
        subprocess.Popen(
            [sys.executable, py_path],
            cwd=base_dir
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start {script_name}\n{e}")


# ---------------- MODULE LAUNCHERS ---------------- #

def start_mouse():
    run_script("gesture_mouse.py")


def start_slide():
    run_script("gesture_slide.py")


def start_art():
    run_script("gesture_art.py")


def start_keyboard():
    run_script("keyborad_control.py")


def start_voice():
    run_script("voice_control.py")


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("The Art of Motion")
root.geometry("500x450")
root.configure(bg="#121212")
root.resizable(False, False)


title = tk.Label(
    root,
    text="🖐️ SmartGestex",
    font=("Segoe UI", 20, "bold"),
    fg="white",
    bg="#121212"
)

title.pack(pady=20)


subtitle = tk.Label(
    root,
    text="Gesture + Voice Control System",
    font=("Bold", 15),
    fg="#bbbbbb",
    bg="#121212"
)

subtitle.pack(pady=5)


frame = tk.Frame(root, bg="#121212")
frame.pack(pady=30)




btn_style = {
    "font": ("Segoe UI", 11, "bold"),
    "width": 18,
    "bg": "#1e88e5",
    "fg": "white",
    "activebackground": "#1565c0",
    "relief": "ridge"
}

mouse_btn = tk.Button(frame, text="🖱 Virtual Mouse", command=start_mouse, **btn_style)
mouse_btn.grid(row=0, column=0, padx=10, pady=10)


slide_btn = tk.Button(frame, text="📽 Slide Controller", command=start_slide, **btn_style)
slide_btn.grid(row=0, column=1, padx=10, pady=10)


art_btn = tk.Button(frame, text="🎨 Gesture Art", command=start_art, **btn_style)
art_btn.grid(row=1, column=0, padx=10, pady=10)


keyboard_btn = tk.Button(frame, text="⌨ Virtual Keyboard", command=start_keyboard, **btn_style)
keyboard_btn.grid(row=1, column=1, padx=10, pady=10)

subtitle = tk.Label(
    root,
    text="Voice Based Control system ",
    font=("bold", 12),
    fg="#bbbbbb",
    bg="#121212"
)

subtitle.pack(pady=5)

voice_btn = tk.Button(root, text="🎙 Start Voice Control", command=start_voice,
                      font=("Segoe UI", 11, "bold"),
                      width=22,
                      bg="#1e88e5",
                      fg="white",
                      activebackground="#1565c0")

voice_btn.pack(pady=20)


footer = tk.Label(
    root,
    text="Desktop support Gesture Interaction System",
    font=("Bold", 9),
    fg="#777",
    bg="#121212"
)

footer.pack(side="bottom", pady=10)


root.mainloop()