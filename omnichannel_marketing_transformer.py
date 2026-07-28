"""
Omnichannel Marketing Content Transformer
Transforms single blog post payloads into tailored multi-channel marketing content for Instagram, X (Twitter), Threads, and Blogs.
"""
import json

class OmnichannelMarketingTransformer:
    def __init__(self):
        pass

    def transform(self, post_data: dict) -> dict:
        """
        Transforms blog post payload into 4-channel social media posts.
        """
        title = post_data.get("title", "")
        keywords = post_data.get("keywords", [])
        sections = post_data.get("sections", [])
        
        hashtag_str = " ".join([f"#{kw.replace(' ', '_')}" for kw in keywords]) + " #마케팅자동화 #AI뉴스"

        # 1. Instagram Carousel Script & Caption
        insta_slides = [
            f"📌 [슬라이드 1]\n{title}\n\n👉 2026 차세대 가이드 한눈에 보기",
        ]
        for idx, sec in enumerate(sections, 2):
            heading = sec.get("heading", "")
            content = sec.get("content", "")[:80]
            insta_slides.append(f"📌 [슬라이드 {idx}]\n{heading}\n\n{content}...")
        insta_slides.append("📌 [마지막 슬라이드]\n도움이 되셨다면 ❤️ 좋아요 & 💾 저장으로 나중에 다시 보세요!")

        insta_caption = (
            f"{title}\n\n"
            f"💡 블로그 핵심 내용 요약:\n"
            f"{post_data.get('meta_description')}\n\n"
            f"프로필 링크에서 전문을 확인하실 수 있습니다!\n\n"
            f"{hashtag_str}"
        )

        # 2. X (Twitter) 280-char Thread Set
        x_threads = [
            f"1/4 🧵 {title}\n\n{post_data.get('meta_description')}\n\n#AI {hashtag_str[:30]}",
            f"2/4 💡 {sections[0]['heading'] if sections else ''}\n\n{sections[0]['content'][:120] if sections else ''}...",
            f"3/4 🚀 {sections[1]['heading'] if len(sections)>1 else ''}\n\n{sections[1]['content'][:120] if len(sections)>1 else ''}...",
            f"4/4 🔗 실전 가이드 전문 읽기:\nhttps://blog.apollon-ai.lab/post/{post_data.get('slug')}"
        ]

        # 3. Threads Casual Storytelling Post
        threads_post = (
            f"🔥 {title}\n\n"
            f"요즘 {keywords[0] if keywords else '이 주제'} 관련 문의가 부쩍 늘었네요!\n\n"
            f"핵심은 'E-E-A-T 검증'과 '자가 고도화 루프'입니다. 단순히 글을 찍어내는 것보다 사용자 경험과 권위성을 챙기는 게 가장 핵심이에요.\n\n"
            f"궁금한 점이 있다면 댓글로 남겨주세요! 💬"
        )

        return {
            "title": title,
            "slug": post_data.get("slug"),
            "channels": {
                "instagram": {
                    "slides": insta_slides,
                    "caption": insta_caption
                },
                "x_twitter": {
                    "threads": x_threads
                },
                "threads": {
                    "post": threads_post
                },
                "blog": {
                    "filepath": post_data.get("filepath"),
                    "json_ld": post_data.get("json_ld")
                }
            }
        }
