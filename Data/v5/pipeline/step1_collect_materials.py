import os
import openai
import subprocess
from typing import List
from utils.io import save_json
from utils.logging_utils import log

def download_audio(video_id: str) -> str:
    """yt-dlp를 사용하여 오디오를 확실하게 추출합니다."""
    output_path = f"data/temp_audio/{video_id}.mp3"
    if os.path.exists(output_path):
        return output_path
    
    os.makedirs("data/temp_audio", exist_ok=True)
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    cmd = [
        'yt-dlp', '-x', '--audio-format', 'mp3', 
        '--audio-quality', '0', 
        '--no-check-certificate',
        '-o', f'data/temp_audio/{video_id}.%(ext)s', url
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except Exception as e:
        log("step1", f"❌ 오디오 추출 실패 ({video_id}): {e}")
        return ""

def transcribe_audio_api(audio_path: str) -> str:
    """OpenAI Whisper API로 텍스트 변환"""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        with open(audio_path, "rb") as f:
            return client.audio.transcriptions.create(
                model="whisper-1", 
                file=f, 
                response_format="text"
            )
    except Exception:
        return ""

def run(videos: List[dict]) -> List[dict]:
    log("step1", "⚡ Whisper API 분석 모드 가동")
    materials = []
    for v in videos:
        video_id = v["video_id"]
        audio_path = download_audio(video_id)
        if audio_path and os.path.exists(audio_path):
            print(f"🎙️  [{video_id}] API 분석 중...")
            v["transcript"] = transcribe_audio_api(audio_path)
        materials.append(v)
    save_json("data/step1_materials.json", materials)
    return materials