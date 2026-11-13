/* ============================================================
   Part VI — style atlas and prompt studio.
   Pure data + DOM, no dependencies. The dossier data is injected
   by tools/build.py as window.GA_STUDIO = { UI, GENRES, BALANCE,
   STYLE_GROUPS, STYLE_ATOMS, PRESETS, FORMATS, GENRE_DECISIONS }.
   ============================================================ */
(function () {
  'use strict';

  const D = window.GA_STUDIO;
  if (!D) return;
  const LANG = (window.GA_LANG === 'en') ? 'en' : 'ru';
  const UI = D.UI;                 // builder ships the table already localised
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const esc = (s) => String(s === undefined || s === null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  /* ---------------- state ---------------- */
  const state = {
    genre: null,
    balance: [],
    atoms: [],
    team: 'team_5',
    platform: 'plat_pc',
    scope: 'scope_small',
    moneta: 'mono_premium',
    format: 'pitch',
    hook: '',
    extra: '',
  };

  const MAX_BALANCE = 3;
  const MAX_ATOMS = 6;

  /* ---------------- helpers ---------------- */
  const byId = (list, id) => list.find((x) => x.id === id);
  const titleOf = (obj) => (obj && obj.title) || '';
  const nameOf = (obj) => (obj && (obj.name || obj.title)) || '';

  /* ---------------- genre + balance pickers ---------------- */
  function optionButton(item, kind) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'studio-chip';
    b.dataset.id = item.id;
    b.dataset.kind = kind;
    b.innerHTML = '<span class="t">' + esc(titleOf(item)) + '</span>' +
      '<span class="s">' + esc((item.tags || []).slice(0, 3).join(' · ')) + '</span>';
    b.addEventListener('click', () => {
      if (kind === 'genre') {
        state.genre = (state.genre === item.id) ? null : item.id;
      } else {
        const i = state.balance.indexOf(item.id);
        if (i >= 0) state.balance.splice(i, 1);
        else if (state.balance.length < MAX_BALANCE) state.balance.push(item.id);
        else state.balance.shift(), state.balance.push(item.id);
      }
      syncPickers();
      render();
    });
    return b;
  }

  function buildPickers() {
    const gBox = $('#studio-genres');
    const bBox = $('#studio-balance');
    if (gBox) {
      const groups = {};
      D.GENRES.forEach((g) => {
        (groups[g.group] = groups[g.group] || []).push(g);
      });
      Object.keys(groups).forEach((key) => {
        const head = document.createElement('div');
        head.className = 'studio-group-head';
        head.innerHTML = '<span>' + esc(key) + '</span><b>' + groups[key].length + '</b>';
        gBox.appendChild(head);
        const row = document.createElement('div');
        row.className = 'studio-chips';
        groups[key].forEach((g) => row.appendChild(optionButton(g, 'genre')));
        gBox.appendChild(row);
      });
    }
    if (bBox) {
      D.BALANCE.forEach((b) => bBox.appendChild(optionButton(b, 'balance')));
    }
  }

  function syncPickers() {
    $$('.studio-chip[data-kind="genre"]').forEach((b) => {
      b.classList.toggle('on', b.dataset.id === state.genre);
    });
    $$('.studio-chip[data-kind="balance"]').forEach((b) => {
      b.classList.toggle('on', state.balance.includes(b.dataset.id));
    });
    const n = $('#studio-balance-count');
    if (n) n.textContent = state.balance.length + ' / ' + MAX_BALANCE;
  }

  /* ---------------- style chips ---------------- */
  function buildStyle() {
    const box = $('#studio-style');
    if (!box) return;
    D.STYLE_GROUPS.forEach((group) => {
      const wrap = document.createElement('div');
      wrap.className = 'studio-style-group';
      wrap.style.setProperty('--cat', group.color);
      wrap.innerHTML = '<div class="studio-group-head"><span class="no">' + esc(group.num) +
        '</span><span>' + esc(titleOf(group)) + '</span>' +
        '<b class="atom-count" data-group="' + group.id + '">0</b></div>';
      const row = document.createElement('div');
      row.className = 'studio-chips';
      D.STYLE_ATOMS.filter((a) => a.group === group.id).forEach((atom) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'studio-chip style-chip';
        b.dataset.id = atom.id;
        b.dataset.group = group.id;
        b.title = atom.text || '';
        b.innerHTML = '<span class="t">' + esc(titleOf(atom)) + '</span>';
        b.addEventListener('click', () => {
          const i = state.atoms.indexOf(atom.id);
          if (i >= 0) state.atoms.splice(i, 1);
          else if (state.atoms.length < MAX_ATOMS) state.atoms.push(atom.id);
          else {
            // replace inside the same group first, then the oldest overall
            const same = state.atoms.findIndex((id) => {
              const a = byId(D.STYLE_ATOMS, id);
              return a && a.group === atom.group;
            });
            if (same >= 0) state.atoms.splice(same, 1);
            else state.atoms.shift();
            state.atoms.push(atom.id);
          }
          syncStyle();
          render();
        });
        row.appendChild(b);
      });
      wrap.appendChild(row);
      box.appendChild(wrap);
    });
  }

  function syncStyle() {
    $$('.style-chip').forEach((b) => b.classList.toggle('on', state.atoms.includes(b.dataset.id)));
    $$('.atom-count').forEach((el) => {
      const n = state.atoms.filter((id) => {
        const a = byId(D.STYLE_ATOMS, id);
        return a && a.group === el.dataset.group;
      }).length;
      el.textContent = n;
    });
    const n = $('#studio-style-count');
    if (n) n.textContent = state.atoms.length + ' / ' + MAX_ATOMS;
  }

  /* ---------------- constraints ---------------- */
  function buildSelect(sel, options, key) {
    const el = $(sel);
    if (!el) return;
    // the builder already ships localised <option>s; JS only fills a gap
    if (!el.options.length) {
      options.forEach((opt) => {
        const o = document.createElement('option');
        o.value = opt;
        o.textContent = UI[opt] || opt;
        el.appendChild(o);
      });
    }
    state[key] = el.value || options[0];
    el.value = state[key];
    el.addEventListener('change', () => { state[key] = el.value; render(); });
  }

  /* ---------------- prompt assembly ---------------- */
  function pick(list) {
    return list[Math.floor(Math.random() * list.length)];
  }

  function compose() {
    const genre = state.genre ? byId(D.GENRES, state.genre) : null;
    if (!genre) return '';
    const T = UI.section_templates;
    const fmtItems = UI.formats[state.format] || UI.formats.pitch;
    const fmtName = nameOf(D.FORMATS.find((f) => f.id === state.format)) || state.format;

    const blocks = [];
    blocks.push(T.genre
      .replace('{title}', titleOf(genre))
      .replace('{summary}', genre.summary || '')
      .replace('{loop}', genre.loop || '')
      .replace('{session}', (genre.session || '').replace(/^(session|сессия)\s*/i, ''))
      .replace('{pacing}', genre.pacing || ''));

    if (state.balance.length) {
      blocks.push(T.balance.replace('{items}', state.balance.map((id) => {
        const b = byId(D.BALANCE, id);
        return b ? T.balance_item
          .replace('{title}', titleOf(b))
          .replace('{summary}', b.summary || '') : '';
      }).filter(Boolean).join('\n')));
    }

    if (state.atoms.length) {
      blocks.push(T.art.replace('{items}', state.atoms.map((id) => {
        const a = byId(D.STYLE_ATOMS, id);
        const g = a ? byId(D.STYLE_GROUPS, a.group) : null;
        return a && g ? T.art_item
          .replace('{group}', titleOf(g))
          .replace('{text}', a.text || titleOf(a)) : '';
      }).filter(Boolean).join('\n')));
    }

    blocks.push(T.constraints
      .replace('{team}', UI[state.team] || state.team)
      .replace('{platform}', UI[state.platform] || state.platform)
      .replace('{scope}', UI[state.scope] || state.scope)
      .replace('{monetisation}', UI[state.moneta] || state.moneta));

    if (state.hook) blocks.push(T.hook.replace('{text}', state.hook));
    if (state.extra) blocks.push(T.extra.replace('{text}', state.extra));

    const deliverable = T.deliverable
      .replace('{name}', fmtName)
      .replace('{items}', fmtItems.map((i) => '- ' + i).join('\n'));

    return UI.prompt_template
      .replace('{sections}', blocks.join('\n\n'))
      .replace('{deliverable}', deliverable);
  }

  /* ---------------- rendering ---------------- */
  function render() {
    syncPickers();
    syncStyle();
    const out = $('#studio-prompt');
    const meta = $('#studio-meta');
    if (!out) return;
    const body = compose();
    if (!body) {
      out.textContent = UI.empty;
      out.classList.add('is-empty');
      if (meta) meta.textContent = '';
      return;
    }
    out.classList.remove('is-empty');
    out.textContent = body;
    if (meta) {
      meta.textContent = UI.counter + ': ' +
        (state.genre ? 1 : 0) + ' ' + UI.labels.genre.toLowerCase() + ' · ' +
        state.balance.length + ' ' + UI.labels.balance.toLowerCase() + ' · ' +
        state.atoms.length + ' ' + UI.atlas_title.toLowerCase();
    }
  }

  /* ---------------- presets ---------------- */
  function buildPresets() {
    const cards = $$('.studio-preset[data-preset]');
    if (!cards.length) return;
    cards.forEach((card) => {
      card.addEventListener('click', () => {
        const p = byId(D.PRESETS, card.dataset.preset);
        if (!p) return;
        state.genre = p.genre;
        state.balance = p.balance.slice(0, MAX_BALANCE);
        state.atoms = p.atoms.slice(0, MAX_ATOMS);
        syncPickers();
        render();
        const target = $('#studio-composer');
        if (target && target.scrollIntoView) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  /* ---------------- filter over the whole composer ---------------- */
  function wireFilter() {
    const input = $('#studio-filter');
    if (!input) return;
    const norm = (s) => (s || '').toLowerCase().replace(/ё/g, 'е').replace(/\s+/g, ' ');
    input.addEventListener('input', () => {
      const q = norm(input.value.trim());
      $$('.studio-chip').forEach((chip) => {
        const hay = norm(chip.dataset.id + ' ' + chip.textContent + ' ' + (chip.title || ''));
        chip.classList.toggle('is-muted', !!q && !hay.includes(q));
      });
      $$('.studio-style-group').forEach((g) => {
        const any = $$('.style-chip', g).some((c) => !c.classList.contains('is-muted'));
        g.style.display = any ? '' : 'none';
      });
    });
  }

  /* ---------------- actions ---------------- */
  function wireActions() {
    const copy = $('#studio-copy');
    if (copy) {
      copy.addEventListener('click', () => {
        const out = $('#studio-prompt');
        const textToCopy = out ? out.textContent : '';
        if (!textToCopy) return;
        const done = () => {
          copy.textContent = UI.copied;
          setTimeout(() => { copy.textContent = UI.copy; }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(textToCopy).then(done).catch(done);
        } else {
          const ta = document.createElement('textarea');
          ta.value = textToCopy;
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand('copy'); } catch (e) { /* noop */ }
          ta.remove();
          done();
        }
      });
    }

    const dl = $('#studio-download');
    if (dl) {
      dl.addEventListener('click', () => {
        const out = $('#studio-prompt');
        const body = out ? out.textContent : '';
        if (!body) return;
        const blob = new Blob([body], { type: 'text/markdown;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'game-prompt.md';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
      });
    }

    const reset = $('#studio-reset');
    if (reset) {
      reset.addEventListener('click', () => {
        state.genre = null;
        state.balance = [];
        state.atoms = [];
        state.hook = '';
        state.extra = '';
        const h = $('#studio-hook');
        const e = $('#studio-extra');
        if (h) h.value = '';
        if (e) e.value = '';
        render();
      });
    }

    const rnd = $('#studio-random');
    if (rnd) {
      rnd.addEventListener('click', () => {
        const g = pick(D.GENRES);
        state.genre = g.id;
        const bal = D.BALANCE.slice().sort(() => Math.random() - 0.5).slice(0, 3).map((b) => b.id);
        state.balance = bal;
        const atoms = [];
        D.STYLE_GROUPS.forEach((group) => {
          const pool = D.STYLE_ATOMS.filter((a) => a.group === group.id);
          if (pool.length && atoms.length < MAX_ATOMS) atoms.push(pick(pool).id);
        });
        state.atoms = atoms;
        render();
      });
    }

    ['studio-hook', 'studio-extra'].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('input', () => {
        if (id === 'studio-hook') state.hook = el.value.trim();
        else state.extra = el.value.trim();
        render();
      });
    });
  }

  /* ---------------- boot ---------------- */
  function boot() {
    buildPickers();
    buildStyle();
    buildPresets();
    buildSelect('#studio-team', ['team_1', 'team_5', 'team_20', 'team_100'], 'team');
    buildSelect('#studio-platform', ['plat_pc', 'plat_web', 'plat_mobile', 'plat_console'], 'platform');
    buildSelect('#studio-scope', ['scope_jam', 'scope_small', 'scope_full', 'scope_live'], 'scope');
    buildSelect('#studio-moneta', ['mono_premium', 'mono_f2p', 'mono_none'], 'moneta');
    buildSelect('#studio-format', D.FORMATS.map((f) => f.id), 'format');
    wireActions();
    wireFilter();
    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
