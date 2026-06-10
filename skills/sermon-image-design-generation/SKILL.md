---
name: sermon-image-design-generation
disable-model-invocation: true
description: [TLDR] sermon-image-design(마스터)의 2번 하위 스킬. scene-planning의 매핑표를 받아 이미지를 실제로 생성한다. 하이브리드 엔진 — ①GEMINI_API_KEY 탐지 시 Gemini 이미지 API(캐릭터 레퍼런스로 일관성) ②OPENAI_API_KEY 탐지 시 gpt-image 계열(edits 레퍼런스 입력) ③둘 다 없거나 실패 시 SVG 코드 직접 작성 → qlmanage/sips 렌더(비용 0, 키 불필요) 폴백. 산출: 1280×720 JPG(텍스트 없는 순수 그림) + 장당 프롬프트 기록. [Triggers] 마스터 스킬이 실행 사이클 3단계에서 Read로 로드하여 실행한다. 단독 자동 발동 금지 (disable-model-invocation). verification FAIL 시 수정 지시서를 받아 해당 이미지만 재생성한다. [Methodology] ①엔진 자동 탐지(환경변수 → API 모델 목록 실측 확인 후 사용, 모델명 하드코딩 단정 금지) ②화풍 고정 블록 구성(references/style-attributes.md — 난색 파스텔·치비 비율·둥근 형태·콜라주 질감, 출판물 고유명사 사용 절대 금지) ③1번 이미지를 스타일 앵커로 먼저 생성·확정 ④AI 경로: 캐릭터 시트 생성 후 전 장면에 레퍼런스 재투입 / SVG 경로: defs 심볼 재사용(references/svg-symbol-templates.md, qlmanage 정사각 렌더 버그 해결책 내장) ⑤전량 1280×720 JPG 변환, NN_장면명.jpg 명명, prompts/ 기록.
---

# Generation — 이미지 생성 (하위 스킬 2/4)

> 호출 주체: `sermon-image-design` 마스터. 입력: 매핑표 초안(+재생성 시 verification 수정 지시서).

## 임무

매핑표의 모든 장면을 **일관된 화풍의 1280×720 JPG**로 만든다. 이미지 안에 글자는 넣지 않는다(순수 그림).

## 1. 엔진 자동 탐지

```bash
# 우선순위: Gemini → OpenAI → SVG 폴백
[ -n "$GEMINI_API_KEY" ] && echo "GEMINI"
[ -n "$OPENAI_API_KEY" ] && echo "OPENAI"
```

| 경로 | 방법 | 일관성 전략 |
|------|------|-------------|
| A. Gemini | 이미지 생성 API (Gemini 3 Pro Image 계열) | 캐릭터 레퍼런스 이미지 입력(공식 지원) |
| B. OpenAI | gpt-image 계열 generations/edits | edits에 앵커 이미지를 레퍼런스로 재투입 |
| C. SVG 폴백 | Claude가 SVG 코드 직접 작성 → qlmanage/sips 렌더 | `<defs>` 심볼 재사용으로 완전 일관 |

**⚠️ 모델명 단정 금지:** API 사용 전 반드시 모델 목록 엔드포인트를 실측 호출해 현재 사용 가능한
이미지 모델 ID를 확인하고 사용한다. 문서 기억 속 모델명을 그대로 하드코딩하지 않는다.
호출 실패(키 무효·쿼터·차단) 시 다음 우선순위로 자동 폴백하고 마스터 trace에 기록한다.

## 2. 화풍 고정 블록 (전 장면 동일 적용)

`references/style-attributes.md`를 Read하여 **고정 프롬프트 블록**을 만든다. 핵심:
- 난색 파스텔 팔레트(노랑·주황 도미넌트 + 하늘색·연두 보조), 밝고 따뜻한 톤
- 치비 비율(큰 머리·작은 몸), 점 눈, 홍조 볼, 미소
- 둥글둥글한 형태, 종이 콜라주/크레용 질감의 플랫 일러스트, 부드러운 음영
- 화면 요소 3–5개, 이미지 내 텍스트 절대 없음, 무섭거나 어두운 표현 없음

> ⛔ **저작권 안전:** 프롬프트에 출판물·작가·브랜드 고유명사를 절대 넣지 않는다.
> 화풍은 위처럼 속성으로만 기술한다.

## 3. 스타일 앵커 → 전 장면 생성

1. **캐릭터 시트(AI 경로)**: 캐릭터 명단의 주요 인물을 한 장(정면·전신)으로 먼저 생성 → 이후 전 장면의 레퍼런스로 재투입.
2. **1번 이미지 = 스타일 앵커**: 가장 먼저 생성·확정하고 나머지를 거기에 맞춘다.
3. 장면별 프롬프트 = 화풍 고정 블록 + 캐릭터 고정 문구 + 해당 장면 묘사(매핑표 기준).
4. 다장 생성은 병렬 에이전트로 가속 가능(단, 앵커 확정 후).

## 4. SVG 폴백 경로 세부

`references/svg-symbol-templates.md`의 심볼 패턴(`#jesus` `#sheep` `#sun` `#sky` 등)을 기반으로 작성.

**qlmanage 정사각 렌더 버그 해결책(검증된 교훈):** qlmanage는 16:9 SVG를 1280×1280 정사각에 맞춰
확대해 우측 객체가 잘린다. → SVG 캔버스를 **1280×1280 정사각으로 작성**(상하 패딩 영역에 하늘·땅 연장)
후 중앙 1280×720 크롭.

```bash
qlmanage -t -s 1280 -o . scene.svg     # SVG → 1280×1280 PNG
sips -c 720 1280 scene.svg.png          # 중앙 크롭 → 1280×720
sips -s format jpeg -s formatOptions 92 scene.svg.png --out 01_장면명.jpg
```

## 5. 산출 규격

| 항목 | 규격 |
|------|------|
| 해상도 | 1280×720 (16:9) |
| 형식 | JPG (품질 92) |
| 파일명 | `NN_장면명.jpg` (01부터, 한글 장면명) |
| 위치 | `<프로젝트 폴더>/jpg/` (SVG 경로 시 원본은 `svg/`) |
| 프롬프트 기록 | `<프로젝트 폴더>/prompts/NN_장면명.md` — 사용 엔진·모델 ID·전체 프롬프트·레퍼런스 사용 내역 |

## 6. 재생성 모드 (verification FAIL 시)

- 수정 지시서에 명시된 **해당 이미지만** 다시 만든다. 통과한 이미지 재생성 금지.
- 수정 사유를 프롬프트에 반영하고, 스타일 앵커·캐릭터 레퍼런스는 유지한다.
- prompts/ 기록에 라운드 번호를 남긴다 (예: `03_장면명_r2.md`).
