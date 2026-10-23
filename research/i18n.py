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
        "ru": ("Сетевая синхронизация",
               "Предсказание, античит, детерминированный lockstep и сжатие снапшотов."),
        "en": ("Network synchronisation",
               "Prediction, anti-cheat, deterministic lockstep and snapshot compression."),
    },
    "procgen": {
        "color": "#6ee7b7",
        "ru": ("Процедурная генерация",
               "Планетные системы, сбалансированные карты, экосистемы и музыка."),
        "en": ("Procedural generation",
               "Planetary systems, balanced maps, ecosystems and music."),
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
    "heavy": {
        "color": "#4ade80",
        "ru": ("Тяжёлые нагрузки и GPU",
               "Compute shaders, миллионы частиц, GPU-driven pipeline, readback и масштабирование качества."),
        "en": ("Heavy workloads and GPU",
               "Compute shaders, millions of particles, GPU-driven pipeline, readback and quality scaling."),
    },
}

# порядок разделов в документе
CHAPTER_ORDER = [
    "mechanics", "ai", "gfx", "network", "procgen", "physics", "optimize",
    "math", "stats", "geometry", "shaders", "economy", "audio", "ml", "heavy",
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
        "ru": ("{n} темы — от баллистики и boids до глобального освещения, lockstep и апскейлинга. "
               "Для каждой: математическая модель, пошаговая реализация, рабочий код, честная сложность, "
               "типичные ошибки и живая интерактивная модель в браузере."),
        "en": ("{n} topics — from ballistics and boids to global illumination, lockstep and upscaling. "
               "Each one: the mathematical model, a step-by-step implementation, working code, honest "
               "complexity, the usual mistakes and a live interactive model in the browser."),
    },
    "hero_start": {"ru": "Начать изучение", "en": "Start reading"},
    "hero_tasks": {"ru": "{n} практических задач", "en": "{n} practical tasks"},
    "stat_topics": {"ru": "тем · {n} разделов", "en": "topics · {n} sections"},
    "stat_demos": {"ru": "интерактивных демо", "en": "interactive demos"},
    "stat_tasks": {"ru": "практических задач", "en": "practical tasks"},
    "stat_deps": {"ru": "внешних зависимостей", "en": "external dependencies"},
    "meta_desc": {
        "ru": "Алгоритмы игр: {n} тем с математикой, кодом, сложностью и интерактивными демо.",
        "en": "Game algorithms: {n} topics with maths, code, complexity and interactive demos.",
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
        "ru": "Пятнадцать разделов, {n} тем. Каждая карточка — группа связанных тем.",
        "en": "Fifteen sections, {n} topics. Every card is a group of related topics.",
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
}
