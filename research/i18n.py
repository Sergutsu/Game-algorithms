# -*- coding: utf-8 -*-
"""Двуязычные строки интерфейса: RU + EN.

Здесь лежит всё, что не является содержимым тем: названия разделов, подписи
интерфейса, словарь терминов и тексты оболочки страницы. Темы лежат в
research/topics_*.py (RU) и research/topics_en_*.py (EN).
"""

# --------------------------------------------------------------------------
# разделы: цвет общий, название и описание — на двух языках
# --------------------------------------------------------------------------
CATS = {
    "mechanics": {
        "color": "#c8f751",
        "ru": ("Геймплейные механики",
               "Баллистика, урон, рынки, кривые и квантовые состояния: как правила превращаются в ощущения."),
        "en": ("Gameplay mechanics",
               "Ballistics, damage, markets, curves and quantum states: how rules turn into feel."),
    },
    "ai": {
        "color": "#7dd3fc",
        "ru": ("Искусственный интеллект",
               "Решения, эмоции, адаптивная сложность, диалоги и роевое поведение."),
        "en": ("Artificial intelligence",
               "Decisions, emotions, adaptive difficulty, dialogue and swarm behaviour."),
    },
    "gfx": {
        "color": "#fbbf6b",
        "ru": ("Компьютерная графика",
               "Террейн, глобальное освещение, разрушения, вода и объёмные облака."),
        "en": ("Computer graphics",
               "Terrain, global illumination, destruction, water and volumetric clouds."),
    },
    "network": {
        "color": "#fda4af",
        "ru": ("Сетевое взаимодействие",
               "Транспорты и топологии, предсказание и rollback, лаг-компенсация, "
               "interest management, шардинг, БД, античит и эксплуатация MMO."),
        "en": ("Networked multiplayer",
               "Transports and topologies, prediction and rollback, lag compensation, "
               "interest management, sharding, databases, anti-cheat and MMO operations."),
    },
    "procgen": {
        "color": "#6ee7b7",
        "ru": ("Процедурная генерация",
               "Шум, пещеры, подземелья, рельеф, биомы, города, предметы, имена, "
               "квесты и музыка — полный атлас алгоритмов."),
        "en": ("Procedural generation",
               "Noise, caves, dungeons, terrain, biomes, cities, items, names, "
               "quests and music — the complete algorithm atlas."),
    },
    "physics": {
        "color": "#a5b4fc",
        "ru": ("Физические симуляции",
               "Ткань, аэродинамика, поля и теплопередача."),
        "en": ("Physical simulations",
               "Cloth, aerodynamics, fields and heat transfer."),
    },
    "optimize": {
        "color": "#fcd34d",
        "ru": ("Системы оптимизации",
               "Бюджет кадра, батчинг, отсечение, data-oriented design, потоки и память."),
        "en": ("Optimisation systems",
               "Frame budget, batching, culling, data-oriented design, threads and memory."),
    },
    "math": {
        "color": "#c4b5fd",
        "ru": ("Математические механики",
               "Порталы, топология, запутанность и хаос как игровые правила."),
        "en": ("Mathematical mechanics",
               "Portals, topology, entanglement and chaos as gameplay rules."),
    },
    "stats": {
        "color": "#f9a8d4",
        "ru": ("Статистика и баланс",
               "Оружие, матчмейкинг, прогнозы и лут."),
        "en": ("Statistics and balance",
               "Weapons, matchmaking, forecasts and loot."),
    },
    "geometry": {
        "color": "#93c5fd",
        "ru": ("Геометрия и коллизии",
               "Видимость, рикошеты и воксельные миры."),
        "en": ("Geometry and collisions",
               "Visibility, ricochets and voxel worlds."),
    },
    "shaders": {
        "color": "#fb923c",
        "ru": ("Шейдеры и GPU",
               "Процедурные материалы, искажения пространства и оптика."),
        "en": ("Shaders and GPU",
               "Procedural materials, space distortion and optics."),
    },
    "economy": {
        "color": "#bef264",
        "ru": ("Игровые экономики",
               "Аукционы, распределение ресурсов и инфляция."),
        "en": ("Game economies",
               "Auctions, resource allocation and inflation."),
    },
    "audio": {
        "color": "#5eead4",
        "ru": ("Аудио-системы",
               "Пространственный звук и физическое моделирование инструментов."),
        "en": ("Audio systems",
               "Spatial sound and physical modelling of instruments."),
    },
    "ml": {
        "color": "#a78bfa",
        "ru": ("Нейросетевые приложения",
               "Генерация контента и апскейлинг в реальном времени."),
        "en": ("Neural network applications",
               "Content generation and real-time upscaling."),
    },
    "balance": {
        "color": "#e879f9",
        "ru": ("Баланс и прогрессия",
               "Урон и защита, кривые опыта и роста, награды, экономика, "
               "мета-баланс: математика, которой держится ощущение игры."),
        "en": ("Balance and progression",
               "Damage and defence, XP and growth curves, rewards, economy and "
               "meta-balance: the maths that holds the feel of a game together."),
    },
    "genres": {
        "color": "#facc15",
        "ru": ("Атлас жанров",
               "Шестнадцать семейств жанров: цикл, темп, ключевые числа и типичные "
               "поломки — от шутеров и стратегий до симуляторов и пати-игр."),
        "en": ("Genre atlas",
               "Thirty-six genre dossiers: loop, tempo, key numbers and the usual "
               "breakages — from shooters and strategies to sims and party games."),
    },
    "styles": {
        "color": "#60a5fa",
        "ru": ("Стиль и студия промптов",
               "Шесть слоёв визуального языка, пресеты и конструктор, который "
               "собирает из досье готовый промпт для игры."),
        "en": ("Style and the prompt studio",
               "Six layers of visual language, presets and a composer that turns "
               "the dossier into a ready-to-use game prompt."),
    },
    "heavy": {
        "color": "#4ade80",
        "ru": ("Тяжёлые нагрузки и GPU",
               "Compute shaders, миллионы частиц, GPU-driven pipeline, readback и масштабирование качества."),
        "en": ("Heavy workloads and GPU",
               "Compute shaders, millions of particles, GPU-driven pipeline, readback and quality scaling."),
    },
}

# порядок разделов в документе.
# "procgen" намеренно стоит последним: это отдельная часть исследования
# (Part II), а не ещё одна глава среди систем.
CHAPTER_ORDER = [
    "mechanics", "ai", "gfx", "physics", "optimize",
    "math", "stats", "geometry", "shaders", "economy", "audio", "ml", "heavy",
    "procgen", "network", "balance", "genres", "styles",
]

# --------------------------------------------------------------------------
# отдельная часть: процедурная генерация
# --------------------------------------------------------------------------
PART_OF = {"procgen": "procgen", "network": "network",
           "balance": "balance", "genres": "genres"}

PARTS = {
    "procgen": {
        "kicker": {"ru": "Часть II · атлас алгоритмов", "en": "Part II · algorithm atlas"},
        "title": {"ru": "Процедурная генерация", "en": "Procedural generation"},
        "subtitle": {
            "ru": "Всё, что игра придумывает сама",
            "en": "Everything the game invents by itself",
        },
        "lede": {
            "ru": ("Здесь собрано всё знание о генерации контента: шум и поля, "
                   "сэмплирование и детерминизм, пещеры и подземелья, лабиринты, WFC, "
                   "рельеф и эрозия, биомы, реки, планеты, воксели, города, растения, "
                   "фасады и shape-грамматики, предметы, имена, квесты, музыка и "
                   "AI-директор. Каждая тема — "
                   "модель, формула, пошаговая сборка, рабочий код и живая модель "
                   "в браузере. Темы сгруппированы в четыре слоя: от фундамента "
                   "до контента и драматургии."),
            "en": ("All the knowledge about content generation in one place: noise and "
                   "fields, sampling and determinism, caves and dungeons, mazes, WFC, "
                   "terrain and erosion, biomes, rivers, planets, voxels, cities, "
                   "plants, facades and shape grammars, items, names, quests, music "
                   "and the AI director. Every "
                   "topic ships a model, a formula, a step-by-step build, working code "
                   "and a live in-browser model. Topics are grouped into four layers, "
                   "from the foundation up to content and drama."),
        },
        "guide_title": {"ru": "Что генерируем → чем", "en": "What you generate → with what"},
        "guide_hint": {"ru": "быстрый выбор алгоритма", "en": "a quick algorithm chooser"},
        "note": {
            "ru": ("Все остальные разделы — «Часть I: системы». Процедурная генерация "
                   "выделена отдельно, потому что это не одна механика, а сквозная "
                   "дисциплина: одни и те же приёмы дают рельеф, лут, уровни и музыку."),
            "en": ("All other sections form “Part I: systems”. Procedural generation is "
                   "kept apart because it is not a single mechanic but a cross-cutting "
                   "discipline: the same techniques produce terrain, loot, levels and music."),
        },
    },
    "network": {
        "kicker": {"ru": "Часть III · сетевой плейбук", "en": "Part III · multiplayer playbook"},
        "title": {"ru": "Сетевое взаимодействие", "en": "Networked multiplayer"},
        "subtitle": {"ru": "Как игра договаривается сама с собой", "en": "How the game agrees with the game"},
        "lede": {
            "ru": ("Всё о сети: транспорты UDP, TCP и QUIC, надёжность и congestion control, "
                   "топологии dedicated / listen / P2P / relay, NAT и ICE; предсказание, "
                   "лаг-компенсация, интерполяция и rollback; interest management, тики и "
                   "часы; шардинг, бесшовные миры, сессии и матчмейкинг, персистентность MMO, "
                   "защита от читеров и DDoS, наблюдаемость и нагрузочные боты. Каждая тема — "
                   "модель, формула, код и живая модель в браузере."),
            "en": ("Everything about networking: UDP, TCP and QUIC transports, reliability and "
                   "congestion control, dedicated / listen / P2P / relay topologies, NAT and ICE; "
                   "prediction, lag compensation, interpolation and rollback; interest management, "
                   "ticks and clocks; sharding, seamless worlds, sessions and matchmaking, MMO "
                   "persistence, anti-cheat and DDoS defence, observability and load bots. Every "
                   "topic ships a model, a formula, working code and a live in-browser model."),
        },
        "note": {
            "ru": ("Часть I — системы, Часть II — генерация. Сеть выделена отдельно: это не "
                   "«ещё одна механика», а инфраструктура, которая определяет, какие механики "
                   "вообще возможны. Секреты больших MMO — не в одном трюке, а в бюджете "
                   "задержки, полосы и доверия, который проектируется целиком."),
            "en": ("Part I covers systems, Part II covers generation. Networking is separate "
                   "because it is not another mechanic but the infrastructure that decides which "
                   "mechanics are even possible. The secrets of large MMOs are not a single trick "
                   "but a latency, bandwidth and trust budget designed end to end."),
        },
        "guide_title": {"ru": "Что синхронизируем → как", "en": "What you synchronise → how"},
        "guide_hint": {"ru": "быстрый выбор модели", "en": "a quick model chooser"},
        "guide_note": {
            "ru": ("Модель выбирается под жанр и бюджет задержки, а не по моде. Шутер без "
                   "предсказания ощущается «резиновым», RTS без детерминизма расходится, "
                   "MMO без interest management тонет в трафике."),
            "en": ("Pick the model by genre and latency budget, not by fashion. A shooter without "
                   "prediction feels rubbery, an RTS without determinism desyncs, an MMO without "
                   "interest management drowns in traffic."),
        },
    },
    "balance": {
        "kicker": {"ru": "Часть IV · математика баланса", "en": "Part IV · the maths of balance"},
        "title": {"ru": "Баланс и прогрессия", "en": "Balance and progression"},
        "subtitle": {
            "ru": "Почему числа ощущаются именно так",
            "en": "Why the numbers feel the way they do",
        },
        "lede": {
            "ru": ("Двадцать четыре темы о том, как числа превращаются в ощущение: броня и "
                   "кривая смягчения, слои формулы урона, TTK и STK, разброс и DoT; щиты, "
                   "контроль и бюджет живучести; кривая опыта, рост статов, мягкие капы, "
                   "бюджет очков и темп прогрессии; награды, редкость, гача, валюты, "
                   "инфляция и гринд; степенной рост силы, сложность, боссы, PvP и "
                   "симуляция. Каждая тема — формула, пошаговая сборка, рабочий код и "
                   "живая модель, которую можно крутить."),
            "en": ("Twenty-four topics about how numbers become feeling: armour and the "
                   "mitigation curve, damage-formula layers, TTK and STK, variance and DoT; "
                   "shields, crowd control and the survivability budget; the XP curve, stat "
                   "growth, soft caps, point budgets and pacing; rewards, rarity, gacha, "
                   "currencies, inflation and grind; power creep, difficulty, bosses, PvP "
                   "and simulation. Every topic ships a formula, a step-by-step build, "
                   "working code and a live model you can twist."),
        },
        "guide_title": {"ru": "Что болит → чем лечить", "en": "What hurts → what fixes it"},
        "guide_hint": {"ru": "быстрый выбор инструмента", "en": "a quick tool chooser"},
        "note": {
            "ru": ("Баланс — не «подкрутить числа», а спроектировать кривые так, чтобы "
                   "игрок чувствовал рост, а система не ломалась. Формулы здесь даны в "
                   "игровых единицах: TTK в секундах, урон в «ударах», экономика — в "
                   "золоте за час."),
            "en": ("Balance is not “tweaking numbers” but designing curves so the player "
                   "feels growth while the system does not break. Formulas here use game "
                   "units: TTK in seconds, damage in “hits”, economy in gold per hour."),
        },
    },
    "genres": {
        "kicker": {"ru": "Часть V · атлас жанров", "en": "Part V · genre atlas"},
        "title": {"ru": "Атлас жанров", "en": "Genre atlas"},
        "subtitle": {"ru": "Тридцать шесть способов играть", "en": "Thirty-six ways to play"},
        "lede": {
            "ru": ("Каждый жанр описан по одной схеме: цикл, сессия, ритм, ключевые числа, "
                   "типичные поломки и референсы. Это не энциклопедические статьи, а "
                   "карточки для решений: что именно делает жанр собой, какие числа его "
                   "держат и где он обычно ломается. Жанры сгруппированы по шести "
                   "семействам — от экшена до социальных игр."),
            "en": ("Every genre is described with the same structure: loop, session, tempo, "
                   "key numbers, typical breakages and references. These are not "
                   "encyclopedia entries but decision cards: what makes the genre itself, "
                   "which numbers hold it together and where it usually breaks. Genres are "
                   "grouped into six families, from action to social games."),
        },
        "guide_title": {"ru": "Чего хочу → в каком жанре", "en": "What I want → which genre"},
        "guide_hint": {"ru": "быстрый выбор жанра", "en": "a quick genre chooser"},
        "note": {
            "ru": ("Жанр — это контракт с игроком: он обещает определённый темп, тип "
                   "решений и цену ошибки. Смешивать жанры можно, но обещание должно "
                   "остаться одним; иначе игрок не понимает, во что играет."),
            "en": ("A genre is a contract with the player: it promises a tempo, a type of "
                   "decision and a price for mistakes. Genres can be mixed, but the promise "
                   "must stay single — otherwise the player cannot tell what they are playing."),
        },
    },
}

# группы внутри части (порядок важен)
PG_GROUP_ORDER = ["foundation", "layout", "world", "content"]

# порядок тем внутри части: от фундамента к контенту.
# Он же задаёт номера PG-01…PG-27 на странице.
PG_ORDER = [
    # foundation
    "noise", "worley", "poisson", "seeds", "diamondsquare", "textures",
    # layout
    "caves", "bsp", "randomwalk", "maze", "wfc", "city", "maps",
    # world
    "terrain", "erosion", "biomes", "rivers", "clouds", "planets", "voxels",
    # content
    "lsystem", "shapegrammar", "items", "names", "quests", "music", "ecosystem", "director",
]

PG_GROUPS = {
    "foundation": {
        "color": "#6ee7b7",
        "num": "01",
        "ru": ("Шум, поля и выборки",
               "Градиентный и клеточный шум, фракталы, blue noise, детерминированные "
               "хэши и процедурные материалы. Фундамент, на котором стоят остальные алгоритмы."),
        "en": ("Noise, fields and sampling",
               "Gradient and cellular noise, fractals, blue noise, deterministic hashes "
               "and procedural materials. The foundation every other algorithm stands on."),
    },
    "layout": {
        "color": "#7dd3fc",
        "num": "02",
        "ru": ("Планировка: пещеры, подземелья, карты",
               "Клеточные автоматы, BSP, пьяная прогулка, лабиринты, Wave Function Collapse "
               "и дорожные сети: как из пустоты получить проходимое пространство."),
        "en": ("Layout: caves, dungeons, maps",
               "Cellular automata, BSP, drunkard's walk, mazes, Wave Function Collapse "
               "and road networks: turning emptiness into traversable space."),
    },
    "world": {
        "color": "#fbbf6b",
        "num": "03",
        "ru": ("Миры и рельеф",
               "Высоты и эрозия, биомы и реки, планеты, воксели и объёмные облака — "
               "от карты высот до целой солнечной системы."),
        "en": ("Worlds and terrain",
               "Heights and erosion, biomes and rivers, planets, voxels and volumetric "
               "clouds — from a heightmap to a whole solar system."),
    },
    "content": {
        "color": "#c4b5fd",
        "num": "04",
        "ru": ("Контент и системы",
               "L-системы и shape-грамматики, фасады и интерьеры, предметы и аффиксы, "
               "имена и языки, квесты и миссионные графы, музыка, экосистемы и AI-директор."),
        "en": ("Content and systems",
               "L-systems and shape grammars, facades and interiors, items and affixes, "
               "names and languages, quests and mission graphs, music, ecosystems and "
               "the AI director."),
    },
}

# «что нужно сгенерировать → чем»
PG_DECISIONS = [
    {"ru": ("Органичный рельеф, острова, горы", "fBm-шум, domain warping, diamond-square, эрозия"),
     "en": ("Organic terrain, islands, mountains", "fBm noise, domain warping, diamond-square, erosion")},
    {"ru": ("Пещеры и каверны", "клеточные автоматы, marching cubes, шум Ворли"),
     "en": ("Caves and caverns", "cellular automata, marching cubes, Worley noise")},
    {"ru": ("Подземелье с комнатами и коридорами", "BSP, граф комнат, WFC, шаблоны"),
     "en": ("A dungeon with rooms and corridors", "BSP, room graph, WFC, hand-made templates")},
    {"ru": ("Лабиринт", "recursive backtracker, Прим, Крускал, Уилсон"),
     "en": ("A maze", "recursive backtracker, Prim, Kruskal, Wilson")},
    {"ru": ("Карта с регионами и фракциями", "Вороной + Ллойд, граф-разбиение, MST, симметрия"),
     "en": ("A map with regions and factions", "Voronoi + Lloyd, graph partition, MST, symmetry")},
    {"ru": ("Равномерно разбросанные объекты", "Пуассон-диск (Бридсон), blue noise, jittered grid"),
     "en": ("Evenly scattered objects", "Poisson disk (Bridson), blue noise, jittered grid")},
    {"ru": ("Город и сеть дорог", "Пуассон + MST, A* по сетке, L-системы, Вороной"),
     "en": ("A city and its road network", "Poisson + MST, grid A*, L-systems, Voronoi")},
    {"ru": ("Фасады, дома и интерьеры", "shape-грамматика, split-правила, WFC, L-системы"),
     "en": ("Facades, buildings and interiors", "shape grammar, split rules, WFC, L-systems")},
    {"ru": ("Сбалансированные предметы и лут", "бюджет редкости, аффиксы, PRD, таблицы наград"),
     "en": ("Balanced items and loot", "rarity budget, affixes, PRD, reward tables")},
    {"ru": ("Имена, языки, топонимы", "слоговая грамматика, цепи Маркова, шаблоны"),
     "en": ("Names, languages, toponyms", "syllable grammar, Markov chains, templates")},
    {"ru": ("Сюжет, миссии, ключи и двери", "миссионный граф, lock-and-key, грамматики"),
     "en": ("Plot, missions, keys and doors", "mission graph, lock-and-key, grammars")},
    {"ru": ("Музыка и ритм", "цепи Маркова, L-системы, клеточные автоматы, генеративная гармония"),
     "en": ("Music and rhythm", "Markov chains, L-systems, cellular automata, generative harmony")},
    {"ru": ("Всё должно воспроизводиться", "seeded PRNG, hash(seed, coord), фиксированный порядок обхода"),
     "en": ("Everything must reproduce", "seeded PRNG, hash(seed, coord), fixed iteration order")},
]

# --------------------------------------------------------------------------
# Часть III: сеть — слои, порядок, сценарии выбора
# --------------------------------------------------------------------------
NET_GROUP_ORDER = ["transport", "sync", "realtime", "scale"]

NET_GROUPS = {
    "transport": {
        "color": "#fda4af",
        "num": "01",
        "ru": ("Транспорт и топология",
               "UDP, TCP, QUIC и WebTransport; надёжность и congestion control; dedicated, "
               "listen, P2P и relay; NAT, STUN, TURN и ICE; браузер и мобильные сети."),
        "en": ("Transport and topology",
               "UDP, TCP, QUIC and WebTransport; reliability and congestion control; dedicated, "
               "listen, P2P and relay; NAT, STUN, TURN and ICE; browsers and mobile radio."),
    },
    "sync": {
        "color": "#c4b5fd",
        "num": "02",
        "ru": ("Модели синхронизации",
               "Детерминированный lockstep, клиентское предсказание с примирением, "
               "дельта-снапшоты, rollback и фиксированная точка вместо float."),
        "en": ("Synchronisation models",
               "Deterministic lockstep, client-side prediction and reconciliation, delta "
               "snapshots, rollback and fixed point instead of floats."),
    },
    "realtime": {
        "color": "#7dd3fc",
        "num": "03",
        "ru": ("Реальное время",
               "Интерполяция и jitter buffer, лаг-компенсация с rewind, interest management, "
               "синхронизация часов и тиков, бюджет полосы и приоритизация."),
        "en": ("Real-time techniques",
               "Interpolation and jitter buffers, lag compensation with rewind, interest "
               "management, clock and tick sync, bandwidth budget and prioritisation."),
    },
    "scale": {
        "color": "#fbbf6b",
        "num": "04",
        "ru": ("Масштаб и эксплуатация",
               "Шардинг и бесшовные миры, сессии и матчмейкинг, персистентность MMO, "
               "античит, DDoS и rate limit, наблюдаемость, нагрузочные боты и live-ops."),
        "en": ("Scale and operations",
               "Sharding and seamless worlds, sessions and matchmaking, MMO persistence, "
               "anti-cheat, DDoS and rate limits, observability, load bots and live ops."),
    },
}

# порядок тем внутри части III (он же задаёт номера NET-01 …)
NET_ORDER = [
    # transport
    "nettransport", "netreliable", "nettopology", "netnat", "netbrowser",
    # sync
    "lockstep", "prediction", "snapshot", "netrollback", "netdeterminism",
    # realtime
    "netinterp", "netlagcomp", "netaoi", "netclock", "netbudget",
    # scale
    "netshard", "netsession", "netpersist", "anticheat", "netsecurity",
    "netops", "nettest",
]

NET_DECISIONS = [
    {"ru": ("Шутер 5v5 с быстрым движением", "client prediction + lag compensation, 30–60 Гц"),
     "en": ("Fast 5v5 shooter", "client prediction + lag compensation, 30–60 Hz")},
    {"ru": ("Файтинг или спорт", "rollback netcode, фиксированная точка и детерминизм"),
     "en": ("Fighting or sports game", "rollback netcode, fixed point and determinism")},
    {"ru": ("RTS или MOBA", "lockstep + контрольные суммы, детерминированная симуляция"),
     "en": ("RTS or MOBA", "lockstep + checksums, deterministic simulation")},
    {"ru": ("MMO на тысячи игроков", "шардинг, interest management, дельта-снапшоты, БД"),
     "en": ("An MMO with thousands of players", "sharding, interest management, delta snapshots, DB")},
    {"ru": ("Кооп на 2–8 игроков", "listen-сервер или relay, авторитет у хоста"),
     "en": ("2–8 player co-op", "listen server or relay, host authority")},
    {"ru": ("Игра в браузере", "WebSocket, WebRTC data channels, WebTransport"),
     "en": ("Browser game", "WebSocket, WebRTC data channels, WebTransport")},
    {"ru": ("Мобильные сессии и метро", "терпимость к потере пакетов, reconnect, пауза"),
     "en": ("Mobile sessions and radio", "packet-loss tolerance, reconnect, pause")},
    {"ru": ("Открытый мир без загрузок", "бесшовные зоны, handoff, кэш соседей"),
     "en": ("Seamless open world", "seamless zones, handoff, neighbour cache")},
    {"ru": ("Экономика и инвентарь", "транзакции, идемпотентность, event sourcing"),
     "en": ("Economy and inventory", "transactions, idempotency, event sourcing")},
    {"ru": ("Матчмейкинг и рейтинг", "рейтинг + регион + backfill после лива"),
     "en": ("Matchmaking and rating", "rating + region + backfill after a leaver")},
    {"ru": ("Читеры, боты и абуз", "server authority, статистика, rate limit"),
     "en": ("Cheaters, bots and abuse", "server authority, statistics, rate limits")},
    {"ru": ("Релиз и DDoS", "anycast, лимиты, очереди, graceful degradation"),
     "en": ("Launch and DDoS", "anycast, limits, queues, graceful degradation")},
    {"ru": ("Отладка сети", "netem, chaos-тесты, нагрузочные боты, SLO"),
     "en": ("Network debugging", "netem, chaos tests, load bots, SLOs")},
]

# --------------------------------------------------------------------------
# Часть IV: баланс и прогрессия — слои, порядок, сценарии выбора
# --------------------------------------------------------------------------
BAL_GROUP_ORDER = ["damage", "defense", "progression", "rewards", "meta"]

BAL_GROUPS = {
    "damage": {
        "color": "#fb7185",
        "num": "01",
        "ru": ("Урон",
               "Смягчение, слои формулы, TTK и STK, разброс и периодический урон: "
               "как одно число превращается в ощущение боя."),
        "en": ("Damage",
               "Mitigation, formula layers, TTK and STK, variance and damage over "
               "time: how one number becomes the feel of combat."),
    },
    "defense": {
        "color": "#a5b4fc",
        "num": "02",
        "ru": ("Защита",
               "Щиты и регенерация, контроль с убывающей отдачей, бюджет живучести "
               "и капы: почему танк становится бессмертным."),
        "en": ("Defence",
               "Shields and regeneration, crowd control with diminishing returns, the "
               "survivability budget and caps: why a tank becomes immortal."),
    },
    "progression": {
        "color": "#6ee7b7",
        "num": "03",
        "ru": ("Прогрессия",
               "Кривая опыта, рост характеристик, мягкие капы, бюджет очков и темп "
               "прогрессии: расписание, по которому игра выдаёт силу."),
        "en": ("Progression",
               "The XP curve, stat growth, soft caps, point budgets and pacing: the "
               "schedule on which a game hands out power."),
    },
    "rewards": {
        "color": "#fbbf6b",
        "num": "04",
        "ru": ("Награды и экономика",
               "Награда за действие, полосы редкости, гача, валюты, инфляция и гринд: "
               "сколько стоит минута игры."),
        "en": ("Rewards and economy",
               "Reward per action, rarity bands, gacha, currencies, inflation and "
               "grind: what a minute of play is worth."),
    },
    "meta": {
        "color": "#c4b5fd",
        "num": "05",
        "ru": ("Мета-баланс",
               "Степенной рост силы, кривая сложности, тюнинг босса, PvP и симуляция "
               "баланса: как удержать игру живой годами."),
        "en": ("Meta-balance",
               "Power creep, the difficulty curve, boss tuning, PvP and balance "
               "simulation: how to keep a game alive for years."),
    },
}

BAL_ORDER = [
    # damage
    "dmg-mitigation", "dmg-formula", "dmg-ehp", "dmg-variance", "dmg-dot",
    # defense
    "def-shield", "def-crowd", "def-budget",
    # progression
    "prog-xpcurve", "prog-growth", "prog-softcap", "prog-points", "prog-pacing",
    # rewards
    "bal-xpreward", "bal-lootband", "bal-gacha", "bal-currency", "bal-inflation", "bal-grind",
    # meta
    "bal-powercreep", "bal-difficulty", "bal-boss", "bal-pvp", "bal-sim",
]

# --------------------------------------------------------------------------
# Часть V: атлас жанров — семейства и порядок
# --------------------------------------------------------------------------
GENRE_GROUP_ORDER = ["action", "strategy", "rpg", "sim", "adventure", "sports"]

GENRE_GROUPS = {
    "action": {
        "color": "#fb7185",
        "num": "01",
        "ru": ("Экшен",
               "Шутеры, королевская битва, файтинги, платформеры, пулевой ад и слэшеры: "
               "жанры, где решают реакция, чтение сцены и темп."),
        "en": ("Action",
               "Shooters, battle royale, fighting games, platformers, bullet hell and "
               "slashers: genres decided by reflex, scene reading and tempo."),
    },
    "strategy": {
        "color": "#7dd3fc",
        "num": "02",
        "ru": ("Стратегии",
               "RTS, пошаговые 4X, MOBA, tower defense, автобаттлеры и варгеймы: "
               "жанры решений, экономики и информации."),
        "en": ("Strategy",
               "RTS, turn-based 4X, MOBA, tower defense, auto battlers and wargames: "
               "genres of decisions, economy and information."),
    },
    "rpg": {
        "color": "#a78bfa",
        "num": "03",
        "ru": ("Ролевые игры",
               "JRPG, CRPG, action RPG, MMO, souls-like и roguelite: рост персонажа, "
               "билды и цена ошибки."),
        "en": ("Role-playing",
               "JRPG, CRPG, action RPG, MMO, souls-like and roguelite: character "
               "growth, builds and the cost of a mistake."),
    },
    "sim": {
        "color": "#bef264",
        "num": "04",
        "ru": ("Симуляции",
               "Тайкуны, градостроительство, фабрики, симуляторы жизни, сурвайвал и "
               "песочницы: системы, которые отвечают числами."),
        "en": ("Simulations",
               "Tycoons, city builders, factories, life sims, survival and sandboxes: "
               "systems that answer in numbers."),
    },
    "adventure": {
        "color": "#fbbf6b",
        "num": "05",
        "ru": ("Приключения",
               "Метроидвании, головоломки, immersive sim, стелс, хоррор и нарративные "
               "игры: исследование, скрытность и история."),
        "en": ("Adventure",
               "Metroidvanias, puzzles, immersive sims, stealth, horror and narrative "
               "games: exploration, concealment and story."),
    },
    "sports": {
        "color": "#5eead4",
        "num": "06",
        "ru": ("Спорт и социальные игры",
               "Гонки, спортсимы, ритм-игры, карточные игры, idle и пати-игры: "
               "правила, соревнование и короткие сессии."),
        "en": ("Sports and social games",
               "Racing, sports sims, rhythm games, card games, idle and party games: "
               "rules, competition and short sessions."),
    },
}

GENRE_ORDER = [
    # action
    "g-fps", "g-br", "g-fighting", "g-platformer", "g-shmup", "g-hackslash",
    # strategy
    "g-rts", "g-tbs", "g-moba", "g-towerdef", "g-autobattler", "g-wargame",
    # rpg
    "g-jrpg", "g-crpg", "g-arpg", "g-mmo", "g-soulslike", "g-roguelike",
    # sim
    "g-sim", "g-citybuilder", "g-factory", "g-lifesim", "g-survival", "g-sandbox",
    # adventure
    "g-metroidvania", "g-puzzle", "g-imsim", "g-stealth", "g-horror", "g-narrative",
    # sports
    "g-racing", "g-sports", "g-rhythm", "g-ccg", "g-idle", "g-party",
]

# --------------------------------------------------------------------------
# уровни сложности
# --------------------------------------------------------------------------
LEVEL_LABEL = {
    1: {"ru": "база", "en": "basic"},
    2: {"ru": "средний", "en": "intermediate"},
    3: {"ru": "продвинутый", "en": "advanced"},
}

LEVELS_HINT = {
    1: {
        "ru": "Можно реализовать за вечер, математика на уровне школьной программы.",
        "en": "An evening of work, high-school level maths.",
    },
    2: {
        "ru": "Нужна аккуратность: интеграторы, вероятности, структуры данных.",
        "en": "Care is required: integrators, probabilities, data structures.",
    },
    3: {
        "ru": "Тяжёлая математика или серьёзная инженерия; читать после базы.",
        "en": "Heavy maths or serious engineering; read after the basics.",
    },
}

# --------------------------------------------------------------------------
# демо
# --------------------------------------------------------------------------
DEMO_TITLES = {
    "ballistics": {
        "ru": "Живая баллистика: угол, ветер, сопротивление",
        "en": "Live ballistics: angle, wind, drag",
    },
    "boids": {
        "ru": "Стая boids: три правила и пространственный поиск",
        "en": "Boids flock: three rules and spatial search",
    },
    "terrain": {
        "ru": "Генератор рельефа: fBm и уровень моря",
        "en": "Terrain generator: fBm and sea level",
    },
    "waves": {
        "ru": "Волновая поверхность: амплитуда, ветер, крутизна",
        "en": "Wave surface: amplitude, wind, steepness",
    },
    "lockstep": {
        "ru": "Lockstep: лаг, безопасный тик и desync",
        "en": "Lockstep: lag, safe tick and desync",
    },
    "transport": {
        "ru": "UDP против TCP и QUIC под потерями",
        "en": "UDP vs TCP and QUIC under loss",
    },
    "reliability": {
        "ru": "Надёжный канал: окно, ACK и RTO",
        "en": "Reliable channel: window, ACK and RTO",
    },
    "topology": {
        "ru": "Топологии: dedicated, listen, P2P и релей",
        "en": "Topologies: dedicated, listen, P2P and relay",
    },
    "nat": {
        "ru": "NAT: STUN, punch и дорога через TURN",
        "en": "NAT: STUN, punch and the TURN detour",
    },
    "rollback": {
        "ru": "Rollback: поздний ввод и ресимуляция",
        "en": "Rollback: late input and resimulation",
    },
    "interp": {
        "ru": "Интерполяция и буфер против джиттера",
        "en": "Interpolation and the jitter buffer",
    },
    "lagcomp": {
        "ru": "Лаг-компенсация и окно отката",
        "en": "Lag compensation and the rewind window",
    },
    "aoi": {
        "ru": "Interest management: круг видимости",
        "en": "Interest management: circle of relevance",
    },
    "budget": {
        "ru": "Бюджет трафика и приоритеты",
        "en": "Bandwidth budget and priorities",
    },
    "shard": {
        "ru": "Шардинг мира и передача на границе",
        "en": "World sharding and border handoff",
    },
    "session": {
        "ru": "Очередь матчмейкера и окно MMR",
        "en": "Matchmaking queue and the MMR window",
    },
    "security": {
        "ru": "Token bucket против флуда и DDoS",
        "en": "Token bucket against floods and DDoS",
    },
    "planets": {
        "ru": "Орбиты Кеплера и зона обитаемости",
        "en": "Kepler orbits and the habitable zone",
    },
    "maps": {
        "ru": "Симметричная карта и метрика баланса",
        "en": "Symmetric map and balance metric",
    },
    "ecosystem": {
        "ru": "Лотка–Вольтерра: циклы хищник–жертва",
        "en": "Lotka–Volterra: predator–prey cycles",
    },
    "cloth": {
        "ru": "Ткань на Verlet: ветер и итерации",
        "en": "Cloth on Verlet: wind and iterations",
    },
    "portal": {
        "ru": "Портал как преобразование пространства",
        "en": "A portal as a space transform",
    },
    "chaos": {
        "ru": "Бифуркационная диаграмма и показатель Ляпунова",
        "en": "Bifurcation diagram and Lyapunov exponent",
    },
    "elo": {
        "ru": "Elo: K-фактор и истинная разница скилла",
        "en": "Elo: K-factor and true skill difference",
    },
    "trend": {
        "ru": "Временной ряд и сезонный прогноз",
        "en": "Time series and seasonal forecast",
    },
    "loot": {
        "ru": "Pity-лут: распределение попыток до легендарки",
        "en": "Pity loot: attempts until the legendary drop",
    },
    "voxel": {
        "ru": "Marching squares: изоуровень поля плотности",
        "en": "Marching squares: density field isolevel",
    },
    "auction": {
        "ru": "Аукцион Викри против первой цены",
        "en": "Vickrey auction vs first price",
    },
    "gpuparticles": {
        "ru": "Compute-симуляция частиц: WebGPU, WebGL2 или CPU",
        "en": "Compute particle sim: WebGPU, WebGL2 or CPU",
    },
    "framebudget": {
        "ru": "Бюджет кадра: кто съедает 16.6 мс",
        "en": "Frame budget: who eats the 16.6 ms",
    },
    "culling": {
        "ru": "Отсечение: frustum, occlusion и LOD",
        "en": "Culling: frustum, occlusion and LOD",
    },
    "drawcalls": {
        "ru": "Batching: из тысячи вызовов в десяток",
        "en": "Batching: from a thousand calls to ten",
    },

    # ---------- часть II: процедурная генерация ----------
    "noise": {
        "ru": "Градиентный шум: value, Perlin, simplex и октавы",
        "en": "Gradient noise: value, Perlin, simplex and octaves",
    },
    "worley": {
        "ru": "Клеточный шум Ворли: F1, F2 и границы ячеек",
        "en": "Worley cellular noise: F1, F2 and cell borders",
    },
    "poisson": {
        "ru": "Пуассон-диск: Бридсон против белого шума",
        "en": "Poisson disk: Bridson versus white noise",
    },
    "pcg": {
        "ru": "Хэш и сид: воспроизводимость и лавинный эффект",
        "en": "Hash and seed: reproducibility and avalanche",
    },
    "materials": {
        "ru": "Процедурный материал: кирпич, дерево, металл",
        "en": "Procedural material: brick, wood, metal",
    },
    "diamondsquare": {
        "ru": "Diamond-square: шероховатость и высоты",
        "en": "Diamond-square: roughness and heights",
    },
    "caves": {
        "ru": "Клеточные автоматы: пещера за пять шагов",
        "en": "Cellular automata: a cave in five steps",
    },
    "bsp": {
        "ru": "BSP-подземелье: разбиение, комнаты, коридоры",
        "en": "BSP dungeon: splits, rooms, corridors",
    },
    "randomwalk": {
        "ru": "Пьяная прогулка: сколько шагов нужно пещере",
        "en": "Drunkard's walk: how many steps a cave needs",
    },
    "maze": {
        "ru": "Лабиринт: backtracker, Прим, Крускал, Уилсон",
        "en": "Maze: backtracker, Prim, Kruskal, Wilson",
    },
    "wfc": {
        "ru": "Wave Function Collapse: энтропия и откат",
        "en": "Wave Function Collapse: entropy and backtracking",
    },
    "city": {
        "ru": "Город: Вороной, MST-дороги и кварталы",
        "en": "City: Voronoi, MST roads and blocks",
    },
    "erosion": {
        "ru": "Гидравлическая эрозия: капли, наносы, дельты",
        "en": "Hydraulic erosion: droplets, sediment, deltas",
    },
    "biomes": {
        "ru": "Биомы: диаграмма Уиттекера и карта мира",
        "en": "Biomes: Whittaker diagram and the world map",
    },
    "rivers": {
        "ru": "Реки: сток, водосборы и русла",
        "en": "Rivers: flow, watersheds and channels",
    },
    "lsystem": {
        "ru": "L-система: дерево, папоротник, кривая Гильберта",
        "en": "L-system: a tree, a fern, the Hilbert curve",
    },
    "items": {
        "ru": "Генератор предметов: редкость, аффиксы, бюджет",
        "en": "Item generator: rarity, affixes, budget",
    },
    "names": {
        "ru": "Генератор имён: слоги и цепь Маркова",
        "en": "Name generator: syllables and a Markov chain",
    },
    "quests": {
        "ru": "Миссионный граф: ключи, двери и ветвление",
        "en": "Mission graph: keys, doors and branching",
    },
    "clouds": {
        "ru": "Объёмные облака: два слоя fBm с domain warping",
        "en": "Volumetric clouds: two fBm layers with domain warping",
    },
    "shapegrammar": {
        "ru": "Shape-грамматика: фасад из правил разбиения",
        "en": "Shape grammar: a facade built from split rules",
    },
    "musicgen": {
        "ru": "Генеративная музыка: цепь Маркова и пентатоника",
        "en": "Generative music: Markov chain and pentatonic",
    },
    "director": {
        "ru": "AI-директор: кривая напряжения и волны врагов",
        "en": "AI director: tension curve and enemy waves",
    },
}

# --------------------------------------------------------------------------
# словарь терминов
# --------------------------------------------------------------------------
GLOSSARY = [
    {"ru": ("A*", "Поиск кратчайшего пути по эвристике h(n): f(n) = g(n) + h(n). Допустимая эвристика не переоценивает остаток."),
     "en": ("A*", "Shortest-path search with a heuristic h(n): f(n) = g(n) + h(n). An admissible heuristic never overestimates the remaining cost.")},
    {"ru": ("ECS", "Entity Component System: сущность — идентификатор, компоненты — данные, системы — логика. Даёт кэш-локальность и композицию."),
     "en": ("ECS", "Entity Component System: entity — an id, components — data, systems — logic. Gives cache locality and composition.")},
    {"ru": ("DOD", "Data-Oriented Design: сначала раскладка данных в памяти под обход, потом код. Основа производительных симуляций."),
     "en": ("DOD", "Data-Oriented Design: lay out memory for the traversal first, code second. The base of fast simulations.")},
    {"ru": ("Fixed-point", "Арифметика с фиксированной запятой (Q16.16): детерминирована между платформами, в отличие от float."),
     "en": ("Fixed-point", "Fixed-point arithmetic (Q16.16): deterministic across platforms, unlike float.")},
    {"ru": ("Lockstep", "Схема, где клиенты обмениваются только командами и считают одинаковую симуляцию; состояние не передаётся."),
     "en": ("Lockstep", "Clients exchange only commands and simulate the same world; state is never transmitted.")},
    {"ru": ("Rollback", "Пересимуляция неподтверждённых вводов после снапшота сервера; основа клиентского предсказания."),
     "en": ("Rollback", "Resimulating unconfirmed inputs from a server snapshot; the basis of client-side prediction.")},
    {"ru": ("Verlet", "Интегрирование по позициям: x′ = 2x − x_prev + a·dt². Устойчиво, удобно для ограничений."),
     "en": ("Verlet", "Position-based integration: x′ = 2x − x_prev + a·dt². Stable, convenient for constraints.")},
    {"ru": ("PBD / XPBD", "Position-Based Dynamics: ограничения проецируются на позиции; XPBD делает жёсткость независимой от итераций."),
     "en": ("PBD / XPBD", "Position-Based Dynamics: constraints are projected onto positions; XPBD makes stiffness iteration-independent.")},
    {"ru": ("SPH", "Smoothed Particle Hydrodynamics: жидкость как частица с ядром сглаживания и давлением."),
     "en": ("SPH", "Smoothed Particle Hydrodynamics: a fluid as particles with a smoothing kernel and pressure.")},
    {"ru": ("BVH", "Bounding Volume Hierarchy: дерево AABB для быстрого отсечения и raycast; строится по SAH."),
     "en": ("BVH", "Bounding Volume Hierarchy: an AABB tree for fast culling and raycasts; built with SAH.")},
    {"ru": ("SAH", "Surface Area Heuristic: критерий качества разбиения BVH по площади оболочек."),
     "en": ("SAH", "Surface Area Heuristic: a BVH split quality criterion based on bounding surface area.")},
    {"ru": ("MCTS / UCT", "Monte Carlo Tree Search с формулой UCT: баланс исследования и использования в дереве игры."),
     "en": ("MCTS / UCT", "Monte Carlo Tree Search with the UCT rule: balancing exploration and exploitation in a game tree.")},
    {"ru": ("Utility AI", "Выбор действия по взвешенной сумме нормированных факторов; альтернатива деревьям поведения."),
     "en": ("Utility AI", "Choosing an action by a weighted sum of normalised factors; an alternative to behaviour trees.")},
    {"ru": ("Flow field", "Поле направлений к цели на сетке: дешёвый путь для больших групп юнитов."),
     "en": ("Flow field", "A grid of directions towards a goal: cheap pathing for large groups of units.")},
    {"ru": ("WFC", "Wave Function Collapse: генерация по ограничениям с распространением возможностей и откатом."),
     "en": ("WFC", "Wave Function Collapse: constraint-based generation with propagation and backtracking.")},
    {"ru": ("SDF", "Signed Distance Field: функция расстояния до поверхности; удобна для CSG и ray marching."),
     "en": ("SDF", "Signed Distance Field: distance to a surface; convenient for CSG and ray marching.")},
    {"ru": ("Marching cubes", "Извлечение изоповерхности из сетки плотности по таблице 256 случаев."),
     "en": ("Marching cubes", "Extracting an isosurface from a density grid using a 256-case table.")},
    {"ru": ("PBR / BRDF", "Physically Based Rendering: энергосберегающие материалы; BRDF описывает отражение света."),
     "en": ("PBR / BRDF", "Physically Based Rendering: energy-conserving materials; the BRDF describes light reflection.")},
    {"ru": ("GGX", "Микрогранная модель распределения нормалей с длинным хвостом блика."),
     "en": ("GGX", "Microfacet normal distribution model with a long specular tail.")},
    {"ru": ("Ambisonics", "Кодирование 3D-звука сферическими гармониками (W, X, Y, Z) с декодированием под наушники/колонки."),
     "en": ("Ambisonics", "Encoding 3D audio in spherical harmonics (W, X, Y, Z) and decoding it for headphones or speakers.")},
    {"ru": ("HRTF", "Head-Related Transfer Function: фильтр, описывающий, как уши и голова окрашивают звук с направления."),
     "en": ("HRTF", "Head-Related Transfer Function: the filter describing how ears and head colour sound from a direction.")},
    {"ru": ("PRD", "Pseudo-Random Distribution: шанс растёт после неудач, снижая дисперсию серий без изменения среднего."),
     "en": ("PRD", "Pseudo-Random Distribution: the chance grows after failures, reducing streak variance without changing the mean.")},
    {"ru": ("Glicko-2 / TrueSkill", "Байесовские рейтинги с неопределённостью (RD/σ) и обновлением после матча."),
     "en": ("Glicko-2 / TrueSkill", "Bayesian ratings with uncertainty (RD/σ) updated after a match.")},
    {"ru": ("ARIMA", "Модель временного ряда: авторегрессия, дифференцирование и скользящее среднее ошибок."),
     "en": ("ARIMA", "Time-series model: autoregression, differencing and a moving average of errors.")},
    {"ru": ("GAN", "Соревнование генератора и дискриминатора; WGAN-GP stabilizes обучение через расстояние Вассерштейна."),
     "en": ("GAN", "Generator versus discriminator; WGAN-GP stabilises training via the Wasserstein distance.")},
    {"ru": ("FFT", "Быстрое преобразование Фурье: O(N log N); используется для океана, текстурирования и аудио."),
     "en": ("FFT", "Fast Fourier Transform: O(N log N); used for oceans, texturing and audio.")},
    {"ru": ("Perlin / fBm", "Градиентный шум и его фрактальная сумма октав; база процедурных ландшафтов и материалов."),
     "en": ("Perlin / fBm", "Gradient noise and its fractal sum of octaves; the base of procedural terrain and materials.")},
    {"ru": ("Кеплер", "T² = 4π²a³/(G(M+m)); уравнение M = E − e·sin E связывает время и положение на орбите."),
     "en": ("Kepler", "T² = 4π²a³/(G(M+m)); the equation M = E − e·sin E links time and position on the orbit.")},
    {"ru": ("Draw call", "Вызов отрисовки: одна порция геометрии с одним состоянием конвейера. Главная единица CPU-стоимости рендера."),
     "en": ("Draw call", "A draw submission: one batch of geometry with one pipeline state. The main unit of CPU render cost.")},
    {"ru": ("Compute shader", "Программа, выполняемая отдельным проходом по сетке данных; не привязана к геометрии."),
     "en": ("Compute shader", "A program executed as a separate pass over a grid of data; not bound to geometry.")},
    {"ru": ("Workgroup", "Группа потоков GPU, работающих вместе; барьер внутри группы почти бесплатен."),
     "en": ("Workgroup", "A group of GPU threads working together; a barrier inside the group is nearly free.")},
    {"ru": ("Stall", "Ожидание, при котором CPU или GPU простаивают в ожидании друг друга. Главный враг асинхронности."),
     "en": ("Stall", "A wait where the CPU or the GPU sits idle waiting for the other. The main enemy of asynchrony.")},
    {"ru": ("Hi-Z", "Пирамида глубины (max-depth reduction) предыдущего кадра; дешёвый источник occlusion-тестов."),
     "en": ("Hi-Z", "A max-depth reduction pyramid of the previous frame; a cheap source of occlusion tests.")},
    {"ru": ("False sharing", "Два потока пишут в разные поля одной кэш-линии и постоянно инвалидируют её друг другу."),
     "en": ("False sharing", "Two threads write to different fields of one cache line and keep invalidating it for each other.")},
    {"ru": ("Temporal reprojection", "Переиспользование результата прошлого кадра, спроецированного по движению камеры."),
     "en": ("Temporal reprojection", "Reusing last frame's result reprojected along camera motion.")},
    {"ru": ("OIT", "Order-Independent Transparency: прозрачность без сортировки, через накопление весов и деление."),
     "en": ("OIT", "Order-Independent Transparency: transparency without sorting, via weighted accumulation and division.")},
    {"ru": ("A/B test", "Сравнение двух вариантов на случайных подгруппах игроков: единственный честный способ проверить эффект."),
     "en": ("A/B test", "Comparing two variants on random player cohorts: the only honest way to verify an effect.")},
]

# --------------------------------------------------------------------------
# строки интерфейса и оболочки страницы
# --------------------------------------------------------------------------
STRINGS = {
    "skip": {"ru": "К содержанию", "en": "Skip to content"},
    "noscript": {
        "ru": "Интерактивные демо и поиск требуют JavaScript — текст, формулы и код читаются и без него.",
        "en": "Interactive demos and search need JavaScript — the text, formulas and code read fine without it.",
    },
    "brand_small": {"ru": "research dossier · 2026", "en": "research dossier · 2026"},
    "nav_overview": {"ru": "Обзор", "en": "Overview"},
    "nav_map": {"ru": "Карта", "en": "Map"},
    "nav_practice": {"ru": "Практика", "en": "Practice"},
    "nav_glossary": {"ru": "Словарь", "en": "Glossary"},
    "print_label": {"ru": "PDF", "en": "PDF"},
    "theme_light": {"ru": "светлая", "en": "light"},
    "theme_dark": {"ru": "тёмная", "en": "dark"},
    "theme_to_light": {"ru": "Включить светлую тему", "en": "Switch to the light theme"},
    "theme_to_dark": {"ru": "Включить тёмную тему", "en": "Switch to the dark theme"},
    "lang_other": {"ru": "English", "en": "Русский"},
    "lang_other_short": {"ru": "EN", "en": "RU"},
    "lang_other_aria": {"ru": "Переключить на английскую версию", "en": "Switch to the Russian version"},
    "eyebrow": {
        "ru": "полное исследование · геймдев-системы",
        "en": "full research · game-dev systems",
    },
    "hero_title_1": {"ru": "Алгоритмы, из которых", "en": "The algorithms behind"},
    "hero_title_2": {"ru": "сделаны ", "en": "the games "},
    "hero_title_emph": {"ru": "игры", "en": "you play"},
    "hero_lede": {
        "ru": ("{n} тем — от баллистики и boids до глобального освещения, lockstep и апскейлинга. "
               "Для каждой: математическая модель, пошаговая реализация, рабочий код, честная сложность, "
               "типичные ошибки и живая интерактивная модель в браузере. "
               "Части II и III — атласы процедурной генерации и сетевого кода; "
               "Часть IV — математика баланса и прогрессии; Часть V — атлас из 36 жанров; "
               "Часть VI — стиль и конструктор промптов."),
        "en": ("{n} topics — from ballistics and boids to global illumination, lockstep and upscaling. "
               "Each one: the mathematical model, a step-by-step implementation, working code, honest "
               "complexity, the usual mistakes and a live interactive model in the browser. "
               "Parts II and III are atlases of procedural generation and netcode; Part IV is the "
               "maths of balance and progression; Part V is an atlas of 36 genres; Part VI is style "
               "and a prompt composer."),
    },
    "hero_start": {"ru": "Начать изучение", "en": "Start reading"},
    "hero_procgen": {"ru": "Атлас генерации", "en": "Generation atlas"},
    "hero_network": {"ru": "Сетевой атлас", "en": "Network atlas"},
    "hero_tasks": {"ru": "{n} практических задач", "en": "{n} practical tasks"},
    "stat_topics": {"ru": "тем · {n} разделов", "en": "topics · {n} sections"},
    "stat_demos": {"ru": "интерактивных демо", "en": "interactive demos"},
    "stat_tasks": {"ru": "практических задач", "en": "practical tasks"},
    "stat_deps": {"ru": "внешних зависимостей", "en": "external dependencies"},
    "meta_desc": {
        "ru": ("Алгоритмы игр: {n} тем с математикой, кодом, сложностью и интерактивными демо; "
               "атласы процедурной генерации и сетевого кода, математика баланса, атлас 36 жанров "
               "и конструктор промптов."),
        "en": ("Game algorithms: {n} topics with maths, code, complexity and interactive demos; "
               "atlases of procedural generation and netcode, the maths of balance, an atlas of "
               "36 genres and a prompt composer."),
    },
    "level_of": {"ru": "уровень {n} из 3", "en": "level {n} of 3"},
    "side_content": {"ru": "Содержание", "en": "Contents"},
    "search_placeholder": {"ru": "Поиск: шум, lockstep, крит…", "en": "Search: noise, lockstep, crit…"},
    "search_aria": {"ru": "Поиск по темам", "en": "Search topics"},
    "level_all": {"ru": "все", "en": "all"},
    "level_1": {"ru": "база", "en": "basic"},
    "level_2": {"ru": "средний", "en": "medium"},
    "level_3": {"ru": "сложный", "en": "hard"},
    "cat_all": {"ru": "Все разделы · {n}", "en": "All sections · {n}"},
    "cat_aria": {"ru": "Фильтр по разделу", "en": "Filter by section"},
    "level_filter_aria": {"ru": "Фильтр по сложности", "en": "Filter by difficulty"},
    "progress": {"ru": "Прогресс", "en": "Progress"},
    "sections": {"ru": "Разделы", "en": "Sections"},
    "nav_procgen": {"ru": "Процедурная генерация", "en": "Procedural generation"},
    "nav_network": {"ru": "Сеть: MMO и netcode", "en": "Networking: MMO & netcode"},
    "nav_balance": {"ru": "Баланс и прогрессия", "en": "Balance & progression"},
    "nav_genres": {"ru": "Атлас жанров", "en": "Genre atlas"},
    "nav_styles": {"ru": "Стиль и промпты", "en": "Style & prompts"},
    "hero_balance": {"ru": "Математика баланса", "en": "Balance maths"},
    "hero_genres": {"ru": "Атлас жанров", "en": "Genre atlas"},
    "nav_procgen_short": {"ru": "Генерация", "en": "Generation"},
    "nav_network_short": {"ru": "Сеть", "en": "Netcode"},
    "nav_balance_short": {"ru": "Баланс", "en": "Balance"},
    "nav_genres_short": {"ru": "Жанры", "en": "Genres"},
    "part_label": {"ru": "часть {i}", "en": "part {i}"},
    "part_topics": {"ru": "{n} тем · {g} слоя", "en": "{n} topics · {g} layers"},
    "part_atlas_title": {"ru": "Атлас алгоритмов", "en": "Algorithm atlas"},
    "part_atlas_hint": {"ru": "все темы части одним взглядом", "en": "every topic of the part at a glance"},
    "part_guide_title": {"ru": "Что генерируем → чем", "en": "What you generate → with what"},
    "part_guide_hint": {"ru": "быстрый выбор алгоритма", "en": "a quick algorithm chooser"},
    "part_guide_note": {
        "ru": ("Таблица — не догма, а отправная точка: почти всегда решение складывается "
               "из двух-трёх приёмов (например, шум + эрозия + биомы)."),
        "en": ("The table is a starting point, not a law: almost always the answer combines "
               "two or three techniques (noise + erosion + biomes, for instance)."),
    },
    "part_group_topics": {"ru": "{n} тем", "en": "{n} topics"},
    "part_back": {"ru": "Часть II · Процедурная генерация", "en": "Part II · Procedural generation"},
    "part_card_kicker": {"ru": "отдельная часть", "en": "a separate part"},
    "part_stat_topics": {"ru": "тем", "en": "topics"},
    "part_stat_demos": {"ru": "интерактивных демо", "en": "interactive demos"},
    "part_stat_layers": {"ru": "слоёв", "en": "layers"},
    "part_stat_guide": {"ru": "сценариев выбора", "en": "algorithm recipes"},
    "part_stat_atoms": {"ru": "атомов стиля", "en": "style atoms"},
    "part_stat_presets": {"ru": "пресетов", "en": "presets"},
    "part_stat_formats": {"ru": "форматов", "en": "formats"},
    "part_minutes": {"ru": "{n} интерактивных моделей", "en": "{n} interactive models"},
    "part_filter": {"ru": "Слой", "en": "Layer"},
    "topic_part_of": {"ru": "{n} / {total} · часть {part}", "en": "{n} / {total} · part {part}"},
    "side_foot": {
        "ru": ("Документ работает офлайн: все стили, скрипты и демо встроены в один файл. "
               "Прогресс и тема хранятся локально в браузере."),
        "en": ("The document works offline: all styles, scripts and demos are embedded in one file. "
               "Progress and theme are stored locally in your browser."),
    },
    "how_title": {"ru": "Как читать это исследование", "en": "How to read this research"},
    "how_p": {
        "ru": ("Материал собран как инженерный справочник, а не как список терминов. Каждая тема отвечает "
               "на одни и те же шесть вопросов, поэтому их можно сравнивать между собой и использовать "
               "как чек-лист при реализации."),
        "en": ("The material is an engineering reference, not a list of terms. Every topic answers the same "
               "six questions, so topics can be compared with each other and used as an implementation checklist."),
    },
    "callout_structure": {
        "ru": ("«Суть» объясняет модель на пальцах; «математическая модель» даёт рабочие формулы; "
               "«как построить» — порядок действий; «рабочий код» — минимальный референс; "
               "«сложность» — бюджет; «где ошибаются» — то, что обычно ломается в проде. "
               "Демо под темой можно крутить и ломать: параметры влияют на модель в реальном времени."),
        "en": ("“Essence” explains the model in plain words; “the mathematical model” gives working formulas; "
               "“how to build it” is the order of steps; “working code” is a minimal reference; "
               "“complexity” is the budget; “where people get it wrong” is what usually breaks in production. "
               "The demo under each topic can be twisted and broken: parameters affect the model live."),
    },
    "callout_levels": {
        "ru": ("база — один вечер и школьная математика; средний — нужны аккуратность и структуры данных; "
               "продвинутый — тяжёлая математика или серьёзная инженерия. "
               "Начните с базы своего раздела, затем берите средний: так проще увидеть связи."),
        "en": ("basic — one evening and school-level maths; medium — care and data structures required; "
               "advanced — heavy maths or serious engineering. "
               "Start with the basic level of your section, then take the medium ones: links become easier to see."),
    },
    "callout_coverage": {
        "ru": ("Что покрыто и насколько глубоко — в карте покрытия: она показывает силу каждой темы "
               "(обзор, рабочая модель, продакшн) и честно перечисляет то, что осталось за рамками "
               "исследования. Оптимизация и тяжёлые нагрузки вынесены в отдельные разделы."),
        "en": ("What is covered and how deeply is shown in the coverage map: it grades every topic "
               "(overview, working model, production) and honestly lists what stayed outside the scope. "
               "Optimisation and heavy workloads have their own sections."),
    },
    "map_title": {"ru": "Карта разделов", "en": "Map of sections"},
    "map_intro": {
        "ru": "Восемнадцать разделов, {n} тем. Каждая карточка — группа связанных тем.",
        "en": "Eighteen sections, {n} topics. Every card is a group of related topics.",
    },
    "chapter_label": {"ru": "раздел {i} / {n}", "en": "section {i} / {n}"},
    "chapter_topics": {"ru": "{n} тем", "en": "{n} topics"},
    "topic_of": {"ru": "тема {n} / {total}", "en": "topic {n} / {total}"},
    "block_essence": {"ru": "Суть", "en": "Essence"},
    "block_build": {"ru": "Как это построить", "en": "How to build it"},
    "block_code": {"ru": "Рабочий код", "en": "Working code"},
    "block_complexity": {"ru": "Вычислительная сложность", "en": "Computational complexity"},
    "block_pitfalls": {"ru": "Где обычно ошибаются", "en": "Where people usually get it wrong"},
    "block_games": {"ru": "В каких играх это видно", "en": "Where you can see it in games"},
    "formula_label": {"ru": "математическая модель", "en": "the mathematical model"},
    "cx_time": {"ru": "Время", "en": "Time"},
    "cx_memory": {"ru": "Память", "en": "Memory"},
    "cx_practice": {"ru": "Практика", "en": "In practice"},
    "cx_session": {"ru": "Сессия", "en": "Session"},
    "cx_tempo": {"ru": "Темп", "en": "Tempo"},
    "cx_metric": {"ru": "Ключевая метрика", "en": "Key metric"},
    "block_identity": {"ru": "Карточка жанра", "en": "Genre identity card"},
    "block_loop": {"ru": "Цикл", "en": "Loop"},
    "block_summary": {"ru": "Что это за жанр", "en": "What this genre is"},
    "block_breaks": {"ru": "Где жанр ломается", "en": "Where the genre breaks"},
    "block_progress": {"ru": "Прогресс", "en": "Progress"},
    "copy": {"ru": "копировать", "en": "copy"},
    "copied": {"ru": "скопировано", "en": "copied"},
    "copy_failed": {"ru": "не вышло", "en": "failed"},
    "live": {"ru": "live", "en": "live"},
    "pause": {"ru": "пауза", "en": "pause"},
    "resume": {"ru": "продолжить", "en": "resume"},
    "reset": {"ru": "сброс", "en": "reset"},
    "demo_failed": {"ru": "не удалось запустить демо: ", "en": "failed to start the demo: "},
    "done_label": {"ru": "отметить изученным", "en": "mark as studied"},
    "done_done": {"ru": "изучено", "en": "studied"},
    "appendix_label": {"ru": "приложение", "en": "appendix"},
    "appendix_title": {"ru": "{n} практических задач", "en": "{n} practical tasks"},
    "appendix_hint": {"ru": "что делать руками", "en": "what to build by hand"},
    "appendix_intro": {
        "ru": ("Вторая часть исходного списка — прикладные задачи, которые чаще всего дают на позиции "
               "геймплейного или движкового программиста. Для каждой указан подход, ключевые алгоритмы, "
               "связанные темы исследования и практическая заметка."),
        "en": ("The second part of the original list: applied tasks that most often show up in gameplay or "
               "engine programmer interviews. Each card gives the approach, the key algorithms, the related "
               "research topics and a practical note."),
    },
    "glossary_label": {"ru": "справочник", "en": "reference"},
    "glossary_title": {"ru": "Словарь терминов", "en": "Glossary of terms"},
    "glossary_hint": {"ru": "{n} понятий", "en": "{n} terms"},
    "glossary_intro": {
        "ru": ("Термины, которые встречаются в тексте и в вакансиях. Держите под рукой во время "
               "технического интервью."),
        "en": ("Terms that show up both in this text and in job descriptions. Keep them handy during a "
               "technical interview."),
    },
    "method_label": {"ru": "метод", "en": "method"},
    "method_title": {"ru": "Метод и границы", "en": "Method and limits"},
    "method_p1": {
        "ru": ("Формулы приведены в игровых единицах, а не в СИ, если так удобнее читать; константы "
               "подобраны под геймплей, а не под физическую лабораторию. Код — минимальный, без "
               "оптимизаций и обработки ошибок: его задача — показать структуру, а не заменить движок. "
               "Сложности указаны для типичной реализации; реальные цифры зависят от платформы и "
               "компилятора."),
        "en": ("Formulas use game units rather than SI where that reads better; constants are tuned for "
               "gameplay, not for a physics lab. The code is minimal, without optimisations or error "
               "handling: its job is to show the structure, not to replace an engine. Complexity figures "
               "assume a typical implementation; real numbers depend on platform and compiler."),
    },
    "method_p2": {
        "ru": ("Демонстрации используют Canvas 2D и обычную математику: никаких библиотек, CDN и "
               "сборки. Это сделано специально — файл открывается двойным кликом, работает офлайн и "
               "не устаревает вместе с зависимостями."),
        "en": ("The demos use Canvas 2D and plain maths: no libraries, no CDN, no build step. That is "
               "deliberate — the file opens with a double click, works offline and never goes stale with "
               "its dependencies."),
    },
    "footer_title": {"ru": "Game Algorithms", "en": "Game Algorithms"},
    "footer_p1": {
        "ru": ("Синтез исходного списка тем, математических моделей и инженерной практики: "
               "то, что нужно, чтобы не просто знать термин, а собрать механику."),
        "en": ("A synthesis of the original topic list, the mathematical models and engineering practice: "
               "what you need to not just know a term but build the mechanic."),
    },
    "footer_p2": {
        "ru": ("Материалы в репозитории: векторная математика, разбор Ханойской башни и маленькие "
               "игры-демо. Новый документ дополняет их системным разбором алгоритмов."),
        "en": ("Other material in the repository: vector maths, a walkthrough of the Tower of Hanoi and "
               "small game demos. This document complements them with a systematic breakdown of algorithms."),
    },
    "footer_fine": {
        "ru": "Один HTML-файл · встроенные CSS и JS · {n} тем · {demos} демо · {tasks} задач · {formulas} формул",
        "en": "One HTML file · inline CSS and JS · {n} topics · {demos} demos · {tasks} tasks · {formulas} formulas",
    },
    "footer_link_how": {"ru": "Как читать", "en": "How to read"},
    "footer_link_map": {"ru": "Карта разделов", "en": "Map of sections"},
    "footer_link_tasks": {"ru": "Практические задачи", "en": "Practical tasks"},
    "footer_link_gloss": {"ru": "Словарь терминов", "en": "Glossary of terms"},
    "footer_link_readme": {"ru": "README репозитория", "en": "Repository README"},
    "footer_link_vector": {"ru": "Векторная математика", "en": "Vector maths"},
    "footer_link_hanoi": {"ru": "Ханойская башня", "en": "Tower of Hanoi"},
    "footer_link_asteroids": {"ru": "Asteroids demo", "en": "Asteroids demo"},
    "to_top_aria": {"ru": "Наверх", "en": "Back to top"},
    "menu_aria": {"ru": "Открыть навигацию", "en": "Open navigation"},
    "print_aria": {"ru": "Печать или сохранение в PDF", "en": "Print or save as PDF"},
    "side_aria": {"ru": "Содержание", "en": "Contents"},
    "hero_side_aria": {"ru": "Ключевые цифры", "en": "Key numbers"},
    "main_aria": {"ru": "Содержание документа", "en": "Document content"},
    "lang_note": {
        "ru": "Полная версия на английском",
        "en": "Full version in Russian",
    },
    "mode": {"ru": "режим", "en": "mode"},
    "loss": {"ru": "потери", "en": "loss"},
    "rtt": {"ru": "RTT", "en": "RTT"},
    "delivered": {"ru": "доставлено", "en": "delivered"},
    "stalls": {"ru": "блокировки", "en": "stalls"},
    "stream": {"ru": "поток", "en": "stream"},
    "transport_note": {
        "ru": "UDP теряет пакет и едет дальше; TCP встаёт целиком; QUIC тормозит только свой stream.",
        "en": "UDP drops one packet and moves on; TCP stops entirely; QUIC stalls only that stream.",
    },
    "inflight": {"ru": "в полёте", "en": "in flight"},
    "retrans": {"ru": "ретрансмиссии", "en": "retransmits"},
    "rto": {"ru": "RTO", "en": "RTO"},
    "reliability_note": {
        "ru": "Окно ограничивает полёт, ACK двигает базу, потеря ждёт RTO и уходит повторно.",
        "en": "The window caps in-flight data, ACKs move the base, a loss waits for RTO then retries.",
    },
    "authority": {"ru": "авторитет", "en": "authority"},
    "links": {"ru": "связей", "en": "links"},
    "host_adv": {"ru": "преимущество хоста", "en": "host advantage"},
    "dedicated": {"ru": "выделенный", "en": "dedicated"},
    "listen": {"ru": "listen-сервер", "en": "listen server"},
    "relay": {"ru": "релей", "en": "relay"},
    "send": {"ru": "отправить", "en": "send"},
    "peers": {"ru": "пиры", "en": "peers"},
    "host": {"ru": "хост", "en": "host"},
    "server": {"ru": "сервер", "en": "server"},
    "topology_note": {
        "ru": "P2P экономит серверы, но авторитет размыт; релей прячет адреса и добавляет хоп.",
        "en": "P2P saves servers but blurs authority; a relay hides addresses and adds a hop.",
    },
    "path": {"ru": "путь", "en": "path"},
    "direct": {"ru": "напрямую", "en": "direct"},
    "relay_cost": {"ru": "цена релея", "en": "relay cost"},
    "symmetric_nat": {"ru": "симметричный NAT", "en": "symmetric NAT"},
    "punch": {"ru": "пробить", "en": "punch"},
    "nat_note": {
        "ru": "STUN даёт адрес, сигнализация обменивается им, punch открывает порт; symmetric NAT требует TURN.",
        "en": "STUN reveals the address, signalling swaps it, punch opens the port; symmetric NAT needs TURN.",
    },
    "rollback": {"ru": "откат", "en": "rollback"},
    "resims": {"ru": "ресимуляции", "en": "resims"},
    "depth": {"ru": "глубина", "en": "depth"},
    "input_delay": {"ru": "задержка ввода", "en": "input delay"},
    "rollback_marker": {"ru": "цель отката", "en": "rewind target"},
    "rollback_note": {
        "ru": "Пришёл поздний ввод — откатываем состояние к нему и пересимулируем кадры.",
        "en": "A late input arrives: rewind state to it and resimulate the frames.",
    },
    "delay": {"ru": "задержка", "en": "delay"},
    "jitter": {"ru": "джиттер", "en": "jitter"},
    "error": {"ru": "ошибка", "en": "error"},
    "extrapolate": {"ru": "экстраполяция", "en": "extrapolate"},
    "interp_note": {
        "ru": "Рендерим прошлое между снапшотами; джиттер лечится буфером, экстраполяция — риском.",
        "en": "We render the past between snapshots; a buffer absorbs jitter, extrapolation adds risk.",
    },
    "rewind_ms": {"ru": "откат, мс", "en": "rewind, ms"},
    "hits": {"ru": "попадания", "en": "hits"},
    "shots": {"ru": "выстрелы", "en": "shots"},
    "lag_comp": {"ru": "лаг-компенсация", "en": "lag compensation"},
    "fire": {"ru": "выстрел", "en": "fire"},
    "range": {"ru": "окно, мс", "en": "window, ms"},
    "lagcomp_note": {
        "ru": "Сервер отматывает цели на RTT стрелка; слишком большое окно открывает прострел сквозь стены.",
        "en": "The server rewinds targets by the shooter RTT; too wide a window lets shots through walls.",
    },
    "visible": {"ru": "видно", "en": "visible"},
    "total": {"ru": "всего", "en": "total"},
    "bandwidth": {"ru": "трафик", "en": "bandwidth"},
    "aoi_radius": {"ru": "радиус AOI", "en": "AOI radius"},
    "budget": {"ru": "бюджет", "en": "budget"},
    "aoi_note": {
        "ru": "Релевантность по расстоянию: всё за кругом не реплицируется вовсе.",
        "en": "Distance relevance: anything outside the circle is never replicated.",
    },
    "sent": {"ru": "отправлено", "en": "sent"},
    "dropped": {"ru": "отброшено", "en": "dropped"},
    "bytes": {"ru": "байты", "en": "bytes"},
    "budget_note": {
        "ru": "Сначала уходят важные и изменившиеся сущности; остальное ждёт следующего тика.",
        "en": "Important and changed entities go first; the rest waits for the next tick.",
    },
    "shards": {"ru": "шарды", "en": "shards"},
    "players": {"ru": "игроки", "en": "players"},
    "handoffs": {"ru": "передач", "en": "handoffs"},
    "shard_note": {
        "ru": "Зоны режут мир, игрок на границе переезжает между процессами без экрана загрузки.",
        "en": "Zones cut the world; a player on a border moves between processes without a loading screen.",
    },
    "queue": {"ru": "в очереди", "en": "queued"},
    "wait": {"ru": "ожидание", "en": "wait"},
    "matches": {"ru": "матчи", "en": "matches"},
    "window": {"ru": "окно MMR", "en": "MMR window"},
    "session_note": {
        "ru": "Матчмейкер расширяет окно MMR со временем ожидания, цена — качество матча.",
        "en": "The matchmaker widens the MMR window with wait time; the price is match quality.",
    },
    "allowed": {"ru": "пропущено", "en": "allowed"},
    "blocked_count": {"ru": "заблокировано", "en": "blocked"},
    "drop_rate": {"ru": "доля блока", "en": "drop rate"},
    "attack": {"ru": "атака", "en": "attack"},
    "limit": {"ru": "лимит", "en": "limit"},
    "security_note": {
        "ru": "Token bucket режет всплеск до лимита; за прокси и CDN считается уже другой лимит.",
        "en": "A token bucket clips the burst to the limit; behind a proxy and CDN the limit is different.",
    },

}
