# 화풍 속성 기술서 — 미취학(1–7세) 표준

> 프롬프트·SVG 작성 시 이 속성만으로 화풍을 기술한다.
> ⛔ 출판물·작가·브랜드 고유명사는 어떤 경우에도 프롬프트에 넣지 않는다 (저작권 안전).

## 색 (Palette)

| 역할 | 색 | hex 기준값 |
|------|----|-----------|
| 도미넌트 | 따뜻한 노랑·주황 | `#ffd84d` `#ffb347` |
| 하늘 | 연한 하늘색 → 크림 그라데이션 | `#bfe8ff` → `#fff7e6` |
| 자연 | 부드러운 연두·초록 | `#a8d878` `#7fc060` |
| 포인트 | 파스텔 분홍(볼터치)·살구 | `#ffb3bf` `#ffd9b3` |
| 윤곽·눈 | 따뜻한 짙은 갈색 (순흑 금지) | `#2b2723` |

- 채도는 파스텔~중간. 형광·네온·어두운 무채색 금지.
- 밤·어둠 장면도 보라·남색 파스텔 + 따뜻한 광원(별·등불)으로 처리.

## 형태 (Shape)

- **치비 비율**: 머리:몸 ≈ 1:1~1:1.5 (큰 머리·작은 몸).
- **점 눈** + 흰 하이라이트, **홍조 볼**(파스텔 분홍 원), 단순 곡선 미소.
- 모든 윤곽은 둥글게 — 뾰족한 모서리·날카로운 형태 금지.
- 동물은 의인화된 순한 표정 (양=구름형 몸통, 새=동그란 몸).

## 질감·렌더 (Texture)

- 종이 콜라주/크레용 질감의 **플랫 일러스트**, 부드러운 단순 음영(셀 셰이딩 1단계 이하).
- 사실적 렌더·3D·포토리얼 금지. 굵고 부드러운 외곽선 허용.

## 구성 (Composition)

- 화면 요소 **3–5개** (주인공 1 + 배경 1–2 + 소품 0–2). 정보 과밀 금지.
- 한 화면 = 한 메시지. 주인공은 화면 중앙~황금비 위치, 크게.
- **이미지 내 텍스트 절대 없음** (글자·숫자·기호 모두).
- 시선 높이는 어린이 눈높이(낮은 카메라), 인물은 항상 정면~3/4 각도의 친근한 포즈.

## 정서 안전 (1–7세)

- 금지: 공포 유발 표정·어둠 속 고립·피·무기 강조·울부짖는 얼굴·괴물형 묘사.
- 위험 장면(폭풍·골리앗 등)은 **밝고 안정된 주인공** 중심으로: 두려움보다 보호·용기가 읽히게.
- 예수님은 항상 따뜻한 미소·열린 팔. 하나님의 임재는 빛·따뜻한 광선으로.

## AI 프롬프트 고정 블록 (영문, 전 장면 공통 앞부분)

```
Children's picture-book flat illustration for ages 1-7, warm pastel palette
(soft yellow #ffd84d, sky blue #bfe8ff, fresh green #a8d878), chibi proportions
with big heads and small bodies, dot eyes with white highlights, rosy blush cheeks,
gentle smiles, rounded shapes only, paper-collage / crayon texture, simple soft
shading, 3-5 elements per scene, bright and cozy mood, absolutely no text or
letters in the image, no scary or dark elements. 16:9 composition.
```

뒤에 캐릭터 고정 문구(캐릭터 명단 기반)와 장면 묘사를 잇는다.
