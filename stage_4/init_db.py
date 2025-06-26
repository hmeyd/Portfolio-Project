import sqlite3

# Change this to match the DB filename used in your app
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Adjust the columns to match your app's insert statement
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Users table created.")
