#!/usr/bin/env python3
"""preflight.py — 결정론 사전점검·프로젝트 폴더 생성 (LLM 추론 금지 영역)

담당: 날짜 계산 / 엔진 탐지 / 의존성 점검 / 서브 스킬 존재 검증 / 폴더 생성.
사용: python3 preflight.py --title <설교제목> [--engine auto|gemini|openai|svg]
출력: JSON (stdout)
"""
import argparse, importlib.util, json, os, re, shutil, sys, time
from pathlib import Path

SUBSKILLS = [
    "sermon-image-design-scene-planning",
    "sermon-image-design-generation",
    "sermon-image-design-verification",
    "sermon-image-design-packaging",
]


def find_skills_root() -> Path:
    """이 스크립트 위치 기준(skills/<master>/scripts/) → skills 루트.
    symlink 설치(~/.claude/skills)와 저장소 직접 실행 모두 지원."""
    here = Path(__file__).resolve().parent          # .../sermon-image-design/scripts
    candidates = [here.parent.parent]               # 저장소 skills/
    candidates.append(Path.home() / ".claude" / "skills")
    for c in candidates:
        if all((c / s / "SKILL.md").exists() for s in SUBSKILLS):
            return c
    return candidates[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True, help="설교 제목 (폴더명에 사용)")
    ap.add_argument("--engine", default="auto", choices=["auto", "gemini", "openai", "svg"])
    a = ap.parse_args()

    title = re.sub(r'[/\\:*?"<>|\s]+', "_", a.title.strip()).strip("_")
    if not title:
        print(json.dumps({"status": "FAIL", "reason": "제목이 비어 있음"}, ensure_ascii=False))
        return 1

    date6 = time.strftime("%y%m%d")
    now_hm = time.strftime("%H:%M")

    engine = a.engine
    if engine == "auto":
        if os.environ.get("GEMINI_API_KEY"):
            engine = "gemini"
        elif os.environ.get("OPENAI_API_KEY"):
            engine = "openai"
        else:
            engine = "svg"

    deps = {
        "qlmanage": bool(shutil.which("qlmanage")),
        "sips": bool(shutil.which("sips")),
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "python-pptx": importlib.util.find_spec("pptx") is not None,
        "pymupdf": importlib.util.find_spec("fitz") is not None,
        "python-docx": importlib.util.find_spec("docx") is not None,
        "pillow": importlib.util.find_spec("PIL") is not None,
    }

    root = find_skills_root()
    subskills = {s: (root / s / "SKILL.md").exists() for s in SUBSKILLS}

    project = Path.home() / "Desktop" / "Agent" / f"{date6}_{title}_유아부"
    for sub in ["jpg", "prompts", "svg", "clips"]:
        (project / sub).mkdir(parents=True, exist_ok=True)

    blockers = []
    if engine == "svg" and not (deps["qlmanage"] and deps["sips"]):
        blockers.append("SVG 폴백에 필요한 qlmanage/sips 없음 (macOS 전용)")
    missing_sub = [s for s, ok in subskills.items() if not ok]
    if missing_sub:
        blockers.append(f"서브 스킬 누락: {missing_sub}")

    out = {
        "status": "FAIL" if blockers else "OK",
        "blockers": blockers,
        "date": date6,
        "now": now_hm,
        "engine": engine,
        "project_dir": str(project),
        "skills_root": str(root),
        "scripts_dir": str(Path(__file__).resolve().parent),
        "subskills": subskills,
        "deps": deps,
        "notes": {
            "mp4": "ffmpeg 없으면 packaging이 설치 시도 후, 실패 시 mp4만 스킵",
            "pptx": "python-pptx 없으면 packaging이 설치 시도 후, 실패 시 PPTX만 스킵",
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    sys.exit(main())
