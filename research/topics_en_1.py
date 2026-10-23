# -*- coding: utf-8 -*-
"""English content for topics 1–13: mechanics, AI, graphics.

Only the translatable text lives here. Structural fields (n, cat, level, demo)
are inherited from the Russian topics_*.py by id, so the two languages can
never drift apart structurally.
"""

TOPICS_EN_1 = [
    dict(
        id="ballistics",
        title="Projectile ballistics with quadratic drag",
        tags=["differential equations", "Runge–Kutta", "CCD"],
        summary="A projectile lives by Newton's second law: gravity pulls it down, the air slows and pushes it sideways. For quadratic drag there is no analytic solution — the trajectory is integrated numerically, most often with RK4.",
        detail=[
            "Drag grows with the square of speed: <b>F<sub>d</sub> = ½ρC<sub>d</sub>A|v|v</b>. At low speeds the linear term matters, but for bullets, shells and balls the quadratic term dominates. Wind enters through the relative velocity <b>v − w</b>: the air pushes the projectile along its own motion instead of merely slowing it down.",
            "Explicit Euler (“position += velocity · dt”) accumulates error and visibly breaks apart at high speeds. RK4 evaluates the derivative four times per step and gives a local error of <b>O(dt⁵)</b> at the price of four evaluations — the best compromise for gameplay. For higher accuracy use adaptive stepping (RK45) or Verlet-like schemes.",
            "Aiming is the inverse problem: find the angle or the fuse time. Solve it by simulating forward with a bisection on the angle, by range tables, or with an iterative ballistic solver. Above roughly 300 m/s a continuous collision test (swept sphere / raycast) is mandatory, otherwise the projectile tunnels through walls between frames.",
        ],
        formula=("m·dv/dt = m·g − ½·ρ·C<sub>d</sub>·A·|v − w|·(v − w)",
                 "ρ — air density, C<sub>d</sub> — drag coefficient, A — cross-section area, w — wind velocity. Acceleration: a = g − (k/m)·|v−w|·(v−w), where k = ½ρC<sub>d</sub>A."),
        steps=[
            "Set the initial position, velocity, mass, C<sub>d</sub>, area and wind vector.",
            "Each sub-step, evaluate the four slopes k₁…k₄ of the coupled (p, v) system.",
            "Update velocity and position with the weighted sum: y += dt/6 · (k₁ + 2k₂ + 2k₃ + k₄).",
            "Test the segment p → p′ against colliders (continuous collision detection).",
            "For trajectory prediction, run the same function in a shadow simulation with no effects and no audio.",
        ],
        complexity=("O(1) per step, 4 acceleration evaluations", "O(1)",
                    "Predicting N steps is O(N). At 120 Hz a step costs microseconds."),
        code=("python", """import math

def deriv(state, wind, g, k_over_m):
    px, py, vx, vy = state
    rx, ry = vx - wind[0], vy - wind[1]
    s = math.hypot(rx, ry)
    ax = g[0] - k_over_m * s * rx
    ay = g[1] - k_over_m * s * ry
    return (vx, vy, ax, ay)

def rk4(state, dt, wind, g, k_over_m):
    k1 = deriv(state, wind, g, k_over_m)
    k2 = deriv([s + dt/2*d for s, d in zip(state, k1)], wind, g, k_over_m)
    k3 = deriv([s + dt/2*d for s, d in zip(state, k2)], wind, g, k_over_m)
    k4 = deriv([s + dt*d   for s, d in zip(state, k3)], wind, g, k_over_m)
    return [s + dt/6*(a + 2*b + 2*c + d_)
            for s, a, b, c, d_ in zip(state, k1, k2, k3, k4)]

# state = [x, y, vx, vy]; g = (0, -9.81)
# at 120 Hz: state = rk4(state, 1/120, wind=(3, 0), g=(0, -9.81), k_over_m=0.0009)"""),
        pitfalls=[
            "Explicit Euler at dt = 1/30 and 800 m/s drifts the projectile by metres — use RK4 or sub-steps.",
            "Tie the integration step to the fixed physics tick and interpolate the render, or the trajectory floats at different frame rates.",
            "C<sub>d</sub> depends on the Mach number: a tabulated curve gives a plausible transonic dip, a single constant does not.",
            "Point collisions tunnel — sweep a capsule or sphere along the whole movement segment.",
        ],
        games=["Arma 3", "Hell Let Loose", "World of Tanks", "Battlefield"],
    ),
    dict(
        id="crits",
        title="Stat-driven critical hit system",
        tags=["Poisson distribution", "logit model", "PRD"],
        summary="A crit chance is not a constant but a function of a stat. The logit model keeps the probability inside (0, 1), while the Poisson distribution answers a different question: how many crits happen over a series of hits.",
        detail=[
            "The logit links a linear combination of stats to a probability: <b>p = 1 / (1 + e<sup>−(β₀ + β₁·stat)</sup>)</b>. The coefficient β₁ sets the price of one stat point in log-odds, so the curve never escapes 100 % and scales to any level. The inverse, logit(p) = ln(p/(1−p)), is a designer's tool: +1 to a stat gives a constant increase in log-odds.",
            "The number of crits over n independent rolls is binomial. For large n and small p it is approximated by a Poisson: <b>P(k) = λᵏe<sup>−λ</sup>/k!</b>, where λ = n·p. That lets you estimate “how many crits will I land in 20 seconds of combat” and budget damage without simulating.",
            "Players feel long dry spells badly even though they are statistically normal. Competitive games therefore use pseudo-random distribution (PRD): the chance grows after each miss and resets after a hit. The mean stays as advertised, the variance drops, and the feeling becomes honest.",
        ],
        formula=("p(stat) = σ(β₀ + β₁·stat),   P(k) = λᵏ·e<sup>−λ</sup> / k!,   λ = n·p",
                 "σ(z) = 1/(1+e<sup>−z</sup>) is the sigmoid. For PRD: pₙ = min(1, C·n) after n misses; pick C numerically so that E[attempts] = 1/p."),
        steps=[
            "Collect a base chance and express stat contributions in log-odds, not in percentages.",
            "Clamp the probability to a sane ceiling (usually 75–90 %) and add a floor.",
            "Roll the RNG once per hit; apply the crit multiplier after armour.",
            "For combo mechanics, evaluate λ = n·p and check the burst against the damage budget.",
            "If players complain about bad luck, enable PRD and re-measure average DPS on a playtest.",
        ],
        complexity=("O(1) per hit", "O(1)",
                    "PRD stores only a failure counter — one variable per character or weapon."),
        code=("python", """import math, random

def crit_chance(stat, b0=-2.2, b1=0.08):
    # b0 sets the base chance, b1 the strength of one stat point
    return 1.0 / (1.0 + math.exp(-(b0 + b1 * stat)))

class PRD:
    \"\"\"Pseudo-random distribution: reduces the variance of streaks.\"\"\"
    def __init__(self, p, constant=0.3):
        self.p = p
        self.constant = constant   # tuned with Monte Carlo
        self.failures = 0

    def roll(self, rng=random):
        chance = min(1.0, self.constant * self.p * (self.failures + 1) ** 1.5)
        if rng.random() < chance:
            self.failures = 0
            return True
        self.failures += 1
        return False

p = crit_chance(stat=42)          # ~0.66 with these betas
prd = PRD(p=0.25)"""),
        pitfalls=[
            "“Five hits without a crit means one is coming” is a player illusion; PRD honestly raises the chance, the raw probability does not change.",
            "Clipping the probability at 1.0 without recomputing the damage budget turns late game into a crit lottery.",
            "Adding or multiplying crit multipliers has to be a conscious choice — mixing them creates unexpected DPS explosions.",
            "The RNG must be server-side and logged, otherwise crit chance is the first thing to be exploited.",
        ],
        games=["Dota 2 (PRD)", "World of Warcraft", "Diablo IV", "Path of Exile"],
    ),
    dict(
        id="prices",
        title="Dynamic economy pricing",
        tags=["differential equations", "game theory", "elasticity"],
        summary="A price is a signal about scarcity. The model is Walrasian price finding: excess demand pushes the price up, excess supply pushes it down, and elasticity sets how strong the reaction is.",
        detail=[
            "The classic dynamics: <b>dp/dt = k·(D(p) − S(p))</b>, where D and S are demand and supply. Modelling them as powers, D(p) = D₀·(p/p₀)<sup>−ε</sup>, gives a convenient dimensionless elasticity ε: the percentage change in demand per percent change in price. For a game economy, stability matters more than accuracy: the price must stay positive and must not oscillate around equilibrium forever.",
            "The second layer is strategic behaviour. NPC traders, auctions and resellers form a game with a Nash equilibrium; if one player can buy out an entire resource and spike the price, the server needs countermeasures: purchase limits, regional markets, a resale tax, instant arbitrage fees. A pure formula without institutions breaks against player behaviour.",
            "In practice prices update on a market tick (every 30–300 seconds), smoothed with an EMA and capped by a relative step. The logarithmic reaction <b>p′ = p·e<sup>k·excess</sup></b> guarantees positivity and makes growth and fall equally noticeable.",
        ],
        formula=("excess = (D − S) / max(D, S),   p′ = p · e<sup>k·excess</sup>,   p ← p + α(p′ − p)",
                 "k — market reaction speed, α — smoothing. An EMA filter damps oscillations and blunts manipulation by a single large order."),
        steps=[
            "Identify sources and sinks of each good: drops, crafting, consumption, taxes, spoilage.",
            "Build D(p) and S(p) with elasticities; give NPC traders a reserve price.",
            "Run the market tick less often than the game tick so prices do not jitter.",
            "Cap the change per tick (e.g. ±10 %) and set absolute floors and ceilings.",
            "Log volume, price and trade count: inflation is visible in a price index, not in one currency.",
        ],
        complexity=("O(1) per good per tick", "O(#goods)",
                    "With player inventories it is O(#orders); use heaps or sorting for the order book."),
        code=("python", """import math

def market_tick(price, demand, supply, k=0.15, alpha=0.25,
                floor=0.2, ceiling=5.0):
    denom = max(demand, supply, 1e-6)
    excess = (demand - supply) / denom          # in [-1, 1]
    target = price * math.exp(k * excess)       # always > 0
    new_price = price + (target - price) * alpha
    return max(price * floor, min(price * ceiling, new_price))

# example: a shortage pushes the price up smoothly, without oscillation
p = 100.0
for _ in range(5):
    p = market_tick(p, demand=120, supply=80)
    print(round(p, 2))"""),
        pitfalls=[
            "A large k makes the price oscillate around equilibrium — the market rings and players cannot react.",
            "Without sinks the currency inflates: prices rise not from scarcity but because there is more money.",
            "Arbitrage between regions must be either forbidden or turned into gameplay with logistics and risk.",
            "Hidden NPC dampeners (“infinite demand”) destroy the point of trading — prefer explicit reserves and quotas.",
        ],
        games=["EVE Online", "Albion Online", "Patrician", "Space Trader"],
    ),
    dict(
        id="splines",
        title="Spline paths and arc-length parameterization",
        tags=["Bézier curves", "Catmull–Rom", "arc length"],
        summary="A spline defines a smooth curve through control points. The classic trap: the parameter t is not proportional to the distance travelled — without an arc-length table, cameras and characters speed up on tight bends.",
        detail=[
            "The cubic Bézier curve: <b>B(t) = (1−t)³P₀ + 3(1−t)²tP₁ + 3(1−t)t²P₂ + t³P₃</b>. It stays inside the convex hull of its control points and is C²-smooth inside a segment, but segment joints need explicit stitching. Catmull–Rom passes through every point and gives C¹ continuity for free — which is why it is the favourite for tracks, cameras and patrols.",
            "The parameter t is uniform in the formula but not along the arc. Moving an object as p(t + Δt) makes it visibly accelerate around corners. The fix is an arc-length table: sample the curve, accumulate distances, normalise, and find t by bisection for the desired distance. Integrating |B′(t)| analytically is possible but a lookup table is simpler and accurate enough (256–1024 samples).",
            "For gameplay what matters is constant speed, a curvature limit (turning radius) and no self-intersections. Check the curvature κ = |x′y″ − y′x″| / (x′² + y′²)<sup>3/2</sup>: too sharp a turn breaks both the camera and the physics.",
        ],
        formula=("B(t) = Σ C(3,i)·(1−t)<sup>3−i</sup>·t<sup>i</sup>·Pᵢ,   s(t) = ∫₀ᵗ |B′(u)| du",
                 "Catmull–Rom: B(t) = ½[(2P₁) + (−P₀+P₂)t + (2P₀−5P₁+4P₂−P₃)t² + (−P₀+3P₁−3P₂+P₃)t³]."),
        steps=[
            "Pick the control points and the spline type: Bézier for authored shapes, Catmull–Rom to pass through points.",
            "Build the arc-length LUT: N samples with accumulated distances.",
            "For a distance s find t by bisection in the LUT (O(log N)).",
            "Orient the object along the tangent B′(t) and derive the roll from curvature and speed.",
            "Clamp the step s so the object does not cut corners on tight bends.",
        ],
        complexity=("O(N) to build, O(log N) per sample", "O(N)",
                    "A static track builds the LUT once; a dynamic one recomputes it as points change."),
        code=("python", """import bisect, math

def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d
                 for a, b, c, d in zip(p0, p1, p2, p3))

def build_lut(points, samples=512):
    pts = [bezier(*points, i/(samples-1)) for i in range(samples)]
    acc, lut = [0.0], [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    total = acc[-1]
    return pts, [d / total for d in acc]   # normalised lengths

def t_at_distance(lut, s):
    s = min(max(s, 0.0), 1.0)
    i = bisect.bisect_left(lut, s)
    return (i - 1) / (len(lut) - 1)        # linear interpolation of t"""),
        pitfalls=[
            "Moving along the raw t gives uneven speed — always reparameterise by arc length.",
            "Catmull–Rom can loop between points; check curvature and limit the tension.",
            "A sparse LUT causes visible jerks on long curves; use 1024+ samples for racing tracks or adaptive subdivision.",
            "Damp the camera follow, otherwise turns look twitchy.",
        ],
        games=["Unity Cinemachine", "Forza / Gran Turismo", "Journey", "Sonic (path sections)"],
    ),
    dict(
        id="quantum",
        title="Quantum state mechanics",
        tags=["linear algebra", "density matrices", "superposition"],
        summary="A quantum state is a vector of amplitudes, and measurement is a probabilistic transition to one of the basis states. In a game this yields an “uncertain until observed” mechanic backed by honest mathematics.",
        detail=[
            "A qubit is described by <b>|ψ⟩ = α|0⟩ + β|1⟩</b>, where |α|² + |β|² = 1. Before measurement the object “is in superposition”: a door is both open and closed, an enemy exists in two corridors. Measurement yields 0 with probability |α|² and 1 with probability |β|², after which the state collapses.",
            "Mixed states (when there is classical uncertainty) are described by a density matrix ρ = Σ pᵢ|ψᵢ⟩⟨ψᵢ|. Gates are unitary matrices: Hadamard creates superposition, CNOT entangles two qubits. For n qubits the vector holds 2ⁿ amplitudes — which is why a full quantum simulator inside a game is limited to roughly 10–20 “qubits”.",
            "The key difference from magic: an unknown state cannot be cloned (no-cloning), entanglement cannot carry information faster than light (no-signaling), and save/load must preserve the distribution — otherwise players reload until they get the outcome they want. Fix the RNG seed inside the world state, and design probabilistic mechanics so that every outcome is playable.",
        ],
        formula=("|ψ⟩ = α|0⟩ + β|1⟩,   |α|² + |β|² = 1,   P(0) = |α|²",
                 "Hadamard gate: H = 1/√2 · [[1, 1], [1, −1]]. For two qubits the basis is |00⟩, |01⟩, |10⟩, |11⟩; CNOT flips the second when the first is 1."),
        steps=[
            "Choose the representation: pure states (n ≤ ~12) or density matrices (noise, decoherence).",
            "Define unitary gates and their visual counterparts in the world.",
            "On “measurement”, roll the RNG with the amplitude probabilities and store the outcome in the object state.",
            "Sync the seed between clients and server for deterministic multiplayer.",
            "Saves store amplitudes/matrices, not the observed outcome — otherwise the mechanic loses its point.",
        ],
        complexity=("O(2ⁿ) per state, O(4ⁿ) per gate (naive)", "O(2ⁿ) amplitudes",
                    "For n = 16 that is 65 536 complex numbers — the practical real-time limit."),
        code=("python", """import math, random

# |psi> = a|0> + b|1>; a state is a list of complex amplitudes
def hadamard(state):
    a, b = state
    r = 1 / math.sqrt(2)
    return [r * (a + b), r * (a - b)]

def measure(state, rng=random):
    p0 = abs(state[0]) ** 2
    outcome = 0 if rng.random() < p0 else 1
    # after measurement the state collapses
    collapsed = [1.0, 0.0] if outcome == 0 else [0.0, 1.0]
    return outcome, collapsed

psi = [1.0, 0.0]          # |0>
psi = hadamard(psi)        # (|0> + |1>) / sqrt(2)
print(measure(psi, random.Random(42)))"""),
        pitfalls=[
            "Storing the “observed” state destroys the superposition and devalues the mechanic.",
            "Reloading until the desired outcome appears means the player lacks control over the probabilities — offer a choice or a pity mechanic.",
            "Do not explain physics to the player; explain rules: “while nobody is looking, the object is in two places”.",
            "Using entanglement as instant communication is a design error, not a physics nuance.",
        ],
        games=["Quantum Break", "Antichamber", "The Talos Principle", "Schrödinger's Cat puzzles"],
    ),
    dict(
        id="4x-ai",
        title="4X strategy AI (utility, MCTS, influence maps)",
        tags=["utility AI", "MCTS/UCT", "decision trees"],
        summary="Strategic AI splits a decision into situation assessment, option generation and choice. Utility AI is faster and more predictable, MCTS is stronger in tactics, and influence maps connect the map to those decisions.",
        detail=[
            "Utility AI scores every action as <b>score = Σ wᵢ·fᵢ(context)</b>, where fᵢ are normalised factors (food need, enemy proximity, gold reserve). The choice can be greedy or sampled with a softmax and a temperature: a high temperature gives variety, a low one gives determinism. Weights are tuned by simulations and telemetry, not by eye.",
            "For tactical fights, use MCTS with UCT: <b>a* = argmax Q(s,a) + c·√(ln N(s)/N(s,a))</b>. The tree grows towards promising branches and rollouts are replaced by a light heuristic. On large maps plain MCTS is expensive, so it is combined with abstraction: unit groups, regions, and “strategic layers” running every N seconds.",
            "Influence maps are a convolution of the map by the influence radius of units and buildings. They answer cheap questions: “where are we strong”, “where is it safe to move”, “where will the opponent open a front”. The fog of war matters: the AI must decide on the last known information, otherwise it reads as cheating and the game stops being fun.",
        ],
        formula=("score(action) = Σ wᵢ·fᵢ(ctx),   P(a) = e<sup>score(a)/τ</sup> / Σ e<sup>score(b)/τ</sup>",
                 "UCT: Q(s,a) + c·√(ln N(s) / N(s,a)). Q — mean reward, N — visit count, c balances exploration and exploitation."),
        steps=[
            "Collect the context: resources, threats, goals, fog of war, diplomacy.",
            "Describe 10–30 actions with their factors; normalise the factors into [0, 1].",
            "Split the layers: strategy (every 5–30 s), tactics (every 0.5–2 s), micro (every tick).",
            "Add hysteresis and cooldowns so the AI does not flip plans every tick.",
            "Validate behaviour on replays: metrics like “time to react”, “units lost”, “map share”.",
        ],
        complexity=("Utility O(#actions·#factors), MCTS O(iterations·depth)", "O(tree + map)",
                    "Budget MCTS iterations per frame; compute influence on a 32×32 grid, not per pixel."),
        code=("python", """import math

def softmax_pick(actions, context, weights, temperature=0.35):
    scores = {}
    for name, feature_fn in actions.items():
        feats = feature_fn(context)          # {"food_need": 0.8, "threat": 0.2, ...}
        scores[name] = sum(weights[name].get(k, 0.0) * v for k, v in feats.items())
    m = max(scores.values())
    exp = {k: math.exp((v - m) / temperature) for k, v in scores.items()}
    z = sum(exp.values())
    return {k: v / z for k, v in exp.items()}

# actions: expand, build_farm, build_barracks, attack, defend
# features(ctx) -> {food_need, threat, gold, enemy_weakness}"""),
        pitfalls=[
            "An AI that sees through the fog of war reads as cheating — keep a separate per-faction memory.",
            "Switching decisions too often makes the army jitter; use hysteresis and a minimum hold time.",
            "Utility weights overfit to one player strategy — test against several styles and on several maps.",
            "MCTS without abstraction hits a combinatorial wall at 20–30 units.",
        ],
        games=["Civilization VI", "Stellaris", "Endless Space 2", "Age of Wonders 4"],
    ),
    dict(
        id="npc-emotions",
        title="Emotional NPC model (PAD + appraisal)",
        tags=["PAD model", "OCC", "clustering"],
        summary="An NPC emotion is a point in “pleasure – arousal – dominance” space that decays smoothly and is shifted by events. Such a model produces continuous reactions instead of a set of scripted animations.",
        detail=[
            "The PAD model (Pleasure, Arousal, Dominance) describes mood as a three-dimensional vector. Events are evaluated with the OCC scheme: desirability, probability, expectedness, control. “An enemy stole the food” drops Pleasure hard, raises Arousal and lowers Dominance; “I won” raises all three with high control.",
            "The dynamics are <b>E′ = E·λ + Σ wᵢ·eventᵢ</b>, with decay towards the base personality and clamping into [−1, 1]. Characters differ by λ (cooling speed), their base point and their appraisal weights. It is cheap, interpretable and easy for a designer to tune from a table.",
            "The raw vector is useless for animation — it has to be discretised. Clustering (k-means over labelled emotions: joy, fear, anger, sadness) yields the state that selects an animation tree and a line of dialogue. Hysteresis and a minimum transition duration prevent flickering; strong emotions suppress weak ones but do not erase them instantly.",
        ],
        formula=("E ∈ [−1,1]³ = (P, A, D),   E′ = clamp(λ·E + Σ wᵢ·eventᵢ)",
                 "λ ≈ 0.9–0.99 per game tick. Classify an emotion by the nearest PAD centroid or by per-axis thresholds."),
        steps=[
            "Define the NPC character: base PAD point, cooling speed, sensitivity to events.",
            "Describe events through appraisal features: desirability, control, expectedness, blame/merit.",
            "Update the emotion on events and let it drift back to the baseline.",
            "Classify the state into animations and lines with hysteresis.",
            "Expose the emotion through behaviour: distance, aggression, willingness to trade — the player must be able to read it.",
        ],
        complexity=("O(#events) per update, O(k) per classification", "O(1) per NPC",
                    "The animation tree and weight tables are static data; the live state is three floats."),
        code=("python", """import math

DECAY = 0.96

def appraise(emotion, event, sensitivity):
    \"\"\"emotion = [P, A, D]; event = [p, a, d] in [-1, 1].\"\"\"
    out = []
    for i in range(3):
        v = emotion[i] * DECAY + event[i] * sensitivity[i]
        out.append(max(-1.0, min(1.0, v)))
    return out

EMOTIONS = {           # PAD centroids
    "joy":    (0.8, 0.6, 0.5),
    "fear":   (-0.6, 0.8, -0.7),
    "anger":  (-0.7, 0.7, 0.6),
    "sadness": (-0.6, -0.4, -0.4),
}

def classify(e):
    return min(EMOTIONS, key=lambda k: math.dist(e, EMOTIONS[k]))

mood = [0.0, 0.0, 0.0]
mood = appraise(mood, event=[-0.9, 0.8, -0.3], sensitivity=[0.8, 0.9, 0.5])
print(classify(mood))   # most likely "fear\""""),
        pitfalls=[
            "Instant emotional jumps look cartoonish — decay and a minimum duration are mandatory.",
            "An emotion without a behavioural outlet is useless: NPCs must change distance, speech tempo and decisions.",
            "An overly complex model is opaque for designers — keep the weights in a table and log the reasons.",
            "Cultural and linguistic differences in lines can break the tone — emotion localisation is more than translation.",
        ],
        games=["The Sims", "RimWorld", "Fable", "Dwarf Fortress"],
    ),
    dict(
        id="adaptive",
        title="Adaptive difficulty (skill estimation + RL)",
        tags=["Q-learning", "Bayesian networks", "bandit"],
        summary="The goal of adaptive difficulty is to hold the player in the flow between boredom and frustration. Difficulty is chosen from an estimate of skill and behaviour, not from a single health bar.",
        detail=[
            "First you have to estimate the player. The simplest version is an Elo/TrueSkill-like rating based on duel outcomes. A more informative one is a Bayesian network over features: accuracy, reaction time, death count, use of cover, pace of progress. The posterior skill distribution is updated after every fight rather than “by account level”.",
            "Choosing the difficulty is a multi-armed bandit: enemy parameters (damage, aggression, reinforcement count) are the arms, the reward is closeness to a target success rate (say 60–70 % wins) plus retention. Thompson sampling or ε-greedy explore the space without breaking the feeling of fairness.",
            "Inside a fight, Q-learning applies: <b>Q(s,a) ← Q(s,a) + α[r + γ·max Q(s′,a′) − Q(s,a)]</b>. The reward encourages tense but winnable fights and punishes instant deaths and meat-grinders. The adaptation has to stay invisible: players must never see enemies “giving up”, or the victory loses its value.",
        ],
        formula=("Q(s,a) ← Q(s,a) + α·[r + γ·max<sub>a′</sub>Q(s′,a′) − Q(s,a)]",
                 "α — learning rate, γ — discount. For DDA the reward is r = −|winrate − target| − λ·(deaths / time)."),
        steps=[
            "Choose a success metric: win rate, fight duration, deaths per checkpoint, resource spend.",
            "Estimate the player's skill Bayesianly; do not mix it with gear progress.",
            "Limit the adaptation space to 3–5 parameters so the balance stays under control.",
            "Change parameters in steps with a delay: abrupt tuning reads as cheating.",
            "Verify that the game stays fun at low skill and does not turn into a punching bag simulator at high skill.",
        ],
        complexity=("O(#states·#actions) per update", "O(#Q-table)",
                    "For large spaces use linear approximations or a small network; inference must fit in a frame."),
        code=("python", """from collections import defaultdict

def q_update(Q, s, a, reward, s2, alpha=0.1, gamma=0.95):
    best_next = max(Q[s2].values()) if Q[s2] else 0.0
    old = Q[s][a]
    Q[s][a] = old + alpha * (reward + gamma * best_next - old)

Q = defaultdict(lambda: defaultdict(float))
# states: (hp_bucket, ammo_bucket, distance_bucket)
# actions: retreat, flank, push, suppress
q_update(Q, ("low", "low", "near"), "retreat", -0.2, ("low", "low", "far"))"""),
        pitfalls=[
            "A visible rubber band in racing or sports enrages players — mask it with rival behaviour instead of teleporting.",
            "Too fast an adaptation punishes good play and rewards deliberately bad play — smooth it and limit the range.",
            "Estimating skill from a single fight is noisy; use Bayesian updates and confidence intervals.",
            "DDA does not replace balance: if a weapon is broken, adaptive difficulty only hides the problem.",
        ],
        games=["Left 4 Dead (AI Director)", "Resident Evil 4", "Mario Kart (rubber band)", "Crash Bandicoot"],
    ),
    dict(
        id="dialogue",
        title="Procedural dialogue (Markov → transformers)",
        tags=["Markov chains", "transformers", "grammars"],
        summary="Dialogue can be generated on three levels: a Markov chain for cheap variation, a grammar for controlled meaning, and an LLM for free-form speech. Games almost always need a hybrid with hard constraints.",
        detail=[
            "A first-order Markov chain stores transition probabilities between words: P(wₜ | wₜ₋₁). Training is a matter of counting pairs, generation is a random walk over the graph. It is cheap and produces plausible noise, but the coherence is short: after 10–15 words the model has forgotten the beginning. For names and short lines that is often enough.",
            "The modern approach is a transformer with attention: <b>Attention(Q,K,V) = softmax(QKᵀ/√d<sub>k</sub>)V</b>. The model accounts for the whole context, but it needs tokens, memory and latency. Games use small local models (1–8B parameters), KV caching, streaming generation and length limits. Quality jumps when the model is given structured context: who speaks, the relationship, known facts, the current quest.",
            "The production pattern: an authored dialogue graph defines branches and consequences, while the LLM rephrases lines inside a node under constraints (tone, length, forbidden topics, world facts). Validating answers, falling back to a template and logging are mandatory — generative text without guardrails breaks lore and ratings.",
        ],
        formula=("P(w₁…wₙ) = Π P(wₜ | wₜ₋₁),   Attention(Q,K,V) = softmax(QKᵀ/√d<sub>k</sub>)·V",
                 "For trigrams: P(wₜ | wₜ₋₂, wₜ₋₁). Temperature T divides the logits before the softmax: higher T is more varied, lower T more stable."),
        steps=[
            "Define the boundaries of freedom: which names, lines and branches may be generated.",
            "Collect a corpus in the character's voice, or define a grammar with slots.",
            "Add state: relationships, memory of events, current goal — otherwise the dialogue is meaningless.",
            "Limit the length and check facts against a knowledge base; fall back to a template on failure.",
            "Log and moderate the output, especially in multiplayer and UGC.",
        ],
        complexity=("Markov O(1) per word, transformer O(n²·d) per layer", "O(vocabulary) / O(model parameters)",
                    "A real-time LLM needs a GPU and streaming; for NPC lines, pre-generation and caching are far more common."),
        code=("python", """import random
from collections import defaultdict

def train(text):
    model = defaultdict(list)
    words = text.split()
    for a, b in zip(words, words[1:]):
        model[a].append(b)
    return model

def generate(model, start, n=24, rng=random):
    if not model:
        return start
    cur, out = start, [start]
    for _ in range(n):
        cur = rng.choice(model[cur]) if model[cur] else rng.choice(list(model))
        out.append(cur)
    return " ".join(out)

corpus = ("The guard closes the gate at night. "
          "The guard dislikes strangers. A merchant waits at the gate at dawn.")
print(generate(train(corpus), "The guard", rng=random.Random(7)))"""),
        pitfalls=[
            "A Markov chain repeats the same phrases — penalise repeats and mix sources.",
            "An LLM without a fact base invents quests and breaks canon; RAG and validation are mandatory.",
            "Long answers break the rhythm of combat — cap the length and give the player a skip.",
            "Generative text in a rated game requires moderation and age gating.",
        ],
        games=["Façade", "AI Dungeon", "Skyrim (mods)", "1001 Nights"],
    ),
    dict(
        id="flocking",
        title="Flocking / boids and crowd steering",
        tags=["flocking theory", "boids", "spatial hash"],
        summary="Three simple rules — keep distance, match heading, approach the centre — produce a convincing flock. The secret is not the rules but the spatial index and the clamping of forces.",
        detail=[
            "Reynolds' boids: separation (push away from close neighbours), alignment (match the heading of neighbours), cohesion (steer towards the centre of the group). Each rule yields a vector; they are blended with weights and clamped by magnitude. Different radii per rule matter: separation short, cohesion long.",
            "Naive all-pairs is O(n²) — for 500 units that is 250 000 checks per frame. A spatial hash (grid with a cell around the perception radius) brings it down to O(n·k), where k is the average neighbour count. For thousands of agents, run the rules in a compute shader or use flow fields for long-range movement.",
            "On top of boids sit steering behaviours: obstacle avoidance, pursuit, formation keeping, queuing at a door. Clamping maximum force and speed, plus priorities (separation beats cohesion), prevent jitter and density explosions. For deterministic multiplayer the update must run on a fixed tick and must not depend on iteration order.",
        ],
        formula=("v ← clamp(v + Σ wᵢ·steerᵢ·dt, v<sub>max</sub>),   steer<sub>sep</sub> = Σ (p − pⱼ)/|p − pⱼ|²",
                 "Neighbouring is usually limited by radius and field of view (270°, say), otherwise the flock “sees” behind itself."),
        steps=[
            "Rebuild the spatial hash from agent positions once per tick.",
            "For each agent gather neighbours inside the perception radius.",
            "Compute the three forces, normalise them, blend with weights; separation gets priority.",
            "Clamp acceleration and speed; add damping so the flock settles down.",
            "Add obstacles and leaders (a flow field or a goal), otherwise the flock circles in place.",
        ],
        complexity=("O(n·k) with a grid, O(n²) naively", "O(n) + grid",
                    "For 10 000+ agents use GPU compute or hierarchical levels (flock leaders)."),
        code=("python", """import math

def neighbors_hash(agents, cell):
    grid = {}
    for a in agents:
        key = (int(a["x"] // cell), int(a["y"] // cell))
        grid.setdefault(key, []).append(a)
    return grid

def steer(b, grid, cell, R=60):
    sep_x = sep_y = ali_x = ali_y = coh_x = coh_y = 0.0
    n = 0
    cx, cy = int(b["x"] // cell), int(b["y"] // cell)
    for gx in (cx-1, cx, cx+1):
        for gy in (cy-1, cy, cy+1):
            for o in grid.get((gx, gy), ()):
                if o is b: continue
                dx, dy = o["x"]-b["x"], o["y"]-b["y"]
                d2 = dx*dx + dy*dy
                if d2 > R*R or d2 == 0: continue
                sep_x -= dx / d2; sep_y -= dy / d2
                ali_x += o["vx"]; ali_y += o["vy"]
                coh_x += o["x"];  coh_y += o["y"]
                n += 1
    if not n: return (0.0, 0.0)
    return (1.6*sep_x + 0.9*(ali_x/n - b["vx"]) + 0.004*(coh_x/n - b["x"]),
            1.6*sep_y + 0.9*(ali_y/n - b["vy"]) + 0.004*(coh_y/n - b["y"]))"""),
        pitfalls=[
            "Without a spatial index O(n²) eats the frame at a few hundred units.",
            "Too much cohesion collapses the flock into a point, too much separation tears it apart.",
            "Agents jitter around obstacles without smoothing and hysteresis — add damping.",
            "The update order influences the result; fix it for the network or compute forces from the previous tick.",
        ],
        games=["StarCraft II", "Total War", "Planet Zoo", "Batman: Arkham (crowds)"],
    ),
    dict(
        id="terrain",
        title="Procedural terrain with fBm and erosion",
        tags=["Perlin noise", "fractals", "erosion"],
        summary="A landscape is a sum of noise octaves: large shapes make mountains, small ones make rocks. Realism arrives when you add erosion, biomes and passability constraints on top of the noise.",
        detail=[
            "Fractal Brownian motion: <b>h(x) = Σ aᵢ·noise(fᵢ·x)</b>, where every octave doubles the frequency and halves the amplitude. Perlin gives gradient noise without the blockiness of value noise, and the ridged variant (1 − |noise|)² creates mountain ridges. Domain warping — displacing coordinates with another noise — adds winding valleys and unusually beautiful shapes.",
            "Raw noise looks fluffy but does not look like land. Hydraulic erosion models water droplets: a droplet rolls along the gradient, erodes the ground, carries sediment and deposits it in the low areas. A few hundred thousand droplets per map produce valleys, alluvial fans and river beds. For real-time use, pre-bake the erosion into a texture and use it as a mask.",
            "Biomes follow temperature and humidity: height plus latitude gives temperature, distance to water plus wind gives humidity. Then the rules: desert, forest, tundra, swamp. Gameplay validation matters: the map needs connected traversable routes, starting zones with resources and natural borders. Chunks are generated with LOD, and noise is sampled in world coordinates — otherwise seams appear at the borders.",
        ],
        formula=("fBm(x) = Σ<sub>i=0</sub><sup>O−1</sup> gain<sup>i</sup>·noise(x·lacunarity<sup>i</sup>)",
                 "Typical: O = 4–8 octaves, lacunarity = 2, gain = 0.5. Ridged: (1 − |noise|)² sharpens the ridges."),
        steps=[
            "Generate the base fBm height in world coordinates from a seed.",
            "Add mountain ridges with ridged noise and warping for valleys.",
            "Run erosion (offline or on the GPU) and keep the sediment map.",
            "Compute temperature and humidity and classify biomes.",
            "Check connectivity and starting zones; build the navigation mesh and LOD chunks.",
        ],
        complexity=("O(N²·O) to generate, O(N²) erosion iterations", "O(N²) heights + textures",
                    "A 256×256 chunk with 6 octaves is millions of samples; cache it and generate in the background."),
        code=("python", """import math

def fbm(x, y, noise2, octaves=6, lacunarity=2.0, gain=0.5):
    amp, freq = 1.0, 1.0
    total = norm = 0.0
    for _ in range(octaves):
        total += amp * noise2(x * freq, y * freq)
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / norm          # normalised to [-1, 1]

def terrain_height(x, y, noise2, sea=0.0):
    base = fbm(x, y, noise2) * 0.5 + 0.5
    ridge = 1.0 - abs(fbm(x * 2.1, y * 2.1, noise2, 4))
    h = base * 0.75 + ridge * 0.25
    return max(0.0, h - sea) ** 1.6   # raised mountains, flat lowlands

# for chunks use WORLD coordinates: x = chunk_x*size + local_x"""),
        pitfalls=[
            "Sampling noise in local chunk coordinates produces seams — use world coordinates only.",
            "The same seed must give the same world on every platform — pin the noise implementation.",
            "Without passability validation the generator creates walls and unreachable resources.",
            "Real-time erosion is expensive: compute it offline or on the GPU, not in the game loop.",
        ],
        games=["Minecraft", "No Man's Sky", "Dwarf Fortress", "Horizon Zero Dawn"],
    ),
    dict(
        id="gi",
        title="Dynamic global illumination",
        tags=["rendering equation", "radiosity", "path tracing", "DDGI"],
        summary="Global illumination is an integral over all directions that accounts for light bounced off other surfaces. In real time it is approximated: with probes, with ray tracing plus denoising, or with baked lightmaps.",
        detail=[
            "The rendering equation: <b>L<sub>o</sub>(x, ω<sub>o</sub>) = L<sub>e</sub> + ∫ f<sub>r</sub>(x, ω<sub>i</sub>, ω<sub>o</sub>)·L<sub>i</sub>(x, ω<sub>i</sub>)·cosθ<sub>i</sub> dω<sub>i</sub></b>. It is recursive: L<sub>i</sub> is the light leaving other surfaces. It has analytic solutions only for simple scenes; numerically it is estimated by Monte Carlo sampling.",
            "Path tracing estimates the integral as the mean over rays: <b>L ≈ (1/N)·Σ f·L·cosθ / pdf</b>. For a Lambertian material f = albedo/π and pdf = cosθ/π, so the factors cancel to albedo — which is why the estimator is so elegant. The problem is noise: removing it needs a denoiser (SVGF, OIDN) and temporal accumulation with reprojection.",
            "Real-time alternatives: baked lightmaps and irradiance probes for static light, DDGI — a grid of probes updated with rays and spherical harmonics, screen-space GI (cheap, but blind to what is off-screen), and Lumen-style hybrids with an SDF scene. Radiosity solves a linear system for diffuse surfaces and is still used for baking.",
        ],
        formula=("L<sub>o</sub> = L<sub>e</sub> + ∫<sub>Ω</sub> f<sub>r</sub>·L<sub>i</sub>·cosθ<sub>i</sub> dω<sub>i</sub>",
                 "For a diffuse surface: L<sub>o</sub> = L<sub>e</sub> + (albedo/π)·∫ L<sub>i</sub> cosθ dω. Radiosity iterations converge to the solution of the form-factor system."),
        steps=[
            "Set the budget: baked light, probes, or a full ray tracer.",
            "Separate direct and indirect light: direct via shadows and maps, indirect via probes or rays.",
            "For path tracing add next-event estimation (NEE) and a denoiser.",
            "For DDGI update probes in portions across frames and store SH coefficients.",
            "Watch for light leaks and shadow bias; tune the bias carefully.",
        ],
        complexity=("Path tracing O(N·samples), DDGI O(#probes·rays) amortised", "O(#probes·SH) + history",
                    "Full GI per frame is infeasible; temporal reprojection and ray budgeting are the key."),
        code=("python", """import math

def basis(n):
    helper = (0.0, 1.0, 0.0) if abs(n[1]) < 0.99 else (1.0, 0.0, 0.0)
    t = normalize(cross(helper, n))
    return t, cross(n, t)

def cosine_hemisphere(n, rng):
    u1, u2 = rng.random(), rng.random()
    r, phi = math.sqrt(u1), 2 * math.pi * u2
    tangent, bitangent = basis(n)      # orthonormal frame around n
    cos_t, sin_t = math.cos(phi), math.sin(phi)
    return tuple(tangent[i] * (r * cos_t) + bitangent[i] * (r * sin_t)
                 + n[i] * math.sqrt(max(0.0, 1.0 - u1)) for i in range(3))

def radiance(ray, depth, scene, rng):
    hit = scene.intersect(ray)
    if hit is None:
        return scene.sky(ray.direction)
    if depth == 0:
        return hit.emission
    wi = cosine_hemisphere(hit.normal, rng)
    # f_r = albedo/pi, pdf = cos(theta)/pi  =>  f_r*cos(theta)/pdf = albedo
    return hit.emission + hit.albedo * radiance(
        hit.spawn(wi), depth - 1, scene, rng)"""),
        pitfalls=[
            "Monte Carlo without a denoiser gives grain; without temporal accumulation it boils.",
            "Screen-space GI cannot see behind the camera — corners and corridors go dark or glow.",
            "Probes placed inside walls leak light; validate visibility and offset the probes.",
            "GI is the most expensive item in the budget — always keep a fallback for weak GPUs.",
        ],
        games=["Metro Exodus: Enhanced Edition", "Cyberpunk 2077 (RTGI)", "UE5 Lumen", "Control"],
    ),
    dict(
        id="destruction",
        title="Destruction: stress, Voronoi, rigid bodies",
        tags=["elasticity", "FEM", "Voronoi"],
        summary="Destruction is a comparison of stress against material strength. To keep it playable, fragments are almost always prepared in advance (Voronoi) and the runtime only decides which piece to break off.",
        detail=[
            "Stress σ = F/A, strain ε = ΔL/L, Hooke's law σ = E·ε. When the stress exceeds the ultimate strength, the material cracks. For brittle objects (glass, concrete) not only the force but the direction of the impact matters; for metals, plastic deformation matters. Full FEM in real time is far too expensive, so physics is simplified to rigid bodies and pre-cut fragments.",
            "Voronoi cutting: generate points inside the volume, then each point claims the nearest volume. The result is a mosaic of convex shards that fit together exactly. Several levels of detail are baked in advance (big pieces → small ones) and the right one is activated on impact. Connectivity is checked by walking the neighbour graph: detached pieces must fly away rather than hang in the air.",
            "The runtime budget: cap the number of active rigid bodies, sleep them once they settle, merge small shards into decals and dust, and use LOD for distant debris. In multiplayer, destruction has to be server-authoritative or deterministic from a seed — otherwise clients see different walls.",
        ],
        formula=("σ = E·ε,   break when σ > σ<sub>max</sub>,   E<sub>impact</sub> = ½mv²",
                 "For brittle materials add a maximum shear stress criterion (Mohr–Coulomb) and cracks along the impact direction."),
        steps=[
            "Split the object into structural and decorative parts; give the structural ones a strength.",
            "Pre-cut the object into Voronoi shards with 2–3 levels of detail.",
            "Build a neighbour graph to check connectivity after an impact.",
            "On impact, compare energy/stress with the threshold and activate the shards.",
            "Cap the number of active bodies and replace small debris with particles and decals.",
        ],
        complexity=("O(#shards) per activation, O(V+E) for the connectivity check", "O(#shards)",
                    "Cutting is offline. At runtime the expensive part is shard physics and collisions, not spawning."),
        code=("csharp", """public class Breakable : MonoBehaviour
{
    [SerializeField] float tensileStrength = 4e6f; // Pa
    [SerializeField] float supportArea = 0.02f;    // m^2
    [SerializeField] FracturePattern pattern;      // pre-baked Voronoi

    public void ApplyImpact(Vector3 point, float impulse)
    {
        float stress = impulse / supportArea;
        if (stress < tensileStrength) return;

        var cell = pattern.ClosestCell(point);
        foreach (var shard in cell.SplitAlongPlanes())
        {
            var rb = shard.SpawnRigidbody();
            rb.AddExplosionForce(impulse, point, 1.5f);
        }
        // connectivity: BFS over the neighbour graph, detached pieces go free
    }
}"""),
        pitfalls=[
            "Thousands of active shards kill the physics — cap the budget and put bodies to sleep.",
            "Fragments without a connectivity check hang in the air or sink through the floor.",
            "Destruction breaks navigation and quests: mark affected zones and rebuild the navmesh.",
            "In a network, destruction must be authoritative, or walls diverge between clients.",
        ],
        games=["Battlefield: Bad Company 2", "Red Faction: Guerrilla", "Teardown", "Control"],
    ),
]
