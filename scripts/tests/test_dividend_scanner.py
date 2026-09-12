"""
Unit Tests for EDITH Multi-Factor Dividend Opportunity Scanner
"""

import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

# 상위 경로 임포트 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dividend_opportunity_scanner import DividendOpportunityScanner, DEFAULT_DIVIDEND_STOCKS
from auto_blogger import get_topic_by_category

class TestDividendOpportunityScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = DividendOpportunityScanner()

    def test_default_stocks_validity(self):
        """기본 종목 풀 무결성 검증"""
        self.assertGreaterEqual(len(DEFAULT_DIVIDEND_STOCKS), 20)
        for s in DEFAULT_DIVIDEND_STOCKS:
            self.assertIn("ticker", s)
            self.assertIn("name", s)
            self.assertIn("keywords", s)
            self.assertIn("type", s)

    def test_market_data_fetching(self):
        """대표 배당주(O) 실시간 시장 데이터 수집 검증"""
        data = self.scanner.fetch_market_data("O")
        self.assertIsNotNone(data)
        self.assertIn("price", data)
        self.assertGreater(data["price"], 0)
        self.assertIn("dividends", data)
        self.assertGreaterEqual(len(data["dividends"]), 1)

    def test_scoring_dividend_hike(self):
        """배당금 인상 시 가산점(+35점) 및 트리거 감지 검증"""
        mock_stock = {"ticker": "TEST", "name": "테스트주", "keywords": ["테스트"], "type": "dividend_growth"}
        mock_market = {
            "price": 100.0,
            "high_52w": 100.0,
            "low_52w": 80.0,
            "dividends": [
                {"amount": 1.0, "date": 1700000000},
                {"amount": 1.1, "date": 1705000000} # +10% 인상
            ]
        }
        res = self.scanner.evaluate_opportunity(mock_stock, mock_market)
        self.assertGreaterEqual(res["score"], 35)
        self.assertEqual(res["primary_trigger"], "dividend_hike")

    def test_scoring_valuation_dip(self):
        """52주 고점 대비 -20% 이상 하락 시 저평가 가산점(+25점) 검증"""
        mock_stock = {"ticker": "TEST", "name": "테스트주", "keywords": ["테스트"], "type": "dividend_growth"}
        mock_market = {
            "price": 75.0,
            "high_52w": 100.0, # -25% 하락
            "low_52w": 70.0,
            "dividends": [
                {"amount": 1.0, "date": 1700000000},
                {"amount": 1.0, "date": 1705000000}
            ]
        }
        res = self.scanner.evaluate_opportunity(mock_stock, mock_market)
        self.assertGreaterEqual(res["score"], 25)
        self.assertIn("저평가", "".join(res["reasons"]))

    def test_cooldown_penalty(self):
        """최근 14일 이내 포스팅 시 쿨다운 감점(-50점) 검증"""
        mock_stock = {"ticker": "KO", "name": "코카콜라 (KO)", "keywords": ["코카콜라"], "type": "dividend_growth"}
        # 임의로 최근 포스팅 일자를 오늘로 주입
        self.scanner.last_posted_dates["KO"] = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
        mock_market = {
            "price": 60.0,
            "high_52w": 65.0,
            "low_52w": 55.0,
            "dividends": [{"amount": 0.485, "date": 1700000000}]
        }
        res = self.scanner.evaluate_opportunity(mock_stock, mock_market)
        self.assertIn("쿨다운 적용: -50점", "".join(res["reasons"]))

if __name__ == "__main__":
    unittest.main()
