/* ============================================================
   Interactive demos: Part IV — balance and progression.
   Mitigation curves, TTK/STK, XP curve, loot bands, gacha,
   inflation and a Monte-Carlo balance simulator.
   Plain canvas 2D, no dependencies.
   ============================================================ */
(function () {
  'use strict';

  const DEMOS = (window.GA_DEMOS = window.GA_DEMOS || {});
  const T = (key) => window.GA_T(key);
  const C = {
    acid: '#c8f751', mint: '#6ee7b7', sky: '#7dd3fc', amber: '#fbbf6b',
    rose: '#fda4af', violet: '#c4b5fd', ink: '#e7eddf', dim: '#6b7368',
    line: 'rgba(255,255,255,0.09)'
  };

  /* ---------- shared UI ---------- */
  function makeStage(el) {
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
        try { draw(dt); } catch (e) {
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
    if (color) { st.ctx.fillStyle = color; st.ctx.fillRect(0, 0, st.w, st.h); }
  }

  function grid(st, step) {
    const ctx = st.ctx;
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < st.w; x += step || 32) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, st.h); ctx.stroke();
    }
    for (let y = 0; y < st.h; y += step || 32) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(st.w, y); ctx.stroke();
    }
  }

  function label(ctx, text, x, y, color, size, align) {
    ctx.fillStyle = color || C.dim;
    ctx.font = (size || 10) + 'px ui-monospace, Menlo, monospace';
    ctx.textAlign = align || 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
  }

  function axes(st, pad) {
    const ctx = st.ctx;
    ctx.strokeStyle = 'rgba(255,255,255,0.16)';
    ctx.beginPath();
    ctx.moveTo(pad, pad);
    ctx.lineTo(pad, st.h - pad);
    ctx.lineTo(st.w - pad / 2, st.h - pad);
    ctx.stroke();
  }

  function polyline(st, pts, color, width) {
    if (!pts.length) return;
    const ctx = st.ctx;
    ctx.strokeStyle = color;
    ctx.lineWidth = width || 1.8;
    ctx.beginPath();
    pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
    ctx.stroke();
  }

  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, t) => a + (b - a) * t;

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
     1. Mitigation curves: armour → share of damage that gets through
     ============================================================ */
  DEMOS.mitigation = function (el) {
    const st = makeStage(el);
    const p = { armour: 100, model: 'multiplicative', hp: 1000, hit: 200 };
    const setReadout = readout(st.readout, [
      ['through', T('mit_through')], ['ehp', T('mit_ehp')], ['stk', T('mit_stk')]
    ]);

    function through(armour) {
      if (p.model === 'linear') return clamp(1 - armour / 400, 0, 1);
      if (p.model === 'log') return clamp(1 - 0.22 * Math.log(1 + armour / 10), 0.2, 1);
      return 100 / (100 + armour);
    }

    const armourCtl = slider(st.controls, T('armour'), 0, 400, p.armour, 5, v => String(v), v => { p.armour = v; });
    segmented(st.controls, [
      ['multiplicative', T('mit_mult')], ['linear', T('mit_lin')], ['log', T('mit_log')]
    ], p.model, (id) => { p.model = id; });

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 34);
      const padL = 40, padB = 26, padT = 18;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      const maxA = 400;
      const t = through(p.armour);
      const ehp = p.hp / t;
      const hits = Math.ceil(ehp / (p.hit * t));

      axes(st, padL);
      // 100% reference
      const y1 = padT;
      st.ctx.setLineDash([3, 4]);
      polyline(st, [[padL, y1], [st.w - 14, y1]], 'rgba(255,255,255,0.18)', 1);
      st.ctx.setLineDash([]);

      const pts = [];
      for (let a = 0; a <= maxA; a += 4) {
        const x = padL + (a / maxA) * plotW;
        const y = padT + (1 - through(a)) * plotH;
        pts.push([x, y]);
      }
      polyline(st, pts, C.acid, 2);

      const x = padL + (p.armour / maxA) * plotW;
      const y = padT + (1 - t) * plotH;
      st.ctx.fillStyle = C.mint;
      st.ctx.beginPath();
      st.ctx.arc(x, y, 4, 0, Math.PI * 2);
      st.ctx.fill();
      st.ctx.strokeStyle = 'rgba(110,231,183,0.4)';
      st.ctx.beginPath();
      st.ctx.moveTo(x, padT); st.ctx.lineTo(x, st.h - padB); st.ctx.stroke();

      label(st.ctx, '100%', padL + 4, padT - 6, C.dim, 8);
      label(st.ctx, '0%', padL + 4, st.h - padB + 10, C.dim, 8);
      label(st.ctx, T('armour'), padL + plotW / 2, st.h - 8, C.dim, 8, 'center');
      label(st.ctx, T('dmg_through'), padL + 6, padT + 12, C.dim, 8);
      label(st.ctx, String(p.armour), x, st.h - padB + 10, C.mint, 8, 'center');

      setReadout({
        through: (t * 100).toFixed(0) + '%',
        ehp: Math.round(ehp),
        stk: String(hits)
      });
    });
    handle.reset = () => { p.armour = 100; armourCtl.set(100); };
    return handle;
  };

  /* ============================================================
     2. TTK / STK matrix: damage vs effective HP
     ============================================================ */
  DEMOS.ttk = function (el) {
    const st = makeStage(el);
    const p = { dmg: 34, hp: 250, mit: 45 };
    const setReadout = readout(st.readout, [
      ['stk', T('mit_stk')], ['ttk', T('ttk_time')], ['ehp', T('mit_ehp')]
    ]);

    const cDmg = slider(st.controls, T('damage'), 10, 120, p.dmg, 1, v => String(v), v => { p.dmg = v; });
    const cHp = slider(st.controls, T('hp'), 80, 400, p.hp, 10, v => String(v), v => { p.hp = v; });
    const cMit = slider(st.controls, T('mitigation'), 0, 70, p.mit, 5, v => v + '%', v => { p.mit = v; });

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 34);
      const padL = 40, padB = 26, padT = 18;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      const ehp = p.hp / (1 - p.mit / 100);
      const stk = Math.ceil(ehp / p.dmg);
      const ttk = ehp / (p.dmg * 2.2);

      axes(st, padL);
      // hits needed as a staircase when damage grows
      const maxDmg = 120;
      let prev = null;
      for (let d = 10; d <= maxDmg; d += 1) {
        const hits = Math.ceil(ehp / d);
        const x = padL + ((d - 10) / (maxDmg - 10)) * plotW;
        const y = padT + plotH - clamp(hits / 20, 0, 1) * plotH;
        if (prev && prev[1] === y) {
          polyline(st, [prev, [x, y]], C.sky, 1.8);
        } else if (prev) {
          polyline(st, [prev, [x, prev[1]]], C.sky, 1.8);
          polyline(st, [[x, prev[1]], [x, y]], 'rgba(125,211,252,0.35)', 1);
        }
        prev = [x, y];
      }

      const cx = padL + ((p.dmg - 10) / (maxDmg - 10)) * plotW;
      st.ctx.strokeStyle = C.acid;
      st.ctx.beginPath();
      st.ctx.moveTo(cx, padT); st.ctx.lineTo(cx, st.h - padB); st.ctx.stroke();

      label(st.ctx, T('damage'), padL + plotW / 2, st.h - 8, C.dim, 8, 'center');
      label(st.ctx, T('hits'), padL + 6, padT + 10, C.dim, 8);
      label(st.ctx, '20', padL - 6, padT, C.dim, 8, 'right');
      label(st.ctx, '1', padL - 6, st.h - padB, C.dim, 8, 'right');
      label(st.ctx, '×' + stk, cx + 4, padT + 12, C.acid, 9);

      setReadout({
        stk: String(stk),
        ttk: ttk.toFixed(2) + T('s_unit'),
        ehp: Math.round(ehp)
      });
    });
    handle.reset = () => { p.dmg = 34; p.hp = 250; p.mit = 45; cDmg.set(34); cHp.set(250); cMit.set(45); };
    return handle;
  };

  /* ============================================================
     3. XP curve vs time to level
     ============================================================ */
  DEMOS.xpcurve = function (el) {
    const st = makeStage(el);
    const p = { b: 2.0, a: 100, rate: 900 };
    const setReadout = readout(st.readout, [
      ['l10', 'L10'], ['l30', 'L30'], ['total', T('xp_total')]
    ]);

    const cB = slider(st.controls, T('exponent'), 1.2, 3.0, p.b, 0.05, v => v.toFixed(2), v => { p.b = v; });
    const cRate = slider(st.controls, T('xp_rate'), 300, 2400, p.rate, 50, v => v + '/min', v => { p.rate = v; });

    const xp = (n) => p.a * Math.pow(n, p.b);

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 34);
      const padL = 42, padB = 26, padT = 18;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      const maxL = 60;
      let maxMin = 1;
      for (let n = 1; n <= maxL; n++) maxMin = Math.max(maxMin, xp(n) / p.rate);

      axes(st, padL);
      const pts = [];
      for (let n = 1; n <= maxL; n++) {
        const x = padL + ((n - 1) / (maxL - 1)) * plotW;
        const y = padT + plotH - (xp(n) / p.rate / maxMin) * plotH;
        pts.push([x, y]);
      }
      polyline(st, pts, C.acid, 2);

      [10, 30, 60].forEach((n) => {
        const x = padL + ((n - 1) / (maxL - 1)) * plotW;
        const y = padT + plotH - (xp(n) / p.rate / maxMin) * plotH;
        st.ctx.fillStyle = n === 30 ? C.amber : C.sky;
        st.ctx.beginPath();
        st.ctx.arc(x, y, 3, 0, Math.PI * 2);
        st.ctx.fill();
        label(st.ctx, 'L' + n, x, st.h - padB + 10, C.dim, 8, 'center');
      });

      label(st.ctx, T('min_level'), padL + 6, padT + 10, C.dim, 8);
      label(st.ctx, Math.round(maxMin) + T('min_unit'), st.w - 14, padT + 10, C.dim, 8, 'right');

      setReadout({
        l10: Math.round(xp(10) / p.rate) + T('min_unit'),
        l30: Math.round(xp(30) / p.rate) + T('min_unit'),
        total: Math.round(xp(60) / p.rate) + T('min_unit')
      });
    });
    handle.reset = () => { p.b = 2.0; p.rate = 900; cB.set(2.0); cRate.set(900); };
    return handle;
  };

  /* ============================================================
     4. Loot bands: weights → observed distribution
     ============================================================ */
  DEMOS.lootbands = function (el) {
    const st = makeStage(el);
    const p = { legendary: 2, epic: 18, rare: 80 };
    const setReadout = readout(st.readout, [
      ['legendary', T('lgd')], ['epic', T('epic')], ['rare', T('rare')]
    ]);

    const tiers = () => [
      ['common', 1000, C.dim],
      ['uncommon', 300, C.sky],
      ['rare', p.rare, C.mint],
      ['epic', p.epic, C.violet],
      ['legendary', p.legendary, C.amber]
    ];

    const cLgd = slider(st.controls, T('lgd'), 0.5, 20, p.legendary, 0.5, v => v.toFixed(1), v => { p.legendary = v; });
    const cEpic = slider(st.controls, T('epic'), 4, 80, p.epic, 1, v => String(v), v => { p.epic = v; });
    const cRare = slider(st.controls, T('rare'), 20, 300, p.rare, 5, v => String(v), v => { p.rare = v; });

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 34);
      const list = tiers();
      const total = list.reduce((s, t) => s + t[1], 0);
      const padL = 34, padB = 44, padT = 16;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      axes(st, padL);

      const bw = plotW / list.length;
      list.forEach((t, i) => {
        const share = t[1] / total;
        const h = Math.pow(share, 0.45) * plotH;      // compressed for readability
        const x = padL + i * bw + 6;
        const grad = st.ctx.createLinearGradient(0, st.h - padB - h, 0, st.h - padB);
        grad.addColorStop(0, t[2]);
        grad.addColorStop(1, t[2] + '22');
        st.ctx.fillStyle = grad;
        st.ctx.fillRect(x, st.h - padB - h, Math.max(3, bw - 12), h);
        label(st.ctx, (share * 100).toFixed(share < 0.01 ? 2 : 1) + '%',
          x + (bw - 12) / 2, st.h - padB - h - 8, t[2], 8, 'center');
        label(st.ctx, t[0].slice(0, 4), x + (bw - 12) / 2, st.h - padB + 10, C.dim, 8, 'center');
      });

      const oneIn = (n) => Math.round(total / n);
      setReadout({
        legendary: '1 / ' + oneIn(p.legendary),
        epic: '1 / ' + oneIn(p.epic),
        rare: '1 / ' + oneIn(p.rare)
      });
    });
    handle.reset = () => {
      p.legendary = 2; p.epic = 18; p.rare = 80;
      cLgd.set(2); cEpic.set(18); cRare.set(80);
    };
    return handle;
  };

  /* ============================================================
     5. Gacha: pulls until the reward, with soft pity
     ============================================================ */
  DEMOS.gacha = function (el) {
    const st = makeStage(el);
    const p = { rate: 0.6, soft: 74, step: 6, hard: 90 };
    const setReadout = readout(st.readout, [
      ['mean', T('gacha_mean')], ['med', T('median')], ['p90', 'p90']
    ]);

    function simulate() {
      const rng = mulberry32(97);
      const out = [];
      for (let i = 0; i < 4000; i++) {
        let k = 1;
        for (; k <= p.hard; k++) {
          const chance = p.rate / 100 + (k >= p.soft ? (p.step / 100) * (k - p.soft + 1) : 0);
          if (rng() < Math.min(1, chance) || k === p.hard) break;
        }
        out.push(k);
      }
      out.sort((a, b) => a - b);
      const mean = out.reduce((a, b) => a + b, 0) / out.length;
      return {
        data: out,
        mean,
        med: out[Math.floor(out.length / 2)],
        p90: out[Math.floor(out.length * 0.9)]
      };
    }

    let sim = simulate();
    const cRate = slider(st.controls, T('base_rate'), 0.1, 3, p.rate, 0.1, v => v.toFixed(1) + '%', v => { p.rate = v; sim = simulate(); });
    const cHard = slider(st.controls, T('hard_pity'), 40, 120, p.hard, 1, v => String(v), v => { p.hard = v; p.soft = Math.min(p.soft, p.hard - 5); sim = simulate(); });
    const cSoft = slider(st.controls, T('soft_pity'), 0, 110, p.soft, 1, v => String(v), v => { p.soft = Math.min(v, p.hard - 1); sim = simulate(); });
    const cStep = slider(st.controls, T('pity_step'), 1, 20, p.step, 1, v => '+' + v + '%', v => { p.step = v; sim = simulate(); });

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 34);
      const padL = 36, padB = 26, padT = 16;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      axes(st, padL);

      const bins = new Array(28).fill(0);
      const maxP = p.hard;
      sim.data.forEach((k) => {
        const b = Math.min(27, Math.floor((k - 1) / maxP * 28));
        bins[b]++;
      });
      const maxBin = Math.max.apply(null, bins) || 1;
      const bw = plotW / bins.length;
      bins.forEach((v, i) => {
        const h = (v / maxBin) * plotH;
        const x = padL + i * bw;
        const mid = (i + 0.5) / bins.length * maxP;
        st.ctx.fillStyle = mid >= p.soft ? 'rgba(251,191,107,0.55)' : 'rgba(200,247,81,0.45)';
        st.ctx.fillRect(x + 0.5, st.h - padB - h, Math.max(1, bw - 1), h);
      });

      const mark = (val, color, text) => {
        const x = padL + (val / maxP) * plotW;
        st.ctx.strokeStyle = color;
        st.ctx.setLineDash([3, 3]);
        st.ctx.beginPath();
        st.ctx.moveTo(x, padT); st.ctx.lineTo(x, st.h - padB); st.ctx.stroke();
        st.ctx.setLineDash([]);
        label(st.ctx, text, x + 3, padT + 8, color, 8);
      };
      mark(sim.med, C.sky, T('median'));
      mark(sim.p90, C.amber, 'p90');

      label(st.ctx, T('pulls'), padL + plotW / 2, st.h - 8, C.dim, 8, 'center');
      label(st.ctx, String(maxP), st.w - 14, st.h - padB + 10, C.dim, 8, 'right');

      setReadout({
        mean: sim.mean.toFixed(1),
        med: String(sim.med),
        p90: String(sim.p90)
      });
    });
    handle.reset = () => {
      p.rate = 0.6; p.soft = 74; p.step = 6; p.hard = 90;
      cRate.set(0.6); cSoft.set(74); cStep.set(6); cHard.set(90);
      sim = simulate();
    };
    return handle;
  };

  /* ============================================================
     6. Inflation: money supply with a progressive sink
     ============================================================ */
  DEMOS.inflation = function (el) {
    const st = makeStage(el);
    const p = { faucet: 250, sink: 30, alpha: 4, beta: 1.15 };
    const setReadout = readout(st.readout, [
      ['money', T('money')], ['sink', T('sink_h')], ['hours', T('years') || 'h']
    ]);

    let series = [];
    function simulate() {
      let money = 1000;
      series = [];
      const alpha = p.alpha / 10000;
      for (let h = 0; h < 240; h++) {
        const sink = p.sink + alpha * Math.pow(money, p.beta);
        money = Math.max(0, money + (p.faucet - sink));
        series.push({ money, sink });
      }
    }
    simulate();

    const cFaucet = slider(st.controls, T('faucet'), 50, 500, p.faucet, 10, v => String(v), v => { p.faucet = v; simulate(); });
    const cSink = slider(st.controls, T('sink'), 0, 300, p.sink, 5, v => String(v), v => { p.sink = v; simulate(); });
    const cGrowth = slider(st.controls, T('sink_growth'), 0, 20, p.alpha, 0.5, v => v.toFixed(1), v => { p.alpha = v; simulate(); });

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 34);
      const padL = 44, padB = 26, padT = 16;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      axes(st, padL);

      const max = Math.max.apply(null, series.map(s => s.money)) || 1;
      const pts = series.map((s, i) => [
        padL + (i / (series.length - 1)) * plotW,
        padT + plotH - (s.money / max) * plotH
      ]);
      polyline(st, pts, C.acid, 2);

      // sink line, normalised to its own maximum
      const maxSink = Math.max.apply(null, series.map(s => s.sink)) || 1;
      const sinkPts = series.map((s, i) => [
        padL + (i / (series.length - 1)) * plotW,
        padT + plotH - (s.sink / maxSink) * plotH
      ]);
      polyline(st, sinkPts, 'rgba(253,164,175,0.8)', 1.4);

      const last = series[series.length - 1];
      label(st.ctx, T('money'), padL + plotW / 2, st.h - 8, C.dim, 8, 'center');
      label(st.ctx, Math.round(max).toLocaleString(), st.w - 14, padT + 8, C.acid, 8, 'right');
      label(st.ctx, T('sink_h'), st.w - 14, padT + 22, C.rose, 8, 'right');
      label(st.ctx, '0', padL - 6, st.h - padB, C.dim, 8, 'right');

      setReadout({
        money: Math.round(last.money).toLocaleString(),
        sink: Math.round(last.sink).toLocaleString(),
        hours: '240'
      });
    });
    handle.reset = () => {
      p.faucet = 250; p.sink = 30; p.alpha = 4;
      cFaucet.set(250); cSink.set(30); cGrowth.set(4);
      simulate();
    };
    return handle;
  };

  /* ============================================================
     7. Balance simulator: a stochastic duel with a win rate
     ============================================================ */
  DEMOS['balance-sim'] = function (el) {
    const st = makeStage(el);
    const p = { dmgA: 12, hpA: 100, dmgB: 12, hpB: 108, turns: 40 };
    const setReadout = readout(st.readout, [
      ['win', T('win_a')], ['ci', '±95%'], ['turns', T('turns')]
    ]);

    let wins = 0.5, ci = 0.02, medTurns = 12, hist = new Array(20).fill(0);

    function simulate() {
      const rng = mulberry32(1234);
      const N = 4000;
      let w = 0;
      const turns = [];
      hist = new Array(20).fill(0);
      for (let i = 0; i < N; i++) {
        let ha = p.hpA, hb = p.hpB, t = 0;
        while (ha > 0 && hb > 0 && t < p.turns) {
          t++;
          hb -= p.dmgA * (0.85 + rng() * 0.3);
          if (hb <= 0) break;
          ha -= p.dmgB * (0.85 + rng() * 0.3);
        }
        if (hb <= 0) { w++; turns.push(t); }
        hist[Math.min(19, Math.floor(t / p.turns * 20))]++;
      }
      wins = w / N;
      ci = 1.96 * Math.sqrt(wins * (1 - wins) / N);
      turns.sort((a, b) => a - b);
      medTurns = turns.length ? turns[Math.floor(turns.length / 2)] : 0;
    }
    simulate();

    const cDa = slider(st.controls, T('dmg_a'), 5, 30, p.dmgA, 0.5, v => String(v), v => { p.dmgA = v; simulate(); });
    const cDb = slider(st.controls, T('dmg_b'), 5, 30, p.dmgB, 0.5, v => String(v), v => { p.dmgB = v; simulate(); });
    const cHa = slider(st.controls, T('hp_a'), 60, 200, p.hpA, 5, v => String(v), v => { p.hpA = v; simulate(); });
    const cHb = slider(st.controls, T('hp_b'), 60, 200, p.hpB, 5, v => String(v), v => { p.hpB = v; simulate(); });

    const handle = loop(() => {
      clear(st, '#07080b');
      grid(st, 34);
      const padL = 40, padB = 26, padT = 16;
      const plotW = st.w - padL - 14, plotH = st.h - padT - padB;
      axes(st, padL);

      // win-rate bar
      const y0 = padT + 10;
      st.ctx.fillStyle = 'rgba(255,255,255,0.06)';
      st.ctx.fillRect(padL, y0, plotW, 12);
      st.ctx.fillStyle = C.acid;
      st.ctx.fillRect(padL, y0, plotW * wins, 12);
      const xl = padL + plotW * (wins - ci);
      const xr = padL + plotW * (wins + ci);
      st.ctx.strokeStyle = C.mint;
      st.ctx.beginPath();
      st.ctx.moveTo(xl, y0 - 3); st.ctx.lineTo(xl, y0 + 15);
      st.ctx.moveTo(xr, y0 - 3); st.ctx.lineTo(xr, y0 + 15);
      st.ctx.stroke();
      label(st.ctx, (wins * 100).toFixed(1) + '%', padL + 6, y0 + 6, '#07080b', 9);

      // battle-length histogram
      const maxBin = Math.max.apply(null, hist) || 1;
      const bw = plotW / hist.length;
      const baseY = st.h - padB;
      const barH = plotH - 44;
      hist.forEach((v, i) => {
        const h = (v / maxBin) * barH;
        st.ctx.fillStyle = 'rgba(125,211,252,0.5)';
        st.ctx.fillRect(padL + i * bw + 1, baseY - h, Math.max(1, bw - 2), h);
      });
      label(st.ctx, T('turns'), padL + 6, padT + 34, C.dim, 8);
      label(st.ctx, T('battle_len'), padL + plotW / 2, st.h - 8, C.dim, 8, 'center');

      setReadout({
        win: (wins * 100).toFixed(1) + '%',
        ci: '±' + (ci * 100).toFixed(1),
        turns: String(medTurns)
      });
    });
    handle.reset = () => {
      p.dmgA = 12; p.hpA = 100; p.dmgB = 12; p.hpB = 108;
      cDa.set(12); cHa.set(100); cDb.set(12); cHb.set(108);
      simulate();
    };
    return handle;
  };
})();
