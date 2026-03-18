import os
import re
import json
import time
import random
import yt_dlp
from utils.logging_utils import log
from utils.io import save_json, load_json

def clean_transcript(raw_text):
    """
    자막 데이터에서 타임스탬프, WEBVTT 헤더, 불필요한 태그 및 공백을 제거합니다.
    """
    # 1. 타임스탬프 제거 (예: 00:00:01.000 --> 00:00:03.000)
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', raw_text)
    # 2. WEBVTT 헤더 및 메타데이터 제거
    text = re.sub(r'WEBVTT|Kind:.*|Language:.*', '', text)
    # 3. 유니코드 및 특수 태그 제거 (예: <c>, [음악])
    text = re.sub(r'\[.*?\]|\<.*?\>|\(.*\)', '', text)
    # 4. 반복되는 공백 및 줄바꿈 정제
    cleaned_lines = [line.strip() for line in text.split('\n') if line.strip()]
    return " ".join(cleaned_lines)

def run(video_list):
    log(f"🚀 Step 1: 소재 수집 시작 - 총 {len(video_list)}개 영상 분석")
    
    data_dir = "data/step1_transcripts"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    results = []
    
    ydl_opts = {
        'skip_download': True,
        'writeautomationsub': True, # 자동 자막 포함
        'getcomments': True,
        'subtitleslangs': ['ko'],
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'webpage']}}
    }

    for video in video_list:
        v_id = video['video_id']
        v_title = video['title']
        save_path = f"{data_dir}/{v_id}.json"
        
        log(f"📥 영상 분석 중: [{v_title[:20]}...]")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={v_id}", download=False)
                
                # 자막 추출 및 정제
                raw_transcript = ""
                sub_info = info.get('requested_subtitles', {}).get('ko') or info.get('automatic_captions', {}).get('ko')
                
                if sub_info:
                    import requests
                    res = requests.get(sub_info['url'], timeout=10)
                    if res.status_code == 200:
                        raw_transcript = clean_transcript(res.text)
                
                # 댓글 데이터 수집 (상위 50개)
                comments_data = info.get('comments', [])[:50]
                top_comments = [c.get('text', '') for c in comments_data if c.get('text')]
                
                full_context = {
                    'video_id': v_id,
                    'title': v_title,
                    'description': info.get('description', ''),
                    'transcript': raw_transcript,
                    'comments': top_comments,
                    'view_count': info.get('view_count', 0),
                    'duration': info.get('duration', 0)
                }
                
                save_json(full_context, save_path)
                results.append(full_context)
                log(f"✅ 수집 완료: 자막({len(raw_transcript)}자), 댓글({len(top_comments)}개)")
                
                # 차단 방지를 위한 랜덤 슬립
                time.sleep(random.uniform(1.0, 3.0))

        except Exception as e:
            log(f"❌ [{v_id}] 수집 중 오류 발생: {str(e)}")
            continue

    log(f"🏁 Step 1 완료: {len(results)}개 영상의 상세 소재 확보")
    return results