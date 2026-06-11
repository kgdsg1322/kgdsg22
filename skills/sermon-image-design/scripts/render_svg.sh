#!/usr/bin/env bash
# render_svg.sh — SVG→JPG 결정론 렌더 (명령 수기 입력 금지, 이 스크립트만 사용)
# 정사각(1280×1280) 캔버스 → 중앙 1280×720 크롭 → JPEG 92 — qlmanage 정사각 버그 해결책 내장
# 사용: bash render_svg.sh <입력.svg> <출력.jpg>
set -euo pipefail

svg="$1"; out="$2"
[ -f "$svg" ] || { echo "FAIL: SVG 없음: $svg"; exit 1; }

# 텍스트 제로 규칙 — <text> 태그 사전 차단
if grep -q "<text" "$svg"; then
  echo "FAIL: SVG에 <text> 태그 존재 — 이미지 내 텍스트 절대 금지 규칙 위반"
  exit 1
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

qlmanage -t -s 1280 -o "$tmpdir" "$svg" >/dev/null 2>&1
png="$tmpdir/$(basename "$svg").png"
[ -f "$png" ] || { echo "FAIL: qlmanage 렌더 실패 ($svg)"; exit 1; }

sips -c 720 1280 "$png" >/dev/null
mkdir -p "$(dirname "$out")"
sips -s format jpeg -s formatOptions 92 "$png" --out "$out" >/dev/null

# 산출 규격 실측 검증
w="$(sips -g pixelWidth  "$out" | awk '/pixelWidth/{print $2}')"
h="$(sips -g pixelHeight "$out" | awk '/pixelHeight/{print $2}')"
f="$(sips -g format      "$out" | awk '/format:/{print $2}')"
if [ "$w" = "1280" ] && [ "$h" = "720" ] && [ "$f" = "jpeg" ]; then
  echo "OK: $out (1280x720 jpeg)"
else
  echo "FAIL: 규격 불일치 — ${w}x${h} ${f} (기대 1280x720 jpeg)"
  exit 1
fi
