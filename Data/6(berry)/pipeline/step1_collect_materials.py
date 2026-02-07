from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import json
import html
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config
from utils.io import save_json
from utils.logging_utils import log
from utils.text_cleaner import merge_transcripts


try:
    import whisper  # openai-whisper
except Exception:
    whisper = None


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def _has_ytdlp() -> bool:
    return _which("yt-dlp") is not None


def _has_ffmpeg() -> bool:
    return _which("ffmpeg") is not None


def _load_whisper_model() -> Any:
    if whisper is None:
        return None
    model_name = getattr(config, "WHISPER_MODEL", "base")
    try:
        return whisper.load_model(model_name)
    except Exception as e:
        log("step1", "whisper.load_model failed", model=model_name, err=str(e)[:200])
        return None


def _run_whisper(model: Any, audio_path: Path, *, language: str = "ko") -> Optional[str]:
    if model is None:
        return None
    try:
        result = model.transcribe(str(audio_path), language=language)
        return (result or {}).get("text")
    except Exception as e:
        log("step1", "whisper transcribe failed", err=str(e)[:200])
        return None


_VTT_TIME_RE = re.compile(
    r"(?P<ts>(?:\d{1,2}:)?\d{1,2}:\d{2})(?:\.(?P<ms>\d{1,3}))?"
)


def _vtt_ts_to_seconds(ts: str) -> float:
    """Convert VTT timestamp like HH:MM:SS.mmm or MM:SS.mmm to seconds(float)."""
    if not ts:
        return 0.0
    ts = ts.strip()
    # split ms
    ms = 0
    if "." in ts:
        base, frac = ts.split(".", 1)
        try:
            ms = int((frac + "000")[:3])
        except Exception:
            ms = 0
    else:
        base = ts

    parts = base.split(":")
    try:
        if len(parts) == 2:
            mm, ss = parts
            sec = int(mm) * 60 + int(ss)
        elif len(parts) == 3:
            hh, mm, ss = parts
            sec = int(hh) * 3600 + int(mm) * 60 + int(ss)
        else:
            sec = 0
    except Exception:
        sec = 0

    return float(sec) + (ms / 1000.0)


_VTT_INLINE_TAG_RE = re.compile(r"<[^>]+>")


def _clean_vtt_text(s: str) -> str:
    if not s:
        return ""

    # Some VTTs contain double-escaped entities (e.g., &amp;gt;).
    # Unescape twice to be safe.
    try:
        s = html.unescape(s)
        s = html.unescape(s)
    except Exception:
        # keep original on failure
        pass

    # Remove inline WEBVTT tags like <00:00:01.000><c> ... </c>
    s = _VTT_INLINE_TAG_RE.sub("", s)

    # Remove leading speaker markers like '>>' (after unescape)
    s = re.sub(r"^\s*>>\s*", "", s)

    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _parse_vtt_cues(vtt_text: str, *, max_cues: int = 2000) -> List[Dict[str, Any]]:
    """Parse WEBVTT into cues: [{start,end,text}].

    NOTE: This is a lightweight parser for typical yt-dlp auto-sub VTT.
    """
    if not vtt_text:
        return []

    lines = vtt_text.splitlines()
    cues: List[Dict[str, Any]] = []

    i = 0
    # skip BOM/WEBVTT header
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].strip().upper().startswith("WEBVTT"):
        i += 1

    buf_text: List[str] = []
    cur_start = None
    cur_end = None

    def flush():
        nonlocal buf_text, cur_start, cur_end
        if cur_start is None or cur_end is None:
            buf_text = []
            cur_start = None
            cur_end = None
            return
        text_raw = " ".join([t.strip() for t in buf_text if t.strip()]).strip()
        text = _clean_vtt_text(text_raw)
        if text:
            cues.append({"start": cur_start, "end": cur_end, "text": text})
        buf_text = []
        cur_start = None
        cur_end = None

    while i < len(lines):
        ln = lines[i].rstrip("\n")
        s = ln.strip()

        # blank line ends a cue
        if not s:
            flush()
            i += 1
            if len(cues) >= max_cues:
                break
            continue

        # ignore NOTE/STYLE blocks crudely
        if s.upper().startswith("NOTE") or s.upper().startswith("STYLE"):
            # consume until blank
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            continue

        # cue timing line
        if "-->" in s:
            flush()
            # examples: 00:01:02.000 --> 00:01:04.000 align:start position:0%
            left = s.split("-->", 1)[0].strip()
            right = s.split("-->", 1)[1].strip()
            # right may include settings
            right_ts = right.split()[0].strip()
            cur_start = _vtt_ts_to_seconds(left)
            cur_end = _vtt_ts_to_seconds(right_ts)
            i += 1
            continue

        # optional numeric cue id line: skip
        if s.isdigit() and cur_start is None and cur_end is None:
            i += 1
            continue

        # text line
        buf_text.append(s)
        i += 1

    flush()
    return cues


_CHAPTER_LINE_RE = re.compile(
    r"^\s*(?:[-•*·]\s*)?(?:\[)?(?P<ts>(?:\d{1,2}:)?\d{1,2}:\d{2})\s*(?:[-–—:)]\s*)?(?P<title>.+?)\s*$"
)


def _extract_description_chapters(description: str, *, max_lines: int = 120) -> str:
    """Extract timestamp/chapter-like lines from YouTube description.

    Example lines:
      00:12 봉성식당: ...
      2:19 글로시 말차 ...
      01:02:30 ...

    Returns a newline-joined string (may be empty).
    """
    if not description:
        return ""

    lines = [ln.strip() for ln in description.splitlines() if ln.strip()]
    picked: List[str] = []

    for ln in lines:
        m = _CHAPTER_LINE_RE.match(ln)
        if not m:
            continue
        # Keep the original line (it often contains address hints)
        picked.append(ln)
        if len(picked) >= max_lines:
            break

    return "\n".join(picked)


# Whisper quality check helper
def _is_low_quality_whisper(text: Optional[str]) -> bool:
    """Heuristic to detect meaningless Whisper output.

    We prefer recall: if unsure, treat as low quality to allow yt-dlp fallback.
    """
    if not text:
        return True
    s = text.strip()
    if not s:
        return True

    # Too short
    if len(s) < int(getattr(config, "WHISPER_MIN_TEXT_CHARS", 450)):
        return True

    # Too few tokens
    if len(s.split()) < int(getattr(config, "WHISPER_MIN_TOKENS", 90)):
        return True

    # Korean ratio (for KR travel vlogs); low ratio often means noise/foreign music
    total = len(s)
    ko = sum(1 for ch in s if '가' <= ch <= '힣')
    if total > 0:
        ko_ratio = ko / total
        if ko_ratio < float(getattr(config, "WHISPER_MIN_KO_RATIO", 0.10)):
            return True

    return False


def run(videos: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    """Step1: 자막/오디오에서 텍스트 재료를 수집.

    반환: [{video_id, title, description, yt_dlp_vtt, whisper_text, transcript, transcript_source}]
    """
    if videos is None:
        raise ValueError("step1_collect_materials.run: videos is required (step0 결과를 넘겨주세요)")

    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_path = data_dir / "step1_materials.json"

    cues_dir = data_dir / "step1_vtt_cues"
    cues_dir.mkdir(parents=True, exist_ok=True)

    ytdlp_ok = _has_ytdlp()
    ffmpeg_ok = _has_ffmpeg()
    log("step1", "deps", ytdlp=ytdlp_ok, ffmpeg=ffmpeg_ok, whisper_pkg=bool(whisper))

    enable_whisper = bool(getattr(config, "ENABLE_WHISPER", True)) and whisper is not None and ytdlp_ok and ffmpeg_ok
    model = _load_whisper_model() if enable_whisper else None

    # Whisper-first controls
    whisper_lang = str(getattr(config, "WHISPER_LANGUAGE", "ko"))
    # Fetch yt-dlp subtitles even when Whisper is OK (for cues/seconds + enrichment).
    # NOTE: This does NOT change the "Whisper-first" policy; it only enriches materials.
    fetch_subs_for_cues = bool(getattr(config, "FETCH_SUBTITLES_FOR_CUES", True))

    # yt-dlp 최신 환경에서는 JS runtime이 없으면 일부 자막/포맷 추출이 실패할 수 있습니다.
    # 기본은 deno를 사용하되, 필요 시 config.YTDLP_JS_RUNTIME 로 변경 가능합니다.
    ytdlp_js_runtime = str(getattr(config, "YTDLP_JS_RUNTIME", "deno")).strip()

    def _ytdlp_base_cmd() -> List[str]:
        cmd = ["yt-dlp"]
        if ytdlp_js_runtime:
            cmd += ["--js-runtimes", ytdlp_js_runtime]

        # Optional: cookies / browser cookies / user-agent to reduce 403/age/consent blocks.
        cookies_file = (
            os.getenv("YTDLP_COOKIES")
            or str(getattr(config, "YTDLP_COOKIES", "") or "").strip()
        )
        cookies_from_browser = (
            os.getenv("YTDLP_COOKIES_FROM_BROWSER")
            or str(getattr(config, "YTDLP_COOKIES_FROM_BROWSER", "") or "").strip()
        )
        user_agent = (
            os.getenv("YTDLP_USER_AGENT")
            or str(getattr(config, "YTDLP_USER_AGENT", "") or "").strip()
        )

        if cookies_from_browser:
            # Example value: "chrome" or "chrome:profile" (yt-dlp supported syntax)
            cmd += ["--cookies-from-browser", cookies_from_browser]
        elif cookies_file:
            cmd += ["--cookies", cookies_file]

        if user_agent:
            cmd += ["--user-agent", user_agent]

        return cmd

    def _download_audio_for_whisper(url: str, out_path: Path) -> bool:
        """Download best audio for Whisper. Returns True if file exists.

        Whisper-first policy:
        - This function is only to *prepare* the audio input for Whisper.
        - If it fails, we may fall back to yt-dlp subtitles (VTT).
        """
        # Prefer m4a to reduce ffmpeg postprocess failures; Whisper can decode via ffmpeg.
        # Keep it configurable.
        audio_ext = str(getattr(config, "WHISPER_AUDIO_EXT", "m4a")).strip().lstrip(".") or "m4a"
        # Ensure extension matches path
        if out_path.suffix.lower() != f".{audio_ext}":
            out_path = out_path.with_suffix(f".{audio_ext}")

        # PO Token (optional) can be provided to improve 403 failures for some clients.
        # If you don't provide it, we still try clients that often work without PO tokens (e.g. web_safari).
        po_token = (
            os.getenv("YTDLP_PO_TOKEN")
            or str(getattr(config, "YTDLP_PO_TOKEN", "") or "").strip()
        )

        attempts = [
            # web_safari often exposes HLS/m3u8 formats that are less likely to require PO tokens for GVS.
            {
                "name": "web_safari",
                "extra": [
                    "-f",
                    f"bestaudio[ext={audio_ext}]/bestaudio/best",
                    "--extractor-args",
                    "youtube:player_client=web_safari",
                ],
            },
            # Standard bestaudio (default client selection)
            {
                "name": "bestaudio",
                "extra": ["-f", f"bestaudio[ext={audio_ext}]/bestaudio/best"],
            },
            # mweb client with optional PO token (when provided)
            {
                "name": "mweb",
                "extra": [
                    "-f",
                    f"bestaudio[ext={audio_ext}]/bestaudio/best",
                    "--extractor-args",
                    (
                        f"youtube:player_client=default,mweb;po_token=mweb.gvs+{po_token}"
                        if po_token
                        else "youtube:player_client=mweb"
                    ),
                ],
            },
            # Android client hint (sometimes helps when YouTube tightens web extraction)
            {
                "name": "android_client",
                "extra": [
                    "-f",
                    f"bestaudio[ext={audio_ext}]/bestaudio/best",
                    "--extractor-args",
                    "youtube:player_client=android",
                ],
            },
        ]

        # Retry knobs
        retries = int(getattr(config, "YTDLP_AUDIO_RETRIES", 2))
        sleep_sec = float(getattr(config, "YTDLP_AUDIO_RETRY_SLEEP", 6))

        for a in attempts:
            for r in range(retries + 1):
                # Clean stale file
                try:
                    out_path.unlink(missing_ok=True)
                except Exception:
                    pass

                cmd = (
                    _ytdlp_base_cmd()
                    + [
                        "--no-playlist",
                        "--no-progress",
                        "--retries",
                        "3",
                        "--fragment-retries",
                        "3",
                        "--concurrent-fragments",
                        "1",
                        "--socket-timeout",
                        "20",
                        "--geo-bypass",
                    ]
                    + a["extra"]
                    + ["-o", str(out_path), url]
                )

                try:
                    subprocess.run(
                        cmd,
                        check=True,
                        timeout=int(getattr(config, "YTDLP_AUDIO_TIMEOUT", 420)),
                        capture_output=True,
                    )
                    if out_path.exists() and out_path.stat().st_size > 0:
                        return True
                except Exception as e:
                    # log stderr snippet for diagnosis
                    extra = ""
                    try:
                        if hasattr(e, "stderr") and e.stderr:
                            extra = (
                                str(e.stderr, "utf-8", errors="ignore")[:600]
                                if isinstance(e.stderr, (bytes, bytearray))
                                else str(e.stderr)[:600]
                            )
                    except Exception:
                        extra = ""

                    log(
                        "step1",
                        "audio download failed",
                        attempt=a["name"],
                        retry=r,
                        video_url=url,
                        err=str(e)[:200],
                        stderr=extra,
                    )

                    # Backoff on 429 / Too Many Requests
                    if "429" in extra or "Too Many Requests" in extra or "HTTP Error 429" in str(e):
                        time.sleep(max(sleep_sec, 8.0))
                    else:
                        time.sleep(sleep_sec)

        return False

    results: List[Dict[str, Any]] = []

    for v in videos:
        vid = v.get("video_id")
        if not vid:
            continue

        title = (v.get("title") or "").strip()
        thumbnail_url = (v.get("thumbnail_url") or "").strip()
        description = v.get("description") or ""
        region_tag = (v.get("region_tag") or "").strip()
        url = v.get("source_url") or f"https://www.youtube.com/watch?v={vid}"

        yt_vtt: Optional[str] = None
        yt_vtt_cleaned: Optional[str] = None
        whisper_text: Optional[str] = None

        vtt_cues: List[Dict[str, Any]] = []
        cues_path: Optional[Path] = None

        whisper_low_quality = True


        # (B) Whisper (오디오 추출 + STT) - Whisper is primary
        if enable_whisper and model is not None:
            with tempfile.TemporaryDirectory() as td:
                audio_path = Path(td) / f"{vid}.m4a"
                try:
                    ok = _download_audio_for_whisper(url, audio_path)
                    if ok and audio_path.exists():
                        whisper_text = _run_whisper(model, audio_path, language=whisper_lang)
                        whisper_low_quality = _is_low_quality_whisper(whisper_text)
                        log(
                            "step1",
                            "whisper done",
                            video_id=vid,
                            ok=bool((whisper_text or "").strip()),
                            lang=whisper_lang,
                            low_quality=whisper_low_quality,
                        )
                    else:
                        log("step1", "audio extraction produced no file", video_id=vid)
                        whisper_low_quality = True
                except Exception as e:
                    log("step1", "whisper pipeline failed", video_id=vid, err=str(e)[:200])
                    whisper_low_quality = True
        else:
            if not (whisper is not None):
                log("step1", "whisper pkg missing; skipping", video_id=vid)
            elif not (ytdlp_ok and ffmpeg_ok):
                log("step1", "yt-dlp/ffmpeg missing; skipping whisper", video_id=vid)
            whisper_low_quality = True

        # (A) yt-dlp 자막(VTT) - Whisper가 저품질이면 fallback, Whisper가 OK여도 cues/보강용으로 가져올 수 있음
        # - Whisper-first 정책 유지: Whisper가 OK이면 transcript는 Whisper를 우선 사용하고, VTT는 보강/seconds(cues)용으로만 사용
        if ytdlp_ok and (whisper_low_quality or fetch_subs_for_cues):
            try:
                if not whisper_low_quality:
                    log("step1", "fetching yt-dlp subtitles for cues/enrich", video_id=vid)
                # Avoid requesting multiple subtitle tracks at once (can trigger 429).
                # Try Korean first, then English only if Korean is not available.
                def _try_subs(lang: str) -> Optional[Path]:
                    cmd = _ytdlp_base_cmd() + [
                        "--skip-download",
                        "--write-subs",
                        "--write-auto-subs",
                        "--sub-langs",
                        lang,
                        "--sub-format",
                        "vtt",
                        "-o",
                        f"{vid}.%(ext)s",
                        url,
                    ]
                    subprocess.run(cmd, check=True, capture_output=True, timeout=60)
                    # Prefer the requested language file if present; otherwise pick any .vtt.
                    cand = sorted(Path(".").glob(f"{vid}*.{lang}.vtt"))
                    if not cand:
                        cand = sorted(Path(".").glob(f"{vid}*.vtt"))
                    return cand[0] if cand else None

                # Clean up any stale subtitle files from previous runs
                try:
                    for p in Path(".").glob(f"{vid}*.vtt"):
                        p.unlink(missing_ok=True)
                except Exception:
                    pass
                vtt_path = None
                for lang in ("ko", "en"):
                    try:
                        vtt_path = _try_subs(lang)
                        if vtt_path and vtt_path.exists():
                            break
                    except Exception as e_lang:
                        # If we hit 429, wait briefly and retry once for this lang
                        msg = str(e_lang)
                        extra_lang = ""
                        try:
                            if hasattr(e_lang, "stderr") and e_lang.stderr:
                                extra_lang = (
                                    str(e_lang.stderr, "utf-8", errors="ignore")[:400]
                                    if isinstance(e_lang.stderr, (bytes, bytearray))
                                    else str(e_lang.stderr)[:400]
                                )
                        except Exception:
                            extra_lang = ""

                        if "HTTP Error 429" in msg or "Too Many Requests" in msg or "429" in extra_lang:
                            log("step1", "yt-dlp subtitle rate-limited; retrying", video_id=vid, lang=lang)
                            time.sleep(8)
                            try:
                                vtt_path = _try_subs(lang)
                                if vtt_path and vtt_path.exists():
                                    break
                            except Exception:
                                # fall through to next lang
                                pass
                        else:
                            # non-429 error: keep trying next language
                            pass

                # vtt_path may still be None if no subtitles exist

                if vtt_path and vtt_path.exists():
                    yt_vtt = vtt_path.read_text(encoding="utf-8", errors="ignore")
                    # VTT cue(타임스탬프) 파싱/저장: Step2에서 seconds 보강에 사용
                    vtt_cues = []
                    cues_path = None
                    try:
                        vtt_cues = _parse_vtt_cues(yt_vtt)
                        cues_path = cues_dir / f"cues_{vid}.json"
                        save_json(cues_path, {"video_id": vid, "title": title, "cues": vtt_cues})
                        yt_vtt_cleaned = "\n".join(c.get("text", "") for c in vtt_cues if (c.get("text") or "").strip())
                    except Exception as e:
                        log("step1", "vtt cue parse failed", video_id=vid, err=str(e)[:200])
                    # 생성물 정리
                    try:
                        vtt_path.unlink(missing_ok=True)
                    except Exception:
                        pass
                    log("step1", "yt-dlp subtitle ok", video_id=vid)
                else:
                    log("step1", "yt-dlp subtitle not found", video_id=vid)
            except Exception as e:
                # include stderr/stdout snippet when available
                extra = ""
                try:
                    if hasattr(e, "stderr") and e.stderr:
                        extra = str(e.stderr, "utf-8", errors="ignore")[:400] if isinstance(e.stderr, (bytes, bytearray)) else str(e.stderr)[:400]
                    elif hasattr(e, "output") and e.output:
                        extra = str(e.output, "utf-8", errors="ignore")[:400] if isinstance(e.output, (bytes, bytearray)) else str(e.output)[:400]
                except Exception:
                    extra = ""
                log("step1", "yt-dlp subtitle failure", video_id=vid, err=str(e)[:200], stderr=extra)
        else:
            if not ytdlp_ok:
                log("step1", "yt-dlp not installed; skipping subtitles", video_id=vid)
            else:
                # If fetch_subs_for_cues is False and Whisper is OK, we truly skip subtitle fetching.
                log(
                    "step1",
                    "whisper ok; subtitle fetch disabled",
                    video_id=vid,
                    fetch_subs_for_cues=bool(fetch_subs_for_cues),
                )

        # Clean VTT inline tags/entities before using as transcript material
        # Prefer cue-based transcript if we parsed cues; otherwise fall back to a simple line-clean.
        if yt_vtt and not yt_vtt_cleaned:
            try:
                yt_vtt_cleaned = "\n".join(_clean_vtt_text(ln) for ln in yt_vtt.splitlines())
            except Exception:
                yt_vtt_cleaned = yt_vtt

        # Prefer whisper transcript; if we have subtitle cues, merge to enrich/patch holes.
        transcript = merge_transcripts(whisper_text, yt_vtt_cleaned if yt_vtt_cleaned is not None else yt_vtt)

        if whisper_text and yt_vtt:
            transcript_source = "whisper+yt-dlp"
        elif whisper_text:
            transcript_source = "whisper"
        elif yt_vtt:
            transcript_source = "yt-dlp"
        else:
            transcript_source = "none"

        # 최후의 안전장치: 자막/whisper가 모두 비었으면 제목/설명으로라도 Step2 재료를 만들어줌
        if not (transcript or "").strip():
            fallback_meta = (title + "\n" + (description or "")).strip()
            if fallback_meta:
                transcript = fallback_meta
                transcript_source = (transcript_source + "+meta").lstrip("+")

        # 설명란에 타임스탬프/챕터 형태의 데이터가 있으면 반드시 transcript에 포함
        desc_chapters = _extract_description_chapters(description)
        if desc_chapters:
            base = (transcript or "").strip()
            if base:
                transcript = base + "\n\n[DESCRIPTION_CHAPTERS]\n" + desc_chapters
            else:
                transcript = "[DESCRIPTION_CHAPTERS]\n" + desc_chapters
            transcript_source = (transcript_source + "+desc").lstrip("+")

        results.append(
            {
                "video_id": vid,
                "title": title,
                "thumbnail_url": thumbnail_url,
                "description": description,
                "region_tag": region_tag,
                "yt_dlp_transcript_vtt": yt_vtt,
                "yt_dlp_transcript_vtt_clean": yt_vtt_cleaned or "",
                "whisper_transcript": whisper_text,
                "transcript": transcript,
                "transcript_source": transcript_source,
                "has_ytdlp_subtitle": bool(yt_vtt),
                "vtt_cues_path": str(cues_path) if cues_path else "",
                "vtt_cues_count": len(vtt_cues),
            }
        )

    save_json(out_path, results)
    log("step1", "saved", path=str(out_path), total=len(results))
    return results
