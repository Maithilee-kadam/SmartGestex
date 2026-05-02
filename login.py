import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess
import hashlib
import sys
import os

# ---------------- HASH FUNCTION ---------------- #

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- LOGIN CHECK ---------------- #

def check_login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    hashed_pwd = hash_password(password)

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_pwd)
    )

    result = cursor.fetchone()
    conn.close()

    return result


# ---------------- LOGIN ACTION ---------------- #

def login():
    user = username_entry.get()
    pwd = password_entry.get()

    if check_login(user, pwd):
        messagebox.showinfo("Success", "Login Successful ✅")

        root.destroy()

        # Correct way to open app.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(base_dir, "app.py")

        subprocess.Popen([sys.executable, app_path])

    else:
        messagebox.showerror("Error", "Invalid Credentials ❌")


# ---------------- UI DESIGN ---------------- #

root = tk.Tk()
root.title("Secure Access")
root.geometry("450x500")
root.configure(bg="#0f172a")
root.resizable(False, False)

# ---------- Main Card ---------- #

card = tk.Frame(root, bg="#1e293b", bd=0)
card.place(relx=0.5, rely=0.5, anchor="center", width=350, height=380)

# ---------- Title ---------- #

title = tk.Label(
    card,
    text="🔐 Secure Login",
    font=("Segoe UI", 20, "bold"),
    fg="white",
    bg="#1e293b"
)
title.pack(pady=(30, 10))

subtitle = tk.Label(
    card,
    text="Access The Art of Motion",
    font=("Segoe UI", 10),
    fg="#94a3b8",
    bg="#1e293b"
)
subtitle.pack(pady=(0, 20))

# ---------- Username ---------- #

tk.Label(
    card,
    text="Username",
    fg="#cbd5e1",
    bg="#1e293b",
    font=("Segoe UI", 10)
).pack(anchor="w", padx=30)

username_entry = tk.Entry(
    card,
    font=("Segoe UI", 12),
    bg="#334155",
    fg="white",
    insertbackground="white",
    relief="flat"
)
username_entry.pack(padx=30, pady=8, fill="x")

# ---------- Password ---------- #

tk.Label(
    card,
    text="Password",
    fg="#cbd5e1",
    bg="#1e293b",
    font=("Segoe UI", 10)
).pack(anchor="w", padx=30, pady=(10, 0))

password_entry = tk.Entry(
    card,
    show="*",
    font=("Segoe UI", 12),
    bg="#334155",
    fg="white",
    insertbackground="white",
    relief="flat"
)
password_entry.pack(padx=30, pady=8, fill="x")

# ---------- Button Hover Effect ---------- #

def on_enter(e):
    login_btn["bg"] = "#2563eb"

def on_leave(e):
    login_btn["bg"] = "#3b82f6"


login_btn = tk.Button(
    card,
    text="Login",
    font=("Segoe UI", 12, "bold"),
    bg="#3b82f6",
    fg="white",
    activebackground="#2563eb",
    activeforeground="white",
    relief="flat",
    command=login
)

login_btn.pack(pady=25, ipadx=10, ipady=5)

login_btn.bind("<Enter>", on_enter)
login_btn.bind("<Leave>", on_leave)

# ---------- Footer ---------- #

footer = tk.Label(
    root,
    text="AI Powered Gesture System",
    font=("Segoe UI", 9),
    fg="#64748b",
    bg="#0f172a"
)
footer.pack(side="bottom", pady=10)

root.mainloop()