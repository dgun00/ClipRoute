import folium
import os
from utils.io import load_json

def run(sorted_data: dict, region: str = "제주"):
    # 지도 중심 설정
    m = folium.Map(location=[33.3617, 126.5292], zoom_start=10)
    
    total_count = 0
    for vid, day_list in sorted_data.items():
        video_count = 0
        for day_data in day_list:
            day_label = day_data.get("day", "일정 미지정 : ")
            locations = day_data.get("locations", [])
            
            for loc in locations:
                if not loc.get("is_verified"): continue
                
                order = loc.get("visit_order", "?")
                # 치키님 요청 포맷: [1일차 : ] [1] 상호명
                title_text = f"[{day_label}] [{order}] {loc['verified_name']}"
                popup_text = f"<b>{title_text}</b><br>사유: {loc.get('visit_reason', '')}"
                
                folium.Marker(
                    location=[float(loc['map_y'])/1e7, float(loc['map_x'])/1e7],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=title_text,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
                
                video_count += 1
                total_count += 1
        print(f"[step5] video_id={vid} 추출 장소={video_count}개")

    os.makedirs("data", exist_ok=True)
    m.save("data/step5_map.html")
    print(f"[step5] 총 {total_count}개의 핀이 박힌 지도가 생성되었습니다.")