"""FastAPI 서버 (Concept.md Phase 3)."""
import os
from datetime import date, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import init_db, get_session
from .models import Paper, Journal, Summary
from .harvest import run_harvest
from .summarize import summarize_pending


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # 테이블 생성 + 저널 시드
    yield


app = FastAPI(title="ESSL Paper Study API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/journals")
def list_journals(db: Session = Depends(get_session)):
    return [
        {"id": j.id, "name": j.name, "issn": j.issn, "impact_factor": j.impact_factor, "field": j.field}
        for j in db.query(Journal).filter(Journal.is_active.is_(True)).all()
    ]


@app.get("/api/papers")
def list_papers(days: int = 7, db: Session = Depends(get_session)):
    """최근 N일 신규 논문 (요약 포함)."""
    since = date.today() - timedelta(days=days)
    rows = (
        db.query(Paper)
        .filter((Paper.published_at >= since) | (Paper.published_at.is_(None)))
        .order_by(Paper.created_at.desc())
        .limit(200)
        .all()
    )
    out = []
    for p in rows:
        out.append({
            "id": p.id,
            "title": p.title,
            "journal": p.journal.name if p.journal else None,
            "impact_factor": p.journal.impact_factor if p.journal else None,
            "published_at": p.published_at.isoformat() if p.published_at else None,
            "url": p.url,
            "authors": p.authors,
            "tldr": p.summary.tldr if p.summary else None,
            "keywords": p.summary.keywords if p.summary else None,
        })
    return out


@app.post("/api/harvest")
def trigger_harvest(summarize: bool = True, db: Session = Depends(get_session)):
    """수동 수집 트리거 (개발/데모용). 실제 운영은 스케줄러 사용."""
    result = run_harvest(db)
    if summarize:
        result["summarized"] = summarize_pending(db)
    return result
