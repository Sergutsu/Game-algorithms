#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает автономный HTML-документ из research/*.py + assets/*.

Запуск:  python3 tools/build.py
Выход:   game-algorithms-research.html  (один файл, без внешних зависимостей)
"""

import html
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

TOPICS = TOPICS_1 + TOPICS_2 + TOPICS_3 + TOPICS_4 + TOPICS_5

CATS = {
    "mechanics": ("Геймплейные механики", "#c8f751",
                  "Баллистика, урон, рынки, кривые и квантовые состояния: как правила превращаются в ощущения."),
    "ai": ("Искусственный интеллект", "#7dd3fc",
           "Решения, эмоции, адаптивная сложность, диалоги и роевое поведение."),
    "gfx": ("Компьютерная графика", "#fbbf6b",
            "Террейн, глобальное освещение, разрушения, вода и объёмные облака."),
    "network": ("Сетевая синхронизация", "#fda4af",
                "Предсказание, античит, детерминированный lockstep и сжатие снапшотов."),
    "procgen": ("Процедурная генерация", "#6ee7b7",
                "Планетные системы, сбалансированные карты, экосистемы и музыка."),
    "physics": ("Физические симуляции", "#a5b4fc",
                "Ткань, аэродинамика, поля и теплопередача."),
    "optimize": ("Системы оптимизации", "#fcd34d",
                 "Бюджет кадра, пространственные индексы и сжатие анимаций."),
    "math": ("Математические механики", "#c4b5fd",
             "Порталы, топология, запутанность и хаос как игровые правила."),
    "stats": ("Статистика и баланс", "#f9a8d4",
              "Оружие, матчмейкинг, прогнозы и лут."),
    "geometry": ("Геометрия и коллизии", "#93c5fd",
                 "Видимость, рикошеты и воксельные миры."),
    "shaders": ("Шейдеры и GPU", "#fb923c",
                "Процедурные материалы, искажения пространства и оптика."),
    "economy": ("Игровые экономики", "#bef264",
                "Аукционы, распределение ресурсов и инфляция."),
    "audio": ("Аудио-системы", "#5eead4",
              "Пространственный звук и физическое моделирование инструментов."),
    "ml": ("Нейросетевые приложения", "#a78bfa",
           "Генерация контента и апскейлинг в реальном времени."),
}

CHAPTER_OVERRIDES = {
    "terrain": "gfx", "gi": "gfx", "destruction": "gfx", "water": "gfx", "clouds": "gfx",
    "textures": "shaders", "distortion": "shaders", "optics": "shaders",
}

LEVEL_LABEL = {1: "база", 2: "средний", 3: "продвинутый"}
LEVELS_HINT = {
    1: "Можно реализовать за вечер, математика на уровне школьной программы.",
    2: "Нужна аккуратность: интеграторы, вероятности, структуры данных.",
    3: "Тяжёлая математика или серьёзная инженерия; читать после базы.",
}

DEMO_TITLES = {
    "ballistics": "Живая баллистика: угол, ветер, сопротивление",
    "boids": "Стая boids: три правила и пространственный поиск",
    "terrain": "Генератор рельефа: fBm и уровень моря",
    "waves": "Волновая поверхность: амплитуда, ветер, крутизна",
    "lockstep": "Lockstep: лаг, безопасный тик и desync",
    "planets": "Орбиты Кеплера и зона обитаемости",
    "maps": "Симметричная карта и метрика баланса",
    "ecosystem": "Лотка–Вольтерра: циклы хищник–жертва",
    "cloth": "Ткань на Verlet: ветер и итерации",
    "portal": "Портал как преобразование пространства",
    "chaos": "Бифуркационная диаграмма и показатель Ляпунова",
    "elo": "Elo: K-фактор и истинная разница скилла",
    "trend": "Временной ряд и сезонный прогноз",
    "loot": "Pity-лут: распределение попыток до легендарки",
    "voxel": "Marching squares: изоуровень поля плотности",
    "auction": "Аукцион Викри против первой цены",
}

GLOSSARY = [
    ("A*", "Поиск кратчайшего пути по эвристике h(n): f(n) = g(n) + h(n). Допустимая эвристика не переоценивает остаток."),
    ("ECS", "Entity Component System: сущность — идентификатор, компоненты — данные, системы — логика. Даёт кэш-локальность и композицию."),
    ("DOD", "Data-Oriented Design: сначала раскладка данных в памяти под обход, потом код. Основа производительных симуляций."),
    ("Fixed-point", "Арифметика с фиксированной запятой (Q16.16): детерминирована между платформами, в отличие от float."),
    ("Lockstep", "Схема, где клиенты обмениваются только командами и считают одинаковую симуляцию; состояние не передаётся."),
    ("Rollback", "Пересимуляция неподтверждённых вводов после снапшота сервера; основа клиентского предсказания."),
    ("Verlet", "Интегрирование по позициям: x′ = 2x − x_prev + a·dt². Устойчиво, удобно для ограничений."),
    ("PBD / XPBD", "Position-Based Dynamics: ограничения проецируются на позиции; XPBD делает жёсткость независимой от итераций."),
    ("SPH", "Smoothed Particle Hydrodynamics: жидкость как частицы с ядром сглаживания и давлением."),
    ("BVH", "Bounding Volume Hierarchy: дерево AABB для быстрого отсечения и raycast; строится по SAH."),
    ("SAH", "Surface Area Heuristic: критерий качества разбиения BVH по площади оболочек."),
    ("MCTS / UCT", "Monte Carlo Tree Search с формулой UCT: баланс исследования и использования в дереве игры."),
    ("Utility AI", "Выбор действия по взвешенной сумме нормированных факторов; альтернатива деревьям поведения."),
    ("Flow field", "Поле направлений к цели на сетке: дешёвый путь для больших групп юнитов."),
    ("WFC", "Wave Function Collapse: генерация по ограничениям с распространением возможностей и откатом."),
    ("SDF", "Signed Distance Field: функция расстояния до поверхности; удобна для CSG и ray marching."),
    ("Marching cubes", "Извлечение изоповерхности из сетки плотности по таблице 256 случаев."),
    ("PBR / BRDF", "Physically Based Rendering: энергосберегающие материалы; BRDF описывает отражение света."),
    ("GGX", "Микрогранная модель распределения нормалей с длинным хвостом блика."),
    ("Ambisonics", "Кодирование 3D-звука сферическими гармониками (W, X, Y, Z) с декодированием под наушники/колонки."),
    ("HRTF", "Head-Related Transfer Function: фильтр, описывающий, как уши и голова окрашивают звук с направления."),
    ("PRD", "Pseudo-Random Distribution: шанс растёт после неудач, снижая дисперсию серий без изменения среднего."),
    ("Glicko-2 / TrueSkill", "Байесовские рейтинги с неопределённостью (RD/σ) и обновлением после матча."),
    ("ARIMA", "Модель временного ряда: авторегрессия, дифференцирование и скользящее среднее ошибок."),
    ("GAN", "Соревнование генератора и дискриминатора; WGAN-GP stabilizes обучение через расстояние Вассерштейна."),
    ("FFT", "Быстрое преобразование Фурье: O(N log N); используется для океана, текстурирования и аудио."),
    ("Perlin / fBm", "Градиентный шум и его фрактальная сумма октав; база процедурных ландшафтов и материалов."),
    ("Кеплер", "T² = 4π²a³/(G(M+m)); уравнение M = E − e·sin E связывает время и положение на орбите."),
]


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
             "normalize mix clamp dot cross length pow exp smoothstep sin cos"),
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


def level_dots(level, color):
    dots = "".join(
        '<i class="on" style="background:%s"></i>' % color if i < level else "<i></i>"
        for i in range(3)
    )
    return '<span class="level" aria-label="сложность %d из 3">%s</span>' % (level, dots)


def demo_block(name, color):
    title = DEMO_TITLES.get(name, "Интерактивная модель")
    return f'''
        <figure class="demo" data-demo="{name}" style="--cat:{color}">
          <div class="demo-bar">
            <span class="live">live</span>
            <span>{esc(title)}</span>
            <span class="spacer"></span>
            <button type="button" data-act="pause" aria-pressed="false">пауза</button>
            <button type="button" data-act="reset">сброс</button>
          </div>
          <div class="demo-body"></div>
        </figure>'''


def render_topic(t, index):
    cat = cat_of(t)
    name, color, _ = CATS[cat]
    n = t["n"]
    tags = "".join(f'<span class="tag">{esc(x)}</span>' for x in t["tags"])
    detail = "".join(f"<p>{p}</p>" for p in t["detail"])
    formula, fnote = t["formula"]
    steps = "".join(f"<li>{s}</li>" for s in t["steps"])
    lang, code = t["code"]
    cx = t["complexity"]
    pitfalls = "".join(f"<li>{p}</li>" for p in t["pitfalls"])
    games = "".join(f'<span class="game-pill">{esc(g)}</span>' for g in t["games"])
    search = strip_tags(" ".join([
        t["title"], t["en"], " ".join(t["tags"]), t["summary"],
        " ".join(t["detail"]), " ".join(t["steps"]), " ".join(t["pitfalls"]),
        " ".join(t["games"]), name, LEVEL_LABEL[t["level"]],
    ]))
    demo = demo_block(t["demo"], color) if t.get("demo") else ""
    lang_label = {"python": "Python", "csharp": "C#", "glsl": "GLSL"}.get(lang, lang)

    return f'''
      <article class="topic" id="{t['id']}" data-cat="{cat}" data-level="{t['level']}"
               data-search="{attr(search)}" style="--cat:{color}">
        <header class="topic-head">
          <div class="topic-num" aria-hidden="true">{n:02d}</div>
          <div class="topic-titles">
            <div class="topic-meta">
              <span class="cat">{esc(name)}</span>
              <span class="dot"></span>
              <span>тема {n:02d} / 51</span>
              <span class="dot"></span>
              {level_dots(t['level'], color)}
              <span>{LEVEL_LABEL[t['level']]}</span>
            </div>
            <h3>{esc(t['title'])}</h3>
            <div class="en">{esc(t['en'])}</div>
          </div>
        </header>

        <p class="lead">{esc(t['summary'])}</p>
        <div class="tag-row">{tags}</div>

        <div class="block-label"><b>01</b> Суть</div>
        <div class="prose">{detail}</div>

        <div class="formula">
          <span class="f-label">математическая модель</span>
          <div class="f-main">{formula}</div>
          <div class="f-note">{fnote}</div>
        </div>

        <div class="block-label"><b>02</b> Как это построить</div>
        <ol class="steps">{steps}</ol>

        <div class="block-label"><b>03</b> Рабочий код</div>
        <div class="code-wrap">
          <div class="code-bar">
            <span class="dots"><i></i><i></i><i></i></span>
            <span class="lang">{lang_label}</span>
            <button class="copy-btn" type="button">копировать</button>
          </div>
          <pre><code>{highlight(code, lang)}</code></pre>
        </div>

        <div class="block-label"><b>04</b> Вычислительная сложность</div>
        <div class="complexity">
          <div class="cx"><div class="k">Время</div><div class="v">{cx[0]}</div></div>
          <div class="cx"><div class="k">Память</div><div class="v">{cx[1]}</div></div>
          <div class="cx"><div class="k">Практика</div><div class="v">{cx[2]}</div></div>
        </div>

        <div class="block-label"><b>05</b> Где обычно ошибаются</div>
        <ul class="pitfalls">{pitfalls}</ul>

        <div class="block-label"><b>06</b> В каких играх это видно</div>
        <div class="games-row"><span class="lbl">референсы</span>{games}</div>
        {demo}

        <button class="done-btn" type="button" aria-pressed="false">
          <span class="box" aria-hidden="true"></span><span>отметить изученным</span>
        </button>
      </article>'''


# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------

def build():
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    js = "\n".join([
        (ROOT / "assets" / "demos-a.js").read_text(encoding="utf-8"),
        (ROOT / "assets" / "demos-b.js").read_text(encoding="utf-8"),
        (ROOT / "assets" / "app.js").read_text(encoding="utf-8"),
    ])

    # chapters in topic order
    chapters = []
    for t in TOPICS:
        cat = cat_of(t)
        if not chapters or chapters[-1][0] != cat:
            chapters.append([cat, []])
        chapters[-1][1].append(t)

    counts = {}
    for t in TOPICS:
        counts[cat_of(t)] = counts.get(cat_of(t), 0) + 1

    # sidebar table of contents
    toc = []
    for idx, (cat, items) in enumerate(chapters, 1):
        name, color, _ = CATS[cat]
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
        f'<option value="{cid}">{esc(cinfo[0])} · {counts[cid]}</option>'
        for cid, cinfo in CATS.items() if counts.get(cid)
    )

    # knowledge map + chapters
    map_cards = []
    for idx, (cat, items) in enumerate(chapters, 1):
        name, color, desc = CATS[cat]
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
        name, color, _ = CATS[cat]
        body = "".join(render_topic(t, i) for i, t in enumerate(items))
        chapter_html.append(f'''
    <section class="chapter-block" id="chapter-{idx}" data-chapter="{cat}" style="--cat:{color}">
      <div class="chapter">
        <span class="idx">раздел {idx:02d} / {len(chapters):02d}</span>
        <h3>{esc(name)}</h3>
        <span class="rule"></span>
        <span class="idx">{len(items):02d} тем</span>
      </div>
      {body}
    </section>''')

    # appendix
    appx_html = []
    for section, cards in APPENDIX:
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
        f'<div class="gloss-row"><dt>{esc(term)}</dt><dd>{esc(desc)}</dd></div>'
        for term, desc in GLOSSARY
    )

    demo_count = sum(1 for t in TOPICS if t.get("demo"))
    appx_count = sum(len(cards) for _, cards in APPENDIX)
    total_formulas = len(TOPICS)

    head_script = """<script>
      (function () {
        try {
          var t = localStorage.getItem('ga:theme');
          if (t === 'light') document.documentElement.setAttribute('data-theme', 'light');
        } catch (e) {}
      })();
    </script>"""

    doc = f'''<!DOCTYPE html>
<html lang="ru" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#08090d">
<meta name="description" content="Алгоритмы игр: 51 тема с математикой, кодом, сложностью и интерактивными демо. Полное исследование игровых систем.">
<title>Алгоритмы игр — полное исследование · 51 тема</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%2308090d'/%3E%3Cpath d='M16 5l9.5 5.5v11L16 27l-9.5-5.5v-11z' fill='none' stroke='%23c8f751' stroke-width='2'/%3E%3Ccircle cx='16' cy='16' r='3' fill='%23c8f751'/%3E%3C/svg%3E">
{head_script}
<style>
{css}
</style>
</head>
<body>
<a class="skip-link" href="#start">К содержанию</a>
<noscript>
  <p style="margin:0;padding:10px 16px;background:#c8f751;color:#101404;font:13px/1.5 system-ui,sans-serif">
    Интерактивные демо и поиск требуют JavaScript — текст, формулы и код читаются и без него.
  </p>
</noscript>
<div class="scroll-progress" aria-hidden="true"></div>

<div class="topbar">
  <button class="icon-btn menu-btn" type="button" data-menu aria-expanded="false" aria-label="Открыть навигацию">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
  </button>
  <a class="brand" href="#top">
    <span class="mark" aria-hidden="true"></span>
    <span>Game Algorithms<small>research dossier · 2026</small></span>
  </a>
  <span class="topbar-spacer"></span>
  <nav class="topbar-links" aria-label="Разделы страницы">
    <a href="#start">Обзор</a>
    <a href="#map">Карта</a>
    <a href="#appendix">Практика</a>
    <a href="#glossary">Словарь</a>
  </nav>
  <button class="icon-btn" type="button" data-print aria-label="Печать или сохранение в PDF" title="Печать / PDF">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 9V4h10v5M7 18H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2"/><rect x="7" y="14" width="10" height="7" rx="1"/></svg>
    <span class="print-label">PDF</span>
  </button>
  <button class="icon-btn" type="button" data-theme-toggle>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6l1.4 1.4m10 10 1.4 1.4m0-12.8-1.4 1.4m-10 10-1.4 1.4"/><circle cx="12" cy="12" r="4"/></svg>
    <span data-theme-label>светлая</span>
  </button>
</div>

<header class="hero" id="top">
  <div class="hero-grid">
    <div>
      <span class="eyebrow">полное исследование · геймдев-системы</span>
      <h1>Алгоритмы, из которых<br>сделаны <em>игры</em></h1>
      <p class="lede">
        51 тема — от баллистики и boids до глобального освещения, lockstep и апскейлинга.
        Для каждой: математическая модель, пошаговая реализация, рабочий код,
        честная сложность, типичные ошибки и живая интерактивная модель в браузере.
      </p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#start">
          Начать изучение
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </a>
        <a class="btn" href="#appendix">45 практических задач</a>
      </div>
    </div>
    <aside class="hero-side" aria-label="Ключевые цифры">
      <div class="stat"><div class="num">{len(TOPICS)}<i>.</i></div><div class="cap">тем · {len(chapters)} разделов</div></div>
      <div class="stat"><div class="num">{demo_count}<i>×</i></div><div class="cap">интерактивных демо</div></div>
      <div class="stat"><div class="num">{appx_count}<i>+</i></div><div class="cap">практических задач</div></div>
      <div class="stat"><div class="num">0<i>.</i></div><div class="cap">внешних зависимостей</div></div>
    </aside>
  </div>
</header>

<div class="shell">
  <aside class="sidebar" aria-label="Содержание">
    <div class="side-head"><span>Содержание</span><b data-result-count>{len(TOPICS)} / {len(TOPICS)}</b></div>

    <div class="search-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input id="site-search" type="search" placeholder="Поиск: шум, lockstep, крит…" autocomplete="off" aria-label="Поиск по темам">
      <kbd>/</kbd>
    </div>

    <div class="chip-row" role="group" aria-label="Фильтр по сложности">
      <button class="chip" type="button" data-level="all" aria-pressed="true">все</button>
      <button class="chip" type="button" data-level="1" aria-pressed="false">база</button>
      <button class="chip" type="button" data-level="2" aria-pressed="false">средний</button>
      <button class="chip" type="button" data-level="3" aria-pressed="false">сложный</button>
    </div>

    <div class="search-wrap" style="margin-bottom:16px">
      <select id="cat-filter" aria-label="Фильтр по разделу" style="width:100%;padding:9px 10px;background:var(--panel);border:1px solid var(--line);border-radius:10px;color:var(--ink);font-size:12px;outline:none">
        <option value="all">Все разделы · {len(TOPICS)}</option>
        {cat_options}
      </select>
    </div>

    <div class="side-head" style="margin-top:4px">
      <span>Прогресс</span><b data-progress>0 / {len(TOPICS)}</b>
    </div>
    <div style="height:3px;background:var(--line);border-radius:99px;overflow:hidden;margin-bottom:16px">
      <div data-progress-bar style="height:100%;width:0;background:linear-gradient(90deg,var(--acid),var(--mint));transition:width .3s"></div>
    </div>

    <div class="side-head"><span>Разделы</span><b>{len(chapters)}</b></div>
    {''.join(toc)}

    <div class="side-foot">
      Документ работает офлайн: все стили, скрипты и демо встроены в один файл.
      Прогресс и тема хранятся локально в браузере.
    </div>
  </aside>

  <main class="content" id="main">
    <div class="content-inner">

      <section class="section-intro" id="start">
        <h2>Как читать это исследование</h2>
        <p>
          Материал собран как инженерный справочник, а не как список терминов. Каждая тема отвечает
          на одни и те же шесть вопросов, поэтому их можно сравнивать между собой и использовать
          как чек-лист при реализации.
        </p>

        <div class="callout">
          <span class="ico">→</span>
          <div>
            <b>Структура темы.</b> «Суть» объясняет модель на пальцах; «математическая модель» даёт
            рабочие формулы; «как построить» — порядок действий; «рабочий код» — минимальный
            референс; «сложность» — бюджет; «где ошибаются» — то, что обычно ломается в проде.
            Демо под темой можно крутить и ломать: параметры влияют на модель в реальном времени.
          </div>
        </div>

        <div class="map-grid" id="map">
          {''.join(map_cards)}
        </div>

        <div class="callout">
          <span class="ico">✦</span>
          <div>
            <b>Уровни.</b> <b>база</b> — один вечер и школьная математика;
            <b>средний</b> — нужны аккуратность и структуры данных;
            <b>продвинутый</b> — тяжёлая математика или серьёзная инженерия.
            Начните с базы своего раздела, затем берите средний: так проще увидеть связи.
          </div>
        </div>
      </section>
      {''.join(chapter_html)}

      <section class="appendix" id="appendix">
        <div class="chapter">
          <span class="idx">приложение</span>
          <h3>45 практических задач</h3>
          <span class="rule"></span>
          <span class="idx">что делать руками</span>
        </div>
        <p class="section-intro" style="padding-top:18px">
          Вторая часть исходного списка — прикладные задачи, которые чаще всего дают на позиции
          геймплейного или движкового программиста. Для каждой указан подход, ключевые алгоритмы,
          связанные темы исследования и практическая заметка.
        </p>
        {''.join(appx_html)}
      </section>

      <section class="appendix" id="glossary">
        <div class="chapter">
          <span class="idx">справочник</span>
          <h3>Словарь терминов</h3>
          <span class="rule"></span>
          <span class="idx">{len(GLOSSARY)} понятий</span>
        </div>
        <p class="section-intro" style="padding-top:18px">
          Термины, которые встречаются в тексте и в вакансиях. Держите под рукой во время
          технического интервью.
        </p>
        <dl class="glossary">{glossary}</dl>
      </section>

      <section class="section-intro" id="method" style="border-top:1px solid var(--line);margin-top:44px">
        <h2>Метод и границы</h2>
        <p>
          Формулы приведены в игровых единицах, а не в СИ, если так удобнее читать; константы
          подобраны под геймплей, а не под физическую лабораторию. Код — минимальный, без
          оптимизаций и обработки ошибок: его задача — показать структуру, а не заменить движок.
          Сложности указаны для типичной реализации; реальные цифры зависят от платформы и
          компилятора.
        </p>
        <p style="margin-top:12px">
          Демонстрации используют Canvas 2D и обычную математику: никаких библиотек, CDN и
          сборки. Это сделано специально — файл открывается двойным кликом, работает офлайн и
          не устаревает вместе с зависимостями.
        </p>
      </section>
    </div>
  </main>
</div>

<footer class="footer">
  <div class="footer-inner">
    <div>
      <h3>Game Algorithms</h3>
      <p>
        Синтез исходного списка тем, математических моделей и инженерной практики:
        то, что нужно, чтобы не просто знать термин, а собрать механику.
      </p>
      <p>
        Материалы в репозитории: векторная математика, разбор Ханойской башни и маленькие
        игры-демо. Новый документ дополняет их системным разбором алгоритмов.
      </p>
      <p class="fine">Один HTML-файл · встроенные CSS и JS · {len(TOPICS)} тем · {demo_count} демо · {appx_count} задач · {total_formulas} формул</p>
    </div>
    <nav class="footer-links" aria-label="Ссылки">
      <a href="#start">Как читать <span>↑</span></a>
      <a href="#map">Карта разделов <span>→</span></a>
      <a href="#appendix">Практические задачи <span>→</span></a>
      <a href="#glossary">Словарь терминов <span>→</span></a>
      <a href="README.md">README репозитория <span>↗</span></a>
      <a href="VectorMath.html">Векторная математика <span>↗</span></a>
      <a href="Hanoi-Tower-solver.md">Ханойская башня <span>↗</span></a>
      <a href="asteroids.html">Asteroids demo <span>↗</span></a>
    </nav>
  </div>
</footer>

<button class="to-top" type="button" aria-label="Наверх">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M6 11l6-6 6 6"/></svg>
</button>

<script>
{js}
</script>
</body>
</html>
'''

    out = ROOT / "game-algorithms-research.html"
    out.write_text(doc, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"собрано: {out.name}  ({size_kb:.0f} KB)")
    print(f"тем: {len(TOPICS)}, разделов: {len(chapters)}, демо: {demo_count}, задач: {appx_count}")
    return out


if __name__ == "__main__":
    build()
