# -*- coding: utf-8 -*-
"""Part II, layers 01–02 (English): noise, sampling, layout. Topics 67–77."""

TOPICS_EN_PG_A = [
    dict(
        id="noise",
        title="Gradient noise: value, Perlin and simplex",
        tags=["value noise", "Perlin", "simplex", "fBm"],
        summary="Noise is a deterministic “random” function of coordinates: the same input always returns the same number, and nearby points return similar values. Perlin and simplex interpolate gradients rather than values, so the result looks organic and shows no square grid.",
        detail=[
            "Value noise throws a random number into each lattice node and interpolates smoothly. It is cheap but gives a “pillowy” look, because every extremum sits on a node. <b>Perlin noise</b> stores a random <i>gradient</i> per node and projects the vector to the sample onto it; the dot product is zero at the nodes, so the field is smooth without a visible lattice. <b>Simplex</b> does the same on simplices (triangles) and costs O(N²) instead of O(2ᴺ) per sample — hence its popularity in 3D and 4D.",
            "A single octave carries one scale of detail. The fractal sum <b>fBm</b> adds octaves with doubled frequency and decaying amplitude: large shapes become continents, small ones become rocks and grass. The amplitude ratio is called gain (usually 0.5), the frequency ratio lacunarity (usually 2.0). Domain warping — feeding noise into the coordinates of another noise — turns soft hills into jagged ridges and swirls.",
            "For GPU noise, seamlessness matters: hash integer coordinates instead of sampling an array, so the texture tiles with the right period. For an infinite world, sample in world units rather than pixels, otherwise the pattern swims when the scale changes. And remember: noise is a field, not randomness; scattering objects needs Poisson sampling, not a noise threshold.",
        ],
        formula=("fBm(p) = Σᵢ₌₀ⁿ⁻¹ gainⁱ · noise(2ⁱ · lacunarity · p + offsetᵢ),   "
                 "Perlin(p) = Σ grad(hash(c)) · fade(p − c)",
                 "fade(t) = 6t⁵ − 15t⁴ + 10t³ is the quintic smoothing curve: its first and second derivatives vanish at cell borders, so the grid is invisible. gain controls roughness, lacunarity controls detail density."),
        steps=[
            "Build an integer hash of (x, y, seed) with a good avalanche — without it you get visible diagonals.",
            "For value noise, take four corner hashes and blend them with the quintic fade.",
            "For Perlin, take eight corner gradients and sum their dot products with the vectors to the sample.",
            "Sum octaves: frequency ×2, amplitude ×0.5, new offset per octave, then normalise by the amplitude sum.",
            "Add domain warping and a ridge function (1 − |n|) for mountains; profile on your target grid size.",
        ],
        complexity=("O(octaves) per sample, 4 hashes per octave", "O(1)",
                    "A 512×512 2D tile with 6 octaves takes milliseconds on the CPU; on the GPU it is a shader over millions of samples."),
        code=("python", """import math

def hash2(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def value_noise(x, y, seed):
    xi, yi = math.floor(x), math.floor(y)
    xf, yf = x - xi, y - yi
    u, v = fade(xf), fade(yf)
    a = hash2(xi,     yi,     seed)
    b = hash2(xi + 1, yi,     seed)
    c = hash2(xi,     yi + 1, seed)
    d = hash2(xi + 1, yi + 1, seed)
    return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v

def fbm(x, y, seed, octaves=6, gain=0.5, lacunarity=2.0):
    total = norm = 0.0
    amp, freq = 1.0, 1.0
    for i in range(octaves):
        total += amp * value_noise(x * freq, y * freq, seed + i * 1013)
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / norm          # always in [0, 1]

# h = fbm(wx * 0.008, wy * 0.008, seed=1337, octaves=6)"""),
        pitfalls=[
            "A weak hash (e.g. `(x*37+y) % 1000`) produces diagonal bands and repeating islands.",
            "Mixing octaves without normalisation pushes values outside [0,1] and breaks sea level.",
            "Unfiltered high frequencies shimmer in the distance — use mips/LOD or drop small octaves.",
            "One Perlin octave looks like soap: without fBm and domain warping it reads as noise, not landscape.",
        ],
        games=["Minecraft", "No Man's Sky", "Valheim", "Terragen"],
    ),
    dict(
        id="worley",
        title="Worley (cellular) noise: F1, F2 and borders",
        tags=["Voronoi", "cellular noise", "F2−F1", "feature points"],
        summary="Scatter feature points across the plane and, for every cell, find the distances to the two nearest ones. F1 gives a rocky texture, F2−F1 gives thin cell borders, and together they produce cracks, scales, foam and Voronoi partitions.",
        detail=[
            "Cellular noise is not interpolation but <b>nearest-neighbour search</b>. Space is divided into lattice cells, each holding one feature point at a random offset. Finding the nearest point takes only the 3×3 surrounding cells (27 in 3D), because nothing farther can reach. Hence O(1) per sample regardless of world size.",
            "The difference <b>F2 − F1</b> is zero on the border between two cells and grows towards the centre — a ready-made contour for stone seams, dragon scales or sea foam. <b>F1</b> gives convex bumps; the distance to the nearest feature centre gives pebbles and spheres. Summing a few octaves of Worley yields convincing rock that never repeats.",
            "The same algorithm is the Voronoi diagram: feature points become region centres. Apply Lloyd relaxation (move each point to the centroid) and the regions even out in area — that is how strategy territories, biomes and honeycombs are generated. For exact region borders you need explicit neighbour traversal; F2−F1 is only an approximation.",
        ],
        formula=("F1(p) = minᵢ |p − cᵢ|,   F2(p) = min₂ᵢ |p − cᵢ|,   border(p) = F2(p) − F1(p)",
                 "cᵢ are the feature points; each lattice cell stores c = cell + hash(cell)·jitter. Voronoi borders are the set of points where F2 = F1."),
        steps=[
            "Tile the plane; deterministically place one jittered point per cell.",
            "For a sample p, walk the 3×3 neighbouring cells and keep the two smallest distances.",
            "Use F1 for bumps, F2−F1 for cracks and F1·F2 for cells; normalise to your range.",
            "Add octaves: fine Worley for rocks, coarse Worley for continents and regions.",
            "For region maps, keep the feature points — they become capitals, biomes and graph nodes.",
        ],
        complexity=("O(1) per sample (9 or 27 cells)", "O(cells) for region maps",
                    "In 3D that is 27 checks per sample; for large regions store points separately and build Delaunay."),
        code=("python", """import math

def hash2(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF

def feature(cx, cy, seed):
    # keep the point at 0.15..0.85 so cells never collapse
    return (cx + 0.15 + 0.7 * hash2(cx, cy, seed),
            cy + 0.15 + 0.7 * hash2(cx, cy, seed + 7919))

def worley(x, y, seed):
    cx, cy = math.floor(x), math.floor(y)
    f1 = f2 = 1e9
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            fx, fy = feature(cx + ox, cy + oy, seed)
            d = math.hypot(fx - x, fy - y)
            if d < f1:
                f2, f1 = f1, d
            elif d < f2:
                f2 = d
    return f1, f2

# rock: 1 - F1, cracks: F2 - F1, regions: index of the nearest cell"""),
        pitfalls=[
            "Checking only your own cell: the nearest point almost always lies in a neighbour.",
            "Forgetting the jitter and getting a perfect grid instead of organic cells.",
            "F2−F1 without normalisation gives near-black borders — use a narrow smoothstep band.",
            "For regions, comparing distances is not enough: you need shared borders (half-edge/Delaunay), or the map tears on diagonals.",
        ],
        games=["Minecraft", "Noita", "Deep Rock Galactic", "RimWorld"],
    ),
    dict(
        id="poisson",
        title="Poisson disk sampling and blue noise",
        tags=["Bridson", "blue noise", "spatial hash", "scattering"],
        summary="White noise clumps: two trees can grow on top of each other while a bare patch sits next to them. Poisson disk sampling guarantees a minimum distance r without collapsing into a grid — the best way to scatter grass, rocks, enemies and points of interest.",
        detail=[
            "The goal: pick points so that no two are closer than <b>r</b> and no room is left for another. Brute force is O(N²). <b>Bridson's</b> algorithm keeps an active list and tries k candidates in the annulus [r, 2r] for each; neighbour checks go through a spatial grid with cell size r/√2, which holds at most one point, making the check local.",
            "The result is <b>blue noise</b>: a spectrum with suppressed low frequencies. The eye reads such a distribution as natural, not as rows or clumps. Expected density is about 0.7 of circle packing, roughly one point per 1.4·r² of area — handy for estimating grass per hectare.",
            "For infinite worlds you do not need global Poisson: generate each chunk independently but account for the ring of neighbouring chunks, otherwise borders get duplicates and gaps. Alternatives: jittered grid (fast, visible rows), void-and-cluster and energy relaxation (slow, perfect), progressive Poisson (for streaming).",
        ],
        formula=("|pᵢ − pⱼ| ≥ r,   cell = r / √2,   E[N] ≈ 0.7 · A / r²",
                 "A cell of r/√2 guarantees at most one point per cell (its diagonal is exactly r). The active list makes Bridson O(N) on average; k = 30 is a typical constant."),
        steps=[
            "Create a grid with cell r/√2; keep an active list and one seed point.",
            "While the list is non-empty: pick a random active point and generate k candidates in [r, 2r].",
            "Reject candidates closer than r to any point in the 3×3 neighbouring cells.",
            "Add the first valid candidate to the grid and the active list; after k failures remove the point from the list.",
            "For chunks, generate with a ring of neighbours and clip to the border; in 3D use cells of r/√3.",
        ],
        complexity=("O(N) average, O(k) candidates per point", "O(N) + grid",
                    "10,000 points take milliseconds on the CPU; on the GPU use progressive Poisson or a blue-noise texture."),
        code=("python", """import math, random

def poisson_disk(width, height, r, k=30, rng=random):
    cell = r / math.sqrt(2)
    gw, gh = int(width / cell) + 1, int(height / cell) + 1
    grid = [None] * (gw * gh)
    pts, active = [], []

    def add(x, y):
        grid[int(y / cell) * gw + int(x / cell)] = (x, y)
        pts.append((x, y))
        active.append(len(pts) - 1)

    add(width / 2, height / 2)
    while active:
        idx = rng.randrange(len(active))
        x, y = pts[active[idx]]
        placed = False
        for _ in range(k):
            a = rng.random() * math.tau
            d = r * (1 + rng.random())
            nx, ny = x + math.cos(a) * d, y + math.sin(a) * d
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            gx, gy = int(nx / cell), int(ny / cell)
            ok = True
            for oy in (-2, -1, 0, 1, 2):
                for ox in (-2, -1, 0, 1, 2):
                    cx, cy = gx + ox, gy + oy
                    if not (0 <= cx < gw and 0 <= cy < gh):
                        continue
                    q = grid[cy * gw + cx]
                    if q and (q[0] - nx) ** 2 + (q[1] - ny) ** 2 < r * r:
                        ok = False
            if ok:
                add(nx, ny)
                placed = True
                break
        if not placed:
            active.pop(idx)
    return pts"""),
        pitfalls=[
            "Using cell size r instead of r/√2 requires more neighbour checks and easily misses a conflict.",
            "Candidates only in [r, 2r]: farther than 2r another active point would already have found the spot.",
            "Independent chunk generation without neighbours produces seams and duplicates.",
            "Poisson does not respect importance: add density masks for grass and trees (rivers, roads, biomes).",
        ],
        games=["Horizon Zero Dawn", "Ghost of Tsushima", "The Elder Scrolls V: Skyrim", "No Man's Sky"],
    ),
    dict(
        id="seeds",
        title="Seeds, hashing and reproducible generation",
        tags=["PRNG", "PCG", "coordinate hash", "determinism"],
        summary="Procedural generation must repeat: one seed, one world. That needs a PRNG with explicit state, a hash of coordinates instead of a shared stream, and a fixed iteration order. A mistake here costs more than bad noise, because the world cannot be reloaded.",
        detail=[
            "A global `random()` is a shared stream: change the call order and the whole world changes. The reliable pattern is a <b>pure function</b> of coordinates: `hash(seed, chunkX, chunkY, index)`. A hash such as PCG or splitmix64 mixes bits so that neighbouring inputs give completely different outputs (avalanche), and the result does not depend on traversal order.",
            "Seed hierarchy: world → region → chunk → object. A chunk seed is derived from the world seed and the coordinates, not from a counter — then chunk #1000 can be generated without creating the previous 999. Give every subsystem a domain (terrain, loot, names), or editing one system reshuffles all the others.",
            "What breaks determinism: unstable sorting, `dict` iteration before Python 3.7, thread order, differing float precision across platforms, time, and unseeded `random`. The rule: generate data in a fixed order and store only the seed, not the result; for networked games also pin the generator version.",
        ],
        formula=("state ← mix(state + 0x9E3779B97F4A7C15);   "
                 "h = xorshift(mul(x ^ (x >> 33), 0xFF51AFD7ED558CCD) ^ seed)",
                 "splitmix64/PCG have an avalanche effect: flipping one input bit changes about half the output bits. For coordinates: h = hash(hash(seed) ^ hash(x) ^ hash(y))."),
        steps=[
            "Keep one 64-bit world seed plus an explicit domain per subsystem.",
            "Implement hash(seed, x, y, i) without global state; test avalanche on neighbouring inputs.",
            "Derive chunk/region seeds from coordinates, never from generation order.",
            "Generate in a fixed order: sort by (y, x), use lists instead of maps, no threads on shared state.",
            "Store the generator version with the save; migrate existing chunks when the algorithm changes.",
        ],
        complexity=("O(1) per value", "O(1) per chunk",
                    "One hash is nanoseconds; the real task is keeping state out of frames and platforms."),
        code=("python", """MASK = 0xFFFFFFFFFFFFFFFF

def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & MASK
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)

def hash_coords(seed, x, y, domain=0):
    h = seed & MASK
    h = splitmix64(h ^ (x * 0xD6E8FEB86659FD93 & MASK))
    h = splitmix64(h ^ (y * 0xA5A3564E27F8862F & MASK))
    h = splitmix64(h ^ (domain * 0x9E3779B97F4A7C15 & MASK))
    return h

def rng_for(seed, x, y, domain=0):
    state = hash_coords(seed, x, y, domain)
    def nxt():
        nonlocal state
        state = (state + 0x9E3779B97F4A7C15) & MASK
        return splitmix64(state) / 2 ** 64
    return nxt

# r = rng_for(1337, chunk_x, chunk_y, domain=1)   # loot"""),
        pitfalls=[
            "Calling `random.seed()` globally and later depending on call order.",
            "Deriving the next object's seed from the previous one: you cannot jump into the middle of the world.",
            "Not separating domains — a loot tweak changes the terrain.",
            "Trusting float determinism across platforms: networked games need fixed-point and a version tag.",
        ],
        games=["Minecraft", "Dwarf Fortress", "Caves of Qud", "No Man's Sky"],
    ),
    dict(
        id="diamondsquare",
        title="Diamond-square and midpoint displacement",
        tags=["fractal", "heightmap", "roughness", "1/f"],
        summary="The classic fractal generator: split a square, put the average of its corners plus random displacement in the centre, then split the diamonds again. Cheap, simple and still useful for clouds, islands and heightmaps.",
        detail=[
            "Start with a square (ideally 2ⁿ+1) with four known corners. In the <b>diamond step</b> the centre gets the average of the corners plus noise; in the <b>square step</b> edge midpoints get the average of the two corners and the centre. Recursion halves the step until single cells remain.",
            "The noise amplitude is multiplied each level by <b>roughness</b> (usually 0.5–0.7). This yields a 1/f spectrum: large shapes dominate and small ones add detail. At roughness → 1 you get white noise and spikes; at 0.3, nearly smooth hills. The 2ⁿ+1 grid is not pedantry: otherwise levels do not line up.",
            "Main drawbacks: lattice artefacts (visible crosses and repetition), fixed size and no seamlessness. For infinite worlds fBm is better, but diamond-square shines as a quick prototype, for cumulus clouds and for old-school sea-level maps. A wrap-around variant makes the texture tile.",
        ],
        formula=("h(c) = ¼·Σ h(corners) + N(0, σ²),   σₖ = σ₀ · roughnessᵏ",
                 "σₖ is the amplitude at level k. Expected fractal dimension relates to roughness: at 0.5 the surface is close to Brownian (H ≈ 1)."),
        steps=[
            "Pick a 2ⁿ+1 grid and set the four corners (e.g. zeros for an island).",
            "Diamond: centre of each square = average of corners + random offset σ.",
            "Square: edge midpoints = average of two corners and the centre + offset σ.",
            "Halve the step and multiply the amplitude by roughness; repeat down to 1×1 cells.",
            "Normalise heights, apply a distribution curve and map colours/normals.",
        ],
        complexity=("O(n²) per grid", "O(n²)",
                    "A 1025×1025 grid takes milliseconds; use the wrap variant for tiling."),
        code=("python", """import random

def diamond_square(size=129, roughness=0.55, seed=0, lo=0.0, hi=1.0):
    assert (size - 1) & (size - 2) == 0, "size must be 2^n + 1"
    rng = random.Random(seed)
    h = [[0.0] * size for _ in range(size)]
    h[0][0] = h[0][-1] = h[-1][0] = h[-1][-1] = (lo + hi) / 2
    step, amp = size - 1, (hi - lo)
    while step > 1:
        half = step // 2
        # diamond step
        for y in range(0, size - 1, step):
            for x in range(0, size - 1, step):
                avg = (h[y][x] + h[y][x + step] +
                       h[y + step][x] + h[y + step][x + step]) / 4
                h[y + half][x + half] = avg + (rng.random() * 2 - 1) * amp
        # square step
        for y in range(0, size, half):
            for x in range((y + half) % step, size, step):
                s = n = 0
                for dx, dy in ((half, 0), (-half, 0), (0, half), (0, -half)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < size and 0 <= yy < size:
                        s += h[yy][xx]; n += 1
                h[y][x] = s / n + (rng.random() * 2 - 1) * amp
        step = half
        amp *= roughness
    return h"""),
        pitfalls=[
            "A size other than 2ⁿ+1 leaves seams and holes between levels.",
            "Constant amplitude instead of decay gives white noise that looks like sandpaper.",
            "Without wrap mode the texture does not tile and chunk borders show.",
            "Diamond-square cannot sample arbitrary coordinates: use fBm/simplex for infinite worlds.",
        ],
        games=["The Elder Scrolls II: Daggerfall", "Warcraft II", "Populous"],
    ),
    dict(
        id="caves",
        title="Cellular automata caves",
        tags=["cellular automata", "4-5 rule", "connectivity", "caves"],
        summary="Fill a grid with random noise and apply one rule a few times: a cell becomes a wall if too many neighbours are walls. After 4–6 iterations the TV static turns into connected, organic caves.",
        detail=[
            "The classic <b>4-5</b> rule: a cell stays a wall if at least 5 of its 8 neighbours are walls (or exactly 4 with the death variant); otherwise it becomes floor. Start at roughly 45 % wall probability — the percolation threshold, where structure is most interesting. Five iterations usually suffice; ten smooths everything into big halls.",
            "The result almost always needs <b>repair</b>: flood-fill the connected components, keep the largest and fill or tunnel the rest. Always add a wall border, otherwise the map edge opens and generation leaks out. The same automata give water and lava with different rules (4-5 for water produces puddles).",
            "Cellular automata guarantee nothing: no rooms, no rhythm, no guaranteed path. Their strength is speed and organic shapes; their place is cave biomes, caverns and raw levels. For room-based dungeons use BSP, for connected layouts use WFC, and keep automata as a mask for natural halls.",
        ],
        formula=("x′ = wall  ⟺  Σ neighbours(wall) ≥ 5  (8-neighbourhood)",
                 "Initial density p₀ ≈ 0.45; iterations 4–6. The 4-5 rule allows variants: ≥5 wall, exactly 4 wall, otherwise floor."),
        steps=[
            "Create a W×H grid and fill walls with probability 0.45 (the border is always wall).",
            "Count the 8 neighbours of every cell, apply the 4-5 rule into a fresh buffer.",
            "Repeat 4–6 times; check that floor coverage is 35–55 %.",
            "Flood-fill the components; keep the largest and fill the rest.",
            "Place entrance/exit on far-apart floor cells, verify an A* path and decorate dead ends.",
        ],
        complexity=("O(iterations · W · H)", "O(W · H)",
                    "256×256 over 5 iterations takes milliseconds; on the GPU it is a shader or compute pass."),
        code=("python", """import random

def cave(width=64, height=40, fill=0.45, steps=5, seed=0):
    rng = random.Random(seed)
    g = [[1] * width for _ in range(height)]
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            g[y][x] = 1 if rng.random() < fill else 0

    def neighbours(x, y):
        return sum(g[y + dy][x + dx]
                   for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dx, dy) != (0, 0))

    for _ in range(steps):
        nxt = [row[:] for row in g]
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                n = neighbours(x, y)
                nxt[y][x] = 1 if n >= 5 or (n == 4 and g[y][x]) else 0
        g = nxt
    return g

def largest_component(g):
    h, w = len(g), len(g[0])
    seen, best = set(), []
    for y in range(h):
        for x in range(w):
            if g[y][x] or (x, y) in seen:
                continue
            stack, comp = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and not g[ny][nx] \\
                            and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            if len(comp) > len(best):
                best = comp
    return set(best)"""),
        pitfalls=[
            "Too low an initial density shatters the caves; too high leaves rare burrows.",
            "No wall border — the map edge opens and connectivity is computed wrongly.",
            "Skipping component checks: the player spawns in a 3×3 pocket with no exit.",
            "Confusing 4- and 8-neighbourhoods: the 4-5 rule is written for eight neighbours.",
        ],
        games=["Terraria", "Dwarf Fortress", "Caves of Qud", "Noita"],
    ),
    dict(
        id="bsp",
        title="BSP dungeons: splits, rooms, corridors",
        tags=["BSP", "tree", "rooms", "connectivity"],
        summary="BSP recursively cuts a rectangle in half until the leaves are small enough, then places a room in every leaf and connects neighbours through the tree with corridors. The result is a guaranteed-connected dungeon with a readable hierarchy.",
        detail=[
            "The tree grows top-down: a node picks an axis (along its longer side), a split point in the 35–65 % range, and produces two children. Stop when a leaf is smaller than <b>2·minRoom + 1</b>. That margin guarantees room plus a one-cell border, and the tree gives the level macro-structure: big halls high up, small chambers deeper.",
            "Rooms go in the leaves; corridors connect the centres of sibling leaves (or an L-shaped path). Because links follow tree edges, traversal is guaranteed by construction: exactly one path between any two rooms. To avoid a boring level, add 10–20 % extra edges (braiding) — loops, alternative routes and secrets.",
            "BSP scales well: the tree depth can drive room type, and the leaves can be assigned biomes and factions. The downside is right angles and predictability; fix it with uneven walls, doorways, decoration and varied proportions. For meaningful spaces (temple, lab) lay templates over the tree.",
        ],
        formula=("split(node) → node.left, node.right;   room ⊆ leaf − margin;   "
                 "corridor = L(center(left), center(right))",
                 "Tree depth ≈ log₂(W/minRoom); leaves ≈ 2^depth. Split a leaf w×h while w ≥ 2·minW + 1 or h ≥ 2·minH + 1."),
        steps=[
            "Set the root rectangle, minRoom and maxDepth; split recursively along the longer side.",
            "Stop when the leaf is smaller than 2·minRoom+1 or the depth limit is reached.",
            "Place a room in every leaf with random margins of at least one cell.",
            "Connect sibling leaves with L-corridors between their room centres (optionally offset).",
            "Add 10–20 % loops, place doors, verify an A* path and assign room types by depth.",
        ],
        complexity=("O(N log N) for rooms", "O(N)",
                    "A 64-leaf tree is built in fractions of a millisecond; validation and decoration dominate."),
        code=("python", """import random

class Node:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.left = self.right = None
        self.room = None

def split(node, depth, min_room, rng):
    if depth == 0 or (node.w < 2 * min_room + 1 and node.h < 2 * min_room + 1):
        return
    horizontal = node.w < node.h if node.w != node.h else rng.random() < 0.5
    if horizontal:
        cut = rng.randint(min_room + 1, node.h - min_room - 1)
        node.left = Node(node.x, node.y, node.w, cut)
        node.right = Node(node.x, node.y + cut, node.w, node.h - cut)
    else:
        cut = rng.randint(min_room + 1, node.w - min_room - 1)
        node.left = Node(node.x, node.y, cut, node.h)
        node.right = Node(node.x + cut, node.y, node.w - cut, node.h)
    split(node.left, depth - 1, min_room, rng)
    split(node.right, depth - 1, min_room, rng)

def carve_rooms(node, rng):
    if node.left or node.right:
        if node.left: carve_rooms(node.left, rng)
        if node.right: carve_rooms(node.right, rng)
        return
    w = rng.randint(max(3, node.w // 2), max(3, node.w - 2))
    h = rng.randint(max(3, node.h // 2), max(3, node.h - 2))
    node.room = (node.x + 1, node.y + 1, min(w, node.w - 2), min(h, node.h - 2))

# then: L-corridors between sibling leaf centres, 10-20% extra edges"""),
        pitfalls=[
            "Splitting without room margin: a 3×3 leaf cannot hold a 3×3 room plus a border.",
            "Connecting every room to every other — hierarchy is lost and corridors explode.",
            "Forgetting doors: a corridor cuts a room diagonally and breaks navigation.",
            "Too deep a tree creates hundreds of tiny rooms — an anthill instead of a dungeon.",
        ],
        games=["The Binding of Isaac", "Enter the Gungeon", "Hades", "Diablo"],
    ),
    dict(
        id="randomwalk",
        title="Drunkard's walk caves",
        tags=["random walk", "carving", "density", "prototype"],
        summary="An agent starts in the middle of the map and on every step carves the cell and moves in a random direction. A few thousand steps later you have a winding cave. It is the simplest connected-space generator and the best way to feel what the parameters do.",
        detail=[
            "Probabilistic version: with 70 % chance step forward, 20 % turn, 10 % stay. The “stickiness” parameter sets the winding: 0.7 gives long corridors, 0.3 gives lumpy chambers. Several independent agents (3–7) produce a network of connected caves because they all start in the same area.",
            "The main metric is <b>carved fraction</b>. At 30 % you get narrow tunnels, at 50 % a maze, at 60 % big halls with wall islands. Stop on the fraction, not the step count: the same step count gives different density on different maps. Always verify connectivity — several agents can cut off a pocket if they start far apart.",
            "A walk gives no rooms and no rhythm, but fits voxel 3D, “wormholes” and erosion masks perfectly. Practical trick: a coarse walk first, then dilate the channel morphologically and add water. In production it is usually one layer, never the final generator.",
        ],
        formula=("p(step) = [0.7 forward, 0.2 turn, 0.1 stay],   "
                 "stop when carved / (W·H) ≥ target",
                 "The target density sets the style: 0.3 tunnels, 0.5 maze, 0.6 halls. Expected walk length grows as O(area / target density)."),
        steps=[
            "Fill the map with walls and put an agent in the centre (or on a random floor cell).",
            "Carve the cell and pick a direction by the probabilities on every step.",
            "Stop at the target floor fraction; keep a step counter for debugging.",
            "Verify connectivity with a flood fill and remove isolated pockets.",
            "Dilate the channel, then place entrance and exit on opposite edges.",
        ],
        complexity=("O(steps) ≈ O(W·H / density)", "O(W·H)",
                    "A 128×128 map takes milliseconds; in 3D cost grows cubically, so carve with a capsule."),
        code=("python", """import random

def drunkard(width=64, height=40, target=0.5, stickiness=0.7, seed=0):
    rng = random.Random(seed)
    g = [[1] * width for _ in range(height)]
    x, y = width // 2, height // 2
    dx, dy = 1, 0
    carved = 0
    goal = int(width * height * target)
    while carved < goal:
        if not g[y][x]:
            carved += 1
        g[y][x] = 0
        if rng.random() < stickiness:
            pass                      # keep direction
        elif rng.random() < 0.5:
            dx, dy = -dy, dx          # turn left
        else:
            dx, dy = dy, -dx          # turn right
        nx, ny = x + dx, y + dy
        if 0 < nx < width - 1 and 0 < ny < height - 1:
            x, y = nx, ny
        else:                         # bounce off the border
            dx, dy = -dx, -dy
    return g

# several agents: all start at the same point and carve into one array"""),
        pitfalls=[
            "Stopping on step count: a small map becomes mush, a large one a thin thread.",
            "Forgetting the borders — the agent leaves the array and teleports.",
            "One agent on a large map yields a single long intestine with no halls.",
            "Skipping connectivity checks with multiple starting points.",
        ],
        games=["Cataclysm: Dark Days Ahead", "Ancient Domains of Mystery", "The Binding of Isaac"],
    ),
    dict(
        id="maze",
        title="Maze generation: backtracker, Prim, Kruskal, Wilson",
        tags=["spanning tree", "DFS", "Prim", "Kruskal"],
        summary="A perfect maze is a spanning tree on a grid: exactly one path between any two cells. Different algorithms produce different character — backtracker long corridors, Prim a hedgehog, Kruskal an even texture, Wilson perfect uniformity.",
        detail=[
            "Grid cells are vertices, neighbours are edges. Backtracker (iterative DFS) dives deep and sweeps long corridors with rare forks — ideal for a Minotaur maze. <b>Prim</b> grows a tree from one cell, picking a random boundary edge, producing many short dead ends. <b>Kruskal</b> shuffles all edges and unions components (DSU), giving a uniform texture. <b>Wilson</b> builds the tree with loop-erased random walks and is uniform over all spanning trees, at a speed cost.",
            "A perfect maze is boring for players: one path means no decisions. So you <b>braid</b> it: remove some walls to create loops and add rooms. A backtracker with 20–30 % braiding is an excellent dungeon base; Prim with braiding suits cave cities.",
            "For on-the-fly generation, cut the maze into chunks, but border edges must agree. Generating the whole level at once is usually simpler: 128×128 is 16k cells, instant for a spanning tree. For 3D voxel mazes the same DFS works over six directions and gives Tron-like puzzles.",
        ],
        formula=("V = w·h,   E = 2wh − w − h;   perfect maze: |E_tree| = |V| − 1",
                 "A tree with V vertices has V−1 edges — exactly enough passages for full connectivity with no cycles. Adding one edge creates exactly one cycle."),
        steps=[
            "Treat the w×h cell grid as vertices with edges between neighbours.",
            "Pick an algorithm: DFS for long corridors, Prim for forks, Wilson for uniformity.",
            "Build the tree, knocking down walls between connected cells.",
            "Braid: remove 10–30 % of remaining walls to create loops and alternate routes.",
            "Widen corridors to 2–3 cells, place rooms at nodes and verify the entrance-to-exit path.",
        ],
        complexity=("O(V + E) for DFS/Prim/Kruskal, O(V²) for Wilson", "O(V)",
                    "A 100×100 grid takes milliseconds; rendering and navigation cost more than generation."),
        code=("python", """import random

def backtracker(w=21, h=21, seed=0, braid=0.0):
    rng = random.Random(seed)
    g = [[1] * w for _ in range(h)]          # 1 = wall
    stack = [(1, 1)]
    g[1][1] = 0
    while stack:
        x, y = stack[-1]
        nbrs = [(x + dx, y + dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
                if 0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx]]
        if nbrs:
            nx, ny = rng.choice(nbrs)
            g[(y + ny) // 2][(x + nx) // 2] = 0   # knock down the wall
            g[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()

    # braiding: remove some walls between two open cells
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if g[y][x] and rng.random() < braid:
                if (not g[y][x - 1] and not g[y][x + 1] and g[y - 1][x] and g[y + 1][x]) \\
                        or (not g[y - 1][x] and not g[y + 1][x] and g[y][x - 1] and g[y][x + 1]):
                    g[y][x] = 0
    return g"""),
        pitfalls=[
            "Even sizes: walls and passages do not line up and dangling segments appear.",
            "Forgetting braiding — the level has no decisions, only dead ends.",
            "Unoptimised Wilson is noticeably slow on large grids: cache walk directions.",
            "No validation: a DSU bug in Kruskal easily leaves two disconnected components.",
        ],
        games=["Pac-Man", "The Legend of Zelda", "Minecraft", "Slay the Spire"],
    ),
    dict(
        id="wfc",
        title="Wave Function Collapse: constraint-based generation",
        tags=["WFC", "AC-3", "entropy", "tiles", "backtracking"],
        summary="WFC is not drawing but solving a CSP: every cell holds a superposition of allowed tiles, we collapse the lowest-entropy cell and propagate constraints to neighbours. The output is a globally consistent picture built from local rules.",
        detail=[
            "Model: a tile set and an adjacency matrix (who may stand next to whom in each direction). Every cell stores a bitmask of possible tiles. Step: find the cell with <b>minimum entropy</b> (closest to one option), pick a tile by weight, then <b>propagate</b> — erase incompatible values from neighbours and continue the wave until stable.",
            "If a cell mask becomes empty, we have a contradiction. A simple fix is a restart with a new seed (original WFC style); an engineering fix is <b>backtracking</b> with an undo log, like a SAT solver. Large maps are generated in overlapping chunks with agreed borders; for an “infinite” city, add global constraints (highways, rivers) as separate layers.",
            "Rules can be authored by hand (tile set) or extracted from a sample image (overlap mode), which is what made WFC famous. The price is predictability: local rules do not guarantee large shapes, so WFC is usually combined with direction masks, templates and post-processing.",
        ],
        formula=("H(cell) = −Σ pᵢ log pᵢ,   choose argmin H,   "
                 "allowed(n) ← allowed(n) ∩ compat(tile, dir)",
                 "pᵢ is the weight of tile i in the current mask. Propagation is AC-3: drop values with no support in a neighbour until the queue empties."),
        steps=[
            "Define weighted tiles and an adjacency matrix — which tiles are allowed left/right/up/down.",
            "Initialise every mask to the full set (or restrict borders and mask regions).",
            "Find the minimum-entropy cell; break ties randomly.",
            "Collapse it by weight, then propagate constraints with a queue until stable.",
            "On contradiction, undo through the log (or restart); post-process and verify traversability.",
        ],
        complexity=("O(N · |T|) per propagation, up to O(N²) with backtracking", "O(N · |T|) bitmasks",
                    "32×32 with 20 tiles is milliseconds; 256×256 with backtracking can take seconds — generate in chunks."),
        code=("python", """import random

# tiles: 0 = floor, 1 = wall.  adjacency[direction][tile] -> set(tile)
# dir: 0=right, 1=down, 2=left, 3=up
def wfc(width, height, adjacency, weights, seed=0, tries=20):
    rng = random.Random(seed)
    n_tiles = len(weights)
    full = (1 << n_tiles) - 1
    for attempt in range(tries):
        wave = [full] * (width * height)

        def popcount(v):
            return bin(v).count("1")

        def constrain(x, y):
            todo = [(x, y)]
            while todo:
                cx, cy = todo.pop()
                for d, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
                    nx, ny = cx + dx, cy + dy
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    allowed = 0
                    m = wave[cy * width + cx]
                    for t in range(n_tiles):
                        if m >> t & 1:
                            for other in adjacency[d][t]:
                                allowed |= 1 << other
                    new = wave[ny * width + nx] & allowed
                    if new != wave[ny * width + nx]:
                        if new == 0:
                            return False          # contradiction
                        wave[ny * width + nx] = new
                        todo.append((nx, ny))
            return True

        ok = True
        while True:
            best, best_h = -1, 1e9
            for i, m in enumerate(wave):
                c = popcount(m)
                if 1 < c < best_h:
                    best, best_h = i, c
            if best < 0:
                break
            m = wave[best]
            choices = [t for t in range(n_tiles) if m >> t & 1]
            total = sum(weights[t] for t in choices)
            r = rng.random() * total
            for t in choices:
                r -= weights[t]
                if r <= 0:
                    wave[best] = 1 << t
                    break
            if not constrain(best % width, best // width):
                ok = False
                break
        if ok:
            return [[(wave[i] & -wave[i]).bit_length() - 1
                     for i in range(y * width, (y + 1) * width)]
                    for y in range(height)]
    raise RuntimeError("WFC failed")"""),
        pitfalls=[
            "Collapsing in scan order instead of by entropy: contradictions become far more common.",
            "Ignoring weights — rare tiles vanish or flood the map.",
            "No backtracking: one conflict kills the whole generation, especially on big maps.",
            "A tile set without global constraints yields a carpet with no plazas or routes — add masks and templates.",
        ],
        games=["Bad North", "Townscaper", "Caves of Qud", "RimWorld"],
    ),
    dict(
        id="city",
        title="Cities and road networks: Voronoi, MST and blocks",
        tags=["MST", "Voronoi", "A*", "city building"],
        summary="A city is a hierarchy: districts, highways, streets, blocks, buildings. Scatter nodes and partition the land with Voronoi, connect nodes with a minimum spanning tree, then densify with streets and cut blocks into lots.",
        detail=[
            "Top level — <b>districts</b>: Poisson centres plus a Voronoi diagram (Lloyd relaxation for even areas). Highways are the <b>MST</b> over the centres (Prim/Kruskal, Euclidean distance), plus 10–20 % extra edges for resilience. Inside a district, streets may follow a jittered grid, A* routes between random points, or an L-system for the organic feel of an old town.",
            "Blocks are the faces between streets; cut them into lots by recursive splitting (BSP by area) or greedy rectangle packing. Buildings are placed with setbacks, façades facing the street, density and height taken from a cost map (the centre is expensive). Roads must be connected: an A* check per segment is a cheap validation.",
            "In practice city generators are almost always hybrid. A fully procedural city looks correct but lifeless, so production combines procedural blocks with hand-placed landmarks (cathedral, station, bridge). For a game, traversability and readability matter more than geometric beauty: verify routes, distances and sight lines from key points.",
        ],
        formula=("MST = argmin_T Σ_{e∈T} w(e),   "
                 "block grid = Voronoi(cells) ∩ street network,   "
                 "width ∝ traffic^0.4",
                 "w(e) is the Euclidean distance between centres. Street width grows with the square root of traffic (a transport rule of thumb); an MST has |V|−1 edges."),
        steps=[
            "Scatter district centres with Poisson; build Voronoi and run 2–3 Lloyd iterations.",
            "Connect centres with an MST; add 10–20 % chords for alternative routes.",
            "Lay streets inside districts: jittered grid, A* between points or an L-system.",
            "Cut blocks and lots by recursive splitting; place buildings with street setbacks.",
            "Verify connectivity and distances, place landmarks and density from the cost map.",
        ],
        complexity=("O(V log V + E) for the MST, O(cells) for Voronoi", "O(V + cells)",
                    "Thousands of buildings take seconds on the CPU; stream by district and cache results."),
        code=("python", """import math

def voronoi_labels(points, width, height, step=4):
    \"\"\"Coarse Voronoi rasterisation: nearest centre for every grid point.\"\"\"
    labels = [[0] * (width // step) for _ in range(height // step)]
    for gy in range(height // step):
        for gx in range(width // step):
            px, py = gx * step, gy * step
            best, bi = 1e18, 0
            for i, (cx, cy) in enumerate(points):
                d = (px - cx) ** 2 + (py - cy) ** 2
                if d < best:
                    best, bi = d, i
            labels[gy][gx] = bi
    return labels

def mst(points):
    \"\"\"Prim O(V^2): returns the spanning tree edges.\"\"\"
    n = len(points)
    in_tree = [False] * n
    best = [1e18] * n
    parent = [-1] * n
    best[0] = 0
    edges = []
    for _ in range(n):
        u = min((i for i in range(n) if not in_tree[i]), key=lambda i: best[i])
        in_tree[u] = True
        if parent[u] >= 0:
            edges.append((parent[u], u))
        for v in range(n):
            if not in_tree[v]:
                d = math.dist(points[u], points[v])
                if d < best[v]:
                    best[v], parent[v] = d, u
    return edges

# districts = voronoi_labels(poisson_points, W, H)
# roads = [(points[a], points[b]) for a, b in mst(points)]"""),
        pitfalls=[
            "Connecting centres in a ring instead of an MST — redundant highways and unrealistic topology.",
            "Placing houses without reference to streets: façades face walls, blocks do not read.",
            "Ignoring connectivity: a road ends at a river and the city splits into enclaves.",
            "A perfectly regular grid everywhere looks like a suburb; mix scales and landmarks.",
        ],
        games=["Dwarf Fortress", "Songs of Syx", "RimWorld", "No Man's Sky"],
    ),
]
