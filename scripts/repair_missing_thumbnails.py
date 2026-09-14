#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autoblog Missing Thumbnail Auto-Repair Script
- _posts/ 내 모든 포스트의 대표 이미지 실존 여부 전수 검사
- 누락되거나 외부 URL로 지정된 썸네일을 Picsum 고유 시드 기반으로 자동 다운로드
- WebP 및 JPG 로컬 정적 에셋 생성 및 Frontmatter 경로 완벽 동기화
"""

import os
import sys
import glob
import re
import hashlib
import urllib.request
import ssl

ctx = ssl._create_unverified_context()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(BASE_DIR, "_posts")
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images", "posts")
os.makedirs(IMAGES_DIR, exist_ok=True)

posts = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")), reverse=True)
repaired = 0

print(f"=== 🛠️ 오토블로그 썸네일 누락 전수 검사 및 복구 시작 (총 {len(posts)}개 포스트) ===")

for p_path in posts:
    fname = os.path.basename(p_path)
    with open(p_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", content, re.DOTALL)
    if not fm_match:
        continue

    fm_text, body = fm_match.group(1), fm_match.group(2)
    img_match = re.search(r'^image:\s*"([^"]*)"', fm_text, re.MULTILINE)

    base_slug = fname[:-3]
    target_jpg_name = f"{base_slug}.jpg"
    target_webp_name = f"{base_slug}.webp"
    
    jpg_path = os.path.join(IMAGES_DIR, target_jpg_name)
    webp_path = os.path.join(IMAGES_DIR, target_webp_name)

    needs_repair = False
    target_ext = "webp"

    if not img_match:
        needs_repair = True
    else:
        c_val = img_match.group(1).strip()
        if c_val.startswith("http"):
            needs_repair = True
        elif c_val.endswith(".webp"):
            target_ext = "webp"
            if not os.path.exists(webp_path):
                needs_repair = True
        elif c_val.endswith(".jpg") or c_val.endswith(".jpeg"):
            target_ext = "jpg"
            if not os.path.exists(jpg_path):
                needs_repair = True
        else:
            needs_repair = True

    if needs_repair:
        print(f"🔧 복구 대상 포착: {fname}")
        seed = hashlib.md5(fname.encode("utf-8")).hexdigest()[:8]
        p_urls = [
            f"https://picsum.photos/seed/{seed}/800/450",
            f"https://picsum.photos/800/450?random={seed}"
        ]

        img_bytes = None
        for p_url in p_urls:
            try:
                print(f"  다운로드 시도: {p_url}")
                req = urllib.request.Request(p_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                    b = resp.read()
                    if len(b) > 5000:
                        img_bytes = b
                        break
            except Exception as e:
                print(f"  다운로드 재시도 중 ({e})...")

        if img_bytes:
            try:
                from PIL import Image as PILImage
                import io
                img = PILImage.open(io.BytesIO(img_bytes)).convert("RGB")
                img.save(webp_path, "WEBP", quality=85, method=6)
                with open(jpg_path, "wb") as f_jpg:
                    f_jpg.write(img_bytes)
                final_web_url = f"/assets/images/posts/{target_webp_name}" if target_ext == "webp" else f"/assets/images/posts/{target_jpg_name}"
                print(f"  ✅ WebP & JPG 에셋 동시 생성 완료 ({len(img_bytes)} bytes)")
            except Exception:
                with open(jpg_path, "wb") as f_jpg:
                    f_jpg.write(img_bytes)
                final_web_url = f"/assets/images/posts/{target_jpg_name}"
                print(f"  ✅ 로컬 JPG 에셋 생성 완료 ({len(img_bytes)} bytes)")

            if "image:" in fm_text:
                fm_text = re.sub(r'^[ \t]*image:[^\n]*$', f'image: "{final_web_url}"', fm_text, flags=re.MULTILINE)
            else:
                fm_text += f'\nimage: "{final_web_url}"'

            new_content = f"---\n{fm_text.strip()}\n---\n\n{body.strip()}\n"
            with open(p_path, "w", encoding="utf-8") as f_out:
                f_out.write(new_content)

            print(f"  ✅ Frontmatter image 필드 갱신: {final_web_url}")
            repaired += 1
        else:
            print(f"  ❌ 에셋 다운로드 최종 실패: {fname}")

print(f"\n🎉 총 {repaired}개 누락 포스트 썸네일 복구 완료!")
