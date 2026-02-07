import os
import requests
import re
import time
import pandas as pd
import datetime
from utils.io import save_json, load_json
from utils.logging_utils import log

def get_similarity(a, b):
    """
    팀장님 지시 사항: 포함 관계 시 0.96 부여 및 자카드 유사도 적용
    """
    a_clean = re.sub(r'[^가-힣a-zA-Z0-9]', '', a)
    b_clean = re.sub(r'[^가-힣a-zA-Z0-9]', '', b)
    
    if not a_clean or not b_clean: return 0.0
    
    # 포함 관계 가산점
    if a_clean in b_clean or b_clean in a_clean:
        return 0.96
    
    common = set(a_clean) & set(b_clean)
    union = set(a_clean) | set(b_clean)
    return len(common) / len(union) if union else 0.0

def run(report: dict, region: str = "제주"):
    log("step3", f"🎯 Step 3: 네이버 검증 (유사도: 0.45, 지역힌트: [{region}])")
    
    video_meta = {}
    meta_path = "data/step0_videos.json"
    try:
        if os.path.exists(meta_path):
            video_meta = {v['video_id']: v for v in load_json(meta_path)}
    except Exception as e:
        log("step3", f"⚠️ 메타데이터 로드 중 오류: {e}")

    actual_data = report.get("itinerary", report)
    verified_results = {}
    excel_rows = []
    
    cid = os.getenv("NAVER_CLIENT_ID")
    csec = os.getenv("NAVER_CLIENT_SECRET")

    for vid, itinerary_list in actual_data.items():
        v_list = []
        
        # 데이터가 리스트 형태가 아니면 스킵하여 에러 방지
        if not isinstance(itinerary_list, list): continue

        for p in itinerary_list:
            # ✅ [데이터 가드] p가 딕셔너리가 아닌 문자열로 들어온 경우 대응
            # AttributeError: 'str' object has no attribute 'get' 방지
            if isinstance(p, str):
                name = p
                p = {"place_name": name} # 이후 로직 호환을 위해 객체화
            elif isinstance(p, dict):
                name = p.get("place_name")
            else:
                continue

            if not name: continue
            
            try:
                # 검색 쿼리에 지역 힌트 삽입
                query_with_hint = f"[{region}] {name}"
                
                resp = requests.get(
                    "https://openapi.naver.com/v1/search/local.json",
                    headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": csec},
                    params={"query": query_with_hint, "display": 1},
                    timeout=10
                )
                
                if resp.status_code == 200 and resp.json().get("items"):
                    item = resp.json()["items"][0]
                    v_name = re.sub(r'<[^>]*>', '', item['title'])
                    sim = get_similarity(name, v_name)
                    
                    if sim >= 0.45:
                        # 좌표 데이터 보정 및 업데이트
                        p.update({
                            "verified_name": v_name,
                            "road_address": item['roadAddress'],
                            "naver_top": item,
                            "is_verified": True,
                            "similarity_score": sim,
                            "lat": item.get('mapy'), 
                            "lng": item.get('mapx')
                        })
                        v_list.append(p)
                        
                        excel_rows.append({
                            "Video_ID": vid,
                            "Original_Name": name,
                            "Verified_Name": v_name,
                            "Similarity": sim,
                            "Address": item['roadAddress']
                        })
                time.sleep(0.06)
            except Exception as e:
                log("step3", f"❌ [{name}] 검증 에러: {e}")
                
        if v_list:
            verified_results[vid] = v_list
            log("step3", f"🏆 확실한 영상 등록: {vid} (핀 {len(v_list)}개)")

    save_json("data/step3_verified.json", verified_results)
    
    if excel_rows:
        try:
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            file_name = f"data/v6_verified_itinerary_{timestamp}.xlsx"
            
            pd.DataFrame(excel_rows).to_excel(file_name, index=False)
            log("step3", f"📊 엑셀 리포트 생성 완료: {file_name}")
        except Exception as e:
            log("step3", f"⚠️ 엑셀 저장 실패: {e}")
            pd.DataFrame(excel_rows).to_excel("data/v6_last_hope_itinerary.xlsx", index=False)
        
    return verified_results