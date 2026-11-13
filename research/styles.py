# -*- coding: utf-8 -*-
"""Часть VI: атлас стилей и студия промптов.

Здесь лежат данные, а не текст темы: группы стиля, атомы (короткие
формулировки, которые попадают в промпт), пресеты, форматы выдачи и
двуязычные подписи студии. Сборщик превращает это в интерактивный
конструктор: жанр + баланс + стиль + ограничения → готовый промпт.
"""

# --------------------------------------------------------------------------
# группы стилевых атомов: (ключ, цвет, порядок)
# --------------------------------------------------------------------------
STYLE_GROUP_ORDER = ["look", "palette", "camera", "mood", "audio", "texture"]

STYLE_GROUPS = {
    "look": {
        "color": "#fbbf6b", "num": "01",
        "ru": ("Взгляд и рендер",
               "Как игра выглядит технически: пиксели, рисунок, low-poly, воксели, "
               "фотореализм. Это первое решение, которое отсекает половину остальных."),
        "en": ("Look and rendering",
               "How the game looks technically: pixels, drawing, low-poly, voxels, "
               "photorealism. It is the first decision and it rules out half of the rest."),
    },
    "palette": {
        "color": "#f9a8d4", "num": "02",
        "ru": ("Палитра и свет",
               "Ограниченная палитра задаёт настроение сильнее любого сюжета. "
               "Тёплый закат, неоновый нуар, выцветший пепел, пастель — это язык эмоций."),
        "en": ("Palette and light",
               "A limited palette sets the mood more strongly than any plot. "
               "Warm dusk, neon noir, faded ash, pastel — this is the language of emotion."),
    },
    "camera": {
        "color": "#7dd3fc", "num": "03",
        "ru": ("Камера и пространство",
               "Изометрия, сайдскролл, первое лицо, близкое третье — камера определяет, "
               "что игрок видит, а значит, и во что он играет."),
        "en": ("Camera and space",
               "Isometric, side-scrolling, first-person, close third: the camera decides "
               "what the player sees and therefore what they play."),
    },
    "mood": {
        "color": "#c4b5fd", "num": "04",
        "ru": ("Тон и эмоция",
               "Надежда, меланхолия, жуть, задор, эпос, сатира. Тон — это обещание, "
               "которое игра даёт игроку в первые тридцать секунд."),
        "en": ("Tone and emotion",
               "Hope, melancholy, dread, playfulness, epic scale, satire. Tone is the "
               "promise a game makes in its first thirty seconds."),
    },
    "audio": {
        "color": "#5eead4", "num": "05",
        "ru": ("Звук и музыка",
               "Чиптюн, оркестр, индастриал, эмбиент, лоу-фай, фолк. Звук задаёт темп "
               "и запоминается раньше, чем графика."),
        "en": ("Sound and music",
               "Chiptune, orchestra, industrial, ambient, lo-fi, folk. Sound sets the "
               "tempo and is remembered before the graphics."),
    },
    "texture": {
        "color": "#bef264", "num": "06",
        "ru": ("Фактура и интерфейс",
               "Диегетический HUD, минимум интерфейса, «сочность» отклика, тактильность, "
               "документальная сухость. Это то, что чувствуется пальцами."),
        "en": ("Texture and interface",
               "Diegetic HUD, minimal UI, juicy feedback, tactility, documentary dryness. "
               "This is what the fingers feel."),
    },
}

# --------------------------------------------------------------------------
# атомы стиля: id → группа + короткие формулировки для промпта
# --------------------------------------------------------------------------
STYLE_ATOMS = [
    # ---- look
    {"id": "pixel-lowres", "g": "look",
     "ru": ("Пиксель-арт низкого разрешения", "пиксель-арт 240×135, ограниченная палитра, видимый пиксель, анимация на 8–12 кадрах"),
     "en": ("Low-resolution pixel art", "240×135 pixel art, limited palette, visible pixels, 8–12 frame animation")},
    {"id": "hand-drawn", "g": "look",
     "ru": ("Рисованный 2D", "рисованные вручную спрайты и фоны, живая линия, мягкие тени, акварельные заливки"),
     "en": ("Hand-drawn 2D", "hand-drawn sprites and backdrops, lively linework, soft shadows, watercolour fills")},
    {"id": "stylized-3d", "g": "look",
     "ru": ("Стилизованный 3D", "стилизованный 3D с крупными формами, плоскими материалами и читаемыми силуэтами"),
     "en": ("Stylised 3D", "stylised 3D with chunky forms, flat materials and readable silhouettes")},
    {"id": "photoreal", "g": "look",
     "ru": ("Фотореализм", "PBR-материалы, физически корректный свет, кинематографичная оптика, честные тени"),
     "en": ("Photorealism", "PBR materials, physically based lighting, cinematic optics, honest shadows")},
    {"id": "lowpoly-ps1", "g": "look",
     "ru": ("Low-poly в духе PS1", "низкополигональные модели, аффинные текстуры, дрожание вершин, туман как туман"),
     "en": ("PS1-style low-poly", "low-poly models, affine textures, vertex wobble, fog as fog")},
    {"id": "voxel", "g": "look",
     "ru": ("Воксели", "воксельная геометрия, разрушаемые блоки, крупные объёмы, простые материалы"),
     "en": ("Voxels", "voxel geometry, destructible blocks, chunky volumes, simple materials")},
    {"id": "vector-flat", "g": "look",
     "ru": ("Векторный флэт", "чистые векторные формы, плоские цвета, геометрическая сетка, минимум текстуры"),
     "en": ("Vector flat", "clean vector shapes, flat colours, geometric grid, minimal texture")},
    {"id": "painterly", "g": "look",
     "ru": ("Живописный", "живописные фоны с видимым мазком, атмосферная перспектива, свет как краска"),
     "en": ("Painterly", "painted backdrops with visible brushwork, atmospheric perspective, light as paint")},
    {"id": "anime-cel", "g": "look",
     "ru": ("Аниме-селл", "селл-шейдинг, чёткие контуры, драматичные ракурсы, скоростные линии"),
     "en": ("Anime cel", "cel shading, crisp outlines, dramatic angles, speed lines")},
    {"id": "clay-felt", "g": "look",
     "ru": ("Пластилин и ткань", "съёмочная миниатюра: пластилин, фетр, картон, видимая фактура и швы"),
     "en": ("Clay and felt", "a shot miniature: clay, felt, cardboard, visible texture and seams")},

    # ---- palette
    {"id": "neon-noir", "g": "palette",
     "ru": ("Неоновый нуар", "чёрная основа, кислотный неон, дождь и отражения, контражур"),
     "en": ("Neon noir", "black base, acid neon, rain and reflections, rim light")},
    {"id": "warm-cozy", "g": "palette",
     "ru": ("Тёплый уют", "янтарь, терракота, сливочный свет, мягкие тени, вечернее золото"),
     "en": ("Warm cosy", "amber, terracotta, cream light, soft shadows, evening gold")},
    {"id": "desaturated-grim", "g": "palette",
     "ru": ("Выцветшая суровость", "низкая насыщенность, серо-зелёный, пыль, редкие акценты крови и золота"),
     "en": ("Desaturated grimness", "low saturation, grey-green, dust, rare accents of blood and gold")},
    {"id": "pastel-soft", "g": "palette",
     "ru": ("Мягкая пастель", "пастель, молочные тени, розовый и мята, ощущение бумаги"),
     "en": ("Soft pastel", "pastels, milky shadows, pink and mint, the feel of paper")},
    {"id": "duotone", "g": "palette",
     "ru": ("Дуотон", "два цвета и их оттенки, высокий контраст, графичность постера"),
     "en": ("Duotone", "two colours and their shades, high contrast, poster-like graphics")},
    {"id": "mono-ink", "g": "palette",
     "ru": ("Монохром и тушь", "чёрно-белая тушь, штриховка, белая бумага, один акцентный цвет"),
     "en": ("Monochrome ink", "black-and-white ink, hatching, white paper, a single accent colour")},
    {"id": "solarpunk", "g": "palette",
     "ru": ("Соларпанк", "зелень, стекло, тёплый солнечный свет, медь и мох, оптимизм"),
     "en": ("Solarpunk", "greenery, glass, warm sunlight, copper and moss, optimism")},
    {"id": "acid-brutalist", "g": "palette",
     "ru": ("Кислотный брутализм", "серый бетон, кислотный акцент, крупная типографика, резкие тени"),
     "en": ("Acid brutalism", "grey concrete, an acid accent, big typography, hard shadows")},

    # ---- camera
    {"id": "cam-iso", "g": "camera",
     "ru": ("Изометрия", "изометрическая камера, фиксированный угол, читаемые тайлы, глубина через масштаб"),
     "en": ("Isometric", "isometric camera, fixed angle, readable tiles, depth through scale")},
    {"id": "cam-side", "g": "camera",
     "ru": ("Сайдскролл", "боковая камера, один вектор движения, параллакс-слои, кадр как сцена"),
     "en": ("Side-scrolling", "side camera, one movement vector, parallax layers, a framed stage")},
    {"id": "cam-fps", "g": "camera",
     "ru": ("Первое лицо", "камера от первого лица, оружие в кадре, широкий FOV, инерция головы"),
     "en": ("First person", "first-person camera, weapon in frame, wide FOV, head inertia")},
    {"id": "cam-tps", "g": "camera",
     "ru": ("Близкое третье лицо", "камера за плечом, персонаж в кадре, плавное следование, кинематографичность"),
     "en": ("Close third person", "over-the-shoulder camera, character in frame, smooth follow, cinematic")},
    {"id": "cam-topdown", "g": "camera",
     "ru": ("Вид сверху", "камера сверху, вся арена в кадре, тактическое чтение пространства"),
     "en": ("Top-down", "overhead camera, the whole arena in frame, tactical reading of space")},
    {"id": "cam-fixed", "g": "camera",
     "ru": ("Фиксированные планы", "фиксированные планы как в старом кино, смена ракурса между экранами"),
     "en": ("Fixed shots", "fixed shots like old cinema, angle changes between screens")},
    {"id": "cam-cinematic", "g": "camera",
     "ru": ("Кинематографичная", "плавные кинематографичные проезды, широкий формат, глубина резкости"),
     "en": ("Cinematic", "smooth cinematic moves, widescreen framing, depth of field")},

    # ---- mood
    {"id": "mood-hopeful", "g": "mood",
     "ru": ("Надежда", "тон надежды и восстановления: мир сломан, но его можно починить"),
     "en": ("Hope", "a tone of hope and repair: the world is broken but can be mended")},
    {"id": "mood-melancholy", "g": "mood",
     "ru": ("Меланхолия", "тихая меланхолия, утрата, медленное время, красота в пустоте"),
     "en": ("Melancholy", "quiet melancholy, loss, slow time, beauty in emptiness")},
    {"id": "mood-eerie", "g": "mood",
     "ru": ("Жуть", "тихая жуть: что-то не так, но это нельзя назвать словами"),
     "en": ("Eerie", "quiet dread: something is wrong and cannot be named")},
    {"id": "mood-playful", "g": "mood",
     "ru": ("Задор", "задор и юмор, быстрый темп, преувеличенная анимация"),
     "en": ("Playful", "playfulness and humour, fast tempo, exaggerated animation")},
    {"id": "mood-epic", "g": "mood",
     "ru": ("Эпос", "эпический масштаб, большие пространства, торжественность"),
     "en": ("Epic", "epic scale, vast spaces, solemnity")},
    {"id": "mood-satire", "g": "mood",
     "ru": ("Сатира", "сатира и абсурд, узнаваемые типажи, злая улыбка"),
     "en": ("Satire", "satire and absurdity, recognisable types, a mean smile")},
    {"id": "mood-intimate", "g": "mood",
     "ru": ("Интимность", "интимность и близость, маленькие пространства, личные истории"),
     "en": ("Intimacy", "intimacy and closeness, small spaces, personal stories")},
    {"id": "mood-clinical", "g": "mood",
     "ru": ("Холодная клиника", "клиническая точность, стерильность, бюрократия, тревога порядка"),
     "en": ("Clinical", "clinical precision, sterility, bureaucracy, the anxiety of order")},

    # ---- audio
    {"id": "audio-chiptune", "g": "audio",
     "ru": ("Чиптюн", "чиптюн на 2–3 каналах, арифметические волны, шумовые ударные"),
     "en": ("Chiptune", "2–3 channel chiptune, arithmetic waves, noise percussion")},
    {"id": "audio-orchestral", "g": "audio",
     "ru": ("Оркестр", "живой оркестр, лейтмотивы, динамические слои по напряжению"),
     "en": ("Orchestral", "a live orchestra, leitmotifs, dynamic layers driven by tension")},
    {"id": "audio-industrial", "g": "audio",
     "ru": ("Индастриал", "индустриальные ритмы, металл, механический гул, дисторшн"),
     "en": ("Industrial", "industrial rhythms, metal, mechanical hum, distortion")},
    {"id": "audio-ambient", "g": "audio",
     "ru": ("Эмбиент", "эмбиент-дроны, тишина как инструмент, редкие события"),
     "en": ("Ambient", "ambient drones, silence as an instrument, rare events")},
    {"id": "audio-lofi", "g": "audio",
     "ru": ("Лоу-фай", "лоу-фай биты, тёплая шершавость, джазовые аккорды, винил"),
     "en": ("Lo-fi", "lo-fi beats, warm grit, jazz chords, vinyl")},
    {"id": "audio-folk", "g": "audio",
     "ru": ("Фолк", "акустический фолк, живые инструменты, локальные лады"),
     "en": ("Folk", "acoustic folk, live instruments, local modes")},
    {"id": "audio-synthwave", "g": "audio",
     "ru": ("Синтвейв", "синтвейв, аналоговые пэды, гейтед-барабаны, широкое стерео"),
     "en": ("Synthwave", "synthwave, analogue pads, gated drums, wide stereo")},
    {"id": "audio-diegetic", "g": "audio",
     "ru": ("Диегетический звук", "звук только из мира: радио, шаги, ветер; музыки почти нет"),
     "en": ("Diegetic sound", "sound from the world only: radio, footsteps, wind; almost no score")},

    # ---- texture / interface
    {"id": "ui-diegetic", "g": "texture",
     "ru": ("Диегетический HUD", "интерфейс внутри мира: приборы, записки, физические шкалы"),
     "en": ("Diegetic HUD", "interface inside the world: gauges, notes, physical scales")},
    {"id": "ui-minimal", "g": "texture",
     "ru": ("Минимальный интерфейс", "минимум интерфейса, информация через мир и звук"),
     "en": ("Minimal UI", "minimal interface, information through the world and sound")},
    {"id": "juice-heavy", "g": "texture",
     "ru": ("Сочный отклик", "сильный отклик: хитстоп, тряска, частицы, вспышки, звук на каждое действие"),
     "en": ("Heavy juice", "strong feedback: hitstop, shake, particles, flashes, a sound for every action")},
    {"id": "tactile", "g": "texture",
     "ru": ("Тактильность", "тактильные детали: перетаскивание, вес предметов, физические ручки и кнопки"),
     "en": ("Tactility", "tactile details: dragging, item weight, physical levers and buttons")},
    {"id": "docu-calm", "g": "texture",
     "ru": ("Документальная сдержанность", "сдержанная подача без эффектов, длинные планы, доверие к тишине"),
     "en": ("Documentary calm", "restrained presentation without effects, long shots, trust in silence")},
    {"id": "systemic", "g": "texture",
     "ru": ("Системность", "каждое действие имеет системное следствие; правила важнее скриптов"),
     "en": ("Systemic design", "every action has a systemic consequence; rules matter more than scripts")},
]

# --------------------------------------------------------------------------
# пресеты: готовые комбинации «жанр + стиль + баланс»
# --------------------------------------------------------------------------
STYLE_PRESETS = [
    {
        "id": "cozy-farm",
        "ru": ("Тёплый уют: ферма и соседи", "Медленная жизнь, тёплый свет и маленькие личные истории."),
        "en": ("Warm cosy: farm and neighbours", "Slow life, warm light and small personal stories."),
        "genre": "g-lifesim", "balance": ["prog-pacing", "bal-grind"],
        "atoms": ["pixel-lowres", "warm-cozy", "cam-iso", "mood-hopeful", "audio-lofi", "tactile"],
    },
    {
        "id": "neon-extraction",
        "ru": ("Неоновый экстракшн", "Быстрый шутер, риск и кислотный свет в мокром городе."),
        "en": ("Neon extraction", "A fast shooter, risk and acid light in a wet city."),
        "genre": "g-fps", "balance": ["dmg-ehp", "bal-lootband"],
        "atoms": ["stylized-3d", "neon-noir", "cam-fps", "mood-eerie", "audio-industrial", "juice-heavy"],
    },
    {
        "id": "grim-souls",
        "ru": ("Суровый соулс", "Выцветший мир, тяжёлые удары и честные телеграфы."),
        "en": ("Grim souls", "A faded world, heavy blows and honest telegraphs."),
        "genre": "g-soulslike", "balance": ["dmg-mitigation", "def-crowd"],
        "atoms": ["photoreal", "desaturated-grim", "cam-tps", "mood-melancholy", "audio-orchestral", "ui-minimal"],
    },
    {
        "id": "sky-platformer",
        "ru": ("Небесный платформер", "Солнечные острова, точный прыжок и радость движения."),
        "en": ("Sky platformer", "Sunny islands, precise jumps and the joy of movement."),
        "genre": "g-platformer", "balance": ["dmg-ehp"],
        "atoms": ["hand-drawn", "pastel-soft", "cam-side", "mood-playful", "audio-orchestral", "juice-heavy"],
    },
    {
        "id": "brutal-factory",
        "ru": ("Бетонная фабрика", "Серый бетон, идеальные пропорции и гул станков."),
        "en": ("Concrete factory", "Grey concrete, perfect ratios and the hum of machines."),
        "genre": "g-factory", "balance": ["bal-currency", "bal-powercreep"],
        "atoms": ["stylized-3d", "acid-brutalist", "cam-iso", "mood-clinical", "audio-industrial", "ui-minimal"],
    },
    {
        "id": "deep-horror",
        "ru": ("Глубокий космос: страх", "Тесные коридоры, темнота и звук, который врёт."),
        "en": ("Deep space horror", "Tight corridors, darkness and sound that lies."),
        "genre": "g-horror", "balance": ["dmg-dot", "def-shield"],
        "atoms": ["photoreal", "duotone", "cam-fps", "mood-eerie", "audio-diegetic", "docu-calm"],
    },
    {
        "id": "folk-mystery",
        "ru": ("Деревенская мистика", "Туман, обряды и разговоры, в которых все что-то скрывают."),
        "en": ("Folk mystery", "Fog, rituals and conversations where everyone hides something."),
        "genre": "g-crpg", "balance": ["bal-difficulty", "prog-pacing"],
        "atoms": ["painterly", "mono-ink", "cam-fixed", "mood-melancholy", "audio-folk", "ui-diegetic"],
    },
    {
        "id": "retro-bullet",
        "ru": ("Ретро-пулевой ад", "Пиксели, узоры и музыка, которая держит ритм."),
        "en": ("Retro bullet hell", "Pixels, patterns and music that keeps the beat."),
        "genre": "g-shmup", "balance": ["dmg-variance"],
        "atoms": ["pixel-lowres", "mono-ink", "cam-topdown", "mood-epic", "audio-chiptune", "juice-heavy"],
    },
]

# --------------------------------------------------------------------------
# форматы выдачи промпта
# --------------------------------------------------------------------------
PROMPT_FORMATS = [
    {
        "id": "pitch",
        "ru": ("Питч на одну страницу", "Короткий документ для команды или инвестора: идея, цикл, стиль, отличие."),
        "en": ("One-page pitch", "A short document for the team or an investor: idea, loop, style, difference."),
    },
    {
        "id": "gdd",
        "ru": ("Каркас GDD", "Структура дизайн-документа: системы, экономика, контент, риски."),
        "en": ("GDD skeleton", "A design-document structure: systems, economy, content, risks."),
    },
    {
        "id": "llm",
        "ru": ("Промпт для языковой модели", "Роль, ограничения, критерии качества и запрет на клише."),
        "en": ("LLM prompt", "Role, constraints, quality rubric and a ban on clichés."),
    },
    {
        "id": "prototype",
        "ru": ("План прототипа на 2 недели", "Что сделать руками, чтобы проверить главный риск."),
        "en": ("2-week prototype plan", "What to build by hand to test the main risk."),
    },
]

# --------------------------------------------------------------------------
# подписи студии (RU + EN)
# --------------------------------------------------------------------------
STUDIO_STRINGS = {
    "kicker": {"ru": "Часть VI · атлас стилей и студия промптов",
               "en": "Part VI · style atlas and prompt studio"},
    "title": {"ru": "Стиль и студия промптов", "en": "Style and the prompt studio"},
    "subtitle": {"ru": "Из досье — в задание", "en": "From dossier to brief"},
    "lede": {
        "ru": ("Три части досье дают механики, баланс и жанры. Эта собирает из них задание: "
               "выберите жанр, добавьте два-три балансовых принципа, наложите стиль — "
               "и получите готовый промпт для команды или языковой модели."),
        "en": ("The earlier parts give you mechanics, balance and genres. This part assembles a "
               "brief from them: pick a genre, add two or three balance principles, apply a "
               "style — and get a prompt ready for a team or a language model."),
    },
    "note": {
        "ru": ("Промпт — это не магия, а бюджет внимания: чем точнее названы числа, "
               "тем меньше остаётся места для среднего результата."),
        "en": ("A prompt is not magic but a budget of attention: the more precisely the numbers "
               "are named, the less room is left for an average result."),
    },
    "atlas_title": {"ru": "Атлас стилей", "en": "Style atlas"},
    "atlas_hint": {"ru": "шесть слоёв, из которых складывается вид игры",
                   "en": "six layers that make up the look of a game"},
    "presets_title": {"ru": "Пресеты", "en": "Presets"},
    "presets_hint": {"ru": "готовые комбинации — начните с них", "en": "ready combinations — start here"},
    "composer_title": {"ru": "Конструктор промпта", "en": "Prompt composer"},
    "composer_hint": {"ru": "жанр + баланс + стиль → задание", "en": "genre + balance + style → brief"},
    "step_genre": {"ru": "01 · Жанр", "en": "01 · Genre"},
    "step_balance": {"ru": "02 · Балансовые принципы (до 3)", "en": "02 · Balance principles (up to 3)"},
    "step_style": {"ru": "03 · Стиль (до 6)", "en": "03 · Style (up to 6)"},
    "step_constraints": {"ru": "04 · Ограничения", "en": "04 · Constraints"},
    "step_output": {"ru": "05 · Формат выдачи", "en": "05 · Output format"},
    "team": {"ru": "Команда", "en": "Team"},
    "platform": {"ru": "Платформа", "en": "Platform"},
    "scope": {"ru": "Масштаб", "en": "Scope"},
    "monetisation": {"ru": "Монетизация", "en": "Monetisation"},
    "prompt": {"ru": "Промпт", "en": "Prompt"},
    "copy": {"ru": "копировать", "en": "copy"},
    "copied": {"ru": "скопировано", "en": "copied"},
    "reset": {"ru": "сбросить", "en": "reset"},
    "random": {"ru": "случайный набор", "en": "random set"},
    "download": {"ru": "скачать .md", "en": "download .md"},
    "counter": {"ru": "выбрано", "en": "selected"},
    "empty": {"ru": "Выберите жанр — и промпт появится здесь.",
              "en": "Pick a genre and the prompt will appear here."},
    "team_1": {"ru": "соло", "en": "solo"},
    "team_5": {"ru": "2–5 человек", "en": "2–5 people"},
    "team_20": {"ru": "6–20 человек", "en": "6–20 people"},
    "team_100": {"ru": "20+ человек", "en": "20+ people"},
    "plat_pc": {"ru": "PC", "en": "PC"},
    "plat_web": {"ru": "браузер", "en": "browser"},
    "plat_mobile": {"ru": "мобильные", "en": "mobile"},
    "plat_console": {"ru": "консоли", "en": "consoles"},
    "scope_jam": {"ru": "геймджем / 2 недели", "en": "game jam / 2 weeks"},
    "scope_small": {"ru": "малая игра, 3–6 месяцев", "en": "small game, 3–6 months"},
    "scope_full": {"ru": "полная игра, 1–3 года", "en": "full game, 1–3 years"},
    "scope_live": {"ru": "live-сервис", "en": "live service"},
    "mono_premium": {"ru": "премиум", "en": "premium"},
    "mono_f2p": {"ru": "free-to-play", "en": "free-to-play"},
    "mono_none": {"ru": "без монетизации", "en": "no monetisation"},
}
