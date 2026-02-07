import re
from playwright.sync_api import sync_playwright

def resolve_map_links(description):
    # 1. 지도 관련 URL 패턴 추출
    urls = re.findall(r'(https?://(?:kko\.kakao\.com|naver\.me)/[a-zA-Z0-9]+)', description)
    if not urls:
        return ""

    hints = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 실제 사용자처럼 보이게 세션 설정
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        for url in urls:
            try:
                page = context.new_page()
                # 페이지 로딩 및 네트워크 안정화 대기
                page.goto(url, wait_until="networkidle", timeout=15000)
                
                # ✅ [핵심] 카카오맵 그룹 리스트의 다양한 클래스명을 모두 뒤집니다.
                # .tit_name (리스트 상호명), .link_txt (상세 링크 텍스트) 등
                page.wait_for_timeout(3000) # 자바스크립트 렌더링을 위해 3초 더 대기
                
                # 카카오맵 그룹 페이지의 상호명 요소들을 싹 다 가져옵니다.
                selectors = [".tit_name", ".txt_placename", ".link_place", "strong.tit_item"]
                for selector in selectors:
                    elements = page.query_selector_all(selector)
                    for el in elements:
                        name = el.inner_text().strip()
                        if name and name not in ["카카오맵", "지도", "로그인", "메뉴"] and len(name) > 1:
                            hints.append(name)
                
                # 만약 리스트를 못 찾았다면 타이틀이라도 확보
                if not hints:
                    title = page.title()
                    clean_title = re.sub(r" \| 카카오맵| - 네이버 지도|카카오맵", "", title).strip()
                    if clean_title and "에러" not in clean_title:
                        hints.append(clean_title)
                
                page.close()
            except Exception:
                continue
        
        browser.close()
        
    # 중복 제거 및 깔끔하게 합치기
    return ", ".join(list(set(hints)))