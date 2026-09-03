"""데이터 모델 (Concept.md §5 스키마 기반, MVP 축약판)."""
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    issn: Mapped[str] = mapped_column(String(50))            # 대표 ISSN (예: 2058-7546)
    openalex_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 실행 중 ISSN으로 자동 해석/캐시
    impact_factor: Mapped[float | None] = mapped_column(Float, nullable=True)
    field: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    papers: Mapped[list["Paper"]] = relationship(back_populates="journal")


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doi: Mapped[str | None] = mapped_column(String(300), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    journal_id: Mapped[int | None] = mapped_column(ForeignKey("journals.id"), nullable=True)
    published_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="openalex")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    journal: Mapped["Journal"] = relationship(back_populates="papers")
    summary: Mapped["Summary"] = relationship(back_populates="paper", uselist=False)


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id"), unique=True)
    tldr: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_points: Mapped[list | None] = mapped_column(JSON, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(80), nullable=True)

    paper: Mapped["Paper"] = relationship(back_populates="summary")
