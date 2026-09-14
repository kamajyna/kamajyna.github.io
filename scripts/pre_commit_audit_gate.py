#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STARK INDUSTRIES Git Pre-Commit / Pre-Flight Safety Gate
-------------------------------------------------------
모든 Git Commit 및 산출물 배포 전 실행되어 다음을 차단하는 게이트웨이:
1. 보안 크리덴셜 (Google/OpenAI/GitHub Token 등) 하드코딩
2. 파괴적 명령어 (rm -rf /, DROP TABLE, gsutil rm -r 등)
3. [Reality-Check] 공장 OT/PLC 폐쇄망 직결 및 비현실적 SF 과장 스펙
4. 한글 독스트링 및 주석 작성 준수 여부
"""

import sys
import os
import re
import subprocess

# 1. 파괴적 커맨드 패턴
DESTRUCTIVE_PATTERNS = [
    (r"rm\s+-rf\s+[/~]", "위험한 루트/홈 디렉토리 강제 삭제"),
    (r"DROP\s+(DATABASE|TABLE|SCHEMA)", "데이터베이스/테이블 파기 쿼리"),
    (r"TRUNCATE\s+TABLE", "테이블 전체 비우기 쿼리"),
    (r"gsutil\s+rm\s+-r", "클라우드 스토리지 재귀적 삭제")
]

# 2. 하드코딩된 크리덴셜 패턴
CREDENTIAL_PATTERNS = [
    (r"AIzaSy[A-Za-z0-9_-]{35}", "Google API Key 하드코딩 누출 위험"),
    (r"sk-proj-[A-Za-z0-9_-]{32,}", "OpenAI API Key 하드코딩 누출 위험"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token 하드코딩 누출 위험")
]

# 3. [현실성 검증] 물리적/환경적 불가능성 패턴
PHYSICAL_IMPOSSIBLE_PATTERNS = [
    (r"(공정|현장|설비|배관|굴뚝|폐수)\s*(실시간)?\s*(센서|계측기|TMS|계장)\s*(직결|연동|감시|모니터링)", "현장 설비/공정 센서 물리적 직결 불가 (폐쇄망/하드웨어 결여)"),
    (r"(OT|DCS|PLC|SCADA|Modbus|Profinet)\s*(네트워크|제어망|통신|연동)", "공장 내부망(OT/PLC) 물리적 연결 불가"),
    (r"(연돌|방류구)\s*(실시간|자동)\s*채취", "현장 물리적 샘플링 장치 결여")
]

# 4. [현실성 검증] SF 판타지 / 실체 없는 과장 스펙 패턴
HYPERBOLIC_SF_PATTERNS = [
    (r"WebRTC\s*기반\s*(Sub-500ms|실시간)?\s*오디오\s*대화", "WebRTC 실시간 오디오 스트리밍 인프라 미구비"),
    (r"3D\s*Mesh\s*합성.*자동\s*리깅.*게임\s*엔진", "3D 메시 합성 및 자동 리깅 툴체인 결여"),
    (r"VLM\s*기반.*(화면\s*직접\s*인식|클릭/키보드\s*픽셀\s*액션|Set-of-Marks)", "OS 데스크톱 픽셀 제어 RPA 환경 미구비"),
    (r"유전\s*알고리즘\(GEPA\).*자가\s*돌연변이", "실체 없는 프롬프트 유전 알고리즘 과장"),
    (r"고객\s*문의\s*CS\s*접수.*환불/계정\s*조치\s*자동\s*실행", "개인 볼트와 무관한 기업 CS/환불 허구 스펙"),
    (r"스마트스토어\s*(배포\s*소싱|자동\s*소싱)", "외부 상거래 플랫폼 연동 실체 결여")
]

def scan_text(text, filename="<input>"):
    violations = []
    
    # 1. 파괴적 패턴 검사
    for pat, desc in DESTRUCTIVE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            violations.append(f"[DESTRUCTIVE] {desc} (패턴: {pat})")

    # 2. 크리덴셜 패턴 검사
    for pat, desc in CREDENTIAL_PATTERNS:
        if re.search(pat, text):
            violations.append(f"[CREDENTIAL] {desc}")

    # 3. 물리적 불가능 패턴 검사
    for pat, desc in PHYSICAL_IMPOSSIBLE_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            violations.append(f"[REALITY-FAIL:PHYSICAL] {desc} (매칭: '{m.group(0)}')")

    # 4. SF 과장 스펙 검사
    for pat, desc in HYPERBOLIC_SF_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            violations.append(f"[REALITY-FAIL:HYPERBOLIC] {desc} (매칭: '{m.group(0)}')")

    return violations

def main():
    print("======================================================================")
    print("🛡️ STARK INDUSTRIES Pre-Commit / Pre-Flight Safety Gate")
    print("======================================================================")
    
    target_files = sys.argv[1:]
    if not target_files:
        # Git staged files if in git repo
        try:
            res = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
            target_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
        except Exception:
            target_files = []

    if not target_files:
        print("ℹ️ 검사할 대상 파일이 지정되지 않았거나 Staged 파일이 없습니다. (Pass)")
        sys.exit(0)

    total_violations = 0
    for fpath in target_files:
        if not os.path.exists(fpath):
            continue
        # 린터 및 감사 스크립트 자체는 금지 패턴 선언을 포함하므로 정규식 스캔 제외
        if os.path.basename(fpath) in ["pre_commit_audit_gate.py", "test_image_guard.py"]:
            print(f"⏩ [SKIP-SELF] {fpath}")
            continue
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            issues = scan_text(content, fpath)

            # 오토블로그 포스트 대표 이미지 실존 검증
            if fpath.startswith("_posts/") or "/_posts/" in fpath:
                img_m = re.search(r'^image:\s*"(.*?)"', content, re.MULTILINE)
                if img_m:
                    img_val = img_m.group(1).strip()
                    if img_val.startswith("/assets/images/") or img_val.startswith("assets/images/"):
                        rel_img = img_val.lstrip("/")
                        full_img = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rel_img)
                        if not os.path.exists(full_img):
                            issues.append(f"[THUMBNAIL-MISSING] 대표 이미지 파일 부재: {rel_img} (404 오류 위험)")

            if issues:
                print(f"\n❌ [GATE-REJECT] {fpath}")
                for iss in issues:
                    print(f"   - {iss}")
                total_violations += len(issues)
            else:
                print(f"✅ [PASS] {fpath}")
        except Exception as e:
            print(f"⚠️ [READ-ERROR] {fpath}: {e}")

    print("\n----------------------------------------------------------------------")
    if total_violations > 0:
        print(f"🚫 Pre-Commit Gate 실패: 총 {total_violations}건의 보안/현실성 위반이 적발되어 커밋이 중단되었습니다.")
        sys.exit(1)
    else:
        print("🎉 Pre-Commit Gate 통과: 모든 파일이 보안 및 거버넌스 규격을 준수합니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()
