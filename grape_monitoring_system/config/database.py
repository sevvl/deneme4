import sqlite3
import os

DATABASE_NAME = 'data/database.db' # Corrected relative path

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                phone TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Add new columns if they don't exist using PRAGMA to check existence
        cursor.execute("PRAGMA table_info(users);")
        columns = [col[1] for col in cursor.fetchall()]
        if 'receive_email_notifications' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN receive_email_notifications BOOLEAN DEFAULT 1;")
            print("Database: Added 'receive_email_notifications' to users table.")

        print("Database: users table checked/created.")

        # Analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                image_path TEXT NOT NULL,
                disease_detected TEXT,
                confidence_score REAL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                gemini_response TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("Database: analyses table checked/created.")

        # Recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                recommendation_type TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER,
                implementation_date TEXT,
                FOREIGN KEY (analysis_id) REFERENCES analyses (id)
            )
        """)
        cursor.execute("PRAGMA table_info(recommendations);")
        rec_columns = [col[1] for col in cursor.fetchall()]
        if 'estimated_cost' not in rec_columns:
            cursor.execute("ALTER TABLE recommendations ADD COLUMN estimated_cost REAL;")
            print("Database: Added 'estimated_cost' to recommendations table.")

        print("Database: recommendations table checked/created.")

        # Follow-ups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follow_ups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                status TEXT,
                notes TEXT,
                follow_up_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyses (id)
            )
        """)
        print("Database: follow_ups table checked/created.")

        # Questions table for community forum
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                question_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("Database: questions table checked/created.")

        # Answers table for community forum
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("Database: answers table checked/created.")

        conn.commit()
        print(f"Database '{DATABASE_NAME}' initialization process completed.")
    except sqlite3.Error as e:
        print(f"Database Error during initialization: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DATABASE_NAME), exist_ok=True)
    init_db()
    print(f"Database '{DATABASE_NAME}' script finished execution.")

