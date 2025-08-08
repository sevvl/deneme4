import sqlite3
from config.database import DATABASE_NAME
from models.user import User
from models.analysis import Analysis
from models.recommendation import Recommendation
from datetime import datetime, date
from typing import Optional, List

class DatabaseService:
    def __init__(self):
        self.conn = None

    def _get_connection(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(DATABASE_NAME)
            self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
        else:
            # Check if the connection is still open/valid by trying a simple operation
            try:
                self.conn.execute("SELECT 1").fetchone()
            except (sqlite3.ProgrammingError, sqlite3.OperationalError):
                # If connection is closed or invalid, reopen it
                self.conn = sqlite3.connect(DATABASE_NAME)
                self.conn.row_factory = sqlite3.Row
        return self.conn

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # User Operations
    def add_user(self, user: User) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password_hash, phone, location) VALUES (?, ?, ?, ?, ?)",
                           (user.name, user.email, user.password_hash, user.phone, user.location))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Error adding user: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            user_data = dict(row)
            if 'created_at' in user_data and user_data['created_at']:
                user_data['created_at'] = datetime.strptime(user_data['created_at'], '%Y-%m-%d %H:%M:%S')
            return User(**user_data)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            user_data = dict(row)
            if 'created_at' in user_data and user_data['created_at']:
                user_data['created_at'] = datetime.strptime(user_data['created_at'], '%Y-%m-%d %H:%M:%S')
            return User(**user_data)
        return None

    def update_user_settings(self, user_id: int, name: str, email: str, phone: Optional[str], location: Optional[str], receive_email_notifications: bool) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users
                SET name = ?, email = ?, phone = ?, location = ?, receive_email_notifications = ?
                WHERE id = ?
            """, (name, email, phone, location, receive_email_notifications, user_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating user settings for user_id {user_id}: {e}")
            return False

    # Analysis Operations
    def add_analysis(self, analysis: Analysis) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO analyses (user_id, image_path, disease_detected, confidence_score, gemini_response) VALUES (?, ?, ?, ?, ?)",
            (analysis.user_id, analysis.image_path, analysis.disease_detected, analysis.confidence_score, analysis.gemini_response)
        )
        conn.commit()
        return cursor.lastrowid

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Analysis]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        if row:
            analysis_data = dict(row)
            if 'analysis_date' in analysis_data and analysis_data['analysis_date']:
                analysis_data['analysis_date'] = datetime.strptime(analysis_data['analysis_date'], '%Y-%m-%d %H:%M:%S')
            return Analysis(**analysis_data)
        return None

    def get_analyses_by_user_id(self, user_id: int) -> List[Analysis]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE user_id = ? ORDER BY analysis_date DESC", (user_id,))
        rows = cursor.fetchall()
        converted_analyses = []
        for row in rows:
            analysis_data = dict(row)
            if 'analysis_date' in analysis_data and analysis_data['analysis_date']:
                analysis_data['analysis_date'] = datetime.strptime(analysis_data['analysis_date'], '%Y-%m-%d %H:%M:%S')
            converted_analyses.append(Analysis(**analysis_data))
        return converted_analyses

    # Recommendation Operations
    def add_recommendation(self, recommendation: Recommendation) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recommendations (analysis_id, recommendation_type, description, priority, estimated_cost, implementation_date) VALUES (?, ?, ?, ?, ?, ?)",
            (recommendation.analysis_id, recommendation.recommendation_type, recommendation.description, recommendation.priority, recommendation.estimated_cost, recommendation.implementation_date)
        )
        conn.commit()
        return cursor.lastrowid

    def get_recommendations_by_analysis_id(self, analysis_id: int) -> List[Recommendation]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recommendations WHERE analysis_id = ? ORDER BY priority DESC", (analysis_id,))
        rows = cursor.fetchall()
        converted_recommendations = []
        for row in rows:
            rec_data = dict(row)
            if 'implementation_date' in rec_data and rec_data['implementation_date']:
                # Assuming DATE is stored as YYYY-MM-DD
                rec_data['implementation_date'] = datetime.strptime(rec_data['implementation_date'], '%Y-%m-%d').date()
            converted_recommendations.append(Recommendation(**rec_data))
        return converted_recommendations

    # Follow-up Operations
    def add_follow_up(self, analysis_id: int, status: str, notes: str) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO follow_ups (analysis_id, status, notes) VALUES (?, ?, ?)",
            (analysis_id, status, notes)
        )
        conn.commit()
        return cursor.lastrowid

    def get_follow_ups_by_analysis_id(self, analysis_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM follow_ups WHERE analysis_id = ? ORDER BY follow_up_date DESC", (analysis_id,))
        rows = cursor.fetchall()
        converted_follow_ups = []
        for row in rows:
            fu_data = dict(row)
            if 'follow_up_date' in fu_data and fu_data['follow_up_date']:
                fu_data['follow_up_date'] = datetime.strptime(fu_data['follow_up_date'], '%Y-%m-%d %H:%M:%S')
            converted_follow_ups.append(fu_data)
        return converted_follow_ups

    def delete_analysis(self, analysis_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Delete related recommendations first
            cursor.execute("DELETE FROM recommendations WHERE analysis_id = ?", (analysis_id,))
            # Delete related follow-ups
            cursor.execute("DELETE FROM follow_ups WHERE analysis_id = ?", (analysis_id,))
            # Then delete the analysis itself
            cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
            conn.commit()
            print(f"Analysis {analysis_id} and its related data deleted successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting analysis {analysis_id}: {e}")
            conn.rollback()
            return False

    # Forum Operations (Questions)
    def add_question(self, user_id: int, title: str, question_text: str) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO questions (user_id, title, question_text) VALUES (?, ?, ?)",
                           (user_id, title, question_text))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding question: {e}")
            return None

    def get_questions(self) -> List[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        # Join with users table to get user name
        cursor.execute("SELECT q.*, u.name as user_name FROM questions q JOIN users u ON q.user_id = u.id ORDER BY q.created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_question_by_id(self, question_id: int) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT q.*, u.name as user_name FROM questions q JOIN users u ON q.user_id = u.id WHERE q.id = ?", (question_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # Forum Operations (Answers)
    def add_answer(self, question_id: int, user_id: int, answer_text: str) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO answers (question_id, user_id, answer_text) VALUES (?, ?, ?)",
                           (question_id, user_id, answer_text))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding answer: {e}")
            return None

    def get_answers_for_question(self, question_id: int) -> List[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        # Join with users table to get user name
        cursor.execute("SELECT a.*, u.name as user_name FROM answers a JOIN users u ON a.user_id = u.id WHERE a.question_id = ? ORDER BY a.created_at ASC", (question_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_dashboard_stats(self, user_id: int) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total analyses
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE user_id = ?", (user_id,))
        total_analyses = cursor.fetchone()[0]

        # Unique diseases detected
        cursor.execute("SELECT COUNT(DISTINCT disease_detected) FROM analyses WHERE user_id = ? AND disease_detected IS NOT NULL AND disease_detected != 'Unknown' AND disease_detected != 'Healthy'", (user_id,))
        unique_diseases = cursor.fetchone()[0]

        # Placeholder for active follow-ups (requires a 'status' like 'pending' or 'in_progress')
        # This query assumes 'follow_ups' table has a 'status' column and we want to count specific statuses
        cursor.execute("SELECT COUNT(*) FROM follow_ups WHERE analysis_id IN (SELECT id FROM analyses WHERE user_id = ?) AND status IN ('pending', 'in_progress')", (user_id,))
        active_follow_ups = cursor.fetchone()[0]

        return {
            "total_analyses": total_analyses,
            "unique_diseases": unique_diseases,
            "active_follow_ups": active_follow_ups
        }

