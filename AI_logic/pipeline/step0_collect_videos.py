import yt_dlp
import re
import json
from utils.logging_utils import log
from utils.io import save_json

def run(keyword: str, travel_period: str, max_results: int = 10):
    log(f"🚀 Step 0: 유튜브 수집기 가동 - [{keyword} {travel_period}] 검색 시작")
    
    # yt-dlp 기본 설정 (바이트코드 내 추출된 옵션)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
        'ignoreerrors': True
    }
    
    search_query = f"ytsearch{max_results}:{keyword} 여행 브이로그 -숏츠 -shorts"
    scored_entries = []
    seen_ids = set()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(search_query, download=False)
            if not results or 'entries' not in results:
                log("⚠️ 검색 결과가 없습니다.")
                return []

            for entry in results['entries']:
                if not entry: continue
                
                v_id = entry.get('id')
                if v_id in seen_ids: continue
                
                v_title = entry.get('title', '')
                view_count = entry.get('view_count', 0)
                
                # [점수 산정 로직] 조회수 기반 가산점 (바이트코드 내 20만/10만 분기 확인)
                score = 0
                if view_count >= 200000: score += 50
                elif view_count >= 100000: score += 30
                
                # [필터링 로직] 여행 기간(Day) 일치 여부 확인
                # 정규식 패턴: (\d+)박(\d+)일, (\d+)일차 등 분석
                stay_pattern = re.compile(r'(\d+)박\s*(\d+)일|(\d+)일\s*동안|(\d+)박')
                target_match = stay_pattern.search(v_title)
                
                # 사용자가 요청한 기간(travel_period)이 제목에 포함되어 있으면 우선순위 대폭 상승
                if travel_period in v_title:
                    score += 100
                
                scored_entries.append({
                    'video_id': v_id,
                    'title': v_title,
                    'url': f"https://www.youtube.com/watch?v={v_id}",
                    'view_count': view_count,
                    'score': score,
                    'duration': entry.get('duration')
                })
                seen_ids.add(v_id)
                log(f"✅ 발견: [{v_title[:20]}...] (조회수: {view_count})")

        except Exception as e:
            log(f"❌ 수집 중 오류 발생: {str(e)}")

    # 점수 순 정렬 후 상위 결과만 반환
    scored_entries.sort(key=lambda x: x['score'], reverse=True)
    final_videos = scored_entries[:max_results]
    
    save_path = "data/step0_videos.json"
    save_json(final_videos, save_path)
    log(f"🏁 Step 0 완료: {len(final_videos)}개의 최적 영상 선정 -> {save_path}")
    
    return final_videos