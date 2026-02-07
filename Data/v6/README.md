# ClipRoute Demo Pipeline (fixed)

## 1) 폴더 구조

```
cliproute_fixed/
  run_pipeline.py
  config_example.py   # -> config.py로 복사해서 키 입력
  pipeline/
  llm/
  utils/
  data/               # 실행 시 자동 생성
```

## 2) 설치

```bash
pip install -r requirements.txt
```

> Whisper를 쓰려면 로컬에 `ffmpeg`가 설치되어 있어야 하며, `yt-dlp`도 필요합니다.

## 3) 실행

```bash
python run_pipeline.py
```

## 4) 산출물

- `data/step0_videos/videos.json`
- `data/step1_materials.json`
- `data/step2_places_raw.json`
- `data/step2_5_keywords_normalized.json`
- `data/step3_naver_verified/naver_verified_{video_id}.json`
- `data/step4_timeline_sorted/final_places_{video_id}.json`
- `data/step5_final/final_all.json`

