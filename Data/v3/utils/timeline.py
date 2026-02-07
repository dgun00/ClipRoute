import re

# 00:00 / 09:14 / 1:02:33 형태 지원
TIME_RE = re.compile(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*(.*)$")

# 너무 흔한 노이즈(장소로 취급하면 안 됨)
DEFAULT_NOISE_PREFIX = (
    "start", "intro", "오프닝", "시작",
    "check-in", "check in", "체크인",
)

def parse_time_to_seconds(t: str):
    if not t:
        return None
    parts = t.strip().split(":")
    try:
        if len(parts) == 2:
            m, s = parts
            return int(m) * 60 + int(s)
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(s)
    except Exception:
        return None
    return None

def normalize_raw_place(raw: str) -> str:
    """
    타임라인 라인에서 시간 부분 제거 후 장소 문자열 정리.
    - 양끝 공백 제거
    - 과도한 연속 공백 정리
    """
    if not raw:
        return ""
    raw = raw.strip()
    raw = re.sub(r"\s+", " ", raw)
    return raw

def is_noise_place(raw_place: str) -> bool:
    if not raw_place:
        return True
    low = raw_place.strip().lower()
    if low in {"start", "시작"}:
        return True
    for p in DEFAULT_NOISE_PREFIX:
        if low.startswith(p):
            return True
    # 너무 짧은 경우(의미 없는 경우가 많음)
    if len(raw_place) <= 2:
        return True
    return False

def parse_description_timeline(desc: str):
    """
    description에서 타임라인 파싱
    - time_str 추출
    - seconds 계산해서 넣음(핵심!)
    - raw_place 정리
    """
    out = []
    if not desc:
        return out

    for line in desc.splitlines():
        line = line.strip()
        if not line:
            continue

        m = TIME_RE.match(line)
        if not m:
            continue

        time_str = m.group(1).strip()
        rest = m.group(2).strip()

        # 시간 뒤에 아무것도 없으면 스킵
        raw_place = normalize_raw_place(rest)
        if not raw_place:
            continue

        # Start / 체크인 등 노이즈는 여기서 1차 제거(강하게)
        if is_noise_place(raw_place):
            continue

        sec = parse_time_to_seconds(time_str)
        out.append({
            "source": "description",
            "timeline": {
                "type": "description",
                "seconds": sec,
                "time_str": time_str
            },
            "raw_place": raw_place
        })

    return out