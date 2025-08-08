from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None  # Add this field for storing hashed passwords
    phone: Optional[str] = None
    location: Optional[str] = None
    receive_email_notifications: Optional[bool] = True # New field for email notifications
    created_at: Optional[datetime] = None

