import sqlite3


class Question_DB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def create_links_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT 
        )"""
        )
        self.connection.commit()

    def create_questions_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            difficulty TEXT,
            example TEXT,
            constrains TEXT
        )"""
        )
        self.connection.commit()

    def insert_links(self, title, link):
        self.cursor.execute(
            """
            INSERT INTO links (title, link)
            VALUES (?, ?)
        """,
            (title, link),
        )
        self.connection.commit()

    def insert_question(self, title, description, difficulty, example, constrains):
        self.cursor.execute(
            """
            INSERT INTO questions (title, description, difficulty, example, constrains)
            VALUES (?, ?, ?, ?, ?)
        """,
            (title, description, difficulty, example, constrains),
        )
        self.connection.commit()

    def close_connection(self):
        self.connection.close()
