# SVG 심볼 템플릿 — 폴백 경로용 (검증된 실전 패턴)

> 출처: 실제 승인 산출물(2026-06 유아부 4장)에서 추출한 검증된 패턴.
> 핵심 원리: `<defs>`에 심볼을 한 번 정의하고 `<use>`로 전 장면 재사용 → 캐릭터 일관성 100% 보장.

## 캔버스 규약 (qlmanage 정사각 버그 해결책 내장)

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1280" viewBox="0 -280 1280 1280">
```
- qlmanage는 16:9 SVG를 1280×1280에 맞춰 확대해 우측이 잘린다 →
  **캔버스를 1280×1280 정사각으로 작성**하고 viewBox 상단 패딩(-280)에 하늘을 연장.
- 본 장면은 y=0~720 영역에 그린다. 렌더 후 `sips -c 720 1280`으로 중앙 크롭.

## 렌더 명령 (장당)

```bash
qlmanage -t -s 1280 -o . NN_장면명.svg
sips -c 720 1280 NN_장면명.svg.png
sips -s format jpeg -s formatOptions 92 NN_장면명.svg.png --out ../jpg/NN_장면명.jpg
rm NN_장면명.svg.png
```

## 공통 배경 그라데이션

```xml
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#bfe8ff"/>
  <stop offset="60%" stop-color="#e7f6ff"/>
  <stop offset="100%" stop-color="#fff7e6"/>
</linearGradient>
<radialGradient id="sun" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="#fff6c4"/>
  <stop offset="70%" stop-color="#ffe27a"/>
  <stop offset="100%" stop-color="#ffd84d"/>
</radialGradient>
```

## 검증된 캐릭터 심볼 — 양 (구름형 몸통 + 점 눈 + 홍조 볼)

```xml
<g id="sheep">
  <rect x="-22" y="34" width="11" height="34" rx="5" fill="#5a5550"/>
  <rect x="11" y="34" width="11" height="34" rx="5" fill="#5a5550"/>
  <g fill="#ffffff" stroke="#e9e4da" stroke-width="3">
    <circle cx="-30" cy="6" r="26"/><circle cx="-6" cy="-14" r="28"/>
    <circle cx="24" cy="-8" r="26"/><circle cx="34" cy="16" r="22"/>
    <circle cx="8" cy="26" r="26"/><circle cx="-22" cy="26" r="23"/>
    <circle cx="2" cy="2" r="30"/>
  </g>
  <g>
    <ellipse cx="42" cy="6" rx="22" ry="24" fill="#6b6661"/>
    <ellipse cx="33" cy="-12" rx="8" ry="13" fill="#5a5550"/>
    <ellipse cx="55" cy="-10" rx="8" ry="13" fill="#5a5550"/>
    <circle cx="42" cy="-8" r="13" fill="#ffffff"/>
    <circle cx="36" cy="6" r="4.5" fill="#2b2723"/>
    <circle cx="50" cy="6" r="4.5" fill="#2b2723"/>
    <circle cx="37.5" cy="4.5" r="1.6" fill="#fff"/>
    <circle cx="51.5" cy="4.5" r="1.6" fill="#fff"/>
    <circle cx="30" cy="16" r="5" fill="#ffb3bf" opacity="0.8"/>
    <circle cx="56" cy="16" r="5" fill="#ffb3bf" opacity="0.8"/>
    <path d="M40 18 q4 4 8 0" stroke="#2b2723" stroke-width="2.2" fill="none" stroke-linecap="round"/>
  </g>
</g>
```

배치: `<use href="#sheep" transform="translate(640,520) scale(1.2)"/>` — scale·translate만 바꿔 무한 재사용.

## 인물 심볼 설계 규칙 (예수님·아이 등)

- 머리 반지름 ≈ 몸통 높이 (치비 비율). 점 눈 4–5px + 흰 하이라이트 1.5px + 홍조 볼 5px(`#ffb3bf` 80%).
- 예수님: 따뜻한 크림 옷(`#fff3df`) + 갈색 머리, **항상 미소·열린 팔**. 전 장면 동일 심볼 사용.
- 새 장면마다 심볼을 다시 그리지 말 것 — 1번 이미지의 `<defs>`를 표준으로 복사해 시리즈 전체에 사용.

## 장면 구성 체크

- 레이어 순서: 하늘 → 원경(언덕) → 해/구름 → 중경(나무·집) → 주인공 → 근경 소품.
- 요소 3–5개 유지. 텍스트 요소(`<text>`) 사용 절대 금지.
