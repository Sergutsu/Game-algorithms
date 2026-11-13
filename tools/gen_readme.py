#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерирует README.md из данных research/*.py (двуязычный).

Запуск:  python3 tools/gen_readme.py
"""

import importlib
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
from topics_procgen_a import TOPICS_PG_A  # noqa: E402
from topics_procgen_b import TOPICS_PG_B  # noqa: E402
from topics_net_a import TOPICS_NET_A  # noqa: E402
from topics_net_b import TOPICS_NET_B  # noqa: E402
from topics_balance_a import TOPICS_BAL_A  # noqa: E402
from topics_balance_b import TOPICS_BAL_B  # noqa: E402
from topics_genres_a import TOPICS_GENRES_A  # noqa: E402
from topics_genres_b import TOPICS_GENRES_B  # noqa: E402
from styles import STYLE_ATOMS, STYLE_PRESETS, PROMPT_FORMATS  # noqa: E402
from i18n import (  # noqa: E402
    BAL_GROUP_ORDER, BAL_GROUPS, BAL_ORDER, CATS, CHAPTER_ORDER,
    GENRE_GROUP_ORDER, GENRE_GROUPS, GENRE_ORDER,
    NET_GROUP_ORDER, NET_GROUPS, NET_ORDER,
    PG_GROUP_ORDER, PG_GROUPS, PG_ORDER,
)

PG_RANK = {tid: i for i, tid in enumerate(PG_ORDER)}
NET_RANK = {tid: i for i, tid in enumerate(NET_ORDER)}
BAL_RANK = {tid: i for i, tid in enumerate(BAL_ORDER)}
GENRE_RANK = {tid: i for i, tid in enumerate(GENRE_ORDER)}

try:
    from appendix_en import APPENDIX_EN  # noqa: E402
except ImportError:
    APPENDIX_EN = []

RU = (TOPICS_1 + TOPICS_2 + TOPICS_3 + TOPICS_4 + TOPICS_5 + TOPICS_6 +
      TOPICS_7 + TOPICS_PG_A + TOPICS_PG_B + TOPICS_NET_A + TOPICS_NET_B +
      TOPICS_BAL_A + TOPICS_BAL_B + TOPICS_GENRES_A + TOPICS_GENRES_B)
EN = []
for _i in range(1, 8):
    try:
        _m = importlib.import_module("topics_en_%d" % _i)
    except ImportError:
        continue
    for _name in dir(_m):
        if _name.startswith("TOPICS_EN_"):
            EN.extend(getattr(_m, _name))
for _mod, _attr in (("topics_en_procgen_a", "TOPICS_EN_PG_A"),
                    ("topics_en_procgen_b", "TOPICS_EN_PG_B"),
                    ("topics_en_net_a", "TOPICS_EN_NET_A"),
                    ("topics_en_net_b", "TOPICS_EN_NET_B"),
                    ("topics_en_balance_a", "TOPICS_EN_BAL_A"),
                    ("topics_en_balance_b", "TOPICS_EN_BAL_B"),
                    ("topics_en_genres_a", "TOPICS_EN_GENRES_A"),
                    ("topics_en_genres_b", "TOPICS_EN_GENRES_B")):
    try:
        _m = importlib.import_module(_mod)
    except ImportError:
        continue
    EN.extend(getattr(_m, _attr, []))
EN_BY_ID = {t["id"]: t for t in EN}

SITE = "https://sergutsu.github.io/Game-algorithms/"


def cat_of(topic):
    return topic.get("cat", "mechanics")


def en_topic(topic):
    """Английская версия темы: из EN-модуля, иначе — поле 'en' и теги оригинала."""
    merged = dict(topic)
    other = EN_BY_ID.get(topic["id"])
    if other:
        for field in ("title", "tags", "summary", "formula", "complexity"):
            if other.get(field):
                merged[field] = other[field]
    if not other or "formula" not in other:
        try:
            from genres_en import GENRE_EN_EXTRA
        except ImportError:
            GENRE_EN_EXTRA = {}
        extra = GENRE_EN_EXTRA.get(topic["id"])
        if extra:
            merged.update(extra)
    return merged


def topic_list(topics, lang):
    """Список тем по разделам: Part I — системы, Part II — процедурная генерация."""
    lines = []
    for cat in CHAPTER_ORDER:
        items = [t for t in topics if cat_of(t) == cat]
        if cat in ("procgen", "network", "balance", "genres"):
            continue
        items.sort(key=lambda t: t["n"])
        if not items:
            continue
        name = CATS[cat]["ru"][0] if lang == "ru" else CATS[cat]["en"][0]
        lines.append("")
        lines.append("### %s" % name)
        lines.append("")
        for t in items:
            tags = ", ".join(t.get("tags") or [])
            extra = " · 🎮 demo" if t.get("demo") else ""
            lines.append("%d. **%s**  " % (t["n"], t["title"]))
            lines.append("   *(%s)*%s" % (tags, extra))

    part = [t for t in topics if cat_of(t) == "procgen"]
    if part:
        lines.append("")
        lines.append("## Часть II — процедурная генерация / Part II — procedural generation")
        lines.append("")
        if lang == "ru":
            lines.append("> Отдельная часть исследования: полный атлас алгоритмов генерации контента.")
        else:
            lines.append("> A separate part of the research: the full atlas of content generation.")
        num = 0
        for gkey in PG_GROUP_ORDER:
            gitems = [t for t in part if t.get("pg", "foundation") == gkey]
            if not gitems:
                continue
            gitems.sort(key=lambda t: PG_RANK.get(t["id"], 9999))
            gname = PG_GROUPS[gkey][lang][0]
            lines.append("")
            lines.append("### %s" % gname)
            lines.append("")
            for t in gitems:
                num += 1
                tags = ", ".join(t.get("tags") or [])
                extra = " · 🎮 demo" if t.get("demo") else ""
                lines.append("PG-%02d. **%s**  " % (num, t["title"]))
                lines.append("   *(%s)*%s" % (tags, extra))

    net = [t for t in topics if cat_of(t) == "network"]
    if net:
        lines.append("")
        lines.append("## Часть III — сетевое взаимодействие / Part III — networked multiplayer")
        lines.append("")
        if lang == "ru":
            lines.append("> Отдельная часть исследования: полный сетевой плейбук, "
                         "от UDP до операций крупной MMO.")
        else:
            lines.append("> A separate part of the research: the full networking playbook, "
                         "from UDP to large-MMO operations.")
        num = 0
        for gkey in NET_GROUP_ORDER:
            gitems = [t for t in net if t.get("nl", "transport") == gkey]
            if not gitems:
                continue
            gitems.sort(key=lambda t: NET_RANK.get(t["id"], 9999))
            gname = NET_GROUPS[gkey][lang][0]
            lines.append("")
            lines.append("### %s" % gname)
            lines.append("")
            for t in gitems:
                num += 1
                tags = ", ".join(t.get("tags") or [])
                extra = " · 🎮 demo" if t.get("demo") else ""
                lines.append("NET-%02d. **%s**  " % (num, t["title"]))
                lines.append("   *(%s)*%s" % (tags, extra))

    bal = [t for t in topics if cat_of(t) == "balance"]
    if bal:
        lines.append("")
        lines.append("## Часть IV — баланс и прогрессия / Part IV — balance and progression")
        lines.append("")
        if lang == "ru":
            lines.append("> Числа, из которых складывается ощущение игры: урон, защита, "
                         "кривая опыта, награды и экономика.")
        else:
            lines.append("> The numbers that make a game feel the way it feels: damage, "
                         "defence, the XP curve, rewards and economy.")
        num = 0
        for gkey in BAL_GROUP_ORDER:
            gitems = [t for t in bal if t.get("bg", "damage") == gkey]
            if not gitems:
                continue
            gitems.sort(key=lambda t: BAL_RANK.get(t["id"], 9999))
            lines.append("")
            lines.append("### %s" % BAL_GROUPS[gkey][lang][0])
            lines.append("")
            for t in gitems:
                num += 1
                tags = ", ".join(t.get("tags") or [])
                extra = " · 🎮 demo" if t.get("demo") else ""
                lines.append("BAL-%02d. **%s**  " % (num, t["title"]))
                lines.append("   *(%s)*%s" % (tags, extra))

    genres = [t for t in topics if cat_of(t) == "genres"]
    if genres:
        lines.append("")
        lines.append("## Часть V — атлас жанров / Part V — the genre atlas")
        lines.append("")
        if lang == "ru":
            lines.append("> 36 жанров: ядро цикла, темп, типичные провалы и игры, "
                         "в которых жанр виден.")
        else:
            lines.append("> 36 genres: the core loop, the tempo, the usual failures and "
                         "the games where the genre shows.")
        num = 0
        for gkey in GENRE_GROUP_ORDER:
            gitems = [t for t in genres if t.get("gg", "action") == gkey]
            if not gitems:
                continue
            gitems.sort(key=lambda t: GENRE_RANK.get(t["id"], 9999))
            lines.append("")
            lines.append("### %s" % GENRE_GROUPS[gkey][lang][0])
            lines.append("")
            for t in gitems:
                num += 1
                tags = ", ".join(t.get("tags") or [])
                loop = (t.get("formula") or ("", ""))[0]
                lines.append("GEN-%02d. **%s**  " % (num, t["title"]))
                lines.append("   *(%s)* — %s" % (tags, loop))

    if lang == "ru":
        lines.append("")
        lines.append("## Часть VI — стиль и студия промптов / Part VI — style and the prompt studio")
        lines.append("")
        lines.append("> %d атомов стиля в %d слоях, %d готовых пресетов и конструктор, "
                     "который собирает из досье задание для команды или языковой модели "
                     "(%d формата выдачи).  " % (
                         len(STYLE_ATOMS), 6, len(STYLE_PRESETS), len(PROMPT_FORMATS)))
        lines.append("> %d style atoms in 6 layers, %d ready-made presets and a composer "
                     "that turns the dossier into a brief for a team or a language model "
                     "(%d output formats)." % (
                         len(STYLE_ATOMS), len(STYLE_PRESETS), len(PROMPT_FORMATS)))
        lines.append("")
        lines.append("`#part-styles` — живой блок в HTML: атлас, пресеты и конструктор.")
    else:
        lines.append("")
        lines.append("## Part VI — style and the prompt studio")
        lines.append("")
        lines.append("> %d style atoms across 6 layers, %d ready-made presets and a composer "
                     "that turns the dossier into a brief for a team or a language model "
                     "(%d output formats)." % (
                         len(STYLE_ATOMS), len(STYLE_PRESETS), len(PROMPT_FORMATS)))
        lines.append("")
        lines.append("`#part-styles` — the live block in the HTML: atlas, presets and composer.")
    return "\n".join(lines)


def tasks_list(appendix, lang):
    lines = []
    num = 0
    for section, cards in appendix:
        lines.append("")
        lines.append("### %s" % section)
        lines.append("")
        for card in cards:
            num += 1
            lines.append("%d. **%s**  " % (num, card[0]))
            lines.append("   *(%s)*" % card[1])
    return "\n".join(lines)


def main():
    demos = len({t["demo"] for t in RU if t.get("demo")})
    tasks = sum(len(cards) for _, cards in APPENDIX)

    ru_topics = topic_list(RU, "ru")
    en_topics = topic_list([en_topic(t) for t in RU], "en")
    ru_tasks = tasks_list(APPENDIX, "ru")
    en_tasks = tasks_list(APPENDIX_EN or APPENDIX, "en")

    pg_topics = [t for t in RU if cat_of(t) == "procgen"]
    pg_n = len(pg_topics)
    pg_d = len({t.get("demo") for t in pg_topics if t.get("demo")})
    pg_max = "PG-%02d" % len(PG_ORDER)

    net_topics = [t for t in RU if cat_of(t) == "network"]
    net_n = len(net_topics)
    net_d = len({t.get("demo") for t in net_topics if t.get("demo")})

    bal_topics = [t for t in RU if cat_of(t) == "balance"]
    bal_n = len(bal_topics)
    bal_d = len({t.get("demo") for t in bal_topics if t.get("demo")})
    genres_n = len([t for t in RU if cat_of(t) == "genres"])

    atoms = len(STYLE_ATOMS)
    presets = len(STYLE_PRESETS)

    doc = f"""# Game-algorithms

<!-- Файл генерируется: python3 tools/gen_readme.py -->

> ### 📘 Полное исследование: [game-algorithms-research.html](game-algorithms-research.html)
> Один автономный HTML-файл (открывается двойным кликом, работает офлайн):
> **{len(RU)} тем** с математической моделью, пошаговой реализацией, рабочим кодом,
> сложностью, типичными ошибками и референсами; **{demos} интерактивных демо**
> (шум и эрозия, пещеры и подземелья, BSP, лабиринты, WFC, биомы, реки, города,
> предметы, имена, квесты, музыка, фасады, а также баллистика, boids и lockstep);
> **{tasks} практических задач** и словарь терминов.
>
> **Часть II — процедурная генерация** вынесена в отдельный атлас: {pg_n} тем,
> {pg_d} живых моделей, четыре слоя — от шума и сэмплинга до контента и драматургии.
> **Часть III — сетевое взаимодействие**: {net_n} темы, {net_d} живых моделей,
> четыре слоя — транспорт, синхронизация, реальное время и масштаб.
> **Часть IV — баланс и прогрессия**: {bal_n} темы, {bal_d} живых моделей — урон и
> защита, кривые опыта, награды, инфляция и Монте-Карло-симулятор баланса.
> **Часть V — атлас жанров**: {genres_n} жанров с ядром цикла, темпом и провалами.
> **Часть VI — стиль и студия промптов**: {atoms} атомов стиля, {presets} пресетов и
> конструктор, который собирает из досье готовое задание для команды или модели.
> Поиск, фильтры по сложности, прогресс чтения, тёмная/светлая темы и переключатель
> языка — внутри.
>
> Исходники контента — `research/`, сборка — `python3 tools/build.py`, стили и демо — `assets/`.

> ### 📗 Full research (English): [index.en.html](index.en.html)
> The same research in English: **{len(RU)} topics** with the mathematical model, a
> step-by-step build, working code, complexity, pitfalls and references;
> **{demos} interactive demos**; **{tasks} practical tasks** and a glossary.
> **Part II — procedural generation** is a separate atlas: {pg_n} topics, {pg_d} live
> models, four layers from noise and sampling up to content and drama.
> **Part III — networked multiplayer**: {net_n} topics, {net_d} live models,
> four layers: transport, synchronisation, real time and scale.
> **Part IV — balance and progression**: {bal_n} topics, {bal_d} live models — damage
> and defence, XP curves, rewards, inflation and a Monte-Carlo balance simulator.
> **Part V — the genre atlas**: {genres_n} genres with their core loop, tempo and pitfalls.
> **Part VI — style and the prompt studio**: {atoms} style atoms, {presets} presets and a
> composer that turns the dossier into a brief for a team or a model.
> A language switch sits in the header and remembers your choice.

**Онлайн / Live:** <{SITE}> — GitHub Pages, корень репозитория, ветка `main`
(`.nojekyll` включён, внешних зависимостей нет).

---

## 🚀 Быстрый старт

```bash
# локальный просмотр
open index.html            # русская версия
open index.en.html         # английская версия

# пересборка обоих языков из research/*.py
python3 tools/build.py
python3 tools/gen_readme.py   # обновить этот README
```

| Файл | Что это |
|---|---|
| `index.html` | Русская версия — точка входа GitHub Pages |
| `index.en.html` | Английская версия |
| `game-algorithms-research.html` | Копия русской версии (старые ссылки работают) |
| `research/topics_*.py` | Часть I, темы RU (1–30, 31–36 оптимизация, 37–57, 58–66 heavy/GPU) |
| `research/topics_procgen_a.py` | Часть II, слои 01–02: шум, сэмплинг, планировка (RU) |
| `research/topics_procgen_b.py` | Часть II, слои 03–04: миры, контент, системы (RU) |
| `research/topics_net_a.py` | Часть III, слои 01–02: транспорт и синхронизация (RU) |
| `research/topics_net_b.py` | Часть III, слои 03–04: реальное время и масштаб (RU) |
| `research/topics_en_*.py` | Часть I, темы EN (те же id, английский текст) |
| `research/topics_en_procgen_*.py` | Часть II на английском |
| `research/topics_en_net_*.py` | Часть III на английском |
| `research/topics_balance_a.py` | Часть IV, слои 01–03: урон, защита, прогрессия (RU) |
| `research/topics_balance_b.py` | Часть IV, слои 04–05: награды, экономика, симуляция (RU) |
| `research/topics_genres_a.py` | Часть V, экшен / стратегии / RPG — 18 жанров (RU) |
| `research/topics_genres_b.py` | Часть V, симуляции / приключения / спорт — 18 жанров (RU) |
| `research/topics_en_balance_*.py` | Часть IV на английском |
| `research/topics_en_genres_*.py` | Часть V на английском |
| `research/genres_en.py` | Английские формулы и темпы для всех 36 жанров |
| `research/styles.py` | Часть VI: слои стиля, атомы, пресеты, форматы промпта |
| `research/studio_i18n.py` | Подписи и шаблоны конструктора промптов (RU + EN) |
| `research/appendix_en.py` | 45 практических задач на английском |
| `research/codes_en.py` | Английские комментарии в примерах кода |
| `research/i18n.py` | Разделы, подписи интерфейса, словарь, строки оболочки (RU + EN) |
| `tools/build.py` | Сборщик: `research/*.py` + `assets/` → два HTML |
| `assets/studio.js` | Конструктор промптов: выборки, пресеты, сборка и экспорт |
| `assets/` | Стили, клиентская логика, {demos} демо, таблицы подписей |

---

## 📚 Темы — русская версия

Сначала **Часть I — системы**, затем отдельная **Часть II — атлас процедурной
генерации** (нумерация PG-01…{pg_max}) и **Часть III — сетевой плейбук**
(нумерация NET-01…NET-{net_n:02d}).
{ru_topics}

---

## 🛠 Практические задачи — русская версия
{ru_tasks}

---

## 📚 Topics — English version
{en_topics}

---

## 🛠 Practical tasks — English version
{en_tasks}

---

## 📐 Что требует каждая тема

- **Математических моделей** — дифференциальные уравнения, теорвер, линейная алгебра
- **Алгоритмических парадигм** — динамическое программирование, Монте-Карло, ECS/DOD
- **Оптимизационных подходов** — приближённые вычисления, численные методы, батчинг, GPU
- **Вычислительной сложности** — O-нотация, профилирование, бюджет кадра
- **Геометрических представлений** — кватернионы, проективные пространства, SDF/BVH

**What every topic needs**

- **A mathematical model** — ODEs, probability, linear algebra
- **An algorithmic paradigm** — dynamic programming, Monte Carlo, ECS / data-oriented design
- **An optimisation angle** — approximations, numerics, batching, GPU compute
- **A complexity story** — Big-O, profiling, the frame budget
- **A geometric representation** — quaternions, projective spaces, SDF / BVH

---

## 🖥 Разделы

| # | Раздел | Section |
|---|---|---|
""" + "\n".join(
        "| %d | %s | %s |" % (i + 1, CATS[c]["ru"][0], CATS[c]["en"][0])
        for i, c in enumerate(CHAPTER_ORDER)
    ) + """

---

## 📄 Лицензия и источники

Код и тексты — для обучения и прототипирования. Ссылки на игры приведены как примеры
того, где встречается тот или иной алгоритм.
"""

    out = ROOT / "README.md"
    out.write_text(doc, encoding="utf-8")
    print("записан:", out, f"({out.stat().st_size} байт)")


if __name__ == "__main__":
    main()
