import os
import re
import sys
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError("No frontmatter found in the markdown file.")

    frontmatter_text = frontmatter_match.group(1)
    
    title_match = re.search(r'title:\s*"(.*?)"', frontmatter_text)
    title = title_match.group(1) if title_match else "No Title"

    tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter_text)
    tags = [tag.strip() for tag in tags_match.group(1).split(',')] if tags_match else []

    # Extract clean text for summary
    body = content[frontmatter_match.end():].strip()
    
    # Remove markdown formatting for a clean summary
    clean_body = re.sub(r'#+\s', '', body)
    clean_body = re.sub(r'\* TOC\n\{:toc\}', '', clean_body)
    clean_body = re.sub(r'<[^>]+>', '', clean_body)
    clean_body = re.sub(r'\[.*?\]\(.*?\)', '', clean_body)
    
    summary = clean_body[:150] + "..." if len(clean_body) > 150 else clean_body

    return {
        "title": title,
        "tags": tags,
        "summary": summary,
        "content": body
    }

def post_to_twitter(post_data, url):
    print("[Twitter] Posting to X...")
    api_key = os.environ.get("TWITTER_API_KEY")
    if not api_key:
        print("[Twitter] TWITTER_API_KEY is not set. Skipping Twitter post.")
        return False
        
    tags_str = " ".join([f"#{t}" for t in post_data['tags'][:3]])
    tweet_text = f"🆕 {post_data['title']}\n\n{post_data['summary']}\n\n자세히 보기: {url}\n{tags_str}"
    
    print(f"Would tweet: {tweet_text}")
    print("[Twitter] Posted successfully (Mock).")
    return True

def post_to_naver_blog(post_data, url):
    print("[Naver Blog] Posting to Naver...")
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("[Naver Blog] Naver API keys are not set. Skipping Naver post.")
        return False
        
    print(f"Would post to Naver Blog: {post_data['title']} - {url}")
    print("[Naver Blog] Posted successfully (Mock).")
    return True

def main():
    parser = argparse.ArgumentParser(description="Social Media Publisher")
    parser.add_argument("filepath", help="Path to the markdown post file")
    parser.add_argument("--url", default="https://yourblog.com", help="Base URL of the blog post")
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print(f"Error: File {args.filepath} not found.")
        sys.exit(1)

    try:
        post_data = parse_markdown(args.filepath)
        print(f"Parsed Post: {post_data['title']}")
        
        filename = os.path.basename(args.filepath)
        slug_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.*)\.md', filename)
        if slug_match:
            date_part, slug = slug_match.groups()
            year, month, day = date_part.split('-')
            post_url = f"{args.url}/{year}/{month}/{day}/{slug}.html"
        else:
            post_url = args.url
            
        post_to_twitter(post_data, post_url)
        post_to_naver_blog(post_data, post_url)
        
        print("Publishing sequence completed.")
        
    except Exception as e:
        print(f"Failed to publish: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
