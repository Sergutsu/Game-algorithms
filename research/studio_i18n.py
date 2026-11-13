# -*- coding: utf-8 -*-
"""Подписи и шаблоны студии промптов (Часть VI), RU + EN.

Сборщик подставляет только таблицу нужного языка, поэтому английская
страница никогда не содержит русского текста. Шаблоны промпта — это
текст с {placeholder}, который заполняет assets/studio.js.
"""

STUDIO_UI = {
    "ru": {
        "kicker": "Часть VI · атлас стилей и студия промптов",
        "title": "Стиль и студия промптов",
        "subtitle": "Из досье — в задание",
        "lede": ("Первые части дают механики, баланс и жанры. Эта собирает из них бриф: "
                 "выберите жанр, добавьте два-три балансовых принципа, наложите стиль — "
                 "и получите промпт, с которым можно идти к команде или языковой модели."),
        "note": ("Промпт — это бюджет внимания: чем точнее названы числа и ограничения, "
                 "тем меньше остаётся места для среднего результата. Пустые слоты лучше "
                 "оставлять пустыми, чем заполнять клише."),
        "atlas_title": "Атлас стилей",
        "atlas_hint": "шесть слоёв, из которых складывается вид игры",
        "presets_title": "Пресеты",
        "presets_hint": "готовые комбинации — начните с них",
        "preset_apply": "собрать промпт",
        "composer_title": "Конструктор промпта",
        "composer_hint": "жанр + баланс + стиль → задание",
        "step_genre": "01 · Жанр",
        "step_balance": "02 · Балансовые принципы — до 3",
        "step_style": "03 · Стиль — до 6",
        "step_constraints": "04 · Ограничения",
        "step_output": "05 · Формат выдачи",
        "team": "Команда",
        "platform": "Платформа",
        "scope": "Масштаб",
        "monetisation": "Монетизация",
        "hook": "Одна фраза о сути (необязательно)",
        "hook_ph": "например: город, который помнит каждую смерть игрока",
        "extra": "Дополнительные ограничения (необязательно)",
        "extra_ph": "например: без сетевого режима, весь текст на одном экране",
        "prompt": "Готовый промпт",
        "copy": "копировать",
        "copied": "скопировано",
        "reset": "сбросить",
        "random": "случайный набор",
        "download": "скачать .md",
        "counter": "выбрано",
        "empty": "Выберите жанр — и промпт появится здесь.",
        "search_ph": "фильтр: жанр, стиль, принцип…",
        "team_1": "соло",
        "team_5": "2–5 человек",
        "team_20": "6–20 человек",
        "team_100": "20+ человек",
        "plat_pc": "PC",
        "plat_web": "браузер",
        "plat_mobile": "мобильные",
        "plat_console": "консоли",
        "scope_jam": "геймджем / 2 недели",
        "scope_small": "малая игра, 3–6 месяцев",
        "scope_full": "полная игра, 1–3 года",
        "scope_live": "live-сервис",
        "mono_premium": "премиум",
        "mono_f2p": "free-to-play",
        "mono_none": "без монетизации",
        "labels": {
            "genre": "Жанр",
            "loop": "Ядро цикла",
            "session": "Сессия",
            "pacing": "Ритм",
            "balance": "Балансовые принципы",
            "art": "Визуальный язык",
            "constraints": "Ограничения",
            "team": "команда",
            "platform": "платформа",
            "scope": "масштаб",
            "monetisation": "монетизация",
            "hook": "Суть",
            "extra": "Дополнительно",
            "deliverable": "Что нужно на выходе",
            "rules": "Правила ответа",
            "not": "Чем игра не является",
            "risk": "Главный риск и проверка",
            "missing": "(не выбрано — уберите строку или выберите)",
            "refs": "Референсы",
        },
        "prompt_template": (
            "Ты — геймдизайнер и креативный директор. Собери концепт игры.\n\n"
            "{sections}\n\n"
            "{deliverable}\n\n"
            "ПРАВИЛА ОТВЕТА\n"
            "- Никаких прилагательных без числа: «иммерсивный», «эпичный», «революционный» "
            "запрещены без конкретной метрики или механики.\n"
            "- Каждое утверждение опирается на число, жанровую конвенцию или названный референс.\n"
            "- Назови три риска и один прототип, который проверяет главный риск за две недели.\n"
            "- Явно перечисли, чем игра не является.\n"
            "- Числа из блока баланса используй как решения: TTK, кривая, бюджет — "
            "не пересказывай их общими словами.\n"
        ),
        "section_templates": {
            "genre": "ЖАНР\n- {title} — {summary}\n- Ядро цикла: {loop}\n- Темп: {session}; {pacing}",
            "balance": "БАЛАНС\n{items}",
            "balance_item": "- {title}: {summary}",
            "art": "ВИЗУАЛЬНЫЙ ЯЗЫК И ЗВУК\n{items}",
            "art_item": "- {group}: {text}",
            "constraints": "ОГРАНИЧЕНИЯ\n- Команда: {team}\n- Платформа: {platform}\n"
                           "- Масштаб: {scope}\n- Монетизация: {monetisation}",
            "hook": "СУТЬ\n{text}",
            "extra": "ДОПОЛНИТЕЛЬНО\n{text}",
            "deliverable": "ЧТО НУЖНО НА ВЫХОДЕ: {name}\n{items}",
        },
        "formats": {
            "pitch": ["логлайн в одном предложении", "три столпа дизайна, каждый с механикой",
                      "ядро цикла из пяти шагов с длительностью", "целевой игрок и его мотивация",
                      "два референса и одна честная отличие от них", "чем игра не является",
                      "главный риск и прототип на две недели с критерием провала"],
            "gdd": ["цели дизайна и антицели", "системы: цикл, прогрессия, экономика, бой",
                    "формулы и числа из блока баланса", "контент: уровни, враги, предметы — с объёмом",
                    "UX: экраны, HUD, онбординг", "технические риски и бюджет производства",
                    "метрики успеха и способы их измерить"],
            "llm": ["составь концепт строго по слоям выше", "для каждой системы дай формулу и число",
                    "предложи три варианта сеттинга, различающихся тоном, но не механикой",
                    "укажи, какие решения противоречат друг другу и почему",
                    "предложи тест на две недели и метрику, которая его провалит"],
            "prototype": ["первая неделя: одно ядро, серые блоки, никакой косметики",
                          "вторая неделя: один цикл целиком от старта до награды",
                          "что вырезать, если сроки поехали", "критерий провала и метрика",
                          "что проверить на трёх игроках и какие вопросы задать"],
        },
    },
    "en": {
        "kicker": "Part VI · style atlas and prompt studio",
        "title": "Style and the prompt studio",
        "subtitle": "From dossier to brief",
        "lede": ("The earlier parts give you mechanics, balance and genres. This part assembles a "
                 "brief from them: pick a genre, add two or three balance principles, apply a "
                 "style — and get a prompt you can take to a team or a language model."),
        "note": ("A prompt is a budget of attention: the more precisely the numbers and "
                 "constraints are named, the less room is left for an average result. Empty "
                 "slots are better left empty than filled with clichés."),
        "atlas_title": "Style atlas",
        "atlas_hint": "six layers that make up the look of a game",
        "presets_title": "Presets",
        "presets_hint": "ready combinations — start here",
        "preset_apply": "build the prompt",
        "composer_title": "Prompt composer",
        "composer_hint": "genre + balance + style → brief",
        "step_genre": "01 · Genre",
        "step_balance": "02 · Balance principles — up to 3",
        "step_style": "03 · Style — up to 6",
        "step_constraints": "04 · Constraints",
        "step_output": "05 · Output format",
        "team": "Team",
        "platform": "Platform",
        "scope": "Scope",
        "monetisation": "Monetisation",
        "hook": "One line about the core (optional)",
        "hook_ph": "e.g. a city that remembers every player death",
        "extra": "Extra constraints (optional)",
        "extra_ph": "e.g. no multiplayer, all text on one screen",
        "prompt": "Ready prompt",
        "copy": "copy",
        "copied": "copied",
        "reset": "reset",
        "random": "random set",
        "download": "download .md",
        "counter": "selected",
        "empty": "Pick a genre and the prompt will appear here.",
        "search_ph": "filter: genre, style, principle…",
        "team_1": "solo",
        "team_5": "2–5 people",
        "team_20": "6–20 people",
        "team_100": "20+ people",
        "plat_pc": "PC",
        "plat_web": "browser",
        "plat_mobile": "mobile",
        "plat_console": "consoles",
        "scope_jam": "game jam / 2 weeks",
        "scope_small": "small game, 3–6 months",
        "scope_full": "full game, 1–3 years",
        "scope_live": "live service",
        "mono_premium": "premium",
        "mono_f2p": "free-to-play",
        "mono_none": "no monetisation",
        "labels": {
            "genre": "Genre",
            "loop": "Core loop",
            "session": "Session",
            "pacing": "Tempo",
            "balance": "Balance principles",
            "art": "Visual language and sound",
            "constraints": "Constraints",
            "team": "team",
            "platform": "platform",
            "scope": "scope",
            "monetisation": "monetisation",
            "hook": "Core",
            "extra": "Extra",
            "deliverable": "Deliverable",
            "rules": "Answer rules",
            "not": "What the game is not",
            "risk": "Main risk and the test",
            "missing": "(nothing picked — remove the line or pick one)",
            "refs": "References",
        },
        "prompt_template": (
            "You are a game designer and creative director. Build a game concept.\n\n"
            "{sections}\n\n"
            "{deliverable}\n\n"
            "ANSWER RULES\n"
            "- No adjective without a number: “immersive”, “epic”, “revolutionary” are banned "
            "unless backed by a concrete metric or mechanic.\n"
            "- Every claim rests on a number, a genre convention or a named reference.\n"
            "- Name three risks and one prototype that tests the main risk within two weeks.\n"
            "- State explicitly what the game is not.\n"
            "- Use the numbers from the balance block as decisions: TTK, curve, budget — do not "
            "restate them in general words.\n"
        ),
        "section_templates": {
            "genre": "GENRE\n- {title} — {summary}\n- Core loop: {loop}\n- Tempo: {session}; {pacing}",
            "balance": "BALANCE\n{items}",
            "balance_item": "- {title}: {summary}",
            "art": "VISUAL LANGUAGE AND SOUND\n{items}",
            "art_item": "- {group}: {text}",
            "constraints": "CONSTRAINTS\n- Team: {team}\n- Platform: {platform}\n"
                           "- Scope: {scope}\n- Monetisation: {monetisation}",
            "hook": "CORE\n{text}",
            "extra": "EXTRA\n{text}",
            "deliverable": "DELIVERABLE: {name}\n{items}",
        },
        "formats": {
            "pitch": ["a one-sentence logline", "three design pillars, each with a mechanic",
                      "the core loop in five steps with durations", "the target player and their motivation",
                      "two comparables and one honest difference from them", "what the game is not",
                      "the main risk and a two-week prototype with a fail criterion"],
            "gdd": ["design goals and anti-goals", "systems: loop, progression, economy, combat",
                    "formulas and numbers from the balance block", "content: levels, enemies, items — with volume",
                    "UX: screens, HUD, onboarding", "technical risks and production budget",
                    "success metrics and how to measure them"],
            "llm": ["assemble the concept strictly by the layers above", "give a formula and a number for every system",
                    "propose three settings that differ in tone but not in mechanics",
                    "point out which decisions contradict each other and why",
                    "propose a two-week test and the metric that would fail it"],
            "prototype": ["week one: one core, grey boxes, no cosmetics",
                          "week two: one full loop from start to reward",
                          "what to cut if the schedule slips", "the fail criterion and the metric",
                          "what to test with three players and which questions to ask"],
        },
    },
}
