import glob
import os
import re
import urllib.request
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts_dir = os.path.join(base_dir, "_posts")
img_dest_dir = os.path.join(base_dir, "assets", "images", "posts")
os.makedirs(img_dest_dir, exist_ok=True)

# Curated high-quality Unsplash fallbacks
FALLBACK_FINANCE = [
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&auto=format&fit=crop", # Stock chart
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop", # Trading
    "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=800&auto=format&fit=crop", # Money
    "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&auto=format&fit=crop", # Coins
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&auto=format&fit=crop", # Corporate building
]

FALLBACK_TECH = [
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop", # AI Robot
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop", # Circuit board
    "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&auto=format&fit=crop", # Coding tech
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop", # Data Matrix
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop", # Global tech network
]

posts = sorted(glob.glob(os.path.join(posts_dir, "*.md")))
print(f"Total posts to process: {len(posts)}")

success_count = 0
fallback_count = 0

for i, post_path in enumerate(posts):
    filename = os.path.basename(post_path)
    slug = os.path.splitext(filename)[0]
    dest_image_name = f"{slug}.jpg"
    dest_image_path = os.path.join(img_dest_dir, dest_image_name)
    web_image_url = f"/assets/images/posts/{dest_image_name}"

    with open(post_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Determine category
    is_tech = "tech" in filename.lower() or "categories: [Tech" in content or "categories: [tech" in content

    # Get current image url
    m = re.search(r'^image:\s*"?([^"\n\r]+)"?', content, re.MULTILINE)
    current_img_url = m.group(1).strip() if m else None

    # Check if local image already exists and is valid
    if os.path.exists(dest_image_path) and os.path.getsize(dest_image_path) > 5000:
        print(f"[{i+1}/{len(posts)}] Already cached: {dest_image_name}")
    else:
        # Need to download
        download_success = False
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        # Try downloading current url first if it's an external url
        if current_img_url and current_img_url.startswith("http"):
            try:
                print(f"[{i+1}/{len(posts)}] Downloading: {current_img_url[:60]}...")
                req = urllib.request.Request(current_img_url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as response:
                    data = response.read()
                    if len(data) > 5000:
                        with open(dest_image_path, "wb") as img_file:
                            img_file.write(data)
                        download_success = True
                        success_count += 1
            except Exception as e:
                print(f"   Download failed ({e}), trying fallback...")

        # If failed or no url, use curated Unsplash fallback
        if not download_success:
            fallback_urls = FALLBACK_TECH if is_tech else FALLBACK_FINANCE
            fb_url = fallback_urls[i % len(fallback_urls)]
            try:
                print(f"[{i+1}/{len(posts)}] Downloading fallback: {fb_url[:60]}...")
                req = urllib.request.Request(fb_url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as response:
                    data = response.read()
                    with open(dest_image_path, "wb") as img_file:
                        img_file.write(data)
                    download_success = True
                    fallback_count += 1
            except Exception as e:
                print(f"   Fallback download failed: {e}")

    # Update post frontmatter to use local relative URL
    if current_img_url != web_image_url:
        if m:
            new_content = re.sub(r'^image:\s*"?([^"\n\r]+)"?', f'image: "{web_image_url}"', content, count=1, flags=re.MULTILINE)
        else:
            # Insert image frontmatter
            parts = content.split("---", 2)
            if len(parts) >= 3:
                new_content = f"---{parts[1].rstrip()}\nimage: \"{web_image_url}\"\n---{parts[2]}"
            else:
                new_content = content
        with open(post_path, "w", encoding="utf-8") as f:
            f.write(new_content)

print(f"\nDone! Successfully processed {len(posts)} posts.")
print(f"Downloaded from URL: {success_count}, Fallback used: {fallback_count}")
