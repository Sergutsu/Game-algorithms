/* ============================================================
   Interactive demos: Part II — procedural generation, file B
   Cities, terrain, biomes, rivers, L-systems and content systems.
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

  /* ---------- shared UI (same contract as file A) ---------- */
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
    return { get value() { return +input.value; } };
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
  function fbm(x, y, oct, seed) {
    let sum = 0, norm = 0, amp = 1, f = 1;
    for (let i = 0; i < oct; i++) {
      sum += amp * vnoise(x * f, y * f, seed + i * 131);
      norm += amp; amp *= 0.5; f *= 2;
    }
    return sum / norm;
  }

  /* ============================================================
     12. City: districts, MST roads, blocks
     ============================================================ */
  DEMOS.city = function (el) {
    const st = makeStage(el);
    const p = { districts: 8, density: 0.55, seed: 17 };
    let pts = [], edges = [], cells = null, cols = 0, rows = 0, buildings = 0;
    const setReadout = readout(st.readout, [
      ['districts', T('districts')], ['roads', T('roads')], ['houses', T('buildings')]
    ]);

    function generate() {
      const rng = mulberry32(p.seed * 4241 + 19);
      cols = 58; rows = 34;
      // district centres with a minimum distance (rejection sampling)
      pts = [];
      let guard = 0;
      while (pts.length < p.districts && guard++ < 4000) {
        const x = 3 + rng() * (cols - 6), y = 3 + rng() * (rows - 6);
        if (pts.every(q => Math.hypot(q[0] - x, q[1] - y) > 5)) pts.push([x, y]);
      }
      // Prim MST
      const n = pts.length;
      const inTree = new Array(n).fill(false);
      const best = new Array(n).fill(1e9);
      const parent = new Array(n).fill(-1);
      best[0] = 0;
      edges = [];
      for (let k = 0; k < n; k++) {
        let u = -1;
        for (let i = 0; i < n; i++) if (!inTree[i] && (u < 0 || best[i] < best[u])) u = i;
        inTree[u] = true;
        if (parent[u] >= 0) edges.push([parent[u], u]);
        for (let v = 0; v < n; v++) {
          if (inTree[v]) continue;
          const d = Math.hypot(pts[u][0] - pts[v][0], pts[u][1] - pts[v][1]);
          if (d < best[v]) { best[v] = d; parent[v] = u; }
        }
      }
      // a few extra links
      for (let i = 0; i < Math.max(1, Math.floor(n * 0.25)); i++) {
        const a = Math.floor(rng() * n), b = Math.floor(rng() * n);
        if (a !== b) edges.push([a, b]);
      }
      // district labels + buildings near roads
      cells = [];
      buildings = 0;
      for (let y = 0; y < rows; y++) {
        const row = [];
        for (let x = 0; x < cols; x++) {
          let bi = 0, bd = 1e9;
          pts.forEach((q, i) => {
            const d = Math.hypot(q[0] - x, q[1] - y);
            if (d < bd) { bd = d; bi = i; }
          });
          // distance to the road network (segments between centres)
          let rd = 1e9;
          edges.forEach(([a, b]) => {
            rd = Math.min(rd, segDist(x, y, pts[a], pts[b]));
          });
          const build = rd < 3.2 && hash2(x, y, p.seed) < p.density && rd > 0.45;
          if (build) buildings++;
          row.push({ d: bi, road: rd, build });
        }
        cells.push(row);
      }
    }
    function segDist(px, py, a, b) {
      const dx = b[0] - a[0], dy = b[1] - a[1];
      const l2 = dx * dx + dy * dy || 1;
      const t = clamp(((px - a[0]) * dx + (py - a[1]) * dy) / l2, 0, 1);
      return Math.hypot(px - (a[0] + dx * t), py - (a[1] + dy * t));
    }

    slider(st.controls, T('districts'), 3, 14, p.districts, 1, v => String(v), v => { p.districts = v; generate(); });
    slider(st.controls, T('density'), 0.2, 0.9, p.density, 0.05, v => Math.round(v * 100) + '%', v => {
      p.density = v; generate();
    });
    button(st.controls, T('new_city'), () => { p.seed = Math.floor(Math.random() * 9999); generate(); });

    setTimeout(generate, 0);
    const handle = loop(() => {
      if (!cells) return;
      clear(st, '#07080b');
      const pad = 8;
      const s = Math.min((st.w - pad * 2) / cols, (st.h - pad * 2) / rows);
      const ox = (st.w - cols * s) / 2, oy = (st.h - rows * s) / 2;
      const tints = ['#122a24', '#152a33', '#1b2a3a', '#2a2418', '#241b2a', '#1e2c1e'];
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const c = cells[y][x];
          st.ctx.fillStyle = tints[c.d % tints.length];
          st.ctx.fillRect(ox + x * s, oy + y * s, s + 0.5, s + 0.5);
        }
      }
      // buildings
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const c = cells[y][x];
          if (!c.build) continue;
          const k = hash2(x, y, p.seed + 5);
          st.ctx.fillStyle = k > 0.75 ? 'rgba(200,247,81,0.75)' : 'rgba(190,205,200,0.5)';
          const w = s * (0.35 + k * 0.35);
          st.ctx.fillRect(ox + (x + 0.5) * s - w / 2, oy + (y + 0.5) * s - w / 2, w, w);
        }
      }
      // roads on top
      st.ctx.strokeStyle = 'rgba(253,164,175,0.85)';
      st.ctx.lineWidth = Math.max(1.2, s * 0.35);
      edges.forEach(([a, b]) => {
        st.ctx.beginPath();
        st.ctx.moveTo(ox + pts[a][0] * s, oy + pts[a][1] * s);
        st.ctx.lineTo(ox + pts[b][0] * s, oy + pts[b][1] * s);
        st.ctx.stroke();
      });
      pts.forEach((q, i) => {
        st.ctx.fillStyle = i === 0 ? C.acid : 'rgba(255,255,255,0.9)';
        st.ctx.beginPath();
        st.ctx.arc(ox + q[0] * s, oy + q[1] * s, Math.max(1.6, s * 0.4), 0, TAU);
        st.ctx.fill();
      });
      setReadout({
        districts: String(p.districts),
        roads: String(edges.length),
        houses: String(buildings)
      });
      label(st.ctx, T('voronoi_districts') + ' · ' + T('mst_roads'), 10, 12, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.districts = 8; p.density = 0.55; p.seed = 17; generate(); };
    return handle;
  };

  /* ============================================================
     13. Hydraulic erosion
     ============================================================ */
  DEMOS.erosion = function (el) {
    const st = makeStage(el);
    const p = { drops: 26000, strength: 1, seed: 1337, showBefore: false };
    let W = 0, H = 0, base = null, h = null, done = 0, img = null, canvas2 = null, dirty = true, builtW = 0;
    const setReadout = readout(st.readout, [
      ['drops', T('droplets')], ['range', T('height_range')], ['state', T('state')]
    ]);

    function build() {
      W = clamp(Math.round(st.w / 1.6), 100, 260);
      H = clamp(Math.round(st.h / 1.9), 70, 180);
      base = new Float32Array(W * H);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          base[y * W + x] = fbm(x / W * 3.4, y / H * 3.4, 6, p.seed);
        }
      }
      h = Float32Array.from(base);
      done = 0;
      dirty = true;
      canvas2 = document.createElement('canvas');
      canvas2.width = W; canvas2.height = H;
      img = canvas2.getContext('2d').createImageData(W, H);
      builtW = st.w;
    }
    function droplet(rng) {
      let x = 1 + rng() * (W - 3), y = 1 + rng() * (H - 3);
      let dx = 0, dy = 0, speed = 1, water = 1, sed = 0;
      const inertia = 0.075, capK = 4 * p.strength;
      for (let s = 0; s < 44; s++) {
        const x0 = Math.floor(x), y0 = Math.floor(y);
        if (x0 < 1 || y0 < 1 || x0 >= W - 2 || y0 >= H - 2) break;
        const tx = x - x0, ty = y - y0;
        const i = y0 * W + x0;
        const h00 = h[i], h10 = h[i + 1], h01 = h[i + W], h11 = h[i + W + 1];
        const gx = (h10 - h00) * (1 - ty) + (h11 - h01) * ty;
        const gy = (h01 - h00) * (1 - tx) + (h11 - h10) * tx;
        dx = dx * inertia - gx * (1 - inertia);
        dy = dy * inertia - gy * (1 - inertia);
        const len = Math.hypot(dx, dy);
        if (len < 1e-6) break;
        dx /= len; dy /= len;
        x += dx; y += dy;
        const nx = Math.floor(x), ny = Math.floor(y);
        const dh = h[ny * W + nx] - h[i];
        const cap = Math.max(-dh, 0.001) * speed * water * capK;
        if (sed > cap || dh > 0) {
          const amt = dh > 0 ? Math.min(dh, sed) : sed;
          h[i] += amt * 0.3;
          sed -= amt * 0.3;
        } else {
          const amt = Math.min((cap - sed) * 0.3, -dh);
          h[i] -= amt;
          sed += amt;
        }
        speed = Math.sqrt(Math.max(0, speed * speed + dh * -2));
        water *= 0.99;
      }
    }
    function render() {
      const src = p.showBefore ? base : h;
      let lo = 1e9, hi = -1e9;
      for (let i = 0; i < W * H; i++) { lo = Math.min(lo, src[i]); hi = Math.max(hi, src[i]); }
      const span = Math.max(1e-4, hi - lo);
      const sea = 0.42;
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x;
          const v = (src[i] - lo) / span;
          let r, g, b;
          if (v < sea) {
            const d = 1 - v / sea;
            r = 12 + 12 * d; g = 34 + 30 * d; b = 56 + 44 * d;
          } else {
            const nx = (src[Math.min(W * H - 1, i + 1)] - src[Math.max(0, i - 1)]) * 260;
            const ny = (src[Math.min(W * H - 1, i + W)] - src[Math.max(0, i - W)]) * 260;
            let shade = clamp(0.72 - nx * 0.55 - ny * 0.35, 0.2, 1.25);
            const t = (v - sea) / (1 - sea);
            if (t < 0.16) { r = 190; g = 178; b = 138; }
            else if (t < 0.5) { r = 96; g = 132; b = 74; }
            else if (t < 0.78) { r = 128; g = 120; b = 100; }
            else { r = 214; g = 220; b = 216; }
            r = Math.min(255, r * shade); g = Math.min(255, g * shade); b = Math.min(255, b * shade);
          }
          const k = i * 4;
          img.data[k] = r; img.data[k + 1] = g; img.data[k + 2] = b; img.data[k + 3] = 255;
        }
      }
      canvas2.getContext('2d').putImageData(img, 0, 0);
    }

    slider(st.controls, T('droplets'), 4000, 90000, p.drops, 1000,
      v => (v / 1000).toFixed(0) + 'k', v => { p.drops = v; build(); });
    slider(st.controls, T('erosion_strength'), 0.3, 2.2, p.strength, 0.1,
      v => v.toFixed(1), v => { p.strength = v; build(); });
    toggle(st.controls, T('before'), false, v => { p.showBefore = v; dirty = true; });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); build(); });

    setTimeout(build, 0);
    const handle = loop(() => {
      if (!h) return;
      clear(st, '#07080b');
      if (Math.abs(st.w - builtW) > 30) build();
      if (done < p.drops) {
        const rng = mulberry32((p.seed * 7919 + done * 31) >>> 0);
        const batch = Math.min(700, p.drops - done);
        for (let i = 0; i < batch; i++) droplet(rng);
        done += batch;
        if (done % 3500 < 700) dirty = true;
      }
      if (dirty) { render(); dirty = false; }
      st.ctx.drawImage(canvas2, 0, 0, st.w, st.h);
      const g = st.ctx.createLinearGradient(0, st.h - 40, 0, st.h);
      g.addColorStop(0, 'rgba(7,8,11,0)');
      g.addColorStop(1, 'rgba(7,8,11,0.8)');
      st.ctx.fillStyle = g;
      st.ctx.fillRect(0, st.h - 40, st.w, 40);
      label(st.ctx, p.showBefore ? T('before') + ' · fBm' : T('after') + ' · ' + done.toLocaleString('en-US') + ' drops',
        10, st.h - 14, p.showBefore ? C.rose : C.mint, 9);
      setReadout({
        drops: done.toLocaleString('en-US'),
        range: (done / p.drops * 100).toFixed(0) + '%',
        state: done >= p.drops ? T('done') : T('running')
      });
    });
    handle.reset = () => { p.drops = 26000; p.strength = 1; p.showBefore = false; build(); };
    return handle;
  };

  /* ============================================================
     14. Biomes (Whittaker)
     ============================================================ */
  DEMOS.biomes = function (el) {
    const st = makeStage(el);
    const p = { sea: 0.42, temp: 0, moist: 0, seed: 71 };
    let W = 0, H = 0, canvas2 = null, biomeCounts = null, topBiome = '', builtW = 0;
    const setReadout = readout(st.readout, [
      ['biome', T('biome')], ['land', T('land')], ['climate', T('climate')]
    ]);

    const BIOMES = [
      { name: 'ocean', c: '#12384a' },
      { name: 'beach', c: '#c9b87a' },
      { name: 'desert', c: '#d8b86a' },
      { name: 'steppe', c: '#a8a05e' },
      { name: 'savanna', c: '#b58f4a' },
      { name: 'taiga', c: '#38664c' },
      { name: 'temperate', c: '#4f8a52' },
      { name: 'jungle', c: '#20663c' },
      { name: 'tundra', c: '#9fb2a8' },
      { name: 'rock', c: '#777d78' },
      { name: 'snow', c: '#dfe7e4' }
    ];
    function classify(temp, moist, height) {
      if (height < p.sea) return 0;
      if (height < p.sea + 0.035) return 1;
      const h = (height - p.sea) / (1 - p.sea);
      if (h < 0.028) return 1;
      if (h > 0.85) return h > 0.96 ? 10 : 9;
      if (temp < 0.2) return 8;
      if (temp < 0.42) return moist > 0.55 ? 5 : 8;
      if (moist < 0.24) return 2;
      if (moist < 0.42) return temp > 0.62 ? 4 : 3;
      if (moist < 0.66) return temp > 0.6 ? 6 : 5;
      return 7;
    }
    function build() {
      W = clamp(Math.round(st.w / 1.4), 120, 340);
      H = clamp(Math.round(st.h / 1.7), 80, 220);
      canvas2 = document.createElement('canvas');
      canvas2.width = W; canvas2.height = H;
      const ctx2 = canvas2.getContext('2d');
      const img = ctx2.createImageData(W, H);
      biomeCounts = new Array(BIOMES.length).fill(0);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const nx = x / W, ny = y / H;
          let e = fbm(nx * 3.2, ny * 3.2, 5, p.seed);
          e = clamp((e - 0.5) * 1.9 + 0.5, 0, 1);
          const lat = Math.abs(ny * 2 - 1);
          let temp = 1.04 - lat * 0.72 - Math.max(0, e - p.sea) * 0.55 + p.temp;
          temp = clamp(temp + (vnoise(nx * 8, ny * 8, p.seed + 5) - 0.5) * 0.18, 0, 1);
          let moist = clamp(0.68 - (e - p.sea) * 0.9 + p.moist +
            (vnoise(nx * 4.5, ny * 4.5, p.seed + 9) - 0.5) * 0.55, 0, 1);
          const bi = classify(temp, moist, e);
          biomeCounts[bi]++;
          const c = rgb(BIOMES[bi].c);
          const shade = 0.86 + 0.28 * (e - p.sea);
          const k = (y * W + x) * 4;
          img.data[k] = clamp(c[0] * shade, 0, 255);
          img.data[k + 1] = clamp(c[1] * shade, 0, 255);
          img.data[k + 2] = clamp(c[2] * shade, 0, 255);
          img.data[k + 3] = 255;
        }
      }
      ctx2.putImageData(img, 0, 0);
      builtW = st.w;
      let best = 1;
      for (let i = 1; i < BIOMES.length; i++) if (biomeCounts[i] > biomeCounts[best]) best = i;
      topBiome = BIOMES[best].name;
    }

    slider(st.controls, T('sea_level'), 0.3, 0.55, p.sea, 0.01, v => v.toFixed(2), v => { p.sea = v; build(); });
    slider(st.controls, T('temperature_lbl'), -0.35, 0.35, 0, 0.05, v => (v > 0 ? '+' : '') + v.toFixed(2), v => {
      p.temp = v; build();
    });
    slider(st.controls, T('moisture_lbl'), -0.35, 0.35, 0, 0.05, v => (v > 0 ? '+' : '') + v.toFixed(2), v => {
      p.moist = v; build();
    });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); build(); });

    setTimeout(build, 0);
    const handle = loop(() => {
      if (!canvas2) return;
      clear(st, '#07080b');
      if (Math.abs(st.w - builtW) > 30) build();
      st.ctx.drawImage(canvas2, 0, 0, st.w, st.h);
      // Whittaker inset
      const iw = Math.min(150, st.w * 0.38), ih = Math.min(92, st.h * 0.36);
      const ix = st.w - iw - 10, iy = st.h - ih - 10;
      st.ctx.fillStyle = 'rgba(7,8,11,0.82)';
      st.ctx.fillRect(ix - 5, iy - 14, iw + 10, ih + 19);
      st.ctx.strokeStyle = 'rgba(255,255,255,0.18)';
      st.ctx.strokeRect(ix, iy, iw, ih);
      const rows = ['tundra', 'taiga', 'temperate', 'savanna', 'desert'];
      const cols2 = ['dry', '', 'wet'];
      for (let r = 0; r < rows.length; r++) {
        for (let c = 0; c < 3; c++) {
          const t = r / (rows.length - 1);
          const m = c / 2;
          let name = classify(1 - t * 0.9, 0.15 + m * 0.7, 0.7);
          st.ctx.fillStyle = BIOMES[name].c;
          st.ctx.globalAlpha = 0.8;
          st.ctx.fillRect(ix + c * iw / 3, iy + r * ih / rows.length, iw / 3, ih / rows.length);
          st.ctx.globalAlpha = 1;
        }
      }
      st.ctx.fillStyle = 'rgba(255,255,255,0.9)';
      const mx = ix + clamp(0.5 + p.moist, 0, 1) * iw;
      const my = iy + (1 - clamp(0.5 + p.temp, 0, 1)) * ih;
      st.ctx.beginPath();
      st.ctx.arc(mx, my, 3, 0, TAU);
      st.ctx.fill();
      label(st.ctx, 'Whittaker', ix + 3, iy - 7, 'rgba(255,255,255,0.6)', 8);
      label(st.ctx, T('temp_arrow'), ix + iw / 2, iy + ih + 8, 'rgba(255,255,255,0.4)', 8, 'center');
      label(st.ctx, T('moist_arrow'), ix - 2, iy + ih / 2, 'rgba(255,255,255,0.4)', 8, 'right');
      let land = 0;
      biomeCounts.forEach((n, i) => { if (i !== 0) land += n; });
      setReadout({
        biome: T(topBiome),
        land: (100 * land / (W * H)).toFixed(0) + '%',
        climate: (p.temp >= 0 ? '+' : '') + p.temp.toFixed(2) + ' / ' +
          (p.moist >= 0 ? '+' : '') + p.moist.toFixed(2)
      });
      label(st.ctx, T('climate_map') + ' · ' + BIOMES.length + ' ' + T('biomes_lbl'), 10, 12, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.sea = 0.42; p.temp = 0; p.moist = 0; p.seed = 71; build(); };
    return handle;
  };

  /* ============================================================
     15. Rivers: priority-flood + D8 accumulation
     ============================================================ */
  DEMOS.rivers = function (el) {
    const st = makeStage(el);
    const p = { sea: 0.42, threshold: 260, seed: 1234, mode: 'rivers' };
    let W = 0, H = 0, canvas2 = null, area = null, down = null, water = null, builtW = 0;
    const setReadout = readout(st.readout, [
      ['rivers', T('rivers_lbl')], ['max', T('max_basin')], ['mode', T('mode')]
    ]);

    function build() {
      W = clamp(Math.round(st.w / 1.5), 110, 300);
      H = clamp(Math.round(st.h / 1.8), 75, 200);
      const h0 = new Float32Array(W * H);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          let e = fbm(x / W * 3.1, y / H * 3.1, 5, p.seed);
          e = clamp((e - 0.5) * 1.8 + 0.5, 0, 1);
          h0[y * W + x] = e;
        }
      }
      // priority-flood (binary heap of [height, index])
      const h = Float32Array.from(h0);
      const heap = [];
      const seen = new Uint8Array(W * H);
      const push = (z, i) => {
        heap.push([z, i]);
        let k = heap.length - 1;
        while (k > 0) {
          const par = (k - 1) >> 1;
          if (heap[par][0] <= heap[k][0]) break;
          [heap[par], heap[k]] = [heap[k], heap[par]];
          k = par;
        }
      };
      const pop = () => {
        const top = heap[0];
        const last = heap.pop();
        if (heap.length) {
          heap[0] = last;
          let k = 0;
          for (;;) {
            let s = k, l = k * 2 + 1, r = l + 1;
            if (l < heap.length && heap[l][0] < heap[s][0]) s = l;
            if (r < heap.length && heap[r][0] < heap[s][0]) s = r;
            if (s === k) break;
            [heap[s], heap[k]] = [heap[k], heap[s]];
            k = s;
          }
        }
        return top;
      };
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          if (x === 0 || y === 0 || x === W - 1 || y === H - 1) {
            seen[y * W + x] = 1;
            push(h[y * W + x], y * W + x);
          }
        }
      }
      while (heap.length) {
        const [z, i] = pop();
        const x = i % W, y = (i / W) | 0;
        [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(([dx, dy]) => {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= W || ny >= H) return;
          const j = ny * W + nx;
          if (seen[j]) return;
          seen[j] = 1;
          h[j] = Math.max(h[j], z + 1e-5);
          push(h[j], j);
        });
      }
      // D8 downstream
      down = new Int32Array(W * H).fill(-1);
      const order = [];
      for (let i = 0; i < W * H; i++) order.push(i);
      order.sort((a, b) => h0[b] - h0[a]);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          let bi = -1, bh = h[y * W + x];
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              if (!dx && !dy) continue;
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
              const j = ny * W + nx;
              if (h[j] < bh) { bh = h[j]; bi = j; }
            }
          }
          down[y * W + x] = bi;
        }
      }
      area = new Float32Array(W * H).fill(1);
      order.forEach((i) => {
        if (down[i] >= 0) area[down[i]] += area[i];
      });
      water = new Uint8Array(W * H);
      for (let i = 0; i < W * H; i++) water[i] = h0[i] < p.sea ? 1 : 0;
      // watershed root labels
      const root = new Int32Array(W * H).fill(-1);
      for (let i = 0; i < W * H; i++) {
        if (root[i] >= 0) continue;
        let j = i, guard = 0;
        while (down[j] >= 0 && root[j] < 0 && guard++ < 5000) j = down[j];
        const r = root[j] >= 0 ? root[j] : j;
        j = i;
        while (j >= 0 && root[j] < 0) { root[j] = r; j = down[j]; }
      }
      // raster
      canvas2 = document.createElement('canvas');
      canvas2.width = W; canvas2.height = H;
      const img = canvas2.getContext('2d').createImageData(W, H);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x;
          const e = h0[i];
          let c;
          if (e < p.sea) {
            c = mix(rgb('#0a2030'), rgb('#256b83'), clamp(e / p.sea, 0, 1));
          } else {
            const nx = (h0[Math.min(W * H - 1, i + 1)] - h0[Math.max(0, i - 1)]) * 300;
            const ny = (h0[Math.min(W * H - 1, i + W)] - h0[Math.max(0, i - W)]) * 300;
            const shade = clamp(0.8 - nx * 0.5 - ny * 0.3, 0.25, 1.2);
            c = mix(rgb('#4f6f45'), rgb('#c9c6a8'), clamp((e - p.sea) / (1 - p.sea), 0, 1) * 0.8);
            c = [c[0] * shade, c[1] * shade, c[2] * shade];
          }
          if (p.mode === 'rivers' && e >= p.sea && area[i] > p.threshold) {
            const w = clamp(Math.sqrt(area[i] / p.threshold) * 0.34, 0.34, 1);
            c = mix(c, rgb('#7dd3fc'), w);
          }
          if (p.mode === 'basins' && e >= p.sea) {
            const k = hash2(root[i] % 997, 3, 11);
            c = mix(c, [Math.round(60 + k * 170), Math.round(90 + (1 - k) * 130), Math.round(120 + k * 100)], 0.5);
          }
          const q = i * 4;
          img.data[q] = c[0]; img.data[q + 1] = c[1]; img.data[q + 2] = c[2]; img.data[q + 3] = 255;
        }
      }
      canvas2.getContext('2d').putImageData(img, 0, 0);
      builtW = st.w;
      let count = 0, maxA = 0;
      for (let i = 0; i < W * H; i++) {
        if (area[i] > p.threshold) count++;
        maxA = Math.max(maxA, area[i]);
      }
      setReadout({
        rivers: String(count),
        max: maxA.toFixed(0),
        mode: p.mode === 'rivers' ? T('rivers_lbl') : T('watersheds')
      });
    }

    segmented(st.controls, [
      ['rivers', T('rivers_lbl')], ['basins', T('watersheds')]
    ], 'rivers', (id) => { p.mode = id; build(); });
    slider(st.controls, T('sea_level'), 0.3, 0.55, p.sea, 0.01, v => v.toFixed(2), v => { p.sea = v; build(); });
    slider(st.controls, T('threshold'), 40, 900, p.threshold, 20, v => String(v), v => {
      p.threshold = v; build();
    });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); build(); });

    setTimeout(build, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!canvas2) return;
      if (Math.abs(st.w - builtW) > 30) build();
      st.ctx.drawImage(canvas2, 0, 0, st.w, st.h);
      label(st.ctx, p.mode === 'rivers' ? 'D8 flow accumulation' : 'watersheds (D8 roots)',
        10, 12, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { p.sea = 0.42; p.threshold = 260; p.seed = 1234; build(); };
    return handle;
  };

  /* ============================================================
     16. L-systems
     ============================================================ */
  DEMOS.lsystem = function (el) {
    const st = makeStage(el);
    const p = { preset: 'tree', iterations: 5, angle: 24, seed: 5 };
    let segs = [], builtW = 0, growth = 0;
    const setReadout = readout(st.readout, [
      ['segments', T('segments')], ['iterations', T('iterations')], ['preset', T('preset')]
    ]);
    const PRESETS = {
      tree: { axiom: 'X', rules: { X: 'F[+X][-X]FX', F: 'FF' }, angle: 24, iter: 5 },
      fern: { axiom: 'X', rules: { X: 'F[+X]F[-X]+X', F: 'FF' }, angle: 20, iter: 6 },
      plant: { axiom: 'F', rules: { F: 'FF+[+F-F-F]-[-F+F+F]' }, angle: 22, iter: 4 },
      hilbert: { axiom: 'A', rules: { A: '-BF+AFA+FB-', B: '+AF-BFB-FA+' }, angle: 90, iter: 4 },
      dragon: { axiom: 'FX', rules: { X: 'X+YF+', Y: '-FX-Y' }, angle: 90, iter: 9 },
      koch: { axiom: 'F--F--F', rules: { F: 'F+F--F+F' }, angle: 60, iter: 4 }
    };

    function expand() {
      const preset = PRESETS[p.preset];
      let s = preset.axiom;
      const limit = 120000;
      for (let i = 0; i < p.iterations && s.length < limit; i++) {
        let out = '';
        for (let k = 0; k < s.length; k++) out += preset.rules[s[k]] || s[k];
        s = out;
      }
      return s;
    }
    function build() {
      const preset = PRESETS[p.preset];
      const s = expand();
      const angle = p.angle * Math.PI / 180;
      let x = 0, y = 0, dir = -Math.PI / 2;
      const stack = [];
      segs = [];
      let minX = 0, maxX = 0, minY = 0, maxY = 0;
      for (let i = 0; i < s.length; i++) {
        const ch = s[i];
        if (ch === 'F' || ch === 'G') {
          const nx = x + Math.cos(dir), ny = y + Math.sin(dir);
          segs.push([x, y, nx, ny, stack.length]);
          x = nx; y = ny;
          minX = Math.min(minX, x); maxX = Math.max(maxX, x);
          minY = Math.min(minY, y); maxY = Math.max(maxY, y);
        } else if (ch === '+') dir += angle;
        else if (ch === '-') dir -= angle;
        else if (ch === '[') stack.push([x, y, dir]);
        else if (ch === ']') { const q = stack.pop(); x = q[0]; y = q[1]; dir = q[2]; }
      }
      segs.bounds = { minX, maxX, minY, maxY };
      builtW = st.w;
      growth = 0;
      setReadout({
        segments: segs.length.toLocaleString('en-US'),
        iterations: String(p.iterations),
        preset: T(p.preset)
      });
    }

    function pick(id) {
      p.preset = id;
      p.iterations = PRESETS[id].iter;
      p.angle = PRESETS[id].angle;
      build();
    }
    segmented(st.controls, [
      ['tree', T('tree')], ['fern', T('fern')], ['plant', T('plant')],
      ['hilbert', T('hilbert')], ['dragon', T('dragon')], ['koch', T('koch')]
    ], 'tree', pick);
    slider(st.controls, T('iterations'), 1, 9, p.iterations, 1, v => String(v), v => {
      p.iterations = Math.min(v, p.preset === 'dragon' ? 12 : 7); build();
    });
    slider(st.controls, T('angle'), 5, 120, p.angle, 1, v => v + '°', v => { p.angle = v; build(); });

    setTimeout(build, 0);
    const handle = loop((dt) => {
      clear(st, '#07080b');
      if (!segs.length) return;
      if (Math.abs(st.w - builtW) > 24) build();
      growth = Math.min(1, growth + dt * 0.9);
      const b = segs.bounds;
      const pad = 22;
      const sx = (st.w - pad * 2) / Math.max(1e-6, b.maxX - b.minX);
      const sy = (st.h - pad * 2) / Math.max(1e-6, b.maxY - b.minY);
      const s = Math.min(sx, sy);
      const ox = (st.w - (b.maxX - b.minX) * s) / 2 - b.minX * s;
      const oy = (st.h - (b.maxY - b.minY) * s) / 2 - b.minY * s;
      const upTo = Math.floor(segs.length * growth);
      st.ctx.lineCap = 'round';
      for (let i = 0; i < upTo; i++) {
        const q = segs[i];
        const depth = q[4];
        st.ctx.strokeStyle = depth < 2 ? 'rgba(200,247,81,0.95)'
          : depth < 4 ? 'rgba(110,231,183,0.85)' : 'rgba(125,211,252,0.6)';
        st.ctx.lineWidth = Math.max(0.8, (5 - Math.min(4, depth)) * 0.55);
        st.ctx.beginPath();
        st.ctx.moveTo(ox + q[0] * s, oy + q[1] * s);
        st.ctx.lineTo(ox + q[2] * s, oy + q[3] * s);
        st.ctx.stroke();
      }
      label(st.ctx, T(p.preset) + ' · n=' + p.iterations + ' · ' + p.angle + '° · ' +
        segs.length.toLocaleString('en-US') + ' F', 10, st.h - 12, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { pick('tree'); };
    return handle;
  };

  /* ============================================================
     17. Shape grammar: split-rule facades
     ============================================================ */
  DEMOS.shapegrammar = function (el) {
    const st = makeStage(el);
    const p = { style: 'modern', units: 8, depth: 6, jitter: 0.5, lit: 0.45, seed: 21 };
    let leaves = [], builtW = 0, builtH = 0, reveal = 0, litPct = 0;
    const setReadout = readout(st.readout, [
      ['cells', T('cells')], ['depth', T('depth')], ['lit', T('lit')]
    ]);

    function palette() {
      if (p.style === 'brick') return { wall: '#2f1c17', frame: '#5d382c', glass: '#243139', glow: '#fbbf6b' };
      if (p.style === 'glass') return { wall: '#16242f', frame: '#33495b', glass: '#28475a', glow: '#ffe3a8' };
      return { wall: '#121820', frame: '#26313c', glass: '#1f2f3b', glow: '#ffd08a' };
    }

    function build() {
      const pad = 16;
      const x0 = pad, y0 = pad + 4;
      const W = Math.max(140, st.w - pad * 2);
      const H = Math.max(120, st.h - pad * 2 - 14);
      const unit = W / p.units;
      const rng = mulberry32(p.seed * 7919 + p.units * 17 + p.depth * 31 + p.style.length);
      leaves = [];

      function snap(frac, total) {
        let part = Math.round(total * frac / unit) * unit;
        part = Math.max(0.26 * total, Math.min(0.74 * total, part));
        return part / total;
      }
      function rec(x, y, w, h, depth) {
        if (depth >= p.depth || w < unit * 0.72 || h < unit * 0.6) {
          const win = w > unit * 0.3 && h > unit * 0.25 && rng() < 0.9;
          leaves.push({ x, y, w, h, depth, win });
          return;
        }
        const f = snap(0.5 + (rng() - 0.5) * p.jitter, w > h ? w : h);
        if (p.style === 'glass' || w > h * 1.05) {
          rec(x, y, w * f, h, depth + 1);
          rec(x + w * f, y, w * (1 - f), h, depth + 1);
        } else {
          rec(x, y, w, h * f, depth + 1);
          rec(x, y + h * f, w, h * (1 - f), depth + 1);
        }
      }
      rec(x0, y0, W, H, 0);
      leaves.sort((a, b) => a.depth - b.depth || a.y - b.y);
      let lit = 0;
      leaves.forEach((l) => {
        l.lit = l.win && hash2(Math.round(l.x * 3), Math.round(l.y * 3), p.seed) < p.lit;
        if (l.lit) lit++;
      });
      litPct = Math.round(100 * lit / Math.max(1, leaves.length));
      reveal = 0;
      builtW = st.w; builtH = st.h;
      setReadout({ cells: String(leaves.length), depth: String(p.depth), lit: litPct + '%' });
    }

    segmented(st.controls, [
      ['modern', T('modern')], ['brick', T('brick')], ['glass', T('glass')]
    ], 'modern', (id) => { p.style = id; build(); });
    slider(st.controls, T('units'), 5, 14, p.units, 1, v => String(v), v => { p.units = v; build(); });
    slider(st.controls, T('depth'), 3, 6, p.depth, 1, v => String(v), v => { p.depth = v; build(); });
    slider(st.controls, T('lit'), 0, 0.9, p.lit, 0.05, v => Math.round(v * 100) + '%', v => { p.lit = v; build(); });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); build(); });

    setTimeout(build, 0);
    const handle = loop((dt) => {
      if (!leaves.length) return;
      if (Math.abs(st.w - builtW) > 24 || Math.abs(st.h - builtH) > 24) build();
      reveal = Math.min(p.depth + 1, reveal + dt * 7);
      const pal = palette();
      clear(st, '#07080b');
      const bg = st.ctx.createLinearGradient(0, 0, 0, st.h);
      bg.addColorStop(0, '#080b10'); bg.addColorStop(1, '#121a22');
      st.ctx.fillStyle = bg; st.ctx.fillRect(0, 0, st.w, st.h);

      st.ctx.fillStyle = 'rgba(0,0,0,0.45)';
      st.ctx.fillRect(18, st.h - 24, st.w - 36, 12);
      st.ctx.fillStyle = pal.wall;
      st.ctx.fillRect(13, 17, st.w - 26, st.h - 46);

      leaves.forEach((l) => {
        if (l.depth > reveal) return;
        const inset = Math.max(1, Math.min(2.4, l.w * 0.07));
        if (!l.win) {
          st.ctx.fillStyle = pal.frame;
          st.ctx.fillRect(l.x, l.y, l.w, l.h);
          return;
        }
        st.ctx.fillStyle = pal.frame;
        st.ctx.fillRect(l.x, l.y, l.w, l.h);
        const g = st.ctx.createLinearGradient(l.x, l.y, l.x + l.w, l.y + l.h);
        if (l.lit) { g.addColorStop(0, pal.glow); g.addColorStop(1, '#e08b45'); }
        else { g.addColorStop(0, pal.glass); g.addColorStop(1, '#0d1822'); }
        st.ctx.fillStyle = g;
        st.ctx.fillRect(l.x + inset, l.y + inset,
          Math.max(1, l.w - inset * 2), Math.max(1, l.h - inset * 2));
      });

      label(st.ctx, T('facade') + ' · ' + T(p.style) + ' · ' + leaves.length + ' ' + T('cells'),
        10, st.h - 8, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => {
      p.style = 'modern'; p.units = 8; p.depth = 6; p.lit = 0.45; p.seed = 21;
      build();
    };
    return handle;
  };

  /* ============================================================
     17. Item generator
     ============================================================ */
  DEMOS.items = function (el) {
    const st = makeStage(el);
    const p = { ilvl: 60, rarity: 'legendary', seed: 123, count: 3 };
    let items = [];
    const setReadout = readout(st.readout, [
      ['budget', T('budget')], ['affixes', T('affixes')], ['rarity', T('rarity')]
    ]);
    const COLS = {
      common: '#9aa39c', rare: '#7dd3fc', epic: '#c4b5fd', legendary: '#fbbf6b'
    };
    const AFFIX = [
      { k: 'damage', name: 'of Ruin', rng: [4, 12], cost: 1.0 },
      { k: 'crit', name: 'of Precision', rng: [2, 8], cost: 1.4 },
      { k: 'life', name: 'of Vigour', rng: [10, 40], cost: 1.1 },
      { k: 'resist', name: 'of Warding', rng: [3, 15], cost: 0.8 },
      { k: 'speed', name: 'of Haste', rng: [3, 9], cost: 1.6 },
      { k: 'move', name: 'of the Wind', rng: [2, 8], cost: 0.6 }
    ];
    const BASE = ['Iron Blade', 'Oaken Staff', 'Runed Axe', 'Warden Plate', 'Cinder Ring'];
    const PREFIX = ['Rusted', 'Gleaming', 'Ancient', 'Cursed', 'Stormforged'];
    const RARITY = { common: [1, 1.0], rare: [2, 1.35], epic: [3, 1.7], legendary: [4, 2.1] };

    function roll() {
      const rng = mulberry32(p.seed * 6151 + p.ilvl * 13 + 7);
      const [count, mult] = RARITY[p.rarity];
      const budget = (6 + p.ilvl * 1.6) * mult;
      items = [];
      for (let n = 0; n < p.count; n++) {
        const pool = AFFIX.slice();
        for (let i = pool.length - 1; i > 0; i--) {
          const j = Math.floor(rng() * (i + 1));
          [pool[i], pool[j]] = [pool[j], pool[i]];
        }
        const chosen = [];
        let spent = 0;
        for (const a of pool) {
          if (chosen.length >= count) break;
          const frac = (rng() + rng() + rng()) / 3;      // bell-ish, mean 0.5
          const val = Math.round(a.rng[0] + (a.rng[1] - a.rng[0]) * frac);
          const cost = frac * a.cost * 3;
          if (spent + cost > budget && chosen.length) continue;
          spent += cost;
          chosen.push({ name: a.name, val, k: a.k });
        }
        const base = BASE[Math.floor(rng() * BASE.length)];
        const prefix = PREFIX[Math.floor(rng() * PREFIX.length)];
        items.push({
          name: prefix + ' ' + base,
          suffix: chosen.length ? chosen[0].name : '',
          affixes: chosen,
          power: clamp(spent / budget, 0, 1)
        });
      }
      setReadout({
        budget: String(Math.round(budget)),
        affixes: String(items.reduce((a, it) => a + it.affixes.length, 0)),
        rarity: T(p.rarity)
      });
    }
    const STAT = { damage: 'DMG', crit: 'CRIT', life: 'HP', resist: 'RES', speed: 'SPD', move: 'MOV' };

    segmented(st.controls, [
      ['common', T('common')], ['rare', T('rare')], ['epic', T('epic')], ['legendary', T('legendary')]
    ], 'legendary', (id) => { p.rarity = id; roll(); });
    slider(st.controls, T('level'), 1, 100, p.ilvl, 1, v => String(v), v => { p.ilvl = v; roll(); });
    button(st.controls, T('reroll'), () => { p.seed = Math.floor(Math.random() * 99999); roll(); });

    setTimeout(roll, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!items.length) return;
      const pad = 12;
      const gap = 8;
      const cardH = Math.min(76, (st.h - pad * 2 - gap * (p.count - 1)) / p.count);
      items.forEach((it, i) => {
        const y = pad + i * (cardH + gap);
        st.ctx.fillStyle = 'rgba(255,255,255,0.035)';
        st.ctx.fillRect(pad, y, st.w - pad * 2, cardH);
        st.ctx.fillStyle = COLS[p.rarity];
        st.ctx.fillRect(pad, y, 3, cardH);
        st.ctx.font = '600 12px ui-monospace, Menlo, monospace';
        st.ctx.textBaseline = 'middle';
        st.ctx.textAlign = 'left';
        st.ctx.fillStyle = COLS[p.rarity];
        st.ctx.fillText(it.name, pad + 10, y + 14);
        st.ctx.fillStyle = 'rgba(231,237,223,0.9)';
        st.ctx.font = '10px ui-monospace, Menlo, monospace';
        st.ctx.fillText('iLvl ' + p.ilvl + ' · ' + p.rarity, pad + 10, y + 30);
        let ax = pad + 10;
        it.affixes.forEach((a) => {
          const text = '+' + a.val + ' ' + STAT[a.k];
          const w = st.ctx.measureText(text).width + 10;
          st.ctx.fillStyle = 'rgba(110,231,183,0.16)';
          st.ctx.fillRect(ax, y + 40, w, 15);
          st.ctx.fillStyle = C.mint;
          st.ctx.fillText(text, ax + 5, y + 47.5);
          ax += w + 5;
        });
        // power bar
        st.ctx.fillStyle = 'rgba(255,255,255,0.10)';
        st.ctx.fillRect(pad + 10, y + cardH - 9, st.w - pad * 2 - 20, 3);
        st.ctx.fillStyle = COLS[p.rarity];
        st.ctx.fillRect(pad + 10, y + cardH - 9, (st.w - pad * 2 - 20) * it.power, 3);
      });
      label(st.ctx, T('budget') + ' · ' + T('rarity_mult') + ' ' + RARITY[p.rarity][1] + '×',
        12, st.h - 3, 'rgba(255,255,255,0.4)', 8);
    });
    handle.reset = () => { p.ilvl = 60; p.rarity = 'legendary'; p.seed = 123; roll(); };
    return handle;
  };

  /* ============================================================
     18. Name generator (Markov + syllables)
     ============================================================ */
  DEMOS.names = function (el) {
    const st = makeStage(el);
    const p = { culture: 'elf', order: 2, seed: 8 };
    let names = [];
    const setReadout = readout(st.readout, [
      ['count', T('generated')], ['uniq', T('unique')], ['order', T('order')]
    ]);
    const CORPUS = {
      elf: ['aelire', 'thalion', 'lindari', 'erendil', 'silmar', 'noldor', 'galadriel', 'mireth', 'aranel', 'celeborn'],
      orc: ['grommash', 'zugor', 'kragg', 'morgul', 'snagrat', 'uruk', 'ghazat', 'karbag', 'zulmak', 'durgash'],
      nord: ['bjorn', 'sigrid', 'halvard', 'ragnar', 'astrid', 'eirik', 'gunnar', 'solveig', 'ivar', 'freya'],
      latin: ['valerius', 'aurelia', 'maximus', 'cassia', 'octavia', 'lucius', 'serena', 'titus', 'livia', 'felix']
    };
    const ENDINGS = { elf: ['iel', 'or', 'wen', 'las'], orc: ['ak', 'gul', 'ash', 'uk'], nord: ['sson', 'dottir', 'heim', 'vik'], latin: ['us', 'a', 'ian', 'or'] };

    function model() {
      const m = {};
      CORPUS[p.culture].forEach((name) => {
        const s = '^'.repeat(p.order) + name + '$';
        for (let i = 0; i < s.length - p.order; i++) {
          const st0 = s.slice(i, i + p.order);
          (m[st0] = m[st0] || []).push(s[i + p.order]);
        }
      });
      return m;
    }
    function gen(m, rng) {
      let state = '^'.repeat(p.order);
      let out = '';
      for (let i = 0; i < 18; i++) {
        const nxt = m[state];
        if (!nxt || !nxt.length) break;
        const ch = nxt[Math.floor(rng() * nxt.length)];
        if (ch === '$') break;
        out += ch;
        state = (state + ch).slice(-p.order);
      }
      if (out.length < 4) return null;
      const ends = ENDINGS[p.culture];
      if (p.culture !== 'nord' && rng() < 0.5) {
        // keep some names as-is, some get a regional suffix
        out = out.slice(0, Math.max(3, out.length - 1)) + ends[Math.floor(rng() * ends.length)];
      }
      return out[0].toUpperCase() + out.slice(1);
    }
    function build() {
      const rng = mulberry32(p.seed * 811 + p.order * 17 + p.culture.length);
      const m = model();
      names = [];
      let guard = 0;
      while (names.length < 36 && guard++ < 900) {
        const n = gen(m, rng);
        if (n && names.indexOf(n) < 0) names.push(n);
      }
      setReadout({
        count: String(names.length),
        uniq: '100%',
        order: String(p.order)
      });
    }

    segmented(st.controls, [
      ['elf', T('elf')], ['orc', T('orc')], ['nord', T('nord')], ['latin', T('latin')]
    ], 'elf', (id) => { p.culture = id; build(); });
    slider(st.controls, T('order'), 1, 3, p.order, 1, v => String(v), v => { p.order = v; build(); });
    button(st.controls, T('reroll'), () => { p.seed = Math.floor(Math.random() * 99999); build(); });

    setTimeout(build, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      const cols3 = st.w > 460 ? 3 : 2;
      const rows3 = Math.ceil(names.length / cols3);
      const cw = (st.w - 20) / cols3;
      const ch = Math.min(22, (st.h - 26) / Math.max(1, rows3));
      names.forEach((n, i) => {
        const x = 12 + (i % cols3) * cw;
        const y = 18 + Math.floor(i / cols3) * ch;
        st.ctx.font = (ch > 17 ? 11 : 9) + 'px ui-monospace, Menlo, monospace';
        st.ctx.textAlign = 'left';
        st.ctx.textBaseline = 'middle';
        st.ctx.fillStyle = 'rgba(231,237,223,' + (0.95 - (i / names.length) * 0.35) + ')';
        st.ctx.fillText(n, x, y);
      });
      label(st.ctx, T(p.culture) + ' · ' + T('markov_order') + ' ' + p.order, 10, st.h - 6,
        'rgba(255,255,255,0.45)', 8);
    });
    handle.reset = () => { p.culture = 'elf'; p.order = 2; p.seed = 8; build(); };
    return handle;
  };

  /* ============================================================
     19. Quest / mission graph
     ============================================================ */
  DEMOS.quests = function (el) {
    const st = makeStage(el);
    const p = { depth: 4, keys: 0.55, seed: 31, speed: 1 };
    let nodes = [], edges = [], builtW = 0, reveal = 0, solvable = true;
    const setReadout = readout(st.readout, [
      ['nodes', T('nodes')], ['edges', T('edges')], ['solvable', T('solvable')]
    ]);
    const KIND = {
      start: C.acid, kill: C.rose, fetch: C.sky, escort: C.amber,
      explore: C.violet, key: C.mint, door: '#9aa39c', goal: '#fbbf6b'
    };

    function generate() {
      const rng = mulberry32(p.seed * 3571 + 13);
      nodes = [{ id: 0, type: 'start', deps: [] }];
      edges = [];
      let prev = 0, nid = 1;
      const add = (type, deps) => {
        const id = nid++;
        nodes.push({ id, type, deps });
        deps.forEach((d) => edges.push([d, id]));
        return id;
      };
      for (let step = 0; step < p.depth; step++) {
        const kinds = ['kill', 'fetch', 'escort', 'explore'];
        prev = add(kinds[Math.floor(rng() * kinds.length)], [prev]);
        if (step < p.depth - 1 && rng() < p.keys) {
          const k = add('key', [prev]);
          prev = add('door', [k]);
        }
        if (step > 0 && rng() < 0.4) {
          // optional side branch, not required for the goal
          add(['explore', 'fetch'][Math.floor(rng() * 2)], [prev]);
        }
      }
      const goal = add('goal', [prev]);
      // solvability: every door needs a key reachable before it
      solvable = check();
      // levels for layout
      const byId = {};
      nodes.forEach((n) => { byId[n.id] = n; });
      nodes.forEach((n) => { n.level = 0; });
      for (let pass = 0; pass < 12; pass++) {
        nodes.forEach((n) => {
          n.deps.forEach((d) => { n.level = Math.max(n.level, byId[d].level + 1); });
        });
      }
      nodes.forEach((n) => { n.goal = n.id === goal; });
      builtW = st.w;
      reveal = 0;
      setReadout({ nodes: String(nodes.length), edges: String(edges.length), solvable: solvable ? '✓' : '✗' });
    }
    function check() {
      const reach = new Set([0]);
      let changed = true;
      while (changed) {
        changed = false;
        nodes.forEach((n) => {
          if (reach.has(n.id)) return;
          if (n.deps.length && n.deps.some((d) => reach.has(d))) {
            reach.add(n.id);
            changed = true;
          }
        });
      }
      return reach.size === nodes.length;
    }

    slider(st.controls, T('depth'), 2, 7, p.depth, 1, v => String(v), v => { p.depth = v; generate(); });
    slider(st.controls, T('keys'), 0, 1, p.keys, 0.05, v => Math.round(v * 100) + '%', v => {
      p.keys = v; generate();
    });
    button(st.controls, T('reroll'), () => { p.seed = Math.floor(Math.random() * 99999); generate(); });

    setTimeout(generate, 0);
    const handle = loop((dt) => {
      clear(st, '#07080b');
      if (!nodes.length) return;
      if (Math.abs(st.w - builtW) > 24) generate();
      reveal = Math.min(nodes.length, reveal + dt * nodes.length * 0.8);
      const show = Math.floor(reveal);
      const maxLevel = Math.max(1, ...nodes.map((n) => n.level));
      const pad = 20;
      const colW = (st.w - pad * 2) / (maxLevel + 1);
      const byLevel = {};
      nodes.forEach((n) => { (byLevel[n.level] = byLevel[n.level] || []).push(n); });
      const pos = {};
      Object.keys(byLevel).forEach((lvl) => {
        const arr = byLevel[lvl];
        arr.forEach((n, i) => {
          const x = pad + n.level * colW + colW / 2;
          const y = st.h / 2 + (i - (arr.length - 1) / 2) * Math.min(34, (st.h - 50) / Math.max(1, arr.length));
          pos[n.id] = [x, y];
        });
      });
      st.ctx.lineWidth = 1;
      edges.forEach(([a, b]) => {
        if (b >= show) return;
        const pa = pos[a], pb = pos[b];
        st.ctx.strokeStyle = 'rgba(255,255,255,0.16)';
        st.ctx.beginPath();
        st.ctx.moveTo(pa[0], pa[1]);
        st.ctx.bezierCurveTo((pa[0] + pb[0]) / 2, pa[1], (pa[0] + pb[0]) / 2, pb[1], pb[0], pb[1]);
        st.ctx.stroke();
      });
      nodes.forEach((n, i) => {
        const q = pos[n.id];
        if (i > show) return;
        st.ctx.globalAlpha = i === show ? 0.5 : 1;
        st.ctx.fillStyle = KIND[n.type] || C.ink;
        st.ctx.beginPath();
        st.ctx.arc(q[0], q[1], n.goal ? 6 : 4.2, 0, TAU);
        st.ctx.fill();
        if (n.type === 'key' || n.type === 'door' || n.goal) {
          st.ctx.font = '8px ui-monospace, Menlo, monospace';
          st.ctx.textAlign = 'center';
          st.ctx.textBaseline = 'middle';
          st.ctx.fillStyle = 'rgba(7,8,11,0.95)';
          st.ctx.fillText(n.type === 'key' ? 'K' : n.type === 'door' ? 'D' : '★', q[0], q[1] + 0.5);
        }
        st.ctx.globalAlpha = 1;
      });
      label(st.ctx, T('solvable') + ': ' + (solvable ? '✓' : '✗') + ' · ' + nodes.length + ' nodes',
        st.w - 10, 12, solvable ? C.mint : C.rose, 9, 'right');
    });
    handle.reset = () => { p.depth = 4; p.keys = 0.55; p.seed = 31; generate(); };
    return handle;
  };

  /* ============================================================
     20. Generative music (Markov + pentatonic)
     ============================================================ */
  DEMOS.musicgen = function (el) {
    const st = makeStage(el);
    const p = { tempo: 112, seed: 12, scale: 'penta', octave: 0, playing: false };
    let notes = [], startAt = 0, audio = null, playBtn = null;
    const setReadout = readout(st.readout, [
      ['notes', T('notes')], ['tempo', T('tempo')], ['scale', T('scale')]
    ]);
    const SCALES = {
      penta: [0, 2, 4, 7, 9, 12, 14, 16],
      major: [0, 2, 4, 5, 7, 9, 11, 12],
      minor: [0, 2, 3, 5, 7, 8, 10, 12]
    };
    const ROOT = 220;

    function compose() {
      const rng = mulberry32(p.seed * 137 + 5);
      const scale = SCALES[p.scale];
      let deg = 3;
      notes = [];
      for (let i = 0; i < 32; i++) {
        const r = rng();
        let step = r < 0.28 ? 0 : r < 0.62 ? (rng() < 0.5 ? 1 : -1) : r < 0.85 ? (rng() < 0.5 ? 2 : -2) : (rng() < 0.5 ? 3 : -3);
        deg = clamp(deg + step, 0, scale.length - 1);
        notes.push({
          deg: deg,
          len: rng() < 0.22 ? 2 : 1,
          vel: 0.5 + rng() * 0.5,
          beat: i
        });
      }
      setReadout({
        notes: String(notes.length),
        tempo: String(p.tempo),
        scale: p.scale === 'penta' ? T('pentatonic') : T(p.scale)
      });
    }
    function noteHz(deg) {
      return ROOT * Math.pow(2, (SCALES[p.scale][deg] + p.octave * 12) / 12);
    }
    function stopAudio() {
      p.playing = false;
      if (audio) { try { audio.close(); } catch (e) { /* noop */ } audio = null; }
      if (playBtn) playBtn.textContent = T('play');
    }
    function play() {
      stopAudio();
      try {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return;
        audio = new Ctx();
        p.playing = true;
        startAt = audio.currentTime + 0.08;
        const spb = 60 / p.tempo / 2;
        notes.forEach((n) => {
          const osc = audio.createOscillator();
          const gain = audio.createGain();
          osc.type = 'triangle';
          osc.frequency.value = noteHz(n.deg);
          const t0 = startAt + n.beat * spb;
          const dur = spb * n.len * 0.92;
          gain.gain.setValueAtTime(0, t0);
          gain.gain.linearRampToValueAtTime(0.12 * n.vel, t0 + 0.012);
          gain.gain.exponentialRampToValueAtTime(0.0008, t0 + dur);
          osc.connect(gain).connect(audio.destination);
          osc.start(t0);
          osc.stop(t0 + dur + 0.02);
        });
        if (playBtn) playBtn.textContent = T('stop');
        setTimeout(() => { if (p.playing) stopAudio(); }, (startAt + notes.length * spb + 0.3) * 1000 - (audio ? audio.currentTime * 1000 : 0));
      } catch (e) {
        stopAudio();
      }
    }

    segmented(st.controls, [
      ['penta', T('pentatonic')], ['major', T('major')], ['minor', T('minor')]
    ], 'penta', (id) => { p.scale = id; stopAudio(); compose(); });
    slider(st.controls, T('tempo'), 70, 180, p.tempo, 2, v => String(v), v => { p.tempo = v; });
    slider(st.controls, T('octave'), -1, 2, 0, 1, v => (v > 0 ? '+' : '') + v, v => { p.octave = v; });
    button(st.controls, T('reroll'), () => { p.seed = Math.floor(Math.random() * 99999); stopAudio(); compose(); });
    playBtn = button(st.controls, T('play'), () => { if (p.playing) stopAudio(); else play(); });

    setTimeout(compose, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!notes.length) return;
      const lane = st.h - 34;
      const noteH = Math.max(4, (lane - 16) / 9);
      const bw = (st.w - 20) / notes.length;
      // grid
      st.ctx.strokeStyle = 'rgba(255,255,255,0.05)';
      for (let i = 0; i < 9; i++) {
        st.ctx.beginPath();
        st.ctx.moveTo(10, 12 + i * noteH);
        st.ctx.lineTo(st.w - 10, 12 + i * noteH);
        st.ctx.stroke();
      }
      notes.forEach((n, i) => {
        const y = 12 + (8 - n.deg) * noteH;
        st.ctx.fillStyle = 'rgba(110,231,183,' + (0.55 + n.vel * 0.4) + ')';
        st.ctx.fillRect(10 + i * bw + 1, y, Math.max(2, bw * n.len - 2), noteH - 1.5);
      });
      if (p.playing && audio) {
        const spb = 60 / p.tempo / 2;
        const beat = (audio.currentTime - startAt) / spb;
        const x = 10 + clamp(beat, 0, notes.length) * bw;
        st.ctx.fillStyle = C.acid;
        st.ctx.fillRect(x, 10, 1.5, lane - 10);
      }
      label(st.ctx, p.playing ? T('playing') : 'markov melody · 32 notes',
        10, st.h - 8, p.playing ? C.acid : 'rgba(255,255,255,0.45)', 8);
    });
    handle.reset = () => { p.tempo = 112; p.scale = 'penta'; p.seed = 12; stopAudio(); compose(); };
    return handle;
  };


  /* ============================================================
     22. Volumetric-style clouds (layered domain-warped fBm)
     ============================================================ */
  DEMOS.clouds = function (el) {
    const st = makeStage(el);
    const p = { coverage: 0.52, scale: 5, speed: 0.25, seed: 31 };
    let bmp = null, bw = 0, bh = 0, builtW = 0, phase = 0, acc = 0, covPct = 0;
    const setReadout = readout(st.readout, [
      ['cover', T('coverage')], ['oct', T('octaves')], ['wind', T('wind')]
    ]);

    function density(u, v) {
      const wx = fbm(u * 0.7 + 11.3, v * 0.5 - 4.1, 2, p.seed + 61) - 0.5;
      const wy = fbm(u * 0.6 - 2.7, v * 0.7 + 7.7, 2, p.seed + 83) - 0.5;
      const q = fbm(u + wx * 0.8, v + wy * 0.8, 5, p.seed);
      return q * 0.72 + fbm(u * 2.3 + 5.1, v * 2.3 - 3.4, 3, p.seed + 17) * 0.28;
    }

    function build() {
      bw = clamp(Math.round(st.w / 3.4), 100, 240);
      bh = clamp(Math.round(st.h / 2.8), 70, 150);
      bmp = document.createElement('canvas');
      bmp.width = bw; bmp.height = bh;
      const ctx2 = bmp.getContext('2d');
      const img = ctx2.createImageData(bw, bh);
      let covered = 0;
      for (let y = 0; y < bh; y++) {
        const ny = y / bh;
        for (let x = 0; x < bw; x++) {
          const nx = x / bw;
          // sky gradient: deep blue up top, pale at the horizon
          const sky = mix(rgb('#0b1b33'), rgb('#7e93a8'), Math.pow(ny, 1.5));
          let c = sky;
          const horizonFade = clamp((1 - ny) * 3.2, 0, 1);
          let alpha = 0;
          for (let layer = 0; layer < 2; layer++) {
            const depth = 0.5 + layer * 0.55;
            const u = (nx - 0.5) * p.scale * depth + phase * (1.1 + layer * 0.7) + layer * 23;
            const v = (0.55 + (ny - 0.35) * 1.7) * p.scale * depth * 0.55 + layer * 7.3;
            const d = density(u, v);
            const cover = clamp((d - p.coverage) / 0.16, 0, 1);
            if (layer === 0) covered += cover > 0.4 ? 1 : 0;
            // shade from the density gradient: light from the upper left
            const lit = clamp(0.55 + (d - 0.5) * 1.4 + (0.5 - nx) * 0.12, 0.15, 1.15);
            const cloud = mix(rgb('#5a6675'), rgb('#f4f1e6'), lit);
            const a = cover * (layer === 0 ? 0.9 : 0.65) * (0.35 + horizonFade * 0.65);
            if (a > alpha) alpha = a;
            c = mix(c, mix(cloud, sky, 0.02), alpha);
          }
          const i = (y * bw + x) * 4;
          img.data[i] = c[0]; img.data[i + 1] = c[1]; img.data[i + 2] = c[2]; img.data[i + 3] = 255;
        }
      }
      ctx2.putImageData(img, 0, 0);
      // sun glow over the clouds: light comes from the upper left
      const g = ctx2.createRadialGradient(bw * 0.22, bh * 0.2, 2, bw * 0.22, bh * 0.2, bw * 0.3);
      g.addColorStop(0, 'rgba(255,240,200,0.5)');
      g.addColorStop(0.35, 'rgba(255,220,170,0.16)');
      g.addColorStop(1, 'rgba(255,220,170,0)');
      ctx2.fillStyle = g;
      ctx2.fillRect(0, 0, bw, bh);
      covPct = 100 * covered / (bw * bh);
      builtW = st.w;
    }

    slider(st.controls, T('coverage'), 0.35, 0.68, p.coverage, 0.01, v => (v * 100).toFixed(0) + '%', v => {
      p.coverage = v; build();
    });
    slider(st.controls, T('scale'), 2, 10, p.scale, 1, v => String(v), v => { p.scale = v; build(); });
    slider(st.controls, T('wind'), 0, 1, p.speed, 0.05, v => v.toFixed(2), v => { p.speed = v; });
    button(st.controls, T('new_seed'), () => { p.seed = Math.floor(Math.random() * 9999); build(); });

    setTimeout(build, 0);
    const handle = loop((dt) => {
      if (!bmp) return;
      if (Math.abs(st.w - builtW) > 30) build();
      acc += dt;
      if (p.speed > 0 && acc > 0.16) { phase += acc * p.speed * 1.6; acc = 0; build(); }
      clear(st, '#07080b');
      st.ctx.drawImage(bmp, 0, 0, st.w, st.h);
      label(st.ctx, T('clouds_note'), 10, 13,
        'rgba(255,255,255,0.55)', 9);
      setReadout({ cover: covPct.toFixed(0) + '%', oct: '5 + 3', wind: p.speed.toFixed(2) });
    });
    handle.reset = () => { p.coverage = 0.52; p.scale = 5; p.speed = 0.25; p.seed = 31; build(); };
    return handle;
  };

  /* ============================================================
     21. AI director
     ============================================================ */
  DEMOS.director = function (el) {
    const st = makeStage(el);
    const p = { aggression: 1, seed: 3 };
    let t = 0, intensity = 0.2, budget = 0, cooldown = 0, hp = 1, waves = [], history = [];
    const setReadout = readout(st.readout, [
      ['waves', T('waves')], ['budget', T('budget_lbl')], ['hp', T('player_hp')]
    ]);

    function targetAt(time) {
      const a = 0.34 + 0.42 * Math.pow(Math.sin(time * 0.55), 2);
      const b = time > 26 ? 0.18 * Math.sin(time * 0.9) : 0;
      return clamp((a + b) * p.aggression, 0.15, 1);
    }
    function reset() {
      t = 0; intensity = 0.2; budget = 0; cooldown = 1.2; hp = 1;
      waves = []; history = [];
    }

    slider(st.controls, T('aggression'), 0.5, 1.6, 1, 0.05, v => v.toFixed(2), v => { p.aggression = v; });
    button(st.controls, T('reset_short'), reset);
    button(st.controls, T('reroll'), () => { p.seed = Math.floor(Math.random() * 999); reset(); });

    setTimeout(reset, 0);
    const handle = loop((dt) => {
      clear(st, '#07080b');
      const speed = 2.2;
      t += dt * speed;
      if (t > 40) reset();
      const goal = targetAt(t);
      const measured = clamp(0.15 + waves.filter((w) => t - w.at < 3).length * 0.18 + (1 - hp) * 0.25, 0, 1);
      intensity += (measured - intensity) * Math.min(1, dt * speed * 2);
      const err = goal - intensity;
      budget = clamp(budget + err * 1.1 * dt * speed, 0, 9);
      cooldown = Math.max(0, cooldown - dt * speed);
      if (cooldown <= 0 && budget >= 1.2) {
        budget -= 1.2;
        cooldown = 1.5;
        waves.push({ at: t, x: Math.random() });
        hp = clamp(hp - 0.06, 0.05, 1);
      }
      if (waves.filter((w) => t - w.at < 3).length === 0) hp = clamp(hp + dt * speed * 0.03, 0.05, 1);
      history.push({ t: t, i: intensity, g: goal });
      if (history.length > 900) history.shift();
      while (waves.length && t - waves[0].at > 6) waves.shift();

      // graph
      const gx = 14, gy = 22, gw = st.w - 28, gh = st.h * 0.5;
      st.ctx.strokeStyle = 'rgba(110,231,183,0.55)';
      st.ctx.lineWidth = 1.2;
      st.ctx.beginPath();
      history.forEach((h, i) => {
        const x = gx + (h.t / 40) * gw;
        const y = gy + (1 - h.g) * gh;
        if (i) st.ctx.lineTo(x, y); else st.ctx.moveTo(x, y);
      });
      st.ctx.stroke();
      st.ctx.strokeStyle = 'rgba(200,247,81,0.9)';
      st.ctx.beginPath();
      history.forEach((h, i) => {
        const x = gx + (h.t / 40) * gw;
        const y = gy + (1 - h.i) * gh;
        if (i) st.ctx.lineTo(x, y); else st.ctx.moveTo(x, y);
      });
      st.ctx.stroke();
      // spawn markers
      waves.forEach((w) => {
        const x = gx + (w.at / 40) * gw;
        st.ctx.fillStyle = 'rgba(253,164,175,0.55)';
        st.ctx.fillRect(x - 1.5, gy, 3, gh);
      });
      // budget bar
      const by = gy + gh + 20;
      st.ctx.fillStyle = 'rgba(255,255,255,0.08)';
      st.ctx.fillRect(gx, by, gw, 8);
      st.ctx.fillStyle = C.acid;
      st.ctx.fillRect(gx, by, gw * clamp(budget / 9, 0, 1), 8);
      label(st.ctx, T('budget_lbl') + ' ' + budget.toFixed(1), gx, by + 18, 'rgba(255,255,255,0.5)', 8);
      // hp bar
      const hy = by + 30;
      st.ctx.fillStyle = 'rgba(255,255,255,0.08)';
      st.ctx.fillRect(gx, hy, gw, 6);
      st.ctx.fillStyle = hp > 0.35 ? C.mint : C.rose;
      st.ctx.fillRect(gx, hy, gw * hp, 6);
      label(st.ctx, T('player_hp') + ' ' + Math.round(hp * 100) + '%', gx, hy + 14,
        'rgba(255,255,255,0.5)', 8);
      label(st.ctx, T('target_lbl'), gx, 12, 'rgba(255,255,255,0.55)', 8);
      label(st.ctx, T('intensity'), st.w - 14, 12, 'rgba(255,255,255,0.55)', 8, 'right');
      setReadout({
        waves: String(waves.filter((w) => t - w.at < 3).length),
        budget: budget.toFixed(1),
        hp: Math.round(hp * 100) + '%'
      });
    });
    handle.reset = () => { p.aggression = 1; reset(); };
    return handle;
  };
})();
