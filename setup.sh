#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  ESSL Paper Study — 로컬 설치 스크립트
#  실행:  bash setup.sh
#  (Windows는 WSL 또는 Git Bash에서 실행하세요)
# ─────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/5 사전 요구사항 확인"
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 필요 (3.10+)"; exit 1; }
command -v node   >/dev/null 2>&1 || { echo "❌ node 필요 (18+)"; exit 1; }
command -v npm    >/dev/null 2>&1 || { echo "❌ npm 필요"; exit 1; }
echo "   python3: $(python3 --version) / node: $(node --version)"

echo "==> 2/5 .env 준비"
[ -f .env ] || cp .env.example .env && echo "   .env 생성(또는 존재)"

echo "==> 3/5 백엔드 설치 (venv + pip)"
cd backend
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt
echo "   백엔드 의존성 설치 완료"

echo "==> 4/5 DB 초기화 + 저널 시드"
python -c "from app.db import init_db; init_db()"
deactivate
cd ..

echo "==> 5/5 프론트엔드 설치 (npm)"
cd frontend
npm install
cd ..

echo ""
echo "✅ 설치 완료!  다음 명령으로 실행하세요:"
echo "   bash run.sh          # 백엔드 + 프론트 동시 실행"
echo "   또는 개별 실행:"
echo "     (터미널1) cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "     (터미널2) cd frontend && npm run dev"
echo ""
echo "   브라우저: http://localhost:5173  →  '지금 수집' 클릭"
