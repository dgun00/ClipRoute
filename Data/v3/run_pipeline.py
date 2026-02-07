import argparse

from pipeline.step0_collect_videos import run as step0
from pipeline.step1_collect_materials import run as step1
from pipeline.step2_build_itinerary_llm import run as step2
from pipeline.step3_naver_enrich import run as step3
from pipeline.step4_sort_timeline import run as step4
from pipeline.step5_map_debug import run as step5


def main():
    parser = argparse.ArgumentParser("ClipRoute Pipeline")
    parser.add_argument("--keyword")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--skip-llm", action="store_true")
    args = parser.parse_args()

    keyword = args.keyword or input("YouTube 검색 키워드를 입력하세요: ").strip()

    step0(keyword=keyword, max_results=args.max_results)
    step1()
    step2(skip_llm=args.skip_llm)  # ✅ 이제 step2가 이 인자를 받습니다
    step3()
    step4()
    step5()


if __name__ == "__main__":
    main()