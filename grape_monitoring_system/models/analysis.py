from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Analysis:
    id: Optional[int] = None
    user_id: Optional[int] = None
    image_path: Optional[str] = None
    disease_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    analysis_date: Optional[datetime] = None
    gemini_response: Optional[str] = None

