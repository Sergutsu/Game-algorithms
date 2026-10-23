#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает двуязычные HTML-документы из research/*.py + assets/*.

Запуск:  python3 tools/build.py
Выход:   index.html          — русская версия (точка входа GitHub Pages)
          index.en.html       — английская версия
          game-algorithms-research.html — копия русской версии (старые ссылки)
"""

import html
import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from topics_1 import TOPICS_1  # noqa: E402
from topics_2 import TOPICS_2  # noqa: E402
from topics_3 import TOPICS_3  # noqa: E402
from topics_4 import TOPICS_4  # noqa: E402
from topics_5 import TOPICS_5, APPENDIX  # noqa: E402
from topics_6 import TOPICS_6  # noqa: E402
from topics_7 import TOPICS_7  # noqa: E402
from i18n import (  # noqa: E402
    CATS, CHAPTER_ORDER, DEMO_TITLES, GLOSSARY, LEVEL_LABEL,
    LEVELS_HINT, STRINGS,
)

RU_TOPICS = TOPICS_1 + TOPICS_2 + TOPICS_3 + TOPICS_4 + TOPICS_5 + TOPICS_6 + TOPICS_7

# английские версии подключаются опционально: если файла нет — остаётся русский текст
EN_TOPICS = []
for _mod in ("topics_en_1", "topics_en_2", "topics_en_3",
             "topics_en_4", "topics_en_5", "topics_en_6", "topics_en_7"):
    try:
        _m = importlib.import_module(_mod)
    except ImportError:
        continue
    EN_TOPICS.extend(getattr(_m, "TOPICS_EN_" + _mod.split("_")[-1], []))

try:
    from appendix_en import APPENDIX_EN
except ImportError:
    APPENDIX_EN = []

try:
    from codes_en import CODE_EN
except ImportError:
    CODE_EN = {}

CHAPTER_OVERRIDES = {
    "terrain": "gfx", "gi": "gfx", "destruction": "gfx", "water": "gfx", "clouds": "gfx",
    "textures": "shaders", "distortion": "shaders", "optics": "shaders",
}

TEXT_FIELDS = ("title", "tags", "summary", "detail", "formula", "steps",
               "complexity", "pitfalls", "games")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def esc(text):
    return html.escape(str(text), quote=False)


def attr(text):
    return html.escape(str(text), quote=True)


def strip_tags(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def cat_of(topic):
    return CHAPTER_OVERRIDES.get(topic["id"], topic["cat"])


def S(key, lang, **kw):
    """Строка интерфейса на нужном языке с подстановкой {placeholders}."""
    text = STRINGS.get(key, {}).get(lang, STRINGS.get(key, {}).get("ru", key))
    if kw:
        text = text.format(**kw)
    return text


def merge_topics(ru_list, en_list):
    """Сливает английские тексты в русские записи (структура — из RU)."""
    by_id = {t["id"]: t for t in en_list}
    merged = []
    for ru in ru_list:
        en = by_id.get(ru["id"])
        topic = dict(ru)
        if en:
            for field in TEXT_FIELDS:
                if field in en and en[field]:
                    topic[field] = en[field]
            if en.get("code"):
                topic["code"] = en["code"]
            elif ru["id"] in CODE_EN:
                topic["code"] = CODE_EN[ru["id"]]
            if en.get("en"):
                topic["en"] = en["en"]
        merged.append(topic)
    return merged


def build_chapters(topics):
    """Разделы собираются по фиксированному порядку категорий, темы — по номеру."""
    chapters = []
    for cat in CHAPTER_ORDER:
        items = sorted([t for t in topics if cat_of(t) == cat], key=lambda t: t["n"])
        if items:
            chapters.append((cat, items))
    return chapters


KEYWORDS = {
    "python": ("and as assert break class continue def del elif else except finally for from "
               "global if import in is lambda None nonlocal not or pass raise return True False "
               "try while with yield self"),
    "csharp": ("public private protected internal static readonly struct class void int float "
               "bool double var new return if else for foreach while in null true false "
               "override virtual abstract string const using namespace this get set "
               "Vector2 Vector3 Matrix4x4 Quaternion Mathf Debug"),
    "glsl": ("float vec2 vec3 vec4 mat3 mat4 int bool void return if else for while "
             "uniform varying attribute in out const true false sampler2D texture "
             "normalize mix clamp dot cross length pow exp smoothstep sin cos "
             "layout binding buffer struct atomicAdd memoryBarrier workgroup "
             "compute fragment vertex main readonly writeonly local_size_x"),
    "wgsl": ("fn let var const struct array return if else for while loop break continue "
             "discard true false u32 i32 f32 vec2 vec3 vec4 mat4x4 storage uniform "
             "read write read_write compute vertex fragment workgroup_size "
             "builtin global_invocation_id local_invocation_id"),
}


def highlight(code, lang):
    """Простое, но аккуратное раскрашивание без внешних зависимостей."""
    text = html.escape(code, quote=False)
    words = KEYWORDS.get(lang, "")
    kw = r"\b(?:" + r"|".join(re.split(r"\s+", words)) + r")\b" if words else r"(?!x)x"
    if lang == "python":
        comment = r"#[^\n]*"
    else:
        comment = r"//[^\n]*|/\*[\s\S]*?\*/"
    pattern = re.compile(
        r"(?P<c>" + comment + r")"
        r"|(?P<s>&quot;.*?&quot;|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
        r"|(?P<n>\b\d+(?:\.\d+)?\b)"
        r"|(?P<k>" + kw + r")"
    )

    def repl(m):
        if m.group("c"):
            return '<span class="c">' + m.group("c") + "</span>"
        if m.group("s"):
            return '<span class="s">' + m.group("s") + "</span>"
        if m.group("n"):
            return '<span class="n">' + m.group("n") + "</span>"
        return '<span class="k">' + m.group("k") + "</span>"

    return pattern.sub(repl, text)


def level_dots(level, color, lang="ru"):
    dots = "".join(
        '<i class="on" style="background:%s"></i>' % color if i < level else "<i></i>"
        for i in range(3)
    )
    aria = S("level_of", lang, n=level)
    return '<span class="level" aria-label="%s">%s</span>' % (attr(aria), dots)


def demo_block(name, color, lang):
    title = DEMO_TITLES.get(name, {}).get(lang, DEMO_TITLES.get(name, {}).get("ru", ""))
    return f'''
        <figure class="demo" data-demo="{name}" style="--cat:{color}">
          <div class="demo-bar">
            <span class="live">{esc(S("live", lang))}</span>
            <span>{esc(title)}</span>
            <span class="spacer"></span>
            <button type="button" data-act="pause" aria-pressed="false">{esc(S("pause", lang))}</button>
            <button type="button" data-act="reset">{esc(S("reset", lang))}</button>
          </div>
          <div class="demo-body"></div>
        </figure>'''


def render_topic(t, total, lang):
    cat = cat_of(t)
    name, _desc = CATS[cat][lang]
    color = CATS[cat]["color"]
    n = t["n"]
    tags = "".join(f'<span class="tag">{esc(x)}</span>' for x in t["tags"])
    detail = "".join(f"<p>{p}</p>" for p in t["detail"])
    formula, fnote = t["formula"]
    steps = "".join(f"<li>{s}</li>" for s in t["steps"])
    lang_label = {"python": "Python", "csharp": "C#", "glsl": "GLSL",
                  "wgsl": "WGSL"}.get(t["code"][0], t["code"][0])
    cx = t["complexity"]
    pitfalls = "".join(f"<li>{p}</li>" for p in t["pitfalls"])
    games = "".join(f'<span class="game-pill">{esc(g)}</span>' for g in t["games"])
    search = strip_tags(" ".join([
        t["title"], t["en"], " ".join(t["tags"]), t["summary"],
        " ".join(t["detail"]), " ".join(t["steps"]), " ".join(t["pitfalls"]),
        " ".join(t["games"]), name, LEVEL_LABEL[t["level"]][lang],
    ]))
    demo = demo_block(t["demo"], color, lang) if t.get("demo") else ""
    en_title = t["en"] if lang == "en" else ""

    return f'''
      <article class="topic" id="{t['id']}" data-cat="{cat}" data-level="{t['level']}"
               data-search="{attr(search)}" style="--cat:{color}">
        <header class="topic-head">
          <div class="topic-num" aria-hidden="true">{n:02d}</div>
          <div class="topic-titles">
            <div class="topic-meta">
              <span class="cat">{esc(name)}</span>
              <span class="dot"></span>
              <span>{esc(S("topic_of", lang, n="%02d" % n, total=total))}</span>
              <span class="dot"></span>
              {level_dots(t['level'], color, lang)}
              <span>{esc(LEVEL_LABEL[t['level']][lang])}</span>
            </div>
            <h3>{esc(t["title"])}</h3>
            <div class="en">{esc(en_title or t["en"])}</div>
          </div>
        </header>

        <p class="lead">{esc(t["summary"])}</p>
        <div class="tag-row">{tags}</div>

        <div class="block-label"><b>01</b> {esc(S("block_essence", lang))}</div>
        <div class="prose">{detail}</div>

        <div class="formula">
          <span class="f-label">{esc(S("formula_label", lang))}</span>
          <div class="f-main">{formula}</div>
          <div class="f-note">{fnote}</div>
        </div>

        <div class="block-label"><b>02</b> {esc(S("block_build", lang))}</div>
        <ol class="steps">{steps}</ol>

        <div class="block-label"><b>03</b> {esc(S("block_code", lang))}</div>
        <div class="code-wrap">
          <div class="code-bar">
            <span class="dots"><i></i><i></i><i></i></span>
            <span class="lang">{lang_label}</span>
            <button class="copy-btn" type="button">{esc(S("copy", lang))}</button>
          </div>
          <pre><code>{highlight(t['code'][1], t['code'][0])}</code></pre>
        </div>

        <div class="block-label"><b>04</b> {esc(S("block_complexity", lang))}</div>
        <div class="complexity">
          <div class="cx"><div class="k">{esc(S("cx_time", lang))}</div><div class="v">{cx[0]}</div></div>
          <div class="cx"><div class="k">{esc(S("cx_memory", lang))}</div><div class="v">{cx[1]}</div></div>
          <div class="cx"><div class="k">{esc(S("cx_practice", lang))}</div><div class="v">{cx[2]}</div></div>
        </div>

        <div class="block-label"><b>05</b> {esc(S("block_pitfalls", lang))}</div>
        <ul class="pitfalls">{pitfalls}</ul>

        <div class="block-label"><b>06</b> {esc(S("block_games", lang))}</div>
        <div class="games-row"><span class="lbl">{esc(S("block_games", lang))}</span>{games}</div>
        {demo}

        <button class="done-btn" type="button" aria-pressed="false">
          <span class="box" aria-hidden="true"></span><span>{esc(S("done_label", lang))}</span>
        </button>
      </article>'''


# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------

def build_page(lang, topics, appendix, css, js):
    chapters = build_chapters(topics)
    total = len(topics)
    counts = {}
    for t in topics:
        counts[cat_of(t)] = counts.get(cat_of(t), 0) + 1

    # sidebar table of contents
    toc = []
    for idx, (cat, items) in enumerate(chapters, 1):
        name, _ = CATS[cat][lang]
        color = CATS[cat]["color"]
        links = "".join(
            f'<li><a href="#{t["id"]}" data-cat="{cat}" data-level="{t["level"]}">'
            f'<span class="no">{t["n"]:02d}</span><span>{esc(t["title"])}</span></a></li>'
            for t in items
        )
        toc.append(f'''
        <details class="toc-group"{" open" if idx <= 2 else ""}>
          <summary>
            <span class="swatch" style="background:{color}"></span>
            <span>{esc(name)}</span>
            <span class="count">{len(items):02d}</span>
          </summary>
          <ul class="toc-list">{links}</ul>
        </details>''')

    cat_options = "".join(
        f'<option value="{cid}">{esc(CATS[cid][lang][0])} · {counts[cid]}</option>'
        for cid in CHAPTER_ORDER if counts.get(cid)
    )

    # knowledge map + chapters
    map_cards = []
    for idx, (cat, items) in enumerate(chapters, 1):
        name, desc = CATS[cat][lang]
        color = CATS[cat]["color"]
        first, last = items[0]["n"], items[-1]["n"]
        rng = f"{first:02d}" if first == last else f"{first:02d}–{last:02d}"
        map_cards.append(f'''
        <a class="map-card" href="#chapter-{idx}" style="--cat:{color}">
          <div class="top">
            <span class="name">{esc(name)}</span>
            <span class="n">{rng}</span>
          </div>
          <p>{esc(desc)}</p>
          <div class="bar" style="background:linear-gradient(90deg,{color},{color}00)"></div>
        </a>''')

    chapter_html = []
    for idx, (cat, items) in enumerate(chapters, 1):
        name, _ = CATS[cat][lang]
        color = CATS[cat]["color"]
        body = "".join(render_topic(t, total, lang) for t in items)
        chapter_html.append(f'''
    <section class="chapter-block" id="chapter-{idx}" data-chapter="{cat}" style="--cat:{color}">
      <div class="chapter">
        <span class="idx">{esc(S("chapter_label", lang, i="%02d" % idx, n=len(chapters)))}</span>
        <h3>{esc(name)}</h3>
        <span class="rule"></span>
        <span class="idx">{esc(S("chapter_topics", lang, n="%02d" % len(items)))}</span>
      </div>
      {body}
    </section>''')

    # appendix
    appx_html = []
    for section, cards in appendix:
        cards_html = "".join(f'''
        <article class="appx-card" data-search="{attr(strip_tags(' '.join([c[0], c[1], c[2], c[3], c[4], section])))}">
          <h5>{esc(c[0])}</h5>
          <div class="sub">{esc(c[1])}</div>
          <p>{esc(c[2])}</p>
          <div class="foot"><span class="ref">{esc(c[3])}</span></div>
          <div class="note">{esc(c[4])}</div>
        </article>''' for c in cards)
        appx_html.append(f'''
      <div class="appx-section">
        <h4><span>{esc(section)}</span><span class="bar"></span></h4>
        <div class="appx-grid">{cards_html}</div>
      </div>''')

    glossary = "".join(
        f'<div class="gloss-row"><dt>{esc(g[lang][0])}</dt><dd>{esc(g[lang][1])}</dd></div>'
        for g in GLOSSARY
    )

    demo_count = len({t["demo"] for t in topics if t.get("demo")})
    appx_count = sum(len(cards) for _, cards in appendix)
    total_formulas = len(topics)
    other_lang = "en" if lang == "ru" else "ru"
    other_file = "index.en.html" if lang == "ru" else "index.html"

    head_script = """<script>
      (function () {
        try {
          var t = localStorage.getItem('ga:theme');
          if (t === 'light') document.documentElement.setAttribute('data-theme', 'light');
        } catch (e) {}
      })();
    </script>"""

    doc = f'''<!DOCTYPE html>
<html lang="{lang}" data-theme="dark" data-lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#08090d">
<meta name="description" content="{attr(S('meta_desc', lang, n=total))}">
<title>{'Алгоритмы игр — полное исследование' if lang == 'ru' else 'Game Algorithms — the full research'} · {total} {('тем' if lang == 'ru' else 'topics')}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%2308090d'/%3E%3Cpath d='M16 5l9.5 5.5v11L16 27l-9.5-5.5v-11z' fill='none' stroke='%23c8f751' stroke-width='2'/%3E%3Ccircle cx='16' cy='16' r='3' fill='%23c8f751'/%3E%3C/svg%3E">
<link rel="alternate" hreflang="ru" href="index.html">
<link rel="alternate" hreflang="en" href="index.en.html">
<link rel="alternate" hreflang="x-default" href="index.html">
{head_script}
<style>
{css}
</style>
</head>
<body>
<a class="skip-link" href="#start">{esc(S("skip", lang))}</a>
<noscript>
  <p style="margin:0;padding:10px 16px;background:#c8f751;color:#101404;font:13px/1.5 system-ui,sans-serif">
    {esc(S("noscript", lang))}
  </p>
</noscript>
<div class="scroll-progress" aria-hidden="true"></div>

<div class="topbar">
  <button class="icon-btn menu-btn" type="button" data-menu aria-expanded="false" aria-label="{attr(S("menu_aria", lang))}">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
  </button>
  <a class="brand" href="#top">
    <span class="mark" aria-hidden="true"></span>
    <span>Game Algorithms<small>{esc(S("brand_small", lang))}</small></span>
  </a>
  <span class="topbar-spacer"></span>
  <nav class="topbar-links" aria-label="{attr(S("nav_overview", lang))}">
    <a href="#start">{esc(S("nav_overview", lang))}</a>
    <a href="#map">{esc(S("nav_map", lang))}</a>
    <a href="#appendix">{esc(S("nav_practice", lang))}</a>
    <a href="#glossary">{esc(S("nav_glossary", lang))}</a>
  </nav>
  <a class="icon-btn lang-btn" href="{other_file}" data-lang-switch="{other_lang}" hreflang="{other_lang}"
     aria-label="{attr(S("lang_other_aria", lang))}" title="{attr(S("lang_note", lang))}">
    <span>{esc(S("lang_other_short", lang))}</span>
  </a>
  <button class="icon-btn" type="button" data-print aria-label="{attr(S("print_aria", lang))}" title="{attr(S("print_aria", lang))}">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 9V4h10v5M7 18H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2"/><rect x="7" y="14" width="10" height="7" rx="1"/></svg>
    <span class="print-label">{esc(S("print_label", lang))}</span>
  </button>
  <button class="icon-btn" type="button" data-theme-toggle>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6l1.4 1.4m10 10 1.4 1.4m0-12.8-1.4 1.4m-10 10-1.4 1.4"/><circle cx="12" cy="12" r="4"/></svg>
    <span data-theme-label>{esc(S("theme_light", lang))}</span>
  </button>
</div>

<header class="hero" id="top">
  <div class="hero-grid">
    <div>
      <span class="eyebrow">{esc(S("eyebrow", lang))}</span>
      <h1>{esc(S("hero_title_1", lang))}<br>{esc(S("hero_title_2", lang))}<em>{esc(S("hero_title_emph", lang))}</em></h1>
      <p class="lede">
        {esc(S("hero_lede", lang, n=total))}
      </p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#start">
          {esc(S("hero_start", lang))}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </a>
        <a class="btn" href="#appendix">{esc(S("hero_tasks", lang, n=appx_count))}</a>
      </div>
    </div>
    <aside class="hero-side" aria-label="{attr(S("hero_side_aria", lang))}">
      <div class="stat"><div class="num">{total}<i>.</i></div><div class="cap">{esc(S("stat_topics", lang, n=len(chapters)))}</div></div>
      <div class="stat"><div class="num">{demo_count}<i>×</i></div><div class="cap">{esc(S("stat_demos", lang))}</div></div>
      <div class="stat"><div class="num">{appx_count}<i>+</i></div><div class="cap">{esc(S("stat_tasks", lang))}</div></div>
      <div class="stat"><div class="num">0<i>.</i></div><div class="cap">{esc(S("stat_deps", lang))}</div></div>
    </aside>
  </div>
</header>

<div class="shell">
  <aside class="sidebar" aria-label="{attr(S("side_aria", lang))}">
    <div class="side-head"><span>{esc(S("side_content", lang))}</span><b data-result-count>{total} / {total}</b></div>

    <div class="search-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input id="site-search" type="search" placeholder="{attr(S("search_placeholder", lang))}" autocomplete="off" aria-label="{attr(S("search_aria", lang))}">
      <kbd>/</kbd>
    </div>

    <div class="chip-row" role="group" aria-label="{attr(S("level_filter_aria", lang))}">
      <button class="chip" type="button" data-level="all" aria-pressed="true">{esc(S("level_all", lang))}</button>
      <button class="chip" type="button" data-level="1" aria-pressed="false">{esc(S("level_1", lang))}</button>
      <button class="chip" type="button" data-level="2" aria-pressed="false">{esc(S("level_2", lang))}</button>
      <button class="chip" type="button" data-level="3" aria-pressed="false">{esc(S("level_3", lang))}</button>
    </div>

    <div class="search-wrap" style="margin-bottom:16px">
      <select id="cat-filter" aria-label="{attr(S("cat_aria", lang))}" style="width:100%;padding:9px 10px;background:var(--panel);border:1px solid var(--line);border-radius:10px;color:var(--ink);font-size:12px;outline:none">
        <option value="all">{esc(S("cat_all", lang, n=total))}</option>
        {cat_options}
      </select>
    </div>

    <div class="side-head" style="margin-top:4px">
      <span>{esc(S("progress", lang))}</span><b data-progress>0 / {total}</b>
    </div>
    <div style="height:3px;background:var(--line);border-radius:99px;overflow:hidden;margin-bottom:16px">
      <div data-progress-bar style="height:100%;width:0;background:linear-gradient(90deg,var(--acid),var(--mint));transition:width .3s"></div>
    </div>

    <div class="side-head"><span>{esc(S("sections", lang))}</span><b>{len(chapters)}</b></div>
    {''.join(toc)}

    <div class="side-foot">
      {esc(S("side_foot", lang))}
    </div>
  </aside>

  <main class="content" id="main">
    <div class="content-inner">

      <section class="section-intro" id="start">
        <h2>{esc(S("how_title", lang))}</h2>
        <p>
          {esc(S("how_p", lang))}
        </p>

        <div class="callout">
          <span class="ico">→</span>
          <div>
            <b>{esc(S("block_essence", lang))}.</b> {esc(S("callout_structure", lang))}
          </div>
        </div>

        <div class="map-grid" id="map">
          {''.join(map_cards)}
        </div>

        <div class="callout">
          <span class="ico">✦</span>
          <div>
            <b>{esc(S("level_all", lang).capitalize())}.</b> {esc(S("callout_levels", lang))}
          </div>
        </div>

        <div class="callout">
          <span class="ico">◎</span>
          <div>
            <b>{esc(S("nav_map", lang))}.</b> {esc(S("callout_coverage", lang))}
          </div>
        </div>
      </section>
      {''.join(chapter_html)}

      <section class="appendix" id="appendix">
        <div class="chapter">
          <span class="idx">{esc(S("appendix_label", lang))}</span>
          <h3>{esc(S("appendix_title", lang, n=appx_count))}</h3>
          <span class="rule"></span>
          <span class="idx">{esc(S("appendix_hint", lang))}</span>
        </div>
        <p class="section-intro" style="padding-top:18px">
          {esc(S("appendix_intro", lang))}
        </p>
        {''.join(appx_html)}
      </section>

      <section class="appendix" id="glossary">
        <div class="chapter">
          <span class="idx">{esc(S("glossary_label", lang))}</span>
          <h3>{esc(S("glossary_title", lang))}</h3>
          <span class="rule"></span>
          <span class="idx">{esc(S("glossary_hint", lang, n=len(GLOSSARY)))}</span>
        </div>
        <p class="section-intro" style="padding-top:18px">
          {esc(S("glossary_intro", lang))}
        </p>
        <dl class="glossary">{glossary}</dl>
      </section>

      <section class="section-intro" id="method" style="border-top:1px solid var(--line);margin-top:44px">
        <h2>{esc(S("method_title", lang))}</h2>
        <p>{esc(S("method_p1", lang))}</p>
        <p style="margin-top:12px">{esc(S("method_p2", lang))}</p>
      </section>
    </div>
  </main>
</div>

<footer class="footer">
  <div class="footer-inner">
    <div>
      <h3>{esc(S("footer_title", lang))}</h3>
      <p>{esc(S("footer_p1", lang))}</p>
      <p>{esc(S("footer_p2", lang))}</p>
      <p class="fine">{esc(S("footer_fine", lang, n=total, demos=demo_count, tasks=appx_count, formulas=total_formulas))}</p>
    </div>
    <nav class="footer-links" aria-label="{attr(S("footer_link_how", lang))}">
      <a href="#start">{esc(S("footer_link_how", lang))} <span>↑</span></a>
      <a href="#map">{esc(S("footer_link_map", lang))} <span>→</span></a>
      <a href="#appendix">{esc(S("footer_link_tasks", lang))} <span>→</span></a>
      <a href="#glossary">{esc(S("footer_link_gloss", lang))} <span>→</span></a>
      <a href="README.md">{esc(S("footer_link_readme", lang))} <span>↗</span></a>
      <a href="VectorMath.html">{esc(S("footer_link_vector", lang))} <span>↗</span></a>
      <a href="Hanoi-Tower-solver.md">{esc(S("footer_link_hanoi", lang))} <span>↗</span></a>
      <a href="asteroids.html">{esc(S("footer_link_asteroids", lang))} <span>↗</span></a>
    </nav>
  </div>
</footer>

<button class="to-top" type="button" aria-label="{attr(S("to_top_aria", lang))}">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M6 11l6-6 6 6"/></svg>
</button>

<script>
window.GA_LANG = "{lang}";
window.GA_STRINGS = {{
  copy: "{esc(S("copy", lang))}",
  copied: "{esc(S("copied", lang))}",
  failed: "{esc(S("copy_failed", lang))}",
  done: "{esc(S("done_done", lang))}",
  todo: "{esc(S("done_label", lang))}",
  pause: "{esc(S("pause", lang))}",
  resume: "{esc(S("resume", lang))}",
  themeLight: "{esc(S("theme_light", lang))}",
  themeDark: "{esc(S("theme_dark", lang))}",
  themeToLight: "{esc(S("theme_to_light", lang))}",
  themeToDark: "{esc(S("theme_to_dark", lang))}",
  demoFailed: "{esc(S("demo_failed", lang))}"
}};
</script>
<script>
{js}
</script>
</body>
</html>
'''
    return doc


def extract_js_object(text, marker):
    """Вырезает объектный литерал из JS по маркеру (скобки считаются)."""
    i = text.index(marker)
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j:k + 1]
    raise ValueError("не найден конец объекта: " + marker)


def labels_runtime(labels_js, lang):
    """Только таблица нужного языка — чтобы в EN-страницу не попадал русский текст."""
    marker = "TABLES.ru = " if lang == "ru" else "TABLES.en = "
    table = extract_js_object(labels_js, marker)
    return (
        "(function(){var T={};T.%(lang)s=%(table)s;"
        "var l=(typeof window!=='undefined'&&window.GA_LANG==='en')?'en':'ru';"
        "var t=T[l]||T.%(lang)s||{};"
        "window.GA_LABELS=T;"
        "window.GA_T=function(k){return t[k]!==undefined?t[k]:k};})();"
    ) % {"lang": lang, "table": table}


def build():
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    labels_js = (ROOT / "assets" / "labels.js").read_text(encoding="utf-8")
    demos_js = "\n".join([
        (ROOT / "assets" / "demos-a.js").read_text(encoding="utf-8"),
        (ROOT / "assets" / "demos-b.js").read_text(encoding="utf-8"),
        (ROOT / "assets" / "demos-c.js").read_text(encoding="utf-8"),
        (ROOT / "assets" / "app.js").read_text(encoding="utf-8"),
    ])

    en_topics = merge_topics(RU_TOPICS, EN_TOPICS)
    appendix_en = list(zip([s for s, _ in APPENDIX], [c for _, c in APPENDIX]))
    if APPENDIX_EN:
        appendix_en = []
        for i, (section, cards) in enumerate(APPENDIX):
            en_cards = APPENDIX_EN[i][1] if i < len(APPENDIX_EN) else cards
            appendix_en.append((APPENDIX_EN[i][0] if i < len(APPENDIX_EN) else section, en_cards))
    else:
        appendix_en = APPENDIX

    outputs = {
        "index.html": build_page("ru", RU_TOPICS, APPENDIX, css,
                                 labels_runtime(labels_js, "ru") + "\n" + demos_js),
        "index.en.html": build_page("en", en_topics, appendix_en, css,
                                    labels_runtime(labels_js, "en") + "\n" + demos_js),
    }
    # старый адрес остаётся рабочим
    outputs["game-algorithms-research.html"] = outputs["index.html"]

    for name, doc in outputs.items():
        out = ROOT / name
        out.write_text(doc, encoding="utf-8")
        size_kb = out.stat().st_size / 1024
        print(f"собрано: {name}  ({size_kb:.0f} KB)")

    demo_count = len({t["demo"] for t in RU_TOPICS if t.get("demo")})
    appx_count = sum(len(cards) for _, cards in APPENDIX)
    missing_en = [t["id"] for t in RU_TOPICS if t["id"] not in {e["id"] for e in EN_TOPICS}]
    print(f"тем: {len(RU_TOPICS)}, разделов: {len(CHAPTER_ORDER)}, демо: {demo_count}, задач: {appx_count}")
    if missing_en:
        print(f"без английского перевода: {len(missing_en)} → {', '.join(missing_en[:12])}"
              f"{' …' if len(missing_en) > 12 else ''}")
    return outputs


if __name__ == "__main__":
    build()
