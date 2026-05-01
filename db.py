import sqlite3
import os

class SQLiteCursor:
    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self.dictionary = dictionary
        
    def execute(self, query, params=None):
        # Automatically convert MySQL placeholders to SQLite placeholders
        if query and '%s' in query:
            query = query.replace('%s', '?')
        
        if params is None:
            self._cursor.execute(query)
        else:
            self._cursor.execute(query, params)
            
    def fetchone(self):
        row = self._cursor.fetchone()
        if row and self.dictionary:
            return dict(row)
        return row
        
    def fetchall(self):
        rows = self._cursor.fetchall()
        if rows and self.dictionary:
            return [dict(row) for row in rows]
        return rows
        
    @property
    def lastrowid(self):
        return self._cursor.lastrowid

class SQLiteConnection:
    def __init__(self, conn):
        self._conn = conn
        
    def cursor(self, dictionary=False):
        if dictionary:
            self._conn.row_factory = sqlite3.Row
        else:
            self._conn.row_factory = None
        return SQLiteCursor(self._conn.cursor(), dictionary=dictionary)
        
    def commit(self):
        self._conn.commit()
        
    def close(self):
        self._conn.close()

def get_connection():
    # Use a local SQLite file database
    db_path = os.path.join(os.path.dirname(__file__), 'bank.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    
    # Automatically create tables if they don't exist yet
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password BLOB NOT NULL,
                    mpin BLOB NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    balance REAL NOT NULL,
                    account_type TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts (account_id)
                )''')
    conn.commit()
    
    return SQLiteConnection(conn)
