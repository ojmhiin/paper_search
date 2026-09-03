# Concept.md — Top-tier 저널 신규 논문 수집·학습 앱

> 매일 Nature, Advanced Energy Materials 등 고임팩트(IF > 15) 저널에 새로 출판되는 논문을 자동으로 모아, AI 요약과 학습 기능으로 효율적으로 공부하는 앱.

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **목적** | 관심 분야 top-tier 저널의 신규 논문을 매일 자동 수집하고, 읽고 공부하기 좋은 형태로 가공·제공 |
| **핵심 가치** | (1) 놓치지 않는 데일리 큐레이션 (2) AI 요약으로 스크리닝 시간 단축 (3) 학습 도구(플래시카드/퀴즈/노트) 내장 |
| **타겟 사용자** | 대학원생, 연구원, R&D 엔지니어 (에너지·소재·화학 등) |
| **차별점** | 단순 알림/RSS 리더가 아니라 "IF 기준 필터 + AI 학습 파이프라인"을 결합 |

---

## 2. 가장 먼저 정해야 할 핵심 설계 결정: "IF > 15"를 어떻게 필터링할 것인가

이 앱의 성패를 가르는 지점입니다. **Impact Factor(IF)는 개별 논문의 속성이 아니라 저널 단위 연간 지표**이며, Clarivate JCR의 **유료·독점 데이터**입니다. 따라서 "논문마다 IF를 조회해서 거른다"는 접근은 불가능하고, 다음 전략을 씁니다.

### 전략: 저널 화이트리스트(whitelist) 방식

1. **IF > 15 저널 목록을 사전에 큐레이션**해 두고(대략 100~250개 수준), 각 저널의 **ISSN**을 확보한다.
2. 데이터 수집 시 **저널 단위로 신규 논문을 가져온다** → 필터링이 자동으로 완성됨.
3. IF는 매년 갱신되므로, 화이트리스트는 **연 1회 수동 업데이트**한다.

### IF 데이터를 합법적으로 다루는 방법

- **JCR(Clarivate) 원본**을 스크래핑/재배포하는 것은 라이선스 위반 소지 → 지양.
- 대안: **오픈 지표를 프록시로 사용**
  - **OpenAlex** `sources`의 `summary_stats.2yr_mean_citedness` → IF와 거의 동일한 정의(2년 평균 피인용)로, **무료·합법**.
  - **SJR (Scimago Journal Rank)**, **CiteScore(Scopus)** 등도 참고 가능.
- 실무 권장: **소속 기관 라이선스로 확인한 IF 값을 화이트리스트에 수동 기재**하고, 앱 내부 자동 필터는 OpenAlex 지표로 이중 확인.

> ⚠️ 결론: "IF > 15 논문을 실시간으로 계산해 거른다"가 아니라, **"IF > 15 저널을 미리 골라 그 저널의 신규 논문을 수집한다"** 로 설계한다.

---

## 3. 데이터 소스 전략

논문 **메타데이터(제목·초록·저자·DOI·출판일)** 는 아래 오픈 소스로 대부분 확보 가능하다. **전문(full-text PDF)은 저작권 대상**이므로 앱이 호스팅하지 않고 publisher 링크로 연결한다(§9 참고).

| 소스 | 용도 | 특징 | 비용 |
|------|------|------|------|
| **OpenAlex API** | 메인 수집원 | 저널(source) 필터·출판일 필터 강력, 저널 지표 제공, 초록(역색인) 포함 | 무료 |
| **Crossref API** | 보조/교차검증 | DOI 기준 표준, `from-online-pub-date` 필터, ISSN별 조회 | 무료 |
| **저널 RSS/Atom 피드** | 실시간성 보완 | Nature·Wiley·ACS·RSC 등이 신규 논문 피드 제공, 지연 적음 | 무료 |
| **Publisher API** | 초록·전문 보강 | Springer Nature API, Elsevier(ScienceDirect), Wiley TDM 등 | 키 필요, 일부 유료 |
| **Semantic Scholar API** | 인용·추천 보강 | 논문 간 관계, TLDR 필드 | 무료(레이트리밋) |
| **PubMed E-utilities** | 생의학 분야 | 해당 분야 저널이면 병행 | 무료 |

**권장 조합**: `OpenAlex(수집 본체)` + `RSS(실시간 보완)` + `Crossref(중복제거·교차검증)`.

> 📌 API 세부 파라미터·레이트리밋은 시간이 지나면 바뀌므로 구현 시점에 각 공식 문서를 반드시 재확인할 것.

---

## 4. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      데이터 수집 계층                          │
│  [스케줄러: 매일 실행]                                          │
│   ├─ OpenAlex Harvester  (저널×출판일 필터)                    │
│   ├─ RSS Poller          (저널 피드 파싱)                      │
│   └─ Crossref Cross-check (DOI 중복제거)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │  신규 논문(raw)
┌───────────────────────────▼─────────────────────────────────┐
│                      처리·가공 계층                            │
│   ├─ Dedup / Normalize   (DOI 기준 정규화)                     │
│   ├─ LLM 요약 파이프라인  (TL;DR·핵심기여·쉬운설명)             │
│   ├─ 임베딩 생성          (의미 검색·추천용)                    │
│   └─ 학습자료 생성        (플래시카드·퀴즈)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│            저장 계층: PostgreSQL (+ pgvector)                  │
│   papers / journals / summaries / user_data / embeddings      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                 API 서버 (FastAPI / REST)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│        프론트엔드: Web(Next.js) / Mobile(React Native)        │
│   데일리 피드 · 상세 뷰 · 요약 · 학습모드 · 북마크/노트         │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 데이터 모델 (스키마 초안)

```sql
-- 대상 저널 화이트리스트 (핵심)
journals (
  id            SERIAL PRIMARY KEY,
  name          TEXT,
  issn          TEXT[],          -- print/online ISSN 배열
  openalex_id   TEXT,            -- 예: S137773608
  impact_factor NUMERIC,         -- 수동 기재 (연 1회 갱신)
  metric_year   INT,
  field         TEXT,            -- energy, materials, chem ...
  is_active     BOOLEAN DEFAULT true
)

-- 수집된 논문
papers (
  id            SERIAL PRIMARY KEY,
  doi           TEXT UNIQUE,     -- 중복제거 키
  title         TEXT,
  abstract      TEXT,
  authors       JSONB,
  journal_id    INT REFERENCES journals(id),
  published_at  DATE,
  url           TEXT,            -- publisher 원문 링크
  source        TEXT,            -- openalex / rss / crossref
  created_at    TIMESTAMP DEFAULT now()
)

-- AI 가공 결과
summaries (
  paper_id      INT REFERENCES papers(id),
  tldr          TEXT,            -- 3~4줄 요약
  key_points    JSONB,           -- 핵심 기여 리스트
  plain_explain TEXT,            -- 쉬운 설명
  keywords      TEXT[],
  model_used    TEXT
)

-- 학습·개인화
user_bookmarks (user_id, paper_id, note, created_at)
flashcards       (paper_id, question, answer)
quizzes          (paper_id, question, options JSONB, answer)
embeddings       (paper_id, vector VECTOR(1536))   -- 의미검색/추천
```

---

## 6. 구현 절차 (단계별)

### Phase 0 — 저널 화이트리스트 구축 (0.5주)
- [ ] 관심 분야의 IF > 15 저널을 조사해 목록화 (Nature, Nature Energy, Advanced Energy Materials, Adv. Materials, JACS, Angew. Chem., Energy & Environmental Science 등).
- [ ] 각 저널의 **ISSN, OpenAlex source ID, IF, RSS URL** 을 수집해 `journals` 테이블 시드 데이터로 저장.

### Phase 1 — 데이터 수집 파이프라인 (1~1.5주)
- [ ] OpenAlex에서 `저널 × 최근 출판일`로 신규 논문 조회.
- [ ] RSS 피드 파서로 실시간 신규 논문 보완.
- [ ] **DOI 기준 중복제거**, 필드 정규화 후 `papers`에 저장.
- [ ] 스케줄러(cron/GitHub Actions/Celery beat)로 **매일 자동 실행**.

**OpenAlex 수집 예시 (Python):**
```python
import requests
from datetime import date, timedelta

def fetch_new_papers(openalex_source_id: str, since: date):
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"primary_location.source.id:{openalex_source_id},"
                  f"from_publication_date:{since.isoformat()}",
        "per-page": 50,
        "mailto": "you@example.com",   # polite pool (레이트리밋 완화)
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

# 매일 실행: 어제 이후 출판분 수집
papers = fetch_new_papers("S137773608", date.today() - timedelta(days=2))
```

**Crossref 교차검증 예시:**
```python
# ISSN 기준 온라인 출판일 필터
url = f"https://api.crossref.org/journals/{issn}/works"
params = {"filter": f"from-online-pub-date:{since.isoformat()}", "rows": 50}
```

### Phase 2 — AI 요약·학습자료 생성 (1주)
- [ ] 신규 논문의 제목+초록을 LLM API(예: Claude API)에 넣어 **TL;DR / 핵심 기여 / 쉬운 설명 / 키워드** 생성.
- [ ] 임베딩 생성 → `pgvector`에 저장(의미 검색·추천용).
- [ ] 초록 기반으로 **플래시카드·퀴즈** 자동 생성.

**요약 생성 프롬프트 예시:**
```
아래 논문 초록을 읽고 JSON으로만 답하라.
{
  "tldr": "3~4문장 핵심 요약",
  "key_points": ["핵심 기여 1", "핵심 기여 2", ...],
  "plain_explain": "비전공자도 이해할 쉬운 설명",
  "keywords": ["...", "..."]
}
제목: {title}
초록: {abstract}
```
> 초록이 없는 논문은 요약 품질이 낮으므로, publisher API로 초록을 보강하거나 "초록 미제공"으로 표시.

### Phase 3 — 백엔드 API (0.5~1주)
- [ ] REST 엔드포인트: 데일리 피드, 논문 상세, 검색, 북마크, 노트, 학습자료.
- [ ] 필터 파라미터: 분야·저널·날짜·키워드.

### Phase 4 — 프론트엔드 (1.5~2주)
- [ ] **데일리 피드**: 날짜별 신규 논문 카드 리스트(저널·IF·TL;DR 표시).
- [ ] **상세 뷰**: 요약 + 원문 링크 + 북마크/노트.
- [ ] **학습 모드**: 플래시카드·퀴즈.
- [ ] **검색/추천**: 키워드 + 의미 검색.

### Phase 5 — 개인화·알림 (선택, 1주)
- [ ] 관심 키워드 기반 필터링, 읽은 이력 기반 추천.
- [ ] 데일리 다이제스트 푸시/이메일.

### Phase 6 — 배포·운영 (0.5주)
- [ ] Docker 컨테이너화, 클라우드 배포(Fly.io/Railway/AWS 등).
- [ ] 수집 잡 모니터링·에러 알림, 저널 목록 연 1회 갱신 루틴.

---

## 7. 기술 스택 (권장)

| 계층 | 추천 | 이유 |
|------|------|------|
| 수집·백엔드 | **Python + FastAPI** | 데이터 파이프라인·LLM 연동 용이 |
| 스케줄러 | cron / GitHub Actions(초기) → Celery/Airflow(확장) | 규모에 따라 점진 도입 |
| DB | **PostgreSQL + pgvector** | 관계형 + 벡터검색 통합 |
| LLM | Claude API 등 LLM API | 요약·플래시카드·Q&A |
| 웹 | **Next.js (React)** | SSR·빠른 개발 |
| 모바일 | React Native / Flutter | 크로스플랫폼 |
| 배포 | Docker + Fly.io/Railway/AWS | 간편 배포 |

---

## 8. 학습(Study) 기능 상세

- **데일리 브리핑**: 오늘의 신규 논문을 TL;DR과 함께 3분 스캔.
- **AI 요약 레벨 조절**: 한 줄 / 3줄 / 상세.
- **플래시카드**: 핵심 개념 Q&A 자동 생성 → 간격 반복(spaced repetition).
- **퀴즈**: 초록 기반 객관식으로 이해도 점검.
- **논문 Q&A(RAG)**: 저장한 논문에 대해 질문하면 임베딩 검색 기반으로 답변.
- **노트·하이라이트**: 개인 메모 저장·검색.
- **주간 리뷰**: 이번 주 저장 논문 자동 요약.

---

## 9. 법적·윤리적 고려사항 (필수)

- **메타데이터(제목·저자·DOI·출판일)**: 대부분 자유롭게 이용 가능.
- **초록**: 소스에 따라 이용 조건이 다름(OpenAlex/Crossref는 대체로 가능, 일부 publisher는 제한) → 소스별 라이선스 확인.
- **전문 PDF**: **저작권 대상. 앱이 호스팅·재배포하지 말 것.** 반드시 publisher 원문 링크로 연결.
- **IF/JCR 데이터**: Clarivate 독점 → 원본 스크래핑·재배포 금지. 화이트리스트에 수동 기재 + 오픈 지표 프록시 사용.
- **API 이용약관·레이트리밋** 준수, `mailto`/API 키로 polite 요청.
- LLM 요약은 **참고용**임을 명시(원문 확인 권고).

---

## 10. MVP 범위 및 로드맵

**MVP (약 3~4주 목표)**
1. 관심 분야 IF > 15 저널 20~30개 화이트리스트.
2. OpenAlex 매일 수집 + DOI 중복제거.
3. LLM TL;DR 생성.
4. 웹 데일리 피드 + 북마크.

**V1 확장**
- RSS 실시간 보완, 퀴즈·플래시카드, 의미검색.

**V2 확장**
- 개인화 추천, 모바일 앱, 논문 Q&A(RAG), 데일리 다이제스트 알림.

---

## 11. 예상 운영 비용 (개략)

| 항목 | 비용 성격 |
|------|-----------|
| OpenAlex/Crossref/RSS | 무료 |
| LLM 요약 | 논문당 소액(초록 길이에 비례) — 하루 신규 논문 수 × 단가로 산정 |
| DB·서버 호스팅 | 소규모면 월 저비용(무료 티어~수만 원) |
| Publisher API(선택) | 초록/전문 보강 시 유료 가능 |

> 비용의 대부분은 **LLM 요약 호출량**에서 발생. 신규 논문 수를 화이트리스트로 제한하면 비용이 자연스럽게 통제됨.

---

## 12. 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| 초록 미제공 논문 | publisher API 보강 / "초록 없음" 표시 |
| IF 갱신·저널 변동 | 연 1회 화이트리스트 점검 루틴 |
| API 레이트리밋/스펙 변경 | polite 요청, 캐싱, 다중 소스 이중화 |
| 요약 부정확성 | "참고용" 고지 + 원문 링크 병기 |
| 저작권 | 전문 비호스팅, 메타데이터·링크 중심 |

---

### 다음 액션
1. **관심 분야 확정** → IF > 15 저널 리스트업(§Phase 0).
2. OpenAlex source ID·ISSN 수집해 `journals` 시드 작성.
3. Phase 1 수집 스크립트 프로토타입 → 하루 수집 결과 검증.
