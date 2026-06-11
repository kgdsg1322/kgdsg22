#!/usr/bin/env python3
"""build_motion.py — Ken Burns 모션 mp4 결정론 생성 (ffmpeg zoompan + xfade, 무음)

장면별 클립(기본 15초, 아주 느린 줌 0.0008/frame) → clips/NN.mp4
→ 1초 크로스페이드로 통합 <제목>_모션.mp4. BGM 없음(설계 합의).
사용: python3 build_motion.py <프로젝트폴더> <매핑표.md> --title <제목> [--sec 15]
출력: JSON. ffmpeg 없으면 status=SKIP(exit 2) — 전체 실패 금지 원칙.
"""
import argparse, json, re, shutil, subprocess, sys
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


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration(path: Path) -> float:
    r = run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("mapping")
    ap.add_argument("--title", required=True)
    ap.add_argument("--sec", type=int, default=15)
    a = ap.parse_args()

    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print(json.dumps({"status": "SKIP", "reason": "ffmpeg/ffprobe 없음 — brew install ffmpeg 후 재실행. mp4만 스킵하고 나머지 산출 계속."}, ensure_ascii=False))
        return 2

    proj = Path(a.project_dir).expanduser()
    files = mapping_files(Path(a.mapping).expanduser().read_text(encoding="utf-8", errors="replace"))
    if not files:
        print(json.dumps({"status": "FAIL", "reason": "매핑표에서 장면 행을 찾지 못함"}, ensure_ascii=False))
        return 1

    clips_dir = proj / "clips"
    clips_dir.mkdir(exist_ok=True)
    sec, fps = a.sec, 25
    frames = sec * fps
    clips, clip_reports = [], []

    for i, f in enumerate(files, start=1):
        img = proj / "jpg" / f
        if not img.exists():
            print(json.dumps({"status": "FAIL", "reason": f"이미지 누락: {f}"}, ensure_ascii=False))
            return 1
        out = clips_dir / f"{i:02d}.mp4"
        # 줌인/줌아웃 교차 — 미취학 어지러움 방지용 저속(0.0008/frame)
        if i % 2 == 1:
            z = "min(zoom+0.0008,1.3)"
        else:
            z = f"if(eq(on,1),1.3,max(zoom-0.0008,1.0))"
        vf = (f"scale=2560:-2,zoompan=z='{z}'"
              f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s=1280x720:fps={fps}")
        r = run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-frames:v", str(frames),
                 "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(out)])
        if r.returncode != 0 or not out.exists():
            print(json.dumps({"status": "FAIL", "reason": f"클립 생성 실패 {f}",
                              "stderr": r.stderr[-400:]}, ensure_ascii=False))
            return 1
        d = duration(out)
        clip_reports.append({"clip": out.name, "sec": round(d, 2),
                             "ok": abs(d - sec) <= 1.0})
        clips.append(out)

    final = proj / f"{a.title}_모션.mp4"
    if len(clips) == 1:
        shutil.copy(clips[0], final)
    else:
        xfade_sec = 1
        inputs = []
        for c in clips:
            inputs += ["-i", str(c)]
        filters, prev = [], "0:v"
        offset = 0
        for k in range(1, len(clips)):
            offset += sec - xfade_sec
            label = f"v{k}"
            filters.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={xfade_sec}:offset={offset}[{label}]")
            prev = label
        r = run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
                 "-map", f"[{prev}]", "-c:v", "libx264", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p", str(final)])
        if r.returncode != 0 or not final.exists():
            print(json.dumps({"status": "FAIL", "reason": "통합본 xfade 실패",
                              "stderr": r.stderr[-400:]}, ensure_ascii=False))
            return 1

    expected_total = sec * len(clips) - (len(clips) - 1) * 1
    total = duration(final)
    ok = all(c["ok"] for c in clip_reports) and abs(total - expected_total) <= 2.0
    print(json.dumps({"status": "OK" if ok else "FAIL",
                      "final": str(final), "total_sec": round(total, 2),
                      "expected_sec": expected_total, "clips": clip_reports},
                     ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
