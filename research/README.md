# Контент исследования / Research content

Темы хранятся как данные, а не как разметка: HTML собирается скриптом.
Topics are stored as data, not as markup: the HTML pages are built by a script.

Документ разделён на три части: **Часть I — системы** (механики, ИИ, графика,
физика, оптимизация, математика, статистика, геометрия, шейдеры, экономика,
аудио, нейросети, тяжёлые нагрузки), **Часть II — процедурная генерация** —
отдельный атлас из 28 тем с нумерацией `PG-01…PG-28` — и **Часть III — сетевое
взаимодействие**: 22 темы с нумерацией `NET-01…NET-22`, от транспорта до
эксплуатации крупной MMO.

## Русский контент / Russian content

### Часть I — системы

| Файл | Темы |
|---|---|
| `topics_1.py` | 01–13: механики, ИИ, графика |
| `topics_2.py` | 14–23: вода, облака, сети, процедурная генерация |
| `topics_3.py` | 24–30: физика + 37–40: математические механики |
| `topics_4.py` | 41–50: статистика, геометрия, шейдеры |
| `topics_5.py` | 51–57: экономика, аудио, нейросети + 45 практических задач (`APPENDIX`) |
| `topics_6.py` | 31–36: системы оптимизации |
| `topics_7.py` | 58–66: тяжёлые нагрузки и GPU |

### Часть II — процедурная генерация

| Файл | Слои и темы |
|---|---|
| `topics_procgen_a.py` | 01 «Шум, поля и выборки» и 02 «Планировка»: noise, worley, poisson, seeds, diamond-square, caves, BSP, random walk, maze, WFC, city (темы 67–77) |
| `topics_procgen_b.py` | 03 «Миры и рельеф» и 04 «Контент и системы»: erosion, biomes, rivers, L-systems, shape-грамматики, items, names, quests, director (темы 78–86) |
| `topics_2.py` (перенесены) | `terrain`, `clouds`, `planets`, `maps`, `ecosystem`, `music` — теперь `cat="procgen"` |
| `topics_4.py` (перенесены) | `voxels`, `textures` — теперь `cat="procgen"` |

Порядок тем внутри части задаёт `PG_ORDER` в `i18n.py`; он же определяет номера
`PG-01…PG-28` на странице. Группа темы задаётся полем `pg`:
`foundation`, `layout`, `world` или `content`.

### Часть III — сетевое взаимодействие

| Файл | Слои и темы |
|---|---|
| `topics_net_a.py` | 01 «Транспорт и топология» и 02 «Модели синхронизации»: transport, reliable, topology, NAT, browser, rollback, determinism (темы 87–93) |
| `topics_net_b.py` | 03 «Реальное время» и 04 «Масштаб и эксплуатация»: interp, lagcomp, AOI, clock, budget, shard, session, persistence, security, ops, testing (темы 94–104) |
| `topics_2.py` (перенесены) | `prediction`, `anticheat`, `lockstep`, `snapshot` — уже `cat="network"` |

Порядок задаёт `NET_ORDER` в `i18n.py`, он же формирует номера `NET-01…NET-22`.
Группа темы задаётся полем `nl`: `transport`, `sync`, `realtime` или `scale`.

## Английский контент / English content

| Файл | Темы |
|---|---|
| `topics_en_1.py` | 01–13 |
| `topics_en_2.py` | 14–23 |
| `topics_en_3.py` | 24–30 |
| `topics_en_4.py` | 31–47 (оптимизация, математика, статистика, геометрия) |
| `topics_en_5.py` | 48–57 (шейдеры, экономика, аудио, нейросети) |
| `topics_en_6.py` | 58–66 (heavy / GPU) |
| `topics_en_procgen_a.py` | Часть II, слои 01–02 (19 новых тем; 8 перенесённых уже были на английском) |
| `topics_en_procgen_b.py` | Часть II, слои 03–04 |
| `topics_en_net_a.py` | Часть III, слои 01–02 |
| `topics_en_net_b.py` | Часть III, слои 03–04 |
| `appendix_en.py` | 45 практических задач на английском (`APPENDIX_EN`) |
| `codes_en.py` | английские версии примеров кода (`CODE_EN`) — комментарии переведены |
| `i18n.py` | разделы, подписи интерфейса, словарь, строки оболочки (RU + EN), `PARTS`, `PG_GROUPS`, `PG_ORDER`, `PG_DECISIONS` |

Английские файлы **не содержат** `n`, `cat`, `level`, `pg`, `demo`: эти поля
наследуются от русской темы с тем же `id` при сборке.

## Структура темы / Topic schema

Каждая тема — словарь с полями:

- `n`, `id`, `cat`, `level` (1–3)
- `title`, `en`, `tags`, `summary`
- `detail` — 3 абзаца объяснения (можно с HTML: `<b>`, `<code>`, `<sub>`)
- `formula` — `(формула, пояснение)`
- `steps` — список шагов реализации
- `code` — `(язык, код)`; языки: `python`, `csharp`, `glsl`, `wgsl`
- `complexity` — `(время, память, практика)`
- `pitfalls` — список типичных ошибок
- `games` — игры-референсы
- `demo` — необязательный ключ демо из `assets/demos-*.js`
- `pg` — **только для `cat="procgen"`**: слой части II
  (`foundation` / `layout` / `world` / `content`)
- `nl` — **только для `cat="network"`**: слой части III
  (`transport` / `sync` / `realtime` / `scale`)

## Демо / Demos

| Файл | Что внутри |
|---|---|
| `assets/demos-a.js` | базовые демо Части I (баллистика, boids, рельеф, волны, планеты…) |
| `assets/demos-b.js` | ткань, портал, хаос, Elo, лут, воксели, аукцион |
| `assets/demos-c.js` | GPU-частицы, бюджет кадра, отсечение, батчинг |
| `assets/demos-procgen-a.js` | шум, Ворли, Пуассон, сид/хэш, материалы, diamond-square, пещеры, BSP, random walk, лабиринты, WFC |
| `assets/demos-procgen-b.js` | город, эрозия, биомы, реки, облака, L-системы, предметы, имена, квесты, музыка, AI-директор |
| `assets/demos-network.js` | транспорт и надёжность, топологии и NAT, rollback и интерполяция, лаг-компенсация, AOI, бюджет, шардинг, матчмейкинг, rate limit |

Демо монтируются лениво (`IntersectionObserver`) и останавливаются вне экрана.
Все подписи — через `T('key')`, ключи лежат в `assets/labels.js` (RU + EN).

## Пересборка / Rebuild

```bash
python3 tools/build.py       # → index.html (RU), index.en.html (EN), game-algorithms-research.html
python3 tools/gen_readme.py  # → README.md (список тем и задач)
```

Скрипт сам подставляет CSS, JS, собирает оглавление, карту разделов, отдельную
часть II (hero, атлас, таблица выбора алгоритма, слои), приложение и словарь.
Внешних зависимостей нет: только стандартная библиотека Python.
Для английской страницы подставляется только английская таблица подписей
(`assets/labels.js` разбирается на `TABLES.ru` / `TABLES.en`).

## Добавление темы / Adding a topic

1. Добавьте словарь в подходящий `topics_*.py` (RU) и в `topics_en_*.py` (EN) —
   с тем же `id`.
2. Для части II добавьте `cat="procgen"`, `pg="<слой>"` и `id` в `PG_ORDER`;
   для части III — `cat="network"`, `nl="<слой>"` и `id` в `NET_ORDER`.
3. Для интерактивной модели — функцию в `assets/demos-procgen-*.js` /
   `demos-network.js` (`DEMOS.<имя> = function (el) { ... }`) и укажите
   `demo="<имя>"`. Подписи добавьте в `assets/labels.js` (RU и EN).
4. Запустите сборку и откройте HTML.
