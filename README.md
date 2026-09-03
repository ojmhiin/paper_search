# paper_search — ESSL Paper Study

IF>15 저널의 신규 논문을 매일 수집하고, AI 요약과 함께 학습하는 앱.

- **Web (React/Vite)** 프론트엔드 + **FastAPI** 백엔드 + **SQLite** DB
- 데이터 수집: **OpenAlex** (저널 화이트리스트 기반)
- AI 요약: **Claude API** (선택, 키 없으면 자동 스킵)

기획·설계 배경은 `Concept.md`, `Design.md` 참고. 구현 계획·체크리스트는 `ToDo.md` 참고.

## 빠른 시작
```bash
bash setup.sh     # 설치 (venv, 의존성, DB 초기화, npm)
bash run.sh       # 실행 → http://localhost:5173
```
브라우저에서 **지금 수집** 버튼 → OpenAlex에서 신규 논문을 가져옵니다.

## 구조
```
backend/app/  main.py(API) db.py models.py seed.py harvest.py summarize.py
frontend/src/ App.jsx (데일리 피드 UI)
setup.sh run.sh .env.example
```
