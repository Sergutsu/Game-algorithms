# -*- coding: utf-8 -*-
"""English content for topics 24–30: physics, and the first optimisation block."""

TOPICS_EN_3 = [
    dict(
        id="cloth",
        title="Cloth and soft bodies (Verlet, XPBD)",
        tags=["mass-spring", "Verlet integration", "XPBD"],
        summary="Cloth is a grid of particles linked by length constraints. Verlet gives free damping and a simple implementation, while XPBD adds stability under stiff constraints.",
        detail=[
            "Verlet without an explicit velocity: <b>x′ = 2x − x<sub>prev</sub> + a·dt²</b>. The position is updated from the two previous ones and the velocity is implicit — that makes the scheme stable and lets you apply constraints directly to positions. The constraint “the distance between two particles equals L” is solved by projection: move both points along the connecting line by a fraction of the error. 10–20 iterations give cloth that is stiff but does not explode.",
            "A mass-spring model with stiff springs needs a tiny dt or implicit integration. Cloth and ropes therefore use the constraint-based approach (PBD/XPBD), where stiffness is expressed through compliance α instead of a huge coefficient k. XPBD: <b>Δλ = (−C − α̃λ)/(w₁ + w₂ + α̃)</b>, where C is the constraint error — this makes stiffness independent of the iteration count.",
            "For gameplay what matters is collision with the character capsule, wind as a force per area, tearing past a deformation threshold, LOD, and “freezing” cloth that is off screen. Cloth with hundreds of particles is expensive; capes usually use skinning plus bones with physics instead of a full mesh.",
        ],
        formula=("Verlet: x′ = 2x − x<sub>prev</sub> + a·dt²,   PBD: Δx = ±w/(w₁+w₂)·C,   XPBD: α̃ = α/dt²",
                 "C — the constraint function (for example |x₁−x₂| − L). w — inverse mass. α = 0 means a hard constraint."),
        steps=[
            "Build the grid of particles and constraints (structural, shear, bend).",
            "Set the pinned points and the initial positions; keep the previous positions.",
            "Each sub-step: integrate with Verlet, then run N iterations of constraint projection.",
            "Handle collisions (spheres, capsules, planes) after or inside the projections.",
            "Add wind, damping, tearing and LOD; put invisible cloth to sleep.",
        ],
        complexity=("O(#particles·#iterations) per sub-step", "O(#particles + #constraints)",
                    "A 32×32 grid with 10 iterations and 2 sub-steps is tens of thousands of projections per frame."),
        code=("python", """import math

def verlet(x, x_prev, acc, dt):
    # x' = 2x - x_prev + a*dt^2; velocity is implicit
    nx = [2 * x[i] - x_prev[i] + acc[i] * dt * dt for i in range(len(x))]
    return nx, list(x)

def solve_distance(p1, p2, rest, w1, w2, stiffness=1.0):
    # C = |p1-p2| - rest; move both points along the line by the error
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    d = math.hypot(dx, dy)
    if d < 1e-9:
        return p1, p2
    C = d - rest
    wsum = w1 + w2
    if wsum <= 0:
        return p1, p2
    k = stiffness * C / wsum
    return ([p1[0] + dx / d * k * w1, p1[1] + dy / d * k * w1],
            [p2[0] - dx / d * k * w2, p2[1] - dy / d * k * w2])"""),
        pitfalls=[
            "Stiff springs at a large dt explode — use sub-steps and PBD/XPBD.",
            "Cloth without damping rings forever; add decay and sleeping.",
            "Colliding only with the hero capsule lets cloth sink through the floor — you need planes and broadphase.",
            "A full simulation for every cape on screen is expensive; LOD and bones solve 80 % of it.",
        ],
        games=["Shadow of the Tomb Raider", "Marvel's Spider-Man", "Assassin's Creed", "UE Chaos Cloth"],
    ),
    dict(
        id="aerodynamics",
        title="Aerodynamics and flight models",
        tags=["Bernoulli", "CFD", "aerodynamic coefficients"],
        summary="Lift scales with density, the square of speed and wing area, and the lift coefficient depends on the angle of attack. That formula is enough for arcade flight; a simulator needs tables and stall behaviour.",
        detail=[
            "Lift: <b>L = ½·ρ·v²·S·C<sub>L</sub>(α)</b>, drag: <b>D = ½·ρ·v²·S·C<sub>D</sub>(α)</b>. C<sub>L</sub> grows linearly with the angle of attack up to a critical value (~15°), then collapses — that is the stall, which makes the aircraft drop. C<sub>D</sub> = C<sub>D0</sub> + C<sub>L</sub>²/(π·e·AR): induced drag grows with lift.",
            "Bernoulli's principle explains part of the picture (faster flow, lower pressure), but lift is described better by flow deflection and circulation (Zhukovsky's theorem: L = ρ·v·Γ). For a game the empirical curves C<sub>L</sub>(α) and C<sub>D</sub>(α) matter more than physical accuracy. CFD is used for design and pre-computation; at runtime it is replaced by tables.",
            "The flight model: forces in a body frame (thrust, lift, drag, weight), moments from ailerons, rudder and elevator, plus inertia. Damping moments provide stability. Arcade games simplify: the aircraft levels itself, roll steers the turn, and stall is disabled. A simulator wants honest aerodynamics, trimming, and air density that falls with altitude.",
        ],
        formula=("L = ½ρv²S·C<sub>L</sub>(α),   D = ½ρv²S·(C<sub>D0</sub> + C<sub>L</sub>²/(πeAR))",
                 "ρ falls with altitude: ρ ≈ ρ₀·(1 − 2.2557e−5·h)<sup>4.2559</sup>. Stall at α > α<sub>crit</sub> ≈ 15°."),
        steps=[
            "Set mass, wing area, span and the C<sub>L</sub>/C<sub>D</sub> curves versus angle of attack.",
            "Compute body-frame velocities, the angle of attack and the sideslip.",
            "Compute forces and moments, then apply angular damping.",
            "Add thrust, weight, air density versus altitude and stall behaviour.",
            "Tune the controls: assists for arcade, trim and honest axes for a simulator.",
        ],
        complexity=("O(1) per body, O(log n) for the table lookups", "O(#bodies + tables)",
                    "One aircraft costs nothing; CFD is computed offline and baked into tables."),
        code=("python", """import math

def cl_cd(alpha_deg, cl_alpha=0.09, cl_max=15.0, cd0=0.025, k_induced=0.05):
    a = math.radians(alpha_deg)
    if abs(a) <= math.radians(cl_max):
        cl = cl_alpha * a
    else:
        # past the critical angle the lift collapses (stall)
        over = (abs(a) - math.radians(cl_max)) / math.radians(5)
        cl = math.copysign(cl_alpha * math.radians(cl_max) * max(0.0, 1.0 - over), a)
    cd = cd0 + k_induced * cl * cl
    return cl, cd

def forces(mass, speed, area, rho, alpha_deg, cl=None, cd=None):
    cl_c, cd_c = (cl, cd) if cl is not None else cl_cd(alpha_deg)
    q = 0.5 * rho * speed * speed * area
    return q * cl_c, q * cd_c"""),
        pitfalls=[
            "A linear C<sub>L</sub> without stall gives an aircraft that “sticks” to the sky at any angle.",
            "Ignoring air density breaks high-altitude behaviour — at 10 km both thrust and lift drop noticeably.",
            "Moments without damping make the aircraft oscillate and become uncontrollable.",
            "Arcade assists hidden deep in the code feel like a magnet — leave the player a sense of control.",
        ],
        games=["Microsoft Flight Simulator", "IL-2 Sturmovik", "War Thunder", "Ace Combat"],
    ),
    dict(
        id="fields",
        title="Vector fields, divergence and curl",
        tags=["vector fields", "divergence/curl", "potential"],
        summary="A field defines a force at every point in space. Divergence shows sources, curl shows vortices; together they tell you whether a field can be expressed as a potential and how to visualise it without chaos.",
        detail=[
            "A vector field F(x, y) = (P, Q). The divergence <b>∇·F = ∂P/∂x + ∂Q/∂y</b> is the density of sources; the curl (a scalar in 2D) <b>∇×F = ∂Q/∂x − ∂P/∂y</b> is local rotation. A magnetic field in vacuum is source-free (∇·B = 0), an electrostatic field is potential (∇×E = 0). Gravity is a potential field too, with ∇·g = −4πGρ.",
            "In games, fields are usually built by summing sources: a point charge or mass gives F = k·q·r̂/r², a dipole a more complex pattern. The sum needs softening: as r → 0 the force must not diverge, or objects get flung. For planets use a spherically symmetric model (linear growth inside) rather than a point singularity.",
            "Visualisation: streamline curves integrate dx/ds = F(x)/|F(x)|, colour follows the magnitude, arrows the direction. For gameplay, readability wins: do not draw the field where it does not matter, limit the number of lines and use animated dashes. For magnetic puzzles, equipotential lines are useful — they hint where an object will roll.",
        ],
        formula=("F = k·q·r̂/r²,   ∇·F = ∂P/∂x + ∂Q/∂y,   ∇×F = ∂Q/∂x − ∂P/∂y",
                 "Softening: F = k·q·r̂/(r² + ε²). Potential φ: F = −∇φ; for a point mass φ = −GM/r."),
        steps=[
            "Define the field sources and the force law (1/r², dipole, vortex).",
            "Add softening and a maximum force for stability.",
            "Evaluate forces for dynamic objects; for static ones, pre-bake the field into a texture.",
            "Visualise streamlines or equipotentials with a bounded density.",
            "Check the integrator's stability: a field with strong gradients needs sub-steps.",
        ],
        complexity=("O(#objects·#sources) per frame", "O(field grid) or O(#sources)",
                    "With hundreds of sources use a grid or a multipole approximation."),
        code=("python", """import math

def field_force(sources, x, y, softening=0.5, max_force=1e4):
    fx = fy = 0.0
    for sx, sy, strength in sources:
        dx, dy = x - sx, y - sy
        r2 = dx * dx + dy * dy + softening * softening
        inv = strength / (r2 * math.sqrt(r2))     # k*q*r_hat / (r^2 + eps^2)
        fx += dx * inv
        fy += dy * inv
    mag = math.hypot(fx, fy)
    if mag > max_force:                          # clamp for stability
        fx = fx / mag * max_force
        fy = fy / mag * max_force
    return fx, fy"""),
        pitfalls=[
            "The 1/r² singularity at the centre flings objects away — always soften it.",
            "Explicit Euler breaks down in a strong field; use symplectic integrators for orbits.",
            "Too dense a field visualisation turns into mush — show only the regions that matter.",
            "A magnetic field cannot be made “attractive” without a physical justification — players notice the contradiction.",
        ],
        games=["Portal 2 (excursion funnel)", "Super Mario Galaxy", "Prey (GLOO)", "Kerbal Space Program"],
    ),
    dict(
        id="heat",
        title="Heat diffusion and thermodynamics",
        tags=["Fourier's equation", "diffusion", "entropy"],
        summary="Heat flows from hot to cold in proportion to the temperature gradient. The heat equation is a diffusion; in games it is solved on a grid or simplified into “zones” with a heat capacity.",
        detail=[
            "Fourier's equation: <b>∂T/∂t = α·∇²T</b>, where α = k/(ρc<sub>p</sub>) is the thermal diffusivity. On a grid this is an explicit scheme: T′ᵢ = Tᵢ + α·dt/h²·(Tᵢ₋₁ − 2Tᵢ + Tᵢ₊₁). The stability condition is α·dt/h² ≤ 0.25 in 2D (≤ 1/6 in 3D). Breaking it produces oscillations and a checkerboard — the classic mistake.",
            "For gameplay a “zone” model is often enough: rooms with a temperature, a heat capacity and connections (doors, ventilation). Then heat exchange is Q = k·(T₁ − T₂) and T′ᵢ = Tᵢ + Q/cᵢ. It is stable, cheap and readable: the player sees that an open door cools the room. For visuals, add a heat map and steam or ice as indicators.",
            "Thermodynamics: the first law ΔU = Q − W (energy is conserved), the second — entropy does not decrease in a closed system. In games the second law is a design constraint: no perpetual motion without heat rejection. Cooling, efficiency and overheating equipment become natural mechanics for sci-fi and survival, as long as the numbers are shown to the player.",
        ],
        formula=("∂T/∂t = α∇²T,   explicit: T′ᵢ = Tᵢ + α·dt/h²·(Tᵢ₋₁ − 2Tᵢ + Tᵢ₊₁)",
                 "Stability: α·dt/h² ≤ 1/4 (2D), ≤ 1/6 (3D). Otherwise use an implicit scheme (Crank–Nicolson)."),
        steps=[
            "Choose the representation: a grid for visuals, zones for gameplay.",
            "Set the heat sources, heat capacities and the conductivity of the materials.",
            "Check the stability condition or switch to an implicit scheme.",
            "Connect the temperature to effects: damage, freezing, steam, overheating.",
            "Show numbers and colours — the player must understand why they are freezing.",
        ],
        complexity=("O(#cells) per step, O(#zones²) for zones", "O(grid) / O(#zones)",
                    "A 256×256 grid is 65k cells per step; for gameplay 10–50 zones usually suffice."),
        code=("python", """import math

def heat_step(T, alpha, dt, h=1.0):
    # explicit diffusion; stability needs alpha*dt/h^2 <= 0.25 in 2D
    if alpha * dt / (h * h) > 0.25:
        raise ValueError("unstable step: use sub-steps or an implicit scheme")
    n = len(T)
    out = [0.0] * n
    for i in range(n):
        left  = T[i - 1] if i > 0 else T[i]
        right = T[i + 1] if i < n - 1 else T[i]
        out[i] = T[i] + alpha * dt / (h * h) * (left - 2 * T[i] + right)
    return out

def zone_exchange(zones, edges, dt=1.0):
    # zones: {id: (temperature, capacity)}; edges: [(a, b, k)]
    temps = {k: v[0] for k, v in zones.items()}
    caps  = {k: v[1] for k, v in zones.items()}
    for a, b, k in edges:
        q = k * (temps[a] - temps[b]) * dt
        temps[a] -= q / caps[a]
        temps[b] += q / caps[b]
    return temps"""),
        pitfalls=[
            "Breaking the stability condition gives a checkerboard pattern instead of heat.",
            "Heat capacity matters more than conductivity: metal conducts fast but is expensive to heat.",
            "Without visual feedback an overheating mechanic is unreadable — you need indicators and sound.",
            "Entropy as a “magical” resource without rules confuses players; tie it to a concrete mechanic.",
        ],
        games=["Frostpunk", "Oxygen Not Included", "RimWorld", "Stationeers"],
    ),
    dict(
        id="scheduling",
        title="Frame scheduling and work distribution",
        tags=["linear programming", "simplex", "job system"],
        summary="The frame budget is a scheduling problem: you have 16.6 ms and a set of jobs with different costs and dependencies. Formally it is LP/ILP; practically it is priorities, task pools and cutting work at the budget.",
        detail=[
            "The formalisation: maximise Σ uᵢ·xᵢ subject to Σ cᵢ·xᵢ ≤ B (the budget), dependencies (xᵢ ≤ xⱼ) and integrality. The simplex method solves the continuous relaxation and rounding gives a nearly optimal schedule. In practice jobs (shadows, GI, particles, physics) are discrete with hard dependencies, so a greedy algorithm on “utility per millisecond” with cutoff is the usual answer.",
            "Job system: a pool of tasks with dependencies (a DAG), worker threads, lock-free queues. The key is to minimise synchronisation and to size the tasks well: tasks that are too small drown in overhead, tasks that are too large give no balance. For the GPU, use command buffers and asynchronous compute queues so you never wait for a copy.",
            "Adaptive quality: measure the actual time of each system, keep a moving average, and decide what to lower when the budget is exceeded. The policy needs hysteresis so quality does not flicker every frame. And keep separate CPU and GPU budgets: they overlap, but synchronisation can eat the gain.",
        ],
        formula=("max Σ uᵢxᵢ  s.t.  Σ cᵢxᵢ ≤ B,  xᵢ ∈ {0,1}",
                 "Greedy approximation: sort by uᵢ/cᵢ and add while the budget lasts. The LP relaxation gives an upper bound on the optimum."),
        steps=[
            "Split the frame into systems and measure their cost (P50/P95).",
            "Build a dependency DAG and parallelise the independent branches.",
            "Set priorities and a cutoff policy for when the budget is exceeded.",
            "Implement a task pool with worker threads and minimal synchronisation.",
            "Add adaptive quality with hysteresis and log the decisions.",
        ],
        complexity=("LP — polynomial; greedy — O(n log n)", "O(#tasks) + queues",
                    "The scheduler must cost microseconds, not milliseconds."),
        code=("python", """def greedy_schedule(tasks, budget_ms):
    \"\"\"tasks: [(name, cost_ms, utility, [dependencies])]\"\"\"
    done, used, plan = set(), 0.0, []
    remaining = list(tasks)
    while remaining:
        ready = [t for t in remaining if all(d in done for d in t[3])]
        if not ready:
            break
        # highest utility per millisecond first
        best = max(ready, key=lambda t: t[2] / max(t[1], 1e-6))
        if used + best[1] > budget_ms:
            break                       # out of budget: cut the rest
        plan.append(best[0])
        used += best[1]
        done.add(best[0])
        remaining.remove(best)
    return plan, used"""),
        pitfalls=[
            "Optimising the average frame does not remove hitches — look at P99 and the peaks.",
            "Tasks that are too small cost more in synchronisation than they save.",
            "Adaptive quality without hysteresis flickers and annoys more than a dip would.",
            "A CPU→GPU synchronisation in the middle of the frame kills the parallelism — put it at the end.",
        ],
        games=["Doom Eternal (id Tech 7)", "Frostbite", "Unity DOTS", "Unreal Insights"],
    ),
    dict(
        id="bvh",
        title="Spatial partitioning (BVH, k-d tree, grid)",
        tags=["BVH", "k-d tree", "broadphase"],
        summary="Testing every pair is O(n²). A spatial index discards obviously distant pairs and turns collisions into an almost linear problem.",
        detail=[
            "Broadphase: build an AABB per object, let the index find the intersecting pairs, then run the narrowphase on the exact geometry (GJK, SAT, triangles). Index options: a uniform grid (fast, but poor when object scales differ), sweep-and-prune (sort along an axis, good for nearly sorted data), a BVH (an AABB hierarchy — the best choice for static geometry and raycasts) and a k-d tree (good for point queries and nearest-neighbour searches).",
            "A BVH is built top-down: pick an axis (SAH — the surface area heuristic), sort by centroids, split in half. SAH minimises the expected traversal cost: <b>cost = C<sub>trav</sub> + (S<sub>L</sub>/S)·C<sub>L</sub> + (S<sub>R</sub>/S)·C<sub>R</sub></b>. For dynamic objects you refit parts of the tree or keep several trees by layer.",
            "Important: broadphase does not replace the exact test, it only reduces the number of pairs. For thousands of projectiles a fixed-cell grid with pair de-duplication wins. For mesh raycasts, a BVH with ordered traversal (nearest child first) and early exit is the answer. Cache locality decides the rest: a flat array of structs beats a tree of pointers.",
        ],
        formula=("SAH: cost = C<sub>trav</sub> + (S<sub>L</sub>/S)·C<sub>L</sub> + (S<sub>R</sub>/S)·C<sub>R</sub>",
                 "S — the AABB surface area. For a grid: cell size ≈ the average object size; with varied sizes use a hierarchical grid."),
        steps=[
            "Collect the AABBs and pick a structure for the scenario (grid, BVH, SAP).",
            "Build the index; once for static geometry, refit or rebuild for dynamic content.",
            "Query the pairs and pass them to the narrowphase with layer filters.",
            "For raycasts, traverse with a nearest-node priority and an early exit.",
            "Profile build, queries and updates separately — they are three different budget lines.",
        ],
        complexity=("Build O(n log n), query O(log n + k), naive O(n²)", "O(n)",
                    "A BVH over 1M triangles builds in seconds; a ray traversal takes microseconds."),
        code=("python", """import math

def union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))

def overlaps(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

class Node:
    __slots__ = ("box", "left", "right", "items")
    def __init__(self, box):
        self.box = box          # (minx, miny, maxx, maxy)
        self.left = self.right = None
        self.items = []

def build(boxes, depth=0):
    node = Node(union(boxes))
    if len(boxes) <= 4 or depth > 24:
        node.items = boxes
        return node
    # split along the longest axis at the median centroid
    ex = node.box[2] - node.box[0]
    ey = node.box[3] - node.box[1]
    axis = 0 if ex >= ey else 1
    boxes = sorted(boxes, key=lambda b: (b[axis] + b[axis + 2]) * 0.5)
    mid = len(boxes) // 2
    node.left = build(boxes[:mid], depth + 1)
    node.right = build(boxes[mid:], depth + 1)
    return node"""),
        pitfalls=[
            "One grid for objects of different scales (a mouse and a tank) is inefficient — use a hierarchy or a BVH.",
            "Rebuilding a BVH every frame on a large scene costs more than the collisions — refit static parts.",
            "A pointer-based BVH caches badly; flat arrays give a multiple of the performance.",
            "Broadphase does not replace narrowphase: AABBs overlap far more often than real meshes do.",
        ],
        games=["PhysX", "Havok", "Bullet", "UE5 Chaos"],
    ),
    dict(
        id="animcompression",
        title="Animation compression (quantization + curve fitting)",
        tags=["quantisation", "splines", "curves"],
        summary="Animation is rotation and position curves sampled at a high rate. You compress them by quantising, dropping keys within a tolerance and fitting splines; the crucial part is not to lose footfalls and sharp impacts.",
        detail=[
            "A quaternion takes 16 bytes; it is quantised to 4×16 bits (8 bytes) or to 3×10 bits plus a sign (smallest-three). At a tolerance of 0.1° this is visually invisible. Positions and scales are quantised over the skeleton's range; small bones (fingers) need a smaller range, so they can spend fewer bits.",
            "The key step is key removal: the curve is approximated within a tolerance (say 0.5 cm / 0.5°), redundant keys are dropped and the rest are encoded as Hermite splines with tangents. The algorithm is greedy: extend the segment while the error stays below the tolerance. That gives a 5–20× compression on smooth clips and less on sharp ones.",
            "Advanced techniques: significance-based curve simplification, delta encoding against the A-pose, a different sample rate per bone, and separate compression for translation and rotation. For large clips, split into chunks and stream them. Validate by comparing the visual result and the maximum deviation — not the average; the eye notices the peaks.",
        ],
        formula=("bits ≈ log₂(range/tolerance),   3-component quaternion: 32 bits → 30 bits + sign",
                 "Approximation error: max|curve(t) − approx(t)| < tolerance over the whole interval."),
        steps=[
            "Define rotation and position tolerances per bone, based on its size and visibility.",
            "Convert quaternions to a compact representation (smallest-three).",
            "Simplify the curves greedily while tracking the maximum error.",
            "Encode the remaining keys as splines with tangents and compress the stream.",
            "Check visually and by peak error; use tighter tolerances for sharp clips.",
        ],
        complexity=("O(#keys·#bones) to compress", "O(#keys·#bones)",
                    "Compression is an offline pipeline; decompression on CPU/GPU has to be cheap."),
        code=("python", """def simplify(keys, tolerance, metric=lambda a, b: abs(a - b)):
    \"\"\"Greedy key removal: keep points while the linear interpolation
    error stays below the tolerance.\"\"\"
    if len(keys) < 3:
        return list(keys)
    out = [keys[0]]
    last = 0
    for i in range(2, len(keys)):
        # check every intermediate point against the segment last -> i
        ok = True
        for j in range(last + 1, i):
            t = (keys[j][0] - keys[last][0]) / (keys[i][0] - keys[last][0])
            approx = keys[last][1] + t * (keys[i][1] - keys[last][1])
            if metric(keys[j][1], approx) > tolerance:
                ok = False
                break
        if not ok:
            out.append(keys[i - 1])
            last = i - 1
    out.append(keys[-1])
    return out"""),
        pitfalls=[
            "A small average error with a visible peak during fast motion — control the maximum.",
            "Too aggressive compression breaks footfalls and impacts; use separate tolerances for legs and arms.",
            "Quantising a quaternion without renormalising causes drift — normalise after reconstruction.",
            "Clips with different frame rates cannot be blended without resampling, or the timings drift.",
        ],
        games=["Unity Animation Compression", "Unreal Anim Compression", "For Honor", "Mortal Kombat 11"],
    ),
]
