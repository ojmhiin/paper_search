"""OpenAlex 기반 신규 논문 수집 (Concept.md Phase 1).

전략: 저널 화이트리스트 → ISSN으로 OpenAlex source id 해석 → 최근 출판분 수집 → DOI 중복제거 upsert.
"""
import os
from datetime import date, timedelta
import httpx
from sqlalchemy.orm import Session
from .models import Journal, Paper

OPENALEX = "https://api.openalex.org"
MAILTO = os.getenv("OPENALEX_MAILTO", "you@example.com")
LOOKBACK_DAYS = int(os.getenv("HARVEST_LOOKBACK_DAYS", "3"))


def _client() -> httpx.Client:
    return httpx.Client(timeout=30, headers={"User-Agent": f"ESSL-PaperApp (mailto:{MAILTO})"})


def resolve_source_id(client: httpx.Client, issn: str) -> str | None:
    """ISSN → OpenAlex source id (예: S137773608)."""
    r = client.get(f"{OPENALEX}/sources/issn:{issn}", params={"mailto": MAILTO})
    if r.status_code != 200:
        return None
    data = r.json()
    sid = data.get("id", "")
    return sid.rsplit("/", 1)[-1] if sid else None


def invert_abstract(inv_index: dict | None) -> str | None:
    """OpenAlex의 abstract_inverted_index → 평문 초록 복원."""
    if not inv_index:
        return None
    positions: list[tuple[int, str]] = []
    for word, idxs in inv_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def fetch_works(client: httpx.Client, source_id: str, since: date) -> list[dict]:
    params = {
        "filter": f"primary_location.source.id:{source_id},from_publication_date:{since.isoformat()}",
        "per-page": 50,
        "mailto": MAILTO,
        "sort": "publication_date:desc",
    }
    r = client.get(f"{OPENALEX}/works", params=params)
    r.raise_for_status()
    return r.json().get("results", [])


def run_harvest(session: Session) -> dict:
    since = date.today() - timedelta(days=LOOKBACK_DAYS)
    added, scanned = 0, 0
    with _client() as client:
        journals = session.query(Journal).filter(Journal.is_active.is_(True)).all()
        for j in journals:
            if not j.openalex_id:
                try:
                    j.openalex_id = resolve_source_id(client, j.issn)
                except Exception as e:  # 네트워크 오류 등은 이 저널만 건너뜀
                    print(f"[harvest] source 해석 실패: {j.name} ({j.issn}) - {e}")
                    continue
                if not j.openalex_id:
                    print(f"[harvest] source 해석 실패: {j.name} ({j.issn})")
                    continue
                session.commit()
            try:
                works = fetch_works(client, j.openalex_id, since)
            except Exception as e:  # 네트워크/레이트리밋 등은 스킵
                print(f"[harvest] {j.name} 수집 실패: {e}")
                continue

            for w in works:
                scanned += 1
                doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
                if doi and session.query(Paper).filter(Paper.doi == doi).first():
                    continue  # 중복제거
                pub = w.get("publication_date")
                paper = Paper(
                    doi=doi,
                    title=w.get("title") or w.get("display_name") or "(제목 없음)",
                    abstract=invert_abstract(w.get("abstract_inverted_index")),
                    authors=[a.get("author", {}).get("display_name") for a in w.get("authorships", [])][:15],
                    journal_id=j.id,
                    published_at=date.fromisoformat(pub) if pub else None,
                    url=(w.get("primary_location") or {}).get("landing_page_url") or w.get("id"),
                    source="openalex",
                )
                session.add(paper)
                added += 1
            session.commit()

    result = {"scanned": scanned, "added": added, "since": since.isoformat()}
    print(f"[harvest] 완료: {result}")
    return result


if __name__ == "__main__":
    from .db import SessionLocal, init_db
    init_db()
    with SessionLocal() as s:
        run_harvest(s)
