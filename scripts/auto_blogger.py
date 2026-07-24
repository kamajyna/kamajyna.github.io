import os
import sys
import argparse
import datetime
import random
from google import genai
from google.genai import types

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import feedparser

def get_topic_by_category(category):
    if category == "auto":
        # 현재 시각(시 단위) 또는 확률에 따라 자동 선택
        # 짝수 시: tech, 홀수 시: dividend
        now_hour = datetime.datetime.now().hour
        category = "tech" if now_hour % 2 == 0 else "dividend"
        
    print(f"선택된 카테고리: {category.upper()}")

    if category == "tech":
        rss_urls = [
            "https://news.google.com/rss/search?q=AI+OR+%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5+OR+%ED%85%8C%ED%81%AC+when:1d&hl=ko&gl=KR&ceid=KR:ko",
            "https://feeds.feedburner.com/zdkorea"
        ]
        fallback_topics = [
            "직장인을 위한 구글 스프레드시트 업무 자동화 꿀팁",
            "생성형 AI 시대, ChatGPT를 업무에 200% 활용하는 비법",
            "노션(Notion) 템플릿으로 완벽한 개인 일정 관리 시스템 만들기",
            "개발자와 기획자를 위한 생성형 AI 프롬프트 엔지니어링 실전 가이드"
        ]
    else:  # dividend / finance
        rss_urls = [
            "https://news.google.com/rss/search?q=%EC%9B%94%EB%B0%B0%EB%8B%B9+OR+ETF+OR+%EB%B0%B0%EB%8B%B9%EC%A3%BC+when:2d&hl=ko&gl=KR&ceid=KR:ko",
            "https://news.google.com/rss/search?q=%EC%97%B0%EA%B8%88%EC%A0%80%EC%B6%95+OR+ISA%EA%B3%84%EC%A2%8C+when:2d&hl=ko&gl=KR&ceid=KR:ko"
        ]
        fallback_topics = [
            "SCHD vs JEPI: 미국 대표 월배당 ETF 장단점 및 수익률 비교 분석",
            "연금저축펀드 계좌에서 절세 효과 누리며 모아가는 월배당 ETF 포트폴리오",
            "월 50만원 현금흐름(배당금)을 만들기 위해 필요한 투자금과 추천 조합",
            "초보자를 위한 한국판 SCHD(SOL, ACE, KODEX 미국배당다우존스) 전격 비교",
            "ISA 계좌 배당주 투자 시 반드시 알아야 할 비과세 절세 혜택 총정리"
        ]

    articles = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # 피드당 상위 5개
                articles.append(entry.title)
        except Exception as e:
            print(f"RSS 파싱 에러 ({url}): {e}")

    if articles:
        topic = random.choice(articles)
        print(f"RSS에서 추출한 주제 [{category.upper()}]: {topic}")
        return category, topic
    else:
        topic = random.choice(fallback_topics)
        print(f"백업 목록에서 선택한 주제 [{category.upper()}]: {topic}")
        return category, topic

def generate_blog_post(category, topic):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    if category == "tech":
        prompt = f"""
당신은 IT/테크 및 생산성 향상 팁을 전문으로 다루는 최상위 파워 블로거입니다.
다음 주제 혹은 최신 뉴스 타겟에 대해 SEO에 완벽히 최적화된 블로그 포스트를 작성해주세요.

주제: {topic}

요구사항:
1. 매력적이고 클릭을 유도하는 제목을 작성할 것 (정보 가치 중심)
2. 서론(도입부 및 흥미 유발), 목차(TOC), 본론(3가지 이상의 상세 팁/분석/방법론), 결론(요약 및 인사이트), FAQ 구조로 작성할 것
3. 마크다운 형식으로 작성할 것 (제목은 #, 소제목은 ##, ### 사용)
4. 본문 내 강조할 부분은 굵은 글씨(**bold**)나 인용구(`>`)를 적극 활용하여 가독성을 높일 것
5. 본문 내 뉴스 보도나 인물 발언 등이 언급될 경우, 해당 보도/출처 기반임을 자연스럽게 밝히고 객관적 사실과 독자적인 분석을 바탕으로 작성할 것 (저작권 및 신뢰도 준수)
6. 포스트 최상단에 관련 썸네일 이미지를 Unsplash 소스에서 가져와 삽입할 것. 예: `![썸네일](https://source.unsplash.com/800x400/?tech,ai)` (주제에 맞는 영어 키워드 사용)
7. 본문 마지막에는 작성한 내용(주제)과 가장 연관성 높은 특정 IT 기기나 생산성 도구, 관련 서적을 추천하는 문단(HTML `<div class="partners-box">`)을 작성할 것. 
   - 링크는 쿠팡 검색 결과 링크 포맷인 `https://link.coupang.com/a/search?q=[추천_상품_키워드]` 형식을 활용하여, 실제 검색어로 연결되도록 만들 것. (예: `q=맥북프로M3`)
   - 버튼 스타일 태그(`<a href="..." class="partners-btn" target="_blank">관련 상품 최저가 확인하기</a>`)를 사용할 것.
8. 추천 박스 바로 아래에 `<p class="partners-notice">*(이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.)*</p>` 문구를 반드시 포함할 것.
9. 응답은 Frontmatter (layout, title, date, categories, tags)를 포함한 완벽한 Jekyll markdown 파일 내용이어야 합니다.
10. 마크다운 코드블록(```markdown)으로 감싸지 말고 순수 텍스트만 출력하세요.

Frontmatter 예시:
---
layout: post
title: "생성된 매력적인 제목"
date: YYYY-MM-DD HH:MM:SS +0900
categories: [Tech, Trend]
tags: [AI, 기술, 트렌드]
---

내용...
"""
    else:  # dividend / finance
        prompt = f"""
당신은 현금흐름 기반 금융/주식/월배당 ETF 및 절세 재테크를 전문으로 다루는 수석 수량분석가이자 파워 블로거입니다.
다음 월배당/재테크 주제에 대해 SEO에 완벽히 최적화된 블로그 포스트를 작성해주세요.

주제: {topic}

요구사항:
1. 배당 투자자 및 재테크 관심층의 클릭을 유도하는 직관적이고 가치 있는 제목을 작성할 것
2. 서론(투자 포인트 및 현금흐름 중요성), 목차(TOC), 본론(상세 스펙/배당수익률/절세 혜택/비교 표), 결론(투자의견 및 리스크 관리), FAQ 구조로 작성할 것
3. 본론에는 수치 데이터를 한눈에 볼 수 있는 마크다운 비교 표(Markdown Table)를 반드시 1개 이상 포함할 것
4. 마크다운 형식으로 작성할 것 (제목은 #, 소제목은 ##, ### 사용)
5. 본문 내 강조할 부분은 굵은 글씨(**bold**)나 인용구(`>`)를 적극 활용할 것
6. 본문 내 뉴스 보도나 시장 지표가 언급될 경우 출처 및 객관적 데이터 기반임을 밝히고 객관적인 정보 제공에 집중할 것 (신뢰도 준수)
7. 포스트 최상단에 관련 썸네일 이미지를 Unsplash 소스에서 가져와 삽입할 것. 예: `![썸네일](https://source.unsplash.com/800x400/?finance,investment)`
8. 본문 최하단에는 반드시 다음 **투자 면책 조항(Disclaimer)** 문구를 포함할 것:
   `<div class="disclaimer-box"><p>*(본 포스팅은 단순 정보 제공을 목적으로 작성되었으며, 특정 종목이나 상품에 대한 투자 권유가 아닙니다. 모든 투자의 판단과 책임은 투자자 본인에게 있습니다.)*</p></div>`
9. 응답은 Frontmatter (layout, title, date, categories, tags)를 포함한 완벽한 Jekyll markdown 파일 내용이어야 합니다.
10. 마크다운 코드블록(```markdown)으로 감싸지 말고 순수 텍스트만 출력하세요.

Frontmatter 예시:
---
layout: post
title: "생성된 매력적인 제목"
date: YYYY-MM-DD HH:MM:SS +0900
categories: [Dividend, Finance]
tags: [월배당, ETF, 재테크, 주식]
---

내용...
"""

    models_to_try = ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-2.0-flash']
    last_err = None
    for model_name in models_to_try:
        try:
            print(f"Generating content with model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Model {model_name} failed ({e}), trying fallback...")
            last_err = e
    raise last_err

def save_post(content, category):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_dir = os.path.join(base_dir, "_posts")
    os.makedirs(posts_dir, exist_ok=True)

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    slug = f"auto-post-{category}-{now.strftime('%H%M%S')}"
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(posts_dir, filename)

    if content.startswith("```markdown"):
        content = content[11:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

    print(f"새 포스트가 생성되었습니다 [{category.upper()}]: {filepath}")
    return filepath

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Blogger CLI")
    parser.add_argument(
        "--category", 
        choices=["tech", "dividend", "auto"], 
        default="auto", 
        help="Category choice (tech, dividend, or auto alternating)"
    )
    args = parser.parse_args()

    try:
        print("1. 카테고리 및 주제 선정 중...")
        category, topic = get_topic_by_category(args.category)
        print(f"최종 결정된 주제: {topic}")

        print("2. 블로그 포스트 생성 중... (Gemini API 호출)")
        post_content = generate_blog_post(category, topic)

        print("3. 포스트 저장 중...")
        save_post(post_content, category)

        print("작업 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)
