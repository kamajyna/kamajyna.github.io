import glob
import re

posts = glob.glob('_posts/*.md')
missing_image = []

for p in posts:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if image frontmatter exists
    m = re.search(r'^image:\s*"?([^"\n\r]+)"?', content, re.MULTILINE)
    if not m or not m.group(1).strip():
        # Get title
        t = re.search(r'^title:\s*"?([^"\n\r]+)"?', content, re.MULTILINE)
        title = t.group(1) if t else "No title"
        missing_image.append((p, title))

print(f"Total posts checked: {len(posts)}")
print(f"Missing image posts count: {len(missing_image)}")
for p, title in missing_image:
    print(f" - {p}: {title}")
