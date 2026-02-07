import re
from schema import PlaceCandidate

def parse_description(description: str):
    results = []

    # 1. 타임라인
    for m in re.finditer(r"(\d{1,2}):(\d{2})\s+(.+)", description):
        sec = int(m.group(1))*60 + int(m.group(2))
        name = m.group(3).strip()
        results.append(
            PlaceCandidate(
                place_name=name,
                seconds=sec,
                source="description",
                confidence=0.9,
                evidence="timeline"
            )
        )

    # 2. 괄호 나열
    for m in re.finditer(r"\(([^)]+)\)", description):
        for name in m.group(1).split("/"):
            results.append(
                PlaceCandidate(
                    place_name=name.strip(),
                    seconds=None,
                    source="description",
                    confidence=0.8,
                    evidence="parentheses"
                )
            )

    return results