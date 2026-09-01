import glob
import os
import re
import urllib.request
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts_dir = os.path.join(base_dir, "_posts")
img_dest_dir = os.path.join(base_dir, "assets", "images", "posts")
os.makedirs(img_dest_dir, exist_ok=True)

# 100% Curated Real Stock Photos from Unsplash (High Quality, Natural, Professional)
# ?w=1000&q=80&auto=format&fit=crop

SPECIFIC_TOPIC_PHOTOS = {
    # 펩시코 / 코카콜라 / 음료
    "pep": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=1000&q=80&auto=format&fit=crop", # Real soda beverage can
    "pepsico": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=1000&q=80&auto=format&fit=crop",
    "펩시": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=1000&q=80&auto=format&fit=crop",
    "coca": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=1000&q=80&auto=format&fit=crop", # Coca cola real bottle
    "콜라": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=1000&q=80&auto=format&fit=crop",
    "ko": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=1000&q=80&auto=format&fit=crop",

    # 엔비디아 / NVDY / 반도체
    "nvdy": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1000&q=80&auto=format&fit=crop", # Real GPU / Semiconductor
    "nvda": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1000&q=80&auto=format&fit=crop",
    "엔비디아": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1000&q=80&auto=format&fit=crop",
    "semiconductor": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop", # Real Circuit Board
    "반도체": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
    "microchip": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
    "texas": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
    "txn": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
    "broadcom": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",
    "qualcomm": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop",

    # 애플 / 마이크로소프트 / 테크 기업
    "apple": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000&q=80&auto=format&fit=crop", # Real Apple MacBook
    "애플": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000&q=80&auto=format&fit=crop",
    "aapl": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000&q=80&auto=format&fit=crop",
    "microsoft": "https://images.unsplash.com/photo-1583321500900-82807e458f3c?w=1000&q=80&auto=format&fit=crop",
    "msft": "https://images.unsplash.com/photo-1583321500900-82807e458f3c?w=1000&q=80&auto=format&fit=crop",
    "마이크로소프트": "https://images.unsplash.com/photo-1583321500900-82807e458f3c?w=1000&q=80&auto=format&fit=crop",
    "meta": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=1000&q=80&auto=format&fit=crop",
    "google": "https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=1000&q=80&auto=format&fit=crop",
    "naver": "https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=1000&q=80&auto=format&fit=crop",
    "samsung": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=1000&q=80&auto=format&fit=crop",
    "삼성": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=1000&q=80&auto=format&fit=crop",

    # 스타벅스 / 맥도날드 / 코스트코
    "starbucks": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&q=80&auto=format&fit=crop", # Real Coffee
    "스타벅스": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&q=80&auto=format&fit=crop",
    "sbux": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&q=80&auto=format&fit=crop",
    "mcdonald": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=1000&q=80&auto=format&fit=crop", # Real Burger
    "맥도날드": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=1000&q=80&auto=format&fit=crop",
    "costco": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=1000&q=80&auto=format&fit=crop", # Retail store
    "코스트코": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=1000&q=80&auto=format&fit=crop",

    # 제약 / 헬스케어 (JNJ, 화이자, 애비브)
    "jnj": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=1000&q=80&auto=format&fit=crop", # Medical Lab
    "존슨": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=1000&q=80&auto=format&fit=crop",
    "pfizer": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=1000&q=80&auto=format&fit=crop",
    "화이자": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=1000&q=80&auto=format&fit=crop",
    "abbv": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=1000&q=80&auto=format&fit=crop",
    "의료": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1000&q=80&auto=format&fit=crop", # Doctor with tablet
    "medical": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1000&q=80&auto=format&fit=crop",
    "hospital": "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=1000&q=80&auto=format&fit=crop",

    # 부동산 / 리츠 (Realty Income, AGNC)
    "realty": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1000&q=80&auto=format&fit=crop", # Real Modern Skyscraper
    "리얼티": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1000&q=80&auto=format&fit=crop",
    "agnc": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1000&q=80&auto=format&fit=crop",
    "realestate": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1000&q=80&auto=format&fit=crop",
    "warehouse": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1000&q=80&auto=format&fit=crop", # Warehouse logistics

    # 통신 / 네트워크 (Verizon, Cisco, Telecom)
    "verizon": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1000&q=80&auto=format&fit=crop", # Network Server / Tower
    "버라이즌": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1000&q=80&auto=format&fit=crop",
    "cisco": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1000&q=80&auto=format&fit=crop",
    "telecom": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1000&q=80&auto=format&fit=crop",

    # 금융 / 은행 / 배당주 (JPMorgan, BDC, Wall Street)
    "jpm": "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=1000&q=80&auto=format&fit=crop", # Wall Street Bank
    "제이피모건": "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=1000&q=80&auto=format&fit=crop",
    "bank": "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=1000&q=80&auto=format&fit=crop",
    "main_street": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1000&q=80&auto=format&fit=crop",
    "vanguard": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1000&q=80&auto=format&fit=crop",

    # 에너지 / 방산 (Chevron, Exxon, Lockheed)
    "chevron": "https://images.unsplash.com/photo-1516937941344-00b4e0337589?w=1000&q=80&auto=format&fit=crop", # Real Energy Plant
    "셰브론": "https://images.unsplash.com/photo-1516937941344-00b4e0337589?w=1000&q=80&auto=format&fit=crop",
    "lockheed": "https://images.unsplash.com/photo-1519074069444-1ba4fff16def?w=1000&q=80&auto=format&fit=crop", # Aircraft
    "록히드": "https://images.unsplash.com/photo-1519074069444-1ba4fff16def?w=1000&q=80&auto=format&fit=crop",

    # 테크 / AI / 코딩 / 데이터센터 / 번역 / 보안
    "data_center": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1000&q=80&auto=format&fit=crop", # Real Server Rack
    "server": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1000&q=80&auto=format&fit=crop",
    "security": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1000&q=80&auto=format&fit=crop", # Cyber Security
    "보안": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1000&q=80&auto=format&fit=crop",
    "code": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1000&q=80&auto=format&fit=crop", # Real Code Editor
    "코딩": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1000&q=80&auto=format&fit=crop",
    "개발": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1000&q=80&auto=format&fit=crop",
    "translation": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1000&q=80&auto=format&fit=crop", # Real Book & Writing desk
    "번역": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1000&q=80&auto=format&fit=crop",
    "writing": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1000&q=80&auto=format&fit=crop", # Pen and Notebook
    "cloud": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1000&q=80&auto=format&fit=crop",
    "hackathon": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1000&q=80&auto=format&fit=crop", # Collaboration
    "meeting": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1000&q=80&auto=format&fit=crop",
}

# General Natural Stock Pools (Variety for each category)
NATURAL_FINANCE_POOL = [
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1000&q=80&auto=format&fit=crop", # Stock Chart
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000&q=80&auto=format&fit=crop", # Financial Trading Screen
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1000&q=80&auto=format&fit=crop", # Glass Skyscraper
    "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1000&q=80&auto=format&fit=crop", # Financial Analytics
    "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1000&q=80&auto=format&fit=crop", # Coins / Investment
    "https://images.unsplash.com/photo-1565372195458-9de0b320ef04?w=1000&q=80&auto=format&fit=crop", # Modern Office
    "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1000&q=80&auto=format&fit=crop", # Business Meeting
    "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=1000&q=80&auto=format&fit=crop", # Dollar Currency
]

NATURAL_TECH_POOL = [
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1000&q=80&auto=format&fit=crop", # Code on screen
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=80&auto=format&fit=crop", # Real Microchip
    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1000&q=80&auto=format&fit=crop", # Server room
    "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1000&q=80&auto=format&fit=crop", # Team working with laptops
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1000&q=80&auto=format&fit=crop", # Global tech network
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1000&q=80&auto=format&fit=crop", # Matrix digital code
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1000&q=80&auto=format&fit=crop", # Modern tech office
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1000&q=80&auto=format&fit=crop", # Tech workspace
]

posts = sorted(glob.glob(os.path.join(posts_dir, "*.md")))
print(f"Total posts to process: {len(posts)}")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for i, post_path in enumerate(posts):
    filename = os.path.basename(post_path)
    slug = os.path.splitext(filename)[0]
    dest_image_name = f"{slug}.jpg"
    dest_image_path = os.path.join(img_dest_dir, dest_image_name)
    web_image_url = f"/assets/images/posts/{dest_image_name}"

    with open(post_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Search for matching topic photo
    target_photo_url = None
    content_lower = (filename + " " + content[:600]).lower()

    for keyword, photo_url in SPECIFIC_TOPIC_PHOTOS.items():
        if keyword in content_lower:
            target_photo_url = photo_url
            break

    # If no specific match, use natural category pool
    if not target_photo_url:
        is_tech = "tech" in filename.lower() or "categories: [Tech" in content or "categories: [tech" in content
        pool = NATURAL_TECH_POOL if is_tech else NATURAL_FINANCE_POOL
        target_photo_url = pool[i % len(pool)]

    # Download high-res stock photo
    try:
        req = urllib.request.Request(target_photo_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            if len(data) > 5000:
                with open(dest_image_path, "wb") as img_file:
                    img_file.write(data)
                print(f"[{i+1}/{len(posts)}] Saved natural stock photo: {dest_image_name} (from {target_photo_url[:50]}...)")
    except Exception as e:
        print(f"[{i+1}/{len(posts)}] Download failed ({e}) for {dest_image_name}")

    # Ensure frontmatter is set to local asset path
    m = re.search(r'^image:\s*"?([^"\n\r]+)"?', content, re.MULTILINE)
    if m:
        if m.group(1).strip() != web_image_url:
            new_content = re.sub(r'^image:\s*"?([^"\n\r]+)"?', f'image: "{web_image_url}"', content, count=1, flags=re.MULTILINE)
            with open(post_path, "w", encoding="utf-8") as f:
                f.write(new_content)
    else:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            new_content = f"---{parts[1].rstrip()}\nimage: \"{web_image_url}\"\n---{parts[2]}"
            with open(post_path, "w", encoding="utf-8") as f:
                f.write(new_content)

print("\nDone! All post images replaced with 100% natural, high-res Unsplash stock photos.")
