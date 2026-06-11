#!/usr/bin/env bash
# selftest.sh — 결정론 게이트 회귀 테스트 (검증의 검증, 재현 가능)
# 사용: bash selftest.sh   → 전 케이스 통과 시 "ALL PASS", 하나라도 실패 시 비0 종료
set -uo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail=0
chk() { if [ "$1" = "$2" ]; then echo "  ✓ $3"; else echo "  ✗ $3 (기대=$1 실제=$2)"; fail=1; fi; }

# 기준 설교문 (자족적 — 외부 파일 의존 제거)
cat > "$TMP/sermon.txt" <<'EOF'
본문 요한복음 10장 11절. 제목 선한 목자이신 예수님.
예수님은 자기를 선한 목자라고 소개하셨어요. 양들은 길을 잘 찾지 못해요.
목자가 풀밭으로 인도하면 가서 풀을 뜯어먹고 물가로 인도하면 가서 물을 마시는 거예요.
예수님은 우리의 가장 좋은 목자이세요. 우리를 사랑하셔서 끝까지 지켜주세요.
EOF

mk() { printf '| # | 파일명 | 장면 설명 | 설교문 대응 단락 (원문 인용) | 전달 메시지 |\n|---|---|---|---|---|\n%s\n' "$1" > "$2"; }

# 1. 정상 → PASS
mk '| 1 | 01_양.jpg | 양 | "양들은 길을 잘 찾지 못해요" | 메시지 |' "$TMP/ok.md"
st=$(python3 "$S/validate_mapping.py" "$TMP/ok.md" "$TMP/sermon.txt" | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])")
chk PASS "$st" "validate: 정상 인용"

# 2. 날조 인용 → FAIL
mk '| 1 | 01_x.jpg | x | "용이 불을 뿜으며 양을 구했어요" | 메시지 |' "$TMP/fab.md"
st=$(python3 "$S/validate_mapping.py" "$TMP/fab.md" "$TMP/sermon.txt" | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])")
chk FAIL "$st" "validate: 날조 인용 차단"

# 3. 파일명 패턴 위반 → FAIL
mk '| 1 | 1_x.jpg | x | "양들은 길을 잘 찾지 못해요" | 메시지 |' "$TMP/pat.md"
st=$(python3 "$S/validate_mapping.py" "$TMP/pat.md" "$TMP/sermon.txt" | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])")
chk FAIL "$st" "validate: 파일명 패턴 차단"

# 4. 빈 컬럼 → FAIL
mk '| 1 | 01_x.jpg | x | "양들은 길을 잘 찾지 못해요" |  |' "$TMP/empty.md"
st=$(python3 "$S/validate_mapping.py" "$TMP/empty.md" "$TMP/sermon.txt" | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])")
chk FAIL "$st" "validate: 빈 컬럼 차단"

# 5. 초단문 입력 거부
printf '짧음' > "$TMP/short.txt"
python3 "$S/extract_sermon.py" "$TMP/short.txt" "$TMP/o.txt" >/dev/null 2>&1
chk 1 "$?" "extract: 초단문 거부"

# 6. 미지원 형식 거부
touch "$TMP/x.pages"
python3 "$S/extract_sermon.py" "$TMP/x.pages" "$TMP/o.txt" >/dev/null 2>&1
chk 1 "$?" "extract: .pages 거부"

# 7. SVG <text> 차단 (qlmanage 있을 때만)
if command -v qlmanage >/dev/null && command -v sips >/dev/null; then
  printf '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1280" viewBox="0 -280 1280 1280"><rect width="1280" height="720" fill="#bfe8ff"/><text x="10" y="10">x</text></svg>' > "$TMP/t.svg"
  bash "$S/render_svg.sh" "$TMP/t.svg" "$TMP/t.jpg" >/dev/null 2>&1
  chk 1 "$?" "render: <text> 차단"
  printf '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1280" viewBox="0 -280 1280 1280"><rect width="1280" height="720" fill="#a8d878"/></svg>' > "$TMP/g.svg"
  bash "$S/render_svg.sh" "$TMP/g.svg" "$TMP/g.jpg" >/dev/null 2>&1
  chk 0 "$?" "render: 정상 SVG 1280x720"
else
  echo "  - render 테스트 스킵 (qlmanage/sips 없음)"
fi

# 8. preflight 날짜·엔진 결정론
out=$(python3 "$S/preflight.py" --title "셀프테스트" --engine svg)
eng=$(echo "$out" | python3 -c "import sys,json;print(json.load(sys.stdin)['engine'])")
chk svg "$eng" "preflight: 엔진 고정"

echo "----"
if [ "$fail" = 0 ]; then echo "ALL PASS"; else echo "SOME FAIL"; fi
exit $fail
