# Game-algorithms

<!-- Файл генерируется: python3 tools/gen_readme.py -->

> ### 📘 Полное исследование: [game-algorithms-research.html](game-algorithms-research.html)
> Один автономный HTML-файл (открывается двойным кликом, работает офлайн):
> **164 тем** с математической моделью, пошаговой реализацией, рабочим кодом,
> сложностью, типичными ошибками и референсами; **62 интерактивных демо**
> (шум и эрозия, пещеры и подземелья, BSP, лабиринты, WFC, биомы, реки, города,
> предметы, имена, квесты, музыка, фасады, а также баллистика, boids и lockstep);
> **45 практических задач** и словарь терминов.
>
> **Часть II — процедурная генерация** вынесена в отдельный атлас: 28 тем,
> 28 живых моделей, четыре слоя — от шума и сэмплинга до контента и драматургии.
> **Часть III — сетевое взаимодействие**: 22 темы, 13 живых моделей,
> четыре слоя — транспорт, синхронизация, реальное время и масштаб.
> **Часть IV — баланс и прогрессия**: 24 темы, 7 живых моделей — урон и
> защита, кривые опыта, награды, инфляция и Монте-Карло-симулятор баланса.
> **Часть V — атлас жанров**: 36 жанров с ядром цикла, темпом и провалами.
> **Часть VI — стиль и студия промптов**: 47 атомов стиля, 8 пресетов и
> конструктор, который собирает из досье готовое задание для команды или модели.
> Поиск, фильтры по сложности, прогресс чтения, тёмная/светлая темы и переключатель
> языка — внутри.
>
> Исходники контента — `research/`, сборка — `python3 tools/build.py`, стили и демо — `assets/`.

> ### 📗 Full research (English): [index.en.html](index.en.html)
> The same research in English: **164 topics** with the mathematical model, a
> step-by-step build, working code, complexity, pitfalls and references;
> **62 interactive demos**; **45 practical tasks** and a glossary.
> **Part II — procedural generation** is a separate atlas: 28 topics, 28 live
> models, four layers from noise and sampling up to content and drama.
> **Part III — networked multiplayer**: 22 topics, 13 live models,
> four layers: transport, synchronisation, real time and scale.
> **Part IV — balance and progression**: 24 topics, 7 live models — damage
> and defence, XP curves, rewards, inflation and a Monte-Carlo balance simulator.
> **Part V — the genre atlas**: 36 genres with their core loop, tempo and pitfalls.
> **Part VI — style and the prompt studio**: 47 style atoms, 8 presets and a
> composer that turns the dossier into a brief for a team or a model.
> A language switch sits in the header and remembers your choice.

**Онлайн / Live:** <https://sergutsu.github.io/Game-algorithms/> — GitHub Pages, корень репозитория, ветка `main`
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
| `assets/` | Стили, клиентская логика, 62 демо, таблицы подписей |

---

## 📚 Темы — русская версия

Сначала **Часть I — системы**, затем отдельная **Часть II — атлас процедурной
генерации** (нумерация PG-01…PG-28) и **Часть III — сетевой плейбук**
(нумерация NET-01…NET-22).

### Геймплейные механики

1. **Баллистика снарядов с сопротивлением воздуха**  
   *(дифференциальные уравнения, Рунге–Кутта, CCD)* · 🎮 demo
2. **Система крит-ударов с зависимостью от статистики**  
   *(распределение Пуассона, логит-модель, PRD)*
3. **Динамическая генерация сбалансированных цен**  
   *(дифференциальные уравнения, теория игр, эластичность)*
4. **Плавное перемещение объектов по сплайнам**  
   *(кривые Безье, Catmull–Rom, арк-длина)*
5. **Механика квантовых состояний в геймплее**  
   *(линейная алгебра, матрицы плотности, суперпозиция)*

### Искусственный интеллект

6. **ИИ для стратегических решений в 4X-играх**  
   *(utility AI, MCTS/UCT, деревья решений)*
7. **Система эмоциональных реакций NPC**  
   *(PAD-модель, OCC, кластеризация)*
8. **Адаптивная сложность противников**  
   *(Q-learning, байесовские сети, bandit)*
9. **Генерация правдоподобных диалогов**  
   *(цепи Маркова, трансформеры, грамматики)*
10. **Оптимизация группового поведения юнитов**  
   *(теория роя, boids, spatial hash)* · 🎮 demo

### Физические симуляции

24. **Реализация ткани и мягких тел**  
   *(масс-пружины, интегрирование Верле, XPBD)* · 🎮 demo
25. **Аэродинамика летательных аппаратов**  
   *(Бернулли, CFD, аэродинамические коэффициенты)*
26. **Магнитные и гравитационные поля**  
   *(векторные поля, дивергенция/ротор, потенциал)*
27. **Тепловая передача и термодинамика**  
   *(уравнение Фурье, диффузия, энтропия)*

### Системы оптимизации

28. **Распределение вычислений в рендеринге**  
   *(линейное программирование, симплекс, job system)*
29. **Пространственное разбиение для коллизий**  
   *(BVH, k-d дерево, broadphase)*
30. **Сжатие анимационных данных**  
   *(квантование, сплайны, кривые)*
31. **Профилирование и бюджет кадра**  
   *(профилировщик, frame budget, p95, троттлинг)* · 🎮 demo
32. **Батчинг, инстансинг и борьба с draw call**  
   *(draw call, instancing, SRP Batcher, indirect draw)* · 🎮 demo
33. **Отсечение: frustum, occlusion и LOD**  
   *(frustum culling, occlusion, LOD, HLOD, HZB)* · 🎮 demo
34. **Data-Oriented Design, SIMD и дружба кэша**  
   *(SoA, SIMD, кэш, выравнивание, AoS)*
35. **Многопоточность и job system**  
   *(job system, work stealing, задачи, main thread)*
36. **Память: пулы, GC и стриминг ассетов**  
   *(пул объектов, GC, fragmentation, streaming, virtual texturing)*

### Математические механики

37. **Порталы и неевклидова геометрия**  
   *(проективная геометрия, кватернионы, recursion)* · 🎮 demo
38. **Геймплей на торе и ленте Мёбиуса**  
   *(топология, склейки, эйлерова характеристика)*
39. **Система квантовой запутанности**  
   *(тензорная алгебра, гильбертово пространство, Белл)*
40. **Динамические системы и хаос**  
   *(теория хаоса, аттракторы, ляпуновские показатели)* · 🎮 demo

### Статистика и баланс

41. **Анализ игрового баланса оружия**  
   *(регрессия, ANOVA, TTK)*
42. **Система matchmaking для ранговых игр**  
   *(Elo, Glicko-2, TrueSkill, байес)* · 🎮 demo
43. **Прогнозирование игровых трендов**  
   *(ARIMA, сезонность, аномалии)* · 🎮 demo
44. **Вероятностные системы лута**  
   *(распределение Парето, ЦПТ, pity)* · 🎮 demo

### Геометрия и коллизии

45. **Определение видимости в 3D-пространстве**  
   *(BSP, PVS, occlusion culling)*
46. **Расчёт траекторий рикошетов**  
   *(отражение, закон Снелла, случайность)*

### Игровые экономики

51. **Динамическая балансировка рынка**  
   *(аукцион Викри, равновесие, рынок)* · 🎮 demo
52. **Алгоритмы распределения ресурсов**  
   *(оптимальное управление, LP, приоритеты)*
53. **Моделирование инфляционных процессов**  
   *(монетарная экономика, стоки, уравнение обмена)*

### Аудио-системы

54. **Пространственный 3D-звук**  
   *(HRTF, ITD/ILD, сферические гармоники)*
55. **Физическое моделирование инструментов**  
   *(волновод, КИХ-фильтры, резонанс)*

### Нейросетевые приложения

56. **Генерация контента через GAN**  
   *(GAN, Вассерштейн, backprop)*
57. **Апскейлинг графики в реальном времени**  
   *(свёрточные сети, трансформеры, TAA)*

### Тяжёлые нагрузки и GPU

58. **Compute shaders: перенос симуляций на GPU**  
   *(compute shader, workgroup, dispatch, barrier, GPGPU)* · 🎮 demo
59. **Миллионы частиц: GPU-симуляция и сортировка**  
   *(particles, bitonic sort, indirect draw, GPU particles)* · 🎮 demo
60. **GPU-driven pipeline: отсечение и сборка команд на GPU**  
   *(indirect draw, GPU culling, Hi-Z, bindless, compute pipeline)*
61. **Асинхронный readback: как не встать в stall**  
   *(fence, stall, readback, triple buffering, PBO)*
62. **Процедурная геометрия на GPU: marching cubes и SDF**  
   *(marching cubes, SDF, isosurface, voxelization, mesh generation)*
63. **Физика и broadphase на GPU**  
   *(broadphase, XPBD, GPU physics, сортировка контактов, solver)*
64. **Тяжёлые шейдеры: ray marching, волюметрика, SSR**  
   *(ray marching, volumetrics, SSR, temporal reprojection, denoise)*
65. **Профилирование GPU: таймстемпы, счётчики и occlusion queries**  
   *(timestamp query, GPU counter, RenderDoc, occlusion query, pipeline statistics)*
66. **Масштабирование качества и деградация на слабом железе**  
   *(scalability, dynamic resolution, LOD bias, fallback, tier)*

## Часть II — процедурная генерация / Part II — procedural generation

> Отдельная часть исследования: полный атлас алгоритмов генерации контента.

### Шум, поля и выборки

PG-01. **Градиентный шум: value, Perlin и simplex**  
   *(value noise, Perlin, simplex, fBm)* · 🎮 demo
PG-02. **Клеточный шум Ворли: F1, F2 и границы**  
   *(Вороной, клеточный шум, F2−F1, фича-точки)* · 🎮 demo
PG-03. **Пуассон-диск и blue noise: равномерный разброс без комков**  
   *(Бридсон, blue noise, spatial hash, скаттеринг)* · 🎮 demo
PG-04. **Сид, хэш и воспроизводимость генерации**  
   *(PRNG, PCG, хэш координат, детерминизм)* · 🎮 demo
PG-05. **Diamond-square и midpoint displacement**  
   *(фрактал, карта высот, шероховатость, 1/f)* · 🎮 demo
PG-06. **Процедурные текстуры материалов**  
   *(шум, преобразования Фурье, tiling)* · 🎮 demo

### Планировка: пещеры, подземелья, карты

PG-07. **Клеточные автоматы: пещеры за пять шагов**  
   *(клеточные автоматы, 4-5 rule, связность, пещеры)* · 🎮 demo
PG-08. **BSP-подземелья: разбиение, комнаты, коридоры**  
   *(BSP, дерево, комнаты, связность)* · 🎮 demo
PG-09. **Пьяная прогулка: пещера из случайных шагов**  
   *(random walk, carving, плотность, прототип)* · 🎮 demo
PG-10. **Лабиринты: backtracker, Прим, Крускал, Уилсон**  
   *(остовное дерево, DFS, Прим, Крускал)* · 🎮 demo
PG-11. **Wave Function Collapse: генерация по ограничениям**  
   *(WFC, AC-3, энтропия, тайлы, откат)* · 🎮 demo
PG-12. **Города и дорожные сети: Вороной, MST и кварталы**  
   *(MST, Вороной, A*, градостроительство)* · 🎮 demo
PG-13. **Генерация сбалансированных карт для стратегий**  
   *(теория графов, симметрия, фэйрнесс)* · 🎮 demo

### Миры и рельеф

PG-14. **Процедурная генерация реалистичных ландшафтов**  
   *(шум Перлина, фракталы, эрозия)* · 🎮 demo
PG-15. **Гидравлическая эрозия: дождь, наносы и дельты**  
   *(эрозия, осадки, карта высот, нормали)* · 🎮 demo
PG-16. **Биомы: диаграмма Уиттекера, климат и переходы**  
   *(Уиттекер, температура, влажность, климат)* · 🎮 demo
PG-17. **Реки: направление стока, водосборы и русла**  
   *(D8, аккумуляция, водосбор, озёра)* · 🎮 demo
PG-18. **Генерация объёмных облаков**  
   *(ray marching, функции плотности, Beer–Lambert)* · 🎮 demo
PG-19. **Создание уникальных планетарных систем**  
   *(законы Кеплера, n-body, зоны обитаемости)* · 🎮 demo
PG-20. **Генерация воксельных миров**  
   *(marching cubes, SDF, октодерево)* · 🎮 demo

### Контент и системы

PG-21. **L-системы: растения, города и фрактальные узоры**  
   *(грамматика, черепашья графика, фрактал, растения)* · 🎮 demo
PG-22. **Shape-грамматики: генеративные фасады и интерьеры**  
   *(split grammar, фасады, правила, LOD)* · 🎮 demo
PG-23. **Генератор предметов: редкость, аффиксы и бюджет**  
   *(лут, аффиксы, редкость, бюджет)* · 🎮 demo
PG-24. **Генерация имён: слоговая грамматика и цепи Маркова**  
   *(Марков, слоги, фонотактика, нейминг)* · 🎮 demo
PG-25. **Квесты и миссионные графы: ключи, двери и ритм**  
   *(mission graph, lock-and-key, грамматика, солвабельность)* · 🎮 demo
PG-26. **Процедурные музыкальные композиции**  
   *(L-системы, теория музыки, марковские цепи)* · 🎮 demo
PG-27. **Построение правдоподобных экосистем**  
   *(Лотка–Вольтерра, динамические системы, трофические сети)* · 🎮 demo
PG-28. **AI-директор: кривая напряжения и волны врагов**  
   *(AI director, пейсинг, динамическая сложность, волны)* · 🎮 demo

## Часть III — сетевое взаимодействие / Part III — networked multiplayer

> Отдельная часть исследования: полный сетевой плейбук, от UDP до операций крупной MMO.

### Транспорт и топология

NET-01. **Транспорт: UDP, TCP, QUIC и WebTransport**  
   *(UDP, TCP, QUIC, MTU)* · 🎮 demo
NET-02. **Надёжность поверх UDP: sequence, ACK, RTO и congestion control**  
   *(ACK, RTO, congestion, retransmit)* · 🎮 demo
NET-03. **Топологии: dedicated, listen, P2P, relay и mesh**  
   *(dedicated, listen, P2P, relay)* · 🎮 demo
NET-04. **NAT, STUN, TURN, ICE и hole punching**  
   *(NAT, STUN, TURN, ICE)* · 🎮 demo
NET-05. **Браузер и мобильные сети: WebSocket, WebRTC и радио**  
   *(WebSocket, WebRTC, mobile, battery)*

### Модели синхронизации

NET-06. **Детерминированная симуляция RTS**  
   *(fixed-point, детерминизм, lockstep)* · 🎮 demo
NET-07. **Предсказание движения в FPS**  
   *(фильтр Калмана, экстраполяция, rollback)*
NET-08. **Оптимизация передачи состояния мира**  
   *(энтропия Шеннона, квантование, дельта)*
NET-09. **Rollback netcode: пересимуляция для файтингов**  
   *(rollback, GGPO, prediction, determinism)* · 🎮 demo
NET-10. **Детерминизм и сериализация: fixed-point, квантование, bitpacking**  
   *(fixed-point, quantisation, bitpacking, checksum)*

### Реальное время

NET-11. **Интерполяция, экстраполяция и jitter buffer**  
   *(interpolation, jitter, buffer, snapshots)* · 🎮 demo
NET-12. **Lag compensation: rewind и валидация попаданий**  
   *(rewind, hitscan, latency, anti-cheat)* · 🎮 demo
NET-13. **Interest management: AOI, сетки и relevance**  
   *(AOI, spatial hash, relevance, MMO)* · 🎮 demo
NET-14. **Синхронизация времени и тиков: часы, offset и timeline**  
   *(clock, tick, NTP, timeline)*
NET-15. **Бюджет полосы: приоритизация, дельты и квантование**  
   *(bandwidth, priority, delta, quantisation)* · 🎮 demo

### Масштаб и эксплуатация

NET-16. **Шардинг, зоны и бесшовный мир**  
   *(sharding, zones, handoff, MMO)* · 🎮 demo
NET-17. **Сессии, лобби, матчмейкинг и reconnect**  
   *(session, matchmaking, lobby, reconnect)* · 🎮 demo
NET-18. **Персистентность MMO: БД, кэш, транзакции и event sourcing**  
   *(database, redis, transactions, event sourcing)*
NET-19. **Система защиты от читеров**  
   *(z-score, аномалии, доверие)*
NET-20. **Безопасность: DDoS, rate limit, auth и шифрование**  
   *(DDoS, rate limit, auth, encryption)* · 🎮 demo
NET-21. **Эксплуатация: метрики, SLO, трейсы и live-ops**  
   *(observability, SLO, metrics, live-ops)*
NET-22. **Тестирование сети: netem, хаос и нагрузочные боты**  
   *(netem, chaos, load test, replay)*

## Часть IV — баланс и прогрессия / Part IV — balance and progression

> Числа, из которых складывается ощущение игры: урон, защита, кривая опыта, награды и экономика.

### Урон

BAL-01. **Броня и кривая смягчения урона**  
   *(armour, mitigation, Time-to-kill, curve)* · 🎮 demo
BAL-02. **Формула урона: слои сложения и умножения**  
   *(damage formula, modifiers, buckets, stacking)*
BAL-03. **Эффективное здоровье, TTK и выстрелы до убийства**  
   *(EHP, TTK, STK, breakpoints)* · 🎮 demo
BAL-04. **Разброс урона, шанс попадания и дисперсия**  
   *(variance, RNG, hit chance, expected value)*
BAL-05. **Периодический урон: стаки, обновление и тики**  
   *(DoT, stacking, tick rate, uptime)*

### Защита

BAL-06. **Щиты, поглощение и регенерация**  
   *(shield, absorb, regen, effective HP)*
BAL-07. **Контроль и его убывающая отдача**  
   *(CC, diminishing returns, immunity, PvP)*
BAL-08. **Бюджет живучести: стаки смягчения и капы**  
   *(stacking, diminishing returns, caps, budget)*

### Прогрессия

BAL-09. **Кривая опыта и стоимость уровня**  
   *(XP, curve, level cap, exponent)* · 🎮 demo
BAL-10. **Рост характеристик: линейный, геометрический и мягкие капы**  
   *(stat growth, power curve, scaling, caps)*
BAL-11. **Мягкие капы и убывающая отдача**  
   *(soft cap, diminishing returns, curve, stats)*
BAL-12. **Бюджет очков: деревья навыков и цена выбора**  
   *(skill tree, budget, opportunity cost, build)*
BAL-13. **Темп прогрессии: гейты, время до уровня и кривая силы**  
   *(pacing, gates, retention, power curve)*

### Награды и экономика

BAL-14. **Награда за действие: опыт, добыча и масштабирование**  
   *(reward, scaling, economy of time, quests)*
BAL-15. **Полосы редкости и таблицы дропа**  
   *(loot table, rarity, weights, item level)* · 🎮 demo
BAL-16. **Гача: вероятности, soft pity и ожидаемые попытки**  
   *(gacha, pity, expected value, monetisation)* · 🎮 demo
BAL-17. **Валюты: краны, стоки и скорость накопления**  
   *(currency, faucet, sink, economy)*
BAL-18. **Инфляция и sinks в живой экономике**  
   *(inflation, sink, money supply, live ops)* · 🎮 demo
BAL-19. **Гринд, энергия и сессионные циклы**  
   *(grind, session, energy, retention)*

### Мета-баланс

BAL-20. **Степенной рост силы и горизонтальная прогрессия**  
   *(power creep, progression, content, live ops)*
BAL-21. **Кривая сложности, DDA и доступность**  
   *(difficulty, DDA, accessibility, onboarding)*
BAL-22. **Тюнинг босса: фазы, DPS-check и энрейдж**  
   *(boss, phases, DPS check, enrage)*
BAL-23. **PvP-баланс: нормализация, рейтинг и снаряжение**  
   *(PvP, normalisation, rating, gear)*
BAL-24. **Симуляция баланса, Монте-Карло и A/B-тесты**  
   *(Monte Carlo, simulation, A/B test, telemetry)* · 🎮 demo

## Часть V — атлас жанров / Part V — the genre atlas

> 36 жанров: ядро цикла, темп, типичные провалы и игры, в которых жанр виден.

### Экшен

GEN-01. **Шутер от первого лица**  
   *(aim, TTK, map control, gun feel)* — Сессия: спавн → ротация → дуэль → смерть/победа → спавн   ·   TTK 0.15–1.2 с
GEN-02. **Battle royale**  
   *(shrinking, loot, risk, one life)* — Матч: 100 → 1 за T ≈ 15–25 мин,   P(выжить) ≈ (1/2)^(стычек)
GEN-03. **Файтинг**  
   *(frame data, neutral, mixup, determinism)* — input → frame N: startup, active, recovery;   advantage = (hit/block stun) − recovery
GEN-04. **Платформер**  
   *(jump arc, coyote time, level design, feel)* — h = v₀²/(2g),   t_air = 2v₀/g,   дальность = v₀ₓ · t_air
GEN-05. **Скролл-шутер и bullet hell**  
   *(pattern, hitbox, score, reading)* — узоры: ρ(θ) = a + b·sin(kθ + φt),   скорость пули v = const
GEN-06. **Hack & slash и character action**  
   *(combo, enemy design, rank, camera)* — DPS_стиля = Σ урон · множитель_комбо / время,   телеграф 0.3–0.6 с

### Стратегии

GEN-07. **Стратегия в реальном времени**  
   *(economy, map control, counters, APM)* — доход = Σ рабочих · скорость добычи · (1 − потери),   армия(t) = ∫(доход − расход)dt
GEN-08. **Пошаговая стратегия и 4X**  
   *(explore, expand, exploit, exterminate)* — рост = (наука · производство · территория)^(1/3) · бонус_эры,   цена расширения ∝ n^1.5
GEN-09. **MOBA**  
   *(lanes, snowball, team, roles)* — золото(t) = фарм + баунти − смерти,   окно_силы = тир предметов × уровень
GEN-10. **Tower defense**  
   *(pathing, economy, waves, scaling)* — DPS_позиции = Σ башен / время в зоне,   доход(w) = base · (1 + k)^w,   HP(w) = hp₀ · (1 + k')^w
GEN-11. **Автобаттлер**  
   *(draft, economy, synergy, RNG)* — доход = base_per_round + floor(gold/10) · 1 (макс 5),   сила = Σ юнитов · синергии
GEN-12. **Тактические игры и варгеймы**  
   *(initiative, cover, fog of war, permadeath)* — hit = clamp(0.05, base + acc − cover − range, 0.95),   действия = 1–2 на юнита

### Ролевые игры

GEN-13. **JRPG**  
   *(party, turn order, story, growth)* — урон = (ATK² / (ATK + DEF)) · элемент · (1 + бафф) · rand(0.9, 1.1)
GEN-14. **CRPG**  
   *(dialogue, builds, choice, systems)* — успех ⇔ d20 + мод ≥ DC,   P = (21 − (DC − мод)) / 20
GEN-15. **Action RPG и looter shooter**  
   *(loot, builds, density, endgame)* — DPS_билда = урон · скорость · крит · (1 + синергии),   апгрейд = max(0, ilvl_new − ilvl_old)
GEN-16. **MMO**  
   *(social, persistence, roles, endgame)* — прогресс = контент(сезон) / (время · обязательные_активности),   группа = танк + хилер + 3 dps
GEN-17. **Souls-like**  
   *(stamina, telegraph, risk, world)* — stamina(t) = max(0, stamina₀ − Σcost + regen·t),   урон_блока = урон · (1 − block) − stamina_cost
GEN-18. **Roguelike и roguelite**  
   *(procedural, permadeath, synergy, runs)* — P(победного прогона) ≈ f(синергии, скилл),   длина прогона 20–60 мин

### Симуляции

GEN-19. **Симулятор менеджмента и тайкун**  
   *(economy, optimisation, feedback, spreadsheets)* — прибыль = Σ (цена − себестоимость) · объём − постоянные,   рост = k · (1 − загрузка)
GEN-20. **Градостроительный симулятор**  
   *(zoning, traffic, services, growth)* — население' = приток − отток,   приток ∝ счастье · жильё · работа · доступность
GEN-21. **Фабрика и автоматизация**  
   *(throughput, ratios, blueprints, scaling)* — throughput = min(производство, потребление, логистика),   ratio = t_produce / t_consume
GEN-22. **Симулятор жизни и социальные симуляции**  
   *(needs, relationships, routine, emergence)* — энергия(t) = Σ потребности,   действие = f(время, стоимость, настроение)
GEN-23. **Сурвайвал**  
   *(resources, threat, crafting, bases)* — выживание ⇔ запас(t) > потребление(t),   угроза(t) ≈ k · прогресс(t)
GEN-24. **Песочница и творческие игры**  
   *(creation, tools, sharing, no goals)* — выразительность = мощность_инструментов / трение_интерфейса

### Приключения

GEN-25. **Метроидвания**  
   *(gating, backtracking, map, abilities)* — мир = граф комнат,   ребро открыто ⇔ способность ∈ инвентарь
GEN-26. **Головоломки**  
   *(rules, insight, levels, teaching)* — сложность ≈ число доступных ходов + глубина следствий
GEN-27. **Immersive sim**  
   *(systemic, emergent, stealth, choice)* — решения = комбинации(правил, инструментов, среды)
GEN-28. **Стелс**  
   *(visibility, sound, patrol, failure)* — обнаружение ⇔ видимость · свет · расстояние / укрытие + шум > порог
GEN-29. **Хоррор**  
   *(tension, powerlessness, sound, pacing)* — напряжение(t) = нехватка_контроля · неопределённость / привыкание
GEN-30. **Нарративные приключения**  
   *(story, choice, dialogue, pacing)* — агентность ≈ (влияние выбора) · (видимость последствий)

### Спорт и социальные игры

GEN-31. **Гоночные игры**  
   *(physics, tracks, sense of speed, progression)* — v_max ≈ P / (ρ·C_d·A)^(1/3),   сцепление = μ·N,   тормозной путь ≈ v²/(2μg)
GEN-32. **Спортивные симуляторы**  
   *(rules, season, ratings, meta)* — rating ≈ f(статистика, позиция, контекст),   итог матча = правила + состав + исполнение
GEN-33. **Ритм-игры**  
   *(timing, charting, calibration, flow)* — оценка = f(|t_нажатия − t_ноты|),   Perfect ≤ 30 мс, Great ≤ 80 мс
GEN-34. **Коллекционные карточные игры**  
   *(deck building, mana curve, meta, RNG)* — темп = Σ (мана / ход),   вероятность добрать ответ = 1 − C(n−k, m)/C(n, m)
GEN-35. **Idle и инкрементальные игры**  
   *(exponential, prestige, numbers, automation)* — доход = base · Π множителей,   цена(n) = base · 1.15ⁿ,   время до покупки ≈ цена / доход
GEN-36. **Пати-игры и социальная дедукция**  
   *(social, bluffing, short rounds, spectators)* — раунд 1–5 мин,   объяснение правил ≤ 60 с,   доля выбывших в любой момент ≤ 25 %

## Часть VI — стиль и студия промптов / Part VI — style and the prompt studio

> 47 атомов стиля в 6 слоях, 8 готовых пресетов и конструктор, который собирает из досье задание для команды или языковой модели (4 формата выдачи).  
> 47 style atoms in 6 layers, 8 ready-made presets and a composer that turns the dossier into a brief for a team or a language model (4 output formats).

`#part-styles` — живой блок в HTML: атлас, пресеты и конструктор.

---

## 🛠 Практические задачи — русская версия

### Геймплей и механики

1. **ИИ для NPC в RTS**  
   *(Поведение юнитов, принятие решений)*
2. **Физика движения персонажа в платформере**  
   *(Прыжки, инерция, столкновения)*
3. **Система диалогов для RPG**  
   *(Ветвление, условия, последствия)*
4. **Система крафтинга ресурсов**  
   *(Рецепты, ингредиенты, вероятности)*
5. **Дерево навыков с прокачкой**  
   *(Зависимости, комбинации, баланс)*

### Графика и рендеринг

6. **Отрисовка большого количества объектов**  
   *(Инстансинг, LOD, пространственное разбиение)*
7. **Динамическое освещение в 2D**  
   *(Тени, световые карты, шейдеры)*
8. **Система частиц для магии и взрывов**  
   *(Жизненный цикл, физика)*
9. **Процедурные ландшафты**  
   *(Террейн, текстурирование, биомы)*
10. **Погода с плавными переходами**  
   *(Дождь, снег, ветер, видимость)*

### ИИ и алгоритмы

11. **Поиск пути для групп в RTS**  
   *(Оптимизация для групп, динамические изменения)*
12. **ИИ для карточной игры с блефом**  
   *(Теория игр, вероятностные модели)*
13. **Фазовый бой как в Slay the Spire**  
   *(Паттерны атак, адаптивное поведение)*
14. **Процедурные квесты с валидными условиями**  
   *(Семантические ограничения, графы зависимостей)*
15. **Эмоции NPC на основе событий**  
   *(Конечные автоматы, нейросети)*

### Сетевые технологии

16. **Синхронизация состояния в MMO**  
   *(Авторитарный сервер, предсказание, интерполяция)*
17. **Античит для мультиплеера**  
   *(Валидация действий, детекция аномалий)*
18. **P2P-архитектура для кооператива**  
   *(Децентрализованная синхронизация, разрешение конфликтов)*
19. **Рейтинговая система с учётом скилла**  
   *(TrueSkill, Glicko, матчмейкинг)*
20. **Массовые события (1000+ юнитов)**  
   *(Lockstep, детерминизм, оптимизация)*

### Системы и архитектура

21. **Сохранения сложного состояния**  
   *(Сериализация, версионность, миграции)*
22. **Редактор уровней с тестированием**  
   *(Hot-reload, компонентный подход)*
23. **Смена дня и ночи с эффектами**  
   *(Глобальное освещение, события по времени)*
24. **Оптимизация памяти на мобильных**  
   *(Пулы объектов, асинхронная загрузка)*
25. **Система модов с поддержкой скриптов**  
   *(Sandboxing, API-дизайн, хотсвоппинг)*

### Генерация контента

26. **Сбалансированные предметы**  
   *(Атрибуты, редкость, алгоритмы баланса)*
27. **Уникальные имена**  
   *(Марковские цепи, лингвистические правила)*
28. **Пещеры с проходимыми путями**  
   *(Клеточные автоматы, алгоритм Ли)*
29. **Реалистичные планетарные системы**  
   *(Физика орбит, зонирование климатов)*
30. **Музыкальные темплейты под геймплей**  
   *(Адаптивный звук, вертикальные миксы)*

### UI/UX

31. **Перетаскивание инвентаря**  
   *(Обработка событий, визуальная обратная связь)*
32. **Адаптивный интерфейс**  
   *(Якорные точки, динамическое масштабирование)*
33. **Лутбоксы с анимациями**  
   *(Вероятностные веса, визуальные эффекты)*
34. **Достижения с отслеживанием**  
   *(Event bus, триггеры, статистика)*
35. **Тактильная обратная связь**  
   *(Адаптивные вибрации, триггерные эффекты)*

### Физика и симуляции

36. **Разрушаемые объекты**  
   *(Воксельные сетки, физика фрагментов)*
37. **Реалистичная вода с волнами**  
   *(Навье–Стокс, шейдеры)*
38. **Симуляция толпы**  
   *(Agent-based модели, навигационные меши)*
39. **Баллистика с ветром**  
   *(Траектории, поправки, предсказание)*
40. **Веревки и тросы**  
   *(Verlet-интеграция, ограничения)*

### Особые механики

41. **Манипуляция временем (Braid)**  
   *(Запись состояний, ветвление)*
42. **Четырёхмерное пространство**  
   *(Проекции, навигация, визуализация)*
43. **Квантовая механика в геймплее**  
   *(Суперпозиция, запутанность)*
44. **Меняющиеся законы физики**  
   *(Динамические системы правил)*
45. **Нейроинтерфейс для управления**  
   *(ML-классификация, адаптивные пороги)*

---

## 📚 Topics — English version

### Gameplay mechanics

1. **Projectile ballistics with quadratic drag**  
   *(differential equations, Runge–Kutta, CCD)* · 🎮 demo
2. **Stat-driven critical hit system**  
   *(Poisson distribution, logit model, PRD)*
3. **Dynamic economy pricing**  
   *(differential equations, game theory, elasticity)*
4. **Spline paths and arc-length parameterization**  
   *(Bézier curves, Catmull–Rom, arc length)*
5. **Quantum state mechanics**  
   *(linear algebra, density matrices, superposition)*

### Artificial intelligence

6. **4X strategy AI (utility, MCTS, influence maps)**  
   *(utility AI, MCTS/UCT, decision trees)*
7. **Emotional NPC model (PAD + appraisal)**  
   *(PAD model, OCC, clustering)*
8. **Adaptive difficulty (skill estimation + RL)**  
   *(Q-learning, Bayesian networks, bandit)*
9. **Procedural dialogue (Markov → transformers)**  
   *(Markov chains, transformers, grammars)*
10. **Flocking / boids and crowd steering**  
   *(flocking theory, boids, spatial hash)* · 🎮 demo

### Physical simulations

24. **Cloth and soft bodies (Verlet, XPBD)**  
   *(mass-spring, Verlet integration, XPBD)* · 🎮 demo
25. **Aerodynamics and flight models**  
   *(Bernoulli, CFD, aerodynamic coefficients)*
26. **Vector fields, divergence and curl**  
   *(vector fields, divergence/curl, potential)*
27. **Heat diffusion and thermodynamics**  
   *(Fourier's equation, diffusion, entropy)*

### Optimisation systems

28. **Frame scheduling and work distribution**  
   *(linear programming, simplex, job system)*
29. **Spatial partitioning (BVH, k-d tree, grid)**  
   *(BVH, k-d tree, broadphase)*
30. **Animation compression (quantization + curve fitting)**  
   *(quantisation, splines, curves)*
31. **Profiling and the frame budget**  
   *(profiler, frame budget, p95, throttling)* · 🎮 demo
32. **Batching, instancing and draw-call reduction**  
   *(draw call, instancing, SRP Batcher, indirect draw)* · 🎮 demo
33. **Culling: frustum, occlusion and LOD**  
   *(frustum culling, occlusion, LOD, HLOD, HZB)* · 🎮 demo
34. **Data-oriented design, SIMD and cache friendliness**  
   *(SoA, SIMD, cache, alignment, AoS)*
35. **Multithreading and the job system**  
   *(job system, work stealing, tasks, main thread)*
36. **Memory: pools, GC and asset streaming**  
   *(object pools, GC, fragmentation, streaming, virtual texturing)*

### Mathematical mechanics

37. **Portals and non-Euclidean geometry**  
   *(projective geometry, quaternions, recursion)* · 🎮 demo
38. **Topological gameplay (torus, Möbius)**  
   *(topology, glues, Euler characteristic)*
39. **Entanglement as a game mechanic**  
   *(tensor algebra, Hilbert space, Bell)*
40. **Chaos, bifurcations and attractors**  
   *(chaos theory, attractors, Lyapunov exponent)* · 🎮 demo

### Statistics and balance

41. **Weapon balance analysis (regression, ANOVA)**  
   *(regression, ANOVA, TTK)*
42. **Matchmaking with Elo, Glicko-2 and TrueSkill**  
   *(Elo, Glicko-2, TrueSkill, Bayesian)* · 🎮 demo
43. **Time-series forecasting (ARIMA, seasonality)**  
   *(ARIMA, seasonality, anomalies)* · 🎮 demo
44. **Loot systems (Pareto, CLT, pity)**  
   *(Pareto distribution, CLT, pity)* · 🎮 demo

### Geometry and collisions

45. **Visibility: PVS, portals, BSP**  
   *(BSP, PVS, occlusion culling)*
46. **Ricochet and reflection vectors**  
   *(reflection, Snell's law, randomness)*

### Game economies

51. **Auction design and market clearing**  
   *(Vickrey auction, equilibrium, market)* · 🎮 demo
52. **Resource allocation and optimal control**  
   *(optimal control, LP, priorities)*
53. **In-game inflation and monetary sinks**  
   *(monetary economy, sinks, equation of exchange)*

### Audio systems

54. **Spatial audio and HRTF**  
   *(HRTF, ITD/ILD, spherical harmonics)*
55. **Physical modeling synthesis (Karplus–Strong, waveguide)**  
   *(waveguide, FIR filters, resonance)*

### Neural network applications

56. **GANs for game content**  
   *(GAN, Wasserstein, backprop)*
57. **Real-time upscaling (DLSS/FSR/XeSS)**  
   *(convolutional networks, transformers, TAA)*

### Heavy workloads and GPU

58. **Compute shaders: moving simulations to the GPU**  
   *(compute shader, workgroup, dispatch, barrier, GPGPU)* · 🎮 demo
59. **Millions of particles: GPU simulation and sorting**  
   *(particles, bitonic sort, indirect draw, GPU particles)* · 🎮 demo
60. **GPU-driven pipeline: GPU-side culling and command building**  
   *(indirect draw, GPU culling, Hi-Z, bindless, compute pipeline)*
61. **Async readback: avoiding GPU stalls**  
   *(fence, stall, readback, triple buffering, PBO)*
62. **Procedural geometry on the GPU: marching cubes and SDF**  
   *(marching cubes, SDF, isosurface, voxelization, mesh generation)*
63. **Physics and broadphase on the GPU**  
   *(broadphase, XPBD, GPU physics, contact sorting, solver)*
64. **Heavy shaders: ray marching, volumetrics and SSR**  
   *(ray marching, volumetrics, SSR, temporal reprojection, denoise)*
65. **GPU profiling: timestamps, counters and occlusion queries**  
   *(timestamp query, GPU counter, RenderDoc, occlusion query, pipeline statistics)*
66. **Quality scaling and graceful degradation**  
   *(scalability, dynamic resolution, LOD bias, fallback, tier)*

## Часть II — процедурная генерация / Part II — procedural generation

> A separate part of the research: the full atlas of content generation.

### Noise, fields and sampling

PG-01. **Gradient noise: value, Perlin and simplex**  
   *(value noise, Perlin, simplex, fBm)* · 🎮 demo
PG-02. **Worley (cellular) noise: F1, F2 and borders**  
   *(Voronoi, cellular noise, F2−F1, feature points)* · 🎮 demo
PG-03. **Poisson disk sampling and blue noise**  
   *(Bridson, blue noise, spatial hash, scattering)* · 🎮 demo
PG-04. **Seeds, hashing and reproducible generation**  
   *(PRNG, PCG, coordinate hash, determinism)* · 🎮 demo
PG-05. **Diamond-square and midpoint displacement**  
   *(fractal, heightmap, roughness, 1/f)* · 🎮 demo
PG-06. **Procedural textures (noise, FFT, weathering)**  
   *(noise, Fourier transform, tiling)* · 🎮 demo

### Layout: caves, dungeons, maps

PG-07. **Cellular automata caves**  
   *(cellular automata, 4-5 rule, connectivity, caves)* · 🎮 demo
PG-08. **BSP dungeons: splits, rooms, corridors**  
   *(BSP, tree, rooms, connectivity)* · 🎮 demo
PG-09. **Drunkard's walk caves**  
   *(random walk, carving, density, prototype)* · 🎮 demo
PG-10. **Maze generation: backtracker, Prim, Kruskal, Wilson**  
   *(spanning tree, DFS, Prim, Kruskal)* · 🎮 demo
PG-11. **Wave Function Collapse: constraint-based generation**  
   *(WFC, AC-3, entropy, tiles, backtracking)* · 🎮 demo
PG-12. **Cities and road networks: Voronoi, MST and blocks**  
   *(MST, Voronoi, A*, city building)* · 🎮 demo
PG-13. **Balanced strategy map generation**  
   *(graph theory, symmetry, fairness)* · 🎮 demo

### Worlds and terrain

PG-14. **Procedural terrain with fBm and erosion**  
   *(Perlin noise, fractals, erosion)* · 🎮 demo
PG-15. **Hydraulic erosion: rain, sediment and deltas**  
   *(erosion, sediment, heightmap, normals)* · 🎮 demo
PG-16. **Biomes: Whittaker diagram, climate and transitions**  
   *(Whittaker, temperature, moisture, climate)* · 🎮 demo
PG-17. **Rivers: flow direction, watersheds and channels**  
   *(D8, accumulation, watershed, lakes)* · 🎮 demo
PG-18. **Volumetric clouds and ray marching**  
   *(ray marching, density functions, Beer–Lambert)* · 🎮 demo
PG-19. **Procedural planetary systems**  
   *(Kepler's laws, n-body, habitable zone)* · 🎮 demo
PG-20. **Voxel worlds and marching cubes**  
   *(marching cubes, SDF, octree)* · 🎮 demo

### Content and systems

PG-21. **L-systems: plants, cities and fractal patterns**  
   *(grammar, turtle graphics, fractal, plants)* · 🎮 demo
PG-22. **Shape grammars: generative facades and interiors**  
   *(split grammar, facades, rules, LOD)* · 🎮 demo
PG-23. **Item generation: rarity, affixes and a stat budget**  
   *(loot, affixes, rarity, budget)* · 🎮 demo
PG-24. **Name generation: syllable grammar and Markov chains**  
   *(Markov, syllables, phonotactics, naming)* · 🎮 demo
PG-25. **Quests and mission graphs: keys, doors and pacing**  
   *(mission graph, lock-and-key, grammar, solvability)* · 🎮 demo
PG-26. **Procedural music with L-systems**  
   *(L-systems, music theory, Markov chains)* · 🎮 demo
PG-27. **Lotka–Volterra ecosystems**  
   *(Lotka–Volterra, dynamical systems, trophic webs)* · 🎮 demo
PG-28. **The AI director: a tension curve and enemy waves**  
   *(AI director, pacing, dynamic difficulty, waves)* · 🎮 demo

## Часть III — сетевое взаимодействие / Part III — networked multiplayer

> A separate part of the research: the full networking playbook, from UDP to large-MMO operations.

### Transport and topology

NET-01. **Transport: UDP, TCP, QUIC and WebTransport**  
   *(UDP, TCP, QUIC, MTU)* · 🎮 demo
NET-02. **Reliability over UDP: sequence, ACK, RTO and congestion control**  
   *(ACK, RTO, congestion, retransmit)* · 🎮 demo
NET-03. **Topologies: dedicated, listen, P2P, relay and mesh**  
   *(dedicated, listen, P2P, relay)* · 🎮 demo
NET-04. **NAT, STUN, TURN, ICE and hole punching**  
   *(NAT, STUN, TURN, ICE)* · 🎮 demo
NET-05. **Browsers and mobile networks: WebSocket, WebRTC and radio**  
   *(WebSocket, WebRTC, mobile, battery)*

### Synchronisation models

NET-06. **Deterministic lockstep simulation**  
   *(fixed-point, determinism, lockstep)* · 🎮 demo
NET-07. **Client-side prediction and interpolation**  
   *(Kalman filter, extrapolation, rollback)*
NET-08. **Snapshot compression and delta encoding**  
   *(Shannon entropy, quantisation, delta)*
NET-09. **Rollback netcode: resimulation for fighting games**  
   *(rollback, GGPO, prediction, determinism)* · 🎮 demo
NET-10. **Determinism and serialisation: fixed point, quantisation, bit packing**  
   *(fixed-point, quantisation, bitpacking, checksum)*

### Real-time techniques

NET-11. **Interpolation, extrapolation and jitter buffers**  
   *(interpolation, jitter, buffer, snapshots)* · 🎮 demo
NET-12. **Lag compensation: rewind and hit validation**  
   *(rewind, hitscan, latency, anti-cheat)* · 🎮 demo
NET-13. **Interest management: AOI, grids and relevance**  
   *(AOI, spatial hash, relevance, MMO)* · 🎮 demo
NET-14. **Clock and tick synchronisation: offsets, ticks and timelines**  
   *(clock, tick, NTP, timeline)*
NET-15. **Bandwidth budget: prioritisation, deltas and quantisation**  
   *(bandwidth, priority, delta, quantisation)* · 🎮 demo

### Scale and operations

NET-16. **Sharding, zones and seamless worlds**  
   *(sharding, zones, handoff, MMO)* · 🎮 demo
NET-17. **Sessions, lobbies, matchmaking and reconnect**  
   *(session, matchmaking, lobby, reconnect)* · 🎮 demo
NET-18. **MMO persistence: databases, caches, transactions and event sourcing**  
   *(database, redis, transactions, event sourcing)*
NET-19. **Anti-cheat: statistical anomaly detection**  
   *(z-score, anomalies, trust)*
NET-20. **Security: DDoS, rate limits, auth and encryption**  
   *(DDoS, rate limit, auth, encryption)* · 🎮 demo
NET-21. **Operations: metrics, SLOs, traces and live ops**  
   *(observability, SLO, metrics, live-ops)*
NET-22. **Network testing: netem, chaos and load bots**  
   *(netem, chaos, load test, replay)*

## Часть IV — баланс и прогрессия / Part IV — balance and progression

> The numbers that make a game feel the way it feels: damage, defence, the XP curve, rewards and economy.

### Damage

BAL-01. **Armour and the damage mitigation curve**  
   *(armour, mitigation, time-to-kill, curve)* · 🎮 demo
BAL-02. **The damage formula: additive and multiplicative layers**  
   *(damage formula, modifiers, buckets, stacking)*
BAL-03. **Effective HP, TTK and shots-to-kill**  
   *(EHP, TTK, STK, breakpoints)* · 🎮 demo
BAL-04. **Damage variance, hit chance and dispersion**  
   *(variance, RNG, hit chance, expected value)*
BAL-05. **Damage over time: stacks, refresh and ticks**  
   *(DoT, stacking, tick rate, uptime)*

### Defence

BAL-06. **Shields, absorption and regeneration**  
   *(shield, absorb, regen, effective HP)*
BAL-07. **Crowd control and diminishing returns**  
   *(CC, diminishing returns, immunity, PvP)*
BAL-08. **Survivability budget: stacking mitigation and caps**  
   *(stacking, diminishing returns, caps, budget)*

### Progression

BAL-09. **The XP curve and the cost of a level**  
   *(XP, curve, level cap, exponent)* · 🎮 demo
BAL-10. **Stat growth: linear, geometric and soft caps**  
   *(stat growth, power curve, scaling, caps)*
BAL-11. **Soft caps and diminishing returns**  
   *(soft cap, diminishing returns, curve, stats)*
BAL-12. **Point budgets: skill trees and the price of choice**  
   *(skill tree, budget, opportunity cost, build)*
BAL-13. **Progression pacing: gates, time-to-level and the power curve**  
   *(pacing, gates, retention, power curve)*

### Rewards and economy

BAL-14. **Reward per action: XP, drops and scaling**  
   *(reward, scaling, economy of time, quests)*
BAL-15. **Rarity bands and loot tables**  
   *(loot table, rarity, weights, item level)* · 🎮 demo
BAL-16. **Gacha: rates, soft pity and expected pulls**  
   *(gacha, pity, expected value, monetisation)* · 🎮 demo
BAL-17. **Currencies: faucets, sinks and the accumulation rate**  
   *(currency, faucet, sink, economy)*
BAL-18. **Inflation and sinks in a live economy**  
   *(inflation, sink, money supply, live ops)* · 🎮 demo
BAL-19. **Grind, energy and session loops**  
   *(grind, session, energy, retention)*

### Meta-balance

BAL-20. **Power creep and horizontal progression**  
   *(power creep, progression, content, live ops)*
BAL-21. **Difficulty curves, DDA and accessibility**  
   *(difficulty, DDA, accessibility, onboarding)*
BAL-22. **Boss tuning: phases, DPS checks and enrage**  
   *(boss, phases, DPS check, enrage)*
BAL-23. **PvP balance: normalisation, rating and gear**  
   *(PvP, normalisation, rating, gear)*
BAL-24. **Balance simulation, Monte Carlo and A/B tests**  
   *(Monte Carlo, simulation, A/B test, telemetry)* · 🎮 demo

## Часть V — атлас жанров / Part V — the genre atlas

> 36 genres: the core loop, the tempo, the usual failures and the games where the genre shows.

### Action

GEN-01. **First-person shooter**  
   *(aim, TTK, map control, gun feel)* — Session: spawn → rotate → duel → death/win → spawn   ·   TTK 0.15–1.2 s
GEN-02. **Battle royale**  
   *(shrinking, loot, risk, one life)* — Match: 100 → 1 in T ≈ 15–25 min,   P(survive) ≈ (1/2)^(fights)
GEN-03. **Fighting game**  
   *(frame data, neutral, mixup, determinism)* — input → frame N: startup, active, recovery;   advantage = (hit/block stun) − recovery
GEN-04. **Platformer**  
   *(jump arc, coyote time, level design, feel)* — h = v₀²/(2g),   t_air = 2v₀/g,   range = v₀ₓ · t_air
GEN-05. **Shoot 'em up and bullet hell**  
   *(pattern, hitbox, score, reading)* — patterns: ρ(θ) = a + b·sin(kθ + φt),   bullet speed v = const
GEN-06. **Hack & slash and character action**  
   *(combo, enemy design, rank, camera)* — style DPS = Σ damage · combo multiplier / time,   telegraph 0.3–0.6 s

### Strategy

GEN-07. **Real-time strategy**  
   *(economy, map control, counters, APM)* — income = Σ workers · gather rate · (1 − losses),   army(t) = ∫(income − spending)dt
GEN-08. **Turn-based strategy and 4X**  
   *(explore, expand, exploit, exterminate)* — growth = (science · production · territory)^(1/3) · era bonus,   expansion cost ∝ n^1.5
GEN-09. **MOBA**  
   *(lanes, snowball, team, roles)* — gold(t) = farm + bounty − deaths,   power window = item tier × level
GEN-10. **Tower defense**  
   *(pathing, economy, waves, scaling)* — position DPS = Σ towers / time in zone,   income(w) = base · (1 + k)^w,   HP(w) = hp₀ · (1 + k')^w
GEN-11. **Auto battler**  
   *(draft, economy, synergy, RNG)* — income = base_per_round + floor(gold/10) · 1 (max 5),   power = Σ units · synergies
GEN-12. **Tactical games and wargames**  
   *(initiative, cover, fog of war, permadeath)* — hit = clamp(0.05, base + acc − cover − range, 0.95),   actions = 1–2 per unit

### Role-playing

GEN-13. **JRPG**  
   *(party, turn order, story, growth)* — damage = (ATK² / (ATK + DEF)) · element · (1 + buff) · rand(0.9, 1.1)
GEN-14. **CRPG**  
   *(dialogue, builds, choice, systems)* — success ⇔ d20 + mod ≥ DC,   P = (21 − (DC − mod)) / 20
GEN-15. **Action RPG and looter shooter**  
   *(loot, builds, density, endgame)* — build DPS = damage · speed · crit · (1 + synergies),   upgrade = max(0, ilvl_new − ilvl_old)
GEN-16. **MMORPG**  
   *(social, persistence, roles, endgame)* — progress = content(season) / (time · mandatory activities),   group = tank + healer + 3 dps
GEN-17. **Souls-like**  
   *(stamina, telegraph, risk, world)* — stamina(t) = max(0, stamina₀ − Σcost + regen·t),   block damage = damage · (1 − block) − stamina_cost
GEN-18. **Roguelike and roguelite**  
   *(procedural, permadeath, synergy, runs)* — P(winning run) ≈ f(synergies, skill),   run length 20–60 min

### Simulations

GEN-19. **Management sim and tycoon**  
   *(economy, optimisation, feedback, spreadsheets)* — profit = Σ (price − cost) · volume − fixed,   growth = k · (1 − load)
GEN-20. **City builder**  
   *(zoning, traffic, services, growth)* — population' = inflow − outflow,   inflow ∝ happiness · housing · jobs · access
GEN-21. **Factory and automation**  
   *(throughput, ratios, blueprints, scaling)* — throughput = min(production, consumption, logistics),   ratio = t_produce / t_consume
GEN-22. **Life sim and social simulation**  
   *(needs, relationships, routine, emergence)* — energy(t) = Σ needs,   action = f(time, cost, mood)
GEN-23. **Survival**  
   *(resources, threat, crafting, bases)* — survival ⇔ stock(t) > consumption(t),   threat(t) ≈ k · progress(t)
GEN-24. **Sandbox and creative games**  
   *(creation, tools, sharing, no goals)* — expressiveness = tool power / interface friction

### Adventure

GEN-25. **Metroidvania**  
   *(gating, backtracking, map, abilities)* — world = graph of rooms,   edge open ⇔ ability ∈ inventory
GEN-26. **Puzzle games**  
   *(rules, insight, levels, teaching)* — difficulty ≈ available moves + depth of consequences
GEN-27. **Immersive sim**  
   *(systemic, emergent, stealth, choice)* — solutions = combinations(rules, tools, environment)
GEN-28. **Stealth**  
   *(visibility, sound, patrol, failure)* — detection ⇔ visibility · light · distance / cover + noise > threshold
GEN-29. **Horror**  
   *(tension, powerlessness, sound, pacing)* — tension(t) = lack_of_control · uncertainty / habituation
GEN-30. **Narrative adventure**  
   *(story, choice, dialogue, pacing)* — agency ≈ (choice impact) · (visible consequences)

### Sports and social games

GEN-31. **Racing games**  
   *(physics, tracks, sense of speed, progression)* — v_max ≈ P / (ρ·C_d·A)^(1/3),   grip = μ·N,   braking distance ≈ v²/(2μg)
GEN-32. **Sports games**  
   *(rules, season, ratings, meta)* — rating ≈ f(statistics, position, context),   result = rules + lineup + execution
GEN-33. **Rhythm games**  
   *(timing, charting, calibration, flow)* — grade = f(|t_press − t_note|),   Perfect ≤ 30 ms, Great ≤ 80 ms
GEN-34. **Collectible card games**  
   *(deck building, mana curve, meta, RNG)* — tempo = Σ (mana / turn),   P(draw an answer) = 1 − C(n−k, m)/C(n, m)
GEN-35. **Idle and incremental games**  
   *(exponential, prestige, numbers, automation)* — income = base · Π multipliers,   cost(n) = base · 1.15ⁿ,   time to buy ≈ cost / income
GEN-36. **Party games and social deduction**  
   *(social, bluffing, short rounds, spectators)* — round 1–5 min,   rules explained ≤ 60 s,   eliminated share at any moment ≤ 25 %

## Part VI — style and the prompt studio

> 47 style atoms across 6 layers, 8 ready-made presets and a composer that turns the dossier into a brief for a team or a language model (4 output formats).

`#part-styles` — the live block in the HTML: atlas, presets and composer.

---

## 🛠 Practical tasks — English version

### Gameplay and mechanics

1. **NPC AI in an RTS**  
   *(Unit behaviour and decision making)*
2. **Character movement physics in a platformer**  
   *(Jumping, inertia, collisions)*
3. **A dialogue system for an RPG**  
   *(Branching, conditions, consequences)*
4. **A resource crafting system**  
   *(Recipes, ingredients, probabilities)*
5. **A skill tree with progression**  
   *(Dependencies, combinations, balance)*

### Graphics and rendering

6. **Drawing a large number of objects**  
   *(Instancing, LOD, spatial partitioning)*
7. **Dynamic lighting in 2D**  
   *(Shadows, lightmaps, shaders)*
8. **A particle system for magic and explosions**  
   *(Lifecycle, physics)*
9. **Procedural landscapes**  
   *(Terrain, texturing, biomes)*
10. **Weather with smooth transitions**  
   *(Rain, snow, wind, visibility)*

### AI and algorithms

11. **Pathfinding for groups in an RTS**  
   *(Group optimisation, dynamic changes)*
12. **AI for a card game with bluffing**  
   *(Game theory, probabilistic models)*
13. **A phase-based combat like in Slay the Spire**  
   *(Attack patterns, adaptive behaviour)*
14. **Procedural quests with valid conditions**  
   *(Semantic constraints, dependency graphs)*
15. **Event-driven NPC emotions**  
   *(Finite state machines, neural networks)*

### Networking

16. **State synchronisation in an MMO**  
   *(Authoritative server, prediction, interpolation)*
17. **Anti-cheat for multiplayer**  
   *(Action validation, anomaly detection)*
18. **A P2P architecture for co-op**  
   *(Decentralised synchronisation, conflict resolution)*
19. **A skill-aware rating system**  
   *(TrueSkill, Glicko, matchmaking)*
20. **Massive events (1000+ units)**  
   *(Lockstep, determinism, optimisation)*

### Systems and architecture

21. **Saving a complex state**  
   *(Serialisation, versioning, migrations)*
22. **A level editor with testing**  
   *(Hot-reload, a component approach)*
23. **A day/night cycle with effects**  
   *(Global illumination, time-based events)*
24. **Memory optimisation on mobile**  
   *(Object pools, asynchronous loading)*
25. **A mod system with scripting support**  
   *(Sandboxing, API design, hot swapping)*

### Content generation

26. **Balanced items**  
   *(Attributes, rarity, balance algorithms)*
27. **Unique names**  
   *(Markov chains, linguistic rules)*
28. **Caves with traversable paths**  
   *(Cellular automata, the Lee algorithm)*
29. **Realistic planetary systems**  
   *(Orbital physics, climate zoning)*
30. **Music templates that follow the gameplay**  
   *(Adaptive audio, vertical mixes)*

### UI/UX

31. **Drag and drop in the inventory**  
   *(Event handling, visual feedback)*
32. **An adaptive interface**  
   *(Anchors, dynamic scaling)*
33. **Loot boxes with animations**  
   *(Probabilistic weights, visual effects)*
34. **Achievements with tracking**  
   *(An event bus, triggers, statistics)*
35. **Haptic feedback**  
   *(Adaptive vibrations, triggered effects)*

### Physics and simulations

36. **Destructible objects**  
   *(Voxel grids, fragment physics)*
37. **Realistic water with waves**  
   *(Navier–Stokes, shaders)*
38. **Crowd simulation**  
   *(Agent-based models, navigation meshes)*
39. **Ballistics with wind**  
   *(Trajectories, corrections, prediction)*
40. **Ropes and cables**  
   *(Verlet integration, constraints)*

### Special mechanics

41. **Time manipulation (Braid)**  
   *(State recording, branching)*
42. **Four-dimensional space**  
   *(Projections, navigation, visualisation)*
43. **Quantum mechanics in gameplay**  
   *(Superposition, entanglement)*
44. **Physics laws that change**  
   *(Dynamic rule systems)*
45. **A neural interface for control**  
   *(ML classification, adaptive thresholds)*

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
| 1 | Геймплейные механики | Gameplay mechanics |
| 2 | Искусственный интеллект | Artificial intelligence |
| 3 | Компьютерная графика | Computer graphics |
| 4 | Физические симуляции | Physical simulations |
| 5 | Системы оптимизации | Optimisation systems |
| 6 | Математические механики | Mathematical mechanics |
| 7 | Статистика и баланс | Statistics and balance |
| 8 | Геометрия и коллизии | Geometry and collisions |
| 9 | Шейдеры и GPU | Shaders and GPU |
| 10 | Игровые экономики | Game economies |
| 11 | Аудио-системы | Audio systems |
| 12 | Нейросетевые приложения | Neural network applications |
| 13 | Тяжёлые нагрузки и GPU | Heavy workloads and GPU |
| 14 | Процедурная генерация | Procedural generation |
| 15 | Сетевое взаимодействие | Networked multiplayer |
| 16 | Баланс и прогрессия | Balance and progression |
| 17 | Атлас жанров | Genre atlas |
| 18 | Стиль и студия промптов | Style and the prompt studio |

---

## 📄 Лицензия и источники

Код и тексты — для обучения и прототипирования. Ссылки на игры приведены как примеры
того, где встречается тот или иной алгоритм.
