import sqlite3
from hashlib import sha256

# Connect to the SQLite database
conn = sqlite3.connect('C:/v1/database/users.db')
cursor = conn.cursor()

# Create a table for user accounts
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

# Sample user data (You can change these values or add more users)
users_data = [
    ('user1', '1234'),
    ('user2', 'abcd'),
    ('user3', 'test')
]

# Insert sample user data into the database
hashed_users_data = [(username, sha256(password.encode()).hexdigest()) for username, password in users_data]

cursor.executemany('''
    INSERT INTO users (username, password) VALUES (?, ?)
''', hashed_users_data)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Sample users added to the database.")