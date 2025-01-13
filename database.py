import sqlite3
from datetime import datetime

class ConversationDatabase:
    def __init__(self, db_path='conversations.db'):
        self.db_path = db_path
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """
        Ensures the database table exists before any operations.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_message TEXT,
                bot_message TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_message(self, user_text, bot_text):
        """
        Adds a user and bot message pair to the database with a timestamp.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO conversation (timestamp, user_message, bot_message)
            VALUES (?, ?, ?)
        """, (timestamp, user_text, bot_text))
        conn.commit()
        conn.close()

    def get_recent_messages(self, limit=20):
        """
        Retrieves the most recent messages from the database up to the specified limit.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, user_message, bot_message
            FROM conversation
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        # Return in ascending chronological order for natural reading flow
        return rows[::-1]

    def clear_all_messages(self):
        """
        Deletes all records in the conversation table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversation")
        conn.commit()
        conn.close()
