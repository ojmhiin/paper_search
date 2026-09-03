"""초록 기반 AI 요약 (Concept.md Phase 2). ANTHROPIC_API_KEY가 있을 때만 동작."""
import os
import json
from sqlalchemy.orm import Session
from .models import Paper, Summary

API_KEY = os.getenv("ANTHROPIC_API_KEY")
# 현재 사용 가능한 모델명은 docs.claude.com 에서 확인 후 .env 의 CLAUDE_MODEL 로 지정하세요.
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

PROMPT = (
    "아래 논문 초록을 읽고 JSON으로만 답하라(코드블록/설명 금지).\n"
    '{{"tldr":"3~4문장 핵심 요약","key_points":["핵심 기여1","핵심 기여2"],"keywords":["kw1","kw2"]}}\n'
    "제목: {title}\n초록: {abstract}"
)


def summarize_pending(session: Session, limit: int = 20) -> int:
    """요약이 없는 논문에 대해 요약 생성. 반환: 생성 개수."""
    if not API_KEY:
        print("[summarize] ANTHROPIC_API_KEY 미설정 → 요약 건너뜀")
        return 0

    from anthropic import Anthropic
    client = Anthropic(api_key=API_KEY)

    pending = (
        session.query(Paper)
        .outerjoin(Summary)
        .filter(Summary.id.is_(None), Paper.abstract.isnot(None))
        .limit(limit)
        .all()
    )
    made = 0
    for p in pending:
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=600,
                messages=[{"role": "user", "content": PROMPT.format(title=p.title, abstract=p.abstract[:4000])}],
            )
            text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
            data = json.loads(text.strip().strip("`"))
            session.add(Summary(
                paper_id=p.id,
                tldr=data.get("tldr"),
                key_points=data.get("key_points"),
                keywords=data.get("keywords"),
                model_used=MODEL,
            ))
            session.commit()
            made += 1
        except Exception as e:
            print(f"[summarize] paper {p.id} 실패: {e}")
    print(f"[summarize] {made}건 요약 생성")
    return made
