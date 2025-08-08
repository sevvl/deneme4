from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Recommendation:
    id: Optional[int] = None
    analysis_id: Optional[int] = None
    recommendation_type: Optional[str] = None  # 'treatment', 'pruning', 'prevention'
    description: Optional[str] = None
    priority: Optional[int] = None  # 1-5 (5 en yüksek)
    estimated_cost: Optional[float] = None # New field for estimated cost
    implementation_date: Optional[date] = None

