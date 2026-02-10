import os
import datetime
import requests
import re
import time
import pandas as pd
from utils.io import save_json, load_json
from utils.logging_utils import log

def get_similarity(a, b):
    """문자열 유사도 측정 (포함 관계 가산점 적용)"""
    a_clean = re.sub(r'[^가-힣a-zA-Z0-9]', '', a)
    b_clean = re.sub(r'[^가-힣a-zA-Z0-9]', '', b)
    if not a_clean or not b_clean: return 0.0
    if a_clean in b_clean or b_clean in a_clean: return 0.96
    common = set(a_clean) & set(b_clean)
    union = set(a_clean) | set(b_clean)
    return len(common) / len(union) if union else 0.0

def run(report: dict, region: str = "제주"):
    """
    Step 3: 네이버 API 2중 검색을 통해 주소 확보율을 극대화합니다.
    검색 실패 시에도 데이터를 삭제하지 않고 보존하며, 타 지역 환각만 걸러냅니다.
    """
    log("step3", f"🎯 Step 3: 주소 풀-로드 엔진 기동 (입력 지역: {region})")
    
    cid = os.getenv("NAVER_CLIENT_ID")
    csec = os.getenv("NAVER_CLIENT_SECRET")
    
    actual_data = report.get("itinerary", report)
    verified_results = {}
    excel_rows = []

    for vid, itinerary_list in actual_data.items():
        if not isinstance(itinerary_list, list): continue
        
        v_list = []
        for p in itinerary_list:
            if isinstance(p, str): p = {"place_name": p}
            elif not isinstance(p, dict): continue

            name = p.get("place_name") or p.get("name")
            if not name or "미언급" in name: 
                p["address"] = "주소 미추출"
                v_list.append(p)
                continue

            # ✅ [보정 핵심] 불필요한 노이즈 제거 후 검색어 생성
            clean_name = re.sub(r'맛집|카페|추천|장소|코스', '', name).strip()
            
            try:
                # 🚀 2중 검색 전략: [지역+이름] 우선 시도 후 실패 시 [이름]만 검색
                search_queries = [f"{region} {clean_name}", clean_name]
                found_item = None
                
                for query in search_queries:
                    resp = requests.get(
                        "https://openapi.naver.com/v1/search/local.json",
                        headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": csec},
                        params={"query": query, "display": 5}, # 결과 5개까지 훑음
                        timeout=5
                    )
                    
                    if resp.status_code == 200 and resp.json().get("items"):
                        items = resp.json()["items"]
                        # 검색 결과 중 실제 해당 지역 주소가 포함된 항목을 최우선 선택
                        for item in items:
                            if region in item['roadAddress']:
                                found_item = item
                                break
                        if found_item: break # 지역 일치 항목 찾으면 즉시 중단
                
                # 결과 반영
                if found_item:
                    v_name = re.sub(r'<[^>]*>', '', found_item['title'])
                    p.update({
                        "place_name": v_name,
                        "address": found_item['roadAddress'],
                        "is_verified": True,
                        "lat": found_item.get('mapy'),
                        "lng": found_item.get('mapx')
                    })
                else:
                    if not p.get("address"):
                        p["address"] = "주소 미추출 (수동 확인 필요)"

                time.sleep(0.07) # API 속도 안정화
            except Exception as e:
                log("step3", f"⚠️ [{name}] 검색 건너뜀: {e}")
                if not p.get("address"): p["address"] = "주소 미추출"

            # ✅ 2. 지역 필터링 (환각 방지)
            address = p.get("address", "")
            if address == "주소 미추출 (수동 확인 필요)" or address == "주소 미추출" or region in address:
                v_list.append(p)
            else:
                log("step3", f"🗑️ 타 지역 환각 제거: {name} ({address})")
                continue
            
            excel_rows.append({
                "Video_ID": vid,
                "Original_Name": name,
                "Verified_Name": p.get("place_name"),
                "Address": p.get("address")
            })
            
        if v_list:
            verified_results[vid] = v_list
            log("step3", f"✅ {vid} 주소 보정 완료 (데이터 {len(v_list)}개)")

    save_json("data/step3_verified.json", verified_results)
    
    if excel_rows:
        try:
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            file_name = f"data/v6_verified_itinerary_{timestamp}.xlsx"
            pd.DataFrame(excel_rows).to_excel(file_name, index=False)
        except: pass
            
    return verified_results