import yt_dlp
import re
from utils.logging_utils import log
from utils.io import save_json

def run(keyword: str, travel_period: str = "2박 3일", max_results: int = 10):
    """
    Step 0: 요청한 숙박 기간(n박)과 일치하지 않는 영상을 정규식으로 엄격히 차단합니다.
    """
    log("step0", f"🎯 [{keyword} + {travel_period}] 수집 및 철벽 필터링 가동")
    
    collected_videos = []
    seen_ids = set()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'ignoreerrors': True,
    }

    # 검색 쿼리: 요청한 기간을 명확히 포함
    search_query = f"ytsearch100:{keyword} {travel_period} 여행 브이로그 -추천 -코스"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(search_query, download=False)
            if not results or 'entries' not in results:
                log("step0", "❌ 검색 결과가 없습니다.")
                return []

            entries = [e for e in results.get('entries', []) if e is not None]
            
            scored_entries = []
            for e in entries:
                v_title = e.get('title', '')
                score = e.get('view_count', 0) or 0
                
                # ✅ [핵심 개선] 기간 불일치 철벽 방어 로직
                # 1. 사용자가 요청한 숫자 추출 (예: "4박 5일" -> 4)
                target_match = re.search(r'(\d+)박', travel_period)
                target_num = target_match.group(1) if target_match else None
                
                if target_num:
                    # 2. 제목에서 타겟 숫자와 다른 'n박' 패턴이 있는지 검사
                    # 예: 4박 요청 시 1박, 2박, 3박, 5박 등이 보이면 차단
                    other_stay_pattern = re.compile(rf'\b(?!(?:{target_num}))\d+박|\b(?!(?:{int(target_num)+1}))\d+일')
                    
                    # 3. '당일치기' 요청이 아닌데 제목에 '당일'이 있거나, 다른 박수가 있으면 0점
                    if travel_period != "당일치기" and ("당일" in v_title or other_stay_pattern.search(v_title)):
                        # 단, 제목에 타겟 박수(예: 4박)가 동시에 있으면 허용 (예: 4박 5일인데 1일차... 이런 경우)
                        if f"{target_num}박" not in v_title:
                            log("step0", f"🗑️ 기간 불일치 제거: {v_title[:20]}...")
                            score = 0

                # 4. 당일치기 전용 필터 (기존 로직 유지)
                if travel_period == "당일치기":
                    title_for_check = v_title.replace("당일치기", "---").replace("당일", "---")
                    stay_pattern = re.compile(r'(\d+박|\d+일|\d박\d일)')
                    if stay_pattern.search(title_for_check) or any(k in title_for_check for k in ["숙소", "호텔", "체크인"]):
                        score = 0

                # 가점: 제목에 요청한 기간이 정확히 박혀있는 경우
                if travel_period in v_title:
                    score *= 20

                scored_entries.append((score, e))

            # 점수 높은 순 정렬
            scored_entries.sort(key=lambda x: x[0], reverse=True)

            for score, entry in scored_entries:
                if len(collected_videos) >= max_results:
                    break

                # 필터링된 영상(score 0) 제외
                if score == 0:
                    continue

                v_id = entry.get('id')
                v_title = entry.get('title', '')
                if not v_id or v_id in seen_ids: continue

                collected_videos.append({
                    "video_id": v_id,
                    "title": v_title,
                    "duration": entry.get('duration', 0),
                    "view_count": entry.get('view_count', 0) or 0,
                    "day_category": travel_period,
                    "url": f"https://www.youtube.com/watch?v={v_id}"
                })
                seen_ids.add(v_id)
                log("step0", f"✅ 확보 ({len(collected_videos)}/{max_results}): {v_title[:20]}...")

        except Exception as e:
            log("step0", f"❌ 수집 중 오류 발생: {e}")

    save_json("data/step0_videos.json", collected_videos)
    log("step0", f"🚀 최종 {len(collected_videos)}개 수집 완료 (기간 정밀 검증 완료)")
    return collected_videos