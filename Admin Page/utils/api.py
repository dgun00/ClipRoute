import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Mock 데이터 (추후 실제 API로 교체)
MOCK_DATA = [
    {"id": 1, "name": "테스트 항목 1", "category": "카테고리 A", "status": "활성", "created_at": "2024-02-01"},
    {"id": 2, "name": "테스트 항목 2", "category": "카테고리 B", "status": "비활성", "created_at": "2024-02-02"},
    {"id": 3, "name": "테스트 항목 3", "category": "카테고리 A", "status": "활성", "created_at": "2024-02-03"},
    {"id": 4, "name": "테스트 항목 4", "category": "카테고리 C", "status": "대기", "created_at": "2024-02-04"},
    {"id": 5, "name": "테스트 항목 5", "category": "카테고리 B", "status": "활성", "created_at": "2024-02-05"},
]

def fetch_all_data() -> List[Dict]:
    """모든 데이터 가져오기 (추후 API 연동)"""
    return MOCK_DATA.copy()

def fetch_data_by_id(data_id: int) -> Optional[Dict]:
    """ID로 데이터 조회"""
    for item in MOCK_DATA:
        if item['id'] == data_id:
            return item.copy()
    return None

def create_data(data: Dict) -> bool:
    """새 데이터 생성 (추후 API 연동)"""
    # 실제로는 API POST 요청
    new_id = max([item['id'] for item in MOCK_DATA]) + 1
    data['id'] = new_id
    MOCK_DATA.append(data)
    return True

def update_data(data_id: int, updated_data: Dict) -> bool:
    """데이터 업데이트 (추후 API 연동)"""
    # 실제로는 API PUT 요청
    for i, item in enumerate(MOCK_DATA):
        if item['id'] == data_id:
            MOCK_DATA[i] = {**item, **updated_data}
            return True
    return False

def delete_data(data_id: int) -> bool:
    """데이터 삭제 (추후 API 연동)"""
    # 실제로는 API DELETE 요청
    global MOCK_DATA
    MOCK_DATA = [item for item in MOCK_DATA if item['id'] != data_id]
    return True

# 추후 실제 API 연동 시 사용할 함수들
def get_api_base_url() -> str:
    """API 베이스 URL 가져오기"""
    return os.getenv('API_BASE_URL', 'http://localhost:8000')

def get_api_headers() -> Dict[str, str]:
    """API 요청 헤더 생성"""
    api_key = os.getenv('API_KEY', '')
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
