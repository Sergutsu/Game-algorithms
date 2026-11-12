# -*- coding: utf-8 -*-
"""Part II, layers 03–04 (English): worlds, content and systems. Topics 78–85."""

TOPICS_EN_PG_B = [
    dict(
        id="erosion",
        title="Hydraulic erosion: rain, sediment and deltas",
        tags=["erosion", "sediment", "heightmap", "normals"],
        summary="fBm gives believable roughness but no valleys, channels or alluvial fans. Erosion simulates rain: a droplet runs downhill, scours the slope, carries sediment and drops it where it slows down. That is what turns noise into landscape.",
        detail=[
            "The droplet model: position, direction with inertia, and a sediment load. On each step the droplet moves along the height gradient (bilinearly, so it does not jump between cells), computes <b>stream capacity</b> from slope and speed, picks up sediment when below capacity and deposits when above. Slow evaporation reduces capacity, so droplets unload in lowlands.",
            "Key parameters: droplets per cell (10–30), inertia (0.05–0.2), erosion rate, deposition rate, erosion brush radius (3×3 with weights). The radius is mandatory: otherwise you get one-pixel canyons and aliasing. After the droplets, recompute normals — the beauty of erosion lives in slope shading.",
            "A cheap alternative is <b>thermal erosion</b>: when a height difference exceeds the talus angle, material slides downhill. It smooths spikes and builds scree. In production, erosion is often baked offline in Houdini/World Machine, but infinite worlds move it to the GPU: 100k droplets per frame is realistic.",
        ],
        formula=("C = Kc · sinα · |v|,   Δh = Ks · (C − s),   "
                 "s ← s + Δh,   h ← h − Δh",
                 "α is the slope angle, v the droplet speed, s the sediment. If s < C the droplet erodes (h decreases); if s > C it deposits. Kc and Ks are tuned to map scale."),
        steps=[
            "Build a heightmap (fBm) and normals; allocate a sediment buffer and an erosion brush.",
            "Launch N droplets from random points with initial speed and direction.",
            "Move with inertia and gradient; sample the new position bilinearly.",
            "Compute capacity, erode or deposit through the brush, reduce capacity (evaporation).",
            "Stop at the bottom or in a pit; afterwards recompute normals and lightly smooth artefacts.",
        ],
        complexity=("O(drops · steps)", "O(W·H) + sediment buffer",
                    "100k droplets × 30 steps is seconds on the CPU, milliseconds on the GPU; tile large worlds with overlap."),
        code=("python", """import math, random

def erode(h, iterations=50000, seed=0, inertia=0.08, capacity=4.0,
          erode_speed=0.3, deposit_speed=0.3, evaporate=0.01):
    rng = random.Random(seed)
    height, width = len(h), len(h[0])
    sediment = [[0.0] * width for _ in range(height)]

    def grad(x, y):
        x0, y0 = int(x), int(y)
        tx, ty = x - x0, y - y0
        gx = (h[y0][min(x0 + 1, width - 1)] - h[y0][x0]) * (1 - ty) + \\
             (h[min(y0 + 1, height - 1)][min(x0 + 1, width - 1)] -
              h[min(y0 + 1, height - 1)][x0]) * ty
        gy = (h[min(y0 + 1, height - 1)][x0] - h[y0][x0]) * (1 - tx) + \\
             (h[min(y0 + 1, height - 1)][min(x0 + 1, width - 1)] -
              h[y0][min(x0 + 1, width - 1)]) * tx
        return gx, gy

    for _ in range(iterations):
        x, y = rng.uniform(0, width - 2), rng.uniform(0, height - 2)
        dx = dy = 0.0
        speed = 1.0
        water = 1.0
        carried = 0.0
        for step in range(48):
            gx, gy = grad(x, y)
            dx = dx * inertia - gx * (1 - inertia)
            dy = dy * inertia - gy * (1 - inertia)
            length = math.hypot(dx, dy)
            if length < 1e-6:
                break
            dx, dy = dx / length, dy / length
            x, y = x + dx, y + dy
            if not (0 <= x < width - 1 and 0 <= y < height - 1):
                break
            dh = h[int(y)][int(x)] - h[int(y - dy)][int(x - dx)]
            cap = max(-dh, 0.01) * speed * water * capacity
            if carried > cap or dh > 0:
                amount = min(dh if dh > 0 else carried, carried)
                h[int(y - dy)][int(x - dx)] += amount * deposit_speed
                carried -= amount * deposit_speed
            else:
                amount = min((cap - carried) * erode_speed, -dh)
                h[int(y - dy)][int(x - dx)] -= amount
                carried += amount
            speed = math.sqrt(max(0.0, speed * speed + dh * -2.0))
            water *= 1 - evaporate
        sediment[int(y)][int(x)] += carried
    return h, sediment"""),
        pitfalls=[
            "No brush radius — one-pixel channels and aliasing instead of valleys.",
            "Droplets without inertia get stuck in local minima and drill pits.",
            "Erosion that is too strong shaves off the whole relief; start with 10–30 droplets per cell.",
            "Not recomputing normals — the map looks flat although heights changed.",
        ],
        games=["No Man's Sky", "Valheim", "Horizon Forbidden West", "Starfield"],
    ),
    dict(
        id="biomes",
        title="Biomes: Whittaker diagram, climate and transitions",
        tags=["Whittaker", "temperature", "moisture", "climate"],
        summary="A biome is a function of climate. Temperature depends on latitude and altitude, moisture on proximity to water, wind and relief. The Whittaker diagram turns (temperature, precipitation) into a terrain type, and soft transitions remove the checkerboard.",
        detail=[
            "Base temperature: <b>T = T₀ − k·|latitude| − 6.5 °C/km · altitude</b>. Moisture is harder: evaporation near water, wind transport, rain shadow behind mountains, runoff. A practical approach sums sources with distance falloff (or a fast blur over the water mask) and adds noise for heterogeneity.",
            "Classification is a table: tundra, taiga, temperate forest, steppe, desert, savanna, tropical rainforest, mountains, ocean. Thresholds must be <b>soft</b>: blend the two nearest biomes by distance to the boundary, otherwise the map shows teeth. In a game, readability matters most — a player should recognise a biome by silhouette and palette in a second.",
            "Beyond climate, a biome defines <b>rules</b>: plants, monsters, resources, music. So biomes are usually stored as region tags rather than per-pixel colours. For large worlds use two levels: broad climate zones (Voronoi/low-frequency noise) and local variation inside them — that keeps forests from becoming spots.",
        ],
        formula=("T = T₀ − a·|lat| − Γ·h,   M = Σ sources · exp(−d/λ) + noise,   "
                 "biome = table(T, M)",
                 "Γ ≈ 6.5 °C/km is the standard lapse rate; λ is the moisture transport length (tens of kilometres). The Whittaker table is piecewise constant with soft borders."),
        steps=[
            "Generate heights and a water mask; compute latitude and altitude per cell.",
            "Compute temperature from latitude and altitude; add seasonal/noise variation.",
            "Compute moisture: water sources, wind transport, rain shadow, falloff.",
            "Classify with the table and blend neighbouring classes at the borders (dither/blend).",
            "Distribute resources, plants and spawns per biome; verify key biomes are reachable.",
        ],
        complexity=("O(W·H) per map", "O(W·H)",
                    "A 2048² map takes tens of milliseconds; moisture falloff can be done with a few blur passes."),
        code=("python", """def wind_shadow(heights, x, y, wind=(1, 0), reach=8):
    # 0 — cell is windward, 1 — deep rain shadow behind a ridge.
    H, W = len(heights), len(heights[0])
    h, shadow = heights[y][x], 0.0
    for d in range(1, reach + 1):
        sx, sy = int(x - wind[0] * d), int(y - wind[1] * d)
        if not (0 <= sx < W and 0 <= sy < H):
            break
        shadow = max(shadow, (heights[sy][sx] - h) * 2.2 / d)
    return max(0.0, min(1.0, shadow))

def temperature(lat, height, t0=30.0, lapse=6.5):
    # lat in degrees, height in km
    return t0 - abs(lat) * 0.55 - lapse * height

def moisture(water_distance, wind_shadow, noise=0.0, lam=12.0):
    import math
    return math.exp(-water_distance / lam) * (1 - 0.7 * wind_shadow) + noise

def biome(temp, moist):
    if temp < 0:            return "tundra"
    if temp < 8:            return "taiga"
    if moist < 0.2:         return "desert"
    if temp < 18:
        return "steppe" if moist < 0.45 else "temperate_forest"
    if moist < 0.3:         return "desert"
    if moist < 0.55:        return "savanna"
    return "tropical_rainforest"

def classify_grid(heights, water, lat_per_row, noise_fn):
    out = []
    for y, row in enumerate(heights):
        line = []
        for x, h in enumerate(row):
            t = temperature(lat_per_row(y), h)
            m = moisture(water[y][x], wind_shadow(heights, x, y), noise_fn(x, y))
            line.append("ocean" if h < 0.4 else biome(t, m))
        out.append(line)
    return out"""),
        pitfalls=[
            "Hard thresholds produce pixel borders and a biome checkerboard.",
            "Moisture from water distance alone ignores mountains: rainforest appears behind the ridge.",
            "A biome as colour without rules: trees and mobs disagree with the climate.",
            "Forgetting altitude zones — tropical forest on a 4 km peak.",
        ],
        games=["Minecraft", "Dwarf Fortress", "Valheim", "No Man's Sky"],
    ),
    dict(
        id="rivers",
        title="Rivers: flow direction, watersheds and channels",
        tags=["D8", "accumulation", "watershed", "lakes"],
        summary="A river is not a line but a consequence of relief. Give every cell a flow direction towards its lowest neighbour and accumulate area downstream — where accumulation is large, draw a river. That yields both channels and watershed borders.",
        detail=[
            "The <b>D8</b> algorithm picks the lowest of the eight neighbours per cell; if all are higher, the cell is a pit. Areas are then accumulated in topological order: <b>A(cell) = 1 + Σ A(upstream)</b>. High-accumulation cells are rivers, and width grows with the square root of the catchment area (a hydrological rule of thumb).",
            "D8 has artefacts: strict eight-way flow gives staircases and parallel lines. D-infinity distributes flow between two neighbours by angle, and priority-flood fills local pits so water never stalls. For game maps D8 + pit filling + light spline smoothing is enough.",
            "Rivers shape gameplay: natural borders, trade routes, water sources and bridge sites. Generate them early — before biomes and cities. If a river does not reach the sea, check pits and iteration order; if it meanders too much, reduce noise in the heightmap.",
        ],
        formula=("dir(c) = argmin_{n∈N8} h(n),   A(c) = 1 + Σ_{u→c} A(u),   "
                 "width ∝ √A,   stream if A > A_threshold",
                 "A is the catchment area in cells. A_threshold separates brooks from rivers; a river of width w needs A ∼ w²·const."),
        steps=[
            "Build a heightmap and a land/sea mask.",
            "Fill local pits (priority-flood) — otherwise rivers break.",
            "Choose a flow direction per cell towards the lowest neighbour (D8) or distribute by D∞.",
            "Sort cells by height and accumulate area downstream.",
            "Draw channels above the area threshold; smooth, add lakes in pits and bridges at narrow points.",
        ],
        complexity=("O(W·H log W·H) with sorting", "O(W·H)",
                    "A 1024² map takes tens of milliseconds; priority-flood parallelises by tiles."),
        code=("python", """import heapq

def fill_pits(h):
    \"\"\"Priority-flood: raise pits to the level of the nearest sea outlet.\"\"\"
    height, width = len(h), len(h[0])
    out = [row[:] for row in h]
    seen = [[False] * width for _ in range(height)]
    pq = []
    for y in range(height):
        for x in range(width):
            if x in (0, width - 1) or y in (0, height - 1):
                heapq.heappush(pq, (out[y][x], x, y))
                seen[y][x] = True
    while pq:
        z, x, y = heapq.heappop(pq)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not seen[ny][nx]:
                seen[ny][nx] = True
                out[ny][nx] = max(out[ny][nx], z + 1e-6)
                heapq.heappush(pq, (out[ny][nx], nx, ny))
    return out

def accumulate(h):
    height, width = len(h), len(h[0])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    downstream = [[None] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            best, best_h = None, h[y][x]
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and h[ny][nx] < best_h:
                    best, best_h = (nx, ny), h[ny][nx]
            downstream[y][x] = best
    order = sorted(((h[y][x], x, y) for y in range(height) for x in range(width)),
                   reverse=True)
    area = [[1] * width for _ in range(height)]
    for _, x, y in order:
        dst = downstream[y][x]
        if dst:
            nx, ny = dst
            area[ny][nx] += area[y][x]
    return area, downstream

# river mask: area[y][x] > 400; width = sqrt(area) * k"""),
        pitfalls=[
            "Not filling pits: rivers stop in random places and watersheds break.",
            "Accumulating in random order — areas are wrong; you need topological height order.",
            "Constant river width makes mountain brooks as wide as estuaries — use √A.",
            "Generating rivers after biomes and cities: water conflicts with relief and bridges.",
        ],
        games=["Minecraft", "Dwarf Fortress", "Valheim", "Horizon Zero Dawn"],
    ),
    dict(
        id="lsystem",
        title="L-systems: plants, cities and fractal patterns",
        tags=["grammar", "turtle graphics", "fractal", "plants"],
        summary="An L-system is a grammar that rewrites a string on every iteration. Turtle interpretation (F forward, +/− turn, [ ] branch) turns the string into a tree, a fern or a Hilbert curve. Five lines of code give endless variety.",
        detail=[
            "Axiom and rules: for example <b>X → F[+X][−X]FX</b>, <b>F → FF</b>. Symbol count grows exponentially, so depth 5–7 is the limit for interactive generation. The turtle reads the string: F steps, +/− turns, [ saves state, ] restores it. Thickness and colour can follow stack depth.",
            "Stochastic L-systems add variation by choosing rules with probabilities. Parametric L-systems carry numbers (angle, length) and can model real plants from botanical data. Context-sensitive rules look at neighbours — a full developmental grammar.",
            "Beyond plants, L-systems produce road networks (F street, + − turn), dungeons (branching and dead ends), circuit layouts and even music. The main limits are exponential growth and fractal monotony: without randomness and pruning, all trees look alike. Games usually generate 8–20 variants offline and randomise parameters.",
        ],
        formula=("ω = axiom,   ωₙ₊₁ = rewrite(ωₙ)   "
                 "F: move d, +: turn +δ, −: turn −δ, [ : push, ] : pop",
                 "String length grows as λⁿ, where λ is the spectral radius of the rule matrix. For binary rules (A→AB, B→A) it is the Fibonacci sequence."),
        steps=[
            "Define the axiom, alphabet (F, +, −, [, ]) and rewrite rules.",
            "Apply the rules n times (keep n ≤ 7 for interactivity); add probabilities if needed.",
            "Interpret the string with a turtle: step, turn, push/pop state.",
            "Tie thickness, colour and segment length to stack depth to get trunk and branches.",
            "Bake the result into a mesh/sprite and randomise parameters for variants.",
        ],
        complexity=("O(λⁿ) symbols, O(nodes) to draw", "O(λⁿ)",
                    "Depth 7 is tens of thousands of segments; go deeper only offline or on the GPU."),
        code=("python", """import math

def expand(axiom, rules, iterations=5):
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(ch, ch) for ch in s)
    return s

def turtle(s, angle=25.0, step=6.0):
    \"\"\"Return segments; state = (x, y, heading).\"\"\"
    x = y = 0.0
    heading = -math.pi / 2
    stack, segments = [], []
    for ch in s:
        if ch == "F":
            nx = x + math.cos(heading) * step
            ny = y + math.sin(heading) * step
            segments.append((x, y, nx, ny))
            x, y = nx, ny
        elif ch == "+":
            heading += math.radians(angle)
        elif ch == "-":
            heading -= math.radians(angle)
        elif ch == "[":
            stack.append((x, y, heading))
        elif ch == "]":
            x, y, heading = stack.pop()
    return segments

TREE = expand("X", {"X": "F[+X][-X]FX", "F": "FF"}, 5)
FERN = expand("X", {"X": "F[+X]F[-X]+X", "F": "FF"}, 6)

# Hilbert curve: A -> -BF+AFA+FB-,  B -> +AF-BFB-FA+,  F = draw"""),
        pitfalls=[
            "Too deep a recursion: strings grow exponentially and the browser freezes at n=10.",
            "Forgetting the [ ] stack — the whole tree collapses into one line.",
            "The same angle and length for every branch makes a plant look like a diagram.",
            "No scale normalisation: the tree leaves the screen or shrinks to a dot.",
        ],
        games=["Spore", "No Man's Sky", "Minecraft", "Dwarf Fortress"],
    ),
    dict(
        id="shapegrammar",
        title="Shape grammars: generative facades and interiors",
        tags=["split grammar", "facades", "rules", "LOD"],
        summary="A shape grammar does not place windows from a list — it splits a volume with rules until only terminals remain: walls, windows, doors, balconies. One box plus a set of ratios yields thousands of facades, and every one of them is built from whole parts.",
        detail=[
            "A shape starts as a labelled box (massing). A rule such as <b>S → Split('y', [0.55, 0.45]) { Floors }</b> divides it, while labels (floors, bays, window, wall, door) choose the next rule. Terminals are shapes that cannot or need not be split any further: they become meshes, sprites or tiles. This is how CGA split grammars work in CityEngine and how most production facade generators operate.",
            "Architecture comes from the order and probabilities of the rules. Massing first, then floors, then window bays, then details. Split ratios are sampled from a distribution (uniform or triangular) and <b>snapped to a module</b> — 3 m, for instance — otherwise windows drift and stop aligning between floors. A minimum size and a maximum depth cut the recursion: without them, 0.5+0.5 ratios eventually produce a zero-width window.",
            "Stiny's full shape grammar operates on shapes rather than strings and can produce interior plans: rooms as rectangles, doors as cut openings, furniture as terminals with placement rules. In practice it is combined with other tools: L-systems for ornament, WFC for interiors, a grammar for the shell. For a city, LOD is mandatory: nearby the recursion goes down to windows, far away it stops at the floor and swaps in a texture — otherwise a million terminals kill the frame.",
        ],
        formula=("S → Split(axis, [w₁ … wₙ]) { S₁ … Sₙ },   Σwᵢ = L,   wᵢ ≥ w_min,   terminal → Window | Wall | Door",
                 "A split preserves area and bounds, so parts never overlap. A stochastic choice of rules and ratios creates variants, while the minimum size guarantees that a terminal still makes sense."),
        steps=[
            "Describe the input box (width, height, depth) and the set of terminal labels.",
            "Write the rules: massing → floors → window bays → details; for each label, pick a split axis and limits.",
            "Sample ratios from a distribution, clamp them by the minimum size and snap them to the module (3 m, 0.5 m).",
            "Apply the rules recursively down to terminals; keep the tree and depth for LOD and debugging.",
            "Build meshes/sprites from terminals, cache them per style and randomise the seed for variants.",
        ],
        complexity=("O(T) terminals, T ≤ 2^depth", "O(T + depth)",
                    "Thousands of facades per second on the CPU; windows are instanced and distant levels are replaced by a texture."),
        code=("python", """import random

def split_grammar(width, height, seed=0, unit=1.0, max_depth=5):
    \"\"\"A facade as a split tree: terminals are (x, y, w, h, kind).\"\"\"
    rng = random.Random(seed)
    terminals = []

    def snap(frac, total):
        part = round(total * frac / unit) * unit
        part = min(max(part, 0.3 * total), 0.7 * total)
        return part / total

    def rec(x, y, w, h, depth):
        if depth >= max_depth or w < 3 * unit or h < 2 * unit:
            kind = "window" if w > 1.5 * unit and h > 1.2 * unit else "wall"
            terminals.append((x, y, w, h, kind))
            return
        if w > h * 1.15:                      # wide box: window bays
            f = snap(rng.uniform(0.35, 0.65), w)
            rec(x, y, w * f, h, depth + 1)
            rec(x + w * f, y, w * (1 - f), h, depth + 1)
        else:                                 # tall box: floors
            f = snap(rng.uniform(0.4, 0.6), h)
            rec(x, y, w, h * f, depth + 1)
            rec(x, y + h * f, w, h * (1 - f), depth + 1)

    rec(0.0, 0.0, width, height, 0)
    return terminals"""),
        pitfalls=[
            "No minimum size: on a small box the ratios produce zero-width windows and holes in the wall.",
            "Windows are not snapped to a module, so floors fail to line up and the facade drifts.",
            "The same split ratio at every level gives a rigid grid; add jitter and probabilities.",
            "Without LOD and caching, a city of tens of thousands of facades turns into millions of terminals.",
        ],
        games=["Cities: Skylines", "Cyberpunk 2077", "Marvel's Spider-Man", "No Man's Sky"],
    ),
    dict(
        id="items",
        title="Item generation: rarity, affixes and a stat budget",
        tags=["loot", "affixes", "rarity", "budget"],
        summary="A good item generator is a budget, not a list of random properties. An item has a level, a rarity and an affix pool; the total stat “cost” never exceeds the budget, so a legendary does not accidentally beat a mythic. The rest is taste and tables.",
        detail=[
            "Scheme: <b>itemLevel</b> sets base numbers, rarity sets the affix count and budget multiplier, the slot sets allowed affixes. Affix cost = (value / max value) · weight. The generator adds affixes until the budget is spent, then derives secondary stats (DPS, armour, resistance) from primary ones.",
            "Value spread is a separate decision. A uniform distribution produces many near-max rolls and devalues perfect ones; use a <b>triangular</b> or beta distribution with a 60–70 % mean. Add pity counters and PRD (see crits) against bad luck, and smart loot for seasonal items: a higher chance of affixes useful to the current class.",
            "Item names come from a template: base + prefix + suffix (“Rusted Blade of Storms”). Variety matters, but so does <b>readability</b>: the player must grasp what an item does in a second. Group affixes by meaning, and give legendaries unique effects that do not fit the budget and are balanced by hand.",
        ],
        formula=("budget = base(ilvl) · rarityMult,   "
                 "Σ cost(affix) ≤ budget,   "
                 "value = min + (max − min) · Beta(2,2)",
                 "Beta(2,2) is a triangular distribution with mean 0.5; a “generous” loot table uses Beta(3,2). cost = (value − min)/(max − min) · weight."),
        steps=[
            "Define levels, rarities, slots and an affix table with weights and ranges.",
            "Pick a base and a rarity; compute the budget and affix count.",
            "Draw affixes without duplicates until the budget is spent; roll values from the distribution.",
            "Recompute derived stats and assemble the name from templates.",
            "Validate: no budget overshoot, affixes allowed for the slot, no duplicate names.",
        ],
        complexity=("O(affixes) per item", "O(pool)",
                    "Millions of server-side rolls take seconds; the expensive part is balance simulation, not generation."),
        code=("python", """import random

AFFIXES = {
    "damage":     dict(cost=1.0, rng=(4, 12),  tags=("weapon",)),
    "crit":       dict(cost=1.4, rng=(2, 8),   tags=("weapon", "ring")),
    "life":       dict(cost=1.1, rng=(10, 40), tags=("armor", "ring")),
    "resist":     dict(cost=0.8, rng=(3, 15),  tags=("armor", "ring")),
    "attack_spd": dict(cost=1.6, rng=(3, 9),   tags=("weapon",)),
    "movement":   dict(cost=0.6, rng=(2, 8),   tags=("armor",)),
}
RARITY = {"common": (1, 1.0), "rare": (2, 1.35),
          "epic": (3, 1.7), "legendary": (4, 2.1)}

def roll_item(ilvl, slot, rarity, rng=random):
    count, mult = RARITY[rarity]
    budget = (6 + ilvl * 1.6) * mult
    pool = [k for k, a in AFFIXES.items() if slot in a["tags"]]
    rng.shuffle(pool)
    chosen, spent = [], 0.0
    for key in pool:
        if len(chosen) >= count:
            break
        a = AFFIXES[key]
        frac = rng.betavariate(2, 2)            # 0..1, mean 0.5
        lo, hi = a["rng"]
        value = int(round(lo + (hi - lo) * frac))
        cost = frac * a["cost"] * 3.0
        if spent + cost > budget and chosen:
            continue
        spent += cost
        chosen.append((key, value))
    return {"slot": slot, "ilvl": ilvl, "rarity": rarity,
            "power": round(spent / budget, 2), "affixes": chosen}

# roll_item(60, "weapon", "legendary")"""),
        pitfalls=[
            "Stacking random affixes without a budget produces god rolls that break the economy.",
            "Uniform values devalue high rolls and players stop caring about them.",
            "Affixes that do not fit the slot (attack speed on boots) break trust.",
            "A name that does not reflect power: a legendary sounds like trash and gets skipped.",
        ],
        games=["Diablo IV", "Path of Exile", "Borderlands", "Destiny 2"],
    ),
    dict(
        id="names",
        title="Name generation: syllable grammar and Markov chains",
        tags=["Markov", "syllables", "phonotactics", "naming"],
        summary="Names are generated in two ways: assembled from syllables by rules (CVC, CV-CV) or learned with a Markov chain from a corpus. The first controls the sound, the second captures a national flavour. Both need uniqueness and pronounceability.",
        detail=[
            "A syllable grammar is a template: <b>CV-CVC</b> gives “Ka-lor”, <b>CVC-V</b> gives “Tar-na”. Consonant and vowel sets define the language: many sibilants sound “orcish”, many liquids sound “elven”. Phonotactic rules forbid awkward clusters like “ktl” and repeated identical syllables.",
            "A Markov chain of order 2–3 learns from a name corpus and generates new ones: <b>P(next | previous two)</b>. It captures typical endings and beginnings but may produce unreadable output, so add a filter: length, forbidden combinations, duplicates. The higher the order, the closer to the original and the less novelty.",
            "For a world with a map, names must be <b>consistent</b>: toponyms of one region share roots and suffixes (-heim, -gard). So generate a language, not strings: roots, word-formation rules and a dictionary. And check locales: a name must be pronounceable and free of unpleasant associations in players' languages.",
        ],
        formula=("P(wₜ | wₜ₋₁) = count(wₜ₋₁, wₜ) / count(wₜ₋₁),   "
                 "syllable = Onset + Nucleus + (Coda)",
                 "For order n the state is the previous n characters or syllables. Add-k smoothing prevents zero probabilities on rare transitions."),
        steps=[
            "Collect a corpus in the target style or define syllable sets (onset/nucleus/coda).",
            "Build a transition table (Markov) or assembly rules (syllables).",
            "Generate N candidates; filter by length, pronounceability and duplicates.",
            "Add gender endings and suffixes for classes and regions.",
            "Check names for unwanted associations and keep a dictionary for consistency.",
        ],
        complexity=("O(length) per name, O(corpus) to train", "O(transitions)",
                    "Thousands of names take milliseconds; training on a 10k corpus is one pass."),
        code=("python", """import collections, random

def train(names, order=2):
    model = collections.defaultdict(collections.Counter)
    for name in names:
        padded = "^" * order + name.lower() + "$"
        for i in range(len(padded) - order):
            state = padded[i:i + order]
            model[state][padded[i + order]] += 1
    return model

def generate(model, order=2, rng=random, max_len=12):
    state = "^" * order
    out = []
    for _ in range(max_len * 2):
        nxt = model.get(state)
        if not nxt:
            break
        chars, weights = zip(*nxt.items())
        ch = rng.choices(chars, weights)[0]
        if ch == "$":
            break
        out.append(ch)
        state = (state + ch)[-order:]
    name = "".join(out).capitalize()
    return name or None

CORPUS = ["aldric", "bran", "cassia", "dorian", "eira", "fenrir",
          "gwen", "hadrian", "isolde", "jorunn", "kael", "lyra"]
model = train(CORPUS, order=2)
names = {generate(model, 2, random) for _ in range(50)} - {None}

# syllables: "ka" + "lor" + "en" -> Kaloren; keep roots per region"""),
        pitfalls=[
            "Order-1 Markov gives word salad: “aelri” instead of a name.",
            "No uniqueness filter — a world ends up with two “Kaslan” with different fates.",
            "Syllables without phonotactics produce “Ktlrmn”, which nobody can say.",
            "Inconsistent regional names: “Tar-Vorn” living next to “Jennifer”.",
        ],
        games=["Dwarf Fortress", "No Man's Sky", "Caves of Qud", "Elite Dangerous"],
    ),
    dict(
        id="quests",
        title="Quests and mission graphs: keys, doors and pacing",
        tags=["mission graph", "lock-and-key", "grammar", "solvability"],
        summary="A quest is a graph: nodes are tasks, edges are dependencies. The generator builds “get key → open door → reach goal” chains and verifies that every lock opens before it is met. That is how Zelda-style dungeons and Diablo-style contracts are made.",
        detail=[
            "Basic grammar: <b>chain</b> (A→B→C), <b>lock-key</b> (key K opens door L), <b>branch</b> (Y-fork), <b>loop</b> (return). Combining them yields a mission graph with a critical path and optional branches. Joris Dormans formalised this as a grammar with unrealised nodes: the generator “grows” the graph until no open tasks remain.",
            "The key property is <b>solvability</b>: for every door there must be a key reachable without it. Verification is a BFS over states: (keys collected, doors opened). Additionally constrain critical-path length (10–20 minutes), branch count (2–4) and reward density, or the quest becomes “fetch 10 hides”.",
            "Procedural quests get boring when only the objectives change. What works is <b>context and characters</b>: who asks, why, what happens on refusal. So the generator should emit a structure with actors, place and stakes, and compose text from templates with substitutions. Always check conflicts: two quests must not need the same NPC in two places at once.",
        ],
        formula=("V = tasks, E = dependencies,   "
                 "solvable ⇔ ∀ lock L ∃ key K: K reachable before L,   "
                 "critical path ≤ T_max",
                 "The traversal state is a key bitmask. Branching b and depth d give b^d leaves; 2–4 branches over 3–5 levels feels comfortable."),
        steps=[
            "Define the grammar: node types (kill, fetch, escort, explore) and connectors (chain, lock-key, branch).",
            "Generate the graph from the final goal backwards, expanding prerequisites.",
            "Verify solvability with a state-space BFS (keys → doors).",
            "Cap the critical path and branch count; drop unreachable and empty nodes.",
            "Bind nodes to places and NPCs, generate text from templates and check conflicts.",
        ],
        complexity=("O(V + E) to verify, exponential in keys", "O(V + E)",
                    "A 30-node graph verifies instantly; for thousands of quests cache templates and validation."),
        code=("python", """import random

def build_quest_chain(depth=4, rng=random):
    \"\"\"Task chain with keys: every door is opened by a key from an earlier step.\"\"\"
    nodes, edges = [], []
    start = {"id": 0, "type": "start", "text": "Take the contract"}
    nodes.append(start)
    prev = 0
    nid = 1
    for step in range(depth):
        kind = rng.choice(["kill", "fetch", "escort", "explore"])
        task = {"id": nid, "type": kind, "requires": [prev]}
        nodes.append(task)
        edges.append((prev, nid))
        prev = nid
        nid += 1
        if step < depth - 1 and rng.random() < 0.5:
            key = {"id": nid, "type": "key"}
            door = {"id": nid + 1, "type": "door", "requires": [key["id"]]}
            nodes += [key, door]
            edges += [(prev, key["id"]), (key["id"], door["id"])]
            prev = door["id"]
            nid += 2
    goal = {"id": nid, "type": "goal", "requires": [prev]}
    nodes.append(goal)
    edges.append((prev, goal["id"]))
    return nodes, edges

def is_solvable(nodes, edges, start=0):
    \"\"\"BFS over states (sets of completed tasks).\"\"\"
    req = {n["id"]: set(n.get("requires", [])) for n in nodes}
    frontier, seen = [frozenset()], {frozenset()}
    goal = max(req)
    while frontier:
        done = frontier.pop()
        if goal in done:
            return True
        for n in nodes:
            if n["id"] in done or not req[n["id"]] <= done:
                continue
            nxt = frozenset(done | {n["id"]})
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return False"""),
        pitfalls=[
            "Generating doors without keys — the level is unsolvable and playtesting finds out.",
            "A critical path that is too long: 40 identical tasks in a row.",
            "Template text without actors or place: the quest is forgettable.",
            "Not checking conflicts between simultaneous quests that share an NPC.",
        ],
        games=["The Legend of Zelda", "The Binding of Isaac", "Hades", "Diablo"],
    ),
    dict(
        id="director",
        title="The AI director: a tension curve and enemy waves",
        tags=["AI director", "pacing", "dynamic difficulty", "waves"],
        summary="A director generates not content but experience: it decides when to grant a breather and when to stage a siege. It follows a target tension curve, computes a threat budget and reacts to player state — health, ammo, skill, time since the last fight.",
        detail=[
            "Tension <b>I(t)</b> is a target curve authored by designers: rise, climax, release. The director measures actual tension (damage, enemy count, pace) and moves the spawn budget to catch up. Left 4 Dead is the classic example: quiet periods, waves, final sieges and special infected spawning out of sight.",
            "The key to avoiding a “rubber-band” feel is <b>asymmetry</b>. The director may increase pressure after success but must not punish a death instantly. The player should see cause and effect: silence, sound, appearance. Hidden damage tweaks annoy far more than honest waves.",
            "Implementation is a controller: error e = I_target − I_actual, budget B += k·e, with limits and cooldowns. Add rules: never spawn in view, grant 20–40 seconds of quiet after a hard fight, do not spawn a tank if the player has no heavy weapon. And log decisions — without telemetry such a director cannot be tuned.",
        ],
        formula=("e = I_target − I_actual,   B ← clamp(B + k·e, B_min, B_max),   "
                 "spawn when cooldown = 0 ∧ B ≥ cost",
                 "I is normalised tension [0,1]. B is a “threat point” budget; enemy cost depends on type. k is the reaction rate (0.05–0.2 per tick)."),
        steps=[
            "Define tension metrics: damage per second, enemy count, distance, player resources.",
            "Author a target curve per level phase and a threat budget.",
            "Implement the controller: error → budget change with limits and hysteresis.",
            "Add safety rules: never behind the player, never in view, cooldowns, rest after fights.",
            "Log decisions and tune in playtests; verify the player understands why it got harder.",
        ],
        complexity=("O(1) per tick", "O(active spawns)",
                    "Computation is negligible; the difficulty is in rule design and telemetry, not code."),
        code=("python", """import math

class Director:
    def __init__(self, budget=0.0):
        self.intensity = 0.0      # measured 0..1
        self.budget = budget
        self.cooldown = 0.0
        self.phase = 0.0

    def target(self, t):
        # two build-ups and a climax, then breathing room
        return 0.35 + 0.45 * math.sin(t * 0.5) ** 2

    def tick(self, dt, measured_intensity, player_hp):
        self.intensity += (measured_intensity - self.intensity) * min(1, dt * 2)
        self.phase += dt
        goal = self.target(self.phase)
        if player_hp < 0.25:
            goal *= 0.5           # mercy rule
        err = goal - self.intensity
        self.budget = max(0.0, min(10.0, self.budget + err * 1.2 * dt))
        self.cooldown = max(0.0, self.cooldown - dt)

    def request_spawn(self, cost=1.0):
        if self.cooldown <= 0 and self.budget >= cost:
            self.budget -= cost
            self.cooldown = 1.2
            return True
        return False

# d.tick(dt=0.016, measured_intensity=0.7, player_hp=0.8)
# if d.request_spawn(1.0) and not visible_to_player(pos): spawn()"""),
        pitfalls=[
            "Secretly tweaking damage and HP instead of honestly changing enemy counts.",
            "Spawning behind the player or in view — players read that as cheating.",
            "Punishing a death immediately: a breather is needed after respawn.",
            "No telemetry — the director “works” but nobody knows whether it meets the curve.",
        ],
        games=["Left 4 Dead", "Alien: Isolation", "Deep Rock Galactic", "Back 4 Blood"],
    ),
]
