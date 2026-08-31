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
        dividend_stocks_data = [
            # 초우량 / 배당성장
            {"ticker": "KO", "name": "코카콜라 (KO)", "keywords": ["KO", "코카콜라"]},
            {"ticker": "O", "name": "리얼티 인컴 (O)", "keywords": ["리얼티 인컴", "리얼티인컴", "Realty Income"]},
            {"ticker": "JNJ", "name": "존슨앤존슨 (JNJ)", "keywords": ["JNJ", "존슨앤존슨", "존슨앤드존슨"]},
            {"ticker": "AAPL", "name": "애플 (AAPL)", "keywords": ["AAPL", "애플"]},
            {"ticker": "MSFT", "name": "마이크로소프트 (MSFT)", "keywords": ["MSFT", "마이크로소프트"]},
            {"ticker": "SBUX", "name": "스타벅스 (SBUX)", "keywords": ["SBUX", "스타벅스"]},
            {"ticker": "MCD", "name": "맥도날드 (MCD)", "keywords": ["MCD", "맥도날드"]},
            {"ticker": "PG", "name": "프록터앤갬블 (PG)", "keywords": ["PG", "프록터앤갬블", "프록터 & 갬블"]},
            {"ticker": "XOM", "name": "엑슨모빌 (XOM)", "keywords": ["XOM", "엑슨모빌"]},
            {"ticker": "CVX", "name": "셰브론 (CVX)", "keywords": ["CVX", "셰브론"]},
            {"ticker": "ABBV", "name": "애비브 (ABBV)", "keywords": ["ABBV", "애비브"]},
            {"ticker": "PFE", "name": "화이자 (PFE)", "keywords": ["PFE", "화이자"]},
            {"ticker": "HD", "name": "홈디포 (HD)", "keywords": ["HD", "홈디포"]},
            {"ticker": "LMT", "name": "록히드마틴 (LMT)", "keywords": ["LMT", "록히드마틴"]},
            {"ticker": "TXN", "name": "텍사스 인스트루먼트 (TXN)", "keywords": ["TXN", "텍사스 인스트루먼트", "텍사스인스트루먼트"]},
            {"ticker": "COST", "name": "코스트코 (COST)", "keywords": ["COST", "코스트코"]},
            {"ticker": "JPM", "name": "제이피모건체이스 (JPM)", "keywords": ["JPM", "제이피모건", "JP모건"]},
            {"ticker": "BAC", "name": "뱅크오브아메리카 (BAC)", "keywords": ["BAC", "뱅크오브아메리카"]},
            {"ticker": "PEP", "name": "펩시코 (PEP)", "keywords": ["PEP", "펩시코"]},
            {"ticker": "CSCO", "name": "시스코 시스템즈 (CSCO)", "keywords": ["CSCO", "시스코"]},
            {"ticker": "AVGO", "name": "브로드컴 (AVGO)", "keywords": ["AVGO", "브로드컴"]},
            {"ticker": "QCOM", "name": "퀄컴 (QCOM)", "keywords": ["QCOM", "퀄컴"]},
            
            # 고배당 / 리츠 / BDC / 통신 / 에너지 / 모기지
            {"ticker": "T", "name": "AT&T (T)", "keywords": ["AT&T", "AT and T"]},
            {"ticker": "VZ", "name": "버라이즌 (VZ)", "keywords": ["VZ", "버라이즌"]},
            {"ticker": "MO", "name": "알트리아 (MO)", "keywords": ["MO", "알트리아"]},
            {"ticker": "BTI", "name": "브리티시 아메리칸 토바코 (BTI)", "keywords": ["BTI", "브리티시 아메리칸 토바코", "브리티시아메리칸"]},
            {"ticker": "ARCC", "name": "아레스 캐피탈 (ARCC)", "keywords": ["ARCC", "아레스 캐피탈", "아레스캐피탈"]},
            {"ticker": "MAIN", "name": "메인 스트리트 캐피탈 (MAIN)", "keywords": ["MAIN", "메인 스트리트", "메인스트리트"]},
            {"ticker": "PSEC", "name": "프로스펙트 캐피탈 (PSEC)", "keywords": ["PSEC", "프로스펙트 캐피탈", "프로스펙트캐피탈"]},
            {"ticker": "AGNC", "name": "에이전시 인베스트먼트 (AGNC)", "keywords": ["AGNC", "에이전시 인베스트먼트", "에이전시인베스트먼트"]},
            {"ticker": "ARR", "name": "아머 레지덴셜 리츠 (ARR)", "keywords": ["ARR", "아머 레지덴셜", "아머레지덴셜"]},
            {"ticker": "STWD", "name": "스타우드 프로퍼티 (STWD)", "keywords": ["STWD", "스타우드 프로퍼티", "스타우드프로퍼티"]},
            {"ticker": "OHI", "name": "오메가 헬스케어 (OHI)", "keywords": ["OHI", "오메가 헬스케어", "오메가헬스케어"]},
            {"ticker": "MPW", "name": "메디컬 프로퍼티즈 트러스트 (MPW)", "keywords": ["MPW", "메디컬 프로퍼티즈", "메디컬프로퍼티즈"]},
            {"ticker": "WPC", "name": "W.P. 캐리 (WPC)", "keywords": ["WPC", "W.P. 캐리", "W.P.캐리", "WP 캐리"]},
            {"ticker": "EPD", "name": "엔터프라이즈 프로덕츠 파트너스 (EPD)", "keywords": ["EPD", "엔터프라이즈 프로덕츠"]},
            {"ticker": "EQIX", "name": "에퀴닉스 (EQIX)", "keywords": ["EQIX", "에퀴닉스"]},
            {"ticker": "AMT", "name": "아메리칸 타워 (AMT)", "keywords": ["AMT", "아메리칸 타워"]},
            {"ticker": "VICI", "name": "비시 프로퍼티스 (VICI)", "keywords": ["VICI", "비시 프로퍼티스", "VICI Properties"]},
            
            # 고배당 / 커버드콜 / 배당 ETF
            {"ticker": "SCHD", "name": "슈와브 US 디비던드 에퀴티 (SCHD)", "keywords": ["SCHD", "슈와브 US", "Schwab U.S. Dividend"]},
            {"ticker": "JEPI", "name": "JP모건 에퀴티 프리미엄 인컴 (JEPI)", "keywords": ["JEPI", "JP모건 에퀴티 프리미엄"]},
            {"ticker": "JEPQ", "name": "JP모건 나스닥 에퀴티 프리미엄 (JEPQ)", "keywords": ["JEPQ", "JP모건 나스닥 에퀴티"]},
            {"ticker": "QYLD", "name": "Global X 나스닥 100 커버드콜 (QYLD)", "keywords": ["QYLD", "Global X 나스닥"]},
            {"ticker": "SDIV", "name": "Global X 슈퍼디비던드 (SDIV)", "keywords": ["SDIV", "슈퍼디비던드"]},
            {"ticker": "TSLY", "name": "일드맥스 TSLA 옵션 인컴 (TSLY)", "keywords": ["TSLY", "일드맥스 TSLA", "YieldMax TSLA"]},
            {"ticker": "NVDY", "name": "일드맥스 NVDA 옵션 인컴 (NVDY)", "keywords": ["NVDY", "일드맥스 NVDA", "YieldMax NVDA"]},
            {"ticker": "VYM", "name": "뱅가드 하이 디비던드 (VYM)", "keywords": ["VYM", "뱅가드 하이 디비던드"]},
            {"ticker": "DVY", "name": "iShares Select Dividend (DVY)", "keywords": ["DVY", "iShares Select Dividend"]}
        ]

        # _posts 디렉토리 경로
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        posts_dir = os.path.join(base_dir, "_posts")

        # 최근 포스팅 기록 파싱
        import glob
        import re

        stock_last_dates = {item["ticker"]: None for item in dividend_stocks_data}
        if os.path.exists(posts_dir):
            post_files = glob.glob(os.path.join(posts_dir, "*.md"))
            for file_path in post_files:
                try:
                    filename = os.path.basename(file_path)
                    date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', filename)
                    if not date_match:
                        continue
                    post_date_str = date_match.group(1)

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    for item in dividend_stocks_data:
                        ticker = item["ticker"]
                        keywords = item["keywords"]
                        for kw in keywords:
                            if kw.lower() in content.lower():
                                if stock_last_dates[ticker] is None or post_date_str > stock_last_dates[ticker]:
                                    stock_last_dates[ticker] = post_date_str
                                break
                except Exception as e:
                    pass

        # Round-Robin / LRU (Least Recently Used) 선택 알고리즘
        # 1. 포스팅 이력이 없는(None) 종목 후보군
        never_posted = [item for item in dividend_stocks_data if stock_last_dates[item["ticker"]] is None]

        if never_posted:
            selected_item = random.choice(never_posted)
            print(f"신규 종목 선택 (포스팅 이력 없음) [{category.upper()}]: {selected_item['name']}")
        else:
            # 2. 모든 종목이 1회 이상 작성된 경우, 가장 오래전에 작성된 일자 탐색
            min_date = min(stock_last_dates[item["ticker"]] for item in dividend_stocks_data)
            oldest_candidates = [
                item for item in dividend_stocks_data 
                if stock_last_dates[item["ticker"]] == min_date
            ]
            selected_item = random.choice(oldest_candidates)
            print(f"Round-Robin / LRU 순환 선택 (마지막 작성일: {min_date}) [{category.upper()}]: {selected_item['name']}")

        stock = selected_item["name"]
        topic = f"{stock} 배당 및 재무 분석 팩트시트"
        print(f"최종 결정된 배당주 주제: {topic}")
        return category, topic

def generate_blog_post(category, topic):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    if category == "tech":
        prompt = f"""
당신은 IT/테크 및 생산성 향상 팁을 전문으로 다루는 최상위 테크 저널리스트이자 전문 블로거입니다.
다음 주제에 대해 독자에게 실질적인 통찰과 고유한 가치를 제공하는 최고 품질(E-E-A-T 준수)의 블로그 포스트를 작성해주세요.

주제: {topic}

핵심 작성 지침 (구글 품질 가이드라인 엄수):
1. **분량 및 깊이**: 단순 요약이나 불릿 포인트 나열을 지양하고, 배경 설명, 심층 분석, 실무 적용 팁 등 완성도 높은 서술형 문단으로 풍부하게 작성할 것 (공백 제외 1,800자 ~ 2,500자 분량).
2. **독창적 시각(Insight)**: 뉴스나 오픈 데이터의 단순 전달에 그치지 않고, 기술적 파급 효과, 실제 활용 시의 장단점, 도입 시 주의사항 등 전문적인 분석 의견을 반드시 포함할 것.
3. **구조화된 목차**:
   - 목차(TOC)는 Jekyll 마크다운 파서가 자동 생성하므로 본문 맨 앞에 딱 한 번 아래 내용을 그대로 입력할 것:
     * TOC
     {{:toc}}
   - 서론(도입 배경 및 왜 지금 중요한지), 본론(3개 이상의 소주제별 심층 해설 및 활용 가이드), 결론(향후 전망 및 액션 아이템), FAQ(실제 사용자가 궁금해할 핵심 질문 2~3개와 상세 답변) 구조로 작성할 것.
4. **Frontmatter 메타데이터**:
   - `title`: 클릭을 유도하면서도 전문성이 느껴지는 명확한 제목
   - `description`: 검색 결과 및 SNS 카드에 노출될 1~2문장의 핵심 요약문 (80~120자 내외)
   - `categories`: [Tech, Trend] 또는 관련 카테고리
   - `tags`: 핵심 키워드 4~5개
    - `image`: "https://image.pollinations.ai/prompt/[주제_관련_구체적_영어키워드]?width=800&height=450&nologo=true" (예: cloud_computing_server, artificial_intelligence_code 등)
5. **금지 사항**:
   - 상업적 제휴 링크(쿠팡 파트너스 등)나 어필리에이트 문구를 절대 삽입하지 말 것.
   - 본문 내에 불필요한 마크다운 이미지 태그를 중복 삽입하지 말 것.
   - 응답은 마크다운 코드블록(```markdown) 없이 순수 Jekyll 텍스트 포맷으로 출력할 것.

Frontmatter 형식 예시:
---
layout: post
title: "생성된 제목"
date: {datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')} +0900
description: "포스트의 핵심 내용을 1~2문장으로 요약한 텍스트입니다."
categories: [Tech, Trend]
tags: [AI, 클라우드, 생산성, 테크트렌드]
image: "https://image.pollinations.ai/prompt/artificial_intelligence_future?width=800&height=450&nologo=true"
---

본문 내용...
"""
    else:  # dividend / finance
        prompt = f"""
당신은 글로벌 주식 시장과 현금흐름 자산을 전문으로 분석하는 월스트리트 수석 퀀트 애널리스트이자 금융 전문 칼럼니스트입니다.
아래 종목에 대해 투자자들에게 깊이 있는 펀더멘털 분석과 객관적 리스크를 전달하는 **'프리미엄 배당 & 재무 분석 팩트시트'**를 작성해주세요.

종목/주제: {topic}

핵심 작성 지침 (구글 품질 가이드라인 엄수):
1. **분량 및 심층성**: 단순 수치 표 나열을 넘어 각 데이터가 의미하는 비즈니스 경쟁력, 잉여현금흐름(FCF) 구조, 배당 지속 가능성을 충분한 줄글 서술로 설명할 것 (공백 제외 1,800자 ~ 2,500자 분량).
2. **객관적 리스크와 하방 압력 분석(필수)**: 
   - 고배당 뒤에 숨겨진 리스크(NAV 침식 우려, 부채 만기 구조, 금리 민감도, 배당 삭감 이력 등)를 냉정하고 비판적인 시각에서 균형 있게 다룰 것.
3. **구조화된 섹션**:
   - 목차(TOC)는 자동 생성을 위해 본문 맨 앞에 딱 한 번 아래 내용을 그대로 입력할 것:
     * TOC
     {{:toc}}
   - 🏢 **기업 개요 및 비즈니스 모델**: 매출 구조 및 잉여현금흐름 창출 메커니즘 상세 설명
   - 💰 **핵심 배당 팩트 & 과거 성장 궤적**: 시가배당률, 지급 주기, 연속 증배 연수, 과거 5년 CAGR 등
   - 📊 **재무 건전성 및 리스크 심층 평가**: FCF 배당성향, 부채 비율, 이자보상배율, 산업적 위협 요인
   - 🎯 **월가 애널리스트 컨센서스 & 밸류에이션**: 목표주가 밴드, PER/PBR 수준, 투자의견 종합
   - 📋 **한눈에 보는 핵심 요약 표**: 핵심 지표를 정리한 깔끔한 마크다운 Table
4. **Frontmatter 메타데이터**:
   - `title`: 직관적이고 정보 가치가 명확한 제목 (예: "[종목명] 배당률 N%, 연 N회 지급! 2026년 배당 및 재무 팩트시트")
   - `description`: 해당 기업의 배당 매력도와 핵심 리스크 요약을 담은 1~2문장 (80~120자)
   - `categories`: [Dividend, Finance]
   - `tags`: 종목명, 티커, 배당주, 미국주식 등 4~5개
   - `image`: "https://image.pollinations.ai/prompt/[해당기업_산업_관련_영어키워드]?width=800&height=450&nologo=true"
5. **하단 투자 면책 조항**:
   - 최하단에 `<div class="disclaimer-box"><p><em>(본 포스팅은 단순 정보 제공을 목적으로 작성되었으며, 특정 종목이나 상품에 대한 투자 권유가 아닙니다. 모든 투자의 판단과 책임은 투자자 본인에게 있습니다.)</em></p></div>` 포함.
6. **금지 사항**:
   - 상업적 링크나 제휴 마케팅 문구 절대 금지.
   - 마크다운 코드블록(```markdown)으로 감싸지 말고 순수 텍스트만 출력할 것.

Frontmatter 형식 예시:
---
layout: post
title: "생성된 제목"
date: {datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')} +0900
description: "기업명 배당 수익률과 재무 건전성, 잉여현금흐름 및 투자 리스크에 대한 종합 분석 팩트시트입니다."
categories: [Dividend, Finance]
tags: [배당주, 미국주식, 팩트시트, 재무분석]
image: "https://image.pollinations.ai/prompt/Coca_Cola_beverage_corporate?width=800&height=450&nologo=true"
---

본문 내용...
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
    fm_keys = ["layout:", "title:", "date:", "description:", "categories:", "tags:", "image:"]
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
    image_url_match = re.search(r'^image:\s*"(https?://[^"]+)"', content, re.MULTILINE)
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
