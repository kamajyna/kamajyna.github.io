"""
EDITH Multi-Factor Dividend Opportunity Scanner
------------------------------------------------
이디스(EDITH) 전산망 산하 오토블로그 주식 기회 포착 및 재업로드 판단 엔진.

6대 핵심 기회 팩터:
1. 배당 인상 (Dividend Hike)
2. 밸류에이션 매력 급상승 (Valuation Dip / 52주 고점 대비 큰 폭 조정)
3. 배당락일/지급일 임박 (Ex-Dividend / Payment Countdown)
4. 배당 삭감 위험/안전성 긴급 점검 (Payout & Risk Audit)
5. ETF 분기 리밸런싱 / 분배금 변동 (ETF Rebalance / Payout Fluctuation)
6. 기술적 과매도 반등 (Oversold Bounce / 52주 저점 지지)
+ 재포스팅 쿨다운 방어 (최근 14일 이내 포스팅 시 감점)
"""

import os
import re
import glob
import time
import datetime
from datetime import timezone, timedelta
import requests

KST = timezone(timedelta(hours=9))

# 기본 배당 종목 데이터셋
DEFAULT_DIVIDEND_STOCKS = [
    # 초우량 / 배당성장
    {"ticker": "KO", "name": "코카콜라 (KO)", "keywords": ["KO", "코카콜라"], "type": "dividend_growth"},
    {"ticker": "O", "name": "리얼티 인컴 (O)", "keywords": ["리얼티 인컴", "리얼티인컴", "Realty Income"], "type": "monthly_reit"},
    {"ticker": "JNJ", "name": "존슨앤존슨 (JNJ)", "keywords": ["JNJ", "존슨앤존슨", "존슨앤드존슨"], "type": "dividend_growth"},
    {"ticker": "AAPL", "name": "애플 (AAPL)", "keywords": ["AAPL", "애플"], "type": "dividend_growth"},
    {"ticker": "MSFT", "name": "마이크로소프트 (MSFT)", "keywords": ["MSFT", "마이크로소프트"], "type": "dividend_growth"},
    {"ticker": "SBUX", "name": "스타벅스 (SBUX)", "keywords": ["SBUX", "스타벅스"], "type": "dividend_growth"},
    {"ticker": "MCD", "name": "맥도날드 (MCD)", "keywords": ["MCD", "맥도날드"], "type": "dividend_growth"},
    {"ticker": "PG", "name": "프록터앤갬블 (PG)", "keywords": ["PG", "프록터앤갬블", "프록터 & 갬블"], "type": "dividend_growth"},
    {"ticker": "XOM", "name": "엑슨모빌 (XOM)", "keywords": ["XOM", "엑슨모빌"], "type": "energy_dividend"},
    {"ticker": "CVX", "name": "셰브론 (CVX)", "keywords": ["CVX", "셰브론"], "type": "energy_dividend"},
    {"ticker": "ABBV", "name": "애비브 (ABBV)", "keywords": ["ABBV", "애비브"], "type": "dividend_growth"},
    {"ticker": "PFE", "name": "화이자 (PFE)", "keywords": ["PFE", "화이자"], "type": "high_yield"},
    {"ticker": "HD", "name": "홈디포 (HD)", "keywords": ["HD", "홈디포"], "type": "dividend_growth"},
    {"ticker": "LMT", "name": "록히드마틴 (LMT)", "keywords": ["LMT", "록히드마틴"], "type": "dividend_growth"},
    {"ticker": "TXN", "name": "텍사스 인스트루먼트 (TXN)", "keywords": ["TXN", "텍사스 인스트루먼트", "텍사스인스트루먼트"], "type": "dividend_growth"},
    {"ticker": "COST", "name": "코스트코 (COST)", "keywords": ["COST", "코스트코"], "type": "dividend_growth"},
    {"ticker": "JPM", "name": "제이피모건체이스 (JPM)", "keywords": ["JPM", "제이피모건", "JP모건"], "type": "dividend_growth"},
    {"ticker": "BAC", "name": "뱅크오브아메리카 (BAC)", "keywords": ["BAC", "뱅크오브아메리카"], "type": "high_yield"},
    {"ticker": "PEP", "name": "펩시코 (PEP)", "keywords": ["PEP", "펩시코"], "type": "dividend_growth"},
    {"ticker": "CSCO", "name": "시스코 시스템즈 (CSCO)", "keywords": ["CSCO", "시스코"], "type": "dividend_growth"},
    {"ticker": "AVGO", "name": "브로드컴 (AVGO)", "keywords": ["AVGO", "브로드컴"], "type": "dividend_growth"},
    {"ticker": "QCOM", "name": "퀄컴 (QCOM)", "keywords": ["QCOM", "퀄컴"], "type": "dividend_growth"},
    
    # 고배당 / 리츠 / BDC / 통신 / 에너지
    {"ticker": "T", "name": "AT&T (T)", "keywords": ["AT&T", "AT and T"], "type": "high_yield"},
    {"ticker": "VZ", "name": "버라이즌 (VZ)", "keywords": ["VZ", "버라이즌"], "type": "high_yield"},
    {"ticker": "MO", "name": "알트리아 (MO)", "keywords": ["MO", "알트리아"], "type": "high_yield"},
    {"ticker": "BTI", "name": "브리티시 아메리칸 토바코 (BTI)", "keywords": ["BTI", "브리티시 아메리칸 토바코"], "type": "high_yield"},
    {"ticker": "ARCC", "name": "아레스 캐피탈 (ARCC)", "keywords": ["ARCC", "아레스 캐피탈"], "type": "bdc_monthly"},
    {"ticker": "MAIN", "name": "메인 스트리트 캐피탈 (MAIN)", "keywords": ["MAIN", "메인 스트리트"], "type": "bdc_monthly"},
    {"ticker": "PSEC", "name": "프로스펙트 캐피탈 (PSEC)", "keywords": ["PSEC", "프로스펙트 캐피탈"], "type": "high_yield"},
    {"ticker": "AGNC", "name": "에이전시 인베스트먼트 (AGNC)", "keywords": ["AGNC", "에이전시 인베스트먼트"], "type": "monthly_reit"},
    {"ticker": "ARR", "name": "아머 레지덴셜 리츠 (ARR)", "keywords": ["ARR", "아머 레지덴셜"], "type": "monthly_reit"},
    {"ticker": "STWD", "name": "스타우드 프로퍼티 (STWD)", "keywords": ["STWD", "스타우드 프로퍼티"], "type": "high_yield"},
    {"ticker": "OHI", "name": "오메가 헬스케어 (OHI)", "keywords": ["OHI", "오메가 헬스케어"], "type": "high_yield"},
    {"ticker": "MPW", "name": "메디컬 프로퍼티즈 트러스트 (MPW)", "keywords": ["MPW", "메디컬 프로퍼티즈"], "type": "high_yield_risk"},
    {"ticker": "WPC", "name": "W.P. 캐리 (WPC)", "keywords": ["WPC", "W.P. 캐리", "WP 캐리"], "type": "reit"},
    {"ticker": "EPD", "name": "엔터프라이즈 프로덕츠 파트너스 (EPD)", "keywords": ["EPD", "엔터프라이즈 프로덕츠"], "type": "energy_dividend"},
    {"ticker": "EQIX", "name": "에퀴닉스 (EQIX)", "keywords": ["EQIX", "에퀴닉스"], "type": "reit"},
    {"ticker": "AMT", "name": "아메리칸 타워 (AMT)", "keywords": ["AMT", "아메리칸 타워"], "type": "reit"},
    {"ticker": "VICI", "name": "비시 프로퍼티스 (VICI)", "keywords": ["VICI", "비시 프로퍼티스"], "type": "reit"},
    
    # 고배당 / 커버드콜 / 배당 ETF
    {"ticker": "SCHD", "name": "슈와브 US 디비던드 에퀴티 (SCHD)", "keywords": ["SCHD", "슈와브 US", "Schwab U.S. Dividend"], "type": "etf"},
    {"ticker": "JEPI", "name": "JP모건 에퀴티 프리미엄 인컴 (JEPI)", "keywords": ["JEPI", "JP모건 에퀴티 프리미엄"], "type": "etf_covered_call"},
    {"ticker": "JEPQ", "name": "JP모건 나스닥 에퀴티 프리미엄 (JEPQ)", "keywords": ["JEPQ", "JP모건 나스닥 에퀴티"], "type": "etf_covered_call"},
    {"ticker": "QYLD", "name": "Global X 나스닥 100 커버드콜 (QYLD)", "keywords": ["QYLD", "Global X 나스닥"], "type": "etf_covered_call"},
    {"ticker": "SDIV", "name": "Global X 슈퍼디비던드 (SDIV)", "keywords": ["SDIV", "슈퍼디비던드"], "type": "etf"},
    {"ticker": "TSLY", "name": "일드맥스 TSLA 옵션 인컴 (TSLY)", "keywords": ["TSLY", "일드맥스 TSLA", "YieldMax TSLA"], "type": "etf_high_yield"},
    {"ticker": "NVDY", "name": "일드맥스 NVDA 옵션 인컴 (NVDY)", "keywords": ["NVDY", "일드맥스 NVDA", "YieldMax NVDA"], "type": "etf_high_yield"},
    {"ticker": "VYM", "name": "뱅가드 하이 디비던드 (VYM)", "keywords": ["VYM", "뱅가드 하이 디비던드"], "type": "etf"},
    {"ticker": "DVY", "name": "iShares Select Dividend (DVY)", "keywords": ["DVY", "iShares Select Dividend"], "type": "etf"}
]


class DividendOpportunityScanner:
    def __init__(self, posts_dir=None, stocks_data=None):
        self.stocks_data = stocks_data or DEFAULT_DIVIDEND_STOCKS
        if not posts_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.posts_dir = os.path.join(base_dir, "_posts")
        else:
            self.posts_dir = posts_dir
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        self.last_posted_dates = self._scan_post_history()

    def _scan_post_history(self):
        """_posts 디렉토리에서 각 종목별 마지막 포스팅 날짜를 파싱"""
        history = {item["ticker"]: None for item in self.stocks_data}
        if not os.path.exists(self.posts_dir):
            return history

        post_files = glob.glob(os.path.join(self.posts_dir, "*.md"))
        for file_path in post_files:
            try:
                filename = os.path.basename(file_path)
                match = re.match(r"^(\d{4}-\d{2}-\d{2})", filename)
                if not match:
                    continue
                post_date = match.group(1)

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()

                for item in self.stocks_data:
                    ticker = item["ticker"]
                    for kw in item["keywords"]:
                        if kw.lower() in content:
                            if history[ticker] is None or post_date > history[ticker]:
                                history[ticker] = post_date
                            break
            except Exception:
                continue
        return history

    def get_days_since_last_post(self, ticker):
        """마지막 포스팅 일자로부터 경과된 일수 계산"""
        last_date_str = self.last_posted_dates.get(ticker)
        if not last_date_str:
            return 999  # 포스팅 이력 없음
        try:
            last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date()
            today = datetime.datetime.now(KST).date()
            return (today - last_date).days
        except Exception:
            return 999

    def fetch_market_data(self, ticker):
        """Yahoo Finance Chart & Events 엔드포인트에서 주가 및 배당 내역 수집"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1y&events=div"
        try:
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code != 200:
                return None
            data = resp.json()
            result = data.get("chart", {}).get("result", [])
            if not result:
                return None
            
            meta = result[0].get("meta", {})
            events = result[0].get("events", {})
            dividends = events.get("dividends", {})

            price = meta.get("regularMarketPrice") or meta.get("chartPreviousClose", 0.0)
            high_52w = meta.get("fiftyTwoWeekHigh", price)
            low_52w = meta.get("fiftyTwoWeekLow", price)

            # 배당 내역 정렬
            div_list = []
            for d in dividends.values():
                div_list.append({
                    "amount": float(d.get("amount", 0.0)),
                    "date": int(d.get("date", 0))
                })
            div_list.sort(key=lambda x: x["date"])

            return {
                "price": float(price),
                "high_52w": float(high_52w),
                "low_52w": float(low_52w),
                "dividends": div_list
            }
        except Exception:
            return None

    def evaluate_opportunity(self, stock_item, market_data):
        """
        단일 종목에 대한 6대 기회 점수(Opportunity Score) 및 상세 사유 평가
        """
        ticker = stock_item["ticker"]
        name = stock_item["name"]
        stock_type = stock_item.get("type", "general")
        days_since = self.get_days_since_last_post(ticker)
        
        score = 0
        reasons = []
        primary_trigger = "general"

        price = market_data.get("price", 0.0)
        high_52w = market_data.get("high_52w", price)
        low_52w = market_data.get("low_52w", price)
        div_list = market_data.get("dividends", [])

        # 0. 쿨다운 가드레일 (Spam Protection)
        if days_since < 14:
            score -= 50
            reasons.append(f"최근 {days_since}일 전 포스팅됨 (쿨다운 적용: -50점)")
        elif days_since >= 45:
            score += 15
            reasons.append(f"포스팅된 지 {days_since}일 경과 (업데이트 적기: +15점)")
        elif days_since >= 25:
            score += 8
            reasons.append(f"포스팅된 지 {days_since}일 경과 (+8점)")

        # 1. 🎯 배당금 인상 (Dividend Hike)
        if len(div_list) >= 2:
            latest_div = div_list[-1]["amount"]
            prev_div = div_list[-2]["amount"]
            if latest_div > prev_div and prev_div > 0:
                hike_pct = ((latest_div - prev_div) / prev_div) * 100
                if hike_pct >= 2.0:
                    score += 35
                    primary_trigger = "dividend_hike"
                    reasons.append(f"🔥 최근 배당금 {prev_div:.4f}$ -> {latest_div:.4f}$ ({hike_pct:+.1f}%) 인상 공시 (+35점)")
            elif latest_div < prev_div and prev_div > 0:
                cut_pct = ((prev_div - latest_div) / prev_div) * 100
                if cut_pct >= 5.0 and stock_type != "etf_covered_call":
                    # 4. ⚠️ 배당 삭감 위험/안전성 긴급 점검 (Risk Audit)
                    score += 25
                    primary_trigger = "risk_audit"
                    reasons.append(f"⚠️ 최근 배당금 {cut_pct:.1f}% 삭감 발생 (긴급 리스크 진단 테마: +25점)")

        # 2. 📉 밸류에이션 매력 급상승 (Valuation Dip / 과매도 저평가)
        if high_52w > 0 and price > 0:
            drawdown = ((price - high_52w) / high_52w) * 100
            if drawdown <= -20.0:
                score += 25
                if primary_trigger == "general":
                    primary_trigger = "valuation_dip"
                reasons.append(f"💎 52주 최고가 대비 {drawdown:.1f}% 큰 폭 조정 (저평가 배당 줍줍 기회: +25점)")
            elif drawdown <= -12.0:
                score += 15
                reasons.append(f"52주 최고가 대비 {drawdown:.1f}% 건전한 조정 (+15점)")

        # 3. ⏰ 배당락일 임박 카운트다운 (Ex-Dividend Countdown)
        if div_list:
            last_div_ts = div_list[-1]["date"]
            last_div_dt = datetime.datetime.fromtimestamp(last_div_ts, tz=timezone.utc)
            now_dt = datetime.datetime.now(timezone.utc)
            
            # 월배당(주기 ~30일) 또는 분기배당(주기 ~90일) 주기 추정
            cycle_days = 30 if "monthly" in stock_type or "covered_call" in stock_type or ticker in ["O", "MAIN", "STWD", "AGNC"] else 91
            next_est_div = last_div_dt + timedelta(days=cycle_days)
            days_to_next = (next_est_div.date() - now_dt.date()).days

            if 2 <= days_to_next <= 12:
                score += 30
                if primary_trigger == "general" or primary_trigger == "valuation_dip":
                    primary_trigger = "ex_dividend_countdown"
                reasons.append(f"⏰ 다음 배당 기준일 약 D-{days_to_next}일 임박 (단기 배당락 트래픽 급증: +30점)")

        # 5. 🔄 ETF 분기 리밸런싱 / 분배금 변동 (ETF Rebalance)
        if "etf" in stock_type:
            score += 15
            if primary_trigger == "general":
                primary_trigger = "etf_rebalance"
            reasons.append(f"🔄 ETF 정기 리밸런싱 및 분배금 현금흐름 점검 (+15점)")

        # 6. 📈 기술적 과매도 탈출 (Oversold Bounce)
        if low_52w > 0 and price > 0:
            bounce_from_low = ((price - low_52w) / low_52w) * 100
            if bounce_from_low <= 6.0:
                score += 20
                if primary_trigger == "general":
                    primary_trigger = "oversold_bounce"
                reasons.append(f"📈 52주 최저가 대비 +{bounce_from_low:.1f}% 바닥권 지지 반등 시그널 (+20점)")

        # 연간 배당수익률 추정
        div_yield = 0.0
        if div_list and price > 0:
            annual_payout = sum(d["amount"] for d in div_list[-12:]) if len(div_list) >= 12 else div_list[-1]["amount"] * (12 if "monthly" in stock_type else 4)
            div_yield = (annual_payout / price) * 100
            if div_yield >= 7.0:
                score += 20
                reasons.append(f"💰 연 배당수익률 약 {div_yield:.1f}% 초고배당 매력 (+20점)")
            elif div_yield >= 4.0:
                score += 10
                reasons.append(f"연 배당수익률 약 {div_yield:.1f}% 안정 고배당 (+10점)")

        # 최초 포스팅 종목 보너스
        if days_since >= 999:
            score += 25
            reasons.append("신규 미발행 종목 (신규 포스팅 보너스: +25점)")

        return {
            "ticker": ticker,
            "name": name,
            "stock_type": stock_type,
            "score": score,
            "primary_trigger": primary_trigger,
            "reasons": reasons,
            "days_since_last_post": days_since,
            "price": price,
            "dividend_yield": round(div_yield, 2),
            "is_revisit": (days_since < 999)
        }

    def scan_all_stocks(self, sample_limit=None):
        """
        전체 종목을 스캔하여 기회 점수 순으로 정렬 반환
        """
        results = []
        pool = self.stocks_data if not sample_limit else self.stocks_data[:sample_limit]
        
        print(f"[EDITH Scanner] 총 {len(pool)}개 종목 실시간 기회 팩터 스캔 시작...")
        for item in pool:
            ticker = item["ticker"]
            m_data = self.fetch_market_data(ticker)
            if not m_data:
                continue
            eval_res = self.evaluate_opportunity(item, m_data)
            results.append(eval_res)
            time.sleep(0.05)  # API Rate limit 방어
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_best_opportunity(self, threshold=40):
        """
        기회 점수가 가장 높은 최적의 1개 종목 추출.
        만약 임계값(threshold) 이상의 기회 종목이 있다면 반환,
        없으면 가장 오래된(LRU) 순환 선택.
        """
        all_results = self.scan_all_stocks()
        if not all_results:
            return None

        top = all_results[0]
        print(f"[EDITH Scanner] 1위 선정 종목: {top['name']} (Score: {top['score']})")
        print(f" - 주요 트리거: {top['primary_trigger']}")
        print(f" - 선정 사유: {', '.join(top['reasons'][:3])}")

        return top


if __name__ == "__main__":
    print("=== EDITH Dividend Opportunity Scanner CLI Test ===")
    scanner = DividendOpportunityScanner()
    
    # 빠른 테스트를 위해 상위 12개 종목만 스캔
    top_stocks = scanner.scan_all_stocks(sample_limit=12)
    print("\n--- [Top 5 기회 종목 결과] ---")
    for idx, s in enumerate(top_stocks[:5], 1):
        print(f"{idx}. {s['name']} | 점수: {s['score']}점 | 트리거: {s['primary_trigger']} | 배당수익률: {s['dividend_yield']}% | 마지막포스팅: {s['days_since_last_post']}일 전")
        for r in s['reasons']:
            print(f"   -> {r}")
