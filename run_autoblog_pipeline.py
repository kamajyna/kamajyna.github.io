"""
Run Next-Level Auto Blogging & Omnichannel Pipeline v2.0
End-to-end execution script for automated blogging and multi-channel content publishing.
"""
import os
import sys
import json

module_dir = os.path.dirname(os.path.abspath(__file__))
if module_dir not in sys.path:
    sys.path.insert(0, module_dir)

from auto_blogging_engine_v2 import AutoBloggingEngineV2
from omnichannel_marketing_transformer import OmnichannelMarketingTransformer

def run_pipeline(topic: str, keywords: list):
    print(f"=== [오토블로그 v2.0 넥스트 레벨 파이프라인] 주제: '{topic}' 생성 시작 ===")
    
    # 1. 20가지 넥스트레벨 통합 SEO 블로그 본문 및 지식 그래프 생성
    blog_engine = AutoBloggingEngineV2(project_dir=module_dir)
    post_data = blog_engine.run_next_level_pipeline(topic=topic, keywords=keywords)
    print(f"✅ [SEO v2.0 블로그 생성 완료] 파일: {post_data['filepath']}")

    # 2. 멀티채널 마케팅 콘텐츠 트랜스포밍 (인스타그램, X, 스레드 포맷팅)
    transformer = OmnichannelMarketingTransformer()
    # omnichannel 변환용 구조 매핑
    legacy_structure = {
        "title": post_data["topic"],
        "slug": os.path.basename(post_data["filepath"]).replace(".md", ""),
        "filepath": post_data["filepath"],
        "sections": [{"heading": f"핵심 분석 ({post_data['topic']})", "content": f"트렌딩 스코어 {post_data['trending_score']}점 달성"}]
    }
    omni_payload = transformer.transform(legacy_structure)
    print("✅ [멀티채널 변환 완료] 인스타그램 / X(트위터) / 스레드 원고 추출 완료")

    # 3. 배포용 JSON 페이로드 저장
    output_json_path = os.path.join(module_dir, f"autoblog_v2_payload_{legacy_structure['slug']}.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(omni_payload, f, indent=4, ensure_ascii=False)

    print(f"🎉 [v2.0 파이프라인 성공] 배포 페이로드 저장 완료 -> {output_json_path}\n")
    return output_json_path, omni_payload

if __name__ == "__main__":
    run_pipeline(
        topic="2026 차세대 AI 에이전트 오토 블로깅 넥스트 레벨 실전 구축 가이드",
        keywords=["오토블로그", "멀티채널마케팅", "AI에이전트", "EEAT_SEO", "인스턴트색인"]
    )

