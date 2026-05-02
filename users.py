import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

users = [
    ("admin", hash_password("admin123")),
    ("vaidehi", hash_password("vaidehi1234")),
    ("manali", hash_password("manali123")),
    ("maithilee", hash_password("maithilee123")),
    ("vaidhehi", hash_password("vaidhehi123")),
]

cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users)

conn.commit()
conn.close()

print("Database created successfully ")
