import json
from pathlib import Path
import config

INPUT_DIR = Path("outputs")
OUTPUT_DIR = Path("maps")
OUTPUT_DIR.mkdir(exist_ok=True)

NAVER_MAP_CLIENT_ID = config.NAVER_MAP_CLIENT_ID

DAY_COLORS = [
    "#FF0000",  # red
    "#FF7F00",  # orange
    "#FFFF00",  # yellow
    "#00FF00",  # green
    "#0000FF",  # blue
    "#4B0082",  # indigo
    "#8B00FF",  # violet
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <script src="https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId={client_id}"></script>
</head>
<body>
<div id="map" style="width:100%;height:100vh;"></div>

<script>
var map = new naver.maps.Map('map', {{
    center: new naver.maps.LatLng({center_lat}, {center_lng}),
    zoom: 10
}});

{markers}

{polylines}
</script>
</body>
</html>
"""

def build_step4(step3_file: Path):
    with open(step3_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    places = [
        p for p in data["verified_places"]
        if p.get("verified") and "lat" in p and "lng" in p
    ]

    if not places:
        print(f"❌ 지도 생성 불가: {data['video_id']}")
        return

    # day → 장소 그룹
    day_map = {}
    for p in places:
        day_map.setdefault(p["day"], []).append(p)

    # day별 order 정렬
    for day in day_map:
        day_map[day].sort(key=lambda x: x["order"])

    # 📌 터미널 출력
    print(f"\n🎬 {data['title']}")
    for day, items in day_map.items():
        print(f"  📅 Day {day}")
        for p in items:
            print(f"    {p['order']}. {p['name']}")

    # 지도 중심 (첫 장소 기준)
    center_lat = places[0]["lat"]
    center_lng = places[0]["lng"]

    markers_js = []
    polylines_js = []

    for day, items in day_map.items():
        color = DAY_COLORS[(day - 1) % len(DAY_COLORS)]
        path = []

        for p in items:
            markers_js.append(f"""
new naver.maps.Marker({{
    position: new naver.maps.LatLng({p['lat']}, {p['lng']}),
    map: map,
    icon: {{
        content: '<div style="background:{color};color:white;border-radius:50%;width:28px;height:28px;line-height:28px;text-align:center;font-weight:bold;">{p['order']}</div>',
        size: new naver.maps.Size(28, 28),
        anchor: new naver.maps.Point(14, 14)
    }},
    title: "{p['name']}"
}});
""")
            path.append(f"new naver.maps.LatLng({p['lat']}, {p['lng']})")

        # day별 경로선
        if len(path) >= 2:
            polylines_js.append(f"""
new naver.maps.Polyline({{
    map: map,
    path: [{",".join(path)}],
    strokeColor: "{color}",
    strokeWeight: 4
}});
""")

    html = HTML_TEMPLATE.format(
        title=data["title"],
        client_id=NAVER_MAP_CLIENT_ID,
        center_lat=center_lat,
        center_lng=center_lng,
        markers="\n".join(markers_js),
        polylines="\n".join(polylines_js)
    )

    out_path = OUTPUT_DIR / f"map_{data['video_id']}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"🗺 지도 생성 완료 → {out_path.name}")

def main():
    files = sorted(INPUT_DIR.glob("step3_verified_*.json"))
    for f in files:
        build_step4(f)

if __name__ == "__main__":
    main()
