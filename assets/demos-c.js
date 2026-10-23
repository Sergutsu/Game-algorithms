/* ============================================================
   Interactive demos, part C (optimisation + heavy workloads)
   Plain canvas 2D plus an optional WebGPU/WebGL2 compute path.
   Each demo returns a handle with start / stop / toggle / reset.
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
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ============================================================
     GPU particles — WebGPU compute → WebGL2 transform feedback → CPU
     ============================================================ */
  DEMOS.gpuparticles = function (el) {
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

    const setReadout = readout;
    const params = { count: 20000, dt: 1 / 60 };
    let backend = 'cpu';
    let backendLabel = T('backend_starting');
    let fps = 0;
    let frames = 0;
    let fpsTimer = 0;

    // ---- controls
    const countSlider = slider(controls, T('particles_cap'), 1000, 200000, params.count, 1000,
      v => Math.round(v / 1000) + 'k', v => { params.count = v; reset(); });
    const speedSlider = slider(controls, T('speed'), 0, 3, 1, 0.05,
      v => v.toFixed(2) + '×', v => { params.dt = (1 / 60) * v; });
    button(controls, T('reset_btn'), () => reset());

    const info = document.createElement('div');
    info.className = 'demo-readout';
    info.style.marginTop = '4px';
    controls.appendChild(info);

    const RO = setReadout([
      ['backend', T('backend')],
      ['count', T('particles_count')],
      ['fps', T('fps')]
    ]);

    let gpu = null;      // { mode, api, ... }
    let raf = null;
    let last = 0;
    let paused = false;
    let t0 = performance.now();

    function fit() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const r = canvas.getBoundingClientRect();
      if (!r.width) return;
      canvas.width = Math.round(r.width * dpr);
      canvas.height = Math.round(r.height * dpr);
      if (gpu && gpu.mode === 'webgpu' && gpu.configure) gpu.configure();
      if (gpu && gpu.mode === 'webgl2' && gpu.resize) gpu.resize();
      if (gpu && gpu.mode === 'cpu') {
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
    }
    if (window.ResizeObserver) new ResizeObserver(fit).observe(canvas);

    /* ---------------- WebGPU path ---------------- */
    async function initWebGPU() {
      if (!navigator.gpu) return null;
      const adapter = await navigator.gpu.requestAdapter();
      if (!adapter) return null;
      const device = await adapter.requestDevice();
      const format = navigator.gpu.getPreferredCanvasFormat();
      const context = canvas.getContext('webgpu');
      if (!context) return null;

      const WGSL_SIM = `
        struct Particle { pos: vec2f, vel: vec2f };
        @group(0) @binding(0) var<storage, read_write> parts: array<Particle>;
        @group(0) @binding(1) var<uniform> params: vec4f; // dt, count, gravity, damping

        @compute @workgroup_size(64)
        fn main(@builtin(global_invocation_id) gid: vec3u) {
          let i = gid.x;
          if (i >= u32(params.y)) { return; }
          var p = parts[i];
          p.vel.y -= params.z * params.x;
          p.vel *= params.w;
          p.pos += p.vel * params.x;
          if (p.pos.y < -1.0) { p.pos.y = -1.0; p.vel.y = abs(p.vel.y) * 0.8; }
          if (p.pos.y > 1.0) { p.pos.y = 1.0; p.vel.y = -abs(p.vel.y) * 0.8; }
          if (p.pos.x < -1.0) { p.pos.x = -1.0; p.vel.x = abs(p.vel.x); }
          if (p.pos.x > 1.0) { p.pos.x = 1.0; p.vel.x = -abs(p.vel.x); }
          parts[i] = p;
        }`;

      const WGSL_DRAW = `
        struct Particle { pos: vec2f, vel: vec2f };
        @group(0) @binding(0) var<storage, read> parts: array<Particle>;
        struct VSOut { @builtin(position) pos: vec4f, @location(0) col: vec4f };
        @vertex
        fn vs(@builtin(vertex_index) vi: u32, @builtin(instance_index) ii: u32) -> VSOut {
          let corners = array<vec2f, 6>(
            vec2f(-1.0, -1.0), vec2f(1.0, -1.0), vec2f(-1.0, 1.0),
            vec2f(-1.0, 1.0), vec2f(1.0, -1.0), vec2f(1.0, 1.0));
          let c = corners[vi];
          let p = parts[ii].pos;
          let speed = length(parts[ii].vel);
          var out: VSOut;
          out.pos = vec4f(p + c * 0.008, 0.0, 1.0);
          out.col = vec4f(0.78, 0.97, 0.32, clamp(speed * 0.5, 0.15, 1.0));
          return out;
        }
        @fragment
        fn fs(in: VSOut) -> @location(0) vec4f { return in.col; }`;

      const simModule = device.createShaderModule({ code: WGSL_SIM });
      const drawModule = device.createShaderModule({ code: WGSL_DRAW });
      const simPipeline = device.createComputePipeline({
        layout: 'auto', compute: { module: simModule, entryPoint: 'main' }
      });
      const drawPipeline = device.createRenderPipeline({
        layout: 'auto',
        vertex: { module: drawModule, entryPoint: 'vs' },
        fragment: { module: drawModule, entryPoint: 'fs', targets: [{ format }] },
        primitive: { topology: 'triangle-list' }
      });

      let particleBuf = null;
      let uniformBuf = null;
      let bindSim = null;
      let bindDraw = null;
      let capacity = 0;

      function allocate(n) {
        if (particleBuf) particleBuf.destroy();
        capacity = n;
        particleBuf = device.createBuffer({
          size: n * 16,
          usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST
        });
        const data = new Float32Array(n * 4);
        const rnd = mulberry32(42);
        for (let i = 0; i < n; i++) {
          data[i * 4 + 0] = rnd() * 2 - 1;
          data[i * 4 + 1] = rnd() * 2 - 1;
          data[i * 4 + 2] = (rnd() - 0.5) * 0.6;
          data[i * 4 + 3] = (rnd() - 0.5) * 0.6;
        }
        device.queue.writeBuffer(particleBuf, 0, data);
        uniformBuf = device.createBuffer({
          size: 16,
          usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST
        });
        bindSim = device.createBindGroup({
          layout: simPipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: { buffer: particleBuf } },
            { binding: 1, resource: { buffer: uniformBuf } }
          ]
        });
        bindDraw = device.createBindGroup({
          layout: drawPipeline.getBindGroupLayout(0),
          entries: [{ binding: 0, resource: { buffer: particleBuf } }]
        });
      }

      function configure() {
        context.configure({ device, format, alphaMode: 'opaque' });
      }

      function frame(dt) {
        if (!particleBuf) return;
        const n = params.count;
        if (n > capacity) allocate(n);
        device.queue.writeBuffer(uniformBuf, 0,
          new Float32Array([params.dt, n, 9.81, 0.999]));

        const enc = device.createCommandEncoder();
        const cp = enc.beginComputePass();
        cp.setPipeline(simPipeline);
        cp.setBindGroup(0, bindSim);
        cp.dispatchWorkgroups(Math.ceil(n / 64));
        cp.end();

        const rp = enc.beginRenderPass({
          colorAttachments: [{
            view: context.getCurrentTexture().createView(),
            clearValue: { r: 0.035, g: 0.04, b: 0.06, a: 1 },
            loadOp: 'clear', storeOp: 'store'
          }]
        });
        rp.setPipeline(drawPipeline);
        rp.setBindGroup(0, bindDraw);
        rp.draw(6, n);
        rp.end();
        device.queue.submit([enc.finish()]);
      }

      configure();
      allocate(params.count);
      return {
        mode: 'webgpu', frame,
        configure,
        resize() { configure(); },
        destroy() { if (particleBuf) particleBuf.destroy(); }
      };
    }

    /* ---------------- WebGL2 transform feedback ---------------- */
    function initWebGL2() {
      const gl = canvas.getContext('webgl2', { antialias: false });
      if (!gl) return null;
      if (!gl.getExtension('EXT_color_buffer_float')) return null;

      const SIM_VS = `#version 300 es
        in vec2 a_pos;
        in vec2 a_vel;
        uniform float u_dt;
        uniform float u_count;
        uniform float u_damp;
        out vec2 v_pos;
        out vec2 v_vel;
        void main() {
          vec2 p = a_pos;
          vec2 v = a_vel;
          v.y -= 9.81 * u_dt;
          v *= u_damp;
          p += v * u_dt;
          if (p.y < -1.0) { p.y = -1.0; v.y = abs(v.y) * 0.8; }
          if (p.y > 1.0)  { p.y = 1.0;  v.y = -abs(v.y) * 0.8; }
          if (p.x < -1.0) { p.x = -1.0; v.x = abs(v.x); }
          if (p.x > 1.0)  { p.x = 1.0;  v.x = -abs(v.x); }
          v_pos = p;
          v_vel = v;
          gl_Position = vec4(p, 0.0, 1.0);
        }`;

      const DRAW_VS = `#version 300 es
        in vec2 a_pos;
        uniform float u_size;
        out float v_speed;
        void main() {
          gl_Position = vec4(a_pos, 0.0, 1.0);
          gl_PointSize = u_size;
          v_speed = length(a_pos);
        }`;

      const DRAW_FS = `#version 300 es
        precision mediump float;
        in float v_speed;
        out vec4 outColor;
        void main() {
          float d = length(gl_PointCoord - vec2(0.5));
          if (d > 0.5) discard;
          outColor = vec4(0.78, 0.97, 0.32, (1.0 - d * 2.0) * 0.85);
        }`;

      function compile(type, src) {
        const sh = gl.createShader(type);
        gl.shaderSource(sh, src);
        gl.compileShader(sh);
        if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
          console.warn('[demo] shader', gl.getShaderInfoLog(sh));
          return null;
        }
        return sh;
      }
      function program(vsSrc, fsSrc, tfVaryings) {
        const vs = compile(gl.VERTEX_SHADER, vsSrc);
        const fs = compile(gl.FRAGMENT_SHADER, fsSrc);
        if (!vs || !fs) return null;
        const p = gl.createProgram();
        gl.attachShader(p, vs);
        gl.attachShader(p, fs);
        if (tfVaryings) {
          gl.transformFeedbackVaryings(p, tfVaryings, gl.SEPARATE_ATTRIBS);
        }
        gl.linkProgram(p);
        if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
          console.warn('[demo] link', gl.getProgramInfoLog(p));
          return null;
        }
        return p;
      }

      const simProg = program(SIM_VS, DRAW_FS, ['v_pos', 'v_vel']);
      const drawProg = program(DRAW_VS, DRAW_FS, null);
      if (!simProg || !drawProg) return null;

      const tf = gl.createTransformFeedback();
      let bufs = [];
      let vaos = [];
      let capacity = 0;

      function allocate(n) {
        bufs.forEach((b) => { gl.deleteBuffer(b.pos); gl.deleteBuffer(b.vel); });
        vaos.forEach((v) => gl.deleteVertexArray(v));
        bufs = []; vaos = []; capacity = n;
        const rnd = mulberry32(42);
        const pos = new Float32Array(n * 2);
        const vel = new Float32Array(n * 2);
        for (let i = 0; i < n; i++) {
          pos[i * 2] = rnd() * 2 - 1;
          pos[i * 2 + 1] = rnd() * 2 - 1;
          vel[i * 2] = (rnd() - 0.5) * 0.6;
          vel[i * 2 + 1] = (rnd() - 0.5) * 0.6;
        }
        for (let k = 0; k < 2; k++) {
          const bpos = gl.createBuffer();
          const bvel = gl.createBuffer();
          gl.bindBuffer(gl.ARRAY_BUFFER, bpos);
          gl.bufferData(gl.ARRAY_BUFFER, pos, gl.DYNAMIC_COPY);
          gl.bindBuffer(gl.ARRAY_BUFFER, bvel);
          gl.bufferData(gl.ARRAY_BUFFER, vel, gl.DYNAMIC_COPY);
          const vao = gl.createVertexArray();
          gl.bindVertexArray(vao);
          gl.bindBuffer(gl.ARRAY_BUFFER, bpos);
          const aPos = gl.getAttribLocation(simProg, 'a_pos');
          gl.enableVertexAttribArray(aPos);
          gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);
          gl.bindBuffer(gl.ARRAY_BUFFER, bvel);
          const aVel = gl.getAttribLocation(simProg, 'a_vel');
          gl.enableVertexAttribArray(aVel);
          gl.vertexAttribPointer(aVel, 2, gl.FLOAT, false, 0, 0);
          gl.bindVertexArray(null);
          bufs.push({ pos: bpos, vel: bvel });
          vaos.push(vao);
        }
        // draw VAOs: read position from the *other* buffer
        drawVaos = [];
        for (let k = 0; k < 2; k++) {
          const vao = gl.createVertexArray();
          gl.bindVertexArray(vao);
          gl.bindBuffer(gl.ARRAY_BUFFER, bufs[k].pos);
          const aPos = gl.getAttribLocation(drawProg, 'a_pos');
          gl.enableVertexAttribArray(aPos);
          gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);
          gl.bindVertexArray(null);
          drawVaos.push(vao);
        }
      }
      let drawVaos = [];
      let cur = 0;

      function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const r = canvas.getBoundingClientRect();
        if (!r.width) return;
        canvas.width = Math.round(r.width * dpr);
        canvas.height = Math.round(r.height * dpr);
        gl.viewport(0, 0, canvas.width, canvas.height);
      }

      function frame(dt) {
        const n = params.count;
        if (n > capacity) allocate(n);
        resize();
        gl.clearColor(0.035, 0.04, 0.06, 1);
        gl.clear(gl.COLOR_BUFFER_BIT);

        // --- simulation pass with transform feedback
        gl.useProgram(simProg);
        gl.uniform1f(gl.getUniformLocation(simProg, 'u_dt'), params.dt);
        gl.uniform1f(gl.getUniformLocation(simProg, 'u_count'), n);
        gl.uniform1f(gl.getUniformLocation(simProg, 'u_damp'), 0.999);
        const src = cur, dst = 1 - cur;
        gl.bindVertexArray(vaos[src]);
        gl.bindTransformFeedback(gl.TRANSFORM_FEEDBACK, tf);
        gl.bindBufferBase(gl.TRANSFORM_FEEDBACK_BUFFER, 0, bufs[dst].pos);
        gl.bindBufferBase(gl.TRANSFORM_FEEDBACK_BUFFER, 1, bufs[dst].vel);
        gl.enable(gl.RASTERIZER_DISCARD);
        gl.beginTransformFeedback(gl.POINTS);
        gl.drawArrays(gl.POINTS, 0, n);
        gl.endTransformFeedback();
        gl.disable(gl.RASTERIZER_DISCARD);
        gl.bindBufferBase(gl.TRANSFORM_FEEDBACK_BUFFER, 0, null);
        gl.bindBufferBase(gl.TRANSFORM_FEEDBACK_BUFFER, 1, null);
        gl.bindTransformFeedback(gl.TRANSFORM_FEEDBACK, null);
        cur = dst;

        // --- render pass
        gl.useProgram(drawProg);
        gl.uniform1f(gl.getUniformLocation(drawProg, 'u_size'), 2.0);
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
        gl.bindVertexArray(drawVaos[dst]);
        gl.drawArrays(gl.POINTS, 0, n);
        gl.disable(gl.BLEND);
        gl.bindVertexArray(null);
      }

      allocate(params.count);
      resize();
      return { mode: 'webgl2', frame, resize, destroy() {} };
    }

    /* ---------------- CPU fallback ---------------- */
    function initCPU() {
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;
      let pos = null, vel = null, n = 0;
      function allocate(count) {
        n = count;
        pos = new Float32Array(count * 2);
        vel = new Float32Array(count * 2);
        const rnd = mulberry32(42);
        for (let i = 0; i < count; i++) {
          pos[i * 2] = rnd() * 2 - 1;
          pos[i * 2 + 1] = rnd() * 2 - 1;
          vel[i * 2] = (rnd() - 0.5) * 0.6;
          vel[i * 2 + 1] = (rnd() - 0.5) * 0.6;
        }
      }
      function frame(dt) {
        if (!pos || pos.length / 2 !== n) allocate(n);
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const r = canvas.getBoundingClientRect();
        if (r.width && canvas.width !== Math.round(r.width * dpr)) {
          canvas.width = Math.round(r.width * dpr);
          canvas.height = Math.round(r.height * dpr);
        }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, r.width, r.height);
        ctx.fillStyle = '#0a0b0f';
        ctx.fillRect(0, 0, r.width, r.height);
        const cx = r.width / 2, cy = r.height / 2;
        const sc = Math.min(r.width, r.height) / 2.4;
        const step = Math.min(params.dt, 0.02);
        ctx.fillStyle = C.acid;
        for (let i = 0; i < n; i++) {
          let vx = vel[i * 2], vy = vel[i * 2 + 1];
          let x = pos[i * 2], y = pos[i * 2 + 1];
          vy -= 9.81 * step;
          vx *= 0.999; vy *= 0.999;
          x += vx * step; y += vy * step;
          if (y < -1) { y = -1; vy = Math.abs(vy) * 0.8; }
          if (y > 1) { y = 1; vy = -Math.abs(vy) * 0.8; }
          if (x < -1) { x = -1; vx = Math.abs(vx); }
          if (x > 1) { x = 1; vx = -Math.abs(vx); }
          pos[i * 2] = x; pos[i * 2 + 1] = y;
          vel[i * 2] = vx; vel[i * 2 + 1] = vy;
          ctx.fillRect(cx + x * sc - 0.7, cy - y * sc - 0.7, 1.6, 1.6);
        }
      }
      allocate(params.count);
      return { mode: 'cpu', frame, destroy() {} };
    }

    /* ---------------- boot ---------------- */
    let ready = false;
    const readyPromise = (async () => {
      let impl = null;
      try { impl = await initWebGPU(); } catch (e) { impl = null; }
      if (!impl) {
        try { impl = initWebGL2(); } catch (e) { impl = null; }
      }
      if (!impl) {
        try { impl = initCPU(); } catch (e) { impl = null; }
      }
      if (!impl) return;
      gpu = impl;
      backend = impl.mode;
      backendLabel = impl.mode === 'webgpu' ? T('backend_webgpu')
        : impl.mode === 'webgl2' ? T('backend_webgl2') : T('backend_cpu');
      ready = true;
      info.textContent = backendLabel;
    })();

    function reset() {
      if (gpu && gpu.mode === 'webgpu') { /* the buffer is reallocated for the new size */ }
      if (gpu && gpu.mode === 'webgl2') { /* allocated for the new size */ }
    }

    function tick(now) {
      const dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016;
      last = now;
      frames++;
      if (now - fpsTimer > 500) {
        fps = Math.round(frames * 1000 / (now - fpsTimer));
        frames = 0;
        fpsTimer = now;
        RO({
          backend: backendLabel,
          count: params.count.toLocaleString('en-US'),
          fps: fps
        });
      }
      if (!paused && ready && gpu) {
        try { gpu.frame(dt); } catch (e) {
          console.warn('[demo]', e);
        }
      }
      raf = requestAnimationFrame(tick);
    }

    fit();
    raf = requestAnimationFrame(tick);
    RO({ backend: backendLabel, count: params.count.toLocaleString('en-US'), fps: '—' });

    return {
      start() { if (raf === null) { last = 0; raf = requestAnimationFrame(tick); } },
      stop() { if (raf !== null) { cancelAnimationFrame(raf); raf = null; } },
      toggle() { paused = !paused; return paused; },
      get paused() { return paused; },
      reset() { reset(); }
    };
  };

  /* ============================================================
     Frame budget — who eats the 16.6 ms
     ============================================================ */
  DEMOS.framebudget = function (el) {
    const st = makeStage(el);
    const params = { cpu_sim: 3.0, cpu_render: 2.0, gpu: 7.0, io: 1.5, fps: 60 };

    const setReadout = readout(st.readout, [
      ['total', T('budget_total')],
      ['free', T('budget_left')]
    ]);

    slider(st.controls, T('budget_cpu') + ' · sim', 0, 20, params.cpu_sim, 0.5,
      v => v.toFixed(1) + ' ms', v => { params.cpu_sim = v; });
    slider(st.controls, T('budget_cpu') + ' · render', 0, 20, params.cpu_render, 0.5,
      v => v.toFixed(1) + ' ms', v => { params.cpu_render = v; });
    slider(st.controls, T('budget_gpu'), 0, 30, params.gpu, 0.5,
      v => v.toFixed(1) + ' ms', v => { params.gpu = v; });
    slider(st.controls, T('budget_io'), 0, 20, params.io, 0.5,
      v => v.toFixed(1) + ' ms', v => { params.io = v; });

    const fpsSel = document.createElement('select');
    fpsSel.className = 'chip';
    [30, 60, 120, 144].forEach((f) => {
      const o = document.createElement('option');
      o.value = f; o.textContent = f + ' FPS';
      if (f === params.fps) o.selected = true;
      fpsSel.appendChild(o);
    });
    fpsSel.addEventListener('change', () => { params.fps = +fpsSel.value; });
    st.controls.appendChild(fpsSel);

    const draw = () => {
      const ctx = st.ctx;
      const budget = 1000 / params.fps;
      const parts = [
        { name: T('budget_cpu') + ' · sim', v: params.cpu_sim, c: C.acid },
        { name: T('budget_cpu') + ' · render', v: params.cpu_render, c: C.mint },
        { name: T('budget_gpu'), v: params.gpu, c: C.sky },
        { name: T('budget_io'), v: params.io, c: C.amber }
      ];
      const total = parts.reduce((s, p) => s + p.v, 0);
      const over = Math.max(0, total - budget);

      ctx.clearRect(0, 0, st.w, st.h);
      const padX = 16, padTop = 30, barH = 34;
      const barW = st.w - padX * 2;

      label(ctx, T('frame_budget') + ' · ' + params.fps + ' FPS = ' + budget.toFixed(1) + ' ms',
        padX, 16, C.ink, 10);

      // budget frame
      ctx.strokeStyle = C.line;
      ctx.lineWidth = 1;
      ctx.strokeRect(padX + 0.5, padTop + 0.5, barW, barH);

      // stacked segments scaled to max(total, budget)
      const scale = barW / Math.max(total, budget);
      let x = padX;
      parts.forEach((p) => {
        const w = p.v * scale;
        ctx.fillStyle = p.c;
        ctx.globalAlpha = 0.85;
        ctx.fillRect(x, padTop + 1, Math.max(0, w - 1), barH - 2);
        ctx.globalAlpha = 1;
        if (w > 46) {
          label(ctx, p.v.toFixed(1), x + 5, padTop + barH / 2, '#0a0b0f', 9);
        }
        x += w;
      });

      // overflow marker
      if (over > 0) {
        const wx = padX + budget * scale;
        ctx.strokeStyle = C.rose;
        ctx.setLineDash([4, 3]);
        ctx.beginPath();
        ctx.moveTo(wx, padTop - 6);
        ctx.lineTo(wx, padTop + barH + 6);
        ctx.stroke();
        ctx.setLineDash([]);
        label(ctx, T('over_budget') + ' +' + over.toFixed(1) + ' ms', Math.min(wx + 6, st.w - 90), padTop + barH + 16, C.rose, 9);
      } else {
        const free = budget - total;
        label(ctx, T('budget_left') + ' ' + free.toFixed(1) + ' ms',
          Math.min(padX + total * scale + 8, st.w - 110), padTop + barH + 16, C.mint, 9);
      }

      // legend
      parts.forEach((p, i) => {
        const ly = padTop + barH + 38 + i * 15;
        ctx.fillStyle = p.c;
        ctx.fillRect(padX, ly - 4, 8, 8);
        label(ctx, p.name + '  ' + p.v.toFixed(1) + ' ms', padX + 14, ly, C.dim, 9);
      });

      // hint
      if (over > 0) {
        const hint = params.gpu > params.cpu_sim + params.cpu_render
          ? T('budget_gpu') + ' → ' + T('resolution')
          : T('budget_cpu') + ' → ' + T('quality');
        label(ctx, hint + ' · ' + T('quality') + ' ↓', padX, st.h - 14, C.amber, 9);
      }

      setReadout({
        total: total.toFixed(1) + ' ms',
        free: (budget - total).toFixed(1) + ' ms'
      });
    };

    const handle = loop(draw);
    handle.reset = () => {
      params.cpu_sim = 3; params.cpu_render = 2; params.gpu = 7; params.io = 1.5;
      params.fps = 60;
    };
    return handle;
  };

  /* ============================================================
     Culling — frustum, occlusion, LOD
     ============================================================ */
  DEMOS.culling = function (el) {
    const st = makeStage(el);
    const params = { count: 900, fov: 70, occlusion: true, lod: true };

    const setReadout = readout(st.readout, [
      ['visible', T('visible')],
      ['culled', T('culled')],
      ['lod', T('lod')]
    ]);

    slider(st.controls, T('objects'), 100, 2000, params.count, 50,
      v => String(v), v => { params.count = v; });
    slider(st.controls, 'FOV', 20, 140, params.fov, 5,
      v => v + '°', v => { params.fov = v; });

    const occBtn = button(st.controls, T('culled') + ': occlusion', () => {
      params.occlusion = !params.occlusion;
      occBtn.textContent = T('culled') + ': occlusion ' + (params.occlusion ? '✓' : '✗');
    });
    occBtn.textContent = T('culled') + ': occlusion ✓';
    const lodBtn = button(st.controls, T('lod') + ': ✓', () => {
      params.lod = !params.lod;
      lodBtn.textContent = T('lod') + ': ' + (params.lod ? '✓' : '✗');
    });

    const objs = [];
    let seeded = 0;
    function ensure(n) {
      while (objs.length < n) {
        const rnd = mulberry32(1234 + objs.length);
        objs.push({
          x: rnd() * 2 - 1,
          y: rnd() * 1.8 - 0.9,
          r: 0.012 + rnd() * 0.022,
          mat: Math.floor(rnd() * 4)
        });
      }
      objs.length = n;
    }

    let angle = 0;

    function draw(dt) {
      const ctx = st.ctx;
      ensure(params.count);
      angle += dt * 0.25;

      const cx = st.w / 2;
      const cy = st.h - 24;
      const scale = Math.min(st.w / 2.4, st.h / 2.2);
      const half = (params.fov * Math.PI / 180) / 2;
      const dir = Math.sin(angle) * 0.9;
      const wallX = 0.18;

      ctx.clearRect(0, 0, st.w, st.h);
      ctx.fillStyle = '#0a0b0f';
      ctx.fillRect(0, 0, st.w, st.h);

      // frustum wedge
      const len = 1.5 * scale;
      const a1 = Math.PI / 2 + dir - half;
      const a2 = Math.PI / 2 + dir + half;
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, len);
      g.addColorStop(0, 'rgba(200,247,81,0.13)');
      g.addColorStop(1, 'rgba(200,247,81,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, len, -a1 + Math.PI / 2, -a2 + Math.PI / 2);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = 'rgba(200,247,81,0.28)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // occluder wall
      if (params.occlusion) {
        const wx = cx + wallX * scale;
        ctx.fillStyle = 'rgba(244,114,182,0.16)';
        ctx.fillRect(wx - 3, cy - 1.25 * scale, 6, 1.25 * scale);
        ctx.strokeStyle = 'rgba(244,114,182,0.5)';
        ctx.strokeRect(wx - 3, cy - 1.25 * scale, 6, 1.25 * scale);
      }

      let visible = 0, culled = 0, lodSum = 0;
      const colors = [C.acid, C.sky, C.violet, C.amber];
      const LOD_C = ['#c8f751', '#7dd3fc', '#c4b5fd', '#fbbf6b'];

      for (const o of objs) {
        const dx = o.x;
        const dy = o.y;
        const dist = Math.hypot(dx, dy);
        // angle test against the wedge
        const ang = Math.atan2(dx, Math.max(0.05, dy + 1.0));
        const rel = Math.abs(ang - dir * 0.9);
        const inFrustum = rel < half && dy > -1.05;
        if (!inFrustum) { culled++; continue; }
        let occluded = false;
        if (params.occlusion && dx > wallX && dy > -1.05) occluded = true;
        if (occluded) { culled++; continue; }
        visible++;
        const lodLevel = params.lod
          ? Math.min(3, Math.floor(dist * 3.2))
          : 0;
        lodSum += lodLevel;
        const px = cx + dx * scale;
        const py = cy - (dy + 1.0) * scale;
        const pr = Math.max(1.4, o.r * scale * (1 - lodLevel * 0.18));
        ctx.fillStyle = LOD_C[lodLevel];
        ctx.globalAlpha = 0.9;
        ctx.beginPath();
        ctx.arc(px, py, pr, 0, TAU);
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      // camera
      ctx.fillStyle = C.ink;
      ctx.beginPath();
      ctx.arc(cx, cy, 4, 0, TAU);
      ctx.fill();

      label(ctx, T('visible') + ': ' + visible, 10, 12, C.mint, 10);
      label(ctx, T('culled') + ': ' + culled, 10, 26, C.dim, 10);
      label(ctx, T('lod') + ': ' + (visible ? (lodSum / visible).toFixed(2) : '0'), 10, 40, C.dim, 10);
      label(ctx, T('draw_calls') + ': ' + visible, st.w - 10, 12, C.sky, 10, 'right');
      label(ctx, T('triangles') + ': ' + (visible * 1800).toLocaleString('en-US'),
        st.w - 10, 26, C.dim, 9, 'right');

      setReadout({
        visible: String(visible),
        culled: String(culled),
        lod: visible ? (lodSum / visible).toFixed(2) : '0'
      });
    }

    const handle = loop(draw);
    handle.reset = () => {
      params.count = 900; params.fov = 70; params.occlusion = true; params.lod = true;
      angle = 0;
    };
    return handle;
  };

  /* ============================================================
     Draw calls — batching
     ============================================================ */
  DEMOS.drawcalls = function (el) {
    const st = makeStage(el);
    const params = { objects: 2000, materials: 12 };

    const setReadout = readout(st.readout, [
      ['calls', T('draw_calls')],
      ['batches', T('batches')],
      ['save', T('save_pct')]
    ]);

    slider(st.controls, T('objects'), 100, 5000, params.objects, 100,
      v => String(v), v => { params.objects = v; });
    slider(st.controls, T('batches'), 1, 40, params.materials, 1,
      v => String(v), v => { params.materials = v; });

    function draw() {
      const ctx = st.ctx;
      ctx.clearRect(0, 0, st.w, st.h);
      ctx.fillStyle = '#0a0b0f';
      ctx.fillRect(0, 0, st.w, st.h);

      const n = params.objects;
      const mats = Math.min(params.materials, n);
      const cols = 40;
      const rows = Math.ceil(n / cols);
      const cell = Math.max(2, Math.min((st.w - 40) / cols, (st.h - 70) / Math.max(1, rows)));
      const gridW = cols * cell;
      const gridH = rows * cell;
      const ox = (st.w - gridW) / 2;
      const oy = 34;

      // objects grouped by material (sorted) — the CPU-side sort
      const order = [];
      for (let m = 0; m < mats; m++) {
        for (let i = m; i < n; i += mats) order.push({ i, m });
      }

      const palette = [C.acid, C.mint, C.sky, C.violet, C.amber, C.rose];
      let prevMat = -1;
      let switches = 0;
      order.forEach((o, k) => {
        if (o.m !== prevMat) { switches++; prevMat = o.m; }
        const x = ox + (k % cols) * cell;
        const y = oy + Math.floor(k / cols) * cell;
        ctx.fillStyle = palette[o.m % palette.length];
        ctx.globalAlpha = 0.85;
        ctx.fillRect(x + 0.5, y + 0.5, Math.max(1, cell - 1.5), Math.max(1, cell - 1.5));
        ctx.globalAlpha = 1;
      });

      const unbatched = n;
      const batched = mats;
      const save = unbatched ? Math.round(100 * (1 - batched / unbatched)) : 0;

      label(ctx, T('objects') + ': ' + n.toLocaleString('en-US'), 12, 16, C.ink, 10);
      label(ctx, T('draw_calls') + ': ' + unbatched.toLocaleString('en-US') + ' → ' + batched,
        12, st.h - 16, C.rose, 10);
      label(ctx, T('save_pct') + ': ' + save + '%', st.w - 12, st.h - 16, C.mint, 10, 'right');

      setReadout({
        calls: unbatched.toLocaleString('en-US'),
        batches: String(batched),
        save: save + '%'
      });
    }

    const handle = loop(draw);
    handle.reset = () => { params.objects = 2000; params.materials = 12; };
    return handle;
  };
})();
