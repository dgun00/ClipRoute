import re
from schema import PlaceCandidate

def parse_metadata(title, tags):
    results = []

    for kw in tags:
        if "제주" in kw:
            results.append(
                PlaceCandidate(
                    place_name=kw,
                    seconds=None,
                    source="yt-dlp",
                    confidence=0.3,
                    evidence="tag"
                )
            )
    return results