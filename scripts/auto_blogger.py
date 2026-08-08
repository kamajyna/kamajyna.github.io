import os
import sys
import argparse
import datetime
import random
from datetime import timezone, timedelta

KST = timezone(timedelta(hours=9))
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
        now_hour = datetime.datetime.now(KST).hour
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

        import re
        noise_pattern = re.compile(
            r'(?:\[부음\]|\[부고\]|\[인사\]|\[동정\]|조모상|빙부상|빙모상|시모상|조부상|부고소식|'
            r'(?:^|[\s\(\[\-])(?:부음|부고|인사|동정|사망)(?:$|[\s\)\]\-]|\b))', 
            re.IGNORECASE
        )

        articles = []
        for url in rss_urls:
            try:
                feed = feedparser.parse(url)
                if getattr(feed, 'bozo', 0) and not feed.entries:
                    print(f"RSS 피드 오류 ({url})")
                    continue
                for entry in feed.entries[:10]:
                    title = getattr(entry, 'title', '').strip()
                    if not title:
                        continue
                    # 노이지/부적절 키워드 정밀 제외 (인사이트 등 오탐 방지)
                    if noise_pattern.search(title):
                        print(f"제외된 노이즈 기사: {title}")
                        continue
                    articles.append(title)
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

    else:  # dividend / finance
        dividend_stocks = [
            # 초우량 안정형 배당주
            "코카콜라 (KO)", "리얼티 인컴 (O)", "존슨앤존슨 (JNJ)", "애플 (AAPL)", 
            "마이크로소프트 (MSFT)", "스타벅스 (SBUX)", "맥도날드 (MCD)", "프록터앤갬블 (PG)", 
            "엑슨모빌 (XOM)", "셰브론 (CVX)", "애비브 (ABBV)", "화이자 (PFE)", 
            "홈디포 (HD)", "록히드마틴 (LMT)", "텍사스 인스트루먼트 (TXN)", "코스트코 (COST)",
            "제이피모건체이스 (JPM)", "뱅크오브아메리카 (BAC)",
            
            # 고배당 / 리츠 / BDC / 통신 / 담배 (리스크 포함 종목)
            "AT&T (T)", "버라이즌 (VZ)", "알트리아 (MO)", "브리티시 아메리칸 토바코 (BTI)",
            "아레스 캐피탈 (ARCC)", "메인 스트리트 캐피탈 (MAIN)", "프로스펙트 캐피탈 (PSEC)",
            "에이전시 인베스트먼트 (AGNC)", "아머 레지덴셜 리츠 (ARR)", "스타우드 프로퍼티 (STWD)",
            "오메가 헬스케어 (OHI)", "메디컬 프로퍼티즈 트러스트 (MPW)", "W.P. 캐리 (WPC)",
            "엔터프라이즈 프로덕츠 파트너스 (EPD)",
            
            # 고배당 / 커버드콜 / ETF
            "슈와브 US 디비던드 에퀴티 (SCHD)", "JP모건 에퀴티 프리미엄 인컴 (JEPI)",
            "JP모건 나스닥 에퀴티 프리미엄 (JEPQ)", "Global X 나스닥 100 커버드콜 (QYLD)",
            "Global X 슈퍼디비던드 (SDIV)", "일드맥스 TSLA 옵션 인컴 (TSLY)"
        ]
        stock = random.choice(dividend_stocks)
        topic = f"{stock} 배당 및 재무 분석 팩트시트"
        print(f"랜덤 선정된 배당주 [{category.upper()}]: {topic}")
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
2. 서론(도입부 및 흥미 유발), 본론(3가지 이상의 상세 팁/분석/방법론), 결론(요약 및 인사이트), FAQ 구조로 작성할 것 (TOC는 직접 작성하지 말고 반드시 3번 규칙을 따를 것)
3. 목차(TOC)는 마크다운 파서가 자동 생성하도록 본문 맨 앞에 딱 한 번 아래 내용을 그대로 입력할 것:
   * TOC
   {{:toc}}
4. 마크다운 형식으로 작성할 것 (제목은 #, 소제목은 ##, ### 사용)
5. 본문 내 강조할 부분은 굵은 글씨(**bold**)나 인용구(`>`)를 적극 활용하여 가독성을 높일 것
6. 본문 내 뉴스 보도나 인물 발언 등이 언급될 경우, 해당 보도/출처 기반임을 자연스럽게 밝히고 객관적 사실과 독자적인 분석을 바탕으로 작성할 것 (저작권 및 신뢰도 준수)
7. Frontmatter에 대표 썸네일 이미지 URL을 다음 형식으로 작성할 것: `image: "https://picsum.photos/seed/[핵심_영어_키워드]/800/450"`. 여기서 '[핵심_영어_키워드]'는 본 포스트 주제를 나타내는 2~3개의 영어 단어(예: artificial_intelligence, server_room 등)를 쉼표나 언더스코어로 연결해서 넣어주세요. 절대 본문(내용) 안에는 이미지를 마크다운 문법으로 중복 삽입하지 마세요.
8. 본문 마지막에는 작성한 내용(주제)과 가장 연관성 높은 특정 IT 기기나 생산성 도구, 관련 서적을 추천하는 문단(HTML `<div class="partners-box">`)을 작성할 것. (내부 제목은 `<h3>`, 설명은 `<p>` 태그를 사용하고, 인라인 스타일이나 `<style>` 태그는 절대 추가하지 말 것)
   - 링크는 쿠팡 검색 결과 링크 포맷인 `https://www.coupang.com/np/search?q=[추천_상품_키워드]` 형식을 활용하여, 실제 검색어로 연결되도록 만들 것. (예: `q=맥북프로M3`)
   - 버튼 스타일 태그(`<a href="..." class="partners-btn" target="_blank">관련 상품 최저가 확인하기</a>`)를 사용할 것.
9. 추천 박스 바로 아래에 `<p class="partners-notice">*(이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.)*</p>` 문구를 반드시 포함할 것.
10. 응답은 Frontmatter (layout, title, date, categories, tags, image)를 포함한 완벽한 Jekyll markdown 파일 내용이어야 합니다.
11. 마크다운 코드블록(```markdown)으로 감싸지 말고 순수 텍스트만 출력하세요.

Frontmatter 예시:
---
layout: post
title: "생성된 매력적인 제목"
date: {datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: [Tech, Trend]
tags: [AI, 기술, 트렌드]
image: "https://picsum.photos/seed/artificial_intelligence_future/800/450"
---

내용...
"""
    else:  # dividend / finance
        prompt = f"""
당신은 현금흐름 기반 금융/배당주를 전문으로 분석하는 월스트리트 수석 수량분석가(Quant)이자 파워 블로거입니다.
아래 종목에 대한 최신 배당 및 재무 데이터를 기반으로 **'배당주 객관적 분석 팩트시트(Factsheet)'**를 작성해주세요.

종목/주제: {topic}

요구사항:
1. 검색엔진(SEO)에 최적화되고 투자자들의 클릭을 유도하는 직관적인 제목을 작성할 것 (예: "[종목명] 배당률 N%, 연 N회 지급! 2026년 배당 팩트시트")
2. 목차(TOC)는 마크다운 파서가 자동 생성하도록 본문 맨 앞에 딱 한 번 아래 내용을 그대로 입력할 것 (직접 목차 리스트를 작성하지 마세요):
   * TOC
   {{:toc}}
3. 다음의 5가지 섹션을 필수적으로 작성할 것:
   - 🏢 **기업 개요 및 비즈니스 모델**: 어떤 돈으로 배당을 주는지 간략한 소개 (BDC, 모기지 리츠, 커버드콜 등 특수 구조일 경우 원리 설명)
   - 💰 **핵심 배당 팩트**: 현재 시가배당률(%), 1년에 배당 몇 번 주는지(월배당/분기배당/반기 등), 주요 배당 지급월, 연속 배당성장 연수 등 팩트 위주 나열
   - 📊 **재무 건전성 및 리스크(Risk)**: 안정적으로 배당을 줄 수 있는 재무상태인지 팩트 기반 기술. 특히 고배당주(모기지 리츠, BDC, 초고배당 ETF 등)의 경우 배당 삭감 이력, 순자산(NAV) 침식 우려, 부채 비율, 배당성향(Payout Ratio) 과다 등의 **부정적/위험 요소를 객관적으로 반드시 포함**할 것.
   - 🎯 **월가 애널리스트 및 전문가 총평**: 투자은행, 분석가들의 목표가 컨센서스 및 최근 전망 요약
   - 📋 **한눈에 보는 핵심 요약 표**: 주요 수치(티커, 배당률, 배당성장연수, 리스크 레벨, 목표가 등)를 마크다운 표(Table)로 정리
4. 억측이나 주관적 감정을 배제하고 **숫자와 팩트** 위주로 전문성 있게 작성할 것. (수익률이 높든 위험하든 냉정하게 팩트만 전달)
5. 마크다운 형식으로 작성할 것 (제목은 #, 소제목은 ##, ### 사용). 본문 내 중요 팩트는 **bold** 처리하여 가독성을 높일 것.
6. Frontmatter에 대표 썸네일 이미지 URL을 다음 형식으로 작성할 것: `image: "https://picsum.photos/seed/[해당종목_관련_영어_키워드]/800/450"`. 여기서 '[해당종목_관련_영어_키워드]'는 해당 기업의 실제 비즈니스 모델이나 주요 제품을 잘 보여주는 구체적인 영어 단어 2~3개(예: Coca_Cola_beverage, Real_estate_skyscraper, Apple_device_modern 등)를 언더스코어로 연결해서 사용하세요. 단순한 'stock_chart'와 같은 키워드는 피하여 썸네일들이 서로 비슷해 보이지 않게 하세요. 절대 본문(내용) 안에는 이미지를 마크다운 문법으로 중복 삽입하지 마세요.
7. 본문 최하단에는 반드시 다음 **투자 면책 조항(Disclaimer)** 문구를 포함할 것:
   `<div class="disclaimer-box"><p><em>(본 포스팅은 단순 정보 제공을 목적으로 작성되었으며, 특정 종목이나 상품에 대한 투자 권유가 아닙니다. 모든 투자의 판단과 책임은 투자자 본인에게 있습니다.)</em></p></div>`
8. 응답은 Frontmatter (layout, title, date, categories, tags, image)를 포함한 완벽한 Jekyll markdown 파일 내용이어야 합니다. 마크다운 코드블록(```markdown)으로 감싸지 말고 순수 텍스트만 출력하세요.

Frontmatter 예시:
---
layout: post
title: "생성된 매력적인 팩트시트 제목"
date: {datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: [Dividend, Finance]
tags: [배당주, 미국주식, 팩트시트, 재테크]
image: "https://picsum.photos/seed/Apple_device_modern_design/800/450"
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
            text = (getattr(response, "text", None) or "").strip()
            if len(text) < 300:
                print(f"Model {model_name} output too short ({len(text)} chars), trying fallback...")
                continue
            return text
        except Exception as e:
            print(f"Model {model_name} failed ({e}), trying fallback...")
            last_err = e
    raise last_err or RuntimeError("All models failed to generate content")

def save_post(content, category):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_dir = os.path.join(base_dir, "_posts")
    os.makedirs(posts_dir, exist_ok=True)

    now = datetime.datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")

    slug = f"auto-post-{category}-{now.strftime('%H%M%S')}"
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(posts_dir, filename)

    import re
    content = content.strip()
    content = re.sub(r'^```[a-zA-Z]*[ \t]*\n?', '', content)
    if content.endswith("```"):
        content = content[:-3].strip()

    # Front Matter 보정 및 닫는 --- 검증
    parts = content.split("---")
    if len(parts) >= 3 and not parts[0].strip():
        # 정상적으로 --- 로 시작하고 닫는 --- 가 존재하는 구조
        fm_text = parts[1].strip()
        body_text = "---".join(parts[2:]).lstrip("\n")
    else:
        # Front Matter 경계가 파손된 경우 보정
        fm_text = f"layout: post\ntitle: \"Auto Post\"\ncategories: [{category.capitalize()}]"
        body_text = content

    # Front Matter 각 라인의 선행 공백 제거
    fm_text = "\n".join(line.strip() for line in fm_text.splitlines() if line.strip())

    # Front Matter 내부 키-값 짝에 줄바꿈 보장 (값 내부 미분할 보장)
    fm_keys = ["layout:", "title:", "date:", "categories:", "tags:", "image:"]
    for key in fm_keys:
        fm_text = re.sub(r'([^\n])[ \t]+(' + re.escape(key) + r')', r'\1\n\2', fm_text)
    
    # LLM이 임의로 생성한 date 필드를 현재 KST 시간으로 강제 덮어쓰기 (행단위 정밀 매칭)
    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S') + " +0900"
    fm_text, n = re.subn(r'^[ \t]*date:[^\n]*$', f"date: {current_time_str}", fm_text, flags=re.MULTILINE | re.IGNORECASE)
    if n == 0:
        fm_text += f"\ndate: {current_time_str}"
        
    content = f"---\n{fm_text.strip()}\n---\n\n{body_text.strip()}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

    # Pre-warm image cache
    image_url_match = re.search(r'^image:\s*"(https?://picsum\.photos/seed/[^"]+)"', content, re.MULTILINE)
    if image_url_match:
        img_url = image_url_match.group(1)
        print(f"Pre-warming image cache for: {img_url}")
        import threading
        import urllib.request
        def prewarm():
            try:
                urllib.request.urlopen(img_url, timeout=15)
            except Exception as e:
                print(f"Image pre-warm failed: {e}")
        threading.Thread(target=prewarm, daemon=True).start()

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
