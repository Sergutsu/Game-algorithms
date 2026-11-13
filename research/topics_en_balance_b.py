# -*- coding: utf-8 -*-
"""English content for Part IV topics 118–128: rewards, economy and meta-balance."""

TOPICS_EN_BAL_B = [
    dict(
        id="bal-xpreward",
        title="Reward per action: XP, drops and scaling",
        tags=["reward", "scaling", "economy of time", "quests"],
        summary="A reward is not a number but a ratio: how much XP an action gives against how much XP is needed. As soon as that ratio shifts, old content becomes either mandatory or pointless.",
        detail=[
            "The simplest healthy scheme scales the reward from the <b>player's level</b>, not the mob's level. Then all content stays relevant. The reverse scheme creates grey zones: the player outgrows a location and it is no longer needed — fine for a linear campaign, fatal for an open world.",
            "Compute <b>reward per minute</b> for every activity: combat, quests, dungeons, PvP, crafting. If one type pays three times more, the rest become decoration. A useful practice is to convert all activities into one currency (say “XP per minute”) and compare them in a table.",
            "Separate the reward for <b>risk</b> from the reward for <b>time</b>. A hard boss must pay for the attempt, not only for the kill; otherwise players pick the safest and dullest activity. Conversely, passive activity must never out-earn active play.",
        ],
        formula=("reward = base · (1 + k·(level_target − level_player)) · multiplier(content)\n"
                 "rate = reward / minutes",
                 "k is small (0.05–0.15): a mild bonus for content above your level and a penalty for content far below. Keep the rate ratio between activities within 1.2–1.5×."),
        steps=[
            "Build a table of activities with typical time and reward.",
            "Compute the rate (reward/minute) for each and even out the discrepancies.",
            "Tie scaling to the player's level or to the level difference.",
            "Add a reward for the attempt where content is hard and requires many tries.",
            "Recompute the table whenever progression tempo changes.",
        ],
        complexity=("O(1) per reward", "O(1)", "The “activity → reward/minute” table is the cheapest balance tool in existence."),
        code=("python", """ACTIVITIES = {
    #                minutes  base_xp  risk
    "mob grind":     (0.5,      90,     1.0),
    "quest":         (4.0,      650,    1.1),
    "dungeon run":   (20.0,    3400,    1.4),
    "boss attempt":  (6.0,      420,    1.8),   # reward for trying, not only winning
    "pvp match":     (12.0,    2100,    1.6),
}

for name, (minutes, xp, risk) in ACTIVITIES.items():
    print(f"{name:14s} {xp / minutes:7.0f} xp/min  (risk x{risk})")"""),
        pitfalls=[
            "Scaling rewards from the mob's level: old locations turn into garbage.",
            "One activity pays several times more — the rest become decoration.",
            "A reward only for winning hard content, so players choose safe farming.",
            "A reward that never scales: by mid-game it has been devalued.",
        ],
        games=["World of Warcraft", "Elden Ring", "Genshin Impact", "Path of Exile"],
    ),
    dict(
        id="bal-lootband",
        title="Rarity bands and loot tables",
        tags=["loot table", "rarity", "weights", "item level"],
        summary="Loot is a distribution, not a list. Rarity bands shape the distribution, weights set probabilities, and item level scales the numbers inside a band.",
        detail=[
            "The classic structure is a <b>rarity tier</b> (common, uncommon, rare, epic, legendary) with weights like 1000 / 300 / 80 / 18 / 2. Probability = weight / total weight. The important part is not the absolute percentages but the <b>ratios</b>: how many times rarer a legendary is than an epic. Ratios are what players feel.",
            "Item level (ilvl) sets the <b>stat budget</b>: the sum of stats on an item is f(ilvl). Inside a rarity band the budget is multiplied by a coefficient (say rare ×1.35). Then item power is predictable and rarity is a multiplier rather than a lottery of random numbers.",
            "For the feeling of luck, <b>guarantees and pity-weighted rolls</b> matter: dry streaks of 50 kills at a 2 % chance happen regularly. Add a failure counter that raises the weight, and a ceiling (“guaranteed drop within N”). And always show where the item came from: the sense of the source is part of the reward.",
        ],
        formula=("P(tier) = wᵗ / Σw,   budget = B(ilvl) · rarity_mult,   Σstats = budget",
                 "Weights set ratios, ilvl sets scale. Keep rarity_mult in the 1.0–1.6 band: a wider gap makes the lower tiers garbage."),
        steps=[
            "Define rarity tiers and weights; check the ratios, not just the percentages.",
            "Define the stat budget as a function of ilvl and a multiplier per tier.",
            "Build drop tables per source (mob, chest, boss) with independent weights.",
            "Add a failure counter and a guarantee for the top tiers.",
            "Validate the distribution by simulation: 10 000 drops and a histogram by tier.",
        ],
        complexity=("O(#tiers) per drop", "O(1)", "One roll over cumulative weights is cheaper than a roll per tier."),
        code=("python", """import bisect, random

TIERS = [("common", 1000, 1.00), ("uncommon", 300, 1.10),
         ("rare", 80, 1.25), ("epic", 18, 1.45), ("legendary", 2, 1.70)]
WEIGHTS = [w for _, w, _ in TIERS]
CUMSUM = []
acc = 0
for w in WEIGHTS:
    acc += w
    CUMSUM.append(acc)

def roll_tier(rng):
    return TIERS[bisect.bisect_left(CUMSUM, rng.random() * acc)][0]

def stat_budget(ilvl, mult):
    return round((10 + 2.5 * ilvl) * mult, 1)

rng = random.Random(3)
counts = {}
for _ in range(10_000):
    t = roll_tier(rng)
    counts[t] = counts.get(t, 0) + 1
print({k: round(v / 100, 2) for k, v in counts.items()}, "%")"""),
        pitfalls=[
            "Watching absolute percentages and missing the ratios between tiers.",
            "A random stat budget inside a tier: the player cannot tell whether the item is “good”.",
            "No guarantee: dry streaks read as broken drops.",
            "Drops without a source: the player cannot connect the reward to the action.",
        ],
        games=["World of Warcraft", "Diablo IV", "Path of Exile", "Borderlands 3"],
        demo="lootbands",
    ),
    dict(
        id="bal-gacha",
        title="Gacha: rates, soft pity and expected pulls",
        tags=["gacha", "pity", "expected value", "monetisation"],
        summary="A gacha mechanic is a distribution of pulls until the reward. You must count the median and p90 pulls, not the chance per pull: they decide how much a player spends or how soon they leave.",
        detail=[
            "With a fixed chance p, the number of pulls until success is geometric: E = 1/p, median ≈ ln2/p, p90 ≈ ln10/p. At p = 0.6 % the expectation is 167 pulls, but 10 % of players will not get the reward within 383. It is the tail, not the mean, that reads as “the gacha is greedy”.",
            "<b>Soft pity</b> raises the chance after a threshold (for example +6 % per step after pull 74), <b>hard pity</b> guarantees it at N. Soft pity compresses the tail while barely moving the mean; hard pity makes the upper bound known and turns spending into a plan. Together they give both predictability and revenue.",
            "Transparency is mandatory: published rates, a counter to the guarantee, and history. A hidden pity system is a legal and reputational risk, not a “secret trick”. And compute the full cost of the reward in currency: 1/p · pull price is the real price of the character.",
        ],
        formula=("P(k) = (1−p)^(k−1)·p,   E = 1/p,   median ≈ ln2/p,   p90 ≈ ln10/p",
                 "With soft pity the chance at step k is p_k = p + c·max(0, k − s). Hard pity H makes P(k > H) = 0 and the expectation ≈ 0.7–0.9·H."),
        steps=[
            "Choose the base chance and the target median and p90 pulls.",
            "Add soft pity: threshold s and step c tuned so that the median hits the target.",
            "Add hard pity and check the expectation by simulation rather than by formula.",
            "Publish the rates and make the guarantee counter visible.",
            "Compute the full cost in currency and compare it with direct purchases.",
        ],
        complexity=("O(1) per pull", "O(1)", "Simulating 10⁶ players takes seconds on a laptop and immediately reveals p99 — the number behind most complaints."),
        code=("python", """import random

def pulls_until_hit(rng, p=0.006, soft_start=74, soft_step=0.06, hard=90):
    for k in range(1, hard + 1):
        chance = p + (soft_step * (k - soft_start) if k >= soft_start else 0.0)
        if rng.random() < min(1.0, chance) or k == hard:
            return k

def simulate(n=200_000, **kw):
    rng = random.Random(42)
    data = sorted(pulls_until_hit(rng, **kw) for _ in range(n))
    return (sum(data) / n, data[n // 2], data[int(n * 0.9)], data[-1])

mean, med, p90, worst = simulate()
print(f"mean {mean:.1f}  median {med}  p90 {p90}  worst {worst}")"""),
        pitfalls=[
            "Counting only the mean and ignoring p90 — p90 is what generates complaints.",
            "Hidden pity: legal risk and loss of trust once discovered.",
            "Hard pity without a visible counter: the player cannot tell how much is left.",
            "A soft-pity step that is too steep breaks the reward economy after the threshold.",
        ],
        games=["Genshin Impact", "Fate/Grand Order", "Honkai: Star Rail", "Puzzle & Dragons"],
        demo="gacha",
    ),
    dict(
        id="bal-currency",
        title="Currencies: faucets, sinks and the accumulation rate",
        tags=["currency", "faucet", "sink", "economy"],
        summary="An economy is a bathtub: faucets pour currency in, sinks drain it out. If the faucets are wider than the sinks, the currency devalues; if narrower, the player cannot afford anything and leaves.",
        detail=[
            "Every currency has a <b>faucet</b> (source: rewards, selling loot, quests) and a <b>sink</b> (spend: repairs, crafting, auction fees, consumables, cosmetics). The health of the economy is the inflow-to-outflow ratio per hour: 0.9–1.1 on average, with seasonal swings. Compute it separately for each currency.",
            "The sink should be <b>voluntary but attractive</b>: a tax you cannot avoid feels like punishment, while an optional spend with tangible benefit feels like a decision. Good sinks: repair after death, crafting accelerators, cosmetics, auction listings, stat re-forging.",
            "On having many currencies: each new one is a new faucet and sink, and the player must understand where it comes from. If a currency exists for a single purchase, make it a resource instead. The rule: no more than 3–4 “real” currencies, everything else is an item.",
        ],
        formula=("ΔM = (Σfaucets − Σsinks) · dt,   inflation ≈ ΔM / M,   price ≈ k · M / supply",
                 "M — the server's money supply. If inflow consistently exceeds outflow by 5–10 % per hour, prices multiply overnight — that is MMO inflation."),
        steps=[
            "List every faucet and sink per currency with numbers per hour of play.",
            "Compute the ΔM balance and the target prices of key goods.",
            "Make the sink mandatory in meaning but optional in action.",
            "Add automatic statistics: currency mass on the server, median prices.",
            "Install a “fuse”: if prices rise above X, trigger an additional sink.",
        ],
        complexity=("O(#faucets + #sinks)", "O(1)", "Measure not “how much gold exists” but “how much gold per hour per player” — that is the controllable quantity."),
        code=("python", """FAUCETS = {"quests": 1200, "mob drops": 900, "vendor junk": 400}   # gold / hour
SINKS = {"repairs": 600, "crafting": 800, "auction fee": 500}

inflow, outflow = sum(FAUCETS.values()), sum(SINKS.values())
delta = inflow - outflow
print(f"in {inflow}/h  out {outflow}/h  delta {delta:+}/h  ratio {inflow / outflow:.2f}")

# what one hour of play does to the money supply
supply = 1_000_000
for hour in range(1, 6):
    supply += delta
    print(f"hour {hour}: supply {supply:,}  (+{delta * hour / 1_000_000:.1%} of the start)")"""),
        pitfalls=[
            "Faucets wider than sinks — hyperinflation within the first week.",
            "Unavoidable sinks (a tax on air) feel like punishment.",
            "Too many currencies: the player loses track of where things come from.",
            "No metrics on currency mass: inflation is discovered when it is too late.",
        ],
        games=["World of Warcraft", "EVE Online", "Albion Online", "RuneScape"],
    ),
    dict(
        id="bal-inflation",
        title="Inflation and sinks in a live economy",
        tags=["inflation", "sink", "money supply", "live ops"],
        summary="MMO inflation is inevitable: players farm faster than they spend. The question is not how to avoid it but how to keep it in a corridor before content loses its value.",
        detail=[
            "Inflation in a game is the growth of money supply relative to goods. While new players outnumber leavers, gold inflow rises and prices rise with it. Symptoms: basic resources get expensive while new items cost the same, and veterans buy everything. Metrics: <b>the median price of a basic resource</b> and the gold mass per active player.",
            "Tools: an <b>auction tax</b> (proportional, not fixed), repairs, consumables, burning materials in high-tier crafting, lotteries and bets, seasonal resets, transfer fees. Crucially, the sink must grow with the money mass — progressive, not fixed.",
            "A separate problem is <b>concentration</b>: even with a healthy total, 1 % of players may hold 80 % of the gold and control the market. That is cured not only by sinks but by institutions: purchase limits, regional markets, bound items, anti-flipping fees.",
        ],
        formula=("π ≈ (inflow − sink) / M · dt,   progressive sink = α · M^β (β > 1)",
                 "A progressive sink (β > 1) brakes inflation harder the richer the server is, without hurting newcomers."),
        steps=[
            "Instrument: gold mass, median prices of the top-10 goods, wealth share of the top 1 %.",
            "Make sinks progressive: the more money in the economy, the higher the effective fee.",
            "Add a mandatory but fair sink (repairs, consumables) and optional prestigious ones.",
            "Plan seasonal resets or new tiers so money does not sit idle.",
            "React to metrics: if a price rises 30 % in a week, trigger an additional sink.",
        ],
        complexity=("O(1) per transaction", "O(#goods)", "This must be measured server-side and regularly: an economy is an observed system, not a static table."),
        code=("python", """def era_tick(money, faucet_rate, sink_rate, beta=1.15, alpha=0.0004, dt_hours=1.0):
    \"\"\"Progressive sink: the richer the economy, the stronger the drain.\"\"\"
    sink = sink_rate + alpha * (money ** beta)
    money += (faucet_rate - sink) * dt_hours
    return max(money, 0.0), sink

money = 1_000_000.0
for hour in range(0, 72, 12):
    for _ in range(12):
        money, sink = era_tick(money, 250_000, 30_000)
    print(f"hour {hour:3d}: money {money:12,.0f}  sink/h {sink:9,.0f}")"""),
        pitfalls=[
            "A fixed sink against a growing money mass: inflation is guaranteed.",
            "Sinks that hit newcomers (expensive repairs at the start) but not the rich.",
            "Ignoring wealth concentration: a handful of players capture the market.",
            "A seasonal reset without compensation: veterans leave, the economy and trust reset together.",
        ],
        games=["World of Warcraft", "EVE Online", "RuneScape", "Albion Online"],
        demo="inflation",
    ),
    dict(
        id="bal-grind",
        title="Grind, energy and session loops",
        tags=["grind", "session", "energy", "retention"],
        summary="Grind is a repeatable action with a reward. It is not bad in itself; it is bad when the repetition offers no new skill and no new decision, only time.",
        detail=[
            "Three kinds of repetition: <b>skilful</b> (the same task, but the player improves), <b>variable</b> (conditions and decisions change) and <b>empty</b> (time in exchange for a number). The first two are normal; the third is what people mean by grind. The sign of an empty loop: the player can do it without looking at the screen.",
            "Session limits (energy, daily rewards, raid cooldowns) control tempo but conflict with the pleasure of a long session. The rule: a limit should protect the player from overplaying, not punish enthusiasm. Daily bonuses work better as “catch-up” (accumulating over missed days) than as burning rewards.",
            "Measure <b>time to the first interesting reward</b> in the loop and the number of decisions per minute. If a five-minute loop spends four minutes on a familiar route, shorten it or add variance (modifiers, random events, escalation).",
        ],
        formula=("loop efficiency = reward / (action time + travel time)",
                 "Measure per loop, not per hour: the loop is what the player repeats a hundred times. If travel time exceeds action time, the loop feels like work."),
        steps=[
            "Break the loop into steps and time each one in a real playtest.",
            "Remove dead time: running, waiting, loading, repeated dialogue.",
            "Add variance: modifiers, random events, different objectives.",
            "Make limits catch-up rather than burn-off.",
            "Compare the reward per loop with other loops — they must be comparable.",
        ],
        complexity=("O(1) per loop", "O(1)", "A stopwatch on a playtest yields more than any spreadsheet."),
        code=("python", """CYCLE = [("travel", 95), ("fight", 70), ("loot", 15), ("travel back", 95)]

def cycle_efficiency(steps, reward=900):
    action = sum(s for n, s in steps if n in ("fight", "loot"))
    total = sum(s for _, s in steps)
    return total, action / total, reward / (total / 60)

total, share, per_min = cycle_efficiency(CYCLE)
print(f"cycle {total}s  action share {share:.0%}  reward {per_min:.0f}/min")"""),
        pitfalls=[
            "Running and waiting take more time than the action itself.",
            "Burning daily rewards: missing a day punishes more than it motivates.",
            "Energy that stops the player exactly when they are engaged.",
            "An empty loop without variance: the player can play without looking at the screen.",
        ],
        games=["World of Warcraft", "Genshin Impact", "Diablo IV", "Warframe"],
    ),
    dict(
        id="bal-powercreep",
        title="Power creep and horizontal progression",
        tags=["power creep", "progression", "content", "live ops"],
        summary="Every new item tier devalues the previous one. The life of a game is a race between power inflation and content inflation, and it can only be won by planning both.",
        detail=[
            "Vertical growth (“every expansion +50 ilvl”) is simple and understandable, but requires enemies, rewards and old raids to grow the same way. After three years the numbers triple and old content becomes decoration. Horizontal growth (new <i>variants</i>, not bigger numbers) preserves content but demands choice design.",
            "A workable hybrid: a <b>small vertical step</b> (5–10 % per season) plus <b>horizontal</b> mechanics (sets, talents, specialisations). Verticality delivers the feeling of growth, horizontality gives a reason to try something new. Keep a “reference build” for checking: a new season must not make it unplayable.",
            "Plan <b>number squashing</b> in advance: once damage exceeds 10⁹ the UI breaks and the player loses the sense of scale. A squish is not a sign of failure but a planned operation, and it must be done without losing the feel.",
        ],
        formula=("power(n) = power(0) · (1 + v)ⁿ,   content(n) = content(0) · (1 + v')ⁿ,   balance ⇔ v ≈ v'",
                 "v — seasonal vertical growth, v' — content growth. If v > v' for two seasons in a row, old content becomes irrelevant; if v < v', the player feels stagnation."),
        steps=[
            "Set the seasonal vertical step (usually 5–10 %) and keep it for a year.",
            "Add horizontal mechanics so a season changes the game, not only the numbers.",
            "Define a reference build and test it every season.",
            "Plan a stat squish ahead: once every 2–3 years or when the limit is exceeded.",
            "Watch difficulty inflation: old raids must stay playable (or be deliberately retired).",
        ],
        complexity=("O(1) per season", "O(#content)", "Recomputing content after a squish is the expensive part; do it in one go, not piecemeal."),
        code=("python", """def season_power(base=1000, rate=0.08, seasons=8):
    return [base * (1 + rate) ** n for n in range(seasons)]

def old_content_share(new_power, old_content_hp, ratio=3.0):
    \"\"\"How much of the old content stays meaningful.\"\"\"
    return old_content_hp * ratio / new_power

powers = season_power()
for n, p in enumerate(powers):
    print(f"season {n}: power {p:8.0f}  old content relevance {old_content_share(p, 1000):.2f}")"""),
        pitfalls=[
            "Vertical growth without content growth: old raids and items lose all value.",
            "Horizontal growth without vertical: the player does not feel stronger.",
            "A stat squish without retuning the feel: players see smaller numbers and assume a nerf.",
            "A new progression currency every season: the player loses track of the system.",
        ],
        games=["World of Warcraft", "Destiny 2", "Path of Exile", "Final Fantasy XIV"],
    ),
    dict(
        id="bal-difficulty",
        title="Difficulty curves, DDA and accessibility",
        tags=["difficulty", "DDA", "accessibility", "onboarding"],
        summary="Difficulty is not a number but the ratio of demand to the player's capability. The curve must grow a little slower than skill so the player lives in the “hard but doable” zone.",
        detail=[
            "Demand rises with levels, capability rises with experience and gear. If demand outpaces it, the player hits a wall; if it lags, the game becomes boring. A good curve is a sawtooth: a difficulty spike, then a plateau where the player learns the new tools, then the next spike.",
            "<b>Dynamic difficulty</b> (DDA) adapts to the player. It is attractive but visible: if enemies “adjust”, rewards lose value and death stops meaning anything. Safe forms: adapt tempo (enemy count) rather than damage; offer hidden help after a run of deaths; offer to lower the difficulty instead of doing it silently.",
            "Accessibility is part of balance, not a separate feature. Damage, speed, timing, reticle-size settings and assist options widen the audience without breaking the curve for everyone else. The rule: give <b>tools</b>, do not silently change the rules.",
        ],
        formula=("difficulty(t) ≈ k · skill(t)^0.85,   flow zone: 0.7 ≤ demand/capability ≤ 1.1",
                 "An exponent below 1 means the game “yields” as skill grows — that is the feeling of mastery. Above 1 is a wall."),
        steps=[
            "Define the demand axis (damage, timings, enemy count, resources) and the capability axis.",
            "Plot the curve by chapter as a sawtooth: spike → plateau → spike.",
            "Find points where demand exceeds capability by more than 20 %.",
            "Add DDA only to tempo and only as hidden help, never to damage.",
            "Ship accessibility settings without changing the base curve for others.",
        ],
        complexity=("O(1) per level", "O(1)", "Collect death telemetry: a map of “where players die” is the best difficulty-balance tool there is."),
        code=("python", """def requirement(chapter, base=10, rate=1.18):
    return base * (rate ** chapter)

def capability(chapter, skill=0.16, gear=0.10):
    return 10 * ((1 + skill) * (1 + gear)) ** chapter

for ch in range(0, 12):
    req, cap = requirement(ch), capability(ch)
    flag = "  <-- wall" if req / cap > 1.2 else ""
    print(f"chapter {ch:2d}  req {req:7.1f}  cap {cap:7.1f}  ratio {req / cap:4.2f}{flag}")"""),
        pitfalls=[
            "DDA on damage: the player notices and stops believing in their own success.",
            "Difficulty grows faster than capability — a wall mid-game.",
            "Accessibility settings buried and never mentioned in the difficulty menu.",
            "No telemetry: “where it is hard” is decided from tester feelings.",
        ],
        games=["Dark Souls", "Celeste", "Left 4 Dead", "Hades"],
    ),
    dict(
        id="bal-boss",
        title="Boss tuning: phases, DPS checks and enrage",
        tags=["boss", "phases", "DPS check", "enrage"],
        summary="A boss fight is a contract: how much damage is required, how many mistakes are allowed and how long an attempt lasts. All three numbers are set in advance, not tuned after release.",
        detail=[
            "The fight budget has three quantities: <b>required DPS</b> (health / duration), <b>tolerable incoming damage</b> (tank health / duration) and <b>allowed mistakes</b> (how many mechanics can be failed before a wipe). The first two are numbers, the third is design. If the allowed mistakes are zero, the fight becomes choreography.",
            "A <b>DPS check</b> is useful when it tests the build and execution, and harmful when it depends only on gear. A 20 % damage gap between “geared” and “ungeared” is a fair check; a 3× gap is a progression gate. An enrage timer is a crude form of the same thing; escalating mechanics are better than a hard stop.",
            "Plan <b>phases</b> as a change of task rather than a change of number: from damage to positioning, from solo to coordination. And keep the attempt duration comfortable: 3–6 minutes for action, 8–12 for raids; longer and a wipe at the last seconds feels like wasted time.",
        ],
        formula=("DPS_required = HP_boss / T_attempt,   mistakes = (T · HPS_available − unavoidable damage) / damage_per_mistake",
                 "Compute for the average player of your audience, not the top 1 %. The top should win easily — that is the reward for mastery."),
        steps=[
            "Set the target fight duration and compute the required DPS for the reference build.",
            "Compute the incoming-damage budget for the tank and the tolerable number of mechanic failures.",
            "Split the fight into phases by task type (damage → position → coordination).",
            "Make enrage an escalation of mechanics, not instant death.",
            "Test the fight on both an under-geared and an over-geared player.",
        ],
        complexity=("O(1) per check", "O(1)", "Keep an attempt log: time, DPS, deaths per mechanic — that is the boss's balance."),
        code=("python", """def boss_budget(hp=2_000_000, target_time=300, tank_hp=180_000,
                unavoidable_dps=450, error_damage=25_000):
    dps = hp / target_time                          # the DPS check
    slack = tank_hp - unavoidable_dps * target_time  # health left for mistakes
    return dps, int(max(0, slack) // error_damage)

for gear in (0.85, 1.0, 1.2):                 # under-, reference, over-geared
    dps, errors = boss_budget(hp=2_000_000 * gear)
    print(f"gear x{gear:.2f}: required dps {dps:7.0f}, tolerable mistakes {errors}")"""),
        pitfalls=[
            "A DPS check that depends only on gear: the player “cannot pass” rather than “cannot play”.",
            "Enrage as instant death: a wipe at 99 % feels like a cheat.",
            "Fights longer than 10 minutes without intermediate checkpoints.",
            "Balancing around top players: the average player never sees the content.",
        ],
        games=["World of Warcraft", "Final Fantasy XIV", "Destiny 2", "Monster Hunter"],
    ),
    dict(
        id="bal-pvp",
        title="PvP balance: normalisation, rating and gear",
        tags=["PvP", "normalisation", "rating", "gear"],
        summary="In PvP, balance is not just character numbers but the distribution of player skill. Weapons and armour should define style, not the outcome by default.",
        detail=[
            "Three models: <b>full normalisation</b> (all stats equal, skill wins — as in template arenas), <b>scaling</b> (gear compressed into a narrow corridor, a 5–10 % difference), <b>full accounting</b> (gear decides). The first is fairer but loses RPG progression; the third is more interesting for an MMO but scares newcomers away in competitive modes.",
            "Balance by <b>rank</b>, not overall: a weapon with a 48 % win rate at low rank and 58 % at high rank is a design issue (a high skill ceiling), not an “imbalance”. Also look at pick rate: if an item appears in 90 % of builds, the problem is the lack of alternatives, not the win rate.",
            "And <b>perceived unfairness</b>: losing to “better gear” demotivates more than losing to skill. So even with full gear accounting it is worth limiting the power gap between players in the same match.",
        ],
        formula=("winrate(item) = wins / matches by rank,   pick_rate = appearances / builds",
                 "Target a 48–52 % win rate across all ranks. The anomaly is not 55 % but a difference of more than 5 pp between ranks."),
        steps=[
            "Choose the model: normalisation, scaling or full gear accounting.",
            "Collect statistics by rank: win rate, pick rate, match duration.",
            "Introduce seasonal limits (bans, item caps, stat templates).",
            "Limit the power gap between players in the same match.",
            "Look at the high ranks separately: skill ceilings show up there more than “imbalances”.",
        ],
        complexity=("O(#items × #ranks)", "O(#matches)", "Measure by rank and by build: an aggregate win rate hides both problems."),
        code=("python", """STATS = {   # item: {rank: (wins, matches)}
    "sword":  {"low": (520, 1000), "mid": (505, 1000), "high": (585, 1000)},
    "dagger": {"low": (480, 1000), "mid": (500, 1000), "high": (415, 1000)},
}

for item, ranks in STATS.items():
    rates = {r: w / m for r, (w, m) in ranks.items()}
    spread = max(rates.values()) - min(rates.values())
    print(f"{item:7s} " + "  ".join(f"{r} {v:.0%}" for r, v in rates.items())
          + f"   spread {spread:.0%}" + ("  <-- skill ceiling" if spread > 0.05 else ""))"""),
        pitfalls=[
            "Balancing on the overall win rate and hiding rank differences.",
            "Ignoring pick rate: “not overpowered” can still be “mandatory”.",
            "A gear gap of more than 20 % within one match reads as unfair.",
            "Normalisation that kills build identity makes the game flat.",
        ],
        games=["World of Warcraft", "Guild Wars 2", "League of Legends", "Counter-Strike 2"],
    ),
    dict(
        id="bal-sim",
        title="Balance simulation, Monte Carlo and A/B tests",
        tags=["Monte Carlo", "simulation", "A/B test", "telemetry"],
        summary="Balance cannot be proven by a formula — it can be measured. Simulation gives numbers before release, telemetry after, and an A/B test answers “did it get better” without relying on intuition.",
        detail=[
            "<b>Monte Carlo</b> answers questions like “what percentage of fights ends in three hits” and “how often is a miss streak longer than six”. The model is simple: agents, actions, distributions. The main thing is to look at tails and confidence intervals rather than means — 10 000 runs give about 1 pp of precision, enough for design decisions.",
            "<b>Telemetry</b> after release answers different questions: where people die, what items they take, where they quit. Look at cohorts (newcomers, veterans, ranks) and distributions, not aggregate averages. A single “average” 50 % win rate can hide two broken modes.",
            "An <b>A/B test</b> is the only way to verify that a change actually improved a metric. It needs random assignment, a sufficient sample, a pre-declared metric and a fixed duration. Common mistakes: checking results daily and stopping when it looks good, changing several variables at once, measuring retention with a single button.",
        ],
        formula=("SE = √(p(1−p)/n),   95 % CI ≈ p ± 1.96·SE,   n ≈ 16·p(1−p)/Δ²",
                 "For a 2 pp difference at p ≈ 0.5 you need roughly 10 000 observations per arm. Stopping earlier means measuring noise."),
        steps=[
            "State the balance question as a measurable quantity (TTK, win share, time to level).",
            "Build a Monte Carlo model with distributions rather than fixed numbers.",
            "Compute tails and confidence intervals; run a sensitivity check on the parameters.",
            "After release collect cohort telemetry and compare it with the model.",
            "Validate the change with an A/B test using a pre-declared metric and duration.",
        ],
        complexity=("O(n) per run", "O(1)", "10⁵ runs take seconds. 10⁵ runs of a full combat simulation take minutes; cache results and look at deltas."),
        code=("python", """import random, statistics

def duel(rng, a=(100, 12, 0.75), b=(110, 10, 0.70), limit=60):
    \"\"\"Simple stochastic duel: (hp, damage, hit chance).\"\"\"
    hp_a, dmg_a, hit_a = a
    hp_b, dmg_b, hit_b = b
    for turn in range(limit):
        if rng.random() < hit_a:
            hp_b -= dmg_a * rng.uniform(0.85, 1.15)
        if hp_b <= 0:
            return "a", turn
        if rng.random() < hit_b:
            hp_a -= dmg_b * rng.uniform(0.85, 1.15)
        if hp_a <= 0:
            return "b", turn
    return "draw", limit

rng = random.Random(11)
outcomes = [duel(rng) for _ in range(20_000)]
wins_a = sum(1 for w, _ in outcomes if w == "a") / len(outcomes)
turns = [t for w, t in outcomes if w == "a"]
se = (wins_a * (1 - wins_a) / len(outcomes)) ** 0.5
print(f"win A {wins_a:.1%} ± {1.96 * se:.1%}   median turns {statistics.median(turns):.0f}")"""),
        pitfalls=[
            "Counting means and ignoring tails — the tails cause the complaints.",
            "Stopping an A/B test at the first good-looking result.",
            "Changing several variables at once makes the effect unassignable.",
            "Telemetry without cohorts: averages hide a broken segment.",
        ],
        games=["Riot Games (LoL)", "Overwatch", "World of Warcraft", "Hearthstone"],
        demo="balance-sim",
    ),
]

BAL_DECISIONS_EN = [
    {"en": ("Damage feels off, everything dies instantly", "TTK/STK table, EHP, mitigation curve")},
    {"en": ("Late game is broken, builds explode", "survivability budget, multiplier cap, diminishing returns")},
    {"en": ("Players stall in the middle", "XP curve, time-to-level, difficulty curve")},
    {"en": ("Progression feels like a wall", "reward pacing, power plateaus, visible gates")},
    {"en": ("One stat is always best", "skill-tree EPP, stat pricing, soft caps")},
    {"en": ("The economy is running hot, prices exploded", "faucets and sinks, progressive sink, money-supply metrics")},
    {"en": ("Loot feels flat and forgettable", "tier weights, ilvl budget, pity and guarantees")},
    {"en": ("The gacha draws complaints", "median and p90 pulls, soft pity, transparent rates")},
    {"en": ("A new season invalidated old content", "seasonal power step, horizontal mechanics, stat squish")},
    {"en": ("Difficulty spikes and players leave", "difficulty sawtooth, tempo-only DDA, accessibility")},
    {"en": ("Bosses are impossible for average players", "fight budget, DPS check, escalation instead of enrage")},
    {"en": ("Gear decides PvP", "normalisation, power corridor, stats by rank")},
    {"en": ("No idea whether the patch helped", "Monte Carlo before release, cohort telemetry, A/B test")},
]
