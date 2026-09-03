import { useEffect, useState } from "react";

// Design.md 토큰 (라이브 사이트 값 확인 후 조정)
const T = {
  bg: "#FFFFFF", text: "#212121", sub: "#5F6368", accent: "#1A73E8", border: "#E0E0E0",
  font: "'Roboto', Arial, 'Noto Sans KR', sans-serif",
  maxW: 1000, padX: 32, gap: 20,
};

export default function App() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [days, setDays] = useState(7);

  const load = async (d = days) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/papers?days=${d}`);
      setPapers(await res.json());
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const harvest = async () => {
    setBusy(true);
    try {
      const res = await fetch(`/api/harvest?summarize=true`, { method: "POST" });
      const r = await res.json();
      alert(`수집 완료: 신규 ${r.added}건 / 요약 ${r.summarized ?? 0}건`);
      await load();
    } catch (e) {
      alert("수집 실패: 백엔드가 실행 중인지 확인하세요.");
    }
    setBusy(false);
  };

  useEffect(() => { load(); }, []); // eslint-disable-line

  return (
    <div style={{ fontFamily: T.font, color: T.text, background: T.bg, minHeight: "100vh" }}>
      {/* 헤더 */}
      <header style={{ borderBottom: `1px solid ${T.border}`, position: "sticky", top: 0, background: T.bg, zIndex: 10 }}>
        <div style={{ maxWidth: T.maxW, margin: "0 auto", padding: `16px ${T.padX}px`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <strong style={{ fontSize: 20 }}>ESSL Paper Study</strong>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <select value={days} onChange={(e) => { setDays(+e.target.value); load(+e.target.value); }}
              style={{ padding: "6px 8px", border: `1px solid ${T.border}`, borderRadius: 6 }}>
              <option value={1}>오늘</option>
              <option value={7}>최근 7일</option>
              <option value={30}>최근 30일</option>
            </select>
            <button onClick={harvest} disabled={busy}
              style={{ padding: "8px 14px", background: T.accent, color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" }}>
              {busy ? "수집 중…" : "지금 수집"}
            </button>
          </div>
        </div>
      </header>

      {/* 본문 */}
      <main style={{ maxWidth: T.maxW, margin: "0 auto", padding: `40px ${T.padX}px` }}>
        <h1 style={{ fontSize: 32, marginBottom: 4 }}>오늘의 신규 논문</h1>
        <p style={{ color: T.sub, marginTop: 0 }}>IF &gt; 15 저널 화이트리스트 기반 데일리 큐레이션</p>

        {loading ? (
          <p style={{ color: T.sub }}>불러오는 중…</p>
        ) : papers.length === 0 ? (
          <div style={{ padding: 24, border: `1px dashed ${T.border}`, borderRadius: 8, color: T.sub }}>
            아직 수집된 논문이 없습니다. 우측 상단 <b>지금 수집</b> 버튼을 눌러보세요.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: T.gap }}>
            {papers.map((p) => (
              <article key={p.id} style={{ border: `1px solid ${T.border}`, borderRadius: 10, padding: 20 }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 13, color: T.accent, fontWeight: 600 }}>{p.journal}</span>
                  <span style={{ fontSize: 13, color: T.sub }}>
                    {p.impact_factor ? `IF ${p.impact_factor}` : ""} {p.published_at ? `· ${p.published_at}` : ""}
                  </span>
                </div>
                <h2 style={{ fontSize: 18, margin: "8px 0" }}>
                  <a href={p.url} target="_blank" rel="noreferrer" style={{ color: T.text, textDecoration: "none" }}>{p.title}</a>
                </h2>
                {p.authors?.length ? (
                  <p style={{ fontSize: 13, color: T.sub, margin: "0 0 8px" }}>{p.authors.slice(0, 6).join(", ")}</p>
                ) : null}
                {p.tldr ? (
                  <p style={{ fontSize: 15, lineHeight: 1.5, margin: 0 }}>{p.tldr}</p>
                ) : (
                  <p style={{ fontSize: 13, color: T.sub, margin: 0 }}>AI 요약 없음 (ANTHROPIC_API_KEY 설정 시 자동 생성)</p>
                )}
                {p.keywords?.length ? (
                  <div style={{ marginTop: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {p.keywords.map((k, i) => (
                      <span key={i} style={{ fontSize: 12, color: T.sub, background: "#F1F3F4", padding: "2px 8px", borderRadius: 12 }}>{k}</span>
                    ))}
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </main>

      <footer style={{ borderTop: `1px solid ${T.border}`, marginTop: 40 }}>
        <div style={{ maxWidth: T.maxW, margin: "0 auto", padding: `16px ${T.padX}px`, fontSize: 12, color: T.sub }}>
          ESSL Paper Study · MVP scaffold
        </div>
      </footer>
    </div>
  );
}
