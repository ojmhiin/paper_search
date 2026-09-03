# Design.md — KNU ESSL 사이트 디자인 분석

> 분석 대상: https://sites.google.com/view/knu2024essl/knu-essl
> 사이트명: **KNU Energy Storage & System Laboratory (ESSL)**
> 제작 플랫폼: **Google Sites (신규 버전)**

---

## 0. 분석 정확도에 대한 안내 (먼저 읽어주세요)

이 사이트는 **Google Sites로 제작**되었습니다. Google Sites는 CSS를 동적으로 생성·난독화하므로, 정적 페이지 fetch만으로는 아래를 구분해서 다뤄야 합니다.

| 구분 | 신뢰도 | 근거 |
|------|--------|------|
| 레이아웃·구조·콘텐츠 계층 | ✅ **확정** | 페이지 소스에서 직접 확인 |
| 컴포넌트 구성(내비·배너·본문·푸터) | ✅ **확정** | 페이지 소스에서 직접 확인 |
| 색상 hex / 폰트 패밀리 / 픽셀 여백 | ⚠️ **추정** | Google Sites 기본 디자인 시스템 기반. **라이브 페이지 DevTools로 최종 확인 필요** |

> 🔍 **정확한 값 확정 방법**: 브라우저에서 페이지 접속 → 요소 우클릭 → "검사(Inspect)" → Computed 탭에서 `color`, `font-family`, `padding`, `margin` 확인. 스크린샷을 주시면 실제 색/폰트에 맞춰 이 문서를 정밀 보정해 드릴 수 있습니다.

---

## 1. 전체 레이아웃 구조 (✅ 확정)

```
┌──────────────────────────────────────────────────────────┐
│  [상단 고정 헤더]                                          │
│  로고 + "KNU ESSL For You"        [검색] 아이콘            │
│  ── 내비게이션 바 (수평, 드롭다운 포함) ──                 │
│   KNU ESSL │ Research▾ │ Publication List │ Members │      │
│            │           │ Contact │ Memories             │  │
├──────────────────────────────────────────────────────────┤
│  [히어로 / 페이지 타이틀]                                  │
│  H1: "KNU Energy Storage & System Laboratory"             │
├──────────────────────────────────────────────────────────┤
│  [이미지 배너 영역]                                        │
│  대형 가로 이미지 다수 (w1280) 세로 나열/캐러셀            │
├──────────────────────────────────────────────────────────┤
│  [본문 콘텐츠 — 단일 컬럼, 중앙 정렬]                      │
│   • On-going Projects   (번호 리스트)                     │
│   • Finished Projects   (번호 리스트)                     │
│   • Research Keywords   (분류 리스트)                     │
│   • News                (연대순 번호 리스트, 링크 포함)   │
├──────────────────────────────────────────────────────────┤
│  [푸터]                                                    │
│  "Energy Storage & System Laboratory (c) 2024, ESSL |     │
│   All Rights Reserved."   + Google Sites 기본 푸터        │
└──────────────────────────────────────────────────────────┘
```

**레이아웃 특징**
- **단일 컬럼(single-column) 중심** 구조. 사이드바 없음.
- **상단 고정 내비게이션** + 드롭다운(Research 하위 3개 항목).
- **풀블리드(full-bleed) 이미지 배너** + **폭이 제한된 중앙 정렬 본문**의 조합(전형적 Google Sites 패턴).
- 콘텐츠는 텍스트 위주의 정보 나열형(프로젝트·키워드·뉴스).

---

## 2. 그리드 & 여백 규칙 (⚠️ Google Sites 표준 기반)

Google Sites 신규 버전의 표준 레이아웃 규칙입니다.

| 항목 | 값(표준) | 비고 |
|------|----------|------|
| 배너/섹션 배경 | **full-width (100vw)** | 이미지·색 배경은 화면 전체 폭 |
| 본문 콘텐츠 최대 폭 | **~1000px (약 960~1024px)** | 중앙 정렬, 좌우 자동 여백 |
| 섹션 좌우 패딩(데스크톱) | **약 24~32px** | 좁은 화면에서 축소 |
| 섹션 상하 패딩 | **약 24~48px** | 섹션 단위 수직 리듬 |
| 요소 간 수직 간격 | **약 16~24px** | 문단/블록 간 |
| 반응형 분기점 | **약 768px 이하 = 모바일** | 내비가 햄버거(≡)로 접힘 |

> ⚠️ 위 값은 Google Sites 기본 그리드 기준의 근사치입니다. 정확한 max-width/padding은 라이브 DevTools로 확인하세요.

---

## 3. 색상 팔레트 (⚠️ 검증 필요)

Google Sites는 **테마(theme)** 단위로 색을 관리하며, 보통 `배경 / 강조(accent) / 텍스트`의 소수 색으로 구성됩니다. 아래는 학술 랩 사이트에서 흔한 기본 테마 팔레트를 기준으로 한 **추정치**이며, 실제 hex는 확인이 필요합니다.

| 역할 | 추정 값 | 용도 | 확인 필요 |
|------|---------|------|:---------:|
| 배경(Base) | `#FFFFFF` | 본문 배경 | ✅ |
| 텍스트(Primary) | `#212121` ~ `#000000` | 본문 글자 | ✅ |
| 텍스트(Secondary) | `#5F6368` | 보조/캡션 | ✅ |
| 강조(Accent/Link) | `#1A73E8`(Google 블루 계열) | 링크·버튼·강조 | ✅ |
| 헤더/내비 배경 | `#FFFFFF` 또는 테마 강조색 | 상단 바 | ✅ |
| 구분선/보더 | `#E0E0E0` | 경계선 | ✅ |

**추천 조사 절차**: DevTools → 헤더 바, 링크 텍스트, 본문 텍스트 각각의 `color` / `background-color`(Computed)를 읽어 위 표를 실제 hex로 치환하세요.

---

## 4. 타이포그래피 (⚠️ 검증 필요)

Google Sites 테마는 **제목용 폰트 + 본문용 폰트** 페어로 구성됩니다. 기본(Simple) 테마는 산세리프 계열(Arial/Roboto 유사)을 사용합니다.

| 스타일 | 추정 폰트/크기 | 용도 |
|--------|----------------|------|
| H1 (페이지 타이틀) | 산세리프, **약 28~40px, 굵게** | "KNU Energy Storage & System Laboratory" |
| H2 (섹션 제목) | 산세리프, **약 20~28px** | On-going Projects, News 등 |
| 본문(Body) | 산세리프, **약 14~16px, line-height ~1.5** | 프로젝트·뉴스 텍스트 |
| 링크 | 본문과 동일 크기, **강조색 + 밑줄/호버** | News 내 [Link] |
| 캡션/푸터 | **약 12~13px, 보조색** | 저작권 문구 |

**폰트 스택 권장(추정 기반 재현용)**:
```css
font-family: 'Roboto', Arial, 'Noto Sans KR', sans-serif;
/* 한글(프로젝트·뉴스 본문) 대응을 위해 Noto Sans KR 병기 권장 */
```
> ⚠️ 실제 테마 폰트는 DevTools의 `font-family`(Computed)로 확인하세요. 한/영 혼용 페이지이므로 **한글 폰트 폴백**이 반드시 필요합니다.

---

## 5. 컴포넌트별 규칙 (✅ 구조 확정 / ⚠️ 스타일 추정)

### 5.1 헤더 & 내비게이션
- 좌측: **로고 이미지 + 사이트명** 텍스트("KNU ESSL For You").
- 우측: **검색** 기능.
- 하단: 수평 메뉴 — `KNU ESSL / Research▾ / Publication List / Members / Contact / Memories`.
- **Research** 항목은 드롭다운(하위 3개: LIB 신소재 / BMS / Advanced E-mobility).
- 모바일: 메뉴가 **햄버거(≡, "More")** 로 접힘.

### 5.2 히어로 / 타이틀
- H1 한 줄로 랩 정식 명칭 표시. 별도 배경색/이미지 오버레이는 확인 필요.

### 5.3 이미지 배너
- **대형 가로 이미지(w1280) 여러 장**이 나열됨(연구·활동 사진 추정).
- 풀블리드 폭. 캐러셀 또는 세로 스택 형태.

### 5.4 본문 콘텐츠 블록 (반복 패턴)
- **섹션 제목(H2) + 번호 매김 목록** 이 반복되는 정보 나열형.
- 리스트 항목은 `(n) 내용 (기관, 기간)` 형식으로 통일.
- News는 `[n] (YY/MM/DD) 내용 [Link]` 형식의 연대기 리스트.
- → **재현 시**: 섹션 제목 + `<ol>`/커스텀 번호 리스트 조합을 컴포넌트화하면 됨.

### 5.5 푸터
- 저작권 한 줄: `Energy Storage & System Laboratory (c) 2024, ESSL | All Rights Reserved.`
- 그 아래 Google Sites 기본 요소(Report abuse, Page details 등).

---

## 6. 반응형 동작 (⚠️ Google Sites 표준)
- **데스크톱**: 수평 내비 + 넓은 배너 + 중앙 정렬 본문.
- **모바일(≤~768px)**: 내비가 햄버거로 축소, 이미지·본문이 1컬럼 풀폭으로 재배치, 좌우 패딩 축소.
- 이미지는 컨테이너 폭에 맞춰 유동 스케일(`max-width:100%`).

---

## 7. 이 디자인을 앱/사이트로 재현하기 위한 디자인 토큰 (실무용)

> 아래는 위 분석을 **재현 가능한 토큰**으로 정리한 것. hex/폰트는 라이브 확인 후 확정 값으로 교체하세요.

```css
:root {
  /* Color (⚠️ 확인 후 확정) */
  --color-bg:        #FFFFFF;
  --color-text:      #212121;
  --color-text-sub:  #5F6368;
  --color-accent:    #1A73E8;   /* 링크·강조 */
  --color-border:    #E0E0E0;

  /* Typography */
  --font-sans: 'Roboto', Arial, 'Noto Sans KR', sans-serif;
  --fs-h1: 32px;
  --fs-h2: 24px;
  --fs-body: 16px;
  --fs-caption: 13px;
  --lh-body: 1.5;

  /* Layout & Spacing */
  --content-max-width: 1000px;
  --section-padding-x: 32px;
  --section-padding-y: 40px;
  --stack-gap: 20px;
  --breakpoint-mobile: 768px;
}

.container {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 var(--section-padding-x);
}
.banner { width: 100%; }           /* full-bleed */
.banner img { width: 100%; height: auto; max-width: 100%; }

@media (max-width: 768px) {
  :root { --section-padding-x: 16px; --fs-h1: 26px; }
}
```

---

## 8. 요약: 디자인 원칙

1. **정보 밀도 높은 단일 컬럼** — 학술 랩 사이트 특성상 텍스트 나열형.
2. **풀블리드 배너 + 폭 제한 본문**의 대비.
3. **미니멀 색상** — 흰 배경 + 무채색 텍스트 + 단일 강조색(링크).
4. **산세리프 + 한글 폴백** — 한/영 혼용 콘텐츠 대응 필수.
5. **일관된 번호 리스트 패턴** — 프로젝트·뉴스 모두 동일한 `(번호) 내용 (메타)` 구조.

---

## 9. 다음 단계 (정밀 보정)

이 문서의 ⚠️ 표시 항목(색상 hex, 폰트, 픽셀 여백)을 확정하려면 둘 중 하나를 주세요.
- **라이브 페이지 스크린샷**(헤더/본문/링크가 보이게) → 색·폰트·비율을 눈으로 보정.
- **DevTools Computed 값**(헤더 배경색, 본문 `color`, `font-family`, 섹션 `padding`) → 정확한 토큰으로 치환.

그러면 이 Design.md를 **픽셀·hex 단위로 정확한 디자인 시스템 스펙**으로 업그레이드해 드리겠습니다.
