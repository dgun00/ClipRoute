import sys
from pathlib import Path

# ✅ [1순위] 경로 보정 로직을 최상단에서 즉시 실행
def _ensure_root():
    here = Path(__file__).resolve()
    # pipeline 폴더 안에 있으므로 parent.parent가 프로젝트 루트(v3)입니다.
    root_path = str(here.parent.parent)
    if root_path not in sys.path:
        sys.path.insert(0, root_path)

_ensure_root() # 함수 선언 직후 바로 호출

# ✅ [2순위] 경로가 확보된 후 나머지 모듈 임포트
import re
import shutil
import subprocess
import config 
from utils.io import load_json, save_json, save_text
from utils.logging_utils import log
from utils.text_cleaner import resolve_map_links  # 링크 해석 함수

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except Exception:
    YouTubeTranscriptApi = None

# ... (중간 함수 _time_to_sec, parse_description_timeline, fetch_transcript는 동일) ...

def _time_to_sec(t):
    p = t.split(":")
    if len(p) == 2:
        return int(p[0]) * 60 + int(p[1])
    if len(p) == 3:
        return int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
    return None

def parse_description_timeline(desc):
    TIME_RE = re.compile(r"(?P<t>(?:\d{1,2}:)?\d{1,2}:\d{2})\s*(?P<rest>.+)$")
    out = []
    for line in (desc or "").splitlines():
        m = TIME_RE.search(line)
        if not m:
            continue
        sec = _time_to_sec(m.group("t"))
        if sec is None:
            continue
        out.append({
            "raw_place": m.group("rest").strip(),
            "seconds": sec,
            "source": "description",
        })
    return out

def fetch_transcript(video_id):
    if not YouTubeTranscriptApi:
        return [], None
    try:
        segs = YouTubeTranscriptApi.fetch(video_id, languages=["ko", "en"]).to_raw_data()
        return [{"start_sec": int(s["start"]), "text": s["text"]} for s in segs], "youtube"
    except Exception:
        return [], None

def run():
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    videos = load_json(data_dir / "step0_videos" / "videos.json")

    materials = []
    print(f"🚀 [안정성 강화 모드] 데이터 수집 및 링크 분석 시작...")

    for v in videos:
        vid = v["video_id"]
        description = v.get("description", "")
        
        # ✅ 미리 지도 링크를 해석하여 텍스트 힌트 확보
        print(f"🔗 {vid} 영상의 지도 링크 해석 중...")
        link_hints = resolve_map_links(description)
        if link_hints:
            print(f"   ㄴ 발견된 장소: {link_hints}")

        transcript, source = fetch_transcript(vid)
        timeline = parse_description_timeline(description)

        log("step1", f'{vid} | title="{v["title"][:30]}" | transcript={len(transcript)}')

        materials.append({
            **v,
            "link_hints": link_hints,  # 힌트 데이터 저장
            "timeline_candidates": timeline,
            "transcript_segments": transcript,
            "transcript_source": source,
        })

    save_json(data_dir / "step1_materials.json", materials)
    log("step1", f"saved=data/step1_materials.json total={len(materials)}")
    print(f"🏁 수집 완료! 'link_hints'가 포함된 {len(materials)}개의 재료가 준비되었습니다.")

if __name__ == "__main__":
    run()