import os
import yt_dlp
import requests
import re
import time
import random
from utils.logging_utils import log
from utils.io import save_json, load_json

def clean_transcript(raw_text):
    """
    자막 노이즈 제거 및 문맥 연결 최적화.
    장기 여행 영상의 경우 문맥이 끊기면 날짜 구분이 어려우므로 줄바꿈을 공백으로 대체하여 연결성을 강화합니다.
    """
    if not raw_text: return ""
    text = re.sub(r'<[^>]*>', '', raw_text)
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', ' ', text)
    text = re.sub(r'WEBVTT|Kind:.*|Language:.*|\[음악\]|\[알림\]|\(.*\)', ' ', text)
    # 줄바꿈 제거 및 연속 공백 정리
    text = " ".join(text.split())
    return text

def run(video_list: list):
    log("step1", "⚡ Step 1 가동: 장기 여행용 하이브리드 고밀도 수집 엔진")
    
    results = []
    data_dir = "data/step1_transcripts"
    if not os.path.exists(data_dir): 
        os.makedirs(data_dir)

    for video in video_list:
        v_id = video['video_id']
        save_path = os.path.join(data_dir, f"{v_id}.json")

        # 기존 부실한 데이터를 갱신하기 위해 삭제 후 실행 권장
        if os.path.exists(save_path):
            log("step1", f"♻️ [{v_id}] 기존 데이터 발견! 재사용")
            results.append(load_json(save_path))
            continue

        max_retries = 3
        for attempt in range(max_retries):
            try:
                log("step1", f"📥 [{v_id}] 장기 여행 단서 수집 시도 ({attempt + 1}/{max_retries})...")
                
                # 차단 방지를 위한 지연시간 증가 (장기 여행은 데이터량이 많아 더 조심해야 함)
                time.sleep(random.uniform(2.0, 4.0))

                ydl_opts = {
                    'skip_download': True,
                    'writeautomaticsub': True,
                    'getcomments': True,        # ✅ 댓글 수집 활성화
                    'subtitleslangs': ['ko'],
                    'quiet': True,
                    'no_warnings': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android'], 
                            'player_skip': ['webpage', 'ios'],
                            'max_comments': [100, 100, 100, 100] # ✅ 댓글 수집량 확대 (장기 여행 단서 확보)
                        }
                    }
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={v_id}", download=False)
                    title = info.get('title', '')
                    description = info.get('description', '')

                    # 1. 자막 수집 (자동 생성 자막 포함)
                    sub_info = info.get('requested_subtitles', {}).get('ko') or \
                               info.get('automatic_captions', {}).get('ko')
                    
                    raw_transcript = ""
                    if sub_info:
                        res = requests.get(sub_info['url'], timeout=15)
                        if res.status_code == 200:
                            raw_transcript = clean_transcript(res.text)

                    # 2. 댓글 수집 (장기 여행은 시청자들의 '정보 공유' 댓글이 핵심)
                    comments_data = info.get('comments', [])
                    # 최대 100개의 댓글을 분석하여 "2일차에 갔던 곳 어디에요?" 같은 단서 확보
                    top_comments = [c.get('text', '') for c in comments_data[:100]]
                    comments_text = "\n".join(top_comments)

                    # ✅ [데이터 배치 전략]
                    # 장기 여행일수록 '설명란'의 타임라인 정보가 가장 정확하므로 최상단 배치
                    full_context = f"=== [영상 제목] ===\n{title}\n\n"
                    full_context += f"=== [설명란 및 타임라인 단서] ===\n{description}\n\n"
                    full_context += f"=== [시청자 제보 및 댓글 단서] ===\n{comments_text}\n\n"
                    full_context += f"=== [자막 전체 본문] ===\n{raw_transcript if raw_transcript else '자막 없음'}"

                    transcript_data = {
                        "video_id": v_id,
                        "title": title,
                        "transcript": full_context, 
                        "raw_info": {
                            "duration": info.get("duration"),
                            "view_count": info.get("view_count"),
                            "comment_count": len(top_comments),
                            "description_len": len(description)
                        }
                    }
                    
                    save_json(save_path, transcript_data)
                    results.append(transcript_data)
                    log("step1", f"✅ [{v_id}] 고밀도 텍스트 확보 완료 ({len(full_context):,}자)")
                    break

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    log("step1", f"⏳ [{v_id}] 차단 감지됨. {wait_time}초 대기 후 재시도...")
                    time.sleep(wait_time)
                else:
                    log("step1", f"❌ [{v_id}] 최종 수집 실패: {str(e)[:50]}")
    return results