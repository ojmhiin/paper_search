# ToDo.md — ESSL Paper Study 구현 계획

> 기반 문서: `Concept.md`, `Design.md`
> 이 문서 = **플랫폼/서버/DB 결정 + 로컬 실행 방법 + 단계별 체크리스트**

---

## 1. 플랫폼 결정: **Web (React) 우선** ✅

| 후보 | 판단 | 이유 |
|------|------|------|
| **Web (React/Vite)** | ✅ **채택 (MVP~V1)** | ① 백엔드가 어차피 필수라 웹 클라이언트가 가장 가벼움 ② 연구자는 주로 **데스크톱에서 논문을 읽고 공부** ③ 개발·배포·로컬셋업 가장 빠름 ④ 긴 텍스트·노트 작성에 유리 |
| Mobile (Flutter) | 🕓 **V2로 연기** | 알림·이동 중 열람엔 좋지만, **동일 백엔드 API를 그대로 재사용**하면 되므로 나중에 추가가 합리적. MVP 단계에서 앱스토어 배포/디바이스 대응은 과투자 |

**결론**: 지금은 **React 웹**으로 만들고, API가 안정되면 Flutter를 **동반 앱**으로 붙인다. (백엔드/DB는 공유)

---

## 2. 서버 · DB 필요성 판단

### 서버: **필요** ✅
1. **매일 자동 수집**은 스케줄 작업이라 클라이언트(브라우저/폰)에서 불가.
2. **LLM API 키**는 서버에 숨겨야 함(클라이언트 노출 금지).
3. 여러 소스 **중복제거·정규화·저장**을 중앙에서 처리.

### DB: **필요** ✅ (단계별 선택)
| 단계 | DB | 이유 |
|------|----|------|
| **MVP (지금)** | **SQLite** | 무설정·단일 파일·즉시 실행. 데일리 피드/요약/북마크에 충분 |
| **V1+** | **PostgreSQL + pgvector** | 시맨틱 검색·추천(임베딩)·동시성 필요해질 때 승급 |

> 코드는 `DATABASE_URL` 환경변수만 바꾸면 SQLite→Postgres 전환되도록 작성됨.

### 확정 스택
```
Frontend : React + Vite            (웹)
Backend  : Python + FastAPI        (API + 수집 + 요약)
DB       : SQLite → (승급) Postgres+pgvector
수집     : OpenAlex API (+ 이후 RSS/Crossref)
요약     : Claude API (선택, 키 없으면 스킵)
스케줄   : 로컬 = 수동/APScheduler → 운영 = cron/Airflow
```

---

## 3. 로컬에서 바로 설치·실행 🚀

### 사전 요구사항
- Python **3.10+**, Node **18+**, npm  (Windows는 WSL/Git Bash 권장)

### 설치 & 실행 (2줄)
```bash
bash setup.sh     # venv·의존성·DB초기화·저널시드·npm install 자동
bash run.sh       # 백엔드(:8000) + 프론트(:5173) 동시 실행
```
→ 브라우저 **http://localhost:5173** 접속 → 우측 상단 **지금 수집** 클릭 → OpenAlex에서 신규 논문 수집·표시.

> AI 요약을 켜려면 `.env`의 `ANTHROPIC_API_KEY`를 채우고 `CLAUDE_MODEL`을 현재 모델명으로 설정(미설정 시 수집·피드는 정상, 요약만 생략).

### setup.sh가 하는 일
1. python3/node/npm 존재 확인
2. `.env.example → .env` 복사
3. `backend/.venv` 생성 + `pip install -r requirements.txt`
4. **DB 테이블 생성 + 저널 화이트리스트 시드**
5. `frontend` `npm install`
6. 실행 방법 안내 출력

### 개별 실행(디버깅용)
```bash
# 터미널 1
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload
# 터미널 2
cd frontend && npm run dev
```

### 제공되는 API
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/health` | 헬스체크 |
| GET | `/api/journals` | 저널 화이트리스트 |
| GET | `/api/papers?days=7` | 최근 N일 신규 논문(요약 포함) |
| POST | `/api/harvest?summarize=true` | 수동 수집+요약 트리거 |

---

## 4. 프로젝트 구조 (스캐폴드 포함됨)

```
paper-study-app/
├── setup.sh / run.sh / README.md / .env.example / ToDo.md
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py        # FastAPI 라우트 (Phase 3)
│       ├── db.py          # SQLite 엔진/세션/init (DB)
│       ├── models.py      # Journal/Paper/Summary (Concept §5)
│       ├── seed.py        # IF>15 저널 시드 (Concept §2)
│       ├── harvest.py     # OpenAlex 수집 (Phase 1)
│       └── summarize.py   # Claude 요약 (Phase 2)
└── frontend/
    └── src/App.jsx        # 데일리 피드 UI (Design.md 토큰 적용)
```

---

## 5. 단계별 ToDo 체크리스트 (Concept.md Phase 매핑)

### ✅ Phase 0 — 저널 화이트리스트  *(스캐폴드에 기본 9종 포함)*
- [x] IF>15 저널 시드(Nature, Nature Energy, Adv. Energy Materials 등)
- [ ] **관심 분야에 맞게 저널 20~30종으로 확장** (`backend/app/seed.py` 수정)
- [ ] 각 저널 IF 값 최신 JCR로 검증 (현재는 예시값)

### ✅ Phase 1 — 수집 파이프라인  *(OpenAlex 동작 구현됨)*
- [x] OpenAlex ISSN→source 해석 + 최근 출판분 수집 + DOI 중복제거
- [ ] **RSS 피드 파서 추가**(실시간성 보완, `feedparser` 이미 포함)
- [ ] Crossref 교차검증 추가
- [ ] 초록 없는 논문 보강 로직

### ✅ Phase 2 — AI 요약  *(Claude 연동 구현됨)*
- [x] 초록→TL;DR/핵심포인트/키워드 JSON 생성(키 있을 때)
- [ ] 요약 실패/JSON 파싱 예외 재시도 로직 강화
- [ ] 쉬운 설명(plain_explain) 필드 추가

### ✅ Phase 3 — 백엔드 API  *(기본 엔드포인트 구현됨)*
- [x] papers/journals/harvest/health 라우트
- [ ] 검색·필터(분야·저널·키워드) 파라미터
- [ ] 북마크·노트 엔드포인트 + 테이블

### 🔨 Phase 4 — 프론트엔드
- [x] 데일리 피드 카드 리스트 + 수집 버튼(Design.md 토큰 적용)
- [ ] 논문 상세 뷰(요약+원문 링크+북마크)
- [ ] 검색/필터 UI
- [ ] Design.md ⚠️값(색/폰트/여백) 라이브 확인 후 토큰 확정

### 🔨 Phase 5 — 학습 기능
- [ ] 플래시카드 생성·복습(간격 반복)
- [ ] 퀴즈 자동 생성·풀이
- [ ] 노트/하이라이트
- [ ] (V1+) 임베딩 + pgvector 시맨틱 검색·논문 Q&A(RAG)

### 🔨 Phase 6 — 자동화·배포
- [ ] 로컬 APScheduler로 매일 자동 수집(현재는 수동 버튼)
- [ ] 운영: cron/Airflow 스케줄 + Docker 컨테이너화
- [ ] PostgreSQL+pgvector 승급(`DATABASE_URL` 교체)
- [ ] 클라우드 배포(Fly.io/Railway/AWS)
- [ ] 데일리 다이제스트 이메일/푸시

### 🔮 V2 — 모바일 (Flutter)
- [ ] 동일 백엔드 API 소비하는 Flutter 앱
- [ ] 푸시 알림, 오프라인 캐시

---

## 6. 지금 바로 할 일 (다음 3스텝)
1. `bash setup.sh && bash run.sh` 로 스캐폴드 실행 확인.
2. `backend/app/seed.py`에서 **본인 분야 저널 목록 확정**(ISSN·IF).
3. `.env`에 `ANTHROPIC_API_KEY` + 현재 `CLAUDE_MODEL` 설정 후 요약 확인.

---

## 7. 유의사항
- **저작권**: 전문 PDF 비호스팅, 원문은 링크로만 연결(Concept §9).
- **IF/ISSN**: 시드값은 예시 — 운영 전 최신 JCR로 검증.
- **모델명**: `CLAUDE_MODEL`은 docs.claude.com에서 현재 제공 모델 확인 후 지정.
- **API 한도**: OpenAlex는 `OPENALEX_MAILTO` 설정 시 polite pool 사용(권장).
