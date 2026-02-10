import os
from utils.logging_utils import log

# ✅ 팀장님 지시: 환율 1,450원 고정
USD_TO_KRW_RATE = 1450.0

def calculate_gemini_cost_krw(input_tokens: int, output_tokens: int):
    """
    Gemini 2.5 Pro (Thinking) 모델 전용 단가 및 1,450원 환율 적용
    """
    # 팀장님 제공 최신 단가: Input $1.25 / Output $5.00 (per 1M tokens)
    input_unit_price_usd = 1.25 
    output_unit_price_usd = 5.00
    
    # 달러 비용 계산
    input_cost_usd = (input_tokens / 1000000) * input_unit_price_usd
    output_cost_usd = (output_tokens / 1000000) * output_unit_price_usd
    
    # 원화 변환 (1,450원)
    total_krw = (input_cost_usd + output_cost_usd) * USD_TO_KRW_RATE
    
    return round(total_krw, 0)

def report_usage(total_input: int, total_output: int):
    """
    실제 파이프라인에서 호출하여 터미널에 영수증을 찍어주는 함수
    """
    krw_total = calculate_gemini_cost_krw(total_input, total_output)
    
    log("billing", "============================================================")
    log("billing", f"💰 Gemini 2.5 Pro (Thinking) 영수증 (환율: {USD_TO_KRW_RATE}원)")
    log("billing", f"📈 총 입력(Input) 토큰: {total_input:,}")
    log("billing", f"📉 총 출력(Output) 토큰: {total_output:,}")
    log("billing", f"💵 이번 분석 비용: 약 {krw_total:,}원")
    log("billing", "============================================================")
    
    return krw_total