import sqlite3

# Connexion ou création du fichier users.db
conn = sqlite3.connect("users.db")
c = conn.cursor()

# Création de la table users
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        phone TEXT UNIQUE,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
