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

try:
    import feedparser
except ImportError:
    feedparser = None
import time

try:
    from scripts.dividend_opportunity_scanner import DividendOpportunityScanner, DEFAULT_DIVIDEND_STOCKS
except ImportError:
    from dividend_opportunity_scanner import DividendOpportunityScanner, DEFAULT_DIVIDEND_STOCKS


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
        if not feedparser:
            print("feedparser 미설치 환경: 기본 폴백 테크 토픽 풀 사용")
            return fallback_topics

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
            return category, topic, None
        else:
            topic = random.choice(fallback_topics)
            print(f"백업 목록에서 선택한 주제 [{category.upper()}]: {topic}")
            return category, topic, None

    else:  # dividend / finance
        # _posts 디렉토리 경로
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        posts_dir = os.path.join(base_dir, "_posts")

        # 1. EDITH Multi-Factor Dividend Opportunity Scanner 가동
        try:
            print("[EDITH Engine] 실시간 금융 데이터 및 6대 기회 스캐너 가동 중...")
            scanner = DividendOpportunityScanner(posts_dir=posts_dir)
            all_opps = scanner.scan_all_stocks()

            # 쿨다운(-50점)을 감안하여 점수 35점 이상인 최상위 기회 종목 탐색
            valid_opps = [o for o in all_opps if o["score"] >= 35]
            if valid_opps:
                top_opp = valid_opps[0]
                stock_name = top_opp["name"]
                trigger = top_opp["primary_trigger"]

                # 트리거별 최적화된 블로그 주제 생성
                if trigger == "dividend_hike":
                    topic = f"{stock_name} 배당금 깜짝 인상 발표 및 2026 현금흐름 팩트시트"
                elif trigger == "valuation_dip":
                    topic = f"{stock_name} 52주 고점 대비 저평가 조정 및 배당 매수 기회 분석"
                elif trigger == "ex_dividend_countdown":
                    topic = f"{stock_name} 배당락일 D-day 임박 및 배당금 수령 투자 전략"
                elif trigger == "risk_audit":
                    topic = f"{stock_name} 배당 삭감 리스크 및 배당 안전성 긴급 진단"
                elif trigger == "etf_rebalance":
                    topic = f"{stock_name} ETF 최신 분배금 발표 및 포트폴리오 리밸런싱 분석"
                elif trigger == "oversold_bounce":
                    topic = f"{stock_name} 바닥권 기술적 과매도 탈출 및 배당+시세차익 분석"
                else:
                    topic = f"{stock_name} 배당 및 재무 분석 팩트시트"

                print(f"🔥 [EDITH 기회 포착 선정] {stock_name} (Score: {top_opp['score']}점, Trigger: {trigger})")
                for r in top_opp["reasons"]:
                    print(f"   -> {r}")
                return category, topic, top_opp
        except Exception as e:
            print(f"[EDITH Scanner Warning] 스캐너 실행 중 예외 발생, Fallback 가동: {e}")

        # 2. Fallback: 기존 LRU 및 미발행 종목 순환 알고리즘
        dividend_stocks_data = DEFAULT_DIVIDEND_STOCKS
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
                        content = f.read().lower()

                    for item in dividend_stocks_data:
                        ticker = item["ticker"]
                        for kw in item["keywords"]:
                            if kw.lower() in content:
                                if stock_last_dates[ticker] is None or post_date_str > stock_last_dates[ticker]:
                                    stock_last_dates[ticker] = post_date_str
                                break
                except Exception:
                    pass

        never_posted = [item for item in dividend_stocks_data if stock_last_dates[item["ticker"]] is None]
        if never_posted:
            selected_item = random.choice(never_posted)
            print(f"신규 종목 선택 (포스팅 이력 없음) [{category.upper()}]: {selected_item['name']}")
        else:
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
        return category, topic, None

def generate_blog_post(category, topic, opp_info=None):
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
        opp_context = ""
        if opp_info:
            trigger_labels = {
                "dividend_hike": "🔥 배당금 깜짝 인상 발표 및 배당 성장성 모멘텀",
                "valuation_dip": "💎 52주 고점 대비 큰 폭 조정에 따른 저평가 배당 매수 기회",
                "ex_dividend_countdown": "⏰ 배당락일 D-day 임박 (단기 배당금 수령 매수 적기)",
                "risk_audit": "⚠️ 배당 삭감 리스크 및 배당 안전성 긴급 진단",
                "etf_rebalance": "🔄 ETF 정기 리밸런싱 및 분배금 현금흐름 심층 해부",
                "oversold_bounce": "📈 바닥권 기술적 과매도 탈출 및 배당+시세차익 공략",
                "general": "📊 2026 최신 펀더멘털 및 배당 현금흐름 분석"
            }
            trigger_name = trigger_labels.get(opp_info.get("primary_trigger"), "최신 배당 기회 분석")
            reasons_str = "\n".join([f"- {r}" for r in opp_info.get("reasons", [])])
            is_revisit = opp_info.get("is_revisit", False)
            revisit_note = "※ 본 종목은 과거 분석 이력이 있는 종목이나, 이번 시장 이벤트/지표 변화로 인해 [긴급 재분석 & 2026 최신 업데이트]로 발행됩니다." if is_revisit else ""

            opp_context = f"""
[이디스 금융 기회 분석 데이터]
- 핵심 분석 테마: {trigger_name}
- 현재 주가 수준: 약 {opp_info.get('price', 0.0)}$
- 연간 추정 배당수익률: 약 {opp_info.get('dividend_yield', 0.0)}%
- 감지된 주요 선정 사유:
{reasons_str}
{revisit_note}
"""

        prompt = f"""
당신은 글로벌 주식 시장과 현금흐름 자산을 전문으로 분석하는 월스트리트 수석 퀀트 애널리스트이자 금융 전문 칼럼니스트입니다.
아래 종목에 대해 투자자들에게 깊이 있는 펀더멘털 분석과 객관적 리스크를 전달하는 **'프리미엄 배당 & 재무 분석 팩트시트'**를 작성해주세요.

종목/주제: {topic}
{opp_context}

핵심 작성 지침 (구글 E-E-A-T 품질 가이드라인 엄수):
1. **분량 및 심층성**: 단순 수치 표 나열을 넘어 각 데이터가 의미하는 비즈니스 경쟁력, 잉여현금흐름(FCF) 구조, 배당 지속 가능성을 충분한 줄글 서술로 설명할 것 (공백 제외 1,900자 ~ 2,600자 분량).
2. **시의성 및 재분석 당위성(필수)**: 
   - 독자에게 "왜 지금 이 시점에 이 종목을 다시 주목해야 하는가?"(배당 인상 공시, 주가 조정으로 인한 시가배당률 상승, 배당락일 임박 등)를 서론과 본문 전반부에서 강력하게 어필할 것.
3. **객관적 리스크와 하방 압력 분석(필수)**: 
   - 고배당 뒤에 숨겨진 리스크(NAV 침식 우려, 부채 만기 구조, 금리 민감도, 배당성향 악화 등)를 냉정하고 비판적인 시각에서 균형 있게 다룰 것.
4. **구조화된 섹션**:
   - 목차(TOC)는 자동 생성을 위해 본문 맨 앞에 딱 한 번 아래 내용을 그대로 입력할 것:
     * TOC
     {{:toc}}
   - 🚨 **왜 지금 다시 주목해야 하는가? (최신 시장 이벤트 & 선정 배경)**: 최근 배당 인상, 가격 조정, 배당락일 등 핵심 모멘텀 심층 분석
   - 🏢 **기업 개요 및 비즈니스 모델**: 매출 구조 및 잉여현금흐름 창출 메커니즘 상세 설명
   - 💰 **핵심 배당 팩트 & 현금흐름 궤적**: 시가배당률, 최근 배당 인상 내역, 지급 주기, 연속 증배 연수 등
   - 📊 **재무 건전성 및 리스크 심층 평가**: FCF 배당성향, 부채 비율, 이자보상배율, 산업적 위협 요인
   - 🎯 **밸류에이션 및 가격대별 투자 전략**: 목표주가 컨센서스, DRIP(배당 재투자) 복리 시뮬레이션
   - 📋 **한눈에 보는 핵심 요약 표**: 핵심 지표를 정리한 깔끔한 마크다운 Table
5. **Frontmatter 메타데이터**:
   - `title`: 클릭률과 전문성을 극대화한 매력적인 제목 (예: "[2026 최신] 리얼티 인컴(O) 배당금 또 올랐다! 지금이 매수 적기인 이유")
   - `description`: 해당 기업의 배당 매력도와 핵심 리스크 요약을 담은 1~2문장 (80~120자)
   - `categories`: [Dividend, Finance]
   - `tags`: 종목명, 티커, 배당주, 미국주식 등 4~5개
   - `image`: "https://image.pollinations.ai/prompt/[해당기업_산업_관련_영어키워드]?width=800&height=450&nologo=true"
6. **하단 투자 면책 조항**:
   - 최하단에 `<div class="disclaimer-box"><p><em>(본 포스팅은 단순 정보 제공을 목적으로 작성되었으며, 특정 종목이나 상품에 대한 투자 권유가 아닙니다. 모든 투자의 판단과 책임은 투자자 본인에게 있습니다.)</em></p></div>` 포함.
7. **금지 사항**:
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

    # 최신 활성 모델 라인업 (gemini-2.0-flash EOL 반영 및 3.8, 3.7 추가)
    models_to_try = ['gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash']
    last_err = None
    for model_name in models_to_try:
        for attempt in range(1, 4):
            try:
                print(f"Generating content with model: {model_name} (attempt {attempt}/3)...")
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
                    break
                return text
            except Exception as e:
                err_str = str(e)
                print(f"Model {model_name} attempt {attempt} failed ({err_str})...")
                last_err = e
                # 일시적 부하(503) 또는 속도 제한(429) 시 지수 백오프 대기 후 재시도
                if any(code in err_str for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]) and attempt < 3:
                    wait_sec = attempt * 3
                    print(f"Temporary API spike detected. Waiting {wait_sec}s before retry...")
                    time.sleep(wait_sec)
                else:
                    break
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
        
    # 이미지 로컬 정적 에셋 다운로드 및 영구 캐싱
    img_dest_dir = os.path.join(base_dir, "assets", "images", "posts")
    os.makedirs(img_dest_dir, exist_ok=True)
    local_img_name = f"{filename[:-3]}.jpg"
    local_img_path = os.path.join(img_dest_dir, local_img_name)
    web_img_url = f"/assets/images/posts/{local_img_name}"

    image_url_match = re.search(r'^image:\s*"(https?://[^"]+)"', fm_text, re.MULTILINE)
    external_img_url = image_url_match.group(1) if image_url_match else None

    # 자연스러운 고화질 Unsplash 실사 스톡 사진 매핑 풀
    SPECIFIC_PHOTOS = {
        "pep": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=1000&q=80&auto=format&fit=crop",
        "펩시": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=1000&q=80&auto=format&fit=crop",
        "coca": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=1000&q=80&auto=format&fit=crop",
        "콜라": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=1000&q=80&auto=format&fit=crop",
        "ko": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=1000&q=80&auto=format&fit=crop",
        "vym": "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=1000&q=80&auto=format&fit=crop",
        "뱅가드": "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=1000&q=80&auto=format&fit=crop",
        "vanguard": "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=1000&q=80&auto=format&fit=crop",
        "schd": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000&q=80&auto=format&fit=crop",
        "배당": "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=1000&q=80&auto=format&fit=crop",
        "etf": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1000&q=80&auto=format&fit=crop",
        "nvdy": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1000&q=80&auto=format&fit=crop",
        "nvda": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1000&q=80&auto=format&fit=crop",
        "엔비디아": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1000&q=80&auto=format&fit=crop",
        "semiconductor": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
        "반도체": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
        "apple": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000&q=80&auto=format&fit=crop",
        "애플": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000&q=80&auto=format&fit=crop",
        "aapl": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000&q=80&auto=format&fit=crop",
        "microsoft": "https://images.unsplash.com/photo-1583321500900-82807e458f3c?w=1000&q=80&auto=format&fit=crop",
        "msft": "https://images.unsplash.com/photo-1583321500900-82807e458f3c?w=1000&q=80&auto=format&fit=crop",
        "마이크로소프트": "https://images.unsplash.com/photo-1583321500900-82807e458f3c?w=1000&q=80&auto=format&fit=crop",
        "starbucks": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&q=80&auto=format&fit=crop",
        "스타벅스": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&q=80&auto=format&fit=crop",
        "mcdonald": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=1000&q=80&auto=format&fit=crop",
        "맥도날드": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=1000&q=80&auto=format&fit=crop",
        "realty": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1000&q=80&auto=format&fit=crop",
        "리얼티": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1000&q=80&auto=format&fit=crop",
        "의료": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1000&q=80&auto=format&fit=crop",
        "medical": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1000&q=80&auto=format&fit=crop",
        "번역": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1000&q=80&auto=format&fit=crop",
        "translation": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1000&q=80&auto=format&fit=crop",
        "보안": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1000&q=80&auto=format&fit=crop",
        "security": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1000&q=80&auto=format&fit=crop",
    }

    natural_finance_fallbacks = [
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=1000&q=80&auto=format&fit=crop"
    ]
    natural_tech_fallbacks = [
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1000&q=80&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1000&q=80&auto=format&fit=crop"
    ]

    # 키워드 매칭 실사 사진 탐색
    content_search = (filename + " " + fm_text).lower()
    selected_photo_url = None
    for kw, p_url in SPECIFIC_PHOTOS.items():
        if kw in content_search:
            selected_photo_url = p_url
            break

    if not selected_photo_url:
        pool = natural_tech_fallbacks if category == "tech" else natural_finance_fallbacks
        selected_photo_url = random.choice(pool)

    import urllib.request
    import ssl
    ctx = ssl._create_unverified_context()
    downloaded = False
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # Pollinations AI 생성 URL을 1순위 후보군에 추가
    candidate_urls = []
    if external_img_url and "pollinations.ai" in external_img_url:
        candidate_urls.append(external_img_url)
    if selected_photo_url:
        candidate_urls.append(selected_photo_url)
    candidate_urls += (natural_tech_fallbacks if category == "tech" else natural_finance_fallbacks)
    
    for url_to_try in candidate_urls:
        try:
            print(f"Downloading stock/AI photo: {url_to_try[:60]}...")
            req = urllib.request.Request(url_to_try, headers=headers)
            with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                img_bytes = resp.read()
                if len(img_bytes) > 5000:
                    try:
                        from PIL import Image as PILImage
                        import io
                        img = PILImage.open(io.BytesIO(img_bytes)).convert("RGB")
                        webp_name = f"{filename[:-3]}.webp"
                        webp_path = os.path.join(img_dest_dir, webp_name)
                        img.save(webp_path, "WEBP", quality=82, method=6)
                        web_img_url = f"/assets/images/posts/{webp_name}"
                        downloaded = True
                        print(f"WebP optimized image created: {webp_name} ({os.path.getsize(webp_path)} bytes)")
                    except Exception as conv_err:
                        with open(local_img_path, "wb") as f_img:
                            f_img.write(img_bytes)
                        downloaded = True
                    break
        except Exception as e:
            print(f"Image download attempt failed ({e}), trying fallback...")

    # [핵심 가드레일]: 실제 다운로드 성공 시에만 로컬 경로 주입, 실패 시 안전한 외부 CDN URL 유지하여 404 방지
    if downloaded:
        target_img_url = web_img_url
    else:
        fallback_web = external_img_url or selected_photo_url or "https://picsum.photos/800/450?grayscale"
        target_img_url = fallback_web
        print(f"Warning: Local download failed. Falling back to external URL: {target_img_url}")

    if "image:" in fm_text:
        fm_text = re.sub(r'^[ \t]*image:[^\n]*$', f'image: "{target_img_url}"', fm_text, flags=re.MULTILINE)
    else:
        fm_text += f'\nimage: "{target_img_url}"'

    content = f"---\n{fm_text.strip()}\n---\n\n{body_text.strip()}"

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
        category, topic, opp_info = get_topic_by_category(args.category)
        print(f"최종 결정된 주제: {topic}")

        print("2. 블로그 포스트 생성 중... (Gemini API 호출)")
        post_content = generate_blog_post(category, topic, opp_info=opp_info)

        print("3. 포스트 저장 중...")
        save_post(post_content, category)

        print("작업 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)
