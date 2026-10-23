/* ============================================================
   Interactive demos, part B (topics 24–51)
   ============================================================ */
(function () {
  'use strict';

  const DEMOS = (window.GA_DEMOS = window.GA_DEMOS || {});
  const T = (key) => window.GA_T(key);
  const C = {
    acid: '#c8f751', mint: '#6ee7b7', sky: '#7dd3fc', amber: '#fbbf6b',
    rose: '#fda4af', violet: '#c4b5fd', ink: '#e7eddf', dim: '#6b7368'
  };
  const TAU = Math.PI * 2;

  function makeStage(el) {
    const body = el.querySelector('.demo-body');
    const stageEl = document.createElement('div');
    stageEl.className = 'demo-stage';
    const canvas = document.createElement('canvas');
    stageEl.appendChild(canvas);
    const controls = document.createElement('div');
    controls.className = 'demo-controls';
    const readout = document.createElement('div');
    readout.className = 'demo-readout';
    body.append(stageEl, controls, readout);
    const ctx = canvas.getContext('2d');
    const st = { canvas, ctx, controls, readout, w: 320, h: 260 };
    function fit() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const r = canvas.getBoundingClientRect();
      if (!r.width) return;
      canvas.width = Math.round(r.width * dpr);
      canvas.height = Math.round(r.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      st.w = r.width;
      st.h = r.height;
    }
    st.fit = fit;
    if (window.ResizeObserver) new ResizeObserver(fit).observe(canvas);
    requestAnimationFrame(fit);
    return st;
  }

  function slider(parent, label, min, max, value, step, fmt, oninput) {
    const wrap = document.createElement('label');
    wrap.className = 'ctl';
    const k = document.createElement('span');
    k.className = 'k';
    k.textContent = label;
    const input = document.createElement('input');
    input.type = 'range';
    input.min = min; input.max = max; input.step = step; input.value = value;
    const out = document.createElement('output');
    out.textContent = fmt(+value);
    input.addEventListener('input', () => {
      out.textContent = fmt(+input.value);
      if (oninput) oninput(+input.value);
    });
    wrap.append(k, input, out);
    parent.appendChild(wrap);
    return { input, get value() { return +input.value; }, set(v) { input.value = v; out.textContent = fmt(+v); } };
  }

  function toggle(parent, label, value, onchange) {
    const wrap = document.createElement('label');
    wrap.className = 'ctl';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.checked = !!value;
    input.style.accentColor = C.acid;
    const span = document.createElement('span');
    span.className = 'k';
    span.textContent = label;
    input.addEventListener('change', () => onchange && onchange(input.checked));
    wrap.append(input, span);
    parent.appendChild(wrap);
    return input;
  }

  function select(parent, label, options, onchange) {
    const wrap = document.createElement('label');
    wrap.className = 'ctl';
    const k = document.createElement('span');
    k.className = 'k';
    k.textContent = label;
    const sel = document.createElement('select');
    options.forEach(([v, t]) => {
      const o = document.createElement('option');
      o.value = v; o.textContent = t;
      sel.appendChild(o);
    });
    sel.addEventListener('change', () => onchange(sel.value));
    wrap.append(k, sel);
    parent.appendChild(wrap);
    return sel;
  }

  function button(parent, label, onclick) {
    const b = document.createElement('button');
    b.className = 'chip';
    b.type = 'button';
    b.textContent = label;
    b.addEventListener('click', onclick);
    parent.appendChild(b);
    return b;
  }

  function readout(parent, keys) {
    const cells = {};
    const frag = document.createDocumentFragment();
    keys.forEach(([id, label]) => {
      const span = document.createElement('span');
      span.innerHTML = label + ' <b>—</b>';
      cells[id] = span.querySelector('b');
      frag.appendChild(span);
    });
    parent.appendChild(frag);
    return (obj) => Object.keys(obj).forEach((k) => {
      if (cells[k]) cells[k].textContent = obj[k];
    });
  }

  function loop(draw) {
    let raf = null, last = 0, paused = false;
    function tick(now) {
      const dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016;
      last = now;
      if (!paused) {
        try { draw(dt, now / 1000); } catch (e) { /* noop */ }
      }
      raf = requestAnimationFrame(tick);
    }
    return {
      start() { if (raf !== null) return; last = 0; raf = requestAnimationFrame(tick); },
      stop() { if (raf !== null) cancelAnimationFrame(raf); raf = null; },
      toggle() { paused = !paused; return paused; },
      get paused() { return paused; },
      reset: null
    };
  }

  function clear(st, color) {
    st.ctx.clearRect(0, 0, st.w, st.h);
    if (color) { st.ctx.fillStyle = color; st.ctx.fillRect(0, 0, st.w, st.h); }
  }

  function grid(st, step, color) {
    const ctx = st.ctx;
    ctx.save();
    ctx.strokeStyle = color || 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x <= st.w; x += step) { ctx.moveTo(x, 0); ctx.lineTo(x, st.h); }
    for (let y = 0; y <= st.h; y += step) { ctx.moveTo(0, y); ctx.lineTo(st.w, y); }
    ctx.stroke();
    ctx.restore();
  }

  function label(ctx, text, x, y, color, size, align) {
    ctx.fillStyle = color || C.dim;
    ctx.font = (size || 10) + 'px ui-monospace, Menlo, monospace';
    ctx.textAlign = align || 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
  }

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ============================================================
     9. Cloth (Verlet)
     ============================================================ */
  DEMOS.cloth = function (el) {
    const st = makeStage(el);
    const params = { wind: 0.7, stiffness: 7 };
    const COLS = 22, ROWS = 14;
    let pts = [];
    let cons = [];
    let spacing = 16;
    let dragIdx = -1;

    const setReadout = readout(st.readout, [['pts', T('particles')], ['it', T('iterations')], ['wind', T('wind')]]);

    function reset() {
      const top = 26;
      const usableW = Math.max(240, st.w - 60);
      spacing = Math.min(usableW / (COLS - 1), (st.h - 60) / (ROWS - 1), 22);
      const ox = (st.w - spacing * (COLS - 1)) / 2;
      pts = [];
      cons = [];
      for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
          pts.push({
            x: ox + x * spacing,
            y: top + y * spacing,
            px: ox + x * spacing,
            py: top + y * spacing,
            pinned: y === 0
          });
        }
      }
      const idx = (x, y) => y * COLS + x;
      for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
          // structural: they hold the shape of the mesh
          if (x < COLS - 1) cons.push([idx(x, y), idx(x + 1, y), spacing, 1.0]);
          if (y < ROWS - 1) cons.push([idx(x, y), idx(x, y + 1), spacing, 1.0]);
          // bend: they resist folding, but only weakly
          if (x < COLS - 2) cons.push([idx(x, y), idx(x + 2, y), spacing * 2, 0.12]);
          if (y < ROWS - 2) cons.push([idx(x, y), idx(x, y + 2), spacing * 2, 0.12]);
          // shear: very soft, otherwise the cloth turns into a stiff sheet
          if (x < COLS - 1 && y < ROWS - 1) {
            const d = spacing * Math.SQRT2;
            cons.push([idx(x, y), idx(x + 1, y + 1), d, 0.18]);
            cons.push([idx(x + 1, y), idx(x, y + 1), d, 0.18]);
          }
        }
      }
    }

    let simTime = 0;
    function simulate(dt) {
      const g = 950;
      simTime += dt;
      const gust = 2600 * params.wind;
      const turb = 1.0 + 0.35 * Math.sin(simTime * 2.3);
      for (const p of pts) {
        if (p.pinned) { p.px = p.x; p.py = p.y; continue; }
        const vx = (p.x - p.px) * 0.982;
        const vy = (p.y - p.py) * 0.982;
        p.px = p.x; p.py = p.y;
        const sway = Math.sin(p.x * 0.045 + p.y * 0.03 + simTime * 3.1) * 0.55 + 0.45;
        p.x += vx + gust * turb * sway * dt * dt;
        p.y += vy + g * dt * dt;
      }
      for (let it = 0; it < params.stiffness; it++) {
        for (let k = 0; k < cons.length; k++) {
          const c = cons[k];
          const pa = pts[c[0]], pb = pts[c[1]];
          const dx = pb.x - pa.x, dy = pb.y - pa.y;
          const d = Math.hypot(dx, dy) || 1e-9;
          const diff = (d - c[2]) / d * 0.5 * c[3];
          if (!pa.pinned) { pa.x += dx * diff; pa.y += dy * diff; }
          if (!pb.pinned) { pb.x -= dx * diff; pb.y -= dy * diff; }
        }
      }
      for (const p of pts) {
        if (p.y > st.h - 4 && !p.pinned) { p.y = st.h - 4; p.py = p.y + 1; }
        if (p.x < 2) p.x = 2;
        if (p.x > st.w - 2) p.x = st.w - 2;
      }
    }

    function pick(e) {
      const r = st.canvas.getBoundingClientRect();
      const mx = e.clientX - r.left, my = e.clientY - r.top;
      let best = -1, bd = 1e9;
      pts.forEach((p, i) => {
        const d = Math.hypot(p.x - mx, p.y - my);
        if (d < bd) { bd = d; best = i; }
      });
      if (bd < spacing * 1.5) dragIdx = best;
    }
    st.canvas.addEventListener('pointerdown', (e) => {
      st.canvas.setPointerCapture(e.pointerId);
      pick(e);
    });
    st.canvas.addEventListener('pointermove', (e) => {
      if (dragIdx < 0) return;
      const r = st.canvas.getBoundingClientRect();
      const p = pts[dragIdx];
      p.x = e.clientX - r.left;
      p.y = e.clientY - r.top;
      p.px = p.x; p.py = p.y;
    });
    st.canvas.addEventListener('pointerup', () => { dragIdx = -1; });
    st.canvas.addEventListener('pointercancel', () => { dragIdx = -1; });

    slider(st.controls, T('wind'), -1, 1, params.wind, 0.05, v => v.toFixed(2), v => params.wind = v);
    slider(st.controls, T('stiffness'), 1, 12, params.stiffness, 1, v => v + T('res'), v => params.stiffness = v);
    button(st.controls, T('reset_btn'), () => reset());

    setTimeout(reset, 0);

    const handle = loop((dt) => {
      if (!pts.length) reset();
      const sub = Math.min(3, Math.max(1, Math.round(dt / 0.008)));
      for (let i = 0; i < sub; i++) simulate(dt / sub);
      clear(st, '#07080b');
      grid(st, 40);

      st.ctx.lineWidth = 1;
      for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
          const i = y * COLS + x;
          if (x < COLS - 1) {
            st.ctx.strokeStyle = 'rgba(125,211,252,' + (0.22 + y / ROWS * 0.45) + ')';
            st.ctx.beginPath();
            st.ctx.moveTo(pts[i].x, pts[i].y);
            st.ctx.lineTo(pts[i + 1].x, pts[i + 1].y);
            st.ctx.stroke();
          }
          if (y < ROWS - 1) {
            st.ctx.strokeStyle = 'rgba(196,181,253,' + (0.18 + y / ROWS * 0.3) + ')';
            st.ctx.beginPath();
            st.ctx.moveTo(pts[i].x, pts[i].y);
            st.ctx.lineTo(pts[i + COLS].x, pts[i + COLS].y);
            st.ctx.stroke();
          }
        }
      }
      for (const p of pts) {
        if (p.pinned) {
          st.ctx.fillStyle = C.acid;
          st.ctx.beginPath(); st.ctx.arc(p.x, p.y, 2, 0, TAU); st.ctx.fill();
        }
      }
      label(st.ctx, 'Verlet · ' + params.stiffness + T('iterations_unit'), 10, 13, C.dim, 9);
      setReadout({
        pts: pts.length,
        it: params.stiffness,
        wind: params.wind.toFixed(2)
      });
    });
    handle.reset = reset;
    return handle;
  };

  /* ============================================================
     10. Portals
     ============================================================ */
  DEMOS.portal = function (el) {
    const st = makeStage(el);
    const params = { speed: 150, rotate: true };
    const portals = [
      { x: 0.26, y: 0.52, color: C.sky, n: 0 },
      { x: 0.74, y: 0.52, color: C.violet, n: Math.PI }
    ];
    let ball = { x: 0, y: 0, vx: 0, vy: 0 };
    let trail = [];
    let cooldown = 0;
    let crossings = 0;
    const setReadout = readout(st.readout, [['cross', T('transitions')], ['speed', T('speed')], ['state', T('state')]]);

    function reset() {
      ball = { x: st.w * 0.5, y: st.h * 0.24, vx: params.speed * 0.7, vy: params.speed * 0.45 };
      trail = [];
      crossings = 0;
      cooldown = 0;
    }

    slider(st.controls, T('speed'), 60, 280, params.speed, 5, v => v, v => { params.speed = v; });
    toggle(st.controls, T('turn90'), true, v => params.rotate = v);

    const handle = loop((dt) => {
      clear(st, '#07080b');
      grid(st, 40);

      const W = st.w, H = st.h;
      const P = portals.map(p => ({ x: p.x * W, y: p.y * H, color: p.color }));
      const rx = 17, ry = 34;

      // move
      ball.x += ball.vx * dt;
      ball.y += ball.vy * dt;
      if (ball.x < 8) { ball.x = 8; ball.vx = Math.abs(ball.vx); }
      if (ball.x > W - 8) { ball.x = W - 8; ball.vx = -Math.abs(ball.vx); }
      if (ball.y < 8) { ball.y = 8; ball.vy = Math.abs(ball.vy); }
      if (ball.y > H - 8) { ball.y = H - 8; ball.vy = -Math.abs(ball.vy); }

      cooldown = Math.max(0, cooldown - dt);
      for (let i = 0; i < 2; i++) {
        const a = P[i], b = P[1 - i];
        if (cooldown > 0) break;
        if (Math.hypot(ball.x - a.x, ball.y - a.y) < 22) {
          ball.x = b.x + (i === 0 ? 26 : -26);
          ball.y = b.y;
          if (params.rotate) {
            const vx = ball.vx, vy = ball.vy;
            ball.vx = -vy;
            ball.vy = vx;
          }
          cooldown = 0.45;
          crossings++;
        }
      }

      trail.push({ x: ball.x, y: ball.y });
      if (trail.length > 60) trail.shift();

      // portals
      P.forEach((p, i) => {
        const t = performance.now() * 0.001;
        st.ctx.save();
        st.ctx.translate(p.x, p.y);
        st.ctx.rotate(Math.sin(t * 0.7 + i) * 0.04);
        const ring = st.ctx.createRadialGradient(0, 0, 4, 0, 0, ry);
        ring.addColorStop(0, 'rgba(7,8,11,0.95)');
        ring.addColorStop(0.6, p.color + '55');
        ring.addColorStop(1, p.color + '00');
        st.ctx.fillStyle = ring;
        st.ctx.beginPath();
        st.ctx.ellipse(0, 0, rx, ry, 0, 0, TAU);
        st.ctx.fill();
        st.ctx.strokeStyle = p.color;
        st.ctx.lineWidth = 2;
        st.ctx.beginPath();
        st.ctx.ellipse(0, 0, rx, ry, 0, 0, TAU);
        st.ctx.stroke();
        st.ctx.restore();
        label(st.ctx, i === 0 ? T('entrance') : T('exit'), p.x, p.y + ry + 12, p.color, 9, 'center');
      });

      // trail
      for (let i = 0; i < trail.length; i++) {
        const t = trail[i];
        st.ctx.fillStyle = 'rgba(200,247,81,' + (i / trail.length * 0.5) + ')';
        st.ctx.beginPath();
        st.ctx.arc(t.x, t.y, 1.4, 0, TAU);
        st.ctx.fill();
      }

      // ball
      const glow = st.ctx.createRadialGradient(ball.x, ball.y, 0, ball.x, ball.y, 18);
      glow.addColorStop(0, 'rgba(200,247,81,0.85)');
      glow.addColorStop(1, 'rgba(200,247,81,0)');
      st.ctx.fillStyle = glow;
      st.ctx.beginPath(); st.ctx.arc(ball.x, ball.y, 18, 0, TAU); st.ctx.fill();
      st.ctx.fillStyle = '#f4ffd6';
      st.ctx.beginPath(); st.ctx.arc(ball.x, ball.y, 4, 0, TAU); st.ctx.fill();

      // vector
      st.ctx.strokeStyle = 'rgba(200,247,81,0.55)';
      st.ctx.beginPath();
      st.ctx.moveTo(ball.x, ball.y);
      st.ctx.lineTo(ball.x + ball.vx * 0.11, ball.y + ball.vy * 0.11);
      st.ctx.stroke();

      setReadout({
        cross: crossings,
        speed: Math.round(Math.hypot(ball.vx, ball.vy)),
        state: params.rotate ? T('vel_turn') : T('translate')
      });
    });
    setTimeout(reset, 0);
    handle.reset = reset;
    return handle;
  };

  /* ============================================================
     11. Chaos / bifurcation
     ============================================================ */
  DEMOS.chaos = function (el) {
    const st = makeStage(el);
    const params = { r: 3.62 };
    let bmp = null;
    let lastW = 0;
    const setReadout = readout(st.readout, [['r', T('param_r')], ['lyap', T('lyapunov')], ['regime', T('mode')]]);

    function buildBifurcation() {
      const w = Math.max(160, Math.round(st.w / 1.5));
      const h = Math.max(90, Math.round(st.h * 0.62));
      bmp = document.createElement('canvas');
      bmp.width = w; bmp.height = h;
      const bctx = bmp.getContext('2d');
      const img = bctx.createImageData(w, h);
      const rMin = 2.5, rMax = 4.0;
      for (let x = 0; x < w; x++) {
        const r = rMin + (x / (w - 1)) * (rMax - rMin);
        let v = 0.5;
        for (let i = 0; i < 180; i++) v = r * v * (1 - v);
        for (let i = 0; i < 220; i++) {
          v = r * v * (1 - v);
          const y = Math.round((1 - v) * (h - 1));
          const idx = (y * w + x) * 4;
          img.data[idx] = 200;
          img.data[idx + 1] = 247;
          img.data[idx + 2] = 81;
          img.data[idx + 3] = Math.min(255, img.data[idx + 3] + 170);
        }
      }
      bctx.putImageData(img, 0, 0);
      lastW = st.w;
    }

    function lyapunov(r) {
      let v = 0.4, sum = 0;
      for (let i = 0; i < 120; i++) v = r * v * (1 - v);
      for (let i = 0; i < 600; i++) {
        v = r * v * (1 - v);
        const d = Math.abs(r * (1 - 2 * v));
        sum += Math.log(Math.max(d, 1e-12));
      }
      return sum / 600;
    }

    slider(st.controls, 'r', 2.5, 4, params.r, 0.001, v => v.toFixed(3), v => params.r = v);

    const handle = loop((dt, time) => {
      clear(st, '#07080b');
      if (!bmp || Math.abs(st.w - lastW) > 20) buildBifurcation();
      const imgH = st.h * 0.62;
      st.ctx.drawImage(bmp, 0, 0, st.w, imgH);

      const rMin = 2.5, rMax = 4;
      const x = ((params.r - rMin) / (rMax - rMin)) * st.w;
      st.ctx.strokeStyle = C.rose;
      st.ctx.lineWidth = 1.5;
      st.ctx.beginPath();
      st.ctx.moveTo(x, 0);
      st.ctx.lineTo(x, imgH);
      st.ctx.stroke();
      st.ctx.fillStyle = C.rose;
      st.ctx.beginPath(); st.ctx.arc(x, imgH * 0.5, 3, 0, TAU); st.ctx.fill();

      // time series strip
      const by = imgH + 10;
      const bh = st.h - by - 8;
      const v0 = 0.4;
      let v = v0;
      for (let i = 0; i < 60; i++) v = params.r * v * (1 - v);
      const n = 54;
      st.ctx.strokeStyle = 'rgba(255,255,255,0.7)';
      st.ctx.lineWidth = 1;
      st.ctx.beginPath();
      for (let i = 0; i < n; i++) {
        v = params.r * v * (1 - v);
        const px = 10 + (i / n) * (st.w - 20);
        const py = by + bh - v * bh;
        if (i === 0) st.ctx.moveTo(px, py); else st.ctx.lineTo(px, py);
      }
      st.ctx.stroke();
      label(st.ctx, 'xₙ₊₁ = r·xₙ(1−xₙ)', 10, by - 2, C.dim, 9);

      const lam = lyapunov(params.r);
      let regime = T('chaos');
      if (lam < -0.02) regime = T('fixed_point');
      else if (lam < 0.02) regime = T('periodic');
      setReadout({
        r: params.r.toFixed(3),
        lyap: lam.toFixed(3),
        regime
      });
    });
    handle.reset = () => { params.r = 3.62; };
    return handle;
  };

  /* ============================================================
     12. Elo matchmaking
     ============================================================ */
  DEMOS.elo = function (el) {
    const st = makeStage(el);
    const params = { k: 24, gap: 120 };
    let ra = 1500, rb = 1500;
    let histA = [], histB = [];
    let games = 0, winsB = 0;
    let acc = 0;
    const rnd = mulberry32(11);
    const setReadout = readout(st.readout, [['ra', T('player_a')], ['rb', T('player_b')], ['games', T('matches')], ['rate', T('winrate_b')]]);

    function match() {
      const pA = 1 / (1 + Math.pow(10, -params.gap / 400));
      const aWins = rnd() < pA;
      const pAw = 1 / (1 + Math.pow(10, (rb - ra) / 400));
      const sA = aWins ? 1 : 0;
      ra += params.k * (sA - pAw);
      rb += params.k * ((1 - sA) - (1 - pAw));
      games++;
      if (!aWins) winsB++;
      histA.push(ra); histB.push(rb);
      if (histA.length > 260) { histA.shift(); histB.shift(); }
    }

    slider(st.controls, T('k_factor'), 4, 60, params.k, 1, v => v, v => params.k = v);
    slider(st.controls, T('true_diff'), -300, 300, params.gap, 10, v => (v > 0 ? '+' : '') + v, v => params.gap = v);
    button(st.controls, T('reset_short'), () => {
      ra = 1500; rb = 1500; histA = []; histB = []; games = 0; winsB = 0;
    });

    const handle = loop((dt) => {
      acc += dt;
      while (acc > 0.1) { match(); acc -= 0.1; }

      clear(st, '#07080b');
      grid(st, 40);
      const padL = 44, padB = 20, padT = 22;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      const all = histA.concat(histB);
      const minV = Math.min(...all, 1380), maxV = Math.max(...all, 1620);

      st.ctx.strokeStyle = 'rgba(255,255,255,0.14)';
      st.ctx.beginPath();
      st.ctx.moveTo(padL, padT);
      st.ctx.lineTo(padL, st.h - padB);
      st.ctx.lineTo(st.w - 8, st.h - padB);
      st.ctx.stroke();

      [1400, 1500, 1600].forEach(v => {
        if (v < minV || v > maxV) return;
        const y = padT + (1 - (v - minV) / (maxV - minV)) * plotH;
        st.ctx.strokeStyle = 'rgba(255,255,255,0.08)';
        st.ctx.setLineDash([2, 4]);
        st.ctx.beginPath(); st.ctx.moveTo(padL, y); st.ctx.lineTo(st.w - 8, y); st.ctx.stroke();
        st.ctx.setLineDash([]);
        label(st.ctx, String(v), padL - 6, y, C.dim, 8, 'right');
      });

      function drawLine(hist, color) {
        st.ctx.strokeStyle = color;
        st.ctx.lineWidth = 1.7;
        st.ctx.beginPath();
        hist.forEach((v, i) => {
          const x = padL + (i / Math.max(1, hist.length - 1)) * plotW;
          const y = padT + (1 - (v - minV) / (maxV - minV)) * plotH;
          if (i === 0) st.ctx.moveTo(x, y); else st.ctx.lineTo(x, y);
        });
        st.ctx.stroke();
      }
      drawLine(histA, C.sky);
      drawLine(histB, C.rose);

      label(st.ctx, 'A ' + ra.toFixed(0), 10, 10, C.sky, 10);
      label(st.ctx, 'B ' + rb.toFixed(0), st.w - 10, 10, C.rose, 10, 'right');

      setReadout({
        ra: ra.toFixed(0),
        rb: rb.toFixed(0),
        games,
        rate: games ? (winsB / games * 100).toFixed(0) + '%' : '—'
      });
    });
    handle.reset = () => { ra = 1500; rb = 1500; histA = []; histB = []; games = 0; winsB = 0; };
    return handle;
  };

  /* ============================================================
     13. Trend forecast
     ============================================================ */
  DEMOS.trend = function (el) {
    const st = makeStage(el);
    const params = { noise: 1.0, trend: 0.35 };
    const rnd = mulberry32(5);
    let series = [];
    let forecast = [];
    let band = 0;

    const setReadout = readout(st.readout, [['last', T('forecast')], ['mape', 'MAPE'], ['slope', T('trend')]]);
    function build() {
      series = [];
      let v = 1000, e = 0;
      for (let d = 0; d < 96; d++) {
        e = e * 0.7 + (rnd() - 0.5) * 90 * params.noise;
        const weekly = Math.sin(d / 7 * TAU) * 70 + (d % 7 === 5 || d % 7 === 6 ? 90 : 0);
        v += params.trend * 8 + e * 0.25;
        series.push(v + weekly);
      }
      // seasonal naive forecast
      forecast = [];
      const start = series[series.length - 1];
      for (let h = 1; h <= 21; h++) {
        const lastWeek = series[series.length - 7 + (h % 7)];
        forecast.push(lastWeek + params.trend * 8 * h * 0.6);
      }
      // backtest
      let err = 0, n = 0;
      for (let i = 14; i < series.length; i++) {
        const pred = series[i - 7] + params.trend * 8 * 7 * 0.6;
        if (Math.abs(series[i]) > 1) { err += Math.abs(pred - series[i]) / series[i]; n++; }
      }
      band = (err / Math.max(1, n)) * 100;
    }

    slider(st.controls, T('noise'), 0.1, 2.4, params.noise, 0.05, v => v.toFixed(2), v => { params.noise = v; build(); });
    slider(st.controls, T('trend'), -0.6, 1.2, params.trend, 0.02, v => v.toFixed(2), v => { params.trend = v; build(); });
    setTimeout(build, 0);

    const handle = loop(() => {
      if (!series.length) build();
      clear(st, '#07080b');
      grid(st, 40);
      const padL = 40, padB = 22, padT = 20;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      const all = series.concat(forecast);
      const minV = Math.min(...all) * 0.96, maxV = Math.max(...all) * 1.04;
      const total = series.length + forecast.length;

      function px(i) { return padL + (i / (total - 1)) * plotW; }
      function py(v) { return padT + (1 - (v - minV) / (maxV - minV)) * plotH; }

      // forecast band
      st.ctx.fillStyle = 'rgba(200,247,81,0.05)';
      st.ctx.beginPath();
      st.ctx.moveTo(px(series.length - 1), padT);
      st.ctx.lineTo(px(total - 1), padT);
      st.ctx.lineTo(px(total - 1), padT + plotH);
      st.ctx.lineTo(px(series.length - 1), padT + plotH);
      st.ctx.fill();

      // history
      st.ctx.strokeStyle = C.sky;
      st.ctx.lineWidth = 1.6;
      st.ctx.beginPath();
      series.forEach((v, i) => { if (i === 0) st.ctx.moveTo(px(i), py(v)); else st.ctx.lineTo(px(i), py(v)); });
      st.ctx.stroke();

      st.ctx.fillStyle = 'rgba(125,211,252,0.07)';
      st.ctx.lineTo(px(series.length - 1), padT + plotH);
      st.ctx.lineTo(px(0), padT + plotH);
      st.ctx.fill();

      // forecast
      st.ctx.strokeStyle = C.acid;
      st.ctx.setLineDash([4, 4]);
      st.ctx.beginPath();
      st.ctx.moveTo(px(series.length - 1), py(series[series.length - 1]));
      forecast.forEach((v, i) => st.ctx.lineTo(px(series.length + i), py(v)));
      st.ctx.stroke();
      st.ctx.setLineDash([]);

      // today marker
      const tx = px(series.length - 1);
      st.ctx.strokeStyle = 'rgba(255,255,255,0.2)';
      st.ctx.beginPath(); st.ctx.moveTo(tx, padT); st.ctx.lineTo(tx, padT + plotH); st.ctx.stroke();
      label(st.ctx, T('today'), tx + 4, padT + 6, C.dim, 8);

      label(st.ctx, T('plus21'), st.w - 12, padT + 6, C.acid, 9, 'right');
      setReadout({
        last: forecast[forecast.length - 1].toFixed(0),
        mape: band.toFixed(1) + '%',
        slope: (params.trend >= 0 ? '+' : '') + params.trend.toFixed(2)
      });
    });
    handle.reset = () => { params.noise = 1; params.trend = 0.35; build(); };
    return handle;
  };

  /* ============================================================
     14. Loot / pity
     ============================================================ */
  DEMOS.loot = function (el) {
    const st = makeStage(el);
    const params = { pity: 90, trials: 5000 };
    let results = [];
    let stats = { avg: 0, med: 0, p90: 0, rate: 0 };

    const setReadout = readout(st.readout, [['avg', T('mean')], ['med', T('median')], ['p90', 'p90'], ['rate', T('chance')]]);

    function simulate() {
      const rnd = mulberry32(params.pity * 31 + 7);
      results = [];
      const hard = Math.round(params.pity);
      const soft = Math.round(hard * 0.78);
      for (let t = 0; t < params.trials; t++) {
        let pulls = 0;
        while (true) {
          pulls++;
          const p = 0.006 + Math.max(0, pulls - soft) * 0.06;
          if (pulls >= hard || rnd() < Math.min(1, p)) break;
        }
        results.push(pulls);
      }
      results.sort((a, b) => a - b);
      const sum = results.reduce((a, b) => a + b, 0);
      stats = {
        avg: sum / results.length,
        med: results[Math.floor(results.length * 0.5)],
        p90: results[Math.floor(results.length * 0.9)],
        rate: results.length / sum * 100
      };
    }

    slider(st.controls, 'hard pity', 30, 120, params.pity, 1, v => v, v => { params.pity = v; simulate(); });
    button(st.controls, T('resimulate'), simulate);
    setTimeout(simulate, 0);

    const handle = loop(() => {
      clear(st, '#07080b');
      if (!results.length) return;
      grid(st, 40);
      const padL = 38, padB = 24, padT = 20;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      const maxPulls = Math.max(...results);
      const bins = new Array(30).fill(0);
      results.forEach(p => {
        const b = Math.min(29, Math.floor(p / (maxPulls + 1) * 30));
        bins[b]++;
      });
      const maxBin = Math.max(...bins);

      st.ctx.strokeStyle = 'rgba(255,255,255,0.14)';
      st.ctx.beginPath();
      st.ctx.moveTo(padL, padT);
      st.ctx.lineTo(padL, st.h - padB);
      st.ctx.lineTo(st.w - 8, st.h - padB);
      st.ctx.stroke();

      bins.forEach((v, i) => {
        const bw = plotW / bins.length;
        const x = padL + i * bw;
        const bh = (v / maxBin) * plotH;
        const pullsMid = (i + 0.5) / bins.length * maxPulls;
        const grad = st.ctx.createLinearGradient(0, st.h - padB - bh, 0, st.h - padB);
        if (pullsMid >= stats.p90) {
          grad.addColorStop(0, 'rgba(251,191,107,0.9)');
          grad.addColorStop(1, 'rgba(251,191,107,0.25)');
        } else {
          grad.addColorStop(0, 'rgba(200,247,81,0.85)');
          grad.addColorStop(1, 'rgba(200,247,81,0.18)');
        }
        st.ctx.fillStyle = grad;
        st.ctx.fillRect(x + 1, st.h - padB - bh, Math.max(1, bw - 2), bh);
      });

      // mean + p90 markers
      const mx = padL + (stats.avg / maxPulls) * plotW;
      st.ctx.strokeStyle = C.acid;
      st.ctx.beginPath(); st.ctx.moveTo(mx, padT); st.ctx.lineTo(mx, st.h - padB); st.ctx.stroke();
      label(st.ctx, T('mean'), mx + 3, padT + 6, C.acid, 8);

      const px90 = padL + (stats.p90 / maxPulls) * plotW;
      st.ctx.strokeStyle = C.amber;
      st.ctx.setLineDash([3, 3]);
      st.ctx.beginPath(); st.ctx.moveTo(px90, padT); st.ctx.lineTo(px90, st.h - padB); st.ctx.stroke();
      st.ctx.setLineDash([]);
      label(st.ctx, 'p90', px90 + 3, padT + 18, C.amber, 8);

      label(st.ctx, T('attempts'), padL + plotW / 2, st.h - 8, C.dim, 8, 'center');
      label(st.ctx, '0', padL - 6, st.h - padB, C.dim, 8, 'right');
      label(st.ctx, String(maxPulls), st.w - 10, st.h - padB + 10, C.dim, 8, 'right');

      setReadout({
        avg: stats.avg.toFixed(1),
        med: String(stats.med),
        p90: String(stats.p90),
        rate: stats.rate.toFixed(2) + '%'
      });
    });
    handle.reset = () => { params.pity = 90; simulate(); };
    return handle;
  };

  /* ============================================================
     15. Voxel / marching squares
     ============================================================ */
  DEMOS.voxel = function (el) {
    const st = makeStage(el);
    const params = { iso: 1.6, balls: 4, speed: 1 };
    const balls = [];
    const setReadout = readout(st.readout, [['cells', T('cells')], ['segs', T('segments')], ['iso', T('isolevel')]]);
    let t = 0;

    function ensureBalls() {
      const rnd = mulberry32(23);
      while (balls.length < 5) {
        balls.push({
          x: 0.2 + rnd() * 0.6, y: 0.2 + rnd() * 0.6,
          vx: (rnd() - 0.5) * 0.12, vy: (rnd() - 0.5) * 0.12,
          r: 0.12 + rnd() * 0.1
        });
      }
    }
    ensureBalls();

    slider(st.controls, T('isolevel'), 0.5, 3.2, params.iso, 0.05, v => v.toFixed(2), v => params.iso = v);
    slider(st.controls, T('spheres'), 1, 5, params.balls, 1, v => v, v => params.balls = v);

    function field(px, py) {
      let f = 0;
      for (let i = 0; i < params.balls; i++) {
        const b = balls[i];
        const dx = px / st.w - b.x;
        const dy = py / st.h - b.y;
        const r = b.r;
        f += r * r / (dx * dx + dy * dy + 1e-4);
      }
      return f;
    }

    const handle = loop((dt) => {
      t += dt * params.speed;
      for (const b of balls) {
        b.x += b.vx * dt;
        b.y += b.vy * dt;
        if (b.x < 0.15 || b.x > 0.85) b.vx *= -1;
        if (b.y < 0.15 || b.y > 0.85) b.vy *= -1;
        b.x = Math.max(0.12, Math.min(0.88, b.x));
        b.y = Math.max(0.12, Math.min(0.88, b.y));
      }

      clear(st, '#07080b');
      grid(st, 34);

      const step = 7;
      const nx = Math.floor(st.w / step), ny = Math.floor(st.h / step);
      const vals = new Float32Array((nx + 1) * (ny + 1));
      for (let y = 0; y <= ny; y++) {
        for (let x = 0; x <= nx; x++) {
          vals[y * (nx + 1) + x] = field(x * step, y * step);
        }
      }

      // faint field glow
      for (let i = 0; i < params.balls; i++) {
        const b = balls[i];
        const gx = b.x * st.w, gy = b.y * st.h;
        const g = st.ctx.createRadialGradient(gx, gy, 0, gx, gy, b.r * st.w * 1.3);
        g.addColorStop(0, 'rgba(125,211,252,0.16)');
        g.addColorStop(1, 'rgba(125,211,252,0)');
        st.ctx.fillStyle = g;
        st.ctx.beginPath(); st.ctx.arc(gx, gy, b.r * st.w * 1.3, 0, TAU); st.ctx.fill();
      }

      const iso = params.iso;
      const edgePt = (ax, ay, av, bx, by, bv) => {
        const t2 = (iso - av) / (bv - av || 1e-9);
        return [ax + (bx - ax) * t2, ay + (by - ay) * t2];
      };
      const table = {
        1: [[3, 0]], 2: [[0, 1]], 3: [[3, 1]], 4: [[1, 2]],
        5: [[3, 0], [1, 2]], 6: [[0, 2]], 7: [[3, 2]], 8: [[2, 3]],
        9: [[2, 0]], 10: [[0, 1], [2, 3]], 11: [[2, 1]], 12: [[1, 3]],
        13: [[1, 0]], 14: [[0, 3]]
      };
      let segs = 0;
      st.ctx.strokeStyle = 'rgba(200,247,81,0.92)';
      st.ctx.lineWidth = 1.4;
      st.ctx.beginPath();
      for (let y = 0; y < ny; y++) {
        for (let x = 0; x < nx; x++) {
          const x0 = x * step, y0 = y * step;
          const v0 = vals[y * (nx + 1) + x];
          const v1 = vals[y * (nx + 1) + x + 1];
          const v2 = vals[(y + 1) * (nx + 1) + x + 1];
          const v3 = vals[(y + 1) * (nx + 1) + x];
          const idx = (v0 > iso ? 1 : 0) | (v1 > iso ? 2 : 0) | (v2 > iso ? 4 : 0) | (v3 > iso ? 8 : 0);
          const pairs = table[idx];
          if (!pairs) continue;
          const pts = {
            0: () => edgePt(x0, y0, v0, x0 + step, y0, v1),
            1: () => edgePt(x0 + step, y0, v1, x0 + step, y0 + step, v2),
            2: () => edgePt(x0 + step, y0 + step, v2, x0, y0 + step, v3),
            3: () => edgePt(x0, y0 + step, v3, x0, y0, v0)
          };
          for (const [a, b] of pairs) {
            const p1 = pts[a](), p2 = pts[b]();
            st.ctx.moveTo(p1[0], p1[1]);
            st.ctx.lineTo(p2[0], p2[1]);
            segs++;
          }
        }
      }
      st.ctx.stroke();

      label(st.ctx, 'marching squares · iso ' + iso.toFixed(2), 10, 13, C.dim, 9);
      setReadout({ cells: nx * ny, segs, iso: iso.toFixed(2) });
    });
    handle.reset = () => { params.iso = 1.6; params.balls = 4; t = 0; };
    return handle;
  };

  /* ============================================================
     16. Auctions
     ============================================================ */
  DEMOS.auction = function (el) {
    const st = makeStage(el);
    const names = ['A', 'B', 'C', 'D'];
    const values = [42, 68, 81, 56];
    const colors = [C.mint, C.sky, C.acid, C.violet];
    const params = { mode: 'vickrey' };
    const setReadout = readout(st.readout, [['win', T('winner')], ['price', T('price')], ['rev', T('revenue')], ['second', T('second_bid')]]);

    names.forEach((n, i) => {
      slider(st.controls, T('price_pad') + n, 5, 100, values[i], 1, v => v, v => { values[i] = v; });
    });
    select(st.controls, T('format'), [['vickrey', T('vickrey')], ['first', T('first_price')]], v => params.mode = v);

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 40);
      const n = values.length;

      const bids = values.map(v => params.mode === 'first' ? v * (n - 1) / n : v);
      let winner = 0;
      for (let i = 1; i < n; i++) if (bids[i] > bids[winner]) winner = i;
      const sorted = bids.slice().sort((a, b) => b - a);
      const price = params.mode === 'vickrey' ? sorted[1] : sorted[0];

      const padL = 40, padB = 26, padT = 22;
      const plotW = st.w - padL - 20, plotH = st.h - padT - padB;
      const bw = plotW / n;

      st.ctx.strokeStyle = 'rgba(255,255,255,0.16)';
      st.ctx.beginPath();
      st.ctx.moveTo(padL, padT);
      st.ctx.lineTo(padL, st.h - padB);
      st.ctx.lineTo(st.w - 8, st.h - padB);
      st.ctx.stroke();

      bids.forEach((b, i) => {
        const h = (b / 100) * plotH;
        const x = padL + i * bw + bw * 0.18;
        st.ctx.fillStyle = i === winner ? colors[i] : 'rgba(255,255,255,0.12)';
        st.ctx.fillRect(x, st.h - padB - h, bw * 0.64, h);
        label(st.ctx, names[i], x + bw * 0.32, st.h - padB + 10, i === winner ? colors[i] : C.dim, 9, 'center');
        label(st.ctx, b.toFixed(0), x + bw * 0.32, st.h - padB - h - 8, i === winner ? colors[i] : C.dim, 9, 'center');
        if (params.mode === 'first') {
          label(st.ctx, 'v=' + values[i], x + bw * 0.32, st.h - padB + 21, 'rgba(255,255,255,0.25)', 7, 'center');
        }
      });

      const py = st.h - padB - (price / 100) * plotH;
      st.ctx.strokeStyle = C.rose;
      st.ctx.setLineDash([4, 4]);
      st.ctx.beginPath();
      st.ctx.moveTo(padL, py);
      st.ctx.lineTo(st.w - 8, py);
      st.ctx.stroke();
      st.ctx.setLineDash([]);
      label(st.ctx, T('price_pad') + price.toFixed(0), padL + 4, py - 8, C.rose, 9);

      label(st.ctx, params.mode === 'vickrey' ? T('second_price') : T('first_price'), st.w - 10, 12, C.dim, 9, 'right');

      setReadout({
        win: names[winner] + ' (' + values[winner] + ')',
        price: price.toFixed(0),
        rev: price.toFixed(0),
        second: sorted[1].toFixed(0)
      });
    });
    handle.reset = () => { values.splice(0, 4, 42, 68, 81, 56); };
    return handle;
  };
})();
