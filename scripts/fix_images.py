import glob
import re

posts = glob.glob('_posts/*.md')
updated = 0

for filepath in posts:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    def replacer(match):
        keyword = match.group(1)
        return f"https://image.pollinations.ai/prompt/{keyword}?width=800&height=450&nologo=true"

    new_content, count = re.subn(r'https?://picsum\.photos/seed/([^/\"\s\)]+)(?:/\d+/\d+)?', replacer, content)
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated += 1

print(f"Total updated posts: {updated}")
