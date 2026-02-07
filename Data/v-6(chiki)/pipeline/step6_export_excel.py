import pandas as pd
import json
import os
from utils.logging_utils import log

def run(json_path="data/step4_jude_spec.json", excel_path="data/clip_route_v6_final.xlsx"):
    """
    Step 6: 주드 API 명세서 규격의 JSON을 읽어 지역별로 시트를 나누어 저장합니다. (중략 없음)
    """
    log("step6", f"📊 최종 엑셀 변환 가동: {json_path}")
    
    if not os.path.exists(json_path):
        log("step6", "❌ 변환 실패: JSON 파일이 없습니다. Step 4를 먼저 확인하세요.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_rows = []
        for course in data:
            # 주드 명세서 8번 응답 구조에서 상위 정보 추출
            v_title = course.get("videoTitle")
            r_name = course.get("regionName", "미지정") 
            
            for iti in course.get("itineraries", []):
                day = iti.get("visitDay")
                for p in iti.get("places", []):
                    # 주드의 API 필드명과 100% 일치화
                    all_rows.append({
                        "regionName": r_name,         
                        "videoTitle": v_title,
                        "visitDay": day,
                        "visitOrder": p.get("visitOrder"),
                        "placeName": p.get("placeName"),
                        "category": p.get("category"),
                        "address": p.get("address"),
                        "lat": p.get("lat"),
                        "lng": p.get("lng"),
                        "timestamp": p.get("timestamp")
                    })

        if not all_rows:
            log("step6", "⚠️ 변환할 데이터가 없습니다.")
            return

        df_total = pd.DataFrame(all_rows)

        # ✅ 지역별(regionName)로 시트를 나누어 저장
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            regions = df_total['regionName'].unique()
            for region in regions:
                df_region = df_total[df_total['regionName'] == region]
                # 시트 이름 제한(31자) 및 특수문자 대응
                sheet_name = str(region)[:30]
                df_region.to_excel(writer, sheet_name=sheet_name, index=False)
                log("step6", f"✅ '{sheet_name}' 지역 시트 생성 완료")

        log("step6", f"✨ 제이(Jay) 전달용 최종 엑셀 생성: {os.path.abspath(excel_path)}")
        return excel_path

    except Exception as e:
        log("step6", f"❌ 엑셀 변환 중 오류 발생: {e}")
        return None