/* ============================================================
   Research reader — navigation, search, progress, demo mounting
   ============================================================ */
(function () {
  'use strict';

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const root = document.documentElement;
  const body = document.body;

  /* ---------------- strings ---------------- */
  const STR = window.GA_STRINGS || {};
  const LANG = root.getAttribute('data-lang') === 'en' ? 'en' : 'ru';
  const S = (key, fallback) => (STR[key] !== undefined ? STR[key] : (fallback || key));

  /* ---------------- theme ---------------- */
  const THEME_KEY = 'ga:theme';
  const themeButtons = $$('[data-theme-toggle]');
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    themeButtons.forEach((b) => {
      const label = b.querySelector('[data-theme-label]');
      if (label) label.textContent = theme === 'dark' ? S('themeLight') : S('themeDark');
      b.setAttribute('aria-label', theme === 'dark' ? S('themeToLight') : S('themeToDark'));
    });
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#08090d' : '#f4f2ea');
  }
  let stored = null;
  try { stored = localStorage.getItem(THEME_KEY); } catch (e) { /* private mode */ }
  applyTheme(stored === 'light' ? 'light' : 'dark');
  themeButtons.forEach((b) => b.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* noop */ }
  }));

  /* ---------------- language switch ---------------- */
  const LANG_KEY = 'ga:lang';
  const langLinks = $$('[data-lang-switch]');
  langLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      const target = link.getAttribute('href') || 'index.html';
      const hash = window.location.hash;
      try {
        localStorage.setItem(LANG_KEY, link.getAttribute('data-lang-switch') || LANG);
        sessionStorage.setItem('ga:lang-explicit', '1');
      } catch (err) { /* noop */ }
      if (hash) {
        e.preventDefault();
        window.location.href = target + hash;
      }
    });
  });

  // on the home page we respect the saved language choice,
  // but only if the user has not picked a language in this session
  (function honourPreferredLanguage() {
    if (LANG !== 'ru') return;                 // index.en.html always stays English
    let pref = null;
    try { pref = localStorage.getItem(LANG_KEY); } catch (e) { /* noop */ }
    if (pref !== 'en') return;
    let explicit = null;
    try { explicit = sessionStorage.getItem('ga:lang-explicit'); } catch (e) { /* noop */ }
    if (explicit) return;
    if (!/index\.html$/.test(window.location.pathname.split('/').pop() || '')) return;
    window.location.replace('index.en.html' + window.location.hash);
  })();

  /* ---------------- print ---------------- */
  $$('[data-print]').forEach((b) => b.addEventListener('click', () => window.print()));

  /* ---------------- mobile nav ---------------- */
  const menuBtn = $('[data-menu]');
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      body.classList.toggle('nav-open');
      menuBtn.setAttribute('aria-expanded', body.classList.contains('nav-open') ? 'true' : 'false');
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') body.classList.remove('nav-open');
  });

  /* ---------------- scroll progress + to top ---------------- */
  const progressBar = $('.scroll-progress');
  const toTop = $('.to-top');
  function onScroll() {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    const p = h > 0 ? Math.min(1, window.scrollY / h) : 0;
    if (progressBar) progressBar.style.width = (p * 100).toFixed(2) + '%';
    if (toTop) toTop.classList.toggle('show', window.scrollY > 900);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  /* ---------------- search + filters ---------------- */
  const topics = $$('.topic');
  const tocLinks = $$('.toc-list a');
  const appxCards = $$('.appx-card');
  const chapterBlocks = $$('.chapter-block');
  const appxSections = $$('.appx-section');
  const state = { q: '', cat: 'all', level: 'all' };
  const norm = (s) => (s || '').toLowerCase().replace(/ё/g, 'е').replace(/\s+/g, ' ');
  const searchInput = $('#site-search');
  const resultCount = $('[data-result-count]');
  const tocGroups = $$('.toc-group');

  function matches(el) {
    const d = el.dataset;
    if (state.q && !norm(d.search).includes(state.q)) return false;
    if (state.cat !== 'all' && d.cat !== state.cat) return false;
    if (state.level !== 'all' && d.level !== state.level) return false;
    return true;
  }

  function render() {
    let visible = 0;
    topics.forEach((t) => {
      const ok = matches(t);
      t.classList.toggle('is-hidden', !ok);
      if (ok) visible++;
    });
    tocLinks.forEach((a) => {
      const topic = document.getElementById(a.getAttribute('href').slice(1));
      const ok = topic ? !topic.classList.contains('is-hidden') : true;
      a.classList.toggle('is-hidden', !ok);
    });
    tocGroups.forEach((g) => {
      const any = $$('a', g).some((a) => !a.classList.contains('is-hidden'));
      g.style.display = any ? '' : 'none';
      if (any && state.q) g.open = true;
    });
    chapterBlocks.forEach((block) => {
      const any = $$('.topic', block).some((t) => !t.classList.contains('is-hidden'));
      block.style.display = any ? '' : 'none';
    });
    appxCards.forEach((c) => {
      const ok = !state.q || norm(c.dataset.search).includes(state.q);
      c.classList.toggle('is-hidden', !ok);
    });
    appxSections.forEach((s) => {
      const any = $$('.appx-card', s).some((c) => !c.classList.contains('is-hidden'));
      s.style.display = any ? '' : 'none';
    });
    const anyAppendix = appxSections.some((s) => s.style.display !== 'none');
    const appendix = $('#appendix');
    const catFilter = state.cat !== 'all' || state.level !== 'all';
    if (appendix) {
      appendix.style.display = (catFilter && !state.q) || (!anyAppendix && !!state.q) ? 'none' : '';
    }
    if (resultCount) {
      const total = topics.length;
      resultCount.textContent = (state.q || state.cat !== 'all' || state.level !== 'all')
        ? visible + ' / ' + total
        : total + ' / ' + total;
    }
    body.classList.toggle('searching', !!state.q || state.cat !== 'all' || state.level !== 'all');
    body.classList.toggle('no-matches', visible === 0 && !anyAppendix);
  }

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      state.q = norm(searchInput.value.trim());
      render();
    });
  }
  $$('[data-level]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.level = btn.dataset.level;
      $$('[data-level]').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
      render();
    });
  });
  const catSelect = $('#cat-filter');
  if (catSelect) {
    catSelect.addEventListener('change', () => {
      state.cat = catSelect.value;
      render();
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      if (searchInput) { searchInput.focus(); searchInput.select(); }
    }
    if (e.key === 'Escape' && searchInput) {
      if (document.activeElement === searchInput) {
        searchInput.value = '';
        state.q = '';
        render();
        searchInput.blur();
      }
    }
  });

  /* ---------------- active TOC link ---------------- */
  const linkByTopic = new Map();
  tocLinks.forEach((a) => linkByTopic.set(a.getAttribute('href').slice(1), a));
  const activeObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const link = linkByTopic.get(entry.target.id);
      if (!link) return;
      tocLinks.forEach((a) => a.classList.remove('is-active'));
      link.classList.add('is-active');
      const group = link.closest('details');
      if (group) group.open = true;
    });
  }, { rootMargin: '-12% 0px -72% 0px', threshold: 0 });
  topics.forEach((t) => activeObserver.observe(t));

  /* ---------------- reading progress ---------------- */
  const DONE_KEY = 'ga:done-v1';
  let done = new Set();
  try { done = new Set(JSON.parse(localStorage.getItem(DONE_KEY) || '[]')); } catch (e) { done = new Set(); }
  const progressLabel = $('[data-progress]');
  const progressTrack = $('[data-progress-bar]');

  function saveDone() {
    try { localStorage.setItem(DONE_KEY, JSON.stringify(Array.from(done))); } catch (e) { /* noop */ }
  }
  function refreshProgress() {
    const total = topics.length || 1;
    const count = topics.filter((t) => done.has(t.id)).length;
    if (progressLabel) progressLabel.textContent = count + ' / ' + total;
    if (progressTrack) progressTrack.style.width = (count / total * 100).toFixed(1) + '%';
    topics.forEach((t) => {
      const isDone = done.has(t.id);
      t.classList.toggle('is-done', isDone);
      const link = linkByTopic.get(t.id);
      if (link) link.classList.toggle('is-done', isDone);
      const btn = $('.done-btn', t);
      if (btn) {
        btn.classList.toggle('is-done', isDone);
        btn.setAttribute('aria-pressed', String(isDone));
        const label = $('span:last-child', btn);
        if (label) label.textContent = isDone ? S('done') : S('todo');
      }
    });
  }
  $$('.done-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const topic = btn.closest('.topic');
      if (!topic) return;
      if (done.has(topic.id)) done.delete(topic.id); else done.add(topic.id);
      saveDone();
      refreshProgress();
    });
  });
  refreshProgress();

  /* ---------------- copy code ---------------- */
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.copy-btn');
    if (!btn) return;
    const wrap = btn.closest('.code-wrap');
    const code = wrap && wrap.querySelector('pre code');
    if (!code) return;
    const text = code.textContent;
    const finish = (ok) => {
      btn.textContent = ok ? S('copied') : S('failed');
      btn.classList.toggle('ok', ok);
      setTimeout(() => { btn.textContent = S('copy'); btn.classList.remove('ok'); }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => finish(true)).catch(() => finish(false));
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); finish(true); } catch (err) { finish(false); }
      ta.remove();
    }
  });

  /* ---------------- close mobile nav on link ---------------- */
  $$('.toc-list a').forEach((a) => a.addEventListener('click', () => body.classList.remove('nav-open')));

  /* ---------------- demos ---------------- */
  const demoEls = $$('.demo[data-demo]');
  demoEls.forEach((el) => {
    const name = el.dataset.demo;
    const pauseBtn = el.querySelector('[data-act="pause"]');
    const resetBtn = el.querySelector('[data-act="reset"]');
    let inst = null;
    let started = false;

    function wire() {
      if (!inst) return;
      if (pauseBtn) {
        pauseBtn.addEventListener('click', () => {
          if (!inst) return;
          const paused = inst.toggle();
          pauseBtn.textContent = paused ? S('resume') : S('pause');
          pauseBtn.setAttribute('aria-pressed', String(paused));
        });
      }
      if (resetBtn) {
        resetBtn.addEventListener('click', () => {
          if (!inst) return;
          if (inst.reset) inst.reset();
          if (inst.paused && pauseBtn) {
            inst.toggle();
            pauseBtn.textContent = S('pause');
          }
        });
      }
    }

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          if (!inst && window.GA_DEMOS && window.GA_DEMOS[name]) {
            try {
              inst = window.GA_DEMOS[name](el);
              wire();
            } catch (err) {
              el.querySelector('.demo-body').innerHTML =
                '<div style="padding:16px;font:11px ui-monospace,monospace;color:#fda4af">' +
                S('demoFailed') + String(err).slice(0, 120) + '</div>';
              return;
            }
          }
          if (inst && !started) { inst.start(); started = true; }
          else if (inst) { inst.start(); }
        } else if (inst) {
          inst.stop();
        }
      });
    }, { rootMargin: '320px 0px' });
    io.observe(el);

    // lazy fallback for browsers without IntersectionObserver
    if (!('IntersectionObserver' in window)) {
      setTimeout(() => {
        if (!inst && window.GA_DEMOS && window.GA_DEMOS[name]) {
          inst = window.GA_DEMOS[name](el);
          wire();
          inst.start();
        }
      }, 600);
    }
  });

  /* ---------------- reveal on scroll ---------------- */
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.02 });
    $$('.topic, .map-card, .appx-card').forEach((el) => {
      el.classList.add('reveal');
      revealObserver.observe(el);
    });
  }

  /* ---------------- keyboard shortcut hint ---------------- */
  document.addEventListener('keydown', (e) => {
    if (e.key === 't' && (e.metaKey || e.ctrlKey) && e.shiftKey) {
      e.preventDefault();
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    }
  });
})();
