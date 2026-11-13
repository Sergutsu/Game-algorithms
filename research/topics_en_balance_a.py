# -*- coding: utf-8 -*-
"""English content for Part IV topics 105–117: damage, defence and progression.

Only translatable text lives here; n, cat, bg, level and demo are inherited
from topics_balance_a.py by id.
"""

TOPICS_EN_BAL_A = [
    dict(
        id="dmg-mitigation",
        title="Armour and the damage mitigation curve",
        tags=["armour", "mitigation", "time-to-kill", "curve"],
        summary="Mitigation is a function, not a flat subtraction. Linear, multiplicative and logarithmic forms feel completely different in the early and late game, and the curve — not the armour number — decides where the game breaks.",
        detail=[
            "Three classic shapes. <b>Linear</b> (damage − armour) nullifies every weapon below a threshold and collapses the late game: once damage overtakes armour, defence disappears. <b>Multiplicative</b> (damage · 100/(100 + armour) — the Warcraft III and Dota scheme) approaches zero asymptotically and never grants immunity: read 100/(100+armour) as the <i>share of damage that gets through</i>, not as a subtraction. <b>Logarithmic</b> (damage · (1 − k·ln(1 + armour))) plateaus quickly and always needs a hand-written cap.",
            "The main metric is not the mitigation percentage but <b>effective health</b>: EHP = HP / (1 − mitigation). With the multiplicative scheme EHP grows linearly with armour: +100 armour always adds +100 % of base HP, which makes balancing easy because every point of armour keeps a constant value. With the logarithmic scheme each further point gives less, and players feel cheated when the numbers in the UI grow but survivability does not.",
            "In practice, keep mitigation in the 0–75 % band and add a <b>flat armour</b> layer only for weak hits (minions, damage over time). Always show the player the resulting percentage, not the raw armour number: the interface is part of the balance. And balance at the edges of the range — the weakest and the strongest build — not on the average one.",
        ],
        formula=("D = A · 100 / (100 + R)   ⇒   EHP = HP · (100 + R) / 100",
                 "A — incoming damage, R — armour, D — damage that lands. With this form every 100 armour adds exactly +100 % of base health, so the price in EHP is linear. Logarithmic variant: D = A · (1 − k·ln(1 + R/R₀))."),
        steps=[
            "Set a base TTK for an unarmoured character: that is the reference point.",
            "Pick the mitigation form and compute EHP at 5–6 control points of armour.",
            "Plot “armour → EHP” and “armour → mitigation %”: the second curve is what players see, the first is what you feel.",
            "Cap the maximum mitigation (usually 60–80 %) and add a separate armour-penetration layer.",
            "Recompute every weapon's damage through the target archetype's EHP rather than in absolute numbers.",
        ],
        complexity=("O(1) per hit", "O(1)", "The numbers matter, not the code: any of the three forms is one line, and all the work is in the balance sheet."),
        code=("python", """def mitigation(armour, model="multiplicative", k=0.06, cap=0.8):
    if model == "linear":                 # flat subtraction: breaks late game
        return min(armour, 1.0)
    if model == "multiplicative":         # WC3 / Dota style: never reaches 100%
        return armour / (100.0 + armour)
    if model == "logarithmic":            # fast plateau, needs a cap
        return min(cap, k * __import__("math").log(1 + armour / 10.0))
    raise ValueError(model)

def damage_after(attack, armour, hp, **kw):
    m = mitigation(armour, **kw)
    dealt = attack * (1 - m)
    return dealt, hp * (1 + armour / 100.0)      # (damage, effective HP)

# breakpoints every designer should print once:
for a in (0, 25, 50, 100, 200, 400):
    d, ehp = damage_after(100, a, 1000)
    print(f"armour {a:>3}: {d:6.1f} dmg, EHP {ehp:7.0f}")"""),
        pitfalls=[
            "Linear armour subtraction: one weapon becomes useless and another becomes omnipotent.",
            "Adding mitigation percentages together: two 40 % sources give 64 %, not 80 % — only the share that gets through multiplies.",
            "Showing raw armour without the resulting percentage — the most common “the numbers don't work” complaint.",
            "Forgetting damage over time and weak hits: under a percentage scheme they become pointless and need their own layer.",
        ],
        games=["Dota 2", "Warcraft III", "World of Tanks", "Diablo II"],
        demo="mitigation",
    ),
    dict(
        id="dmg-formula",
        title="The damage formula: additive and multiplicative layers",
        tags=["damage formula", "modifiers", "buckets", "stacking"],
        summary="Damage is assembled from layers: base, flat additions, percentage multipliers and final effects. The order and grouping of those layers decide whether one synergy explodes the build or everything stays predictable.",
        detail=[
            "The standard production scheme is <b>D = (base + flat) · Π(1 + bucketᵢ) · Π(1 + crit) · (1 − mitigation)</b>. The keyword is <i>bucket</i>: modifiers add up inside a group and multiply between groups. So “+10 % damage” from three sources gives +30 % in one bucket and +33.1 % in three different ones. That distinction is exactly what creates “unexpected” builds.",
            "If everything is additive, the late game degenerates into one best stat; if everything multiplies, explosions appear (ten sources of +20 % give ×6.2). A workable compromise: flat additions and the main stat are additive, rare “exclusive” bonuses are multiplicative, and the number of multiplicative sources is hard-capped.",
            "Order matters: crit lands after armour and after flat additions; elemental amplification applies before mitigation; “damage dealt” and “damage taken by the target” are different multipliers. Write the order down once and implement it in a single function. As soon as the formula is smeared over ten places, balance stops being reproducible.",
        ],
        formula=("D = (B + Σflat) · Π(1 + sᵢ) · Π(1 + mⱼ) · (1 − r) · crit",
                 "B — base weapon or skill damage, flat — flat additions, sᵢ — additive percentages within a bucket, mⱼ — exclusive multipliers (cap their count), r — target mitigation."),
        steps=[
            "List every damage source in one table: base, flat, bucket percentages, exclusive multipliers, crit.",
            "Write a single calculation function and forbid any other place where damage is modified.",
            "Build a spreadsheet “build calculator” with three reference builds per level: weak, average, broken.",
            "Cap the number of exclusive multipliers (usually 2–3) and check the upper bound at +50 % level.",
            "Log each layer's contribution during combat — those numbers are what patches are made from.",
        ],
        complexity=("O(k) in the number of modifiers", "O(k)", "Keep modifiers in an array and multiply in one pass: it simplifies both debugging and logging."),
        code=("python", """def damage(base, flat=(), additive=(), exclusive=(), crit=1.0, mitigation=0.0):
    \"\"\"One place for the whole formula: base → flat → buckets → exclusive → crit → armour.\"\"\"
    value = base + sum(flat)
    bucket = 1.0 + sum(additive)          # +10% and +15% in one bucket = +25%
    for s in exclusive:                   # rare, capped in count
        bucket *= (1.0 + s)
    value *= bucket
    value *= crit                          # after armour in most games
    return value * (1.0 - mitigation)

print(damage(100, flat=[12], additive=[0.10, 0.15], exclusive=[0.2], crit=2.0, mitigation=0.25))
# 112 · (1.25 · 1.2) · 2.0 · 0.75 = 252.0"""),
        pitfalls=[
            "Adding percentages from different systems together: “+20 % damage” and “+20 % attack” are not the same thing.",
            "Crit applied before flat additions gives a different curve — fix the order and never change it between patches.",
            "No upper bound on damage: the “everything into one multiplier” build breaks bosses and PvP.",
            "A formula smeared across the codebase turns a rebalance into weeks of work instead of an hour.",
        ],
        games=["Path of Exile", "Diablo IV", "Warframe", "Genshin Impact"],
    ),
    dict(
        id="dmg-ehp",
        title="Effective HP, TTK and shots-to-kill",
        tags=["EHP", "TTK", "STK", "breakpoints"],
        summary="Players do not feel percentages — they feel shots and seconds. STK (shots-to-kill) and TTK translate abstract stats into the feel of combat tempo, and they should be the unit of balance.",
        detail=[
            "<b>TTK</b> (time to kill) is the time from the first hit to death; <b>STK</b> is how many hits it takes. STK is discrete and therefore more important: the difference between 3 and 4 shots is huge, between 3.1 and 3.4 invisible. Balance by <i>thresholds</i>: a weapon must kill a specific target in a specific number of hits, and only then do you round the damage.",
            "The link to defence: TTK = EHP / DPS. If damage and health both grow linearly, TTK stays healthy while the growing numbers deliver the feeling of power. If health outgrows damage, the late game turns into sponges; if it lags behind, into one-shots. A useful trick: fix the TTK at levels 1, 10, 30 and 60, then bend the curves to hit those four points.",
            "In PvP, TTK is also a reaction budget: 0.15–0.3 s is a duel on reflexes (shooters), 1–3 s is tactics and positioning (MMOs, MOBAs), 5–15 s is a fight over resources (bosses, tanks). Changing TTK changes the genre more than any new mechanic.",
        ],
        formula=("TTK = EHP / DPS,   STK = ceil(EHP / (D · hit_rate))",
                 "EHP = HP / (1 − mitigation); DPS = damage · rate · hit share. Compute TTK at 3–4 campaign levels and at the edges of the build range, never on the average."),
        steps=[
            "Set the target TTK for your genre and for the weak / average / strong player rotation.",
            "Fold health and defence into a single EHP number per class and level.",
            "Compute STK for every weapon against every class — that is a matrix, not a list.",
            "Check the thresholds: “one extra shot” must never be a random side effect of fractions.",
            "Recompute after every damage change: the TTK table should refresh automatically.",
        ],
        complexity=("O(#weapons × #targets)", "O(1)", "An STK matrix for 8 weapons and 5 classes takes a minute in a spreadsheet and catches 90 % of balance errors."),
        code=("python", """import math

def ehp(hp, mitigation=0.0, shield=0.0):
    return (hp + shield) / (1.0 - mitigation)

def ttk(target_hp, mitigation, dps, hit_rate=1.0):
    return ehp(target_hp, mitigation) / (dps * hit_rate)

def stk(target_hp, mitigation, damage, hit_rate=1.0):
    return math.ceil(ehp(target_hp, mitigation) / (damage * hit_rate))

for hp, mit in ((100, 0.0), (100, 0.3), (250, 0.45)):      # three archetypes
    print(f"hp {hp} mit {mit:.0%}: ttk {ttk(hp, mit, 80):.2f}s, "
          f"stk {stk(hp, mit, 34)}")"""),
        pitfalls=[
            "Balancing percentages without checking STK — then “+5 % damage” silently changes the shot count.",
            "The same TTK everywhere: PvP and raid content must differ by a factor, not by a few percent.",
            "Ignoring hit rate: for a weapon with spread, hit rate matters more than raw damage.",
            "Health growing faster than damage in the late game — the classic “sponge”.",
        ],
        games=["Counter-Strike 2", "Apex Legends", "World of Warcraft", "Destiny 2"],
    ),
    dict(
        id="dmg-variance",
        title="Damage variance, hit chance and dispersion",
        tags=["variance", "RNG", "hit chance", "expected value"],
        summary="Randomness makes combat alive, and the same randomness makes balance unfair. Damage spread, hit chance and miss streaks are about managing variance, not about “a bit of random”.",
        detail=[
            "A damage spread (say 80–120 %) preserves the mean and adds drama, but it multiplies the number of “unfair” outcomes. Count not the mean but <b>the probability of killing in N hits</b>: with a wide spread and low HP it can differ several-fold for the same build. A narrow spread (±5 %) gives predictability, a wide one (±30 %) gives excitement; competitive modes usually remove it.",
            "Hit chance is a separate axis. The classic “roll to hit, then roll damage” scheme (D&D, XCOM) creates misses the player remembers for a long time, which is why modern games replace a miss with dispersion (spray, cone) — the player sees the cause. If a chance stays, show it and keep it in the 60–95 % band: 50 % feels like a coin flip and destroys tactics.",
            "Streak variance: even an honest 30 % chance produces runs of 8 misses with noticeable frequency. For comfort, use pity / PRD, a free first hit, guaranteed crits after a run of misses, or deterministic damage. The rule: <i>randomness belongs in outcomes, not in the ability to play</i>.",
        ],
        formula=("E[D] = p · d̄,   Var[D] = p·(1−p)·d̄² + p·σ²d,   P(streak of k misses) = (1−p)ᵏ",
                 "p — hit chance, d̄ — average damage, σ²d — damage variance. At p = 0.7 nine misses in a row happen in 0.002 % of attacks — which still happens daily across 10 000 players."),
        steps=[
            "Decide what exactly is random: hit, damage, crit or AI behaviour — and do not mix everything at once.",
            "Set target means and acceptable spread; compute P(kill in N) at the edges of the build range.",
            "Remove randomness from threshold mechanics: if 4 hits must kill, they must kill.",
            "Add streak protection (PRD, guarantee after k misses) if fairness complaints appear.",
            "Log outcome distributions in playtests, not just averages.",
        ],
        complexity=("O(1) per roll", "O(1)", "A Monte Carlo run of 10⁵ fights takes a second and reveals tails invisible in the mean."),
        code=("python", """import random

def roll_damage(rng, base=100, spread=0.2, crit_p=0.25, crit_mult=2.0):
    d = base * rng.uniform(1 - spread, 1 + spread)
    return d * (crit_mult if rng.random() < crit_p else 1.0)

def p_kill_within(rng, hits, hp, **kw):
    return sum(1 for _ in range(100_000)
               if sum(roll_damage(rng, **kw) for _ in range(hits)) >= hp) / 100_000

rng = random.Random(7)
print("P(kill in 3) =", p_kill_within(rng, 3, 300))   # the tail matters, not the mean"""),
        pitfalls=[
            "Checking only average damage: the tails of the distribution are the feeling of unfairness.",
            "Randomness punishing skill (a miss on perfect play) — the main source of frustration.",
            "Damage variance applied before armour and crit gives unexpectedly wide tails.",
            "No pity in rare-trigger mechanics: streaks read as a bug.",
        ],
        games=["XCOM 2", "Dota 2", "Fire Emblem", "Battle Brothers"],
    ),
    dict(
        id="dmg-dot",
        title="Damage over time: stacks, refresh and ticks",
        tags=["DoT", "stacking", "tick rate", "uptime"],
        summary="Damage over time is not “damage stretched across seconds” but a separate economy: how many effects are active at once, how they refresh and what happens when the same effect is applied twice.",
        detail=[
            "Four stacking policies: <b>refresh</b> (resets the duration, damage does not add), <b>stack</b> (independent instances), <b>extend</b> (adds time to the remaining duration) and <b>replace</b> (overwrites with the strongest). The choice affects both DPS and server load: 40 independent stacks on 20 targets is 800 timers per tick.",
            "Ticks are discrete, so real DPS depends on phase: a 10 s effect ticking every 2 s gives 5 ticks, but one applied mid-window gives 5 one time and 4 the next. Round durations to a multiple of the tick or accrue continuously. For interruptible DoTs, account for uptime — the fraction of time the effect is actually active, not its theoretical DPS.",
            "For the player a DoT is a promise of future damage, so it must be visible and predictable: a timer, ticking numbers, a sound. Otherwise it feels like “damage out of nowhere” and in PvP reads as cheating. Decide separately whether DoTs from different sources stack and whether the effect ends when its caster dies.",
        ],
        formula=("DPS_DoT = Σᵢ (dᵢ · ticksᵢ / durationᵢ) · uptime,   ticks = floor(duration / tick)",
                 "dᵢ — damage of one tick of effect i. With n identical stacks DPS grows linearly, but the simulation load does too: cap the maximum stacks and the length of the effect list."),
        steps=[
            "Choose a stacking policy per effect type and write it into the design document.",
            "Tie ticks to the shared game tick instead of a timer per effect.",
            "Compute real tick counts for typical durations: 6 s at a 1 s tick — 5 or 6 ticks?",
            "Cap the maximum stacks and total DoT per target, or an “all DoT” rotation breaks bosses.",
            "Show the timer and the DoT contribution in the combat log: the player must see where the damage comes from.",
        ],
        complexity=("O(#effects) per tick", "O(#effects per target)", "Thousands of targets with a dozen effects need a flat array and a single pass, not a list of objects with callbacks."),
        code=("python", """class Dot:
    def __init__(self, dmg, duration, tick=1.0, policy="refresh", max_stacks=3):
        self.dmg, self.duration, self.tick = dmg, duration, tick
        self.policy, self.max_stacks = policy, max_stacks
        self.stacks, self.left, self.acc = 0, 0.0, 0.0

    def apply(self):
        if self.policy == "stack":
            self.stacks = min(self.max_stacks, self.stacks + 1)
        elif self.policy == "refresh":
            self.stacks = 1
        elif self.policy == "extend":
            self.left += self.duration
        self.left = max(self.left, self.duration) if self.policy != "extend" else self.left
        self.stacks = max(self.stacks, 1)

    def advance(self, dt):
        if self.left <= 0:
            return 0.0
        self.left -= dt
        self.acc += dt
        dealt = 0.0
        while self.acc >= self.tick:
            self.acc -= self.tick
            dealt += self.dmg * self.stacks        # one tick per stack
        return dealt"""),
        pitfalls=[
            "A timer per effect instead of a shared tick: the server drowns on mass AoE.",
            "Rounding durations up without accounting for the tick: one extra tick is 20 % more DPS.",
            "Invisible DoT in PvP — the player dies “by themselves” and calls it a bug.",
            "Unlimited stacking: one rotation out-damages the entire arsenal.",
        ],
        games=["World of Warcraft", "Path of Exile", "Guild Wars 2", "Elden Ring (Scarlet Rot)"],
    ),
    dict(
        id="def-shield",
        title="Shields, absorption and regeneration",
        tags=["shield", "absorb", "regen", "effective HP"],
        summary="A shield is a buffer that changes not only survivability but tempo: it lets you wait out damage, devalues small hits and breaks the balance when its regeneration is free.",
        detail=[
            "A shield as a <b>separate pool</b> (Halo, Destiny) regenerates after a pause and turns combat into a rhythm of “hide, recover”. A shield as <b>instant absorption</b> (WoW, LoL) is an active resource with a cooldown, valued for timing. A shield as <b>percentage reduction</b> is already armour, and mixing the three is a bad idea: the player cannot tell what actually saved them.",
            "Regeneration is the main source of endless fights. If a shield recovers faster than the opponent deals damage, the fight never ends. Make <b>regeneration slower than the opponent's DPS in an average fight</b> and add reset conditions: damage interrupts regen, out of combat it speeds up.",
            "Also design the order: shield before or after armour? Usually a shield absorbs already-mitigated damage, otherwise it becomes super-valuable on tanks. And mind the UI: two bars are harder to read than one, so sometimes showing the total is better.",
        ],
        formula=("EHP = (HP + Σshield) / (1 − mitigation),   growth = d(shield)/dt − incoming DPS",
                 "While regen < incoming DPS the shield is a one-off buffer; once regen exceeds DPS the fight becomes unwinnable-by-either-side. That single line is all the check you need."),
        steps=[
            "Decide whether the shield is a pool, a cooldown absorption or a percentage: do not mix.",
            "Set the delay and regeneration rate and compare them with typical enemy DPS.",
            "Fix the order: mitigation → shield or shield → mitigation.",
            "Add a counter-mechanic: shield damage, penetration, a “break” effect when overloaded.",
            "Test the mirror match: two identical builds must not end in a draw.",
        ],
        complexity=("O(1) per hit", "O(1) per unit", "Networked shields must replicate separately from HP: the player has to see the shield actually absorb."),
        code=("python", """class Health:
    def __init__(self, hp, shield=0.0, regen=0.0, delay=4.0, mitigation=0.0):
        self.hp, self.max_hp = hp, hp
        self.shield, self.max_shield = shield, shield
        self.regen, self.delay, self.idle = regen, delay, 0.0
        self.mitigation = mitigation

    def take(self, dmg):
        dmg *= (1.0 - self.mitigation)
        absorbed = min(self.shield, dmg)
        self.shield -= absorbed
        self.hp -= (dmg - absorbed)
        self.idle = 0.0                       # damage interrupts regeneration
        return absorbed, dmg - absorbed

    def tick(self, dt):
        self.idle += dt
        if self.idle >= self.delay:           # regen faster than incoming DPS = stalemate
            self.shield = min(self.max_shield, self.shield + self.regen * dt)"""),
        pitfalls=[
            "Shield regeneration without a delay: the player simply waits and wins.",
            "A shield computed before armour — a hidden survivability multiplier for tanks.",
            "Two bars in the UI with no explanation: players confuse shield and health.",
            "A shield that no counter-mechanic can break devalues all other damage.",
        ],
        games=["Halo", "Destiny 2", "League of Legends", "Warframe"],
    ),
    dict(
        id="def-crowd",
        title="Crowd control and diminishing returns",
        tags=["CC", "diminishing returns", "immunity", "PvP"],
        summary="Stun, slow and fear are the strongest effects in a game because they take away not health but the ability to play. So they are balanced by duration, categories and diminishing returns rather than by damage.",
        detail=[
            "The basic PvP rule: <b>a second CC of the same type is shorter, a third shorter still, a fourth is immunity</b>. Multipliers like 1 / 0.5 / 0.25 / 0 give a predictable curve and prevent perma-stunning. Group effects by category (hard control, fear, slow, silence), because the player perceives “stun + root” as one long stun.",
            "CC duration is a budget, not a number: 8 seconds of stun is death in a MOBA and an ordinary mechanic in an MMO. Measure <b>the share of time the target cannot act</b> (CC uptime): above 30–40 % the fight stops being a game. Compute the worst case separately — a chain of three players with control.",
            "PvE usually needs the opposite: bosses must resist control or the mechanic becomes “hold and hit”. The answer is immunity to hard control, vulnerability to positional effects (slow, knockback), and phases where control is allowed.",
        ],
        formula=("T_eff = T_base · DR(n),   DR = [1, 0.5, 0.25, 0, ...],   CC_uptime = ΣT_eff / T_fight",
                 "n — index of a CC of the same type on that target within a window (usually 15–20 s). Keep PvP CC uptime below 35 % even in the worst case."),
        steps=[
            "Sort every effect into categories and decide which count as “the same”.",
            "Set the DR reset window (usually 15–20 s) and the multiplier table.",
            "Cap hard-control duration in PvP and add a “trinket” / reduction.",
            "For PvE make bosses immune to hard control but vulnerable to positional effects.",
            "Test the “three players in a row” chain — that is the worst case, not the average.",
        ],
        complexity=("O(1) per effect", "O(#categories) per target", "Keep DR counters on the server: client-side computation is the first thing people exploit."),
        code=("python", """DR_TABLE = (1.0, 0.5, 0.25, 0.0)      # 1st, 2nd, 3rd, 4th CC of the same kind

class CcTracker:
    def __init__(self, window=18.0):
        self.window = window
        self.last = {}                  # category -> (time, count)

    def duration(self, category, base, now):
        t, n = self.last.get(category, (-1e9, 0))
        if now - t > self.window:
            n = 0
        n = min(n + 1, len(DR_TABLE))
        self.last[category] = (now, n)
        return base * DR_TABLE[n - 1]

cc = CcTracker()
for i in range(4):
    print("stun", i + 1, "->", cc.duration("stun", 4.0, now=i * 5.0), "s")"""),
        pitfalls=[
            "Different categories counted separately while the player experiences them as one long stun.",
            "No DR reset over time: the target stays controlled for the whole fight.",
            "DR computed on the client: desync and an exploit in one bottle.",
            "Hard control in PvE without immunities: the boss becomes a training dummy.",
        ],
        games=["World of Warcraft", "League of Legends", "Dota 2", "Lost Ark"],
    ),
    dict(
        id="def-budget",
        title="Survivability budget: stacking mitigation and caps",
        tags=["stacking", "diminishing returns", "caps", "budget"],
        summary="Defensive bonuses from different sources combine in different ways, and that is exactly what decides whether a tank becomes immortal. A survivability budget is the engineering way to keep total damage reduction in a corridor.",
        detail=[
            "If two 40 % reductions multiply as shares of damage that gets through, the total is 64 %; if they add, 70–80 %. The first is safer, but it also breaks with a dozen sources: 10 × 10 % = 65 %, 20 × 5 % = 64 %. The rule: <b>always multiply the shares that get through</b> and show the player the total, not the individual bonuses.",
            "A hard cap (for example “no more than 70 % total reduction”) is crude but honest. A soft cap (beyond 50 % every further percent costs twice as much) preserves progress but needs explaining. A third route is <b>diminishing returns on the stat</b>: R_eff = R · k/(k + R), where each point of armour is still useful but never infinitely so.",
            "Do not forget indirect survivability: dodge, parry, block, healing, absorption are all multipliers too. Fold them into a single figure — “average incoming damage over 10 seconds of combat” — and balance that, not the individual stats.",
        ],
        formula=("D = A · Π(1 − mᵢ),   R_eff = R · k / (k + R),   survivability = EHP · Σ(1/(1 − mᵢ))",
                 "mᵢ — independent reduction sources. Multiplying the shares that get through is the only scheme that never yields negative damage or immortality."),
        steps=[
            "List every defensive source and convert it to “share of damage that gets through”.",
            "Multiply those shares for the worst-case build and check the total stays above 0.25.",
            "Introduce a hard or soft cap and make sure the player can see it in the UI.",
            "Add a counter layer: penetration, elemental damage, “true” damage.",
            "Recompute the budget after every new item or talent — that is where it breaks most often.",
        ],
        complexity=("O(#sources)", "O(#sources)", "The worst build matters more than the average one: it is what players find on day one."),
        code=("python", """from functools import reduce

def incoming(attack, mitigations):
    through = reduce(lambda acc, m: acc * (1.0 - m), mitigations, 1.0)
    return attack * through, through

def soft_cap(value, k=50.0):
    \"\"\"Diminishing returns that never reach a hard ceiling.\"\"\"
    return value * k / (k + value)

builds = {
    "glass cannon": [0.00],
    "bruiser":      [0.20, 0.15],
    "tank":         [0.40, 0.25, 0.10],
    "stacked tank": [0.40, 0.25, 0.10, 0.10, 0.10, 0.05],
}
for name, m in builds.items():
    dmg, through = incoming(1000, m)
    print(f"{name:13s} through {through:5.0%}  ->  {dmg:6.0f} dmg")"""),
        pitfalls=[
            "Adding reduction percentages until damage goes negative or immunity appears.",
            "A cap the player cannot see: they buy an item that does nothing.",
            "Forgetting dodge and healing — they belong to the same budget.",
            "Balancing the average build when only the maximum one breaks.",
        ],
        games=["Diablo III", "Path of Exile", "World of Warcraft", "Warframe"],
    ),
    dict(
        id="prog-xpcurve",
        title="The XP curve and the cost of a level",
        tags=["XP", "curve", "level cap", "exponent"],
        summary="Experience is the currency of time. The curve sets how many minutes a player pays for the next level, and it alone decides whether progression feels like growth or like a wall.",
        detail=[
            "Three base shapes. <b>Linear</b> (XP = k·n) gives an even tempo but levels stop feeling meaningful. <b>Quadratic</b> (XP = k·n²) is the RPG classic: total XP to level N grows as N³, so every next level costs longer, but not explosively. <b>Exponential</b> (XP = k·rⁿ, r ≈ 1.1–1.5) suits games with endless growth and a soft cap: every level multiplies the time, and sooner or later the player hits a natural ceiling.",
            "Count not experience but <b>time</b>: XP curve · XP earn rate = minutes per level. If the earn rate grows together with the curve, the player never notices the ramp; if it does not, a wall appears around level 20. A good rule: time per level grows by 3–8 % per level up to the cap and no more.",
            "Design the soft cap separately: after the maximum level XP turns into mastery points or currency. That keeps play meaningful without devaluing content. And mind <i>perception</i>: the bar must move even when the level is far away, otherwise the player feels stuck.",
        ],
        formula=("XP(n) = a · n^b,   Total(N) = Σ XP(n) ≈ a·N^(b+1)/(b+1),   T(n) = XP(n) / rate(n)",
                 "b = 1 is linear, b = 2 quadratic (the classic), b > 2 a hard wall. Compare T(n) at levels 1, 10, 30 and 60: the ratio should not differ by more than 3–5×."),
        steps=[
            "Set the target time to the maximum level (say 40–60 hours for an RPG).",
            "Pick the exponent b and fit a so the total matches the target time.",
            "Compute time per level including the growth of XP income; plot T(n).",
            "Add a soft cap: after the maximum — mastery points, not emptiness.",
            "Check the curve on a “slow” player: they must not stall in the middle.",
        ],
        complexity=("O(1) per level", "O(1)", "Recomputing the whole table is one loop; keep it in data, not in code."),
        code=("python", """def xp_to_next(level, a=100, b=2.0):
    return int(a * (level ** b))

def total_xp(level, a=100, b=2.0):
    return sum(xp_to_next(n, a, b) for n in range(1, level))

def time_per_level(level, xp_per_min, a=100, b=2.0):
    return xp_to_next(level, a, b) / xp_per_min

# b = 1.8 keeps the curve steep but not a wall; b = 2.5 is a classic wall
for level in (1, 10, 30, 60):
    print(f"L{level:02d}: {xp_to_next(level):>9,} xp  "
          f"({time_per_level(level, 900):5.1f} min at 900 xp/min)")"""),
        pitfalls=[
            "An exponential without a cap: at level 50 the player sees a level once a week.",
            "The curve ignores the growth of XP income, so the real tempo drifts.",
            "A maximum level with no “after”: the player loses the goal and leaves.",
            "Fixed quest XP with rising level costs makes old quests worthless.",
        ],
        games=["World of Warcraft", "Diablo II", "RuneScape", "Persona 5"],
        demo="xpcurve",
    ),
    dict(
        id="prog-growth",
        title="Stat growth: linear, geometric and soft caps",
        tags=["stat growth", "power curve", "scaling", "caps"],
        summary="How strength, health and damage grow with level is a question about shape, not numbers. The shape decides whether +10 levels feels like +10 levels and whether high-level content breaks.",
        detail=[
            "Linear growth (strength = 10 + 2·level) is predictable and convenient for PvP: the gap between levels is constant. Geometric growth (strength = 10 · 1.08^level) delivers a feeling of power but requires content to grow the same way — otherwise old enemies become dust and new ones a wall. The hybrid: linear growth for the main stat, weaker geometric growth for secondary ones.",
            "Soft caps on a stat (diminishing returns) let the player keep investing with decreasing returns. R_eff = R·k/(k+R) is nice because it never produces “extra” points yet never nullifies investment either. Hard caps are easier to explain but create dead points in a build.",
            "The key check is <b>content scaling</b>: should a player ten levels above an enemy win automatically? In PvE often yes (feeling of growth), in PvP no (that is not a contest). Choose the mode consciously and encode it in one coefficient, not in ten places.",
        ],
        formula=("S(n) = S₀ + g·n   |   S(n) = S₀ · rⁿ   |   S_eff = S · k/(k + S)",
                 "r = 1.05–1.10 is gentle geometric growth; r > 1.2 demands the same growth in content and almost always leads to number inflation."),
        steps=[
            "Decide what grows with level: main stat, health, damage, or all of them.",
            "Pick a shape for each axis and check the “player / enemy” ratio at 5 levels.",
            "Add soft caps on the most explosive stats (crit, speed, damage reduction).",
            "Build a “build power” table at levels 1/10/30/60 — it must grow smoothly.",
            "Check whether growth invalidates old content; sometimes a downscale is the answer.",
        ],
        complexity=("O(1) per level", "O(1)", "The growth table is data. Once it is hard-coded, every patch becomes a refactor."),
        code=("python", """def linear(level, base=10, per_level=2.0):
    return base + per_level * level

def geometric(level, base=10, rate=1.08):
    return base * (rate ** level)

def soft_cap(stat, k=100.0):
    return stat * k / (k + stat)

for level in (1, 10, 30, 60):
    raw = geometric(level)
    print(f"L{level:02d}  linear {linear(level):7.1f}  "
          f"geometric {raw:8.1f}  capped {soft_cap(raw):7.1f}")"""),
        pitfalls=[
            "Geometric stat growth with linear enemy growth: by level 30 the content no longer exists.",
            "A cap the player does not know about: points “disappear” and read as a bug.",
            "All stats growing at once gives a quadratic power spike — a frequent cause of a broken late game.",
            "No downscale in PvP: level decides the outcome instead of skill.",
        ],
        games=["Diablo IV", "Path of Exile", "Elden Ring", "World of Warcraft"],
    ),
    dict(
        id="prog-softcap",
        title="Soft caps and diminishing returns",
        tags=["soft cap", "diminishing returns", "curve", "stats"],
        summary="A soft cap is a way to let the player keep investing without breaking the balance. It turns “useless” points after the cap into slow but still noticeable growth.",
        detail=[
            "R_eff = R·k/(k+R) gives a smooth curve: at R = k the effectiveness is half, at R = 3k it is three quarters. The alternative is a piecewise-linear cap: 1:1 up to the threshold, then 0.5:1, then 0.25:1. It is simpler for the UI and clearer for the player: “beyond 40 % speed every further percent costs twice as much”.",
            "The cap must be <b>visible</b>. Designers often forget that the feeling of cheating comes not from diminishing returns but from hiding them. Show “+0.4 % (soft cap)” in the tooltip and let the player decide whether to keep investing.",
            "Soft caps are also a tool for balance between builds: they prevent one stat from becoming the dominant strategy. But do not use them as a patch: if one stat is always best, the problem is its price, not the absence of a cap.",
        ],
        formula=("S_eff = S · k / (k + S)   |   S_eff = S                    (S ≤ C)\n"
                 "S_eff = C + (S − C) · 0.5      (C < S ≤ 2C)   |   …",
                 "k — the half-effectiveness point, C — the cap threshold. The smooth version reads better in formulas, the piecewise one in the UI."),
        steps=[
            "Find the stats that explode under linear investment (crit, speed, damage reduction).",
            "Choose a smooth or piecewise cap and set the half-effectiveness point.",
            "Show the cap in the UI: the value, the threshold and “x % after the cap”.",
            "Verify that an “all into one stat” build does not beat any balanced build.",
            "Recompute the curve after any change to the damage or armour cap.",
        ],
        complexity=("O(1) per value", "O(1)", "Piecewise caps are cheaper to explain and easier in the UI; smooth ones are better for simulations."),
        code=("python", """def soft_cap(value, k=100.0):
    return value * k / (k + value)

def piecewise(value, c=50.0, rates=(1.0, 0.5, 0.25)):
    total, prev = 0.0, 0.0
    for rate in rates:
        span = min(value, c) - prev
        if span <= 0:
            break
        total += span * rate
        prev = min(value, c)
        c *= 2
    return total

for v in (25, 50, 100, 200, 400):
    print(f"{v:4} -> smooth {soft_cap(v):6.1f}  piecewise {piecewise(v):6.1f}")"""),
        pitfalls=[
            "A cap with no display: the player thinks the item does not work.",
            "Capping everything: builds stop differing and the game loses depth.",
            "Too hard a cap creates a dead zone, too soft a cap solves nothing.",
            "A soft cap used as a patch instead of repricing the stat.",
        ],
        games=["World of Warcraft", "Diablo IV", "Final Fantasy XIV", "Guild Wars 2"],
    ),
    dict(
        id="prog-points",
        title="Point budgets: skill trees and the price of choice",
        tags=["skill tree", "budget", "opportunity cost", "build"],
        summary="A skill tree is a budget, not a list of upgrades. The value of a choice comes from what the player gives up, so you balance the cost of the path rather than the power of the nodes.",
        detail=[
            "Every level grants points; every node costs points and requires prerequisites. Full build power is the sum of nodes, while the <b>budget</b> is the points available across the campaign. If the sum of all nodes is 3× the budget, the player must choose; at 1.2× there is barely a choice. The target ratio is usually 2:1–4:1.",
            "Path cost is a hidden currency. A “+10 % damage” node for 3 points that requires 2 useless nodes really costs 5. Compute <b>efficiency per point</b> (EPP) and plot it: abnormally high-EPP nodes always become mandatory, low-EPP ones are never taken.",
            "The tree and the items must compete: if the tree grants the same percentages as gear, one of the two is redundant. A good practice is for the tree to provide <i>qualitative</i> changes (new options, mechanics) and for gear to provide <i>quantitative</i> ones.",
        ],
        formula=("Budget = points per campaign,   Σnodes ≈ 2…4 × Budget,   EPP = node effect / (cost + path cost)",
                 "EPP is efficiency per point. If one node's EPP is 3× the median, it is mandatory and must be reworked or moved in the tree."),
        steps=[
            "Set the point budget for all content (levels plus bonuses) and the target number of full builds.",
            "Describe nodes with effect and cost, compute EPP and plot it.",
            "Add prerequisites and cap the number of “mandatory” nodes (usually 1–2 per tree).",
            "Test three canonical builds: narrow, wide and hybrid — all must be playable.",
            "Leave a respec path: one mistake must not cost the player 20 hours.",
        ],
        complexity=("O(#nodes) per build", "O(#nodes)", "The tree is a graph. Validate it automatically: unreachable nodes and cycles are caught in seconds."),
        code=("python", """BUDGET = 60          # points earned across the campaign
NODES = {
    "power.1": dict(cost=1, requires=[], effect=0.05),
    "power.2": dict(cost=2, requires=["power.1"], effect=0.08),
    "power.3": dict(cost=3, requires=["power.2"], effect=0.15),
    "utility.1": dict(cost=1, requires=[], effect=0.03),
}

def path_cost(node, nodes):
    cost, seen = 0, set()
    stack = [node]
    while stack:                          # prerequisites are paid for too
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        cost += nodes[n]["cost"]
        stack.extend(nodes[n]["requires"])
    return cost

for name, node in NODES.items():
    epp = node["effect"] / path_cost(name, NODES)
    print(f"{name:10s} cost {path_cost(name, NODES)}  EPP {epp:.3f}")"""),
        pitfalls=[
            "The sum of nodes equals the budget: there is no choice, only one build.",
            "Hidden path cost ignored — part of the tree ends up dead.",
            "“Tax” nodes (+1 %) taken only to unlock the next one: they annoy instead of delighting.",
            "No respec: one mistake at hour 15 kills the motivation.",
        ],
        games=["Path of Exile", "Diablo II", "Borderlands", "Last Epoch"],
    ),
    dict(
        id="prog-pacing",
        title="Progression pacing: gates, time-to-level and the power curve",
        tags=["pacing", "gates", "retention", "power curve"],
        summary="Progression is a schedule. When the player gets a new ability, how many hours until the next one and how long they get to try it — all of that is planned like a timeline, not as a side effect of numbers.",
        detail=[
            "Measure <b>time between “candies”</b>: a new mechanic, a new item tier, a new region. The first hour should deliver 2–3 noticeable upgrades, then the interval grows. If more than 45–60 minutes pass between upgrades, the player gets bored; under 5 minutes and they never get to use them.",
            "Gates (level, resource, boss) are not only restrictions but promises. A gate the player can see in advance (“requires level 15”) motivates; a hidden gate feels arbitrary. Show the condition and the progress towards it.",
            "The power curve needs “plateaus”: a sharp jump at a new tier, then a flat stretch where the player learns the new game. Constant linear growth without plateaus is exhausting, and too frequent jumps devalue the previous rewards.",
        ],
        formula=("interval(n) = T₀ · gⁿ,   T₀ ≈ 8–12 min, g ≈ 1.15–1.35 up to the cap;   gate = max(level, resource, boss)",
                 "The interval curve sets the rhythm: by hour 10 an upgrade should arrive every 30–45 minutes, not every 5 minutes and not every 3 hours."),
        steps=[
            "Build a timeline of the first 10 hours: what the player receives and when.",
            "Mark the gates and check that each is visible in advance.",
            "Plot the power curve (DPS/EHP/utility) by hour and look for dips and spikes.",
            "Add plateaus after large upgrades — time to master the new toy.",
            "Compare the timeline with a real playtest: players almost always go faster than planned.",
        ],
        complexity=("O(1) per point", "O(1)", "The timeline is a table. Without it, balance is argued from feelings instead of numbers."),
        code=("python", """T0, G = 8.0, 1.25          # minutes to first upgrade and growth per upgrade

def upgrade_times(hours=10, t0=T0, g=G):
    t, out = t0, []
    while t <= hours * 60:
        out.append(t)
        t *= g
    return out

times = upgrade_times()
for i, m in enumerate(times, 1):
    gap = m - (times[i - 2] if i > 1 else 0.0)
    print(f"upgrade {i:2d} at {m / 60:5.2f} h  (gap {gap:5.0f} min)")"""),
        pitfalls=[
            "No noticeable upgrades in the first 60 minutes — the most common cause of churn.",
            "Hidden gates (“needs 5000 gold”) with no progress indicator.",
            "Linear growth without plateaus: the player never feels the new power.",
            "Upgrades every 2 minutes: the player cannot use them and stops valuing them.",
        ],
        games=["Hades", "Vampire Survivors", "World of Warcraft", "Slay the Spire"],
    ),
]
