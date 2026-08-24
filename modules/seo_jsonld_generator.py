import json
from typing import Dict, Any, List, Optional

class SEOJsonLDGenerator:
    """
    Google 및 Naver 검색엔진 최적화를 위한 Schema.org JSON-LD 구조화 데이터 생성 모듈
    """

    def __init__(self, site_name: str = "AutoBlog Pro", site_url: str = "https://my-autoblog.github.io"):
        self.site_name = site_name
        self.site_url = site_url.rstrip("/")

    def generate_article_schema(
        self,
        title: str,
        description: str,
        post_url: str,
        date_published: str,
        author_name: str = "AutoBlogger AI",
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Article 스키마 생성"""
        full_url = f"{self.site_url}/{post_url.lstrip('/')}"
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": description,
            "url": full_url,
            "datePublished": date_published,
            "dateModified": date_published,
            "author": {
                "@type": "Organization",
                "name": author_name,
                "url": self.site_url
            },
            "publisher": {
                "@type": "Organization",
                "name": self.site_name,
                "url": self.site_url
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": full_url
            }
        }
        if image_url:
            schema["image"] = image_url
        return schema

    def generate_faq_schema(self, faq_items: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """
        FAQPage 스키마 생성
        faq_items format: [{"question": "Q...", "answer": "A..."}]
        """
        if not faq_items:
            return None

        main_entities = []
        for item in faq_items:
            q = item.get("question")
            a = item.get("answer")
            if q and a:
                main_entities.append({
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a
                    }
                })

        if not main_entities:
            return None

        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entities
        }

    def generate_breadcrumb_schema(self, items: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        BreadcrumbList 스키마 생성
        items format: [{"name": "Home", "url": "/"}, {"name": "Category", "url": "/category"}]
        """
        item_list = []
        for idx, item in enumerate(items, 1):
            url = item.get("url", "")
            full_item_url = url if url.startswith("http") else f"{self.site_url}/{url.lstrip('/')}"
            item_list.append({
                "@type": "ListItem",
                "position": idx,
                "name": item.get("name", ""),
                "item": full_item_url
            })

        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": item_list
        }

    def to_html_script_tag(self, schema_data: Dict[str, Any]) -> str:
        """JSON-LD를 HTML <script type="application/ld+json"> 태그로 변환"""
        return f'<script type="application/ld+json">\n{json.dumps(schema_data, ensure_ascii=False, indent=2)}\n</script>'

if __name__ == "__main__":
    generator = SEOJsonLDGenerator()
    article = generator.generate_article_schema(
        title="2026 차세대 AI 에이전트 구축 가이드",
        description="AI 에이전트와 오토블로깅 파이프라인의 실전 구축 노하우",
        post_url="posts/2026-ai-agent-guide",
        date_published="2026-08-12T10:00:00+09:00"
    )
    print(generator.to_html_script_tag(article))
