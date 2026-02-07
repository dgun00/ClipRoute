import re
from schema import PlaceCandidate

def parse_transcript(segments):
    results = []

    for seg in segments:
        text = seg["text"]
        start = seg.get("start")

        # 아주 단순한 v1 룰
        if "도착" in text or "왔어요" in text:
            results.append(
                PlaceCandidate(
                    place_name=text,
                    seconds=int(start) if start else None,
                    source="transcript",
                    confidence=0.6,
                    evidence="speech"
                )
            )

    return results