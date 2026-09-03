#!/usr/bin/env bash
# 백엔드(:8000) + 프론트(:5173) 동시 실행. Ctrl+C 로 둘 다 종료.
set -euo pipefail
cd "$(dirname "$0")"

cleanup() { kill 0; }
trap cleanup EXIT

echo "==> 백엔드 시작 (http://localhost:8000)"
( cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000 ) &

echo "==> 프론트 시작 (http://localhost:5173)"
( cd frontend && npm run dev ) &

wait
