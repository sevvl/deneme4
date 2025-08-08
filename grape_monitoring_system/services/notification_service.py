class NotificationService:
    def send_notification(self, user_id: int, message: str, type: str = "info"):
        """
        Sends a notification to a specific user.
        This is a placeholder for actual notification mechanisms (e.g., email, SMS, in-app).
        """
        print(f"[Notification to User {user_id} ({type.upper()})]: {message}")

    def send_admin_alert(self, message: str, type: str = "error"):
        """
        Sends an alert to administrators for critical issues.
        """
        print(f"[ADMIN ALERT ({type.upper()})]: {message}")

