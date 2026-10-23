# -*- coding: utf-8 -*-
"""English versions of the code samples (only the comments are translated).

Topics that already carry their own `code` in research/topics_en_*.py win;
this table fills the gaps so that the English page never shows a Russian
comment inside a code block.
"""

CODE_EN = {
    "portals": ("csharp", """Matrix4x4 PortalMatrix(Transform entry, Transform exit)
{
    // from the entry's local space to world space and on to the exit
    var toEntry = Matrix4x4.TRS(entry.position, entry.rotation, Vector3.one).inverse;
    var fromExit = Matrix4x4.TRS(exit.position, exit.rotation, Vector3.one);
    return fromExit * toEntry;
}

void OnTriggerEnter(Collider other)
{
    var m = PortalMatrix(entry, exit);
    var rb = other.attachedRigidbody;
    rb.position = m.MultiplyPoint3x4(rb.position);
    rb.rotation = m.rotation * rb.rotation;
    rb.velocity = m.rotation * rb.velocity;   // rotate the velocity too
}"""),
    "topology": ("python", """def wrap_torus(x, y, w, h):
    return x % w, y % h

def wrap_mobius(u, v):
    \"\"\"u is in [0,1) along the strip, v is in [0,1) across it.\"\"\"
    flips = int(u // 1.0)          # how many seams we crossed
    u = u % 1.0
    v = v % 1.0
    if flips % 2:
        v = 1.0 - v               # non-orientability: the flip
    return u, v

def wrapped_delta(a, b, w):
    \"\"\"The shortest difference on a circle.\"\"\"
    d = (b - a) % w
    return d - w if d > w / 2 else d"""),
    "entanglement": ("python", """import math, random

def bell_correlate(a_angle, b_angle, rng=random):
    \"\"\"Returns a pair of outcomes with the correlation E = -cos(a - b).\"\"\"
    p_same = (1.0 - math.cos(a_angle - b_angle)) / 2.0
    a = 0 if rng.random() < 0.5 else 1
    # for a singlet: equal outcomes are rare at a small angle
    b = a if rng.random() < p_same else 1 - a
    return a, b

def chsh(samples=20000, rng=random.Random(1)):
    angles = (0, math.pi/4, math.pi/8, 3*math.pi/8)
    def E(a, b):
        pairs = [bell_correlate(a, b, rng) for _ in range(samples)]
        return sum(1 if x == y else -1 for x, y in pairs) / samples
    return (E(angles[0], angles[2]) - E(angles[0], angles[3])
            + E(angles[1], angles[2]) + E(angles[1], angles[3]))"""),
    "chaos": ("python", """import math

def logistic(r, x0=0.5, n=1006, skip=100):
    x, out = x0, []
    for i in range(n + skip):
        x = r * x * (1 - x)
        if i >= skip:
            out.append(x)
    return out

def lyapunov(r, x0=0.5, n=2006, skip=200):
    x, total = x0, 0.0
    for i in range(n + skip):
        x = r * x * (1 - x)
        if i >= skip:
            d = abs(r * (1 - 2 * x))
            total += math.log(d) if d > 1e-12 else -30
    return total / n          # > 0 means chaos

def lorenz_step(p, dt=0.01, sigma=10, rho=28, beta=8/3):
    x, y, z = p
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return (x + dx*dt, y + dy*dt, z + dz*dt)"""),
    "weaponbalance": ("python", """import statistics as st

def ttk(hp, damage, rpm, accuracy=1.0, reload_time=0.0, engagement=2.0):
    dps = damage * rpm / 60.0
    eff = dps * accuracy / (1.0 + reload_time / max(engagement, 1e-6))
    return hp / max(eff, 1e-6)

def winrate_ci(wins, n, z=1.96):
    p = wins / n
    se = (p * (1 - p) / n) ** 0.5
    return p, (p - z*se, p + z*se)

def simple_regression(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    var = sum((x-mx)**2 for x in xs)
    beta = cov / var if var else 0.0
    return beta, my - beta*mx      # the slope and the offset"""),
    "matchmaking": ("python", """import math

def elo_update(ra, rb, score_a, k=24.0):
    ea = 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))
    eb = 1.0 - ea
    return ra + k * (score_a - ea), rb + k * ((1 - score_a) - eb)

def glicko_rd_decay(rd, c=34.6, periods=1):
    return math.sqrt(rd*rd + c*c*periods)

def match_quality(mu_a, sigma_a, mu_b, sigma_b, beta=4.17):
    \"\"\"TrueSkill: 1 is a perfectly even match, it drops towards 0 for a big gap.\"\"\"
    variance = 2 * beta * beta + sigma_a ** 2 + sigma_b ** 2
    quality = math.sqrt(2 * beta * beta / variance)
    return quality * math.exp(-(mu_a - mu_b) ** 2 / (2 * variance))"""),
    "trends": ("python", """def diff(series, lag=1):
    return [b - a for a, b in zip(series[:-lag], series[lag:])]

def seasonal_diff(series, s=7):
    return [series[i] - series[i-s] for i in range(s, len(series))]

def moving_average(series, window=7):
    out = []
    for i in range(len(series) - window + 1):
        out.append(sum(series[i:i+window]) / window)
    return out

def mape(actual, forecast):
    pairs = [(a, f) for a, f in zip(actual, forecast) if abs(a) > 1e-9]
    return 100.0 * sum(abs(a-f)/abs(a) for a, f in pairs) / max(len(pairs), 1)"""),
    "loot": ("python", """import random

RARITIES = [("common", 0.70), ("rare", 0.22), ("epic", 0.07), ("legendary", 0.01)]

def roll_rarity(rng=random, table=RARITIES):
    r, acc = rng.random(), 0.0
    for name, p in table:
        acc += p
        if r < acc:
            return name
    return table[-1][0]

class PityLoot:
    def __init__(self, hard_pity=90, soft_pity=75):
        self.counter, self.hard, self.soft = 0, hard_pity, soft_pity

    def open(self, rng=random):
        self.counter += 1
        p = 0.006 + max(0, self.counter - self.soft) * 0.06
        if self.counter >= self.hard or rng.random() < min(p, 1.0):
            self.counter = 0
            return "legendary"
        return roll_rarity(rng)"""),
    "visibility": ("python", """def aabb_in_frustum(box, planes):
    \"\"\"box = (minx,miny,minz,maxx,maxy,maxz); planes = [(nx,ny,nz,d)].\"\"\"
    for nx, ny, nz, d in planes:
        # the positive vertex for the sign of the normal
        px = box[3] if nx > 0 else box[0]
        py = box[4] if ny > 0 else box[1]
        pz = box[5] if nz > 0 else box[2]
        if nx*px + ny*py + nz*pz + d < 0:
            return False          # completely outside
    return True

def bsp_classify(point, plane):
    nx, ny, nz, d = plane
    v = nx*point[0] + ny*point[1] + nz*point[2] + d
    return "front" if v > 0 else ("back" if v < 0 else "on")"""),
    "ricochet": ("python", """import math, random

def reflect(v, n, restitution=0.75):
    dot = v[0]*n[0] + v[1]*n[1] + v[2]*n[2]
    return tuple(restitution * (v[i] - 2*dot*n[i]) for i in range(3))

def can_ricochet(v, n, max_angle_deg=15):
    speed = math.sqrt(sum(c*c for c in v)) or 1e-9
    dot = abs(sum(a*b for a, b in zip(v, n))) / speed
    return dot < math.cos(math.radians(max_angle_deg))

def scatter(v, spread_deg=2.0, rng=random):
    jitter = math.radians(spread_deg) * (rng.random() - 0.5)
    return (v[0] + jitter, v[1] + jitter * 0.5, v[2])"""),
    "voxels": ("python", """def sdf_sphere(p, c=(0, 0, 0), r=1.0):
    return ((p[0]-c[0])**2 + (p[1]-c[1])**2 + (p[2]-c[2])**2) ** 0.5 - r

def sdf_union(a, b):
    return min(a, b)

def sdf_subtract(a, b):
    return max(a, -b)

def sdf_smooth_union(a, b, k=0.1):
    h = max(k - abs(a - b), 0.0) / k
    return min(a, b) - h*h*k*0.25

def marching_edge(p1, p2, f1, f2):
    t = f1 / (f1 - f2) if abs(f1 - f2) > 1e-9 else 0.5
    return tuple(a + (b - a) * t for a, b in zip(p1, p2))"""),
    "textures": ("glsl", """float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {              // value noise
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i), b = hash(i + vec2(1, 0));
    float c = hash(i + vec2(0, 1)), d = hash(i + vec2(1, 1));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
    float sum = 0.0, amp = 0.5;
    for (int i = 0; i < 5; ++i) {
        sum += amp * noise(p);
        p *= 2.0; amp *= 0.5;
    }
    return sum;
}

// a periodic variant: take the noise modulo the period
vec3 normalFromHeight(float h, vec2 uv, float strength) {
    float dx = dFdx(h) * strength, dy = dFdy(h) * strength;
    return normalize(vec3(-dx, -dy, 1.0));
}"""),
    "distortion": ("glsl", """// a lens: a radial UV offset
vec2 lens(vec2 uv, vec2 center, float radius, float strength) {
    vec2 d = uv - center;
    float r = length(d);
    float m = 1.0 - smoothstep(radius * 0.6, radius, r);
    float k = strength * m * m;
    return uv - d * k * (r / radius);
}

// a swirl on the complex plane: w = z * exp(i * theta(r))
vec2 swirl(vec2 uv, vec2 center, float strength, float time) {
    vec2 d = uv - center;
    float r = length(d);
    float a = strength * exp(-r * r * 8.0) + time;
    float s = sin(a), c = cos(a);
    vec2 rot = vec2(d.x * c - d.y * s, d.x * s + d.y * c);
    return center + rot;
}

vec4 distort(sampler2D scene, vec2 uv, vec2 center) {
    vec2 warped = swirl(lens(uv, center, 0.35, 0.25), center, 2.0, 0.0);
    // chromatic aberration
    float r = texture(scene, warped + vec2(0.002, 0.0)).r;
    float g = texture(scene, warped).g;
    float b = texture(scene, warped - vec2(0.002, 0.0)).b;
    return vec4(r, g, b, 1.0);
}"""),
    "optics": ("glsl", """vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

float distributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float denom = NdotH * NdotH * (a2 - 1.0) + 1.0;
    return a2 / (3.14159 * denom * denom);
}

float geometrySmith(float NdotV, float NdotL, float roughness) {
    float k = (roughness + 1.0) * (roughness + 1.0) / 8.0;
    float gv = NdotV / (NdotV * (1.0 - k) + k);
    float gl = NdotL / (NdotL * (1.0 - k) + k);
    return gv * gl;
}

vec3 specularBRDF(vec3 N, vec3 V, vec3 L, vec3 F0, float roughness) {
    vec3 H = normalize(V + L);
    float NdotV = max(dot(N, V), 1e-4);
    float NdotL = max(dot(N, L), 0.0);
    float D = distributionGGX(N, H, roughness);
    float G = geometrySmith(NdotV, NdotL, roughness);
    vec3  F = fresnelSchlick(max(dot(H, V), 0.0), F0);
    return D * G * F / (4.0 * NdotV * NdotL + 1e-4);
}"""),
    "auctions": ("python", """import heapq

def vickrey(bids):
    \"\"\"bids: [(player, value)] -> (winner, price).\"\"\"
    ordered = sorted(bids, key=lambda b: b[1], reverse=True)
    winner = ordered[0][0]
    price = ordered[1][1] if len(ordered) > 1 else 0.0
    return winner, price

class OrderBook:
    def __init__(self):
        self.bids, self.asks = [], []      # max-heap / min-heap

    def add_bid(self, price, qty, owner):
        heapq.heappush(self.bids, (-price, owner, qty))

    def add_ask(self, price, qty, owner):
        heapq.heappush(self.asks, (price, owner, qty))

    def match(self):
        trades = []
        while self.bids and self.asks and -self.bids[0][0] >= self.asks[0][0]:
            bp, buyer, bq = heapq.heappop(self.bids)
            ap, seller, aq = heapq.heappop(self.asks)
            qty = min(bq, aq)
            trades.append((buyer, seller, -bp, ap, qty))
            if bq > qty: heapq.heappush(self.bids, (bp, buyer, bq - qty))
            if aq > qty: heapq.heappush(self.asks, (ap, seller, aq - qty))
        return trades"""),
    "resources": ("python", """def greedy_allocate(workers, jobs, priority):
    \"\"\"jobs: [(name, need_workers, value)] -> the allocation.\"\"\"
    plan, left = {}, workers
    for name, need, value in sorted(jobs, key=priority, reverse=True):
        take = min(need, left)
        if take:
            plan[name] = take
            left -= take
        if left == 0:
            break
    return plan, left

jobs = [("food", 4, 10), ("wood", 3, 6), ("stone", 2, 8), ("gold", 2, 4)]
plan, idle = greedy_allocate(8, jobs, priority=lambda j: j[2] / j[1])
print(plan, idle)"""),
    "inflation": ("python", """def inflation_rate(delta_money_pct, delta_velocity_pct, delta_output_pct):
    return delta_money_pct + delta_velocity_pct - delta_output_pct

def price_index(prices, weights):
    return sum(p * w for p, w in zip(prices, weights)) / sum(weights)

def wealth_tax(wealth, threshold, rate=0.01):
    \"\"\"A progressive sink: only the amount above the threshold is taxed.\"\"\"
    return max(0.0, wealth - threshold) * rate

# example: +12% money, +1% velocity, +5% output -> an inflation of about 8%
print(inflation_rate(12, 1, 5))"""),
    "audio3d": ("python", """import math

SPEED_OF_SOUND = 343.0
HEAD_WIDTH = 0.18

def itd_ild(azimuth_deg, distance=2.0):
    \"\"\"A simple model: the delay and the level difference between the ears.\"\"\"
    theta = math.radians(azimuth_deg)
    path_diff = HEAD_WIDTH * math.sin(theta)
    itd = path_diff / SPEED_OF_SOUND          # seconds
    ild_db = 20.0 * math.log10(max(1e-3, (distance - path_diff/2) /
                                        (distance + path_diff/2)))
    return itd, ild_db

def distance_gain(distance, ref=1.0, rolloff=1.0):
    return ref / (ref + rolloff * max(0.0, distance - ref))

def air_absorption(freq_hz, distance_m):
    # simplified: high frequencies die away faster
    return math.exp(-distance_m * (0.001 + freq_hz * 2e-6))"""),
    "instruments": ("python", """import random

def karplus_strong(freq, duration, sample_rate=44100, decay=0.996):
    n = int(sample_rate / freq)
    buffer = [random.uniform(-1, 1) for _ in range(n)]
    out, idx = [], 0
    prev = 0.0
    for _ in range(int(duration * sample_rate)):
        cur = buffer[idx]
        out.append(cur)
        # a low-pass filter plus the losses
        new = 0.5 * (cur + prev) * decay
        buffer[idx] = new
        prev = cur
        idx = (idx + 1) % n
    return out

# 220 Hz, 2 seconds - a recognisable plucked string
samples = karplus_strong(220.0, 2.0)"""),
    "gan": ("python", """# pseudocode of a WGAN-GP training step (PyTorch-like)
for real in loader:
    z = torch.randn(batch, latent_dim)
    fake = G(z).detach()
    # the discriminator maximises E[D(real)] - E[D(fake)]
    loss_d = -(D(real).mean() - D(fake).mean()) + gp * gradient_penalty(D, real, fake)
    opt_d.zero_grad(); loss_d.backward(); opt_d.step()

    fake = G(torch.randn(batch, latent_dim))
    loss_g = -D(fake).mean()          # the generator wants to fool D
    opt_g.zero_grad(); loss_g.backward(); opt_g.step()

def gradient_penalty(D, real, fake, lambda_=10.0):
    alpha = torch.rand(real.size(0), 1, 1, 1)
    mixed = (alpha * real + (1 - alpha) * fake).requires_grad_(True)
    grad = torch.autograd.grad(D(mixed).sum(), mixed, create_graph=True)[0]
    return lambda_ * ((grad.flatten(1).norm(2, dim=1) - 1) ** 2).mean()"""),
    "upscaling": ("glsl", """vec3 temporalUpscale(vec2 uv, vec2 motion, sampler2D current,
                        sampler2D history, sampler2D depth, float blend) {
    vec2 prevUv = uv - motion;
    vec3 h = texture(history, prevUv).rgb;
    vec3 c = texture(current, uv).rgb;

    // a neighbourhood clamp against ghosting
    vec3 lo = c, hi = c;
    for (int i = -1; i <= 1; ++i)
        for (int j = -1; j <= 1; ++j) {
            vec3 s = texture(current, uv + vec2(i, j) * texel).rgb;
            lo = min(lo, s); hi = max(hi, s);
        }
    h = clamp(h, lo, hi);

    float w = blend * (1.0 - smoothstep(0.01, 0.1, length(motion)));
    return mix(c, h, w);
}"""),
    "gpu-profiling": ("python", """class GpuProfiler:
    \"\"\"Accounting of the passes via timestamp queries and counters.\"\"\"
    def __init__(self):
        self.passes = {}          # name -> list of durations
        self.counters = {}        # name -> value

    def begin_pass(self, name):
        self._t0 = time.perf_counter()   # a real API uses a timestamp query here

    def end_pass(self, name):
        dt = (time.perf_counter() - self._t0) * 1000.0
        self.passes.setdefault(name, []).append(dt)

    def set_counter(self, name, value):
        self.counters[name] = value

    def report(self, budget_ms=16.6):
        rows = []
        for name, vals in sorted(self.passes.items()):
            vals = sorted(vals)
            p95 = vals[min(len(vals) - 1, int(len(vals) * 0.95))]
            rows.append((name, round(sum(vals) / len(vals), 2), round(p95, 2)))
        rows.sort(key=lambda r: -r[2])
        over = [(n, p95) for n, _, p95 in rows if p95 > budget_ms]
        return {
            "passes": rows,
            "over_budget": over,
            "counters": self.counters,
            "gpu_total": round(sum(r[2] for r in rows), 2),
        }

# an expected output:
# passes: [('post', 3.1, 5.8), ('shadow', 2.0, 4.2), ('scene', 4.4, 9.1)]
# gpu_total: 19.1 ms with a budget of 16.6 -> fix post and scene first"""),
}
