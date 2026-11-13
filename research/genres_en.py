# -*- coding: utf-8 -*-
"""English formula/complexity for the genre dossiers (Part V).

The genre topics carry a bilingual identity card: `formula` holds the core
loop, `complexity` holds the session length, the tempo figure and the key
metric. English text lives here so that topics_en_genres_*.py stay free of
duplicated structure.
"""

GENRE_EN_EXTRA = {
    "g-fps": dict(
        formula=("Session: spawn → rotate → duel → death/win → spawn   ·   TTK 0.15–1.2 s",
                 "TTK = EHP / DPS; STK = ceil(EHP / damage). The target TTK defines the subgenre: arcade — longer, tactical — shorter and deadlier."),
        complexity=("session 5–20 min", "TTK 0.15–1.2 s", "key metric: hit share and time to first contact"),
    ),
    "g-br": dict(
        formula=("Match: 100 → 1 in T ≈ 15–25 min,   P(survive) ≈ (1/2)^(fights)",
                 "Each even fight roughly halves the chance of making it to the end. That is why early aggression is about information and loot, not just kills."),
        complexity=("session 15–25 min", "zone 12–16 min", "key metric: survival by time and fights per match"),
    ),
    "g-fighting": dict(
        formula=("input → frame N: startup, active, recovery;   advantage = (hit/block stun) − recovery",
                 "Every move is a window in frames at 60 Hz: 1 frame ≈ 16.7 ms. Plus on block means the attacker acts before the defender."),
        complexity=("match 2–5 min", "window 1–20 frames", "key metric: win rate by rank and combo length"),
    ),
    "g-platformer": dict(
        formula=("h = v₀²/(2g),   t_air = 2v₀/g,   range = v₀ₓ · t_air",
                 "h is jump height, v₀ initial speed, g gravity. These three numbers define the geometry of every level."),
        complexity=("room 10–40 s", "precision ±2 frames", "key metric: share of deaths on a room's first attempt"),
    ),
    "g-shmup": dict(
        formula=("patterns: ρ(θ) = a + b·sin(kθ + φt),   bullet speed v = const",
                 "Pattern density is set by the sine and its rotation speed. Test passability with a corridor: the minimum gap must be 3–4× the hitbox."),
        complexity=("session 3–8 min", "reaction 0.2–0.4 s", "key metric: survival by wave and score per minute"),
    ),
    "g-hackslash": dict(
        formula=("style DPS = Σ damage · combo multiplier / time,   telegraph 0.3–0.6 s",
                 "The multiplier grows with move variety and drops on repetition. Rank is a function of variety, not only of kill speed."),
        complexity=("arena 1–3 min", "telegraph 0.3–0.6 s", "key metric: average rank and damage taken without dodging"),
    ),
    "g-rts": dict(
        formula=("income = Σ workers · gather rate · (1 − losses),   army(t) = ∫(income − spending)dt",
                 "Economy is an integrator: a 10 % income lead gives an army lead that grows over time, which is why economy nerfs hit harder than unit nerfs."),
        complexity=("match 15–40 min", "first contact 2.5–5 min", "key metric: attention distribution and economy tempo"),
    ),
    "g-tbs": dict(
        formula=("growth = (science · production · territory)^(1/3) · era bonus,   expansion cost ∝ n^1.5",
                 "Expansion cost must grow faster than its benefit (exponent 1.3–1.7), otherwise expansion is always optimal."),
        complexity=("campaign 10–30 h", "turn 20–60 s", "key metric: time per turn in mid-game"),
    ),
    "g-moba": dict(
        formula=("gold(t) = farm + bounty − deaths,   power window = item tier × level",
                 "A kill grants ~300 gold and XP, but killing a streaking player grants more — a brake on the leader."),
        complexity=("match 20–45 min", "power window 10–20 min", "key metric: win rate by role and gold distribution"),
    ),
    "g-towerdef": dict(
        formula=("position DPS = Σ towers / time in zone,   income(w) = base · (1 + k)^w,   HP(w) = hp₀ · (1 + k')^w",
                 "k' should slightly exceed k: the threat outgrows income, otherwise the game is over by wave 20."),
        complexity=("level 15–30 min", "wave 20–60 s", "key metric: leaks and income by wave 20"),
    ),
    "g-autobattler": dict(
        formula=("income = base_per_round + floor(gold/10) · 1 (max 5),   power = Σ units · synergies",
                 "The classic scheme gives 1 interest per 10 gold, capped at +5 per round, so greed is a strategy with a price."),
        complexity=("round 20–40 s", "match 20–30 min", "key metric: share of rounds decided by composition"),
    ),
    "g-wargame": dict(
        formula=("hit = clamp(0.05, base + acc − cover − range, 0.95),   actions = 1–2 per unit",
                 "Keep hit chance in the 5–95 % band: 100 % kills tension, 0 % kills trust."),
        complexity=("mission 20–60 min", "odds 5–95 %", "key metric: share of missions finished without losses"),
    ),
    "g-jrpg": dict(
        formula=("damage = (ATK² / (ATK + DEF)) · element · (1 + buff) · rand(0.9, 1.1)",
                 "The quadratic form gives a gentle level advantage without nullifying defence — a genre classic."),
        complexity=("session 30–90 min", "campaign 30–60 h", "key metric: share of battles won without losses"),
    ),
    "g-crpg": dict(
        formula=("success ⇔ d20 + mod ≥ DC,   P = (21 − (DC − mod)) / 20",
                 "At +5 against DC 15 success is 55 %. Show the DC and the modifier: the player must understand the risk."),
        complexity=("campaign 40–80 h", "check d20", "key metric: share of decisions that change content"),
    ),
    "g-arpg": dict(
        formula=("build DPS = damage · speed · crit · (1 + synergies),   upgrade = max(0, ilvl_new − ilvl_old)",
                 "Upgrade frequency matters more than magnitude: one significant item every 20 minutes beats ten small ones per hour."),
        complexity=("session 20–60 min", "loot every 30–90 s", "key metric: upgrades per hour and time to a new build"),
    ),
    "g-mmo": dict(
        formula=("progress = content(season) / (time · mandatory activities),   group = tank + healer + 3 dps",
                 "The classic dungeon group is five: 1 tank, 1 healer, 3 damage. Queue time depends on role scarcity."),
        complexity=("session 1–4 h", "season 8–12 weeks", "key metric: retention and queue time by role"),
    ),
    "g-soulslike": dict(
        formula=("stamina(t) = max(0, stamina₀ − Σcost + regen·t),   block damage = damage · (1 − block) − stamina_cost",
                 "Stamina regen is usually 30–50 per second against a pool of 100–140: two or three actions then a pause."),
        complexity=("session 30–120 min", "telegraph 0.3–0.6 s", "key metric: attempts per boss and deaths to unknown attacks"),
    ),
    "g-roguelike": dict(
        formula=("P(winning run) ≈ f(synergies, skill),   run length 20–60 min",
                 "Target win rate: 5–15 % for a newcomer, 40–60 % for a veteran. Above 80 % variance has vanished."),
        complexity=("run 20–60 min", "decision every 30–60 s", "key metric: win rate and build variety encountered"),
    ),
    "g-sim": dict(
        formula=("profit = Σ (price − cost) · volume − fixed,   growth = k · (1 − load)",
                 "A load limit is a natural brake: the closer the system is to capacity, the more the next step costs."),
        complexity=("session 1–3 h", "cycle 1–5 min", "key metric: profit growth per cycle and time to the first bottleneck"),
    ),
    "g-citybuilder": dict(
        formula=("population' = inflow − outflow,   inflow ∝ happiness · housing · jobs · access",
                 "Growth almost always runs into traffic and services. Keep a 30–40 % capacity reserve on main arteries."),
        complexity=("session 2–5 h", "tick 1–5 s", "key metric: average commute time and capacity reserve"),
    ),
    "g-factory": dict(
        formula=("throughput = min(production, consumption, logistics),   ratio = t_produce / t_consume",
                 "A plant is always limited by its weakest link. Design recipes with multiple times (0.5 / 1 / 2 s)."),
        complexity=("session 2–6 h", "tick 1/60 s", "key metric: machine load and the plant bottleneck"),
    ),
    "g-lifesim": dict(
        formula=("energy(t) = Σ needs,   action = f(time, cost, mood)",
                 "The key balance is the day: 24 hours should fit 60–70 % of what the player wants."),
        complexity=("session 1–3 h", "day 24 in-game hours", "key metric: whether the player achieves their plans"),
    ),
    "g-survival": dict(
        formula=("survival ⇔ stock(t) > consumption(t),   threat(t) ≈ k · progress(t)",
                 "The threat must grow with progress: the stronger the base, the more dangerous the night."),
        complexity=("session 1–4 h", "day cycle 10–20 min", "key metric: deaths by hour and resource shortage"),
    ),
    "g-sandbox": dict(
        formula=("expressiveness = tool power / interface friction",
                 "The entry barrier is inversely proportional to friction: every extra button filters out some players."),
        complexity=("session 20 min – ∞", "no fixed goal", "key metric: share of players publishing their work"),
    ),
    "g-metroidvania": dict(
        formula=("world = graph of rooms,   edge open ⇔ ability ∈ inventory",
                 "An ability should open 2–4 graph edges, otherwise it is one-use."),
        complexity=("session 1–3 h", "game 10–25 h", "key metric: backtracking time and forgotten doors"),
    ),
    "g-puzzle": dict(
        formula=("difficulty ≈ available moves + depth of consequences",
                 "Difficulty comes from depth, not from field size. Verify there is one “beautiful” solution."),
        complexity=("session 15–45 min", "level 1–10 min", "key metric: share solved without hints"),
    ),
    "g-imsim": dict(
        formula=("solutions = combinations(rules, tools, environment)",
                 "The number of solutions grows combinatorially. Test 3–5 “crazy” solutions in every room."),
        complexity=("session 1–2 h", "level 20–60 min", "key metric: paths to the goal and unplanned solutions"),
    ),
    "g-stealth": dict(
        formula=("detection ⇔ visibility · light · distance / cover + noise > threshold",
                 "The threshold should be visible in the UI and patrols predictable: the player learns a system."),
        complexity=("session 30–90 min", "detection 0.5–3 s", "key metric: share of levels cleared without an alarm"),
    ),
    "g-horror": dict(
        formula=("tension(t) = lack_of_control · uncertainty / habituation",
                 "Habituation grows with every repetition: change the shape of the threat, not only its strength."),
        complexity=("session 45–120 min", "peak 10–60 s", "key metric: resource spend and safe minutes"),
    ),
    "g-narrative": dict(
        formula=("agency ≈ (choice impact) · (visible consequences)",
                 "An illusory choice with a dramatic presentation feels worse than no choice at all."),
        complexity=("session 40–120 min", "game 5–20 h", "key metric: share of scenes affected by the player"),
    ),
    "g-racing": dict(
        formula=("v_max ≈ P / (ρ·C_d·A)^(1/3),   grip = μ·N,   braking distance ≈ v²/(2μg)",
                 "Top speed grows as the cube root of power, so upgrades give less and less. Braking distance grows quadratically."),
        complexity=("race 5–20 min", "lap 1–3 min", "key metric: lap-time gap between novice and expert"),
    ),
    "g-sports": dict(
        formula=("rating ≈ f(statistics, position, context),   result = rules + lineup + execution",
                 "Ratings must be multidimensional: speed, passing, shooting, defence. A single number makes selection trivial."),
        complexity=("match 5–15 min", "season 20–40 matches", "key metric: win distribution by tactic"),
    ),
    "g-rhythm": dict(
        formula=("grade = f(|t_press − t_note|),   Perfect ≤ 30 ms, Great ≤ 80 ms",
                 "Total latency = audio + input + display latency. Calibration must compensate for the sum."),
        complexity=("track 2–5 min", "window 25–90 ms", "key metric: Perfect share and calibration drift"),
    ),
    "g-ccg": dict(
        formula=("tempo = Σ (mana / turn),   P(draw an answer) = 1 − C(n−k, m)/C(n, m)",
                 "Hypergeometric distribution: 3 copies in 30 cards with 5 in hand gives ~42 %. That is what fair draw means."),
        complexity=("match 5–15 min", "meta 2–6 weeks", "key metric: share of cards in 80 %+ of decks"),
    ),
    "g-idle": dict(
        formula=("income = base · Π multipliers,   cost(n) = base · 1.15ⁿ,   time to buy ≈ cost / income",
                 "The classic cost step is 1.10–1.20 per purchase, which creates the permanent nearness of the next upgrade."),
        complexity=("session 5–20 min", "cycle 1–60 s", "key metric: time to the next upgrade"),
    ),
    "g-party": dict(
        formula=("round 1–5 min,   rules explained ≤ 60 s,   eliminated share at any moment ≤ 25 %",
                 "Three numbers decide whether people play again: round length, teaching time and the wait for eliminated players."),
        complexity=("round 1–5 min", "teaching 60 s", "key metric: share of players who play again"),
    ),
}
