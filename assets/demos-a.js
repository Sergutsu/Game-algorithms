/* ============================================================
   Interactive demos, part A (topics 1–23)
   Plain canvas 2D, no dependencies. Each demo returns a handle
   with start / stop / toggle / reset.
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
          // one bad frame must not kill the page, but we report it to the console once
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

  function grid(st, step, color) {
    const ctx = st.ctx;
    ctx.save();
    ctx.strokeStyle = color || C.faint;
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
     1. Ballistics
     ============================================================ */
  DEMOS.ballistics = function (el) {
    const st = makeStage(el);
    const params = { angle: 45, speed: 72, drag: 0.00035, wind: 0 };
    const G = 9.81;
    let shell = null;
    let trail = [];
    let shots = [];
    let lastStats = { range: 0, apex: 0, tof: 0 };

    const setReadout = readout(st.readout, [
      ['range', T('range')], ['apex', T('apex')], ['tof', T('flight')]
    ]);

    function accel(vx, vy) {
      const rx = vx - params.wind;
      const ry = vy;
      const sp = Math.hypot(rx, ry);
      const k = params.drag;
      return [-k * sp * rx, -G - k * sp * ry];
    }
    function step(s, dt) {
      const a1 = accel(s.vx, s.vy);
      const vx2 = s.vx + a1[0] * dt / 2, vy2 = s.vy + a1[1] * dt / 2;
      const a2 = accel(vx2, vy2);
      const vx3 = s.vx + a2[0] * dt / 2, vy3 = s.vy + a2[1] * dt / 2;
      const a3 = accel(vx3, vy3);
      const vx4 = s.vx + a3[0] * dt, vy4 = s.vy + a3[1] * dt;
      const a4 = accel(vx4, vy4);
      s.vx += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]);
      s.vy += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1]);
      s.x += s.vx * dt;
      s.y += s.vy * dt;
    }

    function predict() {
      const rad = params.angle * Math.PI / 180;
      const s = { x: 0, y: 1.4, vx: Math.cos(rad) * params.speed, vy: Math.sin(rad) * params.speed };
      const pts = [{ x: s.x, y: s.y }];
      let apex = s.y, t = 0;
      const dt = 1 / 240;
      while (s.y >= 0 && t < 60) {
        step(s, dt);
        t += dt;
        apex = Math.max(apex, s.y);
        if (pts.length < 2000) pts.push({ x: s.x, y: s.y });
      }
      lastStats = { range: s.x, apex, tof: t };
      // smoothly fit the scale to the trajectory
      fitRange += (Math.max(30, s.x) - fitRange) * 0.12;
      fitApex += (Math.max(20, apex) - fitApex) * 0.12;
      return pts;
    }

    let fitRange = 420, fitApex = 120;
    function world() {
      const padX = 46, padTop = 26, padBottom = 28;
      const scale = Math.min(
        (st.w - padX * 2) / Math.max(20, fitRange),
        (st.h - padTop - padBottom) / Math.max(12, fitApex)
      );
      return { scale, x0: padX, y0: st.h - padBottom };
    }
    function toScreen(p, wld) {
      return [wld.x0 + p.x * wld.scale, wld.y0 - p.y * wld.scale];
    }

    function reset() {
      const rad = params.angle * Math.PI / 180;
      shell = {
        x: 0, y: 1.4,
        vx: Math.cos(rad) * params.speed,
        vy: Math.sin(rad) * params.speed
      };
      trail = [];
    }

    function onParam() { reset(); predict(); }

    slider(st.controls, T('angle'), 5, 80, params.angle, 1, v => v + '°', v => { params.angle = v; onParam(); });
    slider(st.controls, T('speed'), 20, 130, params.speed, 1, v => v + T('ms_unit'), v => { params.speed = v; onParam(); });
    slider(st.controls, T('drag'), 0, 0.0016, params.drag, 0.00005, v => v.toFixed(4), v => { params.drag = v; onParam(); });
    slider(st.controls, T('wind'), -18, 18, params.wind, 1, v => v + T('ms_unit'), v => { params.wind = v; onParam(); });

    let predictTimer = 0;
    reset();
    predict();

    const handle = loop((dt) => {
      const wld = world();
      clear(st, '#07080b');
      grid(st, 32);

      // ground with distance ticks
      st.ctx.strokeStyle = 'rgba(255,255,255,0.24)';
      st.ctx.beginPath();
      st.ctx.moveTo(0, wld.y0);
      st.ctx.lineTo(st.w, wld.y0);
      st.ctx.stroke();
      const tickStep = fitRange > 600 ? 200 : fitRange > 300 ? 100 : 50;
      for (let d = 0; d <= fitRange + tickStep; d += tickStep) {
        const [tx, ty] = toScreen({ x: d, y: 0 }, wld);
        if (tx > st.w - 4) break;
        st.ctx.strokeStyle = 'rgba(255,255,255,0.18)';
        st.ctx.beginPath();
        st.ctx.moveTo(tx, ty);
        st.ctx.lineTo(tx, ty + 4);
        st.ctx.stroke();
        label(st.ctx, String(d), tx, ty + 12, C.dim, 8, 'center');
      }

      // predicted path
      if (predictTimer <= 0) { predict(); predictTimer = 0.25; }
      predictTimer -= dt;
      const pts = predict();
      st.ctx.save();
      st.ctx.setLineDash([4, 5]);
      st.ctx.strokeStyle = 'rgba(200,247,81,0.38)';
      st.ctx.lineWidth = 1.4;
      st.ctx.beginPath();
      pts.forEach((p, i) => {
        const [x, y] = toScreen(p, wld);
        if (i === 0) st.ctx.moveTo(x, y); else st.ctx.lineTo(x, y);
      });
      st.ctx.stroke();
      st.ctx.restore();

      // previous shots
      shots.forEach((s, idx) => {
        st.ctx.strokeStyle = 'rgba(125,211,252,' + (0.35 - idx * 0.08) + ')';
        st.ctx.lineWidth = 1;
        st.ctx.beginPath();
        s.path.forEach((p, i) => {
          const [x, y] = toScreen(p, wld);
          if (i === 0) st.ctx.moveTo(x, y); else st.ctx.lineTo(x, y);
        });
        st.ctx.stroke();
      });

      // physics
      for (let i = 0; i < 4; i++) step(shell, dt / 4);
      trail.push({ x: shell.x, y: shell.y });
      if (trail.length > 220) trail.shift();

      if (shell.y < 0) {
        shots.unshift({ path: trail.slice() });
        shots = shots.slice(0, 3);
        reset();
      }

      // trail
      st.ctx.strokeStyle = C.amber;
      st.ctx.lineWidth = 2;
      st.ctx.beginPath();
      trail.forEach((p, i) => {
        const [x, y] = toScreen(p, wld);
        if (i === 0) st.ctx.moveTo(x, y); else st.ctx.lineTo(x, y);
      });
      st.ctx.stroke();

      const [sx, sy] = toScreen(shell, wld);
      const glow = st.ctx.createRadialGradient(sx, sy, 0, sx, sy, 16);
      glow.addColorStop(0, 'rgba(251,191,107,0.9)');
      glow.addColorStop(1, 'rgba(251,191,107,0)');
      st.ctx.fillStyle = glow;
      st.ctx.beginPath(); st.ctx.arc(sx, sy, 16, 0, TAU); st.ctx.fill();
      st.ctx.fillStyle = '#fff';
      st.ctx.beginPath(); st.ctx.arc(sx, sy, 3, 0, TAU); st.ctx.fill();

      // launcher
      const [lx, ly] = toScreen({ x: 0, y: 0 }, wld);
      st.ctx.strokeStyle = C.ink;
      st.ctx.lineWidth = 2;
      const rad = params.angle * Math.PI / 180;
      st.ctx.beginPath();
      st.ctx.moveTo(lx, ly);
      st.ctx.lineTo(lx + Math.cos(rad) * 20, ly - Math.sin(rad) * 20);
      st.ctx.stroke();

      label(st.ctx, T('wind_pad') + params.wind + T('ms_unit'), 10, 14, C.dim, 9);
      setReadout({
        range: lastStats.range.toFixed(0) + T('m_unit'),
        apex: lastStats.apex.toFixed(1) + T('m_unit'),
        tof: lastStats.tof.toFixed(2) + T('s_unit')
      });
    });
    handle.reset = reset;
    return handle;
  };

  /* ============================================================
     2. Boids / flocking
     ============================================================ */
  DEMOS.boids = function (el) {
    const st = makeStage(el);
    const N = 110;
    const agents = [];
    const rnd = mulberry32(7);
    for (let i = 0; i < N; i++) {
      agents.push({
        x: rnd() * 300, y: rnd() * 200,
        vx: (rnd() - 0.5) * 60, vy: (rnd() - 0.5) * 60,
        phase: rnd() * TAU
      });
    }
    const mouse = { x: 0, y: 0, active: false };
    const params = { cohesion: 1.0, separation: 1.0, speed: 1.0 };
    const setReadout = readout(st.readout, [['n', T('agents')], ['align', T('alignment')], ['spread', T('radius')]]);

    st.canvas.addEventListener('pointermove', (e) => {
      const r = st.canvas.getBoundingClientRect();
      mouse.x = e.clientX - r.left;
      mouse.y = e.clientY - r.top;
      mouse.active = true;
    });
    st.canvas.addEventListener('pointerleave', () => { mouse.active = false; });

    slider(st.controls, T('cohesion'), 0, 2.4, params.cohesion, 0.05, v => v.toFixed(2), v => params.cohesion = v);
    slider(st.controls, T('separation'), 0.2, 2.4, params.separation, 0.05, v => v.toFixed(2), v => params.separation = v);

    function frame(dt) {
      const SEP = 24, ALI = 58, COH = 96;
      const maxSpeed = 96;
      let sumSpeed = 0;
      for (const b of agents) {
        let sx = 0, sy = 0, sxN = 0;
        let ax = 0, ay = 0, aN = 0;
        let cx = 0, cy = 0, cN = 0;
        for (const o of agents) {
          if (o === b) continue;
          const dx = o.x - b.x, dy = o.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 1e-4) continue;
          const d = Math.sqrt(d2);
          if (d < SEP) { sx += dx / d; sy += dy / d; sxN++; }
          if (d < ALI) { ax += o.vx; ay += o.vy; aN++; }
          if (d < COH) { cx += o.x; cy += o.y; cN++; }
        }
        let fx = 0, fy = 0;
        // separation: stronger when the birds are close
        if (sxN) {
          const m = Math.hypot(sx, sy) || 1;
          fx -= (sx / m) * 150 * params.separation;
          fy -= (sy / m) * 150 * params.separation;
        }
        if (aN) {
          const m = Math.hypot(ax, ay) || 1;
          fx += (ax / m * maxSpeed - b.vx) * 1.4;
          fy += (ay / m * maxSpeed - b.vy) * 1.4;
        }
        if (cN) {
          const dx = cx / cN - b.x, dy = cy / cN - b.y;
          const m = Math.hypot(dx, dy) || 1;
          fx += (dx / m * maxSpeed - b.vx) * 0.75 * params.cohesion;
          fy += (dy / m * maxSpeed - b.vy) * 0.75 * params.cohesion;
        }
        if (mouse.active) {
          const dx = mouse.x - b.x, dy = mouse.y - b.y;
          const d = Math.hypot(dx, dy) || 1;
          if (d < 150) { fx += dx / d * 220; fy += dy / d * 220; }
        }
        const fm = Math.hypot(fx, fy);
        const maxForce = 320;
        if (fm > maxForce) { fx = fx / fm * maxForce; fy = fy / fm * maxForce; }

        b.vx += fx * dt;
        b.vy += fy * dt;
        const sp = Math.hypot(b.vx, b.vy) || 1;
        if (sp > maxSpeed) { b.vx = b.vx / sp * maxSpeed; b.vy = b.vy / sp * maxSpeed; }
        if (sp < 38) { b.vx = b.vx / sp * 38; b.vy = b.vy / sp * 38; }
        b.x += b.vx * dt;
        b.y += b.vy * dt;

        if (b.x < 0) { b.x = 0; b.vx = Math.abs(b.vx); }
        if (b.x > st.w) { b.x = st.w; b.vx = -Math.abs(b.vx); }
        if (b.y < 0) { b.y = 0; b.vy = Math.abs(b.vy); }
        if (b.y > st.h) { b.y = st.h; b.vy = -Math.abs(b.vy); }
        sumSpeed += Math.hypot(b.vx, b.vy);
        b.phase += dt * 6;
      }
      return sumSpeed / agents.length;
    }

    const handle = loop((dt) => {
      clear(st, '#07080b');
      grid(st, 40);
      const avg = frame(Math.min(dt, 0.033));
      let minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
      for (const b of agents) {
        minX = Math.min(minX, b.x); maxX = Math.max(maxX, b.x);
        minY = Math.min(minY, b.y); maxY = Math.max(maxY, b.y);
        const a = Math.atan2(b.vy, b.vx);
        st.ctx.save();
        st.ctx.translate(b.x, b.y);
        st.ctx.rotate(a);
        st.ctx.fillStyle = 'rgba(200,247,81,' + (0.55 + 0.4 * Math.sin(b.phase)) + ')';
        st.ctx.beginPath();
        st.ctx.moveTo(6, 0);
        st.ctx.lineTo(-4, 3.2);
        st.ctx.lineTo(-2, 0);
        st.ctx.lineTo(-4, -3.2);
        st.ctx.closePath();
        st.ctx.fill();
        st.ctx.restore();
      }
      if (mouse.active) {
        st.ctx.strokeStyle = 'rgba(125,211,252,0.5)';
        st.ctx.beginPath(); st.ctx.arc(mouse.x, mouse.y, 22, 0, TAU); st.ctx.stroke();
        label(st.ctx, T('attraction'), mouse.x + 28, mouse.y, C.sky, 9);
      }
      setReadout({
        n: agents.length,
        align: (avg / 92 * 100).toFixed(0) + '%',
        spread: (Math.max(maxX - minX, maxY - minY) / Math.max(st.w, 1) * 100).toFixed(0) + '%'
      });
    });
    handle.reset = () => {
      for (const b of agents) {
        b.x = rnd() * st.w; b.y = rnd() * st.h;
        b.vx = (rnd() - 0.5) * 80; b.vy = (rnd() - 0.5) * 80;
      }
    };
    return handle;
  };

  /* ============================================================
     3. Procedural terrain (top-down hillshade)
     ============================================================ */
  DEMOS.terrain = function (el) {
    const st = makeStage(el);
    const params = { octaves: 6, sea: 0.42, seed: 1337 };
    let bitmap = null;
    let bw = 0, bh = 0;
    let builtW = 0;
    const setReadout = readout(st.readout, [['land', T('land')], ['peak', T('peak')], ['seed', T('seed')]]);

    function hash2(x, y, seed) {
      let h = Math.imul(x | 0, 374761393) ^ Math.imul(y | 0, 668265263) ^ Math.imul(seed | 0, 1442695041);
      h = Math.imul(h ^ (h >>> 13), 1274126177);
      return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
    }
    function vnoise(x, y, seed) {
      const xi = Math.floor(x), yi = Math.floor(y);
      const xf = x - xi, yf = y - yi;
      const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
      const a = hash2(xi, yi, seed), b = hash2(xi + 1, yi, seed);
      const c = hash2(xi, yi + 1, seed), d = hash2(xi + 1, yi + 1, seed);
      return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v;
    }
    function fbm(x, y, oct, seed) {
      let sum = 0, amp = 1, norm = 0, f = 1;
      for (let i = 0; i < oct; i++) {
        sum += vnoise(x * f, y * f, seed + i * 97) * amp;
        norm += amp; amp *= 0.5; f *= 2;
      }
      return sum / norm;
    }

    function build() {
      bw = Math.max(80, Math.min(240, Math.round(st.w / 3)));
      bh = Math.max(70, Math.min(190, Math.round(st.h / 3)));
      const heights = new Float32Array(bw * bh);
      for (let y = 0; y < bh; y++) {
        for (let x = 0; x < bw; x++) {
          let h = fbm(x / bw * 4.2, y / bh * 4.2, params.octaves, params.seed);
          const warp = fbm(x / bw * 2.1 + 5, y / bh * 2.1 + 9, 3, params.seed + 31);
          h = h * 0.76 + warp * 0.24;
          // contrast: stretch the narrow fBm distribution
          h = Math.min(1, Math.max(0, (h - 0.5) * 2.5 + 0.5));
          // a soft terrace near the shore
          h = h < 0.45 ? h * 0.94 : h;
          heights[y * bw + x] = h;
        }
      }
      bitmap = document.createElement('canvas');
      bitmap.width = bw; bitmap.height = bh;
      const bctx = bitmap.getContext('2d');
      const img = bctx.createImageData(bw, bh);
      const at = (x, y) => heights[Math.min(bh - 1, Math.max(0, y)) * bw + Math.min(bw - 1, Math.max(0, x))];
      // light direction: north-west
      const LX = -0.55, LY = -0.62, LZ = 0.56;
      const ll = Math.hypot(LX, LY, LZ);
      let land = 0, peak = 0;
      for (let y = 0; y < bh; y++) {
        for (let x = 0; x < bw; x++) {
          const i = y * bw + x;
          const h = heights[i];
          peak = Math.max(peak, h);
          const i4 = i * 4;
          if (h < params.sea) {
            const depth = Math.min(1, (params.sea - h) / Math.max(0.08, params.sea));
            img.data[i4] = 10 + (1 - depth) * 18;
            img.data[i4 + 1] = 26 + (1 - depth) * 44;
            img.data[i4 + 2] = 44 + (1 - depth) * 52;
            img.data[i4 + 3] = 255;
            continue;
          }
          land++;
          // the normal from the height map
          const dzdx = (at(x + 1, y) - at(x - 1, y)) * 26;
          const dzdy = (at(x, y + 1) - at(x, y - 1)) * 26;
          const nx = -dzdx, ny = -dzdy, nz = 1;
          const nlen = Math.hypot(nx, ny, nz);
          let shade = (nx * LX + ny * LY + nz * LZ) / (nlen * ll);
          shade = 0.55 + Math.max(0, shade) * 0.62;
          const hn = (h - params.sea) / Math.max(0.05, 1 - params.sea);
          let r, g, b;
          if (hn < 0.05) { r = 206; g = 192; b = 148; }               // beach
          else if (hn < 0.34) {                                       // meadow
            const t = (hn - 0.05) / 0.29;
            r = 92 + t * 24; g = 132 + t * 14; b = 70 + t * 8;
          } else if (hn < 0.62) {                                     // forest
            const t = (hn - 0.34) / 0.28;
            r = 74 + t * 26; g = 100 + t * 14; b = 62 + t * 20;
          } else if (hn < 0.84) {                                     // rocks
            const t = (hn - 0.62) / 0.22;
            r = 112 + t * 34; g = 110 + t * 32; b = 104 + t * 32;
          } else {                                                    // snow
            const t = Math.min(1, (hn - 0.84) / 0.16);
            r = 196 + t * 56; g = 205 + t * 48; b = 214 + t * 40;
          }
          img.data[i4] = Math.min(255, r * shade);
          img.data[i4 + 1] = Math.min(255, g * shade);
          img.data[i4 + 2] = Math.min(255, b * shade);
          img.data[i4 + 3] = 255;
        }
      }
      bctx.putImageData(img, 0, 0);
      builtW = st.w;
      setReadout({
        land: (land / (bw * bh) * 100).toFixed(0) + '%',
        peak: peak.toFixed(2),
        seed: String(params.seed)
      });
    }

    slider(st.controls, T('octaves'), 2, 8, params.octaves, 1, v => v, v => { params.octaves = v; build(); });
    slider(st.controls, T('sea_level'), 0.2, 0.62, params.sea, 0.01, v => v.toFixed(2), v => { params.sea = v; build(); });
    button(st.controls, T('new_seed'), () => {
      params.seed = Math.floor(Math.random() * 99999);
      build();
    });

    setTimeout(build, 0);
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!bitmap) return;
      if (!bitmap || Math.abs(st.w - builtW) > 24) build();
      st.ctx.save();
      st.ctx.imageSmoothingEnabled = true;
      st.ctx.drawImage(bitmap, 0, 0, st.w, st.h);
      st.ctx.restore();
      // sea contour
      label(st.ctx, 'hillshade · fBm · ' + params.octaves + T('octaves_unit'), 10, 13, 'rgba(255,255,255,0.5)', 9);
    });
    handle.reset = () => { params.seed = 1337; params.sea = 0.42; build(); };
    return handle;
  };

  /* ============================================================
     4. Water waves
     ============================================================ */
  DEMOS.waves = function (el) {
    const st = makeStage(el);
    const params = { amp: 1.0, wind: 1.0, chop: 1.0 };
    const setReadout = readout(st.readout, [['h', T('wave_height')], ['t', T('period')], ['e', T('energy')]]);
    slider(st.controls, T('amplitude'), 0.2, 2.2, params.amp, 0.05, v => v.toFixed(2) + '×', v => params.amp = v);
    slider(st.controls, T('wind'), 0.2, 2.4, params.wind, 0.05, v => v.toFixed(2) + '×', v => params.wind = v);
    slider(st.controls, T('steepness'), 0, 1, params.chop, 0.02, v => v.toFixed(2), v => params.chop = v);

    const waveDefs = [
      { k: 0.9, s: 0.55, a: 1.0 },
      { k: 1.7, s: 0.8, a: 0.55 },
      { k: 2.9, s: 1.15, a: 0.3 },
      { k: 4.7, s: 1.5, a: 0.16 }
    ];
    let time = 0;
    const handle = loop((dt) => {
      time += dt * params.wind;
      const ctx = st.ctx;
      clear(st, '#07080b');
      const horizon = st.h * 0.42;

      // sky
      const sky = ctx.createLinearGradient(0, 0, 0, horizon);
      sky.addColorStop(0, '#0a1220');
      sky.addColorStop(0.7, '#122234');
      sky.addColorStop(1, '#203a45');
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, st.w, horizon);

      // sun
      const sunX = st.w * 0.76, sunY = horizon - 34;
      const sunGrad = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, 58);
      sunGrad.addColorStop(0, 'rgba(255,241,196,0.98)');
      sunGrad.addColorStop(0.22, 'rgba(251,191,107,0.5)');
      sunGrad.addColorStop(1, 'rgba(251,191,107,0)');
      ctx.fillStyle = sunGrad;
      ctx.beginPath(); ctx.arc(sunX, sunY, 58, 0, TAU); ctx.fill();
      ctx.fillStyle = '#fff4d6';
      ctx.beginPath(); ctx.arc(sunX, sunY, 8, 0, TAU); ctx.fill();

      // clouds
      ctx.fillStyle = 'rgba(160,190,210,0.09)';
      for (let i = 0; i < 5; i++) {
        const cw = 90 + i * 22;
        const cx2 = ((i * 173 + time * 9) % (st.w + 240)) - 120;
        ctx.beginPath();
        ctx.ellipse(cx2, horizon - 44 - i * 9, cw, 7 + i * 1.4, 0, 0, TAU);
        ctx.fill();
      }

      // far band
      ctx.fillStyle = 'rgba(52,104,116,0.72)';
      ctx.fillRect(0, horizon - 2, st.w, 4);

      function surface(baseY, scale, speed) {
        const pts = [];
        for (let x = 0; x <= st.w + 8; x += 5) {
          let y = 0;
          for (const w of waveDefs) {
            const k = w.k / scale;
            y += Math.sin(x * k * 0.021 + time * w.s * speed) * (w.a * 9 * params.amp * scale)
              + Math.cos(x * k * 0.012 - time * w.s * 0.7 * speed) * (w.a * 4.5 * params.amp * scale)
              + Math.sin(x * k * 0.041 + time * w.s * 1.4 * speed) * (w.a * 2.6 * params.amp * scale * params.chop);
          }
          pts.push([x, baseY + y * 0.55]);
        }
        return pts;
      }

      // mid sea (hazy horizon water)
      const farPts = surface(horizon + 6, 0.5, 0.7);
      const farGrad = ctx.createLinearGradient(0, horizon, 0, st.h * 0.82);
      farGrad.addColorStop(0, '#2b6474');
      farGrad.addColorStop(0.55, '#184955');
      farGrad.addColorStop(1, '#0e2f3a');
      ctx.fillStyle = farGrad;
      ctx.beginPath();
      ctx.moveTo(0, horizon - 6);
      farPts.forEach(([x, y]) => ctx.lineTo(x, Math.max(y, horizon - 5)));
      ctx.lineTo(st.w, horizon - 6);
      ctx.lineTo(st.w, st.h);
      ctx.lineTo(0, st.h);
      ctx.closePath();
      ctx.fill();

      // haze on the horizon line
      const haze = ctx.createLinearGradient(0, horizon - 10, 0, horizon + 16);
      haze.addColorStop(0, 'rgba(120,160,180,0)');
      haze.addColorStop(0.5, 'rgba(120,160,180,0.16)');
      haze.addColorStop(1, 'rgba(120,160,180,0)');
      ctx.fillStyle = haze;
      ctx.fillRect(0, horizon - 10, st.w, 26);

      const nearPts = surface(st.h * 0.72, 1.15, 1.0);
      const water = ctx.createLinearGradient(0, st.h * 0.55, 0, st.h);
      water.addColorStop(0, '#123f4a');
      water.addColorStop(0.55, '#0b2a33');
      water.addColorStop(1, '#06161c');
      ctx.fillStyle = water;
      ctx.beginPath();
      ctx.moveTo(0, st.h);
      nearPts.forEach(([x, y]) => ctx.lineTo(x, y));
      ctx.lineTo(st.w, st.h);
      ctx.closePath();
      ctx.fill();

      // crest lines + glints
      ctx.strokeStyle = 'rgba(110,231,183,0.28)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      nearPts.forEach(([x, y], i) => { if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
      ctx.stroke();

      for (let i = 0; i < nearPts.length; i += 7) {
        const [x, y] = nearPts[i];
        const d = Math.abs(x - sunX) / st.w;
        if (d > 0.45) continue;
        const a = (1 - d * 2) * (0.25 + 0.2 * Math.sin(time * 2 + i));
        ctx.fillStyle = 'rgba(251,191,107,' + Math.max(0, a) + ')';
        ctx.fillRect(x, y + 2, 3, 1);
      }

      // spray
      ctx.fillStyle = 'rgba(255,255,255,0.5)';
      for (let i = 0; i < 34; i++) {
        const a = (time * 0.4 + i * 0.618) % 1;
        const x = (i * 97.3) % st.w;
        const y = horizon + a * (st.h - horizon);
        ctx.globalAlpha = (1 - a) * 0.5;
        ctx.fillRect(x, y, 1.4, 1.4);
      }
      ctx.globalAlpha = 1;

      label(ctx, 'FFT / Gerstner', 10, 13, 'rgba(255,255,255,0.45)', 9);
      setReadout({
        h: (params.amp * 1.9).toFixed(1) + T('m_unit'),
        t: (2.4 / params.wind).toFixed(1) + T('s_unit'),
        e: (params.amp * params.amp * params.wind * 30).toFixed(0) + T('kw_unit')
      });
    });
    handle.reset = () => { time = 0; };
    return handle;
  };

  /* ============================================================
     5. Lockstep determinism
     ============================================================ */
  DEMOS.lockstep = function (el) {
    const st = makeStage(el);
    const clients = [
      { name: 'A', lat: 40, color: C.acid },
      { name: 'B', lat: 120, color: C.sky },
      { name: 'C', lat: 210, color: C.violet }
    ];
    const params = { float: false };
    const TICK = 1 / 20;
    let simTick = 0;
    let acc = 0;
    let elapsed = 0;
    let waiting = '';
    let hashes = clients.map(() => 0);
    let cells = [];
    let desync = false;
    const setReadout = readout(st.readout, [
      ['tick', T('tick')], ['safe', T('safe_tick')], ['hash', T('hashes')], ['status', T('status')]
    ]);

    slider(st.controls, T('lag_a'), 0, 300, clients[0].lat, 5, v => v + T('ms_unit_ms'), v => clients[0].lat = v);
    slider(st.controls, T('lag_b'), 0, 300, clients[1].lat, 5, v => v + T('ms_unit_ms'), v => clients[1].lat = v);
    slider(st.controls, T('lag_c'), 0, 300, clients[2].lat, 5, v => v + T('ms_unit_ms'), v => clients[2].lat = v);
    toggle(st.controls, T('float_drift'), false, v => { params.float = v; cells = []; simTick = 0; acc = 0; });

    let drift = clients.map((c, i) => (i + 1) * 1e-6);

    function reset() {
      simTick = 0; acc = 0; elapsed = 0; cells = []; desync = false;
      hashes = clients.map(() => 0);
    }

    function stepClient(i) {
      // every client has the same tick and the same PRNG, so the states match
      let h = hashes[i] >>> 0;
      if (params.float) {
        const f = Math.sin(simTick * 0.137 + i * drift[i]) * 1e6;
        h = (h ^ ((f | 0) >>> 0)) >>> 0;
      } else {
        h = (Math.imul(h ^ simTick, 16777619) >>> 0);
      }
      hashes[i] = h >>> 0;
      return true;
    }

    const handle = loop((dt) => {
      elapsed += dt;
      const lags = clients.map(c => Math.round(c.lat / 1000 / TICK));
      const maxLag = Math.max(...lags);
      const safeTick = Math.max(0, Math.floor(elapsed / TICK) - maxLag);
      let advanced = 0;
      while (simTick < safeTick && advanced < 4) {
        simTick++;
        const row = [];
        for (let i = 0; i < clients.length; i++) row.push(stepClient(i));
        cells.push({ tick: simTick, ok: row.every(Boolean) });
        if (cells.length > 46) cells.shift();
        advanced++;
      }
      const laggingIdx = lags.indexOf(maxLag);
      waiting = maxLag > 0 ? clients[laggingIdx].name : '';
      acc = simTick;

      clear(st, '#07080b');
      grid(st, 44);
      const maxLagNow = Math.max(...clients.map(c => Math.round(c.lat / 1000 / TICK)));

      const laneH = Math.min(48, (st.h - 52) / clients.length);
      const top = 36;
      const cellW = 9;

      clients.forEach((c, i) => {
        const y = top + i * laneH;
        st.ctx.fillStyle = c.color;
        st.ctx.globalAlpha = 0.9;
        st.ctx.fillRect(12, y + laneH / 2 - 1, 4, 2);
        st.ctx.globalAlpha = 1;
        label(st.ctx, c.name, 22, y + laneH / 2, c.color, 11);
        label(st.ctx, c.lat + T('ms_unit_ms'), 38, y + laneH / 2, C.dim, 9);

        const x0 = 92;
        cells.forEach((cell, k) => {
          if (!cell.ok) return;
          const x = x0 + k * cellW;
          st.ctx.fillStyle = c.color;
          st.ctx.globalAlpha = 0.22 + (k / cells.length) * 0.6;
          st.ctx.fillRect(x, y + 8, cellW - 2, laneH - 16);
        });
      });

      // safe tick marker
      const x0 = 92;
      const markerX = x0 + cells.length * cellW;
      st.ctx.strokeStyle = waiting ? C.rose : C.acid;
      st.ctx.setLineDash([3, 4]);
      st.ctx.beginPath();
      st.ctx.moveTo(markerX, 24);
      st.ctx.lineTo(markerX, st.h - 18);
      st.ctx.stroke();
      st.ctx.setLineDash([]);

      label(st.ctx, 'tick ' + simTick, 12, 16, C.ink, 10);
      label(st.ctx, waiting ? T('wait_client') + waiting + ' (' + maxLagNow + T('tick_dot') : T('all_sync'), 92, 16, waiting ? C.rose : C.mint, 10);

      const f1 = hashes[0].toString(16).padStart(8, '0');
      const f2 = hashes[1].toString(16).padStart(8, '0');
      const f3 = hashes[2].toString(16).padStart(8, '0');
      desync = params.float && !(f1 === f2 && f2 === f3);
      label(st.ctx, 'hash A ' + f1, 12, st.h - 14, C.dim, 9);
      label(st.ctx, 'B ' + f2 + '   C ' + f3, 110, st.h - 14, desync ? C.rose : C.dim, 9);

      setReadout({
        tick: simTick,
        safe: Math.max(0, simTick),
        hash: desync ? T('diverge') : T('match'),
        status: desync ? 'desync' : (waiting ? T('waiting') : 'lockstep')
      });
    });
    handle.reset = reset;
    return handle;
  };

  /* ============================================================
     6. Planetary systems
     ============================================================ */
  DEMOS.planets = function (el) {
    const st = makeStage(el);
    const params = { mass: 1.0, speed: 0.22 };
    const rnd = mulberry32(19);
    const planets = [
      { a: 0.55, e: 0.06, color: C.amber, name: 'I', size: 3.4, M0: 0 },
      { a: 0.92, e: 0.11, color: C.mint, name: 'II', size: 4.6, M0: 2.1 },
      { a: 1.55, e: 0.04, color: C.sky, name: 'III', size: 5.2, M0: 4.2 },
      { a: 2.4, e: 0.16, color: C.violet, name: 'IV', size: 6.8, M0: 1.2 }
    ];
    let age = 0;
    const setReadout = readout(st.readout, [['p1', T('periods')], ['hz', T('habitable')], ['years', T('epoch')]]);

    slider(st.controls, T('star_mass'), 0.4, 2.2, params.mass, 0.05, v => v.toFixed(2) + ' M☉', v => params.mass = v);
    slider(st.controls, T('speed'), 0, 1, params.speed, 0.02, v => v.toFixed(2) + '×', v => params.speed = v);

    function solveKepler(M, e) {
      let E = M;
      for (let i = 0; i < 5; i++) {
        E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
      }
      return E;
    }

    const handle = loop((dt) => {
      age += dt * params.speed;
      const ctx = st.ctx;
      clear(st, '#07080b');

      const cx = st.w * 0.5, cy = st.h * 0.55;
      const maxA = 2.55;
      const scale = Math.min(st.w * 0.42, st.h * 0.46) / maxA;

      // starfield
      const srnd = mulberry32(3);
      for (let i = 0; i < 70; i++) {
        const x = srnd() * st.w, y = srnd() * st.h;
        ctx.fillStyle = 'rgba(255,255,255,' + (0.1 + srnd() * 0.4) + ')';
        ctx.fillRect(x, y, 1, 1);
      }

      // habitable zone
      const hzIn = Math.sqrt(0.95 / params.mass) * 1.0;
      const hzOut = Math.sqrt(1.37 / params.mass) * 1.0;
      ctx.fillStyle = 'rgba(110,231,183,0.07)';
      ctx.beginPath();
      ctx.arc(cx, cy, hzOut * scale, 0, TAU);
      ctx.arc(cx, cy, hzIn * scale, 0, TAU, true);
      ctx.fill();

      // orbits + planets
      planets.forEach((p) => {
        const period = Math.sqrt(p.a * p.a * p.a / params.mass);
        const M = p.M0 + TAU * (age / period);
        const E = solveKepler(M, p.e);
        const x = p.a * (Math.cos(E) - p.e);
        const y = p.a * Math.sqrt(1 - p.e * p.e) * Math.sin(E);
        const sx = cx + x * scale, sy = cy + y * scale;

        ctx.strokeStyle = 'rgba(255,255,255,0.12)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.ellipse(cx - p.a * p.e * scale, cy, p.a * scale, p.a * Math.sqrt(1 - p.e * p.e) * scale, 0, 0, TAU);
        ctx.stroke();

        // trail
        ctx.globalAlpha = 0.18;
        ctx.fillStyle = p.color;
        for (let k = 1; k < 12; k++) {
          const Mk = M - k * 0.09;
          const Ek = solveKepler(Mk, p.e);
          const tx = cx + (p.a * (Math.cos(Ek) - p.e)) * scale;
          const ty = cy + (p.a * Math.sqrt(1 - p.e * p.e) * Math.sin(Ek)) * scale;
          ctx.beginPath(); ctx.arc(tx, ty, p.size * (1 - k / 14), 0, TAU); ctx.fill();
        }
        ctx.globalAlpha = 1;

        const glow = ctx.createRadialGradient(sx, sy, 0, sx, sy, p.size * 4);
        glow.addColorStop(0, p.color);
        glow.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = glow;
        ctx.beginPath(); ctx.arc(sx, sy, p.size * 4, 0, TAU); ctx.fill();
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(sx, sy, p.size, 0, TAU); ctx.fill();
        label(ctx, p.name, sx + p.size + 6, sy, 'rgba(255,255,255,0.5)', 9);
      });

      // star
      const starGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, 60);
      starGlow.addColorStop(0, 'rgba(255,240,180,1)');
      starGlow.addColorStop(0.15, 'rgba(251,191,107,0.8)');
      starGlow.addColorStop(1, 'rgba(251,191,107,0)');
      ctx.fillStyle = starGlow;
      ctx.beginPath(); ctx.arc(cx, cy, 60, 0, TAU); ctx.fill();
      ctx.fillStyle = '#fff6d6';
      ctx.beginPath(); ctx.arc(cx, cy, 7 * Math.min(1.6, Math.sqrt(params.mass)), 0, TAU); ctx.fill();

      const periods = planets.map(p => Math.sqrt(p.a ** 3 / params.mass).toFixed(2)).join(' · ');
      setReadout({
        p1: periods + T('years'),
        hz: hzIn.toFixed(2) + '–' + hzOut.toFixed(2) + T('au'),
        years: age.toFixed(1)
      });
    });
    handle.reset = () => { age = 0; };
    return handle;
  };

  /* ============================================================
     7. Balanced strategy maps
     ============================================================ */
  DEMOS.maps = function (el) {
    const st = makeStage(el);
    const params = { sea: 0.44, seed: 2026 };
    const N = 21;
    let grid = [];
    let stats = { fair: '—', conn: '—', res: '0' };
    const setReadout = readout(st.readout, [['fair', T('balance')], ['conn', T('connectivity')], ['res', T('resources')]]);

    function generate() {
      const rnd = mulberry32(params.seed);
      const half = [];
      for (let y = 0; y < N; y++) {
        for (let x = 0; x < Math.ceil(N / 2); x++) {
          let v = 0;
          const n = rnd();
          if (n > params.sea) v = 1;
          if (rnd() > 0.86) v = 2;
          half[y * Math.ceil(N / 2) + x] = v;
        }
      }
      grid = [];
      for (let y = 0; y < N; y++) {
        const row = [];
        for (let x = 0; x < N; x++) {
          const hx = Math.min(x, N - 1 - x);
          const hy = y;
          row.push(half[hy * Math.ceil(N / 2) + hx]);
        }
        grid.push(row);
      }
      // point symmetry (180°)
      for (let y = 0; y < N; y++) {
        for (let x = 0; x < N; x++) {
          grid[y][x] = grid[N - 1 - y][N - 1 - x] = grid[y][x];
        }
      }
      const bases = [[3, 3], [N - 4, N - 4]];
      bases.forEach(([bx, by]) => { grid[by][bx] = 3; });
      // resources mirrored
      const r2 = mulberry32(params.seed + 77);
      for (let i = 0; i < 10; i++) {
        const x = 1 + Math.floor(r2() * Math.floor(N / 2) - 1);
        const y = 1 + Math.floor(r2() * (N - 2));
        const xx = Math.max(1, Math.min(N - 2, x));
        grid[y][xx] = 4;
        grid[N - 1 - y][N - 1 - xx] = 4;
      }
      // ensure bases are land
      bases.forEach(([bx, by]) => { grid[by][bx] = 1; });
      evaluate();
    }

    function evaluate() {
      const bases = [[3, 3], [N - 4, N - 4]];
      const scores = [];
      let totalReach = 0, resources = 0;
      for (let y = 0; y < N; y++) {
        for (let x = 0; x < N; x++) if (grid[y][x] === 4) resources++;
      }
      bases.forEach(([bx, by]) => {
        const dist = Array.from({ length: N }, () => new Array(N).fill(-1));
        const q = [[bx, by]];
        dist[by][bx] = 0;
        let reach = 0, resDist = [];
        while (q.length) {
          const [x, y] = q.shift();
          reach++;
          for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const nx = x + dx, ny = y + dy;
            if (nx < 0 || ny < 0 || nx >= N || ny >= N) continue;
            if (grid[ny][nx] === 0 || dist[ny][nx] !== -1) continue;
            dist[ny][nx] = dist[y][x] + 1;
            q.push([nx, ny]);
          }
        }
        for (let y = 0; y < N; y++) {
          for (let x = 0; x < N; x++) {
            if (grid[y][x] === 4 && dist[y][x] >= 0) resDist.push(dist[y][x]);
          }
        }
        resDist.sort((a, b) => a - b);
        const score = resDist.slice(0, 5).reduce((a, b) => a + b, 0) / Math.max(1, Math.min(5, resDist.length));
        scores.push(score);
        totalReach += reach;
      });
      const land = grid.flat().filter(v => v !== 0).length;
      stats = {
        fair: (Math.abs(scores[0] - scores[1]) / Math.max(1, (scores[0] + scores[1]) / 2) * 100).toFixed(1) + '%',
        conn: (totalReach / 2 / land * 100).toFixed(0) + '%',
        res: String(resources)
      };
      setReadout(stats);
    }

    slider(st.controls, T('water_level'), 0.2, 0.62, params.sea, 0.01, v => v.toFixed(2), v => { params.sea = v; generate(); });
    button(st.controls, T('new_map'), () => { params.seed = Math.floor(Math.random() * 9999); generate(); });

    setTimeout(generate, 0);

    const colors = { 0: '#0a1a24', 1: '#274a2c', 2: '#4a5240', 4: '#c8f751' };
    const handle = loop(() => {
      clear(st, '#07080b');
      if (!grid.length) return;
      const pad = 14;
      const size = Math.min((st.w - pad * 2) / N, (st.h - pad * 2) / N);
      const ox = (st.w - size * N) / 2, oy = (st.h - size * N) / 2;

      for (let y = 0; y < N; y++) {
        for (let x = 0; x < N; x++) {
          const v = grid[y][x];
          st.ctx.fillStyle = colors[v] || '#333';
          if (v === 3) st.ctx.fillStyle = '#e7eddf';
          st.ctx.fillRect(ox + x * size, oy + y * size, size - 0.6, size - 0.6);
          if (v === 4) {
            st.ctx.fillStyle = '#101404';
            st.ctx.beginPath();
            st.ctx.arc(ox + (x + 0.5) * size, oy + (y + 0.5) * size, size * 0.22, 0, TAU);
            st.ctx.fill();
          }
        }
      }
      // bases
      [[3, 3], [N - 4, N - 4]].forEach(([x, y], i) => {
        const bx = ox + (x + 0.5) * size, by = oy + (y + 0.5) * size;
        st.ctx.fillStyle = i === 0 ? C.sky : C.rose;
        st.ctx.beginPath();
        st.ctx.moveTo(bx, by - size * 0.62);
        st.ctx.lineTo(bx + size * 0.62, by);
        st.ctx.lineTo(bx, by + size * 0.62);
        st.ctx.lineTo(bx - size * 0.62, by);
        st.ctx.closePath();
        st.ctx.fill();
        st.ctx.fillStyle = '#07080b';
        st.ctx.beginPath(); st.ctx.arc(bx, by, size * 0.2, 0, TAU); st.ctx.fill();
      });
      label(st.ctx, T('symmetry'), 10, 11, C.dim, 9);
      setReadout(stats);
    });
    handle.reset = () => { params.seed = 2026; params.sea = 0.44; generate(); };
    return handle;
  };

  /* ============================================================
     8. Ecosystem (Lotka–Volterra)
     ============================================================ */
  DEMOS.ecosystem = function (el) {
    const st = makeStage(el);
    const params = { alpha: 0.9, beta: 0.15, gamma: 0.6, delta: 0.04 };
    let prey = 22, pred = 4.5, K = 160, t = 0;
    let hist = [];
    const setReadout = readout(st.readout, [['prey', T('prey')], ['pred', T('predators')], ['phase', T('phase')]]);

    slider(st.controls, T('birth'), 0.5, 1.6, params.alpha, 0.02, v => v.toFixed(2), v => params.alpha = v);
    slider(st.controls, T('efficiency'), 0.05, 0.35, params.beta, 0.01, v => v.toFixed(2), v => params.beta = v);
    slider(st.controls, T('death'), 0.3, 1.2, params.gamma, 0.02, v => v.toFixed(2), v => params.gamma = v);

    function deriv(p, q) {
      return [params.alpha * p * (1 - p / K) - params.beta * p * q,
              params.delta * p * q - params.gamma * q];
    }
    function step(h) {
      const a = deriv(prey, pred);
      const b = deriv(prey + h / 2 * a[0], pred + h / 2 * a[1]);
      const c = deriv(prey + h / 2 * b[0], pred + h / 2 * b[1]);
      const d = deriv(prey + h * c[0], pred + h * c[1]);
      prey = Math.max(0, prey + h / 6 * (a[0] + 2 * b[0] + 2 * c[0] + d[0]));
      pred = Math.max(0, pred + h / 6 * (a[1] + 2 * b[1] + 2 * c[1] + d[1]));
      t += h;
    }

    const handle = loop((dt) => {
      const adv = Math.min(dt, 0.05) * 5.5;
      const sub = 8;
      for (let i = 0; i < sub; i++) step(adv / sub);
      hist.push({ prey, pred });
      if (hist.length > 260) hist.shift();

      clear(st, '#07080b');
      grid(st, 40);

      const padL = 34, padB = 20, padT = 18;
      const plotW = st.w - padL - 12, plotH = st.h - padT - padB;
      const maxV = Math.max(24, ...hist.map(h => Math.max(h.prey, h.pred))) * 1.08;

      // axes
      st.ctx.strokeStyle = 'rgba(255,255,255,0.16)';
      st.ctx.beginPath();
      st.ctx.moveTo(padL, padT);
      st.ctx.lineTo(padL, st.h - padB);
      st.ctx.lineTo(st.w - 8, st.h - padB);
      st.ctx.stroke();
      label(st.ctx, String(Math.round(maxV)), padL - 6, padT + 4, C.dim, 8, 'right');
      label(st.ctx, '0', padL - 6, st.h - padB, C.dim, 8, 'right');

      const plot = (key, color) => {
        st.ctx.strokeStyle = color;
        st.ctx.lineWidth = 1.6;
        st.ctx.beginPath();
        hist.forEach((h, i) => {
          const x = padL + (i / Math.max(1, hist.length - 1)) * plotW;
          const y = st.h - padB - (h[key] / maxV) * plotH;
          if (i === 0) st.ctx.moveTo(x, y); else st.ctx.lineTo(x, y);
        });
        st.ctx.stroke();
      };
      plot('prey', C.mint);
      plot('pred', C.rose);

      const lx = st.w - 132;
      st.ctx.fillStyle = C.mint; st.ctx.fillRect(lx, 10, 8, 3);
      label(st.ctx, T('prey'), lx + 13, 12, C.dim, 9);
      st.ctx.fillStyle = C.rose; st.ctx.fillRect(lx + 62, 10, 8, 3);
      label(st.ctx, T('predators'), lx + 75, 12, C.dim, 9);

      if (prey < 0.6) label(st.ctx, T('prey_extinct'), st.w / 2, st.h / 2, C.rose, 12, 'center');
      if (pred < 0.6) label(st.ctx, T('predators_extinct'), st.w / 2, st.h / 2 + 16, C.rose, 12, 'center');

      setReadout({
        prey: prey.toFixed(1),
        pred: pred.toFixed(1),
        phase: t.toFixed(1) + ' t'
      });
    });
    handle.reset = () => { prey = 28; pred = 7; hist = []; t = 0; };
    return handle;
  };
})();
