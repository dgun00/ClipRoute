import folium
import os
from utils.logging_utils import log

def run(sorted_data: dict, region: str, color_map: dict):
    """
    Step 5: 정수형 좌표를 실수형 위경도로 변환하여 핀을 정확히 꽂습니다. (중략 없음)
    """
    log("step5", f"📍 Step 5 가동: [{region}] 좌표 정밀 보정 및 지도 생성")

    # 1. 지도의 기본 중심점 (제주)
    m = folium.Map(location=[33.3617, 126.5292], zoom_start=10)
    total_pins = 0

    for vid, places in sorted_data.items():
        color = color_map.get(vid, "gray")
        path_points = []

        for p in places:
            try:
                # ✅ 핵심 수정: 네이버 API 특유의 정수형 좌표(KATECH) 대응
                # 334963420 -> 33.4963420 으로 변환하는 로직 추가
                raw_lat = str(p.get('lat', ''))
                raw_lng = str(p.get('lng', ''))

                if not raw_lat or not raw_lng:
                    continue

                # 점(.)이 없는 거대 정수라면 10,000,000으로 나눠서 소수점 생성
                if '.' not in raw_lat and len(raw_lat) > 5:
                    lat = float(raw_lat) / 10000000.0
                    lng = float(raw_lng) / 10000000.0
                else:
                    lat = float(raw_lat)
                    lng = float(raw_lng)

                # 위경도 범위 체크 (제주도 범위를 너무 벗어나면 무시)
                if not (30 < lat < 40 and 120 < lng < 135):
                    continue

            except (ValueError, TypeError):
                continue
            
            name = p.get('place_name') or p.get('name', '알 수 없는 장소')
            
            if lat and lng:
                tooltip_text = f"📺 {vid} | 📍 {name} ({p.get('day', 1)}일차)"
                popup_text = f"<b>{name}</b><br>출처: {vid}<br>{p.get('visit_reason', '')}"
                
                folium.Marker(
                    location=[lat, lng],
                    tooltip=folium.Tooltip(tooltip_text, sticky=True),
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
                
                path_points.append([lat, lng])
                total_pins += 1

        # 동선 연결 (유효한 좌표가 2개 이상일 때만)
        if len(path_points) > 1:
            folium.PolyLine(
                locations=path_points,
                color=color,
                weight=3,
                opacity=0.6,
                dash_array='5, 10'
            ).add_to(m)

    # 4. 저장
    save_path = "data/step5_map.html"
    if not os.path.exists("data"):
        os.makedirs("data")
    
    m.save(save_path)
    log("step5", f"✨ 지도 생성 완료! (보정된 핀 {total_pins}개 꽂힘)")

    return save_path