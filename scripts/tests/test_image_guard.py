"""
Unit Tests for Autoblog Image Download Guardrails & 404 Prevention
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import auto_blogger


class TestImageGuardrails(unittest.TestCase):
    def setUp(self):
        self.created_files = []

    def tearDown(self):
        for f in self.created_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    def test_vym_keywords_mapping(self):
        """VYM 및 배당 ETF 종목 키워드 매핑 무결성 검증"""
        sample_post = """---
layout: post
title: "VYM 배당금 분석"
date: 2026-09-13 00:00:00 +0900
categories: [Dividend]
---

본문 내용입니다."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b"X" * 6000
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            out_path = auto_blogger.save_post(sample_post, "dividend")
            self.created_files.append(out_path)
            # 이미지 파일도 등록
            base_name = os.path.basename(out_path)[:-3] + ".jpg"
            img_path = os.path.join(os.path.dirname(os.path.dirname(out_path)), "assets", "images", "posts", base_name)
            self.created_files.append(img_path)

            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                saved = f.read()

            self.assertIn('image: "/assets/images/posts/', saved)

    @patch('urllib.request.urlopen')
    def test_download_failure_falls_back_to_external_url(self, mock_urlopen):
        """다운로드 실패 시 404 로컬 경로 대신 외부 URL을 유지하여 404 방지"""
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 403, "Forbidden", {}, None)

        sample_post = """---
layout: post
title: "기술 트렌드 분석"
date: 2026-09-13 00:00:00 +0900
categories: [Tech]
image: "https://image.pollinations.ai/prompt/sample_tech_image"
---

테크 본문 내용입니다."""

        out_path = auto_blogger.save_post(sample_post, "tech")
        self.created_files.append(out_path)

        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 다운로드 실패 시 로컬 /assets/images/posts/ 경로가 아니라 외부 URL로 폴백되었는지 확인
        self.assertNotIn('/assets/images/posts/', content)
        self.assertTrue('image: "https://' in content)

    @patch('urllib.request.urlopen')
    def test_download_success_sets_local_path(self, mock_urlopen):
        """다운로드 성공 시 로컬 이미지 경로 주입 및 파일 저장 검증"""
        fake_data = b"\xff\xd8\xff\xe0" + b"A" * 6000
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_data
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        sample_post = """---
layout: post
title: "애플 실적 발표"
date: 2026-09-13 00:00:00 +0900
categories: [Tech]
---

애플 본문 내용입니다."""

        out_path = auto_blogger.save_post(sample_post, "tech")
        self.created_files.append(out_path)
        base_name = os.path.basename(out_path)[:-3] + ".jpg"
        img_path = os.path.join(os.path.dirname(os.path.dirname(out_path)), "assets", "images", "posts", base_name)
        self.created_files.append(img_path)

        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('image: "/assets/images/posts/', content)
        self.assertTrue(os.path.exists(img_path))


if __name__ == "__main__":
    unittest.main()
