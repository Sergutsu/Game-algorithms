/* ============================================================
   Interactive demos: Part II — procedural generation, file A
   Noise, sampling, determinism and layout algorithms.
   Plain canvas 2D, no dependencies.
   ============================================================ */
(function () {
  'use strict';

  const DEMOS = (window.GA_DEMOS = window.GA_DEMOS || {});
  const T = (key) => window.GA_T(key);
  const C = {
    acid: '#c8f751', mint: '#6ee7b7', sky: '#7dd3fc', amber: '#fbbf6b',
    rose: '#fda4af', violet: '#c4b5fd', ink: '#e7eddf', dim: '#6b7368',
    line: 'rgba(255,255,255,0.09)', faint: 'rgba(255,255,255,0.04)'
  };
  const TAU = Math.PI * 2;

  /* ---------- shared UI ---------- */
  function makeStage(el, onResize) {
    const body = el.querySelector('.demo-body');
    const stageEl = document.createElement('div');
    stageEl.className = 'demo-stage';
    const canvas = document.createElement('canvas');
    canvas.setAttribute('aria-label', T('viz'));
    stageEl.appendChild(canvas);
    const controls = document.createElement('div');
    controls.className = 'demo-controls';
    const readout = document.createElement('div');
    readout.className = 'demo-readout';
    body.append(stageEl, controls, readout);
    const ctx = canvas.getContext('2d');
    const st = { canvas, ctx, controls, readout, w: 300, h: 260 };

    function fit() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const r = canvas.getBoundingClientRect();
      if (!r.width) return;
      canvas.width = Math.round(r.width * dpr);
      canvas.height = Math.round(r.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      st.w = r.width;
      st.h = r.height;
      if (onResize) onResize(st.w, st.h);
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
    return {
      input,
      get value() { return +input.value; },
      set(v) { input.value = v; out.textContent = fmt(+v); }
    };
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

  function button(parent, label, onclick) {
    const b = document.createElement('button');
    b.className = 'chip';
    b.type = 'button';
    b.textContent = label;
    b.addEventListener('click', onclick);
    parent.appendChild(b);
    return b;
  }

  function segmented(parent, items, active, onpick) {
    const row = document.createElement('div');
    row.className = 'demo-seg';
    const btns = {};
    items.forEach(([id, label]) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'chip' + (id === active ? ' on' : '');
      b.textContent = label;
      b.addEventListener('click', () => {
        Object.keys(btns).forEach((k) => btns[k].classList.toggle('on', k === id));
        onpick(id);
      });
      btns[id] = b;
      row.appendChild(b);
    });
    parent.appendChild(row);
    return btns;
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
    return (obj) => {
      Object.keys(obj).forEach((k) => {
        if (cells[k]) cells[k].textContent = obj[k];
      });
    };
  }

  function loop(draw) {
    let raf = null;
    let last = 0;
    let paused = false;
    function tick(now) {
      const dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016;
      last = now;
      if (!paused) {
        try {
          draw(dt, now / 1000);
        } catch (e) {
          if (!window.__gaDemoWarned) { window.__gaDemoWarned = true; console.warn('[demo]', e); }
        }
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
    if (color) {
      st.ctx.fillStyle = color;
      st.ctx.fillRect(0, 0, st.w, st.h);
    }
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

  function hash2(x, y, seed) {
    let h = Math.imul(x | 0, 374761393) ^ Math.imul(y | 0, 668265263) ^ Math.imul(seed | 0, 1442695041);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
  }

  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, t) => a + (b - a) * t;
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);

  function rgb(hex) {
    const n = parseInt(hex.slice(1), 16);
    return [n >> 16 & 255, n >> 8 & 255, n & 255];
  }
  function mix(a, b, t) {
    return [Math.round(lerp(a[0], b[0], t)), Math.round(lerp(a[1], b[1], t)), Math.round(lerp(a[2], b[2], t))];
  }

  function vnoise(x, y, seed) {
    const xi = Math.floor(x), yi = Math.floor(y);
    const u = fade(x - xi), v = fade(y - yi);
    const a = hash2(xi, yi, seed), b = hash2(xi + 1, yi, seed);
    const c = hash2(xi, yi + 1, seed), d = hash2(xi + 1, yi + 1, seed);
    return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v;
  }

  function perlin(x, y, seed) {
    const xi = Math.floor(x), yi = Math.floor(y);
    const xf = x - xi, yf = y - yi;
    const u = fade(xf), v = fade(yf);
    function g(ix, iy, dx, dy) {
      const a = hash2(ix, iy, seed) * TAU;
      return Math.cos(a) * dx + Math.sin(a) * dy;
    }
    const n00 = g(xi, yi, xf, yf);
    const n10 = g(xi + 1, yi, xf - 1, yf);
    const n01 = g(xi, yi + 1, xf, yf - 1);
    const n11 = g(xi + 1, yi + 1, xf - 1, yf - 1);
    return (lerp(lerp(n00, n10, u), lerp(n01, n11, u), v) + 0.7) / 1.4;
  }

  function fbmField(x, y, oct, seed, gain) {
    let sum = 0, norm = 0, amp = 1, f = 1;
    gain = gain === undefined ? 0.5 : gain;
    for (let i = 0; i < oct; i++) {
      sum += amp * perlin(x * f, y * f, seed + i * 131);
      norm += amp; amp *= gain; f *= 2;
    }
    return sum / norm;
  }

  /* ============================================================
     1. Gradient noise
     ============================================================ */
  DEMOS.noise = function (el) {
    const st = makeStage(el);
    const p = { mode: 'perlin', scale: 4.5, octaves: 5, warp: 0.4, speed: 0.35, ridged: false };
    let phase = 0, bmp = null, bw = 0, bh = 0, builtW = 0, seed = 1337, acc = 0;
    const setReadout = readout(st.readout, [
      ['mode', T('mode')], ['oct', T('octaves')], ['val', T('value_range')]
    ]);
    const pal = [rgb('#0a1a24'), rgb('#11485a'), rgb('#2f8f7a'), rgb('#a8d96a'), rgb('#f2f0d8')];

    function colorFor(v) {
      v = clamp(v, 0, 1);
      const t = v * (pal.length - 1);
      const i = Math.min(pal.length - 2, Math.floor(t));
      return mix(pal[i], pal[i + 1], t - i);
    }

    function field(x, y) {
      let v;
      if (p.mode === 'value') {
        v = fbmValue(x, y);
      } else {
        v = fbmField(x, y, p.octaves, seed, 0.5);
        if (p.warp > 0) {
          const wx = fbmField(x + 4.7, y + 1.3, 2, seed + 77, 0.5) - 0.5;
          const wy = fbmField(x - 2.1, y + 8.2, 2, seed + 91, 0.5) - 0.5;
          v = fbmField(x + wx * p.warp * 3, y + wy * p.warp * 3, p.octaves, seed, 0.5);
        }
      }
      if (p.ridged) v = 1 - Math.abs(v * 2 - 1);
      return v;
    }
    function fbmValue(x, y) {
      let sum = 0, norm = 0, amp = 1, f = 1;
      for (let i = 0; i < p.octaves; i++) {
        sum += amp * vnoise(x * f, y * f, seed + i * 131);
        norm += amp; amp *= 0.5; f *= 2;
      }
      return sum / norm;
    }

    function build() {
      bw = clamp(Math.round(st.w / 3), 96, 220);
      bh = clamp(Math.round(st.h / 3), 72, 160);
      bmp = document.createElement('canvas');
      bmp.width = bw; bmp.height = bh;
      const bctx = bmp.getContext('2d');
      const img = bctx.createImageData(bw, bh);
      const s = p.scale / bw * 3;
      for (let y = 0; y < bh; y++) {
        for (let x = 0; x < bw; x++) {
          const v = field(x * s + phase, y * s * 0.9 + phase * 0.6);
          const c = colorFor(v);
          const i = (y * bw + x) * 4;
          img.data[i] = c[0]; img.data[i + 1] = c[1]; img.data[i + 2] = c[2]; img.data[i + 3] = 255;
        }
      }
      bctx.putImageData(img, 0, 0);
      builtW = st.w;
      setReadout({
        mode: p.mode === 'value' ? T('value_noise') : 'Perlin',
        oct: String(p.mode === 'value' ? p.octaves : p.octaves),
        val: (p.ridged ? 'ridged' : 'fBm')
      });
    }

    segmented(st.controls, [
      ['value', T('value_noise')], ['perlin', 'Perlin'], ['fbm', 'fBm']
    ], 'perlin', (id) => {
      p.mode = id === 'value' ? 'value' : 'perlin';
      p.octaves = id === 'value' ? p.octaves : (id === 'fbm' ? 6 : 3);
      build();
    });
    slider(st.controls, T('scale'), 1, 12, p.scale, 0.5, v => v.toFixed(1), v => { p.scale = v; build(); });
    slider(st.controls, T('octaves'), 1, 8, p.octaves, 1, v => String(v), v => { p.octaves = v; build(); });
    slider(st.controls, T('warp'), 0, 1, p.warp, 0.05, v => v.toFixed(2), v => { p.warp = v; build(); });
    toggle(st.controls, T('ridged'), false, v => { p.ridged = v; build(); });
    toggle(st.controls, T('animate'), true, v => { p.speed = v ? 0.35 : 0; });

    setTimeout(build, 0);
    const handle = loop((dt) => {
      if (p.speed) {
        acc += dt;
        if (acc > 0.06) { phase += acc * p.speed; acc = 0; build(); }
      }
      clear(st, '#07080b');
      if (!bmp) return;
      if (Math.abs(st.w - builtW) > 24) build();
      st.ctx.drawImage(bmp, 0, 0, st.w, st.h);
      const g = st.ctx.createLinearGradient(0, st.h - 46, 0, st.h);
      g.addColorStop(0, 'rgba(7,8,11,0)');
      g.addColorStop(1, 'rgba(7,8,11,0.85)');
      st.ctx.fillStyle = g;
      st.ctx.fillRect(0, st.h - 46, st.w, 46);
      label(st.ctx, 'fBm · ' + p.octaves + T('octaves_unit') + ' · ' + T('gain') + ' 0.5', 10, st.h - 14,
        'rgba(255,255,255,0.55)', 9);
    });
    handle.reset = () => { phase = 0; seed = 1337; build(); };
    return handle;
  };

  /* ============================================================
     2. Worley / cellular noise
     ============================================================ */
  DEMOS.worley = function (el) {
    const st = makeStage(el);
    const p = { mode: 'f1', freq: 7, jitter: 0.85, points: false, seed: 42 };
    let bmp = null, bw = 0, bh = 0, builtW = 0;
    const setReadout = readout(st.readout, [
      ['mode', T('mode')], ['cells', T('cells')], ['edges', T('borders')]
    ]);
    const cellColors = ['#1f5f52', '#2d8b6f', '#5fbf8d', '#95d9a5', '#c8f751', '#7dd3fc', '#fbbf6b'];

    function feat(cx, cy) {
      const j = p.jitter;
      return [
        cx + 0.5 + (hash2(cx, cy, p.seed) - 0.5) * j,
        cy + 0.5 + (hash2(cx, cy, p.seed + 977) - 0.5) * j
      ];
    }

    function sample(x, y) {
      const cx = Math.floor(x), cy = Math.floor(y);
      let f1 = 1e9, f2 = 1e9, id = 0, fx = 0, fy = 0;
      for (let oy = -1; oy <= 1; oy++) {
        for (let ox = -1; ox <= 1; ox++) {
          const gx = cx + ox, gy = cy + oy;
          const f = feat(gx, gy);
          const d = Math.hypot(f[0] - x, f[1] - y);
          if (d < f1) {
            f2 = f1; f1 = d;
            id = ((gx * 73856093) ^ (gy * 19349663)) >>> 0;
            fx = f[0]; fy = f[1];
          } else if (d < f2) f2 = d;
        }
      }
      return { f1: f1, f2: f2, id: id, fx: fx, fy: fy };
    }

    function build() {
      bw = clamp(Math.round(st.w / 2), 120, 300);
      bh = clamp(Math.round(st.h / 2), 90, 210);
      bmp = document.createElement('canvas');
      bmp.width = bw; bmp.height = bh;
      const bctx = bmp.getContext('2d');
      const img = bctx.createImageData(bw, bh);
      const s = p.freq / bw * 2.4;
      for (let y = 0; y < bh; y++) {
        for (let x = 0; x < bw; x++) {
          const q = sample(x * s, y * s);
          let c;
          if (p.mode === 'f1') {
            c = colorFor(q.f1);
          } else if (p.mode === 'border') {
            const b = 1 - clamp((q.f2 - q.f1) / 0.09, 0, 1);
            c = mix(rgb('#0b1512'), rgb('#c8f751'), b);
          } else {
            const base = rgb(cellColors[q.id % cellColors.length]);
            const shade = 0.55 + 0.45 * (1 - clamp(q.f1 / 0.9, 0, 1));
            c = [Math.round(base[0] * shade), Math.round(base[1] * shade), Math.round(base[2] * shade)];
          }
          const i = (y * bw + x) * 4;
          img.data[i] = c[0]; img.data[i + 1] = c[1]; img.data[i + 2] = c[2]; img.data[i + 3] = 255;
        }
      }
      bctx.putImageData(img, 0, 0);
      builtW = st.w;
      setReadout({
        mode: p.mode === 'f1' ? 'F1' : (p.mode === 'border' ? 'F2 − F1' : T('cells_lbl')),
        cells: String(Math.round(p.freq * p.freq)),
        edges: p.mode === 'border' ? 'sharp' : 'F2 − F1'
      });
    }
    function colorFor(v) {
      const t = clamp(v / 0.8, 0, 1);
      return mix(rgb('#0b1a1c'), rgb('#e8f7c8'), Math.pow(1 - t, 1.4));
    }

    segmented(st.controls, [
      ['f1', 'F1'], ['border', 'F2−F1'], ['cells', T('cells_lbl')]
    ], 'f1', (id) => { p.mode = id; build(); });
    slider(st.controls, T('cells'), 3, 18, p.freq, 1, v => String(v), v => { p.freq = v; build(); });
    slider(st.controls, T('jitter'), 0, 1, p.jitter, 0.05, v => v.toFixed(2), v => { p.jitter = v; build(); });
    toggle(st.controls, T('points'), false, v => { p.points = v; });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); build(); });

    setTimeout(build, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!bmp) return;
      if (Math.abs(st.w - builtW) > 24) build();
      st.ctx.drawImage(bmp, 0, 0, st.w, st.h);
      if (p.points) {
        const s = p.freq / bw * 2.4;
        const cols = Math.ceil(st.w / (st.w / p.freq));
        st.ctx.fillStyle = 'rgba(255,255,255,0.85)';
        for (let gy = 0; gy < p.freq + 1; gy++) {
          for (let gx = 0; gx < p.freq + 1; gx++) {
            const f = feat(gx, gy);
            const px = f[0] / s;
            const py = f[1] / s;
            if (px > st.w || py > st.h) continue;
            st.ctx.beginPath();
            st.ctx.arc(px, py, 1.6, 0, TAU);
            st.ctx.fill();
          }
        }
      }
      label(st.ctx, 'F1 / F2 − F1 · ' + T('jitter') + ' ' + p.jitter.toFixed(2), 10, 13, 'rgba(255,255,255,0.55)', 9);
    });
    handle.reset = () => { p.seed = 42; p.freq = 7; build(); };
    return handle;
  };

  /* ============================================================
     3. Poisson disk sampling (Bridson)
     ============================================================ */
  DEMOS.poisson = function (el) {
    const st = makeStage(el);
    const p = { radius: 22, white: false, speed: 1 };
    let state = null;
    const setReadout = readout(st.readout, [
      ['points', T('points_lbl')], ['density', T('density')], ['mode', T('mode')]
    ]);

    function reset() {
      const r = p.radius;
      const cell = r / Math.SQRT2;
      const gw = Math.ceil(st.w / cell) + 2;
      const gh = Math.ceil(st.h / cell) + 2;
      state = {
        r: r, cell: cell, gw: gw, gh: gh,
        grid: new Array(gw * gh).fill(null),
        pts: [], active: [], candidates: [], white: p.white
      };
      if (p.white) {
        const n = Math.round(st.w * st.h / (Math.PI * r * r) * 0.7);
        for (let i = 0; i < n; i++) {
          state.pts.push([Math.random() * st.w, Math.random() * st.h]);
        }
        state.active = [];
      } else {
        add(st.w / 2, st.h / 2);
      }
    }
    function add(x, y) {
      const gx = Math.floor(x / state.cell), gy = Math.floor(y / state.cell);
      state.grid[gy * state.gw + gx] = [x, y];
      state.pts.push([x, y]);
      state.active.push(state.pts.length - 1);
    }
    function step() {
      if (p.white) return;
      if (!state.active.length) {
        state.candidates = [];
        return;
      }
      const idx = Math.floor(Math.random() * state.active.length);
      const [x, y] = state.pts[state.active[idx]];
      const r = state.r;
      let placed = false;
      const cands = [];
      for (let k = 0; k < 30; k++) {
        const a = Math.random() * TAU;
        const d = r * (1 + Math.random());
        const nx = x + Math.cos(a) * d, ny = y + Math.sin(a) * d;
        if (nx < 0 || ny < 0 || nx >= st.w || ny >= st.h) continue;
        const gx = Math.floor(nx / state.cell), gy = Math.floor(ny / state.cell);
        let ok = true;
        for (let oy = -2; oy <= 2 && ok; oy++) {
          for (let ox = -2; ox <= 2; ox++) {
            const q = state.grid[(gy + oy) * state.gw + gx + ox];
            if (q && (q[0] - nx) * (q[0] - nx) + (q[1] - ny) * (q[1] - ny) < r * r) { ok = false; break; }
          }
        }
        if (!ok && cands.length < 40) cands.push([nx, ny, false]);
        if (ok) {
          add(nx, ny);
          cands.push([nx, ny, true]);
          placed = true;
          break;
        }
      }
      state.candidates = cands;
      if (!placed) state.active.splice(idx, 1);
    }

    function draw() {
      clear(st, '#07080b');
      if (!state) reset();
      st.ctx.fillStyle = p.white ? 'rgba(253,164,175,0.85)' : 'rgba(110,231,183,0.9)';
      state.pts.forEach(([x, y]) => {
        st.ctx.beginPath();
        st.ctx.arc(x, y, p.white ? 1.6 : 2.2, 0, TAU);
        st.ctx.fill();
      });
      if (state.candidates) {
        state.candidates.forEach(([x, y, ok]) => {
          st.ctx.strokeStyle = ok ? 'rgba(200,247,81,0.9)' : 'rgba(255,255,255,0.16)';
          st.ctx.lineWidth = 1;
          st.ctx.beginPath();
          st.ctx.moveTo(x - 2.5, y); st.ctx.lineTo(x + 2.5, y);
          st.ctx.moveTo(x, y - 2.5); st.ctx.lineTo(x, y + 2.5);
          st.ctx.stroke();
        });
      }
      // radius ruler
      st.ctx.strokeStyle = 'rgba(255,255,255,0.25)';
      st.ctx.beginPath();
      st.ctx.moveTo(14, st.h - 16); st.ctx.lineTo(14 + p.radius, st.h - 16);
      st.ctx.stroke();
      label(st.ctx, 'r = ' + p.radius + ' px', 14, st.h - 27, 'rgba(255,255,255,0.5)', 9);
      const density = p.white
        ? (state.pts.length / (st.w * st.h) * 1e4).toFixed(1)
        : (state.pts.length / (st.w * st.h) * 1e4).toFixed(1);
      label(st.ctx, p.white ? T('white_noise') : 'Bridson · blue noise', st.w - 12, 14,
        p.white ? C.rose : C.mint, 9, 'right');
      setReadout({
        points: String(state.pts.length),
        density: density + ' / 10k px²',
        mode: p.white ? T('white_noise') : T('blue_noise')
      });
    }

    slider(st.controls, T('radius'), 10, 46, p.radius, 1, v => String(v), v => {
      p.radius = v; reset();
    });
    segmented(st.controls, [
      ['blue', T('blue_noise')], ['white', T('white_noise')]
    ], 'blue', (id) => { p.white = id === 'white'; reset(); });
    slider(st.controls, T('speed'), 1, 12, 4, 1, v => String(v), v => { p.speed = v; });
    button(st.controls, T('reset_btn'), reset);

    setTimeout(reset, 0);
    const handle = loop(() => {
      if (!state || Math.abs(state.r - p.radius) > 0.5) return;
      for (let i = 0; i < p.speed; i++) step();
      draw();
    });
    handle.reset = () => { p.white = false; reset(); };
    return handle;
  };

  /* ============================================================
     4. Seeded hash / reproducibility
     ============================================================ */
  DEMOS.pcg = function (el) {
    const st = makeStage(el);
    const p = { seed: 1337 };
    const setReadout = readout(st.readout, [
      ['seed', T('seed')], ['same', T('same_cells')], ['bits', T('bits_flip')]
    ]);
    const cols = 16, rows = 9;
    function colorOf(s, x, y) {
      const h = hash2(x + s * 0.0001, y, s);
      const hue = h;
      const a = [110, 231, 183], b = [125, 211, 252], c = [200, 247, 81];
      const t = hue;
      const base = t < 0.5 ? mix(a, b, t * 2) : mix(b, c, (t - 0.5) * 2);
      const k = 0.45 + 0.55 * hash2(x + 99, y + s, s >> 3);
      return [Math.round(base[0] * k), Math.round(base[1] * k), Math.round(base[2] * k)];
    }
    function drawGrid(ox, oy, w, h, s, title) {
      const cw = w / cols, ch = h / rows;
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const c = colorOf(s, x, y);
          st.ctx.fillStyle = 'rgb(' + c.join(',') + ')';
          st.ctx.fillRect(ox + x * cw + 1, oy + y * ch + 1, cw - 2, ch - 2);
        }
      }
      label(st.ctx, title, ox, oy - 8, 'rgba(255,255,255,0.6)', 9);
    }
    function draw() {
      clear(st, '#07080b');
      const w = (st.w - 36) / 2;
      const h = st.h - 78;
      const oy = 40;
      drawGrid(14, oy, w, h, p.seed, T('seed') + ' = ' + p.seed);
      drawGrid(22 + w, oy, w, h, p.seed + 1, T('seed') + ' = ' + (p.seed + 1));
      // bit avalanche strip
      const by = st.h - 28;
      const bits = 24;
      label(st.ctx, 'splitmix64 · ' + T('avalanche'), 14, by - 13, 'rgba(255,255,255,0.45)', 9);
      let diff = 0;
      for (let i = 0; i < bits; i++) {
        const a = (hash2(i, 7, p.seed) * 2 ** 24) | 0;
        const b = (hash2(i, 7, p.seed + 1) * 2 ** 24) | 0;
        const same = (a & (1 << (i % 24))) === (b & (1 << (i % 24)));
        if (!same) diff++;
        st.ctx.fillStyle = same ? 'rgba(255,255,255,0.18)' : C.acid;
        st.ctx.fillRect(14 + i * (st.w - 28) / bits, by, (st.w - 28) / bits - 2, 9);
      }
      let same = 0;
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const a = colorOf(p.seed, x, y).join();
          const b = colorOf(p.seed + 1, x, y).join();
          if (a === b) same++;
        }
      }
      setReadout({
        seed: String(p.seed),
        same: (100 * same / (cols * rows)).toFixed(0) + '%',
        bits: String(diff) + ' / ' + bits
      });
      label(st.ctx, T('reproducible'), st.w - 14, st.h - 13, C.mint, 9, 'right');
    }
    slider(st.controls, T('seed'), 0, 9999, p.seed, 1, v => String(v), v => { p.seed = v; });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); });
    draw();
    const handle = loop(draw);
    handle.reset = () => { p.seed = 1337; };
    return handle;
  };

  /* ============================================================
     5. Procedural materials
     ============================================================ */
  DEMOS.materials = function (el) {
    const st = makeStage(el);
    const p = { kind: 'brick', scale: 8, seed: 9 };
    let bmp = null, bw = 0, bh = 0, builtW = 0, builtH = 0;
    const setReadout = readout(st.readout, [
      ['kind', T('material')], ['px', T('scale')], ['seed', T('seed')]
    ]);

    function brick(x, y, s) {
      const row = Math.floor(y / (s * 0.6));
      const off = (row % 2) * s * 0.5;
      const bx = ((x + off) % s) / s;
      const by = (y % (s * 0.6)) / (s * 0.6);
      const mortar = (bx < 0.06 || by < 0.1) ? 0.22 : 1;
      const v = 0.62 + 0.25 * hash2(Math.floor((x + off) / s), row, p.seed);
      const n = vnoise(x * 0.35, y * 0.35, p.seed + 3) * 0.18;
      const k = clamp((v + n) * mortar, 0, 1);
      const base = mix(rgb('#7a3b2e'), rgb('#c4765c'), k);
      return mortar < 1 ? mix(rgb('#2a2622'), base, k) : base;
    }
    function wood(x, y, s) {
      const r = Math.hypot(x - bw / 2, y - bh / 2);
      const grain = Math.sin(r * 0.22 + vnoise(x * 0.05, y * 0.4, p.seed) * 7) * 0.5 + 0.5;
      const n = vnoise(x * 0.5, y * 0.6, p.seed + 4);
      const k = clamp(grain * 0.6 + n * 0.4, 0, 1);
      return mix(rgb('#4a2a17'), rgb('#a86b3f'), k);
    }
    function marble(x, y, s) {
      const t = vnoise(x * 0.04, y * 0.04, p.seed) * 5;
      const v = Math.sin((x * 0.05 + y * 0.03 + t) * 2.2) * 0.5 + 0.5;
      const n = vnoise(x * 0.3, y * 0.3, p.seed + 2) * 0.2;
      const k = clamp(v * 0.85 + n, 0, 1);
      return mix(rgb('#2b2f33'), rgb('#e6e2d6'), Math.pow(k, 1.5));
    }
    function stone(x, y, s) {
      const n1 = vnoise(x * 0.12, y * 0.12, p.seed);
      const n2 = vnoise(x * 0.5, y * 0.5, p.seed + 5);
      const k = clamp(n1 * 0.7 + n2 * 0.3, 0, 1);
      return mix(rgb('#2a2b28'), rgb('#9a9c92'), k);
    }
    function build() {
      bw = clamp(Math.round(st.w / 2), 140, 320);
      bh = clamp(Math.round(st.h / 2), 90, 210);
      bmp = document.createElement('canvas');
      bmp.width = bw; bmp.height = bh;
      const bctx = bmp.getContext('2d');
      const img = bctx.createImageData(bw, bh);
      const s = Math.max(4, p.scale * 3);
      const fn = p.kind === 'brick' ? brick : p.kind === 'wood' ? wood : p.kind === 'marble' ? marble : stone;
      for (let y = 0; y < bh; y++) {
        for (let x = 0; x < bw; x++) {
          const c = fn(x, y, s);
          const i = (y * bw + x) * 4;
          img.data[i] = c[0]; img.data[i + 1] = c[1]; img.data[i + 2] = c[2]; img.data[i + 3] = 255;
        }
      }
      bctx.putImageData(img, 0, 0);
      builtW = st.w; builtH = st.h;
      setReadout({ kind: T(p.kind), px: String(bw) + '×' + String(bh), seed: String(p.seed) });
    }
    segmented(st.controls, [
      ['brick', T('brick')], ['wood', T('wood')], ['marble', T('marble')], ['stone', T('stone')]
    ], 'brick', (id) => { p.kind = id; build(); });
    slider(st.controls, T('scale'), 2, 20, p.scale, 1, v => String(v), v => { p.scale = v; build(); });
    slider(st.controls, T('seed'), 0, 99, p.seed, 1, v => String(v), v => { p.seed = v; build(); });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 99); build(); });

    setTimeout(build, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!bmp) return;
      if (Math.abs(st.w - builtW) > 24 || Math.abs(st.h - builtH) > 24) build();
      st.ctx.drawImage(bmp, 0, 0, st.w, st.h);
      // tiling seam hint
      st.ctx.strokeStyle = 'rgba(255,255,255,0.10)';
      st.ctx.strokeRect(0.5, 0.5, st.w - 1, st.h - 1);
      label(st.ctx, T(p.kind) + ' · ' + T('procedural') + ' · seed ' + p.seed, 10, st.h - 14,
        'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.seed = 9; p.scale = 8; build(); };
    return handle;
  };

  /* ============================================================
     6. Diamond-square
     ============================================================ */
  DEMOS.diamondsquare = function (el) {
    const st = makeStage(el);
    const p = { roughness: 0.58, seed: 7 };
    let bmp = null, bw = 0, bh = 0, builtW = 0, level = 0, timer = 0, heights = null;
    const setReadout = readout(st.readout, [
      ['peak', T('peak')], ['level', T('level')], ['rough', T('roughness')]
    ]);

    function generate(n) {
      const rng = mulberry32(p.seed * 7919 + 13);
      const h = [];
      for (let y = 0; y < n; y++) h.push(new Float32Array(n));
      h[0][0] = h[0][n - 1] = h[n - 1][0] = h[n - 1][n - 1] = 0.5;
      let step = n - 1, amp = 0.55;
      while (step > 1) {
        const half = step >> 1;
        for (let y = 0; y < n - 1; y += step) {
          for (let x = 0; x < n - 1; x += step) {
            const avg = (h[y][x] + h[y][x + step] + h[y + step][x] + h[y + step][x + step]) / 4;
            h[y + half][x + half] = avg + (rng() * 2 - 1) * amp;
          }
        }
        for (let y = 0; y < n; y += half) {
          for (let x = (y + half) % step; x < n; x += step) {
            let s = 0, c = 0;
            [[half, 0], [-half, 0], [0, half], [0, -half]].forEach(([dx, dy]) => {
              const xx = x + dx, yy = y + dy;
              if (xx >= 0 && xx < n && yy >= 0 && yy < n) { s += h[yy][xx]; c++; }
            });
            h[y][x] = s / c + (rng() * 2 - 1) * amp;
          }
        }
        step = half;
        amp *= p.roughness;
        level++;
      }
      heights = h;
      return h;
    }

    function build() {
      const n = 65;
      const h = generate(n);
      let lo = 1e9, hi = -1e9;
      for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
        lo = Math.min(lo, h[y][x]); hi = Math.max(hi, h[y][x]);
      }
      bw = clamp(Math.round(st.w / 1.1), 200, 420);
      bh = clamp(Math.round(st.h / 1.1), 140, 260);
      bmp = document.createElement('canvas');
      bmp.width = bw; bmp.height = bh;
      const bctx = bmp.getContext('2d');
      const img = bctx.createImageData(bw, bh);
      const sea = 0.47;
      let peak = 0;
      for (let y = 0; y < bh; y++) {
        for (let x = 0; x < bw; x++) {
          const gx = Math.floor(x / bw * (n - 1));
          const gy = Math.floor(y / bh * (n - 1));
          const v = (h[gy][gx] - lo) / (hi - lo);
          peak = Math.max(peak, v);
          const i = (y * bw + x) * 4;
          let c;
          if (v < sea) {
            c = mix(rgb('#0a2233'), rgb('#2a6f8a'), v / sea);
          } else {
            const t = (v - sea) / (1 - sea);
            c = t < 0.55 ? mix(rgb('#c9c09a'), rgb('#5d8a56'), t / 0.55)
              : mix(rgb('#5d8a56'), rgb('#dfe7e4'), (t - 0.55) / 0.45);
          }
          // contour lines, every 5 height units
          const band = Math.abs(((v * 18) % 1) - 0.5);
          if (band < 0.035) c = mix(c, rgb('#10161a'), 0.35);
          img.data[i] = c[0]; img.data[i + 1] = c[1]; img.data[i + 2] = c[2]; img.data[i + 3] = 255;
        }
      }
      bctx.putImageData(img, 0, 0);
      builtW = st.w;
      setReadout({
        peak: peak.toFixed(2),
        level: String(level),
        rough: p.roughness.toFixed(2)
      });
      level = 0;
    }

    slider(st.controls, T('roughness'), 0.3, 0.75, p.roughness, 0.01, v => v.toFixed(2), v => {
      p.roughness = v; timer = 0;
    });
    button(st.controls, T('new_seed'), () => {
      p.seed = Math.floor(Math.random() * 9999); timer = 0;
    });
    setTimeout(build, 0);
    const handle = loop((dt) => {
      clear(st, '#07080b');
      if (!bmp) return;
      timer += dt;
      if (timer > 0.35) { timer = 0; build(); }
      if (Math.abs(st.w - builtW) > 24) build();
      st.ctx.drawImage(bmp, 0, 0, st.w, st.h);
      label(st.ctx, 'diamond-square · 65×65 · ' + T('roughness') + ' ' + p.roughness.toFixed(2),
        10, st.h - 13, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.roughness = 0.58; p.seed = 7; timer = 0; };
    return handle;
  };

  /* ============================================================
     7. Cellular automata caves
     ============================================================ */
  DEMOS.caves = function (el) {
    const st = makeStage(el);
    const p = { fill: 0.45, steps: 5, seed: 3, speed: 1 };
    let g = null, step = 0, cols = 0, rows = 0, timer = 0, components = 0;
    const setReadout = readout(st.readout, [
      ['step', T('step')], ['floor', T('floor_pct')], ['comp', T('components')]
    ]);

    function metric() {
      const W = cols, H = rows;
      const seen = new Uint8Array(W * H);
      let comps = 0, best = 0, floor = 0;
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          if (!g[y][x]) floor++;
          if (g[y][x] || seen[y * W + x]) continue;
          comps++;
          let n = 0;
          const stack = [[x, y]];
          seen[y * W + x] = 1;
          while (stack.length) {
            const [cx, cy] = stack.pop();
            n++;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(([dx, dy]) => {
              const nx = cx + dx, ny = cy + dy;
              if (nx >= 0 && nx < W && ny >= 0 && ny < H && !g[ny][nx] && !seen[ny * W + nx]) {
                seen[ny * W + nx] = 1;
                stack.push([nx, ny]);
              }
            });
          }
          best = Math.max(best, n);
        }
      }
      components = comps;
      return { comps, best, floor: floor / (W * H) };
    }

    function reset() {
      cols = Math.max(20, Math.floor(st.w / 7));
      rows = Math.max(14, Math.floor(st.h / 7));
      const rng = mulberry32(p.seed * 131 + 7);
      g = [];
      for (let y = 0; y < rows; y++) {
        const row = new Uint8Array(cols);
        for (let x = 0; x < cols; x++) {
          row[x] = (x === 0 || y === 0 || x === cols - 1 || y === rows - 1 || rng() < p.fill) ? 1 : 0;
        }
        g.push(row);
      }
      step = 0;
      timer = 0;
    }
    function advance() {
      if (step >= p.steps) return;
      const next = g.map(r => Uint8Array.from(r));
      for (let y = 1; y < rows - 1; y++) {
        for (let x = 1; x < cols - 1; x++) {
          let n = 0;
          for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
            if (dx || dy) n += g[y + dy][x + dx];
          }
          next[y][x] = (n >= 5 || (n === 4 && g[y][x])) ? 1 : 0;
        }
      }
      g = next;
      step++;
    }

    slider(st.controls, T('fill'), 0.35, 0.6, p.fill, 0.01, v => v.toFixed(2), v => {
      p.fill = v; reset();
    });
    slider(st.controls, T('iterations'), 1, 10, p.steps, 1, v => String(v), v => {
      p.steps = v; reset();
    });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); reset(); });
    slider(st.controls, T('speed'), 1, 6, 1, 1, v => String(v), v => { p.speed = v; });

    setTimeout(reset, 0);
    const handle = loop((dt) => {
      if (!g) return;
      timer += dt;
      if (timer > 0.5 / p.speed && step < p.steps) { timer = 0; advance(); }
      clear(st, '#07080b');
      const cw = st.w / cols, ch = st.h / rows;
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          if (g[y][x]) {
            st.ctx.fillStyle = '#161c1b';
          } else {
            const shade = 0.55 + 0.45 * hash2(x, y, 11);
            st.ctx.fillStyle = 'rgba(' + Math.round(60 * shade) + ',' +
              Math.round(120 * shade) + ',' + Math.round(96 * shade) + ',1)';
          }
          st.ctx.fillRect(x * cw, y * ch, cw + 0.5, ch + 0.5);
        }
      }
      const m = metric();
      setReadout({
        step: step + ' / ' + p.steps,
        floor: (m.floor * 100).toFixed(0) + '%',
        comp: String(m.comps)
      });
      label(st.ctx, '4-5 rule · ' + step + T('iterations_unit'), 10, 13, 'rgba(255,255,255,0.55)', 9);
    });
    handle.reset = () => { p.fill = 0.45; p.steps = 5; p.seed = 3; reset(); };
    return handle;
  };

  /* ============================================================
     8. BSP dungeon
     ============================================================ */
  DEMOS.bsp = function (el) {
    const st = makeStage(el);
    const p = { depth: 5, minRoom: 4, braid: true, seed: 11 };
    let tree = null, splits = [], rooms = [], corridors = [], built = false;
    const setReadout = readout(st.readout, [
      ['rooms', T('rooms')], ['depth', T('depth')], ['edges', T('edges')]
    ]);

    function makeNode(x, y, w, h) {
      return { x, y, w, h, left: null, right: null, room: null, level: 0 };
    }
    function split(node, depth, rng, level) {
      node.level = level;
      if (depth <= 0 || (node.w < p.minRoom * 2 + 1 && node.h < p.minRoom * 2 + 1)) return;
      const horiz = node.w < node.h ? true : node.h < node.w ? false : rng() < 0.5;
      if (horiz) {
        if (node.h < p.minRoom * 2 + 2) return;
        const cut = p.minRoom + 1 + Math.floor(rng() * (node.h - 2 * p.minRoom - 2));
        node.left = makeNode(node.x, node.y, node.w, cut);
        node.right = makeNode(node.x, node.y + cut, node.w, node.h - cut);
        splits.push({ x1: node.x, y1: node.y + cut, x2: node.x + node.w, y2: node.y + cut, level });
      } else {
        if (node.w < p.minRoom * 2 + 2) return;
        const cut = p.minRoom + 1 + Math.floor(rng() * (node.w - 2 * p.minRoom - 2));
        node.left = makeNode(node.x, node.y, cut, node.h);
        node.right = makeNode(node.x + cut, node.y, node.w - cut, node.h);
        splits.push({ x1: node.x + cut, y1: node.y, x2: node.x + cut, y2: node.y + node.h, level });
      }
      split(node.left, depth - 1, rng, level + 1);
      split(node.right, depth - 1, rng, level + 1);
    }
    function carve(node, rng) {
      if (node.left || node.right) {
        if (node.left) carve(node.left, rng);
        if (node.right) carve(node.right, rng);
        if (node.left && node.right) {
          const a = center(node.left), b = center(node.right);
          corridors.push([a, b]);
        }
        return;
      }
      const rw = Math.max(3, Math.min(node.w - 2, p.minRoom + Math.floor(rng() * Math.max(1, node.w - p.minRoom - 1))));
      const rh = Math.max(3, Math.min(node.h - 2, p.minRoom + Math.floor(rng() * Math.max(1, node.h - p.minRoom - 1))));
      const rx = node.x + 1 + Math.floor(rng() * Math.max(1, node.w - rw - 1));
      const ry = node.y + 1 + Math.floor(rng() * Math.max(1, node.h - rh - 1));
      node.room = { x: rx, y: ry, w: rw, h: rh };
      rooms.push(node.room);
    }
    function center(node) {
      if (node.room) return [node.room.x + node.room.w / 2, node.room.y + node.room.h / 2];
      return [node.x + node.w / 2, node.y + node.h / 2];
    }
    function generate() {
      const rng = mulberry32(p.seed * 977 + 31);
      const W = 56, H = 34;
      tree = makeNode(1, 1, W - 2, H - 2);
      splits = []; rooms = []; corridors = [];
      split(tree, p.depth, rng, 0);
      carve(tree, rng);
      if (p.braid) {
        // a few extra edges between random rooms: alternative routes
        for (let i = 0; i < 3; i++) {
          const a = rooms[Math.floor(rng() * rooms.length)];
          const b = rooms[Math.floor(rng() * rooms.length)];
          if (a !== b) corridors.push([[a.x + a.w / 2, a.y + a.h / 2], [b.x + b.w / 2, b.y + b.h / 2]]);
        }
      }
      built = true;
    }

    slider(st.controls, T('depth'), 3, 6, p.depth, 1, v => String(v), v => { p.depth = v; generate(); });
    slider(st.controls, T('min_room'), 3, 7, p.minRoom, 1, v => String(v), v => { p.minRoom = v; generate(); });
    toggle(st.controls, T('braid'), true, v => { p.braid = v; generate(); });
    button(st.controls, T('new_dungeon'), () => { p.seed = Math.floor(Math.random() * 9999); generate(); });

    setTimeout(generate, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!built) return;
      const W = 58, H = 36;
      const pad = 8;
      const sx = (st.w - pad * 2) / W;
      const sy = (st.h - pad * 2) / H;
      const s = Math.min(sx, sy);
      const ox = (st.w - W * s) / 2, oy = (st.h - H * s) / 2;
      // corridors first
      st.ctx.strokeStyle = 'rgba(125,211,252,0.55)';
      st.ctx.lineWidth = Math.max(1, s * 0.5);
      corridors.forEach(([a, b]) => {
        st.ctx.beginPath();
        st.ctx.moveTo(ox + a[0] * s, oy + a[1] * s);
        const midx = ox + b[0] * s;
        st.ctx.lineTo(midx, oy + a[1] * s);
        st.ctx.lineTo(midx, oy + b[1] * s);
        st.ctx.stroke();
      });
      // split lines
      st.ctx.strokeStyle = 'rgba(255,255,255,0.07)';
      st.ctx.lineWidth = 1;
      splits.forEach((l) => {
        st.ctx.beginPath();
        st.ctx.moveTo(ox + l.x1 * s, oy + l.y1 * s);
        st.ctx.lineTo(ox + l.x2 * s, oy + l.y2 * s);
        st.ctx.stroke();
      });
      rooms.forEach((r, i) => {
        st.ctx.fillStyle = i % 2 ? 'rgba(110,231,183,0.20)' : 'rgba(200,247,81,0.16)';
        st.ctx.fillRect(ox + r.x * s, oy + r.y * s, r.w * s, r.h * s);
        st.ctx.strokeStyle = 'rgba(110,231,183,0.55)';
        st.ctx.strokeRect(ox + r.x * s + 0.5, oy + r.y * s + 0.5, r.w * s - 1, r.h * s - 1);
      });
      setReadout({
        rooms: String(rooms.length),
        depth: String(p.depth),
        edges: String(corridors.length)
      });
      label(st.ctx, 'BSP · ' + rooms.length + ' ' + T('rooms') + ' · ' + splits.length + ' ' + T('splits'),
        10, 13, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.depth = 5; p.minRoom = 4; p.seed = 11; generate(); };
    return handle;
  };

  /* ============================================================
     9. Drunkard's walk
     ============================================================ */
  DEMOS.randomwalk = function (el) {
    const st = makeStage(el);
    const p = { target: 0.5, stick: 0.7, agents: 4, seed: 5, speed: 3 };
    let g = null, cols = 0, rows = 0, walkers = [], carved = 0, done = false;
    const setReadout = readout(st.readout, [
      ['carved', T('coverage')], ['agents', T('agents')], ['steps', T('step')]
    ]);

    function reset() {
      cols = Math.max(24, Math.floor(st.w / 6));
      rows = Math.max(16, Math.floor(st.h / 6));
      g = [];
      for (let y = 0; y < rows; y++) g.push(new Uint8Array(cols).fill(1));
      const rng = mulberry32(p.seed * 313 + 17);
      walkers = [];
      for (let i = 0; i < p.agents; i++) {
        walkers.push({
          x: Math.floor(cols / 2) + (i % 2), y: Math.floor(rows / 2) + (i > 1 ? 1 : 0),
          dx: 1, dy: 0, steps: 0
        });
      }
      carved = 0;
      done = false;
    }
    function stepWalker(w, rng) {
      if (w.x > 0 && w.y > 0 && w.x < cols && w.y < rows && g[w.y][w.x]) {
        g[w.y][w.x] = 0;
        carved++;
        w.steps++;
      }
      const r = rng();
      if (r > p.stick) {
        if (rng() < 0.5) { const t = w.dx; w.dx = -w.dy; w.dy = t; }
        else { const t = w.dx; w.dx = w.dy; w.dy = -t; }
      }
      const nx = w.x + w.dx, ny = w.y + w.dy;
      if (nx > 1 && nx < cols - 1 && ny > 1 && ny < rows - 1) { w.x = nx; w.y = ny; }
      else { w.dx = -w.dx; w.dy = -w.dy; }
    }

    slider(st.controls, T('agents'), 1, 8, p.agents, 1, v => String(v), v => { p.agents = v; reset(); });
    slider(st.controls, T('stickiness'), 0.3, 0.95, p.stick, 0.05, v => v.toFixed(2), v => { p.stick = v; reset(); });
    slider(st.controls, T('coverage'), 0.3, 0.65, p.target, 0.01, v => (v * 100).toFixed(0) + '%', v => {
      p.target = v; reset();
    });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); reset(); });

    setTimeout(reset, 0);
    const handle = loop(() => {
      if (!g) return;
      const rng = mulberry32((p.seed * 7919 + carved * 131) >>> 0);
      if (!done) {
        const goal = cols * rows * p.target;
        for (let i = 0; i < p.speed * 40 && carved < goal; i++) {
          walkers.forEach((w) => stepWalker(w, rng));
        }
        if (carved >= goal) done = true;
      }
      clear(st, '#07080b');
      const cw = st.w / cols, ch = st.h / rows;
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          if (g[y][x]) continue;
          const shade = 0.4 + 0.6 * hash2(x, y, 3);
          st.ctx.fillStyle = 'rgba(' + Math.round(58 * shade) + ',' +
            Math.round(120 * shade) + ',' + Math.round(96 * shade) + ',1)';
          st.ctx.fillRect(x * cw, y * ch, cw + 0.4, ch + 0.4);
        }
      }
      walkers.forEach((w) => {
        st.ctx.fillStyle = C.acid;
        st.ctx.beginPath();
        st.ctx.arc((w.x + 0.5) * cw, (w.y + 0.5) * ch, 2.2, 0, TAU);
        st.ctx.fill();
      });
      const total = cols * rows;
      setReadout({
        carved: (100 * carved / total).toFixed(0) + '%',
        agents: String(p.agents),
        steps: String(walkers.reduce((a, w) => a + w.steps, 0))
      });
      label(st.ctx, done ? T('done') + ' · ' + T('coverage') + ' ' + (100 * carved / total).toFixed(0) + '%'
        : 'carving…', 10, 13, done ? C.mint : 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.target = 0.5; p.stick = 0.7; p.agents = 4; p.seed = 5; reset(); };
    return handle;
  };

  /* ============================================================
     10. Mazes (backtracker / Prim / Kruskal / Wilson)
     ============================================================ */
  DEMOS.maze = function (el) {
    const st = makeStage(el);
    const p = { algo: 'dfs', braid: 0, seed: 21, speed: 2 };
    let cols = 0, rows = 0, wallsH = null, wallsV = null, algo = null, done = false, cells = 0;
    const setReadout = readout(st.readout, [
      ['algo', T('algorithm')], ['cells', T('cells')], ['state', T('state')]
    ]);

    function reset() {
      cols = Math.max(15, Math.floor(st.w / 14)) | 1;
      rows = Math.max(11, Math.floor(st.h / 14)) | 1;
      wallsH = []; // horizontal walls between cell (x,y) and (x,y+1)
      wallsV = []; // vertical walls between (x,y) and (x+1,y)
      for (let y = 0; y < rows; y++) {
        wallsH.push(new Uint8Array(cols).fill(1));
        wallsV.push(new Uint8Array(cols).fill(1));
      }
      const rng = mulberry32(p.seed * 613 + 29);
      done = false;
      cells = 0;
      const visited = [];
      for (let y = 0; y < rows; y++) visited.push(new Uint8Array(cols));
      if (p.algo === 'dfs') {
        algo = { stack: [[1, 1]], visited, rng };
        visited[1][1] = 1;
      } else if (p.algo === 'prim') {
        const frontier = [];
        const addFrontier = (x, y) => {
          [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(([dx, dy]) => {
            const nx = x + dx, ny = y + dy;
            if (nx >= 0 && nx < cols && ny >= 0 && ny < rows && !visited[ny][nx]) {
              frontier.push([x, y, nx, ny]);
            }
          });
        };
        visited[1][1] = 1;
        addFrontier(1, 1);
        algo = { frontier, visited, rng, addFrontier };
      } else if (p.algo === 'kruskal') {
        const edges = [];
        for (let y = 0; y < rows; y++) {
          for (let x = 0; x < cols; x++) {
            if (x + 1 < cols) edges.push([x, y, x + 1, y]);
            if (y + 1 < rows) edges.push([x, y, x, y + 1]);
          }
        }
        for (let i = edges.length - 1; i > 0; i--) {
          const j = Math.floor(rng() * (i + 1));
          [edges[i], edges[j]] = [edges[j], edges[i]];
        }
        const parent = [];
        for (let i = 0; i < cols * rows; i++) parent.push(i);
        const find = (a) => {
          while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; }
          return a;
        };
        algo = { edges, parent, find };
      } else {
        algo = wilsonInit(rng);
      }
    }

    function wilsonInit(rng) {
      const inTree = [];
      for (let y = 0; y < rows; y++) inTree.push(new Uint8Array(cols));
      const sx = Math.floor(rng() * cols), sy = Math.floor(rng() * rows);
      inTree[sy][sx] = 1;
      // gather a random unvisited start
      const start = findUnvisited(inTree, rng);
      return { inTree, start, path: start ? [start] : [], rng, sx, sy };
    }
    function findUnvisited(inTree, rng) {
      const pool = [];
      for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) if (!inTree[y][x]) pool.push([x, y]);
      if (!pool.length) return null;
      return pool[Math.floor(rng() * pool.length)];
    }
    function removeWall(x1, y1, x2, y2) {
      if (x1 === x2) {
        const y = Math.min(y1, y2);
        wallsH[y][x1] = 0;
      } else {
        const x = Math.min(x1, x2);
        wallsV[y1][x] = 0;
      }
      cells++;
    }
    function stepAlgo() {
      if (done) return;
      if (p.algo === 'dfs') {
        const a = algo;
        if (!a.stack.length) { finish(); return; }
        const [x, y] = a.stack[a.stack.length - 1];
        const nbrs = [];
        [[2, 0], [-2, 0], [0, 2], [0, -2]].forEach(([dx, dy]) => {
          const nx = x + dx, ny = y + dy;
          if (nx > 0 && nx < cols && ny > 0 && ny < rows && !a.visited[ny][nx]) nbrs.push([nx, ny]);
        });
        if (nbrs.length) {
          const [nx, ny] = nbrs[Math.floor(a.rng() * nbrs.length)];
          a.visited[ny][nx] = 1;
          removeWall(x, y, (x + nx) / 2, (y + ny) / 2);
          removeWall((x + nx) / 2, (y + ny) / 2, nx, ny);
          a.stack.push([nx, ny]);
        } else {
          a.stack.pop();
        }
      } else if (p.algo === 'prim') {
        const a = algo;
        while (a.frontier.length) {
          const i = Math.floor(a.rng() * a.frontier.length);
          const [x, y, nx, ny] = a.frontier.splice(i, 1)[0];
          if (a.visited[ny][nx]) continue;
          a.visited[ny][nx] = 1;
          // cells are adjacent: they share exactly one wall
          removeWall(x, y, nx, ny);
          a.addFrontier(nx, ny);
          return;
        }
        finish();
      } else if (p.algo === 'kruskal') {
        const a = algo;
        while (a.edges.length) {
          const [x, y, nx, ny] = a.edges.pop();
          const ra = a.find(y * cols + x), rb = a.find(ny * cols + nx);
          if (ra === rb) continue;
          a.parent[ra] = rb;
          removeWall(x, y, nx, ny);
          return;
        }
        finish();
      } else {
        const a = algo;
        if (!a.start) { finish(); return; }
        // walk until we hit the tree
        let guard = 0;
        while (guard++ < 200) {
          const [x, y] = a.path[a.path.length - 1];
          if (a.inTree[y][x]) {
            // commit the path
            for (let i = 1; i < a.path.length; i++) {
              const [px, py] = a.path[i - 1], [cx, cy] = a.path[i];
              a.inTree[cy][cx] = 1;
              removeWall(px, py, cx, cy);
            }
            a.start = findUnvisited(a.inTree, a.rng);
            a.path = a.start ? [a.start] : [];
            if (!a.start) finish();
            return;
          }
          const opts = [];
          [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(([dx, dy]) => {
            const nx2 = x + dx, ny2 = y + dy;
            if (nx2 >= 0 && nx2 < cols && ny2 >= 0 && ny2 < rows) opts.push([nx2, ny2]);
          });
          // loop erasure: if we step onto a cell already in the path, cut back
          const [nx2, ny2] = opts[Math.floor(a.rng() * opts.length)];
          const hit = a.path.findIndex(([px, py]) => px === nx2 && py === ny2);
          if (hit >= 0) a.path.length = hit + 1;
          else a.path.push([nx2, ny2]);
        }
      }
    }
    function finish() {
      done = true;
      cells = Math.floor((cols - 1) / 2) * Math.floor((rows - 1) / 2);
      if (p.braid > 0) {
        const rng = mulberry32(p.seed * 31 + 7);
        for (let y = 1; y < rows - 1; y++) {
          for (let x = 1; x < cols - 1; x++) {
            if (rng() > p.braid) continue;
            if (x % 2 === 1 && y % 2 === 0 && wallsH[y][x]) {
              wallsH[y][x] = 0;
            } else if (y % 2 === 1 && x % 2 === 0 && wallsV[y][x]) {
              wallsV[y][x] = 0;
            }
          }
        }
      }
    }

    segmented(st.controls, [
      ['dfs', 'DFS'], ['prim', 'Prim'], ['kruskal', 'Kruskal'], ['wilson', 'Wilson']
    ], 'dfs', (id) => { p.algo = id; reset(); });
    slider(st.controls, T('braid'), 0, 0.5, 0, 0.05, v => Math.round(v * 100) + '%', v => {
      p.braid = v; if (done) { finish(); }
    });
    slider(st.controls, T('speed'), 1, 8, 2, 1, v => String(v), v => { p.speed = v; });
    button(st.controls, T('new_maze'), () => { p.seed = Math.floor(Math.random() * 9999); reset(); });

    setTimeout(reset, 0);
    const handle = loop(() => {
      if (!wallsH) return;
      for (let i = 0; i < p.speed * 18; i++) stepAlgo();
      clear(st, '#07080b');
      const pad = 10;
      const s = Math.min((st.w - pad * 2) / cols, (st.h - pad * 2) / rows);
      const ox = (st.w - cols * s) / 2, oy = (st.h - rows * s) / 2;
      st.ctx.fillStyle = 'rgba(200,247,81,0.06)';
      st.ctx.fillRect(ox, oy, cols * s, rows * s);
      st.ctx.strokeStyle = 'rgba(200,247,81,0.7)';
      st.ctx.lineWidth = Math.max(1, s * 0.12);
      st.ctx.beginPath();
      // outer border
      st.ctx.rect(ox, oy, cols * s, rows * s);
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          if (y < rows - 1 && wallsH[y][x]) {
            st.ctx.moveTo(ox + x * s, oy + (y + 1) * s);
            st.ctx.lineTo(ox + (x + 1) * s, oy + (y + 1) * s);
          }
          if (x < cols - 1 && wallsV[y][x]) {
            st.ctx.moveTo(ox + (x + 1) * s, oy + y * s);
            st.ctx.lineTo(ox + (x + 1) * s, oy + (y + 1) * s);
          }
        }
      }
      st.ctx.stroke();
      // entrance / exit
      st.ctx.fillStyle = C.acid;
      st.ctx.fillRect(ox + s, oy - 2, s * 0.4, 3);
      st.ctx.fillStyle = C.rose;
      st.ctx.fillRect(ox + (cols - 2) * s, oy + rows * s - 1, s * 0.4, 3);
      setReadout({
        algo: p.algo.toUpperCase(),
        cells: String(Math.floor((cols - 1) / 2) * Math.floor((rows - 1) / 2)),
        state: done ? 'perfect' : 'carving…'
      });
      label(st.ctx, (p.algo === 'dfs' ? 'recursive backtracker' : p.algo) +
        (p.braid ? ' · braided ' + Math.round(p.braid * 100) + '%' : ' · perfect'),
        10, 13, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.algo = 'dfs'; p.braid = 0; p.seed = 21; reset(); };
    return handle;
  };

  /* ============================================================
     11. Wave Function Collapse
     ============================================================ */
  DEMOS.wfc = function (el) {
    const st = makeStage(el);
    const p = { seed: 4, speed: 3, showEntropy: false };
    const COLORS = ['#12384a', '#c9b87a', '#5f8f52', '#2f6b45', '#7b7f78'];
    const WEIGHTS = [2.2, 1.0, 2.6, 2.0, 1.1];
    // adjacency is symmetric; each entry lists compatible neighbours
    const COMPAT = [
      [0, 1],          // water
      [0, 1, 2],       // sand
      [1, 2, 3, 4],    // grass
      [2, 3, 4],       // forest
      [2, 3, 4]        // rock
    ];
    let cols = 0, rows = 0, wave = null, state = null, contradictions = 0, restarts = 0;
    let hold = 0, seedSlider = null;
    const setReadout = readout(st.readout, [
      ['entropy', T('entropy')], ['contra', T('contra')],
      ['filled', T('collapsed')], ['restarts', T('restarts')]
    ]);

    function reset() {
      cols = Math.max(24, Math.floor(st.w / 8));
      rows = Math.max(14, Math.floor(st.h / 8));
      wave = new Array(cols * rows).fill(0b11111);
      state = { rng: mulberry32(p.seed * 991 + 3), todo: [] };
      contradictions = 0;
      restarts = 0;
    }
    function popcount(v) {
      let n = 0;
      while (v) { v &= v - 1; n++; }
      return n;
    }
    function compatible(a, b) {
      return COMPAT[a].indexOf(b) >= 0;
    }
    function propagate(x, y) {
      const todo = [[x, y]];
      while (todo.length) {
        const [cx, cy] = todo.pop();
        const m = wave[cy * cols + cx];
        for (let d = 0; d < 4; d++) {
          const nx = cx + (d === 0 ? 1 : d === 2 ? -1 : 0);
          const ny = cy + (d === 1 ? 1 : d === 3 ? -1 : 0);
          if (nx < 0 || nx >= cols || ny < 0 || ny >= rows) continue;
          let allowed = 0;
          for (let t = 0; t < 5; t++) {
            if (!(m >> t & 1)) continue;
            for (let o = 0; o < 5; o++) if (compatible(t, o)) allowed |= 1 << o;
          }
          const next = wave[ny * cols + nx] & allowed;
          if (next !== wave[ny * cols + nx]) {
            if (!next) return false;
            wave[ny * cols + nx] = next;
            todo.push([nx, ny]);
          }
        }
      }
      return true;
    }
    function collapseOne() {
      let best = -1, bestH = 99;
      for (let i = 0; i < wave.length; i++) {
        const c = popcount(wave[i]);
        if (c > 1 && c < bestH) { bestH = c; best = i; }
      }
      if (best < 0) return 'done';
      const m = wave[best];
      const choices = [];
      let total = 0;
      for (let t = 0; t < 5; t++) if (m >> t & 1) { choices.push(t); total += WEIGHTS[t]; }
      let r = state.rng() * total, pick = choices[0];
      for (const t of choices) { r -= WEIGHTS[t]; if (r <= 0) { pick = t; break; } }
      wave[best] = 1 << pick;
      return propagate(best % cols, Math.floor(best / cols)) ? 'ok' : 'contradiction';
    }

    seedSlider = slider(st.controls, T('seed'), 0, 99, p.seed, 1, v => String(v), v => { p.seed = v; reset(); });
    slider(st.controls, T('speed'), 1, 8, 3, 1, v => String(v), v => { p.speed = v; });
    toggle(st.controls, T('entropy'), false, v => { p.showEntropy = v; });
    button(st.controls, T('restart'), reset);

    setTimeout(reset, 0);
    const handle = loop((dt) => {
      if (!wave) return;
      for (let i = 0; i < p.speed * 8; i++) {
        const r = collapseOne();
        if (r === 'contradiction') {
          contradictions++;
          if (contradictions > 2) {
            reset();
            restarts++;
          }
          break;
        }
        if (r === 'done') break;
      }
      clear(st, '#07080b');
      const cw = st.w / cols, ch = st.h / rows;
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const m = wave[y * cols + x];
          const n = popcount(m);
          let col;
          if (n === 1) {
            col = COLORS[Math.log2(m) | 0];
          } else if (p.showEntropy) {
            const t = n / 5;
            col = 'rgb(' + Math.round(40 + t * 120) + ',' + Math.round(50 + t * 60) +
              ',' + Math.round(70 + t * 80) + ')';
          } else {
            col = 'rgba(255,255,255,0.08)';
          }
          st.ctx.fillStyle = col;
          st.ctx.fillRect(x * cw, y * ch, cw + 0.5, ch + 0.5);
        }
      }
      let collapsedCells = 0, branches = 0, open = 0;
      for (let i = 0; i < wave.length; i++) {
        const n = popcount(wave[i]);
        if (n === 1) collapsedCells++;
        else { branches += n; open++; }
      }
      setReadout({
        entropy: open ? (branches / open).toFixed(1) : '0.0',
        contra: String(contradictions),
        filled: (100 * collapsedCells / wave.length).toFixed(0) + '%',
        restarts: String(restarts)
      });
      label(st.ctx, 'WFC · 5 ' + T('tiles') + ' · ' + cols + '×' + rows, 10, 13, 'rgba(255,255,255,0.55)', 9);
      if (collapsedCells === wave.length) {
        hold += dt;
        if (hold > 1.8) {
          hold = 0;
          p.seed = (p.seed + 1 + Math.floor(Math.random() * 17)) % 100;
          if (seedSlider) seedSlider.set(p.seed);
          reset();
        }
      } else {
        hold = 0;
      }
    });
    handle.reset = () => { p.seed = 4; reset(); };
    return handle;
  };
})();
