import sqlite3
import bcrypt

conn = sqlite3.connect('database.db')
c = conn.cursor()

# ⚠️ Drop existing users table (only if you're okay resetting it)
c.execute('DROP TABLE IF EXISTS users')

# ✅ Create updated users table with email
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# User data
username = 'admin'
email = 'admin@example.com'  # Add a valid test email here
password = 'admin123'

# Hash the password
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Insert user
c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
print("User 'admin' created successfully.")

conn.commit()
conn.close()
