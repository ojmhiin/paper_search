"""DB 설정: MVP는 SQLite(무설정), 이후 PostgreSQL+pgvector로 승급 가능."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./essl_papers.db")

# SQLite 사용 시 스레드 옵션
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """테이블 생성 후 저널 화이트리스트 시드."""
    from . import models  # noqa: F401  (모델 등록)
    Base.metadata.create_all(bind=engine)
    from .seed import seed_journals
    with SessionLocal() as session:
        seed_journals(session)


def get_session():
    """FastAPI 의존성."""
    with SessionLocal() as session:
        yield session
