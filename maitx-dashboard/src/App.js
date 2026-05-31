import { useEffect, useRef, useState, useMemo } from "react";

// ─── Inline styles injected once ───────────────────────────────────────────
const GLOBAL_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --navy:    #07111F;
    --midnight:#0F172A;
    --violet:  #7C3AED;
    --cyan:    #22D3EE;
    --blue:    #3B82F6;
    --emerald: #10B981;
    --orange:  #F97316;
    --card-bg: rgba(15,23,42,0.72);
    --border:  rgba(34,211,238,0.12);
    --font:    'Sora', sans-serif;
    --mono:    'JetBrains Mono', monospace;
  }

  html, body, #root {
    height: 100%;
    background: var(--navy);
    color: #E2E8F0;
    font-family: var(--font);
    overflow-x: hidden;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--violet); border-radius: 4px; }

  /* Neural bg canvas */
  #neural-bg {
    position: fixed; inset: 0; z-index: 0;
    pointer-events: none; opacity: 0.18;
  }

  .shell {
    position: relative; z-index: 1;
    min-height: 100vh;
    padding: 24px 28px 48px;
    max-width: 1400px;
    margin: 0 auto;
  }

  /* ── Topbar ── */
  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 28px;
  }
  .brand { display: flex; align-items: center; gap: 10px; }
  .brand-orb {
    width: 36px; height: 36px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, var(--cyan), var(--violet));
    box-shadow: 0 0 18px var(--violet), 0 0 36px rgba(124,58,237,0.3);
    flex-shrink: 0;
    animation: pulse-orb 3s ease-in-out infinite;
  }
  @keyframes pulse-orb {
    0%,100% { box-shadow: 0 0 18px var(--violet), 0 0 36px rgba(124,58,237,0.3); }
    50%      { box-shadow: 0 0 28px var(--cyan),   0 0 54px rgba(34,211,238,0.35); }
  }
  .brand-text { line-height:1; }
  .brand-name {
    font-size: 20px; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .brand-sub { font-size: 10px; color: rgba(148,163,184,0.7); letter-spacing: 2px; text-transform: uppercase; margin-top:1px; }

  .ai-status {
    display: flex; align-items: center; gap: 8px;
    font-size: 12px; color: var(--emerald);
    font-family: var(--mono);
  }
  .pulse-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--emerald);
    box-shadow: 0 0 8px var(--emerald);
    animation: blink 1.4s ease-in-out infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  .topbar-right { display: flex; align-items: center; gap: 14px; }
  .user-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, var(--violet), var(--blue));
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 700; cursor: pointer;
    border: 2px solid rgba(124,58,237,0.5);
    box-shadow: 0 0 12px rgba(124,58,237,0.4);
    transition: box-shadow 0.3s;
  }
  .user-avatar:hover { box-shadow: 0 0 22px rgba(34,211,238,0.5); }

  /* ── Bento Grid ── */
  .bento {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    grid-auto-rows: 80px;
    gap: 14px;
  }

  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
    backdrop-filter: blur(16px);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    overflow: hidden;
    position: relative;
  }
  .card:hover {
    transform: translateY(-3px) scale(1.01);
    border-color: rgba(34,211,238,0.28);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(34,211,238,0.08);
  }
  .card::before {
    content:''; position:absolute; inset:0; border-radius:18px;
    background: radial-gradient(ellipse at 50% 0%, rgba(124,58,237,0.07), transparent 70%);
    pointer-events:none;
  }

  /* Spans */
  .span-4  { grid-column: span 4; }
  .span-3  { grid-column: span 3; }
  .span-6  { grid-column: span 6; }
  .span-7  { grid-column: span 7; }
  .span-5  { grid-column: span 5; }
  .span-8  { grid-column: span 8; }
  .span-12 { grid-column: span 12; }
  .row-2   { grid-row: span 2; }
  .row-3   { grid-row: span 3; }
  .row-4   { grid-row: span 4; }
  .row-5   { grid-row: span 5; }
  .row-6   { grid-row: span 6; }

  /* Stat card */
  .stat-label {
    font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;
    color: rgba(148,163,184,0.6); margin-bottom: 6px;
    font-family: var(--mono);
  }
  .stat-value {
    font-size: 38px; font-weight: 800; line-height: 1;
    letter-spacing: -2px;
  }
  .stat-sub { font-size: 12px; color: rgba(148,163,184,0.5); margin-top: 5px; }
  .stat-accent { display: inline-block; width: 28px; height: 3px; border-radius: 2px; margin-top:8px; }

  /* Cyan */
  .accent-cyan { color: var(--cyan); }
  .accent-violet { color: var(--violet); }
  .accent-orange { color: var(--orange); }
  .accent-emerald { color: var(--emerald); }
  .bg-cyan { background: var(--cyan); }
  .bg-violet { background: var(--violet); }
  .bg-orange { background: var(--orange); }
  .bg-emerald { background: var(--emerald); }

  /* Orb canvas card */
  .orb-card {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; gap: 10px;
  }
  .orb-canvas-wrap {
    width: 160px; height: 160px; position: relative; flex-shrink:0;
  }
  .orb-canvas-wrap canvas { display: block; }
  .orb-label {
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(34,211,238,0.6); font-family: var(--mono);
  }
  .orb-title {
    font-size: 15px; font-weight: 700;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  /* Radar */
  .radar-wrap { display:flex; align-items:center; justify-content:center; height:100%; }

  /* Pipeline */
  .pipeline-scroll {
    display: flex; align-items: center; gap: 0;
    overflow-x: auto; padding: 8px 0;
    scrollbar-width: none;
  }
  .pipeline-scroll::-webkit-scrollbar { display:none; }
  .pipe-step {
    display: flex; flex-direction: column; align-items: center;
    min-width: 90px; gap: 6px; flex-shrink: 0;
  }
  .pipe-icon {
    width: 40px; height: 40px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; position: relative;
  }
  .pipe-icon.active {
    box-shadow: 0 0 16px currentColor;
    animation: pipe-pulse 2s ease-in-out infinite;
  }
  @keyframes pipe-pulse {
    0%,100% { transform: scale(1); }
    50%      { transform: scale(1.08); }
  }
  .pipe-name { font-size: 10px; color: rgba(148,163,184,0.6); text-align:center; font-family: var(--mono); }
  .pipe-connector {
    flex: 1; height: 2px; min-width: 20px;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    opacity: 0.25; position: relative; overflow: hidden;
  }
  .pipe-connector.lit { opacity: 1; }
  .pipe-connector.lit::after {
    content:''; position:absolute; top:0; left:-60%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
    animation: shimmer 2s linear infinite;
  }
  @keyframes shimmer { to { left: 160%; } }

  /* AI Insights panel */
  .insights-header {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 14px;
  }
  .insights-title { font-size: 13px; font-weight: 600; color: var(--cyan); }
  .insight-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 10px 12px; border-radius: 10px;
    background: rgba(34,211,238,0.04);
    border: 1px solid rgba(34,211,238,0.08);
    margin-bottom: 8px;
    font-size: 12px; color: rgba(226,232,240,0.8);
    animation: slide-in 0.4s ease both;
  }
  .insight-item:nth-child(2) { animation-delay:0.1s }
  .insight-item:nth-child(3) { animation-delay:0.2s }
  @keyframes slide-in {
    from { opacity:0; transform:translateX(12px); }
    to   { opacity:1; transform:translateX(0); }
  }
  .insight-dot {
    width: 6px; height: 6px; border-radius: 50%;
    flex-shrink: 0; margin-top: 4px;
  }

  /* Job cards */
  .jobs-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px;
  }
  .section-title { font-size: 13px; font-weight: 600; letter-spacing: 0.3px; }
  .search-bar {
    display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 10px; padding: 7px 12px;
    font-size: 12px; font-family: var(--font); color: #E2E8F0;
    outline: none; width: 200px;
    transition: border-color 0.2s;
  }
  .search-bar:focus { border-color: rgba(34,211,238,0.35); }
  .search-bar::placeholder { color: rgba(148,163,184,0.35); }

  .job-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px; max-height: 340px; overflow-y: auto;
    scrollbar-width: thin; scrollbar-color: var(--violet) transparent;
  }
  .job-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 16px;
    transition: all 0.25s; cursor: pointer; position: relative; overflow: hidden;
  }
  .job-card:hover {
    border-color: rgba(124,58,237,0.35);
    background: rgba(124,58,237,0.06);
    transform: translateY(-2px);
  }
  .job-card-top { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
  .company-logo {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink:0;
  }
  .job-company { font-size: 13px; font-weight: 600; }
  .job-role { font-size: 11px; color: rgba(148,163,184,0.6); margin-top: 1px; }
  .job-meta { display:flex; gap:8px; flex-wrap:wrap; margin-bottom: 10px; }
  .job-tag {
    font-size: 10px; padding: 3px 8px; border-radius: 6px;
    font-family: var(--mono); font-weight: 500;
  }
  .tag-location { background:rgba(59,130,246,0.12); color:var(--blue); }
  .tag-stipend  { background:rgba(16,185,129,0.12); color:var(--emerald); }
  .tag-deadline { background:rgba(249,115,22,0.12); color:var(--orange); }
  .job-card-bottom { display:flex; align-items:center; justify-content:space-between; }
  .match-score {
    display: flex; align-items: center; gap: 5px;
    font-size: 11px; font-weight: 700;
    font-family: var(--mono);
  }
  .match-glow {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 9px; font-weight: 700;
  }
  .status-badge {
    font-size: 10px; padding: 3px 9px; border-radius: 20px;
    font-family: var(--mono); font-weight: 500; letter-spacing: 0.5px;
  }
  .status-saved     { background:rgba(124,58,237,0.15); color:var(--violet); }
  .status-applied   { background:rgba(59,130,246,0.15); color:var(--blue); }
  .status-interview { background:rgba(249,115,22,0.15); color:var(--orange); }
  .status-pending   { background:rgba(148,163,184,0.1); color:rgba(148,163,184,0.6); }

  /* Apply rate bar */
  .rate-bar-wrap { margin-top: 8px; }
  .rate-bar-bg {
    height: 6px; border-radius: 3px; background: rgba(255,255,255,0.07);
    overflow: hidden; margin-top: 4px;
  }
  .rate-bar-fill {
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 0 8px var(--cyan);
  }

  /* Section labels */
  .card-section-label {
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(148,163,184,0.4); font-family: var(--mono); margin-bottom: 4px;
  }

  /* Progress ring */
  .ring-wrap { position:relative; display:inline-block; }
  .ring-text {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    font-size: 18px; font-weight: 800; font-family: var(--mono);
  }

  /* Animations */
  @keyframes float {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-8px); }
  }
  .float { animation: float 5s ease-in-out infinite; }

  @keyframes fade-up {
    from { opacity:0; transform:translateY(20px); }
    to   { opacity:1; transform:translateY(0); }
  }
  .fade-up { animation: fade-up 0.5s ease both; }
  .delay-1 { animation-delay: 0.08s; }
  .delay-2 { animation-delay: 0.16s; }
  .delay-3 { animation-delay: 0.24s; }
  .delay-4 { animation-delay: 0.32s; }
  .delay-5 { animation-delay: 0.40s; }

  @media (max-width: 900px) {
    .span-4,.span-3,.span-5,.span-6,.span-7,.span-8,.span-12 { grid-column: span 12 !important; }
    .row-2,.row-3,.row-4,.row-5,.row-6 { grid-row: auto !important; }
    .bento { grid-template-columns: 1fr; grid-auto-rows: auto; }
    .shell { padding: 16px 14px 40px; }
  }
`;

// ─── Neural Background ───────────────────────────────────────────────────────
function NeuralBg() {
  const ref = useRef(null);
  useEffect(() => {
    const c = ref.current;
    const ctx = c.getContext("2d");
    let W, H, nodes, animId;
    const N = 60;

    function init() {
      W = c.width = window.innerWidth;
      H = c.height = window.innerHeight;
      nodes = Array.from({ length: N }, () => ({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
      }));
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);
      for (let i = 0; i < N; i++) {
        const a = nodes[i];
        a.x += a.vx; a.y += a.vy;
        if (a.x < 0 || a.x > W) a.vx *= -1;
        if (a.y < 0 || a.y > H) a.vy *= -1;
        for (let j = i + 1; j < N; j++) {
          const b = nodes[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < 160) {
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            const alpha = (1 - d / 160) * 0.6;
            ctx.strokeStyle = `rgba(34,211,238,${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
        ctx.beginPath();
        ctx.arc(a.x, a.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(124,58,237,0.7)";
        ctx.fill();
      }
      animId = requestAnimationFrame(draw);
    }

    init();
    draw();
    window.addEventListener("resize", init);
    return () => { cancelAnimationFrame(animId); window.removeEventListener("resize", init); };
  }, []);

  return <canvas id="neural-bg" ref={ref} />;
}

// ─── 3D Neural Orb (pure canvas) ────────────────────────────────────────────
function NeuralOrb({ size = 160 }) {
  const ref = useRef(null);
  useEffect(() => {
    const c = ref.current;
    const ctx = c.getContext("2d");
    const S = size * window.devicePixelRatio || size;
    c.width = c.height = S;
    c.style.width = c.style.height = size + "px";
    const cx = S / 2, cy = S / 2, r = S * 0.38;
    const pts = Array.from({ length: 180 }, (_, i) => {
      const phi = Math.acos(1 - 2 * (i + 0.5) / 180);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i;
      return { ox: Math.sin(phi) * Math.cos(theta), oy: Math.sin(phi) * Math.sin(theta), oz: Math.cos(phi) };
    });

    let t = 0;
    let animId;

    function draw() {
      ctx.clearRect(0, 0, S, S);

      // Glow base
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 1.3);
      g.addColorStop(0, "rgba(34,211,238,0.14)");
      g.addColorStop(0.5, "rgba(124,58,237,0.08)");
      g.addColorStop(1, "transparent");
      ctx.beginPath(); ctx.arc(cx, cy, r * 1.3, 0, Math.PI * 2);
      ctx.fillStyle = g; ctx.fill();

      // Sphere surface gradient
      const sg = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, 0, cx, cy, r);
      sg.addColorStop(0, "rgba(34,211,238,0.35)");
      sg.addColorStop(0.6, "rgba(124,58,237,0.18)");
      sg.addColorStop(1, "rgba(7,17,31,0.8)");
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = sg; ctx.fill();

      // Rotate points
      const cosT = Math.cos(t), sinT = Math.sin(t);
      const rotated = pts.map(p => {
        const x = p.ox * cosT - p.oz * sinT;
        const y = p.oy;
        const z = p.ox * sinT + p.oz * cosT;
        return { x, y, z };
      });

      // Connections
      for (let i = 0; i < rotated.length; i++) {
        for (let j = i + 1; j < rotated.length; j++) {
          const a = rotated[i], b = rotated[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
          if (d < 0.55 && a.z > -0.15 && b.z > -0.15) {
            const alpha = (1 - d / 0.55) * (a.z + 1) * 0.5 * 0.7;
            ctx.beginPath();
            ctx.moveTo(cx + a.x * r, cy + a.y * r);
            ctx.lineTo(cx + b.x * r, cy + b.y * r);
            ctx.strokeStyle = `rgba(34,211,238,${alpha})`;
            ctx.lineWidth = 0.7;
            ctx.stroke();
          }
        }
      }

      // Points
      for (const p of rotated) {
        if (p.z < 0) continue;
        const bri = (p.z + 1) / 2;
        const px = cx + p.x * r, py = cy + p.y * r;
        ctx.beginPath(); ctx.arc(px, py, 1.5 * bri, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(34,211,238,${bri * 0.85})`;
        ctx.fill();
      }

      // Orbiting particle
      const op = { x: Math.cos(t * 1.7) * r * 1.22, y: Math.sin(t * 1.7) * r * 0.5 };
      ctx.beginPath(); ctx.arc(cx + op.x, cy + op.y, 3, 0, Math.PI * 2);
      const pg = ctx.createRadialGradient(cx+op.x, cy+op.y,0, cx+op.x, cy+op.y, 6);
      pg.addColorStop(0,"rgba(249,115,22,1)"); pg.addColorStop(1,"transparent");
      ctx.fillStyle = pg; ctx.fill();

      const op2 = { x: Math.cos(t * 1.1 + 2.1) * r * 1.18, y: Math.sin(t * 1.1 + 2.1) * r * 0.52 };
      ctx.beginPath(); ctx.arc(cx + op2.x, cy + op2.y, 2.5, 0, Math.PI * 2);
      const pg2 = ctx.createRadialGradient(cx+op2.x,cy+op2.y,0,cx+op2.x,cy+op2.y,5);
      pg2.addColorStop(0,"rgba(124,58,237,1)"); pg2.addColorStop(1,"transparent");
      ctx.fillStyle = pg2; ctx.fill();

      t += 0.008;
      animId = requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(animId);
  }, [size]);

  return <canvas ref={ref} />;
}

// ─── Radar Chart ─────────────────────────────────────────────────────────────
function Radar({ data }) {
  const ref = useRef(null);
  useEffect(() => {
    const c = ref.current;
    const ctx = c.getContext("2d");
    const S = 200, cx = S / 2, cy = S / 2, r = 75;
    c.width = c.height = S;
    c.style.width = c.style.height = "170px";

    const labels = data.map(d => d.label);
    const values = data.map(d => d.value);
    const n = labels.length;
    const angles = labels.map((_, i) => (Math.PI * 2 * i) / n - Math.PI / 2);

    ctx.clearRect(0, 0, S, S);

    // Grid rings
    for (let ring = 1; ring <= 4; ring++) {
      ctx.beginPath();
      angles.forEach((a, i) => {
        const fr = (ring / 4) * r;
        const x = cx + Math.cos(a) * fr, y = cy + Math.sin(a) * fr;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.strokeStyle = "rgba(34,211,238,0.08)";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Spokes
    angles.forEach(a => {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r);
      ctx.strokeStyle = "rgba(34,211,238,0.1)";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Data area
    ctx.beginPath();
    angles.forEach((a, i) => {
      const rv = values[i] * r;
      const x = cx + Math.cos(a) * rv, y = cy + Math.sin(a) * rv;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.closePath();
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    g.addColorStop(0, "rgba(34,211,238,0.25)");
    g.addColorStop(1, "rgba(124,58,237,0.08)");
    ctx.fillStyle = g; ctx.fill();
    ctx.strokeStyle = "rgba(34,211,238,0.7)";
    ctx.lineWidth = 1.5; ctx.stroke();

    // Points + labels
    angles.forEach((a, i) => {
      const rv = values[i] * r;
      const x = cx + Math.cos(a) * rv, y = cy + Math.sin(a) * rv;
      ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fillStyle = "#22D3EE"; ctx.fill();

      const lx = cx + Math.cos(a) * (r + 16), ly = cy + Math.sin(a) * (r + 16);
      ctx.font = "600 9px 'JetBrains Mono', monospace";
      ctx.fillStyle = "rgba(148,163,184,0.7)";
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(labels[i].toUpperCase(), lx, ly);
    });
  }, [data]);

  return <canvas ref={ref} />;
}

// ─── Progress Ring ────────────────────────────────────────────────────────────
function Ring({ pct, color, size = 80 }) {
  const ref = useRef(null);
  useEffect(() => {
    const c = ref.current;
    const ctx = c.getContext("2d");
    const S = size * 2; c.width = c.height = S; c.style.width = c.style.height = size + "px";
    const cx = S/2, cy = S/2, r = S*0.38, stroke = S*0.07;
    ctx.clearRect(0,0,S,S);
    ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.strokeStyle="rgba(255,255,255,0.05)"; ctx.lineWidth=stroke; ctx.stroke();
    const start = -Math.PI/2, end = start + (Math.PI*2*(pct/100));
    ctx.beginPath(); ctx.arc(cx,cy,r,start,end);
    ctx.strokeStyle=color; ctx.lineWidth=stroke; ctx.lineCap="round"; ctx.stroke();
    ctx.shadowBlur=12; ctx.shadowColor=color; ctx.stroke();
  }, [pct, color, size]);
  return <canvas ref={ref} />;
}

// ─── Data ────────────────────────────────────────────────────────────────────
const JOBS = [
  { company:"TCS", role:"Software Intern", logo:"🏢", stipend:"₹15k/mo", location:"Mumbai", deadline:"Jun 12", match:94, status:"applied" },
  { company:"Infosys", role:"ML Intern", logo:"🤖", stipend:"₹12k/mo", location:"Pune", deadline:"Jun 18", match:87, status:"saved" },
  { company:"Razorpay", role:"Backend Intern", logo:"⚡", stipend:"₹25k/mo", location:"Bangalore", deadline:"Jun 9", match:91, status:"interview" },
  { company:"Zomato", role:"Data Analyst", logo:"🍔", stipend:"₹18k/mo", location:"Gurgaon", deadline:"Jun 22", match:78, status:"pending" },
  { company:"CRED", role:"Product Intern", logo:"💳", stipend:"₹20k/mo", location:"Bangalore", deadline:"Jun 15", match:83, status:"saved" },
  { company:"Swiggy", role:"iOS Intern", logo:"🛵", stipend:"₹22k/mo", location:"Hyderabad", deadline:"Jun 28", match:76, status:"pending" },
];

const PIPELINE = [
  { icon:"🧠", label:"Detected", color:"#22D3EE", bg:"rgba(34,211,238,0.12)", active:true },
  { icon:"⚙️", label:"Processed", color:"#3B82F6", bg:"rgba(59,130,246,0.12)", active:true },
  { icon:"💾", label:"Saved", color:"#7C3AED", bg:"rgba(124,58,237,0.12)", active:true },
  { icon:"📩", label:"Applied", color:"#F97316", bg:"rgba(249,115,22,0.12)", active:false },
  { icon:"🎯", label:"Interview", color:"#10B981", bg:"rgba(16,185,129,0.12)", active:false },
  { icon:"🏆", label:"Offer", color:"#FBBF24", bg:"rgba(251,191,36,0.12)", active:false },
];

const RADAR_DATA = [
  { label:"Applied", value:0.75 },
  { label:"Pending", value:0.60 },
  { label:"Interview", value:0.35 },
  { label:"Saved", value:0.90 },
  { label:"Rejected", value:0.20 },
];

const INSIGHTS = [
  { text:"3 new internships detected from WhatsApp today", color:"#22D3EE" },
  { text:"TCS is most active — 4 roles this week", color:"#7C3AED" },
  { text:"Your apply rate is 68% — above avg 51%", color:"#10B981" },
  { text:"Deadline alert: Razorpay closes in 2 days", color:"#F97316" },
];

// ─── App ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [search, setSearch] = useState("");
  const [barW, setBarW] = useState(0);

  useEffect(() => {
    const style = document.createElement("style");
    style.textContent = GLOBAL_CSS;
    document.head.appendChild(style);
    setTimeout(() => setBarW(68), 600);
    return () => document.head.removeChild(style);
  }, []);

  const filtered = useMemo(() =>
    JOBS.filter(j =>
      j.company.toLowerCase().includes(search.toLowerCase()) ||
      j.role.toLowerCase().includes(search.toLowerCase())
    ), [search]);

  const matchColor = (m) =>
    m >= 90 ? "#10B981" : m >= 80 ? "#22D3EE" : m >= 70 ? "#F97316" : "#94A3B8";

  return (
    <>
      <NeuralBg />

      <div className="shell">
        {/* ── Topbar ── */}
        <div className="topbar fade-up">
          <div className="brand">
            <div className="brand-orb" />
            <div className="brand-text">
              <div className="brand-name">MAITX AI</div>
              <div className="brand-sub">Internship Intelligence Platform</div>
            </div>
          </div>
          <div className="topbar-right">
            <div className="ai-status">
              <div className="pulse-dot" />
              AI ONLINE · SCANNING
            </div>
            <div className="user-avatar">M</div>
          </div>
        </div>

        {/* ── Bento Grid ── */}
        <div className="bento">

          {/* Stat: Total */}
          <div className="card span-3 row-2 fade-up delay-1" style={{ display:"flex", flexDirection:"column", justifyContent:"space-between" }}>
            <div className="stat-label">Total Jobs</div>
            <div>
              <div className="stat-value accent-cyan">25</div>
              <div className="stat-sub">+3 today via WhatsApp</div>
              <div className="stat-accent bg-cyan" />
            </div>
          </div>

          {/* Stat: Applied */}
          <div className="card span-3 row-2 fade-up delay-2" style={{ display:"flex", flexDirection:"column", justifyContent:"space-between" }}>
            <div className="stat-label">Applied</div>
            <div>
              <div className="stat-value accent-violet">17</div>
              <div className="stat-sub">68% apply rate</div>
              <div className="stat-accent bg-violet" />
            </div>
          </div>

          {/* Stat: Pending */}
          <div className="card span-3 row-2 fade-up delay-3" style={{ display:"flex", flexDirection:"column", justifyContent:"space-between" }}>
            <div className="stat-label">Pending</div>
            <div>
              <div className="stat-value accent-orange">8</div>
              <div className="stat-sub">Awaiting review</div>
              <div className="stat-accent bg-orange" />
            </div>
          </div>

          {/* Stat: Interviews */}
          <div className="card span-3 row-2 fade-up delay-4" style={{ display:"flex", flexDirection:"column", justifyContent:"space-between" }}>
            <div className="stat-label">Interviews</div>
            <div>
              <div className="stat-value accent-emerald">3</div>
              <div className="stat-sub">2 this week</div>
              <div className="stat-accent bg-emerald" />
            </div>
          </div>

          {/* Neural Orb */}
          <div className="card span-4 row-5 orb-card float fade-up delay-2" style={{ minHeight: 300 }}>
            <div className="orb-label">AI Core</div>
            <div className="orb-canvas-wrap">
              <NeuralOrb size={160} />
            </div>
            <div className="orb-title">Neural Engine Active</div>
            <div style={{ fontSize:11, color:"rgba(148,163,184,0.45)", fontFamily:"var(--mono)", textAlign:"center" }}>
              Scanning 12 WhatsApp groups
            </div>
          </div>

          {/* Radar */}
          <div className="card span-4 row-5 fade-up delay-3" style={{ minHeight: 300 }}>
            <div className="card-section-label">Activity Radar</div>
            <div className="radar-wrap">
              <Radar data={RADAR_DATA} />
            </div>
          </div>

          {/* AI Insights */}
          <div className="card span-4 row-5 fade-up delay-4" style={{ minHeight: 300 }}>
            <div className="insights-header">
              <span style={{ fontSize:16 }}>🧠</span>
              <span className="insights-title">AI Insights</span>
              <div className="pulse-dot" style={{ marginLeft:"auto" }} />
            </div>
            {INSIGHTS.map((ins, i) => (
              <div className="insight-item" key={i}>
                <div className="insight-dot" style={{ background: ins.color, boxShadow:`0 0 6px ${ins.color}` }} />
                <span>{ins.text}</span>
              </div>
            ))}
          </div>

          {/* Apply rate */}
          <div className="card span-6 row-2 fade-up delay-3" style={{ display:"flex", flexDirection:"column", justifyContent:"space-between" }}>
            <div>
              <div className="card-section-label">Apply Rate</div>
              <div style={{ display:"flex", alignItems:"center", gap:12, marginTop:4 }}>
                <Ring pct={68} color="#22D3EE" size={64} />
                <div>
                  <div style={{ fontSize:28, fontWeight:800, fontFamily:"var(--mono)", color:"var(--cyan)" }}>68%</div>
                  <div style={{ fontSize:11, color:"rgba(148,163,184,0.5)" }}>17 of 25 applied</div>
                </div>
              </div>
            </div>
            <div className="rate-bar-wrap">
              <div style={{ fontSize:10, color:"rgba(148,163,184,0.4)", fontFamily:"var(--mono)" }}>vs avg 51%</div>
              <div className="rate-bar-bg">
                <div className="rate-bar-fill" style={{ width: barW + "%" }} />
              </div>
            </div>
          </div>

          {/* Offer rate */}
          <div className="card span-6 row-2 fade-up delay-4" style={{ display:"flex", flexDirection:"column", justifyContent:"space-between" }}>
            <div>
              <div className="card-section-label">Interview Conversion</div>
              <div style={{ display:"flex", alignItems:"center", gap:12, marginTop:4 }}>
                <Ring pct={40} color="#7C3AED" size={64} />
                <div>
                  <div style={{ fontSize:28, fontWeight:800, fontFamily:"var(--mono)", color:"var(--violet)" }}>40%</div>
                  <div style={{ fontSize:11, color:"rgba(148,163,184,0.5)" }}>3 of 7 progressed</div>
                </div>
              </div>
            </div>
            <div className="rate-bar-wrap">
              <div style={{ fontSize:10, color:"rgba(148,163,184,0.4)", fontFamily:"var(--mono)" }}>Getting better each week</div>
              <div className="rate-bar-bg">
                <div className="rate-bar-fill" style={{ width:"40%", background:"linear-gradient(90deg,#7C3AED,#3B82F6)", boxShadow:"0 0 8px #7C3AED" }} />
              </div>
            </div>
          </div>

          {/* Pipeline */}
          <div className="card span-12 row-2 fade-up delay-5">
            <div className="card-section-label" style={{ marginBottom:10 }}>Internship Pipeline</div>
            <div className="pipeline-scroll">
              {PIPELINE.map((step, i) => (
                <>
                  <div className="pipe-step" key={i}>
                    <div className="pipe-icon" style={{ background: step.bg, color: step.color }}>
                      <span className={step.active ? "active" : ""}>{step.icon}</span>
                    </div>
                    <div className="pipe-name" style={{ color: step.active ? step.color : undefined }}>{step.label}</div>
                  </div>
                  {i < PIPELINE.length - 1 && (
                    <div className={`pipe-connector${step.active ? " lit" : ""}`} key={`c${i}`} />
                  )}
                </>
              ))}
            </div>
          </div>

          {/* Job List */}
          <div className="card span-12 row-6 fade-up delay-5" style={{ minHeight:300 }}>
            <div className="jobs-header">
              <span className="section-title">🚀 AI Extracted Opportunities</span>
              <input
                className="search-bar"
                placeholder="Search company or role…"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <div className="job-grid">
              {filtered.map((job, i) => (
                <div className="job-card" key={i}>
                  <div className="job-card-top">
                    <div className="company-logo" style={{ background:`rgba(34,211,238,0.08)`, border:"1px solid rgba(34,211,238,0.12)" }}>
                      {job.logo}
                    </div>
                    <div>
                      <div className="job-company">{job.company}</div>
                      <div className="job-role">{job.role}</div>
                    </div>
                  </div>
                  <div className="job-meta">
                    <span className="job-tag tag-location">📍 {job.location}</span>
                    <span className="job-tag tag-stipend">💰 {job.stipend}</span>
                    <span className="job-tag tag-deadline">⏰ {job.deadline}</span>
                  </div>
                  <div className="job-card-bottom">
                    <div className="match-score">
                      <div className="match-glow" style={{
                        background: `rgba(${job.match >= 90 ? "16,185,129" : job.match >= 80 ? "34,211,238" : "249,115,22"},0.12)`,
                        color: matchColor(job.match),
                        boxShadow: `0 0 10px ${matchColor(job.match)}44`,
                        fontSize: 9, fontWeight: 700, fontFamily:"var(--mono)"
                      }}>{job.match}%</div>
                      <span style={{ color: matchColor(job.match) }}>AI Match</span>
                    </div>
                    <div className={`status-badge status-${job.status}`}>{job.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </>
  );
}