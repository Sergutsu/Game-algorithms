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
from i18n import CATS, CHAPTER_ORDER  # noqa: E402

try:
    from appendix_en import APPENDIX_EN  # noqa: E402
except ImportError:
    APPENDIX_EN = []

RU = TOPICS_1 + TOPICS_2 + TOPICS_3 + TOPICS_4 + TOPICS_5 + TOPICS_6 + TOPICS_7
EN = []
for _i in range(1, 7):
    try:
        _m = importlib.import_module("topics_en_%d" % _i)
    except ImportError:
        continue
    for _name in dir(_m):
        if _name.startswith("TOPICS_EN_"):
            EN.extend(getattr(_m, _name))
EN_BY_ID = {t["id"]: t for t in EN}

SITE = "https://sergutsu.github.io/Game-algorithms/"


def cat_of(topic):
    return topic.get("cat", "mechanics")


def en_topic(topic):
    """Английская версия темы: из EN-модуля, иначе — поле 'en' и теги оригинала."""
    merged = dict(topic)
    other = EN_BY_ID.get(topic["id"])
    if other:
        for field in ("title", "tags", "summary"):
            if other.get(field):
                merged[field] = other[field]
    return merged


def topic_list(topics, lang):
    """Список тем по разделам (в порядке CHAPTER_ORDER)."""
    lines = []
    for cat in CHAPTER_ORDER:
        items = sorted([t for t in topics if cat_of(t) == cat], key=lambda t: t["n"])
        if not items:
            continue
        name = CATS[cat]["ru"][0] if lang == "ru" else CATS[cat]["en"][0]
        lines.append("")
        lines.append("### %s" % name)
        lines.append("")
        for t in items:
            title = t["title"] if lang == "ru" else t["title"]
            tags = ", ".join(t.get("tags") or [])
            extra = ""
            if t.get("demo"):
                extra = " · 🎮 demo"
            lines.append("%d. **%s**  " % (t["n"], title))
            lines.append("   *(%s)*%s" % (tags, extra))
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

    doc = f"""# Game-algorithms

<!-- Файл генерируется: python3 tools/gen_readme.py -->

> ### 📘 Полное исследование: [game-algorithms-research.html](game-algorithms-research.html)
> Один автономный HTML-файл (открывается двойным кликом, работает офлайн):
> **{len(RU)} тем** с математической моделью, пошаговой реализацией, рабочим кодом,
> сложностью, типичными ошибками и референсами; **{demos} интерактивных демо**
> (баллистика, boids, lockstep, GPU-частицы, бюджет кадра, отсечение, батчинг…);
> **{tasks} практических задач** и словарь терминов.
> Поиск, фильтры по сложности, прогресс чтения, тёмная/светлая темы и переключатель
> языка — внутри.
>
> Исходники контента — `research/`, сборка — `python3 tools/build.py`, стили и демо — `assets/`.

> ### 📗 Full research (English): [index.en.html](index.en.html)
> The same research in English: **{len(RU)} topics** with the mathematical model, a
> step-by-step build, working code, complexity, pitfalls and references;
> **{demos} interactive demos**; **{tasks} practical tasks** and a glossary.
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
| `research/topics_*.py` | Темы RU (1–30, 31–36 оптимизация, 37–57, 58–66 heavy/GPU) |
| `research/topics_en_*.py` | Темы EN (те же id, английский текст) |
| `research/appendix_en.py` | 45 практических задач на английском |
| `research/codes_en.py` | Английские комментарии в примерах кода |
| `research/i18n.py` | Разделы, подписи интерфейса, словарь, строки оболочки (RU + EN) |
| `tools/build.py` | Сборщик: `research/*.py` + `assets/` → два HTML |
| `assets/` | Стили, клиентская логика, {demos} демо, таблицы подписей |

---

## 📚 Темы — русская версия
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
