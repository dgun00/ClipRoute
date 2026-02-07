from pathlib import Path
import config
from utils.io import load_json
from utils.logging_utils import log


def run():
    in_dir = Path(getattr(config, "DATA_DIR", "data")) / "step4_timeline_sorted"
    for fp in in_dir.glob("final_places_*.json"):
        data = load_json(fp)
        log("step5", f"{data['video_id']} places={len(data['final_places'])}")