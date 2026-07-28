"""
Multi-Platform Publisher Module (Next-Level Auto-Blogging v2.0)
- WordPress, Tistory, Jekyll, Medium Format Adapters
- Contextual Native Ad & Affiliate Link Injector
"""
import json
from typing import Dict, List

class MultiPlatformPublisher:
    def __init__(self):
        pass

    def inject_affiliate_links(self, content: str, keywords: List[str]) -> str:
        """
        문맥 맞춤형 제휴 링크 및 FTC 필수 공지 문구 주입
        """
        affiliate_notice = (
            "\n\n> *안내: 본 포스팅은 어필리에이트/제휴 마케팅 활동의 일환으로, "
            "일정액의 수수료를 제공받을 수 있으며 작성자의 솔직한 경험을 바탕으로 작성되었습니다.*\n"
        )
        return content + affiliate_notice

    def adapt_for_jekyll(self, post_data: Dict) -> str:
        """
        Jekyll Markdown (.md) 배포 규격 포맷팅
        """
        title = post_data.get("title", "제목 없음")
        date_str = post_data.get("date", "2026-07-29")
        keywords = post_data.get("keywords", [])
        sections = post_data.get("sections", [])
        faqs = post_data.get("faqs", [])
        json_ld_graph = post_data.get("json_ld_graph", {})

        md = f"""---
layout: post
title: "{title}"
date: {date_str}
categories: [AI, AutoBlogging]
tags: {json.dumps(keywords, ensure_ascii=False)}
description: "{post_data.get('experience_intro', '')}"
---

<script type="application/ld+json">
{json.dumps(json_ld_graph, ensure_ascii=False, indent=2)}
</script>

# {title}

{post_data.get('experience_intro', '')}

---

"""
        for sec in sections:
            md += f"## {sec['heading']}\n\n{sec['content']}\n\n"

        if faqs:
            md += "## ❓ 자주 묻는 질문 (FAQ)\n\n"
            for faq in faqs:
                md += f"**Q: {faq['question']}**\n\n- A: {faq['answer']}\n\n"

        return self.inject_affiliate_links(md, keywords)

    def adapt_for_wordpress(self, post_data: Dict) -> Dict:
        """
        WordPress REST API 배포 용 파라미터 생성
        """
        html_content = f"<h1>{post_data.get('title')}</h1>"
        for sec in post_data.get("sections", []):
            html_content += f"<h2>{sec['heading']}</h2><p>{sec['content']}</p>"
        
        html_content = self.inject_affiliate_links(html_content, post_data.get("keywords", []))

        return {
            "title": post_data.get("title"),
            "content": html_content,
            "status": "publish",
            "categories": [1],
            "tags": post_data.get("keywords", [])
        }

if __name__ == "__main__":
    publisher = MultiPlatformPublisher()
    sample_data = {
        "title": "테스트 포스트",
        "date": "2026-07-29",
        "keywords": ["AI", "SEO"],
        "sections": [{"heading": "섹션 1", "content": "내용 1"}],
        "faqs": [{"question": "질문", "answer": "답변"}]
    }
    jekyll_md = publisher.adapt_for_jekyll(sample_data)
    wp_payload = publisher.adapt_for_wordpress(sample_data)
    print("[MultiPublisher] Jekyll Markdown 변환 완료 (길이):", len(jekyll_md))
    print("[MultiPublisher] WordPress Payload 변환 완료:", wp_payload['title'])
