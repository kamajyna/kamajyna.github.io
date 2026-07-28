"""
Next-Level Auto Blogging Engine v2.0 Main Orchestrator
Integrates all 20 Next-Level Strategies into an FSM Pipeline.
"""
import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List

# Add modules directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.trend_arbitrage import TrendArbitrageEngine
from modules.eeat_content_generator import EEATContentGenerator
from modules.technical_seo_indexer import TechnicalSEOIndexer
from modules.multi_publisher import MultiPlatformPublisher
from modules.anti_ai_naturalizer import AntiAINaturalizer

class AutoBloggingEngineV2:
    def __init__(self, project_dir: str = None):
        if project_dir is None:
            project_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = project_dir
        self.posts_dir = os.path.join(project_dir, "_posts")
        os.makedirs(self.posts_dir, exist_ok=True)

        # Initialize sub-modules
        self.trend_engine = TrendArbitrageEngine()
        self.eeat_generator = EEATContentGenerator()
        self.seo_indexer = TechnicalSEOIndexer()
        self.publisher = MultiPlatformPublisher()
        self.naturalizer = AntiAINaturalizer()

    def run_next_level_pipeline(self, topic: str, keywords: List[str]) -> Dict:
        """
        [FSM 파이프라인] 20가지 넥스트레벨 통합 자동 발행 파이프라인 실행
        """
        print(f"🚀 [STAGE 1/5] 트렌드 차익 & 검색 의도 분석: {topic}")
        trend_res = self.trend_engine.analyze_trend_gap(topic, keywords)
        
        print(f"✍️ [STAGE 2/5] E-E-A-T 기반 본문 작성 & 시맨틱 JSON-LD 지식 그래프 생성")
        eeat_res = self.eeat_generator.generate_eeat_post(
            topic=topic,
            keywords=trend_res["keywords"],
            gaps=trend_res["missing_gaps"]
        )

        print(f"🛡️ [STAGE 3/5] Anti-AI 자연화 & Zero-Trust 저작권/PII 가드레일 정적 검사")
        safe_pass, audit_msg = self.naturalizer.audit_governance_safety(json.dumps(eeat_res, ensure_ascii=False))
        if not safe_pass:
            raise ValueError(f"안전 가드레일 위반: {audit_msg}")
        
        # 문체 자연화 적용
        for sec in eeat_res["sections"]:
            sec["content"] = self.naturalizer.naturalize_text(sec["content"])

        print(f"📦 [STAGE 4/5] 멀티플랫폼 배포 변환 (Jekyll / WordPress REST API)")
        post_payload = {
            "title": eeat_res["title"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "keywords": trend_res["keywords"],
            "experience_intro": eeat_res["experience_intro"],
            "sections": eeat_res["sections"],
            "faqs": eeat_res["faqs"],
            "json_ld_graph": eeat_res["json_ld_graph"]
        }
        jekyll_md = self.publisher.adapt_for_jekyll(post_payload)
        wp_payload = self.publisher.adapt_for_wordpress(post_payload)

        # _posts 디렉토리에 마크다운 파일 저장
        slug = re.sub(r'[^a-zA-Z0-9가-힣]+', '-', topic).strip('-').lower()
        if not slug:
            slug = "next-level-auto-post"
        
        filename = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}.md"
        filepath = os.path.join(self.posts_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(jekyll_md)

        print(f"⚡ [STAGE 5/5] Core Web Vitals 최적화 & Instant Indexing API 호출")
        opt_html = self.seo_indexer.optimize_html_assets(wp_payload["content"])
        indexing_res = self.seo_indexer.push_instant_indexing(f"https://blog.example.com/posts/{slug}")

        print(f"🎉 [SUCCESS] 20가지 넥스트레벨 오토블로그 파이프라인 완수!")

        return {
            "status": "SUCCESS",
            "topic": topic,
            "filename": filename,
            "filepath": filepath,
            "trending_score": trend_res["trending_score"],
            "red_team_score": eeat_res["red_team_score"],
            "indexing_status": indexing_res["status"],
            "wordpress_payload_preview": {
                "title": wp_payload["title"],
                "content_length": len(opt_html)
            }
        }

if __name__ == "__main__":
    engine = AutoBloggingEngineV2()
    result = engine.run_next_level_pipeline(
        topic="2026 차세대 AI 오토블로그 넥스트 레벨 구축",
        keywords=["오토블로그", "SEO최적화", "EEAT", "인스턴트색인"]
    )
    print("\n[최종 파이프라인 실행 결과 리포트]")
    print(json.dumps(result, ensure_ascii=False, indent=2))
