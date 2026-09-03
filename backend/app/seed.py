"""IF>15 저널 화이트리스트 시드 (Concept.md §2 전략).

주의: ISSN/IF 값은 예시이며, 실제 운영 전 최신 JCR/발행처 정보로 검증하세요.
openalex_id는 비워두면 harvest 시 ISSN으로 자동 해석되어 채워집니다.
"""
from sqlalchemy.orm import Session
from .models import Journal

# (name, 대표 ISSN, IF(예시), field)
SEED = [
    ("Nature",                       "1476-4687", 50.5, "multidisciplinary"),
    ("Nature Energy",                "2058-7546", 56.7, "energy"),
    ("Joule",                        "2542-4351", 38.6, "energy"),
    ("Energy & Environmental Science","1754-5706", 32.4, "energy"),
    ("Advanced Materials",           "1521-4095", 27.4, "materials"),
    ("Advanced Energy Materials",    "1614-6840", 24.4, "energy"),
    ("Energy Storage Materials",     "2405-8297", 20.4, "energy"),
    ("Journal of the American Chemical Society", "1520-5126", 15.0, "chemistry"),
    ("Angewandte Chemie Int. Ed.",   "1521-3773", 16.1, "chemistry"),
]


def seed_journals(session: Session) -> None:
    existing = {j.issn for j in session.query(Journal).all()}
    added = 0
    for name, issn, impact, field in SEED:
        if issn in existing:
            continue
        session.add(Journal(name=name, issn=issn, impact_factor=impact, field=field, is_active=True))
        added += 1
    if added:
        session.commit()
        print(f"[seed] {added}개 저널 추가 완료")
    else:
        print("[seed] 이미 시드됨 (건너뜀)")
