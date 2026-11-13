/* ============================================================
   Interactive demos: Part III — networking and MMO infrastructure
   Transport, reliability, topology, NAT, synchronization, AOI and scale.
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
     1. Transport: UDP vs TCP vs QUIC under loss
     ============================================================ */
  DEMOS.transport = function (el) {
    const st = makeStage(el);
    const p = { mode: 'udp', loss: 4, rtt: 120 };
    let packets = [], spawn = 0, blocked = [0, 0, 0], sent = 0, lost = 0, stalls = 0, now = 0;
    const setReadout = readout(st.readout, [
      ['mode', T('mode')], ['delivered', T('delivered')], ['stall', T('stalls')]
    ]);
    function reset() { packets = []; sent = 0; lost = 0; stalls = 0; blocked = [0, 0, 0]; }
    function push() {
      const stream = Math.floor(Math.random() * 3);
      const bad = Math.random() * 100 < p.loss;
      packets.push({ x: 0, stream, bad, id: sent++, dead: false });
    }
    segmented(st.controls, [
      ['udp', 'UDP'], ['tcp', 'TCP'], ['quic', 'QUIC']
    ], 'udp', (id) => { p.mode = id; reset(); });
    slider(st.controls, T('loss'), 0, 15, p.loss, 1, v => v + '%', v => { p.loss = v; reset(); });
    button(st.controls, T('reset'), reset);

    setTimeout(push, 0);
    const handle = loop((dt) => {
      now += dt;
      spawn += dt;
      if (spawn > 0.14) { spawn = 0; push(); }
      const speed = 0.42 + 120 / Math.max(40, p.rtt);
      packets.forEach((q) => {
        if (q.dead) return;
        const blockedNow = blocked[q.stream] > now;
        if (!blockedNow) q.x += dt * speed;
        if (q.x > 0.78 && q.bad && !q.handled) {
          q.handled = true;
          if (p.mode === 'udp') { q.dead = true; lost++; }
          else if (p.mode === 'quic') { q.dead = true; lost++; blocked[q.stream] = now + 0.25; stalls++; }
          else { blocked[q.stream] = now + 0.45; stalls++; q.bad = false; q.handled = false; }
        }
        if (q.x >= 1) q.dead = true;
      });
      packets = packets.filter((q) => !q.dead).slice(-90);
      clear(st, '#07080b');
      const laneH = (st.h - 46) / 3;
      for (let s = 0; s < 3; s++) {
        const y = 26 + s * laneH;
        st.ctx.fillStyle = 'rgba(255,255,255,0.035)';
        st.ctx.fillRect(36, y + laneH / 2 - 12, st.w - 72, 24);
        label(st.ctx, T('stream') + ' ' + (s + 1), 8, y + laneH / 2, 'rgba(255,255,255,0.4)', 8);
        const blockedNow = blocked[s] > now;
        if (blockedNow) {
          st.ctx.fillStyle = 'rgba(253,164,175,0.18)';
          st.ctx.fillRect(36, y + laneH / 2 - 12, st.w - 72, 24);
        }
      }
      packets.forEach((q) => {
        const y = 26 + q.stream * laneH + laneH / 2;
        const x = 36 + q.x * (st.w - 72);
        st.ctx.fillStyle = q.bad ? 'rgba(253,164,175,0.9)' : 'rgba(125,211,252,0.9)';
        st.ctx.beginPath();
        st.ctx.arc(x, y, q.bad ? 4 : 3, 0, TAU);
        st.ctx.fill();
      });
      const total = Math.max(1, sent);
      setReadout({
        mode: p.mode === 'udp' ? 'UDP' : p.mode === 'tcp' ? 'TCP' : 'QUIC',
        delivered: Math.round(100 * (sent - lost) / total) + '%',
        stall: String(stalls)
      });
      label(st.ctx, T('transport_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = reset;
    return handle;
  };

  /* ============================================================
     2. Reliable channel: window, ACK, RTO
     ============================================================ */
  DEMOS.reliability = function (el) {
    const st = makeStage(el);
    const p = { loss: 8, rtt: 100, window: 16 };
    let pk = [], next = 0, now = 0, retrans = 0;
    const setReadout = readout(st.readout, [
      ['inflight', T('inflight')], ['retrans', T('retrans')], ['rto', T('rto')]
    ]);
    function mk(id) { return { id, state: 'wait', born: 0, lost: Math.random() * 100 < p.loss }; }
    function reset() { pk = []; next = 0; retrans = 0; }
    segmented(st.controls, [
      ['16', '16'], ['32', '32'], ['64', '64']
    ], '16', (id) => { p.window = +id; reset(); });
    slider(st.controls, T('loss'), 0, 20, p.loss, 1, v => v + '%', v => { p.loss = v; reset(); });
    slider(st.controls, T('rtt'), 20, 300, p.rtt, 10, v => v + ' ms', v => { p.rtt = v; reset(); });

    setTimeout(reset, 0);
    const handle = loop((dt) => {
      now += dt;
      while (next < 32 && pk.length < p.window) pk.push(mk(next++));
      const rto = Math.max(0.08, (p.rtt / 1000) * 1.6);
      pk.forEach((q) => {
        if (q.state === 'wait') { q.state = 'sent'; q.born = now; }
        else if (q.state === 'sent') {
          if (!q.lost && now - q.born > p.rtt / 1000) q.state = 'ack';
          else if (q.lost && now - q.born > rto) { q.state = 'wait'; q.lost = false; q.born = now; retrans++; }
        } else if (q.state === 'ack' && now - q.born > p.rtt / 1000 + 0.3) {
          q.state = 'done';
        }
      });
      pk = pk.filter((q) => q.state !== 'done').slice(-64);
      clear(st, '#07080b');
      const cols = 8, size = Math.min(22, (st.w - 40) / cols), top = 34;
      for (let i = 0; i < 32; i++) {
        const q = pk.find((x) => x.id === i);
        const x = 20 + (i % cols) * size, y = top + Math.floor(i / cols) * size;
        let col = 'rgba(255,255,255,0.08)';
        if (q) col = q.state === 'ack' ? 'rgba(200,247,81,0.8)'
          : q.state === 'wait' ? 'rgba(251,191,107,0.75)' : 'rgba(125,211,252,0.8)';
        st.ctx.fillStyle = col;
        st.ctx.fillRect(x, y, size - 3, size - 3);
      }
      label(st.ctx, T('reliability_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
      const inflight = pk.filter((q) => q.state === 'sent').length;
      setReadout({
        inflight: String(inflight),
        retrans: String(retrans),
        rto: Math.round(Math.max(80, p.rtt * 1.6)) + ' ms'
      });
    });
    handle.reset = reset;
    return handle;
  };

  /* ============================================================
     3. Topology: dedicated / listen / P2P / relay
     ============================================================ */
  DEMOS.topology = function (el) {
    const st = makeStage(el);
    const p = { mode: 'dedicated' };
    let dots = [], t = 0;
    const setReadout = readout(st.readout, [
      ['authority', T('authority')], ['links', T('links')], ['host', T('host_adv')]
    ]);
    function nodes() {
      const cx = st.w / 2, cy = st.h / 2;
      if (p.mode === 'p2p') {
        return [0, 1, 2, 3].map((i) => ({
          x: cx + Math.cos(i / 4 * TAU) * Math.min(st.w, st.h) * 0.3,
          y: cy + Math.sin(i / 4 * TAU) * Math.min(st.w, st.h) * 0.3
        }));
      }
      const ring = [0, 1, 2, 3].map((i) => ({
        x: cx + Math.cos(i / 4 * TAU - Math.PI / 2) * Math.min(st.w, st.h) * 0.3,
        y: cy + Math.sin(i / 4 * TAU - Math.PI / 2) * Math.min(st.w, st.h) * 0.3
      }));
      ring.push({ x: cx, y: cy, server: true, relay: p.mode === 'relay', host: p.mode === 'listen' });
      return ring;
    }
    function fire() {
      const ns = nodes();
      const src = Math.floor(Math.random() * 4);
      const dst = p.mode === 'p2p' ? (src + 1 + Math.floor(Math.random() * 3)) % 4 : 4;
      dots.push({ src, dst, t: 0, via: p.mode === 'relay' ? 4 : null });
    }
    segmented(st.controls, [
      ['dedicated', T('dedicated')], ['listen', T('listen')],
      ['p2p', 'P2P'], ['relay', T('relay')]
    ], 'dedicated', (id) => { p.mode = id; dots = []; });
    button(st.controls, T('send'), fire);

    setTimeout(fire, 0);
    const handle = loop((dt) => {
      t += dt;
      if (t > 0.7) { t = 0; fire(); }
      const ns = nodes();
      clear(st, '#07080b');
      const links = [];
      if (p.mode === 'p2p') {
        for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) links.push([i, j]);
      } else if (p.mode === 'relay') {
        for (let i = 0; i < 4; i++) { links.push([i, 4]); links.push([i, 4]); }
      } else {
        for (let i = 0; i < 4; i++) links.push([i, 4]);
      }
      st.ctx.strokeStyle = 'rgba(255,255,255,0.12)';
      st.ctx.lineWidth = 1;
      links.forEach(([a, b]) => {
        st.ctx.beginPath(); st.ctx.moveTo(ns[a].x, ns[a].y); st.ctx.lineTo(ns[b].x, ns[b].y); st.ctx.stroke();
      });
      dots.forEach((d) => {
        d.t += dt * 1.4;
        const a = ns[d.src], b = ns[d.dst];
        const x = a.x + (b.x - a.x) * Math.min(1, d.t);
        const y = a.y + (b.y - a.y) * Math.min(1, d.t);
        st.ctx.fillStyle = 'rgba(200,247,81,0.9)';
        st.ctx.beginPath(); st.ctx.arc(x, y, 3, 0, TAU); st.ctx.fill();
      });
      dots = dots.filter((d) => d.t < 1).slice(-30);
      ns.forEach((n, i) => {
        st.ctx.fillStyle = n.server ? (n.relay ? 'rgba(196,181,253,0.9)' : 'rgba(253,164,175,0.9)')
          : 'rgba(125,211,252,0.85)';
        st.ctx.beginPath(); st.ctx.arc(n.x, n.y, n.server ? 10 : 6, 0, TAU); st.ctx.fill();
      });
      const aut = p.mode === 'p2p' ? T('peers') : p.mode === 'listen' ? T('host') : T('server');
      setReadout({
        authority: aut,
        links: String(p.mode === 'p2p' ? 6 : 4),
        host: p.mode === 'listen' ? '0 ms' : p.mode === 'p2p' ? '—' : '—'
      });
      label(st.ctx, T('topology_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = () => { dots = []; };
    return handle;
  };

  /* ============================================================
     4. NAT: hole punching and TURN fallback
     ============================================================ */
  DEMOS.nat = function (el) {
    const st = makeStage(el);
    const p = { symmetric: false };
    let phase = 0, t = 0, path = '—';
    const setReadout = readout(st.readout, [
      ['path', T('path')], ['direct', T('direct')], ['relay', T('relay_cost')]
    ]);
    toggle(st.controls, T('symmetric_nat'), false, (v) => { p.symmetric = v; t = 0; phase = 0; path = '—'; });
    button(st.controls, T('punch'), () => { t = 0; phase = 0; path = '—'; });

    const handle = loop((dt) => {
      t += dt;
      if (t > 0.9) { t = 0; phase = (phase + 1) % 4; }
      if (phase === 0) path = 'STUN';
      if (phase === 1) path = 'SIGNAL';
      if (phase === 2) path = p.symmetric ? 'BLOCKED' : 'PUNCH';
      if (phase === 3) path = p.symmetric ? 'RELAY' : 'DIRECT';
      clear(st, '#07080b');
      const W = st.w, H = st.h;
      const box = (x, y, w, h, c, title) => {
        st.ctx.fillStyle = c; st.ctx.fillRect(x, y, w, h);
        label(st.ctx, title, x + w / 2, y + 12, 'rgba(255,255,255,0.7)', 8, 'center');
      };
      box(14, H / 2 - 40, 90, 80, 'rgba(125,211,252,0.12)', 'CLIENT A');
      box(W - 104, H / 2 - 40, 90, 80, 'rgba(125,211,252,0.12)', 'CLIENT B');
      box(W / 2 - 46, H / 2 - 30, 92, 60, p.symmetric ? 'rgba(253,164,175,0.16)' : 'rgba(200,247,81,0.12)',
        p.symmetric ? 'symmetric NAT' : 'cone NAT');
      // path lines
      st.ctx.strokeStyle = 'rgba(255,255,255,0.2)';
      st.ctx.beginPath(); st.ctx.moveTo(104, H / 2); st.ctx.lineTo(W / 2 - 46, H / 2);
      st.ctx.moveTo(W - 104, H / 2); st.ctx.lineTo(W / 2 + 46, H / 2); st.ctx.stroke();
      if (path === 'DIRECT') {
        st.ctx.strokeStyle = 'rgba(200,247,81,0.8)'; st.ctx.lineWidth = 2;
        st.ctx.beginPath(); st.ctx.moveTo(104, H / 2); st.ctx.lineTo(W - 104, H / 2); st.ctx.stroke();
        st.ctx.lineWidth = 1;
      }
      if (path === 'RELAY') {
        st.ctx.strokeStyle = 'rgba(251,191,107,0.8)'; st.ctx.lineWidth = 2;
        st.ctx.beginPath(); st.ctx.moveTo(104, H / 2); st.ctx.lineTo(W - 104, H / 2); st.ctx.stroke();
        st.ctx.lineWidth = 1;
      }
      const x = phase % 2 === 0 ? 104 : W - 104;
      st.ctx.fillStyle = 'rgba(255,255,255,0.9)';
      st.ctx.beginPath(); st.ctx.arc(W / 2, H / 2, 4, 0, TAU); st.ctx.fill();
      label(st.ctx, path, W / 2, H / 2 + 40, 'rgba(255,255,255,0.6)', 9, 'center');
      setReadout({
        path, direct: p.symmetric ? '0%' : '100%',
        relay: p.symmetric ? '+40 ms' : '0 ms'
      });
      label(st.ctx, T('nat_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = () => { p.symmetric = false; t = 0; phase = 0; path = '—'; };
    return handle;
  };

  /* ============================================================
     5. Rollback: predicted input vs late remote input
     ============================================================ */
  DEMOS.rollback = function (el) {
    const st = makeStage(el);
    const p = { rtt: 90, delay: 2 };
    let frame = 0, resims = 0, rollback = 0, hist = [], t = 0;
    const setReadout = readout(st.readout, [
      ['rollback', T('rollback')], ['resims', T('resims')], ['depth', T('depth')]
    ]);
    slider(st.controls, T('rtt'), 20, 250, p.rtt, 10, v => v + ' ms', v => { p.rtt = v; });
    slider(st.controls, T('input_delay'), 0, 4, p.delay, 1, v => v + 'f', v => { p.delay = v; });
    button(st.controls, T('reset'), () => { frame = 0; resims = 0; rollback = 0; hist = []; });

    const handle = loop((dt) => {
      t += dt;
      if (t < 0.06) { clear(st, '#07080b'); return; }
      t = 0;
      frame++;
      const remoteSeen = Math.max(0, frame - Math.round(p.rtt / 16.7) - p.delay);
      hist.push({ f: frame, seen: remoteSeen });
      if (hist.length > 12) hist.shift();
      const target = Math.max(0, frame - Math.round(p.rtt / 16.7));
      rollback = Math.min(8, Math.max(0, frame - target));
      if (rollback > 0 && frame % 12 === 0) resims += rollback;
      clear(st, '#07080b');
      const cw = Math.min(26, (st.w - 30) / 14);
      for (let i = 0; i < hist.length; i++) {
        const h = hist[i];
        const x = 14 + i * cw;
        const stale = h.f < target;
        st.ctx.fillStyle = stale ? 'rgba(253,164,175,0.35)' : 'rgba(125,211,252,0.35)';
        st.ctx.fillRect(x, 28, cw - 3, 70);
        label(st.ctx, String(h.f % 100), x + (cw - 3) / 2, 20, 'rgba(255,255,255,0.4)', 7, 'center');
      }
      st.ctx.strokeStyle = 'rgba(200,247,81,0.9)';
      st.ctx.beginPath();
      st.ctx.moveTo(14 + (hist.length - 1 - rollback) * cw, 26);
      st.ctx.lineTo(14 + (hist.length - 1 - rollback) * cw, 102);
      st.ctx.stroke();
      label(st.ctx, T('rollback_marker'), 14 + (hist.length - 1 - rollback) * cw + 4, 112,
        'rgba(200,247,81,0.9)', 8);
      setReadout({
        rollback: String(rollback),
        resims: String(resims),
        depth: p.delay + 'f'
      });
      label(st.ctx, T('rollback_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = () => { frame = 0; resims = 0; rollback = 0; hist = []; };
    return handle;
  };

  /* ============================================================
     6. Interpolation and jitter buffer
     ============================================================ */
  DEMOS.interp = function (el) {
    const st = makeStage(el);
    const p = { jitter: 35, delay: 0.14, extr: false };
    let snaps = [], now = 0, spawn = 0, trueX = 0.5;
    const setReadout = readout(st.readout, [
      ['delay', T('delay')], ['jitter', T('jitter')], ['error', T('error')]
    ]);
    function pos(t) { return 0.5 + 0.32 * Math.sin(t * 1.4); }
    slider(st.controls, T('jitter'), 0, 120, p.jitter, 5, v => v + ' ms', v => { p.jitter = v; });
    slider(st.controls, T('delay'), 40, 300, p.delay * 1000, 10, v => v + ' ms', v => { p.delay = v / 1000; });
    toggle(st.controls, T('extrapolate'), false, v => { p.extr = v; });
    button(st.controls, T('reset'), () => { snaps = []; now = 0; });

    const handle = loop((dt) => {
      now += dt;
      spawn += dt;
      const interval = 0.1 + (p.jitter / 1000) * (Math.random() - 0.5);
      if (spawn > Math.max(0.03, interval)) {
        spawn = 0;
        snaps.push({ t: now, x: pos(now) });
        if (snaps.length > 40) snaps.shift();
      }
      const tr = now - p.delay;
      let x = pos(tr), err = 0;
      if (snaps.length > 1) {
        let a = snaps[0], b = snaps[1];
        for (let i = 1; i < snaps.length; i++) {
          if (snaps[i].t >= tr) { a = snaps[i - 1]; b = snaps[i]; break; }
          a = snaps[i]; b = snaps[i];
        }
        const alpha = clamp((tr - a.t) / Math.max(1e-4, b.t - a.t), 0, 1);
        x = a.x + (b.x - a.x) * alpha;
        const last = snaps[snaps.length - 1];
        if (p.extr && tr > last.t) {
          const prev = snaps[Math.max(0, snaps.length - 2)];
          const slope = (last.x - prev.x) / Math.max(1e-3, last.t - prev.t);
          x = last.x + slope * (tr - last.t);
        }
        err = Math.abs(x - pos(tr));
      }
      clear(st, '#07080b');
      const y = st.h / 2;
      st.ctx.strokeStyle = 'rgba(255,255,255,0.15)';
      st.ctx.beginPath(); st.ctx.moveTo(20, y); st.ctx.lineTo(st.w - 20, y); st.ctx.stroke();
      snaps.forEach((s) => {
        st.ctx.fillStyle = 'rgba(255,255,255,0.28)';
        st.ctx.beginPath(); st.ctx.arc(20 + s.x * (st.w - 40), y - 30, 2, 0, TAU); st.ctx.fill();
      });
      st.ctx.fillStyle = 'rgba(253,164,175,0.8)';
      st.ctx.beginPath(); st.ctx.arc(20 + pos(now) * (st.w - 40), y + 28, 6, 0, TAU); st.ctx.fill();
      st.ctx.fillStyle = 'rgba(200,247,81,0.95)';
      st.ctx.beginPath(); st.ctx.arc(20 + x * (st.w - 40), y, 7, 0, TAU); st.ctx.fill();
      label(st.ctx, 'now', st.w - 18, y + 28, 'rgba(253,164,175,0.8)', 8, 'right');
      label(st.ctx, 'render', st.w - 18, y + 44, 'rgba(200,247,81,0.8)', 8, 'right');
      setReadout({
        delay: Math.round(p.delay * 1000) + ' ms',
        jitter: p.jitter + ' ms',
        error: (err * 100).toFixed(1) + '%'
      });
      label(st.ctx, T('interp_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = () => { snaps = []; now = 0; };
    return handle;
  };

  /* ============================================================
     7. Lag compensation: rewind window
     ============================================================ */
  DEMOS.lagcomp = function (el) {
    const st = makeStage(el);
    const p = { rtt: 80, rewind: true, range: 120 };
    let t = 0, shots = 0, hits = 0, flash = 0, now = 0;
    const setReadout = readout(st.readout, [
      ['rewind_ms', T('rewind_ms')], ['hits', T('hits')], ['shots', T('shots')]
    ]);
    toggle(st.controls, T('lag_comp'), true, v => { p.rewind = v; });
    slider(st.controls, T('rtt'), 20, 220, p.rtt, 10, v => v + ' ms', v => { p.rtt = v; });
    slider(st.controls, T('range'), 20, 200, p.range, 10, v => v + ' ms', v => { p.range = v; });
    button(st.controls, T('fire'), () => {
      shots++;
      const rew = Math.min(p.range, p.rtt / 2 + 30);
      const cur = 0.5 + 0.35 * Math.sin(now * 1.6);
      const past = 0.5 + 0.35 * Math.sin((now - rew / 1000) * 1.6);
      const aim = p.rewind ? past : cur;
      if (Math.abs(aim - past) < 0.14) { hits++; flash = 0.25; }
    });

    const handle = loop((dt) => {
      now += dt; t += dt;
      flash = Math.max(0, flash - dt);
      clear(st, '#07080b');
      const y = st.h / 2;
      const cur = 0.5 + 0.35 * Math.sin(now * 1.6);
      const rew = Math.min(p.range, p.rtt / 2 + 30);
      const past = 0.5 + 0.35 * Math.sin((now - rew / 1000) * 1.6);
      st.ctx.strokeStyle = 'rgba(255,255,255,0.12)';
      st.ctx.beginPath(); st.ctx.moveTo(20, y); st.ctx.lineTo(st.w - 20, y); st.ctx.stroke();
      st.ctx.fillStyle = 'rgba(253,164,175,0.85)';
      st.ctx.beginPath(); st.ctx.arc(20 + cur * (st.w - 40), y, 8, 0, TAU); st.ctx.fill();
      st.ctx.fillStyle = 'rgba(251,191,107,0.65)';
      st.ctx.beginPath(); st.ctx.arc(20 + past * (st.w - 40), y - 30, 6, 0, TAU); st.ctx.fill();
      st.ctx.strokeStyle = 'rgba(200,247,81,0.55)';
      st.ctx.beginPath(); st.ctx.moveTo(20, y + 30); st.ctx.lineTo(st.w - 20, y + 30); st.ctx.stroke();
      st.ctx.fillStyle = 'rgba(200,247,81,0.9)';
      st.ctx.beginPath(); st.ctx.arc(20 + (p.rewind ? past : cur) * (st.w - 40), y + 30, 7, 0, TAU); st.ctx.fill();
      if (flash > 0) {
        st.ctx.fillStyle = 'rgba(200,247,81,' + flash * 1.6 + ')';
        st.ctx.beginPath(); st.ctx.arc(20 + past * (st.w - 40), y - 30, 16, 0, TAU); st.ctx.fill();
      }
      setReadout({
        rewind_ms: String(Math.round(rew)),
        hits: String(hits),
        shots: String(shots)
      });
      label(st.ctx, T('lagcomp_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = () => { shots = 0; hits = 0; flash = 0; };
    return handle;
  };

  /* ============================================================
     8. Interest management (AOI)
     ============================================================ */
  DEMOS.aoi = function (el) {
    const st = makeStage(el);
    const p = { radius: 120, budget: 60 };
    let ents = [], t = 0;
    const setReadout = readout(st.readout, [
      ['visible', T('visible')], ['total', T('total')], ['bw', T('bandwidth')]
    ]);
    slider(st.controls, T('aoi_radius'), 40, 220, p.radius, 10, v => v + ' m', v => { p.radius = v; });
    slider(st.controls, T('budget'), 10, 120, p.budget, 5, v => v + ' kbps', v => { p.budget = v; });
    button(st.controls, T('reset'), () => { ents = []; t = 0; });

    const handle = loop((dt) => {
      t += dt;
      if (ents.length < 220) {
        ents.push({ x: Math.random(), y: Math.random(), vx: (Math.random() - 0.5) * 0.02,
          vy: (Math.random() - 0.5) * 0.02, kind: Math.random() < 0.1 ? 'quest' : 'npc' });
      }
      ents.forEach((e) => {
        e.x += e.vx * dt; e.y += e.vy * dt;
        if (e.x < 0 || e.x > 1) e.vx *= -1;
        if (e.y < 0 || e.y > 1) e.vy *= -1;
      });
      const px = 0.5, py = 0.5;
      const scale = Math.min(st.w, st.h) * 0.9;
      const rNorm = p.radius / 240;
      let vis = 0;
      clear(st, '#07080b');
      st.ctx.strokeStyle = 'rgba(125,211,252,0.4)';
      st.ctx.beginPath();
      st.ctx.arc(st.w / 2, st.h / 2, rNorm * scale, 0, TAU);
      st.ctx.stroke();
      ents.forEach((e) => {
        const d = Math.hypot(e.x - px, e.y - py);
        const inside = d < rNorm;
        if (inside) vis++;
        st.ctx.fillStyle = inside
          ? (e.kind === 'quest' ? 'rgba(251,191,107,0.9)' : 'rgba(200,247,81,0.9)')
          : 'rgba(255,255,255,0.12)';
        st.ctx.beginPath();
        st.ctx.arc(st.w / 2 + (e.x - px) * scale, st.h / 2 + (e.y - py) * scale, inside ? 3 : 2, 0, TAU);
        st.ctx.fill();
      });
      st.ctx.fillStyle = 'rgba(253,164,175,0.95)';
      st.ctx.beginPath(); st.ctx.arc(st.w / 2, st.h / 2, 6, 0, TAU); st.ctx.fill();
      const shown = Math.min(vis, p.budget * 3);
      setReadout({
        visible: String(shown),
        total: String(ents.length),
        bw: (shown * 0.6).toFixed(1) + ' KB/s'
      });
      label(st.ctx, T('aoi_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = () => { ents = []; t = 0; };
    return handle;
  };

  /* ============================================================
     9. Bandwidth budget: priorities
     ============================================================ */
  DEMOS.budget = function (el) {
    const st = makeStage(el);
    const p = { budget: 60 };
    let ents = [], t = 0;
    const setReadout = readout(st.readout, [
      ['sent', T('sent')], ['dropped', T('dropped')], ['bytes', T('bytes')]
    ]);
    function gen() {
      ents = [];
      for (let i = 0; i < 24; i++) {
        ents.push({ id: i, prio: Math.random(), size: 8 + Math.random() * 30,
          near: Math.random(), changed: Math.random() < 0.5 });
      }
      ents.sort((a, b) => (b.prio * b.near + (b.changed ? 0.4 : 0)) - (a.prio * a.near + (a.changed ? 0.4 : 0)));
    }
    slider(st.controls, T('budget'), 10, 120, p.budget, 5, v => v + ' KB/s', v => { p.budget = v; });
    button(st.controls, T('reset'), gen);
    setTimeout(gen, 0);

    const handle = loop((dt) => {
      t += dt;
      if (t > 1.2) { t = 0; ents.forEach((e) => { e.changed = Math.random() < 0.4; }); }
      clear(st, '#07080b');
      let used = 0, sent = 0;
      const cap = p.budget * 10;               // bytes per tick, scaled for display
      const barW = st.w - 80;
      ents.forEach((e, i) => {
        const y = 26 + i * 9;
        const score = e.prio * e.near + (e.changed ? 0.4 : 0);
        const size = e.changed ? e.size : 2;
        const ok = used + size <= cap;
        if (ok) { used += size; sent++; }
        st.ctx.fillStyle = ok ? 'rgba(200,247,81,0.75)' : 'rgba(255,255,255,0.1)';
        st.ctx.fillRect(60, y, Math.max(2, (barW * Math.min(1, score))), 6);
        label(st.ctx, String(e.id), 44, y + 3, 'rgba(255,255,255,0.35)', 7, 'right');
      });
      st.ctx.fillStyle = 'rgba(125,211,252,0.9)';
      st.ctx.fillRect(60, st.h - 30, barW * Math.min(1, used / Math.max(1, cap)), 6);
      label(st.ctx, used + ' / ' + cap + ' B', st.w - 12, st.h - 27, 'rgba(255,255,255,0.5)', 8, 'right');
      setReadout({
        sent: sent + ' / ' + ents.length,
        dropped: String(ents.length - sent),
        bytes: used + ' B'
      });
      label(st.ctx, T('budget_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = gen;
    return handle;
  };

  /* ============================================================
     10. Sharding, zones and handoff
     ============================================================ */
  DEMOS.shard = function (el) {
    const st = makeStage(el);
    const p = { shards: 4, players: 220 };
    let ps = [], t = 0, handoffs = 0;
    const setReadout = readout(st.readout, [
      ['shards', T('shards')], ['players', T('players')], ['handoffs', T('handoffs')]
    ]);
    function gen() {
      ps = [];
      for (let i = 0; i < p.players; i++) {
        ps.push({ x: Math.random(), y: Math.random(), vx: (Math.random() - 0.5) * 0.03,
          vy: (Math.random() - 0.5) * 0.03, zone: 0 });
      }
    }
    slider(st.controls, T('shards'), 2, 8, p.shards, 1, v => String(v), v => { p.shards = v; gen(); });
    slider(st.controls, T('players'), 40, 600, p.players, 20, v => String(v), v => { p.players = v; gen(); });
    button(st.controls, T('reset'), gen);
    setTimeout(gen, 0);
    const cols = 4, rows = 3;

    const handle = loop((dt) => {
      t += dt;
      const W = st.w - 24, H = st.h - 40;
      const cw = W / cols, ch = H / rows;
      ps.forEach((q) => {
        const ox = q.x, oy = q.y;
        q.x += q.vx * dt; q.y += q.vy * dt;
        if (q.x < 0 || q.x > 1) q.vx *= -1;
        if (q.y < 0 || q.y > 1) q.vy *= -1;
        const cx = Math.min(cols - 1, Math.floor(q.x * cols));
        const cy = Math.min(rows - 1, Math.floor(q.y * rows));
        const z = cy * cols + cx;
        const sid = z % p.shards;
        if (sid !== q.zone) { q.zone = sid; handoffs++; }
      });
      clear(st, '#07080b');
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const z = y * cols + x;
          const sid = z % p.shards;
          const load = ps.filter((q) => q.zone === sid).length / p.shards;
          st.ctx.fillStyle = 'hsla(' + (sid / p.shards * 320) + ', 45%, ' +
            (10 + Math.min(24, load / 4)) + '%, 0.55)';
          st.ctx.fillRect(12 + x * cw, 24 + y * ch, cw - 2, ch - 2);
          label(st.ctx, 'S' + sid, 16 + x * cw, 32 + y * ch,
            'rgba(255,255,255,0.5)', 7);
        }
      }
      ps.forEach((q) => {
        st.ctx.fillStyle = 'rgba(200,247,81,0.85)';
        st.ctx.beginPath();
        st.ctx.arc(12 + q.x * W, 24 + q.y * H, 1.6, 0, TAU);
        st.ctx.fill();
      });
      setReadout({
        shards: String(p.shards),
        players: String(ps.length),
        handoffs: String(handoffs)
      });
      label(st.ctx, T('shard_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = gen;
    return handle;
  };

  /* ============================================================
     11. Matchmaking queue
     ============================================================ */
  DEMOS.session = function (el) {
    const st = makeStage(el);
    const p = { players: 120, window: 60 };
    let tickets = [], matched = [], t = 0, waitTotal = 0, matches = 0;
    const setReadout = readout(st.readout, [
      ['queue', T('queue')], ['wait', T('wait')], ['matches', T('matches')]
    ]);
    function gen() {
      tickets = [];
      for (let i = 0; i < p.players; i++) {
        tickets.push({ mmr: 1000 + Math.random() * 1200, born: 0, id: i });
      }
      matched = []; t = 0; waitTotal = 0; matches = 0;
    }
    slider(st.controls, T('players'), 20, 300, p.players, 10, v => String(v), v => { p.players = v; gen(); });
    slider(st.controls, T('window'), 20, 200, p.window, 10, v => String(v), v => { p.window = v; });
    button(st.controls, T('reset'), gen);
    setTimeout(gen, 0);

    const handle = loop((dt) => {
      t += dt;
      if (t > 0.5) {
        t = 0;
        tickets.sort((a, b) => a.mmr - b.mmr);
        for (let i = 0; i < tickets.length - 1; i++) {
          const a = tickets[i], b = tickets[i + 1];
          if (Math.abs(a.mmr - b.mmr) < p.window) {
            matches++;
            waitTotal += Math.min(60, (a.born += 1));
            matched.push({ mmr: (a.mmr + b.mmr) / 2, age: 0 });
            tickets.splice(i, 2);
            break;
          }
        }
        tickets.forEach((q) => { q.born += 0.5; });
        matched.forEach((m) => { m.age += 0.5; });
        matched = matched.slice(-30);
      }
      clear(st, '#07080b');
      const x0 = 30, x1 = st.w - 30, y0 = 26, y1 = st.h - 34;
      const mmrMin = 1000, mmrMax = 2200;
      st.ctx.strokeStyle = 'rgba(255,255,255,0.1)';
      st.ctx.beginPath(); st.ctx.moveTo(x0, y0); st.ctx.lineTo(x0, y1); st.ctx.stroke();
      tickets.forEach((q) => {
        const y = y1 - (q.mmr - mmrMin) / (mmrMax - mmrMin) * (y1 - y0);
        st.ctx.fillStyle = 'rgba(125,211,252,0.75)';
        st.ctx.beginPath(); st.ctx.arc(x0 + 8, y, 2.5, 0, TAU); st.ctx.fill();
      });
      matched.forEach((m) => {
        const y = y1 - (m.mmr - mmrMin) / (mmrMax - mmrMin) * (y1 - y0);
        st.ctx.fillStyle = 'rgba(200,247,81,' + Math.max(0.1, 0.9 - m.age / 20) + ')';
        st.ctx.beginPath();
        st.ctx.moveTo(x1 - 8, y - 4); st.ctx.lineTo(x1, y); st.ctx.lineTo(x1 - 8, y + 4);
        st.ctx.fill();
      });
      setReadout({
        queue: String(tickets.length),
        wait: (waitTotal / Math.max(1, matches)).toFixed(1) + ' s',
        matches: String(matches)
      });
      label(st.ctx, T('session_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = gen;
    return handle;
  };

  /* ============================================================
     12. Rate limit and DDoS
     ============================================================ */
  DEMOS.security = function (el) {
    const st = makeStage(el);
    const p = { attack: 40, rate: 20 };
    let allowed = 0, blocked = 0, tokens = 60, last = 0, t = 0, arrows = [];
    const setReadout = readout(st.readout, [
      ['allowed', T('allowed')], ['blocked', T('blocked_count')], ['drop', T('drop_rate')]
    ]);
    slider(st.controls, T('attack'), 0, 100, p.attack, 5, v => v + ' rps', v => { p.attack = v; });
    slider(st.controls, T('limit'), 5, 60, p.rate, 5, v => v + ' rps', v => { p.rate = v; });
    button(st.controls, T('reset'), () => { allowed = 0; blocked = 0; tokens = 60; arrows = []; });

    const handle = loop((dt) => {
      t += dt;
      tokens = Math.min(60, tokens + p.rate * dt);
      if (t > 0.08) {
        t = 0;
        const n = Math.max(1, Math.round(p.attack / 12));
        for (let i = 0; i < n; i++) {
          const ok = tokens >= 1;
          if (ok) { tokens -= 1; allowed++; } else blocked++;
          arrows.push({ x: 0, y: 0.2 + Math.random() * 0.6, ok });
        }
      }
      arrows.forEach((a) => { a.x += dt * 1.2; });
      arrows = arrows.filter((a) => a.x < 1).slice(-60);
      clear(st, '#07080b');
      st.ctx.fillStyle = 'rgba(125,211,252,0.12)';
      st.ctx.fillRect(st.w - 76, 30, 60, st.h - 60);
      label(st.ctx, T('server'), st.w - 46, 20, 'rgba(255,255,255,0.5)', 8, 'center');
      arrows.forEach((a) => {
        st.ctx.fillStyle = a.ok ? 'rgba(200,247,81,0.85)' : 'rgba(253,164,175,0.6)';
        st.ctx.beginPath();
        st.ctx.arc(20 + a.x * (st.w - 110), 30 + a.y * (st.h - 60), 1.8, 0, TAU);
        st.ctx.fill();
      });
      const total = Math.max(1, allowed + blocked);
      st.ctx.fillStyle = 'rgba(200,247,81,0.85)';
      st.ctx.fillRect(20, st.h - 28, (st.w - 120) * (tokens / 60), 6);
      setReadout({
        allowed: String(allowed),
        blocked: String(blocked),
        drop: Math.round(100 * blocked / total) + '%'
      });
      label(st.ctx, T('security_note'), 10, st.h - 8, 'rgba(255,255,255,0.45)', 9);
    });
    handle.reset = () => { allowed = 0; blocked = 0; tokens = 60; arrows = []; };
    return handle;
  };

})();
