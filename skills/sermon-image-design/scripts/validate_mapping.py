#!/usr/bin/env python3
"""validate_mapping.py — 매핑표 결정론 검증 (할루시네이션 구조 차단의 핵심 게이트)

검증 항목 (전부 기계 판정 — LLM 자가판단 금지):
  M1 장수 범위 1–12
  M2 파일명 패턴 ^NN_장면명.jpg$ + 01부터 연번 + 중복 없음
  M3 필수 5컬럼(#|파일명|장면 설명|설교문 대응 단락|전달 메시지) 비어 있지 않음
  M4 인용 실재성 — '설교문 대응 단락'의 인용이 설교문 원문에 실제로 존재
     (공백·따옴표·문장부호 정규화 후 부분일치, '…'로 끊은 조각은 순서대로 전부 존재해야 함)
사용: python3 validate_mapping.py <매핑표.md> <설교문.txt>
출력: JSON. status=PASS여야 generation 단계 진입 가능.
"""
import argparse, json, re, sys
from pathlib import Path

STRIP = '"\'""''「」『』·,.!?~()[]<>《》〈〉:;…⋯-—_*'


def norm(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    return s.translate(str.maketrans("", "", STRIP))


def quote_fragments(raw: str):
    frags = re.split(r"…|⋯|\.\.\.", raw)
    return [norm(f) for f in frags if len(norm(f)) >= 4]


def parse_table(md: str):
    rows = []
    for line in md.splitlines():
        t = line.strip()
        if not t.startswith("|"):
            continue
        if re.fullmatch(r"[|\s:\-]+", t):  # 구분선
            continue
        cells = [c.strip() for c in t.strip("|").split("|")]
        if cells and cells[0] in ("#", "순번"):  # 헤더
            continue
        rows.append(cells)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mapping")
    ap.add_argument("sermon")
    a = ap.parse_args()

    mp, sp = Path(a.mapping).expanduser(), Path(a.sermon).expanduser()
    for p, nm in ((mp, "매핑표"), (sp, "설교문")):
        if not p.exists():
            print(json.dumps({"status": "FAIL", "reason": f"{nm} 파일 없음: {p}"}, ensure_ascii=False))
            return 1

    sermon_norm = norm(sp.read_text(encoding="utf-8", errors="replace"))
    rows = parse_table(mp.read_text(encoding="utf-8", errors="replace"))

    issues, row_reports = [], []

    if not 1 <= len(rows) <= 12:
        issues.append(f"M1: 장수 {len(rows)} — 허용 범위 1–12 위반")

    seen = set()
    for i, cells in enumerate(rows, start=1):
        r = {"row": i, "errors": []}
        if len(cells) != 5:
            r["errors"].append(f"M3: 컬럼 {len(cells)}개 — 5개(#|파일명|장면 설명|대응 단락|메시지) 필요")
            row_reports.append(r)
            continue
        num, fname, scene, quote, msg = cells
        r["file"] = fname

        m = re.fullmatch(r"(\d{2})_[^/\\\s]+\.jpg", fname)
        if not m:
            r["errors"].append(f"M2: 파일명 '{fname}' 패턴 위반 (NN_장면명.jpg)")
        else:
            if int(m.group(1)) != i:
                r["errors"].append(f"M2: 연번 불일치 — {i}행인데 파일 번호 {m.group(1)}")
            if fname in seen:
                r["errors"].append(f"M2: 파일명 중복 '{fname}'")
            seen.add(fname)

        for label, v in (("장면 설명", scene), ("대응 단락", quote), ("전달 메시지", msg)):
            if not v:
                r["errors"].append(f"M3: '{label}' 비어 있음")

        if quote:
            frags = quote_fragments(quote)
            if not frags:
                r["errors"].append("M4: 인용이 너무 짧아 검증 불가(정규화 후 4자 미만) — 원문을 더 길게 인용할 것")
            else:
                pos = 0
                for f in frags:
                    found = sermon_norm.find(f, pos)
                    if found < 0:
                        r["errors"].append(f"M4: 인용 조각이 설교문 원문에 없음(날조 의심): '{f[:30]}…'")
                        break
                    pos = found + len(f)
        row_reports.append(r)

    bad = [r for r in row_reports if r["errors"]]
    status = "PASS" if not issues and not bad else "FAIL"
    print(json.dumps({"status": status, "scene_count": len(rows),
                      "global_issues": issues, "rows": row_reports},
                     ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
