from dataclasses import dataclass
from typing import Optional

@dataclass
class PlaceCandidate:
    place_name: str
    seconds: Optional[int]
    source: str            # description | transcript | yt-dlp
    confidence: float      # 소스 신뢰도
    evidence: str          # 추출 근거