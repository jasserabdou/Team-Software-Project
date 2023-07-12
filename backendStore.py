import sqlite3
import re
import hashlib
import secrets
"""
This program manages a user database with hashed passwords and text-to-speech input using SQLite3. It defines two classes: 
`User` and `TextSpeech`, each encapsulating the attributes and behaviors related to user accounts and transcribed text, respectively. 
The program creates two tables in the database: `accounts` for user account logins and `text_speech` for text-to-speech input.

The `User` class provides the following methods:
- `__init__(self, username, password, transcribed_text)`: Initializes a new `User` object with the specified `username`, `password`, and `transcribed_text`.
- `hash_password(self, password)`: Hashes the specified `password` using SHA256 and a random salt.
- `add_user(self, conn, c)`: Adds a new user to the `accounts` table and the `text_speech` table using the provided database connection and cursor.

The `TextSpeech` class provides the following methods:
- `__init__(self, user_id, transcribed_text)`: Initializes a new `TextSpeech` object with the specified `user_id` and `transcribed_text`.
- `add_text_speech(self, conn, c)`: Adds a new text-to-speech input to the `text_speech` table using the provided database connection and cursor.

The program also defines two helper functions: `connect_db()` and `close_db(conn)`, 
which respectively create a database connection and cursor and close the database connection.

The program entry point is the `main()` function, which creates the database tables, 
creates a new `User` object for each user, adds them to the database, and closes the database connection when done.

"""


class UserDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.c = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.c = self.conn.cursor()
        except sqlite3.Error as e:
            print(e)

    def close(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(e)

    def create_accounts_table(self):
        try:
            self.c.execute('''CREATE TABLE IF NOT EXISTS accounts
                            (id INTEGER PRIMARY KEY,
                             username TEXT,
                             password TEXT)''')
        except sqlite3.Error as e:
            print(e)

    def create_text_speech_table(self):
        try:
            self.c.execute('''CREATE TABLE IF NOT EXISTS text_speech
                            (id INTEGER PRIMARY KEY,
                             user_id INTEGER,
                             transcribed_text TEXT,
                             FOREIGN KEY(user_id) REFERENCES accounts(id))''')
        except sqlite3.Error as e:
            print(e)

    def add_user(self):
        # define a specific password pattern
        username_pattern = r'^[a-zA-Z][a-zA-Z0-9_]{4,15}$'

        while True:
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            transcribed_text = input("Enter transcribed text: ")

            # check if the username matches the required format
            if not re.match(username_pattern, username):
                print("Invalid username format. Username must start with a letter, be between 5 and 16 characters long, and can only contain letters, numbers, and underscores.")
                continue

            # hash the password and store the hash value in the accounts table
            salt = secrets.token_bytes(16)
            hash_object = hashlib.sha256(salt + password.encode())
            hash_value = hash_object.digest()

            try:
                # insert the username and hash value into the accounts table
                self.c.execute(
                    'INSERT INTO accounts (username, password) VALUES (?, ?)', (username, hash_value))
                user_id = self.c.lastrowid  # get the ID of the inserted row in the accounts table

                # insert the user ID and transcribed text into the text_speech table
                self.c.execute('INSERT INTO text_speech (user_id, transcribed_text) VALUES (?, ?)',
                               (user_id, transcribed_text))

                self.conn.commit()
                print(f"User {username} added to database.")
            except sqlite3.Error as e:
                print(e)

            another_user = input("Welcome New User!! Press Y or N : (Y/N) ")
            if another_user.lower() == 'n':
                break

    def initialize(self):
        try:
            self.connect()
            self.create_accounts_table()
            self.create_text_speech_table()
            self.add_user()
        except sqlite3.Error as e:
            print(e)
        finally:
            self.close()


# main program
try:
    db = UserDatabase('backendstore.db')
    db.initialize()
except sqlite3.Error as e:
    print(e)