import re

def is_valid_email(email: str) -> bool:
    """
    Checks if the provided string is a valid email address.
    """
    if not email: return False
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$", email) is not None

def is_valid_phone(phone: str) -> bool:
    """
    Checks if the provided string is a valid phone number (basic validation).
    """
    if not phone: return False
    # Allows digits, spaces, hyphens, and parentheses. Adjust regex for stricter validation.
    return re.match(r"^[\d\s\-()]{7,20}$", phone) is not None

def is_valid_image_file(filename: str) -> bool:
    """
    Checks if the file extension is a common image format.
    """
    if not filename: return False
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))

def is_valid_confidence_score(score: float) -> bool:
    """
    Checks if the confidence score is within the valid range (0.0 to 1.0).
    """
    return 0.0 <= score <= 1.0

