import os
import datetime
from datetime import timezone, timedelta
import subprocess

KST = timezone(timedelta(hours=9))

def auto_upload_blog():
    # 블로그 레포지토리 로컬 경로 (사용자 환경에 맞게 수정 필요)
    # 현재는 스크립트가 실행되는 위치를 기준으로 잡습니다.
    repo_path = r"G:\내 드라이브\01_Projects\01_오토블로그"
    
    # 폴더가 없으면 생성 (최초 실행 시 에러 방지)
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
        print(f"[알림] {repo_path} 폴더를 생성했습니다. 이곳에 git clone 후 사용하세요.")
        # 더미 파일 하나 생성
        dummy_file = os.path.join(repo_path, "README.md")
        with open(dummy_file, "w", encoding="utf-8") as f:
            f.write("# My Auto Blog\n\n자동화 블로그 레포지토리입니다.")

    # 오늘 날짜 기반의 포스트 파일명 생성
    today = datetime.datetime.now(KST)
    post_filename = f"{today.strftime('%Y-%m-%d')}-auto-post.md"
    post_filepath = os.path.join(repo_path, post_filename)

    # 포스트 내용 작성
    post_content = f"""---
title: "자동 업로드 테스트 ({today.strftime('%Y-%m-%d')})"
date: {today.strftime('%Y-%m-%d %H:%M:%S %z')}
categories: [Update]
tags: [auto, test]
---

아폴론 봇(안티그래비티)에 의해 매일 오전 6시에 자동으로 생성되어 업로드되는 포스트입니다.
"""

    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(post_content)
    
    print(f"[성공] 블로그 포스트 파일이 생성되었습니다: {post_filepath}")

    # Git 커밋 및 푸시
    try:
        # git add
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        # git commit
        commit_msg = f"Auto blog upload: {today.strftime('%Y-%m-%d')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, check=True)
        # git push
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("[성공] GitHub Pages로 성공적으로 Push 되었습니다.")
    except Exception as e:
        print(f"[오류] Git 작업 중 에러 발생: {e}")
        print("Git이 설치되어 있고 레포지토리가 올바르게 설정(인증 포함)되었는지 확인하세요.")

if __name__ == "__main__":
    auto_upload_blog()
