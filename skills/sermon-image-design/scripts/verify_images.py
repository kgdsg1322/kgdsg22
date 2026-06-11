#!/usr/bin/env python3
"""verify_images.py — 산출 이미지 결정론 검증 (V1 존재·V4 금지어·V5 규격의 기계 게이트)

검증 항목 (전부 기계 판정):
  I1 매핑표의 모든 파일이 jpg/에 실재
  I2 규격: 1280×720, JPEG 포맷 (Pillow 실측)
  I3 svg/의 모든 .svg에 <text> 태그 없음
  I4 prompts/의 모든 .md에 금지어(references/banned-terms.txt) 없음 (대소문자 무시)
사용: python3 verify_images.py <프로젝트폴더> <매핑표.md>
출력: JSON. ※ V2(신학)·V3(아동안전)·V5 시각 일관성은 LLM 검증 영역 — 본 스크립트가 대체하지 않음.
"""
import argparse, json, re, sys
from pathlib import Path


def mapping_files(md: str):
    files = []
    for line in md.splitlines():
        t = line.strip()
        if not t.startswith("|") or re.fullmatch(r"[|\s:\-]+", t):
            continue
        cells = [c.strip() for c in t.strip("|").split("|")]
        if len(cells) >= 2 and re.fullmatch(r"\d{2}_[^/\\\s]+\.jpg", cells[1]):
            files.append(cells[1])
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("mapping")
    a = ap.parse_args()

    proj = Path(a.project_dir).expanduser()
    mp = Path(a.mapping).expanduser()
    if not proj.is_dir() or not mp.exists():
        print(json.dumps({"status": "FAIL", "reason": "프로젝트 폴더 또는 매핑표 없음"}, ensure_ascii=False))
        return 1

    try:
        from PIL import Image
    except ImportError:
        print(json.dumps({"status": "FAIL", "reason": "Pillow 미설치 — pip3 install --user pillow"}, ensure_ascii=False))
        return 1

    banned_path = Path(__file__).resolve().parent.parent / "references" / "banned-terms.txt"
    banned = [w.strip() for w in banned_path.read_text(encoding="utf-8").splitlines()
              if w.strip() and not w.startswith("#")] if banned_path.exists() else []

    report = {"images": [], "svg_violations": [], "banned_hits": [], "missing_banned_list": not banned_path.exists()}

    files = mapping_files(mp.read_text(encoding="utf-8", errors="replace"))
    if not files:
        print(json.dumps({"status": "FAIL", "reason": "매핑표에서 파일명을 찾지 못함"}, ensure_ascii=False))
        return 1

    ok = True
    for f in files:
        p = proj / "jpg" / f
        item = {"file": f, "exists": p.exists(), "size_ok": False, "format_ok": False}
        if item["exists"]:
            with Image.open(p) as im:
                item["size"] = list(im.size)
                item["size_ok"] = im.size == (1280, 720)
                item["format_ok"] = im.format == "JPEG"
        if not (item["exists"] and item["size_ok"] and item["format_ok"]):
            ok = False
        report["images"].append(item)

    for svg in sorted((proj / "svg").glob("*.svg")):
        if "<text" in svg.read_text(encoding="utf-8", errors="replace"):
            report["svg_violations"].append(svg.name)
            ok = False

    for md in sorted((proj / "prompts").glob("*.md")):
        low = md.read_text(encoding="utf-8", errors="replace").lower()
        hits = [w for w in banned if w.lower() in low]
        if hits:
            report["banned_hits"].append({"file": md.name, "terms": hits})
            ok = False

    report["status"] = "PASS" if ok else "FAIL"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
