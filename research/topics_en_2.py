# -*- coding: utf-8 -*-
"""English content for topics 14–23: water, clouds, networking, procedural generation."""

TOPICS_EN_2 = [
    dict(
        id="water",
        title="Water rendering with FFT waves and SPH",
        tags=["Navier–Stokes", "SPH", "FFT waves"],
        summary="Water in a game is two different algorithms: an ocean surface (sum of waves, FFT, reflections) and a volume/interaction model (SPH or a height field). Mixing both in one system is expensive, so they are almost always separated.",
        detail=[
            "Navier–Stokes for an incompressible fluid: <b>∂u/∂t + (u·∇)u = −∇p/ρ + ν∇²u + f, ∇·u = 0</b>. Solving it directly on a grid in real time only works for small volumes. For an ocean, the spectral approach wins: a sum of sinusoids with the deep-water dispersion relation <b>ω² = g·k</b>, where k is the wavenumber. An FFT over a Phillips spectrum gives a 256×256 height and normal map in milliseconds on a GPU.",
            "SPH (Smoothed Particle Hydrodynamics) represents the fluid as particles with a smoothing kernel W: density ρᵢ = Σ mⱼW(rᵢⱼ, h), pressure from the equation of state p = k(ρ − ρ₀). Pressure and viscosity forces push the particles apart; boundaries are handled with penalty forces. SPH is great for splashes, waterfalls and puddles, but it needs sub-steps and yields a noisy surface that has to be reconstructed with marching cubes or screen-space fluids.",
            "Rendering water: Fresnel reflection F(θ) = F₀ + (1−F₀)(1−cosθ)⁵, refraction distorted by the normal, depth absorption following Beer's law (colour depends on distance), foam driven by a height/speed threshold, and caustics as a projected texture. Without Fresnel and depth fog, water looks like blue plastic.",
        ],
        formula=("∂u/∂t + (u·∇)u = −∇p/ρ + ν∇²u + f,   ∇·u = 0,   ω² = g·k",
                 "SPH: ρᵢ = Σⱼ mⱼ·W(|rᵢ−rⱼ|, h), pᵢ = k·(ρᵢ − ρ₀). Fresnel: F = F₀ + (1−F₀)(1−cosθ)⁵."),
        steps=[
            "Choose the model: FFT waves for open ocean, a height field for rivers, SPH for splashes and volumes.",
            "For the ocean, generate the spectrum, run the inverse FFT for heights and normals, and add fine ripple with a normal map.",
            "For SPH tune h, mass, stiffness and the number of sub-steps; stabilise the pressure (PCISPH/DFSPH).",
            "Render with Fresnel, refraction and depth absorption; add foam from the velocity.",
            "Sync the wave phases over the network or keep them purely visual on the client.",
        ],
        complexity=("FFT O(N² log N), SPH O(n·k) per sub-step", "O(N²) textures / O(n) particles",
                    "SPH with 100k particles needs a GPU; an FFT ocean is cheaper and more stable over large areas."),
        code=("glsl", """// Gerstner wave: vertical and horizontal displacement
vec3 gerstner(vec2 p, vec2 dir, float steepness, float wavelength,
              float speed, float t, out vec3 normal)
{
    float k = 6.28318 / wavelength;
    float c = sqrt(9.81 / k);          // phase speed
    float f = k * (dot(dir, p) - c * speed * t);
    float a = steepness / k;
    normal = vec3(-dir.x * steepness * cos(f),
                  1.0 - steepness * sin(f),
                  -dir.y * steepness * cos(f));
    return vec3(dir.x * a * cos(f), a * sin(f), dir.y * a * cos(f));
}"""),
        pitfalls=[
            "A sum of sinusoids without dispersion gives “rubber” waves that all move at the same speed.",
            "SPH without sub-steps explodes: pressure has to be solved iteratively.",
            "Reflections without Fresnel and without depth awareness look like painted plastic.",
            "Water in multiplayer should stay visual; buoyancy physics is a separate simplified model.",
        ],
        games=["Sea of Thieves", "Assassin's Creed IV: Black Flag", "Subnautica", "Wave Race"],
    ),
    dict(
        id="clouds",
        title="Volumetric clouds and ray marching",
        tags=["ray marching", "density functions", "Beer–Lambert"],
        summary="A cloud is a density field in a volume. A ray steps through it accumulating scattered light; the key to quality is the density function (fBm with erosion) and a cheap lighting approximation.",
        detail=[
            "Density comes from 3D noise: <b>ρ(x) = smoothstep(threshold, threshold + w, fbm(x))</b> with a height gradient and a “weather map” on the ground. To make clouds look fluffy you subtract higher-frequency noise from the base shape (erosion) — cheaper and prettier than one noise with many octaves.",
            "Ray marching takes N steps along the ray, evaluates density at each step and accumulates transmittance with the Beer–Lambert law <b>T = exp(−∫σ·ds)</b>. Lighting is estimated with a “cheap” second march towards the sun (6–8 steps) and a Henyey–Greenstein phase function for the silver lining. A full sun march at every step is far too expensive, so precomputed light maps or a depth-based approximation are used instead.",
            "Optimisations: empty-space skipping through a mip pyramid of the density, jittering the start offset to hide banding, temporal accumulation with reprojection, and blue-noise dithering. Clouds are the classic case where 32 steps with good noise look better than 128 steps with bad noise.",
        ],
        formula=("T = exp(−∫ σ<sub>t</sub>(x) ds),   L = ∫ σ<sub>s</sub>(x)·T(x)·L<sub>sun</sub>·phase(θ) ds",
                 "HG phase: P(θ) = (1−g²) / (4π(1 + g² − 2g·cosθ)<sup>3/2</sup>), g ≈ 0.6–0.8 for forward scattering."),
        steps=[
            "Generate a 3D density texture: base shape + erosion noise, with height falloff.",
            "Build a mip pyramid of the density for empty-space skipping.",
            "Ray march in the shader with a dithered start and an adaptive step size.",
            "Estimate lighting with a short march towards the sun or from a light map.",
            "Accumulate across frames with reprojection and reset the history when the camera moves.",
        ],
        complexity=("O(N·M) per pixel (N steps, M towards the sun)", "O(3D texture) + history",
                    "1080p with 48 steps is tens of millions of samples per frame; render at half res and upscale."),
        code=("glsl", """float density(vec3 p) {
    float base = texture(noise3D, p * 0.5).r;
    float erosion = texture(noise3D, p * 3.0).r;
    float shape = smoothstep(0.45, 0.75, base - erosion * 0.25);
    float heightFalloff = smoothstep(0.0, 0.3, p.y) *
                          (1.0 - smoothstep(0.7, 1.0, p.y));
    return shape * heightFalloff;
}

vec4 marchClouds(vec3 ro, vec3 rd, float dither, float maxDist) {
    float t = dither * stepSize;
    float transmittance = 1.0;
    vec3 scattered = vec3(0.0);
    for (int i = 0; i < 48 && t < maxDist; ++i) {
        vec3 p = ro + rd * t;
        float d = density(p);
        if (d > 0.001) {
            float sunT = lightMarch(p);            // 6 steps towards the sun
            vec3 lit = sunColor * sunT * phaseHG(rd, sunDir);
            float extinction = exp(-d * stepSize * sigmaT);
            scattered += transmittance * lit * (1.0 - extinction);
            transmittance *= extinction;
        }
        t += stepSize;
    }
    return vec4(scattered, 1.0 - transmittance);
}"""),
        pitfalls=[
            "A fixed step produces banding and “layering” — use dithering and a variable step.",
            "A full sun march at every step kills the frame rate; cap it at 6–8 steps and a limited distance.",
            "Temporal accumulation smears while moving — reprojection and history trimming are required.",
            "Without a height gradient clouds look like uniform cotton all the way to the horizon.",
        ],
        games=["Red Dead Redemption 2", "Flight Simulator", "Horizon Forbidden West", "UE5 Volumetrics"],
    ),
    dict(
        id="prediction",
        title="Client-side prediction and interpolation",
        tags=["Kalman filter", "extrapolation", "rollback"],
        summary="The network brings latency, so the client shows movement earlier than the server does: it predicts its own actions locally and interpolates everyone else's. Divergence is fixed with a soft correction, not a teleport.",
        detail=[
            "The classic scheme: input → the client applies movement immediately (prediction) → the server recomputes authoritatively → the client compares and corrects. Keep a ring buffer of inputs and states; when a server snapshot arrives, resimulate from the last confirmed tick (rollback). That is how Quake/Source and most shooters work.",
            "Other players are rendered with interpolation and a delay of roughly 100–150 ms: show the past, but smoothly. Extrapolation (continuing the current velocity) helps when packets are lost, but produces “rubber” opponents at sharp direction changes. A Kalman filter gives an optimal estimate of position and velocity given measurement noise: <b>x̂ₖ = x̂ₖ⁻ + K(zₖ − Hx̂ₖ⁻)</b>, where K depends on the ratio of process and measurement noise.",
            "Smoothing the error: the position and angle offset decay exponentially (usually over 100–200 ms) rather than snapping. For shooting you need lag compensation — the server rewinds hits to the client's firing moment, otherwise at 80 ms of ping you simply cannot hit moving targets. All of this requires synchronised clocks and a stable tick.",
        ],
        formula=("x̂ₖ = x̂ₖ⁻ + K·(zₖ − H·x̂ₖ⁻),   K = P⁻Hᵀ(HP⁻Hᵀ + R)⁻¹",
                 "Model: xₖ = F·xₖ₋₁ + w, zₖ = H·xₖ + v. For position+velocity F = [[1, dt], [0, 1]], H = [1, 0]."),
        steps=[
            "Fix the server tick (say 30–60 Hz) and the snapshot protocol.",
            "The client applies its own input immediately and stores (tick, input, state) in a buffer.",
            "On a snapshot, find the confirmed tick, correct the state and resimulate the pending inputs.",
            "Render remote players with a delay and interpolation; enable extrapolation only for packet loss.",
            "Smooth the visual error and disable prediction for teleports and death.",
        ],
        complexity=("O(1) per tick plus O(buffer) for the resimulation", "O(input buffer)",
                    "A buffer of 1–2 seconds (60–120 ticks) is enough; longer is more expensive and unnecessary."),
        code=("csharp", """struct Input { public int tick; public float dt; public Vector2 move; }
struct Snapshot { public int tick; public Vector3 pos; public Vector3 vel; }

class PredictedPlayer
{
    readonly Queue<Input> pending = new();
    Vector3 position, velocity;

    public void OnLocalInput(Input i)      // applied locally, immediately
    {
        pending.Enqueue(i);
        Simulate(ref position, ref velocity, i);
    }

    public void OnServerSnapshot(Snapshot s)
    {
        position = s.pos;                   // authoritative state
        velocity = s.vel;
        foreach (var i in pending)          // resimulate the unconfirmed inputs
            if (i.tick > s.tick) Simulate(ref position, ref velocity, i);
    }

    void Simulate(ref Vector3 p, ref Vector3 v, Input i)
    {
        v += new Vector3(i.move.x, 0, i.move.y) * accel * i.dt;
        v *= Mathf.Pow(damping, i.dt);
        p += v * i.dt;
    }
}"""),
        pitfalls=[
            "Teleport corrections kill the feel of control — smooth them and hide small errors.",
            "Extrapolation without a time limit produces opponents that slide into walls.",
            "Lag compensation without a history check lets players shoot “into the past” through walls — validate the line of fire.",
            "For deterministic physics, fix the update order and avoid float instability.",
        ],
        games=["CS:GO / CS2", "Valorant", "Overwatch", "Quake III Arena"],
    ),
    dict(
        id="anticheat",
        title="Anti-cheat: statistical anomaly detection",
        tags=["z-score", "anomalies", "trust"],
        summary="Anti-cheat is a layered system: an authoritative server, statistical anomaly detection, client-side checks and a ban economy. Z-score catches outliers, but you must be careful with false positives.",
        detail=[
            "Basic hygiene first: the server never trusts the client for position, damage or resources. The client sends input, the server sends the result. For particularly sensitive data, run the fog of war on the server: the client never receives enemy positions it cannot see. That removes a whole class of wallhacks without any statistics at all.",
            "Statistics: for every player, track metrics such as headshot ratio, reaction time, accuracy at long range, and the distribution of aim angles. The z-score <b>z = (x − μ)/σ</b> shows how far a metric has drifted from the population. But among millions of players you will find dozens of honest outliers, so use robust estimators (median/MAD), combinations of metrics and Bayesian priors rather than a single threshold.",
            "Detection without a reaction is worthless: review replays of suspicious matches, shadow ban suspects into a separate pool, ban in waves, and provide appeals. Client-side anti-cheats (signatures, memory integrity) raise the price of cheating but give no guarantees; kernel-level solutions are a privacy question of their own. The success metric is not “we caught everyone” but “playing honestly is comfortable”.",
        ],
        formula=("z = (x − μ)/σ,   robust: z′ = 0.6745·(x − median)/MAD",
                 "MAD = median(|x − median(x)|). |z′| > 3.5 is the classic outlier criterion for normal data."),
        steps=[
            "Close the basic holes: server authority, input validation, server-side fog of war.",
            "Collect telemetry: hits, latencies, angles, movement, economy — tagged per match.",
            "Build robust distributions per skill bucket rather than over the whole base.",
            "Fuse signals and send only the top percentiles to manual or ML review.",
            "Act in waves, keep evidence, offer appeals, and never reveal the thresholds.",
        ],
        complexity=("O(1) per metric, O(n) to recompute statistics", "O(#players·#metrics)",
                    "Threshold checks run in real time; distribution recomputation is offline, roughly daily."),
        code=("python", """import statistics as st

def robust_z(x, population):
    med = st.median(population)
    mad = st.median([abs(v - med) for v in population]) or 1e-9
    return 0.6745 * (x - med) / mad

def suspicious(player, population):
    signals = {
        "headshot_rate": robust_z(player["hs"], population["hs"]),
        "snap_angle":    robust_z(player["snap"], population["snap"]),
        "reaction_ms":  -robust_z(player["react"], population["react"]),
    }
    # require agreement between several signals, not a single outlier
    votes = sum(1 for v in signals.values() if v > 3.5)
    return votes >= 2, signals"""),
        pitfalls=[
            "One z-score threshold over the whole population produces a wave of false bans among strong players.",
            "Cheats adapt: the detector has to be updated and the thresholds kept secret.",
            "Kernel anti-cheats clash with privacy and with Linux/Steam Deck — take platforms into account.",
            "Public bans without evidence destroy trust; shadow bans and waves are better.",
        ],
        games=["Valve Anti-Cheat", "Riot Vanguard", "Easy Anti-Cheat", "BattlEye"],
    ),
    dict(
        id="lockstep",
        title="Deterministic lockstep simulation",
        tags=["fixed-point", "determinism", "lockstep"],
        summary="An RTS does not transmit the world state, it transmits player commands: every client simulates the same thing and reaches the same result. That demands strict determinism — integer maths and a fixed update order.",
        detail=[
            "Lockstep: every tick clients send their commands, wait for everyone's commands, and only then compute the next tick. Traffic is minimal (a few kilobytes per match) and a replay is just a command log. The price is that latency equals the slowest player, and any divergence (desync) breaks the match.",
            "Determinism requires: a fixed step (say 20 ticks per second), integer or fixed-point arithmetic (Q16.16), a stable iteration order for containers, the same RNG implementation everywhere (xorshift with a saved state), no dependence on wall-clock time, and no reliance on hash-table ordering. Float arithmetic can produce different bits on different CPUs and compilers — the classic source of desync bugs.",
            "Verification: each client hashes its state (CRC/FNV) every N ticks and compares. On a mismatch, save the state and the replay for analysis. To go faster, shard the simulation and parallelise with a fixed merge order; to smooth it visually, interpolate between ticks and predict your own units.",
        ],
        formula=("x<sub>Q16.16</sub> = round(x·2<sup>16</sup>),   a·b → (a·b) >> 16,   hash = FNV-1a(state)",
                 "Tick: 20–30 Hz. Commands are applied at tick T + delay, identically for everyone."),
        steps=[
            "Fix the tick rate and forbid any dependence of the simulation on real time.",
            "Move the game maths to fixed point or integers; check trigonometry and sqrt separately.",
            "Make the RNG part of the world state and include it in the hash.",
            "Sort every traversal (entities, collisions, timers) by a stable key.",
            "Compare hashes between clients and keep replays for desync debugging.",
        ],
        complexity=("O(#entities) per tick, O(1) per command", "O(world state)",
                    "The simulation must fit into 1/20 s; rendering is interpolated separately."),
        code=("csharp", """// Q16.16 fixed point: determinism matters more than precision
public readonly struct Fix
{
    public const int FRAC = 16;
    public readonly int Raw;
    Fix(int raw) { Raw = raw; }

    public static Fix FromInt(int v) => new(v << FRAC);
    public static Fix operator +(Fix a, Fix b) => new(a.Raw + b.Raw);
    public static Fix operator -(Fix a, Fix b) => new(a.Raw - b.Raw);
    public static Fix operator *(Fix a, Fix b) =>
        new((int)(((long)a.Raw * b.Raw) >> FRAC));   // 64-bit intermediate
    public float ToFloat() => Raw / 65536f;
}

// Deterministic RNG (xorshift32); the state belongs to the world
public struct Rng
{
    public uint State;
    public uint Next() { State ^= State << 13; State ^= State >> 17; State ^= State << 5; return State; }
}"""),
        pitfalls=[
            "Float arithmetic and different sin/cos libraries cause desync between platforms.",
            "The iteration order of Dictionary/HashSet is not deterministic — sort the keys.",
            "One slow player slows everyone down; you need a timeout and a handover to AI control.",
            "A replay is a command log plus a simulation version; after a patch old replays no longer reproduce.",
        ],
        games=["StarCraft", "Age of Empires II", "Supreme Commander", "0 A.D."],
    ),
    dict(
        id="snapshot",
        title="Snapshot compression and delta encoding",
        tags=["Shannon entropy", "quantisation", "delta"],
        summary="The network is expensive, so you transmit changes rather than “the whole world”: deltas, quantised values and bit masks. Information theory sets the lower bound and tells you where it is safe to lose precision.",
        detail=[
            "Shannon entropy <b>H(X) = −Σ p(x)·log₂ p(x)</b> is the average number of bits per symbol under optimal coding. If a unit position has 1024 possible values it needs 10 bits, not 32. Quantising position to 1 cm and rotation to 1° saves three to four times the bandwidth with no visible loss.",
            "Delta encoding: send only the fields that changed since the confirmed snapshot, plus a bit mask of the changes. The baseline is the last <i>confirmed</i> snapshot, not the last one you sent — otherwise a lost packet breaks the whole chain. On top of that: change of basis (positions relative to a reference), areas of interest (close objects update more often and more precisely) and packet compression (zstd/lz4).",
            "Budgets: aim for 10–30 KB/s per player in a shooter and 2–5 KB/s in an RTS. Measure not only the average bitrate but the tail (99th percentile) — the tail is what causes lag. Evaluate every field by “bits × change frequency”; in practice 80 % of the traffic is positions and rotations.",
        ],
        formula=("H = −Σ pᵢ·log₂ pᵢ,   bits ≈ log₂(range/step)",
                 "A position in 0–1024 m with a 0.01 m step needs 17 bits instead of 32. A quaternion: three components at 10–12 bits (smallest-three)."),
        steps=[
            "Inventory the state fields and how often each changes.",
            "Quantise with a tolerance the player cannot notice (scale the scene and the speed).",
            "Build deltas against the confirmed baseline and send a change bit mask.",
            "Prioritise objects by visibility and distance (AOI) and update them at different rates.",
            "Measure the 99th percentile of snapshot size and loss, not just the average.",
        ],
        complexity=("O(#fields) per snapshot, O(n log n) to sort priorities", "O(baseline) + buffer",
                    "Coding is cheap; assembling and sorting the state and testing visibility cost more."),
        code=("python", """import math

def quantize(value, min_v, max_v, bits):
    levels = (1 << bits) - 1
    t = (value - min_v) / (max_v - min_v)
    q = max(0, min(levels, int(round(t * levels))))
    return q

def dequantize(q, min_v, max_v, bits):
    levels = (1 << bits) - 1
    return min_v + (q / levels) * (max_v - min_v)

def delta(baseline, current, mask_fields):
    bits = 0
    changed = []
    for name, mask in mask_fields.items():
        if baseline.get(name) != current.get(name):
            bits += mask
            changed.append(name)
    return changed, bits

def entropy(counts, total):
    return -sum((c/total) * math.log2(c/total) for c in counts if c)"""),
        pitfalls=[
            "A delta against the last sent snapshot instead of the last confirmed one breaks when a packet is lost.",
            "Coarse quantisation produces camera jitter and jerky interpolation.",
            "Without AOI the client receives the whole map — traffic and cheats both grow.",
            "Compressing already compressed textures or animations gains little; compress structured state instead.",
        ],
        games=["Quake III (delta snapshots)", "Overwatch", "Planetside 2", "EVE Online"],
    ),
    dict(
        id="planets",
        title="Procedural planetary systems",
        tags=["Kepler's laws", "n-body", "habitable zone"],
        summary="A planetary system is a hierarchy of orbits where the star's mass sets the scale of time and the orbital radius sets the climate. For gameplay, Keplerian orbits and sensible placement rules beat a full n-body simulation.",
        detail=[
            "Kepler's third law: <b>T² = 4π²a³/(G(M+m))</b>. It ties the period to the semi-major axis, so a system is easy to generate in “astronomical units and years”: for a solar-mass star T(years) = a(AU)<sup>1.5</sup>. Kepler's equation M = E − e·sin E is solved with Newton's method to get the true anomaly and the position on the ellipse.",
            "Plausibility rules: orbits are nearly coplanar (±5°), periods form resonances (2:1, 3:2), gas giants sit further out, rocky planets closer in, and the habitable zone lies where the flux is roughly Earth's. A full n-body simulation is overkill for gameplay and inherently chaotic; use it for spectacle, not for stable orbits.",
            "Climate: stellar flux <b>F = L/(4πa²)</b>, equilibrium temperature T ≈ 278·(L/L☉)<sup>1/4</sup>/√(a/AU) K. Then albedo, greenhouse effect, tides and axial tilt. For the visuals, draw orbits on a logarithmic scale so distant planets stay on screen while the labels keep the real periods.",
        ],
        formula=("T² = 4π²a³ / (G(M+m)),   M = E − e·sin E,   F = L/(4πa²)",
                 "T in seconds, a in metres, M in kg. In game units: T(years) ≈ √(a(AU)³/M(M☉))."),
        steps=[
            "Define the star: mass, luminosity, spectral class, age.",
            "Place planets with a log-uniform distribution of semi-major axes, forbidding overlaps.",
            "Add eccentricities and inclinations, then check stability over 10⁴ orbits.",
            "Compute flux and temperature, assign biome and atmosphere.",
            "Build the visualisation with scaling and labels; compute orbits analytically.",
        ],
        complexity=("O(#planets) per tick, O(iterations) to solve Kepler", "O(#bodies)",
                    "Analytical orbits cost O(1) per body; n-body is O(n²) and chaotic."),
        code=("python", """import math

def orbital_period_years(a_au, star_mass_solar=1.0):
    return math.sqrt(a_au ** 3 / star_mass_solar)   # Kepler's third law

def solve_kepler(M, e, tol=1e-10, iters=30):
    E = M
    for _ in range(iters):
        d = (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        E -= d
        if abs(d) < tol: break
    return E

def position(a, e, E):
    x = a * (math.cos(E) - e)
    y = a * math.sqrt(1 - e*e) * math.sin(E)
    return x, y

def equilibrium_temp(luminosity_solar, a_au, albedo=0.3):
    flux = luminosity_solar / (a_au ** 2)
    return 278.5 * flux ** 0.25 * (1 - albedo) ** 0.25"""),
        pitfalls=[
            "Real scales (AU against planet radii) do not fit on screen — use a log scale and separate scenes.",
            "Random orbits without overlap checks produce instant collisions and impossible systems.",
            "n-body with a game-sized step is unstable: planets scatter or fall into the star.",
            "The habitable zone is not a guarantee of life: you also need an atmosphere, a magnetic field and a stable orbit.",
        ],
        games=["Elite Dangerous", "No Man's Sky", "Kerbal Space Program", "Universe Sandbox"],
    ),
    dict(
        id="maps",
        title="Balanced strategy map generation",
        tags=["graph theory", "symmetry", "fairness"],
        summary="Map balance is not “identical starting zones” but equality of opportunity: connectivity, distance to resources, number of entrances and defensive value. You verify that with graphs and metrics.",
        detail=[
            "First generate the geometry (noise, regions, rivers), then build a connectivity graph of passable zones: nodes are areas, edges are passages, weights are path cost. Then evaluate the map with metrics: graph diameter, distance from each start to the resources, the number of chokepoints (articulation points), the share of passable area, and symmetry about axes or under rotation.",
            "Symmetry comes in mirror (point symmetry — a 180° rotation, as in most RTS maps), axial and rotational flavours. It guarantees equal distances and timings, but makes maps predictable. Asymmetric maps are more interesting, yet they need compensation: different resources, different defence, different expansion speed — and a check that no side has a first-move advantage.",
            "Validation: run thousands of bot matches on generated maps, look at win rates per race and per slot, time to first contact, and access to critical resources. A map where one start has three entrances and the other has one is broken, however pretty it looks. Often the cheapest path is to generate half and mirror it rather than balancing asymmetry heuristically.",
        ],
        formula=("fairness = Σ wᵢ·|metric(startᵢ) − mean(metrics)|,   between starts → 0",
                 "Metrics: distance to the nearest resources, to the centre, number of passages, share of “your” territory, time to key points."),
        steps=[
            "Generate terrain and resources from a seed and mark the passable regions.",
            "Build the connectivity graph and check that all starts sit in one component.",
            "Place starts symmetrically, or with compensation derived from the metrics.",
            "Compute the fairness metrics and reject maps with outliers.",
            "Run bots and watch the win-rate telemetry; when it is off, fix the rules rather than individual maps.",
        ],
        complexity=("O(V + E) for connectivity, O(V·k) for the metrics", "O(V + E)",
                    "Generation with rejection usually takes 10–100 attempts per accepted map."),
        code=("python", """from collections import deque

def bfs_dist(graph, start):
    dist, q = {start: 0}, deque([start])
    while q:
        u = q.popleft()
        for v, w in graph[u]:
            if v not in dist:
                dist[v] = dist[u] + w
                q.append(v)
    return dist

def fairness(graph, starts, resources):
    scores = {}
    for s in starts:
        d = bfs_dist(graph, s)
        reachable = [d[r] for r in resources if r in d]
        scores[s] = sum(sorted(reachable)[:3]) / 3   # the 3 nearest resources
    mean = sum(scores.values()) / len(scores)
    spread = max(abs(v - mean) for v in scores.values())
    return mean, spread          # spread measures the imbalance"""),
        pitfalls=[
            "Perfect symmetry makes every match identical — add controlled asymmetry in decoration and timings.",
            "Grid connectivity does not guarantee connectivity for units of different sizes (tanks, aircraft).",
            "Resources reachable through a single narrow point create a bottleneck and a snowball.",
            "Distance-based balance ignores race speed — metrics must be expressed in game seconds.",
        ],
        games=["StarCraft II (ladder maps)", "Age of Empires IV", "Warcraft III", "Northgard"],
    ),
    dict(
        id="ecosystem",
        title="Lotka–Volterra ecosystems",
        tags=["Lotka–Volterra", "dynamical systems", "trophic webs"],
        summary="An ecosystem is a system of differential equations for “predator vs prey” plus the rules of a trophic web. Simple equations give cycles, but for a game stability matters more than mathematical beauty.",
        detail=[
            "The basic model: <b>dx/dt = αx − βxy</b> (prey), <b>dy/dt = δxy − γy</b> (predator). The solution is closed cycles around the equilibrium: populations oscillate without damping. In a game that looks like waves of population, but in practice numbers fall to zero because of discreteness and randomness. So add environmental capacity (logistic growth) and noise.",
            "Logistics: dx/dt = αx(1 − x/K) − βxy. With capacity K the system gains a stable focus or a limit cycle. With three or more species, chaos and extinctions become possible; to keep the ecosystem alive use “immigration” (spawning from a pool), refuges (prey hide), seasonality and upper/lower bounds on predators.",
            "For gameplay a discrete per-tick model is more practical: <b>x′ = clamp(x + (births − deaths − predation)·dt)</b> with whole individuals. Simulate populations, not every wolf; individual behaviour belongs in a separate system (boids/FSM). The player must see the causal chain: kill the deer and the wolves come to the village — otherwise the simulation is unreadable.",
        ],
        formula=("dx/dt = αx(1 − x/K) − βxy,   dy/dt = δxy − γy",
                 "α — prey birth rate, β — predator efficiency, δ — biomass conversion, γ — predator death rate, K — carrying capacity."),
        steps=[
            "Define the species and the trophic links; start with 3–5 species, no more.",
            "Choose parameters so the equilibrium is stable for reasonable initial conditions.",
            "Add stochasticity, seasonality and immigration to avoid extinction to zero.",
            "Discretise per tick and clamp the values; watch the populations over long runs.",
            "Show the populations in the UI — otherwise the player cannot tell that the ecosystem works at all.",
        ],
        complexity=("O(#species²) per tick", "O(#species)",
                    "A 20-species ecosystem is cheap; individual behaviour is what costs."),
        code=("python", """def ecosystem_tick(prey, pred, alpha=1.1, beta=0.4,
                   delta=0.1, gamma=0.9, K=100.0, dt=0.1):
    d_prey = alpha * prey * (1 - prey / K) - beta * prey * pred
    d_pred = delta * prey * pred - gamma * pred
    prey = max(0.0, prey + d_prey * dt)
    pred = max(0.0, pred + d_pred * dt)
    return prey, pred

prey, pred = 20.0, 5.0
history = []
for _ in range(400):
    prey, pred = ecosystem_tick(prey, pred)
    history.append((prey, pred))   # oscillations damped out by K"""),
        pitfalls=[
            "Pure Lotka–Volterra without capacity gives undamped oscillations and extinction under discretisation.",
            "Too many species means chaos and unpredictability — start small and add complexity.",
            "The player cannot see a simulation that has no UI and no explicit consequences (hunger, migration, attacks).",
            "A species going extinct breaks the content — plan for immigration or a pool reset.",
        ],
        games=["WolfQuest", "The Hunter: Call of the Wild", "RimWorld", "Ecosystem"],
    ),
    dict(
        id="music",
        title="Procedural music with L-systems",
        tags=["L-systems", "music theory", "Markov chains"],
        summary="Music is generated on two levels: structure (forms, sections) with grammars and L-systems, and notes with Markov chains over scale and harmony. The constraints of music theory make randomness meaningful.",
        detail=[
            "An L-system is a parallel rewriting grammar: an axiom is expanded by rules N times, then the symbols are interpreted as musical events. For example F → F+G, G → F−G produces self-similar rhythmic figures. Unlike plain randomness, L-systems produce structure with repetition and variation — which is what the brain hears as music.",
            "Harmony: choose chords from a scale by functional logic (tonic–subdominant–dominant) or with a Markov chain trained on a corpus. The melody is a random walk over chord tones with a pull towards stable scale degrees; strong beats carry chord tones, weak beats passing tones. Rhythm comes from trees or Euclidean rhythms (E(5,8) gives the “cubian” pattern).",
            "For adaptive music (vertical remixing) tracks are split into layers: bass, harmony, melody, percussion. Layer gain follows gameplay intensity, and tempo and key stay synchronised. Seamlessness matters: switch on bar boundaries, not at random moments, and use “stinger” phrases for events.",
        ],
        formula=("A → B, B → A+B (L-system),   P(note<sub>i</sub> | note<sub>i−1</sub>, chord)",
                 "Euclidean rhythm E(k, n): k beats spread as evenly as possible over n steps — a hit when floor(i·k/n) changes."),
        steps=[
            "Define the scale, tempo, time signature and the set of layers.",
            "Generate a rhythmic pattern (Euclidean rhythm or an L-system).",
            "Generate the chord progression with functional logic or a Markov chain.",
            "Build the melody on chord tones with limits on intervals and range.",
            "Tie layer intensity to gameplay and switch sections on bar boundaries.",
        ],
        complexity=("O(pattern length) to generate", "O(#layers·#samples)",
                    "A sequencer one bar ahead takes milliseconds; synthesis and samples are the expensive part."),
        code=("python", """import random

SCALE = [0, 2, 4, 5, 7, 9, 11]        # ionian scale
CHORDS = {"I": [0, 4, 7], "IV": [5, 9, 12], "V": [7, 11, 14], "vi": [9, 12, 16]}

def lsystem(axiom, rules, iterations):
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(c, c) for c in s)
    return s

def euclid(k, n):
    return [1 if ((i * k) % n) < k else 0 for i in range(n)]

def melody(progression, steps=16, rng=random):
    notes, degree = [], 0
    for bar, chord in enumerate(progression):
        for i in range(steps):
            if rng.random() < 0.7:
                degree = max(-3, min(9, degree + rng.choice([-2, -1, 0, 1, 2])))
            octave, idx = divmod(degree, len(SCALE))
            tone = 12 * octave + SCALE[idx]
            if i % 4 == 0:                # strong beat: a chord tone
                tone = 12 * (degree // 7) + CHORDS[chord][i // 4 % 3]
            notes.append(tone)
    return notes"""),
        pitfalls=[
            "Pure randomness without a scale and harmony sounds out of tune; the constraints matter more than the generator.",
            "Seamless transitions are only possible on bar boundaries — keep the sequencer in sync.",
            "Endless variation is tiring: you need repetition and hooks, or the music is not memorable.",
            "Loud stingers over dialogue break the mix — use ducking.",
        ],
        games=["No Man's Sky", "Spore", "The Sims", "Proteus"],
    ),
]
