import os
import yt_dlp
import requests
import re
from utils.logging_utils import log
from utils.io import save_json, load_json

def clean_transcript(raw_text):
    """
    VTT/SRT 형식의 자막에서 타임라인 태그와 불필요한 공백을 제거합니다. (중략 없음)
    """
    # 1. <v ...> 태그 제거
    text = re.sub(r'<[^>]*>', '', raw_text)
    # 2. 타임라인 패턴 (00:00:00.000) 제거
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', text)
    # 3. WEBVTT 헤더 및 메타데이터 제거
    text = re.sub(r'WEBVTT|Kind:.*|Language:.*', '', text)
    # 4. 반복되는 공백 및 줄바꿈 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def run(video_list: list):
    """
    Step 1: 자막 URL에서 본문 전체를 추출하여 Gemini Thinking 모델의 재료를 확보합니다. (중략 없음)
    """
    log("step1", "⚡ Step 1 가동: Thinking 모델용 풀-텍스트 추출 엔진")
    
    results = []
    data_dir = "data/step1_transcripts"
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for video in video_list:
        v_id = video['video_id']
        save_path = os.path.join(data_dir, f"{v_id}.json")

        # 기존 자막이 있다면 재사용
        if os.path.exists(save_path):
            log("step1", f"♻️ [{v_id}] 기존 데이터 발견! 재분석 생략")
            results.append(load_json(save_path))
            continue

        log("step1", f"📥 [{v_id}] 자막 본문 수집 시작 (Deep Thinking 준비)...")

        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko'],
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage', 'ios']
                }
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={v_id}", download=False)
                title = info.get('title', 'Untitled Video')
                
                # 자막 데이터 URL 확보
                sub_info = info.get('requested_subtitles', {}).get('ko') or \
                           info.get('automatic_captions', {}).get('ko')
                
                if sub_info and sub_info.get('url'):
                    # ✅ 핵심: 자막 URL에 직접 접속하여 전체 본문 긁어오기
                    res = requests.get(sub_info['url'], timeout=10)
                    if res.status_code == 200:
                        # 태그 제거 및 텍스트 정제
                        full_transcript = clean_transcript(res.text)
                        log("step1", f"📝 [{v_id}] 본문 {len(full_transcript):,}자 확보 성공")
                    else:
                        full_transcript = "자막 본문 다운로드 실패"
                else:
                    full_transcript = "자막 데이터를 찾을 수 없습니다."

                transcript_data = {
                    "video_id": v_id,
                    "title": title,
                    "transcript": full_transcript,
                    "raw_info": {
                        "duration": info.get("duration"),
                        "view_count": info.get("view_count")
                    }
                }
                
                save_json(save_path, transcript_data)
                results.append(transcript_data)
                log("step1", f"✅ [{v_id}] 자막 풀-텍스트 로드 완료")
                
        except Exception as e:
            log("step1", f"❌ [{v_id}] 수집 실패: {str(e)[:150]}")

    return results