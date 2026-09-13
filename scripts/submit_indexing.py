#!/usr/bin/env python3
"""
Autoblog Fast Indexing & Search Engine Notification Engine
- Google Sitemap Ping & IndexNow (Bing, Yandex, Naver) 실시간 핑 전송
- 최신 발행 포스트의 검색 엔진 색인(Indexing) 수집 속도 극대화
"""

import os
import sys
import glob
import re
import json
import urllib.request
import urllib.parse
import ssl
import argparse
from datetime import datetime

BASE_URL = "https://kamajyna.github.io"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
POSTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_posts")


def get_latest_post_urls(limit=5):
    posts = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")), reverse=True)
    urls = []
    for p in posts[:limit]:
        filename = os.path.basename(p)
        # 2026-09-13-auto-post-dividend-074454.md -> /dividend/finance/2026/09/13/auto-post-dividend-074454.html or date based
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.*)\.md$", filename)
        if m:
            year, month, day, slug = m.groups()
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            cat_match = re.search(r"^categories:\s*\[(.*?)\]", content, re.MULTILINE)
            cats = [c.strip().lower() for c in cat_match.group(1).split(",")] if cat_match else ["blog"]
            cat_path = "/".join(cats)
            url = f"{BASE_URL}/{cat_path}/{year}/{month}/{day}/{slug}.html"
            urls.append(url)
    return urls


def ping_google_sitemap():
    print(f"📡 [Google] Pinging sitemap update: {SITEMAP_URL}...")
    target = f"https://www.google.com/ping?sitemap={urllib.parse.quote(SITEMAP_URL)}"
    ctx = ssl._create_unverified_context()
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
    try:
        req = urllib.request.Request(target, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            print(f"✅ [Google] Sitemap Ping Successful (HTTP {resp.status})")
            return True
    except Exception as e:
        print(f"⚠️ [Google] Sitemap Ping Notice: {e}")
        return False


def ping_indexnow(urls):
    print(f"📡 [IndexNow] Submitting {len(urls)} URLs to IndexNow (Bing / Naver)...")
    endpoint = "https://api.indexnow.org/indexnow"
    ctx = ssl._create_unverified_context()
    payload = {
        "host": "kamajyna.github.io",
        "key": "kamajyna-indexnow-key",
        "urlList": urls
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (compatible; StarkAutoBlogger/1.0)"
    }
    try:
        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            print(f"✅ [IndexNow] URLs Submitted Successfully (HTTP {resp.status})")
            return True
    except Exception as e:
        print(f"ℹ️ [IndexNow] Submission Status ({e})")
        return False


def main():
    parser = argparse.ArgumentParser(description="Autoblog Indexing Ping CLI")
    parser.add_argument("--limit", type=int, default=3, help="Number of recent posts to ping")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 [STARK INDEXER] Search Engine Fast-Indexing Protocol")
    print(f"📅 Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    urls = get_latest_post_urls(limit=args.limit)
    print(f"🔗 Target URLs to Index ({len(urls)} items):")
    for u in urls:
        print(f"  - {u}")
    print("-" * 60)

    g_res = ping_google_sitemap()
    i_res = ping_indexnow(urls)

    print("=" * 60)
    print(f"🎉 Indexing Notification Cycle Completed (Google: {g_res}, IndexNow: {i_res})")
    print("=" * 60)


if __name__ == "__main__":
    main()
