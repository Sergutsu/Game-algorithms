# -*- coding: utf-8 -*-
"""English content for topics 31–47: optimisation, mathematical mechanics, statistics, geometry."""

TOPICS_EN_4 = [
    dict(
        id="profiling",
        title="Profiling and the frame budget",
        tags=["profiler", "frame budget", "p95", "throttling"],
        summary="Optimising without measuring is guessing. First fix the frame budget (16.6 ms at 60 Hz), then find out where it goes, and only then change code. Profile the tail, not the average: p95 and p99 show what players experience as stutter.",
        detail=[
            "The frame budget is a hard sum: 16.67 ms at 60 Hz, 8.33 ms at 120 Hz, 33.3 ms at 30 Hz. Inside the budget you divide time between subsystems: gameplay, physics, AI, animation, rendering (CPU and GPU), audio, input, streaming. The rule is simple: a subsystem that keeps exceeding its quota is either optimised or given a smaller quota — otherwise “optimising” one part eats another part's headroom.",
            "A profiler has to be cheap and always on: counters around subsystems, not just a flame graph in the editor. The key metric is not the average but percentiles: an average of 6 ms with a p99 of 40 ms means the game hitches ten times a second. Hitches — frames longer than 2× the budget — deserve their own hunt; they are almost always an allocation, a resource load, a shader compilation or a GPU synchronisation.",
            "Production profiling differs from studio profiling: the player has different hardware, different drivers and different thermal throttling. So you need built-in telemetry: frame time percentiles, the hottest systems (aggregated by name), driver version, GPU type. Throttling shows up as the frame rate dropping 15–25 % after ten minutes of play — that is not an engine bug but heat, and it is fixed with quality, not with code.",
        ],
        formula=("frame_time = sim + physics + ai + render_cpu + gpu + audio + io,   budget = 1 / target_fps",
                 "Quotas are set up front (say sim 4 ms, render_cpu 3 ms, gpu 7 ms). A profile is a distribution, not a number: look at p50/p95/p99 and the share of frames that fit the budget."),
        steps=[
            "Fix the target frame rate and convert it to milliseconds: 1/fps.",
            "Give each subsystem a quota and add counters that build a histogram, not just a “last frame” value.",
            "Find the three most expensive subsystems and the three main hitch sources (usually: allocation, streaming, shader compilation, readback).",
            "Track p50/p95/p99 and the share of frames inside the budget — those numbers show the real picture, not the average.",
            "Add telemetry: hardware, driver, clocks, temperature, build version — otherwise you are fixing someone else's problem.",
            "Verify on cold hardware (integrated GPU, 4K) and in long sessions where throttling kicks in.",
        ],
        complexity=("O(1) per frame if the counters are plain accumulators", "O(1) per counter",
                    "Profiling has to cost less than 1 % of a frame; otherwise nobody uses it."),
        code=("python", """import time, statistics, collections

class Profiler:
    \"\"\"Minimal counter: accumulates a histogram of frame times.\"\"\"
    def __init__(self):
        self.frames = collections.deque(maxlen=4096)
        self.sections = collections.defaultdict(lambda: collections.deque(maxlen=4096))

    def begin(self, name):
        return time.perf_counter()

    def end(self, name, t0):
        self.sections[name].append((time.perf_counter() - t0) * 1000.0)

    def frame(self, ms):
        self.frames.append(ms)

    def report(self):
        fr = sorted(self.frames)
        if not fr:
            return {}
        def pct(p):
            return fr[min(len(fr) - 1, int(len(fr) * p))]
        out = {
            "p50": round(pct(0.50), 2),
            "p95": round(pct(0.95), 2),
            "p99": round(pct(0.99), 2),
            "hitch%": round(100.0 * sum(1 for f in fr if f > 33.3) / len(fr), 2),
        }
        for name, vals in self.sections.items():
            out[name] = round(statistics.mean(vals), 2)
        return out

# usage:
# p = Profiler()
# t0 = p.begin("sim"); ...; p.end("sim", t0)
# p.frame(dt * 1000)"""),
        pitfalls=[
            "Optimising by the average: with p50 = 6 ms and p99 = 45 ms players still complain about lag.",
            "Profiling only in the editor: a release build has different caches, shaders and memory behaviour.",
            "Forgetting hitches — rare 200 ms frames spoil the impression far more than a steady 30 FPS.",
            "Measuring “frame time” as the gap between frames: that includes waiting for vsync, not just work.",
            "Trusting counters without measuring their own cost: a counter that costs 0.3 ms per frame distorts everything it measures.",
        ],
        games=["Unity Profiler", "Unreal Insights", "PIX", "RenderDoc", "Metal System Trace"],
    ),
    dict(
        id="batching",
        title="Batching, instancing and draw-call reduction",
        tags=["draw call", "instancing", "SRP Batcher", "indirect draw"],
        summary="A modern GPU does not die from triangles, it dies from draw calls: every call is a trip into the driver, a pipeline state change and a synchronisation. 1000 calls of 100 triangles hurt far more than 100 calls of 100 000 triangles.",
        detail=[
            "Each draw call switches pipeline state: shader, buffers, textures, blend, depth state. When the state changes, the GPU flushes internal caches (pipeline stalls) and the real cost of the call jumps from 1–2 µs to hundreds. Hence the rule: sort objects by material and by shader so that the number of switches is minimal — not “sort by Z for transparency” at any cost.",
            "Instancing draws N copies of one mesh in a single call: the poses come from a buffer and the variations (colour, wind, UV offset) from instance attributes. It scales linearly: 10 000 trees are one call instead of ten thousand. The limitation is that every copy shares one material. Different textures are solved with atlases, different shaders with texture arrays or bindless rendering.",
            "The next step is the modern approach: a GPU-driven pipeline where sorting, culling and command assembly happen on the GPU and the CPU issues a single command with an indirect buffer (see topic 60). A pragmatic middle ground is to sort on the CPU by key (shader, material, world chunk), merge neighbours and submit in batches. It also helps to separate “cost of the call” from “cost of the state change”: 500 calls with one material are cheaper than 50 calls that switch the shader every time.",
        ],
        formula=("frame_cpu ≈ draw_calls · c_call + state_changes · c_state + Σ shader_switches",
                 "Typical magnitudes: c_call ≈ 1–5 µs (CPU), c_state ≈ 10–100 µs on a pipeline cache miss. The goal is hundreds of draw calls and tens of state changes."),
        steps=[
            "Measure draw calls and state changes (RenderDoc and Pix give you the counters ready-made).",
            "Sort the scene by key (shader + material + world chunk) — on the CPU that is a cheap O(n log n) with cached keys.",
            "Merge objects that share a material into instances; pack textures into atlases or arrays.",
            "For thousands of identical objects, move to indirect draw and let the GPU pick what is visible.",
            "Watch the state changes: any shader or blend switch inside the loop is a sorting candidate.",
            "Do not batch what does not need drawing: cull first, batch second (topic 33).",
        ],
        complexity=("Sorting O(n log n), merging O(n)", "O(n) sorting keys",
                    "Cache the sort key — rebuilding string keys every frame costs more than the batching saves."),
        code=("csharp", """// Instancing one mesh with N poses and per-instance colours.
using UnityEngine;

public class InstancedProps : MonoBehaviour
{
    public Mesh mesh;
    public Material material;
    public Transform[] instances;

    static readonly int InstanceColorId = Shader.PropertyToID("_InstanceColor");

    void LateUpdate()
    {
        if (instances == null || instances.Length == 0) return;

        // The matrices are copied into the array once per frame - that is a memcpy, not a new.
        var matrices = new Matrix4x4[instances.Length];
        var colors = new Color[instances.Length];
        for (int i = 0; i < instances.Length; i++)
        {
            matrices[i] = instances[i].localToWorldMatrix;
            colors[i] = instances[i].GetComponent<Renderer>().sharedMaterial.color;
        }

        material.SetColorArray("_BaseColor", colors);   // per-instance data
        Graphics.DrawMeshInstanced(mesh, 0, material, matrices);
    }
}"""),
        pitfalls=[
            "Batching everything: merging objects that were going to be culled anyway only wastes time.",
            "Instancing different materials in one call is impossible — use an atlas, a texture array, or separate calls.",
            "Sorting transparent objects by Z while also minimising state changes — the two goals conflict.",
            "Allocating a new matrix array every frame (garbage): reuse the buffer.",
            "Confusing draw calls with “objects in the scene”: 5000 objects in 20 calls is perfectly fine.",
        ],
        games=["Unity SRP Batcher", "Unreal instanced static meshes", "Horizon Zero Dawn", "The Last of Us Part II"],
    ),
    dict(
        id="culling",
        title="Culling: frustum, occlusion and LOD",
        tags=["frustum culling", "occlusion", "LOD", "HLOD", "HZB"],
        summary="Culling answers the question “what does not need drawing at all”. Frustum culling removes what is behind the camera, occlusion culling removes what is hidden behind other objects, LOD changes detail with distance. Together they typically cut 70–95 % of the rendering work.",
        detail=[
            "Frustum culling is the cheapest test: six planes from the camera matrix, an object's AABB against them. Test objects against bounding volumes rather than one by one: one large BVH node that is culled takes all of its children with it.",
            "Occlusion culling answers the question frustum cannot: the object is in view but behind a wall. The classic approach is an occluder hierarchy — large potential “blockers” (walls, rooms) are picked, a depth buffer is rendered for them, and then a query asks whether this object is visible. It has to be asynchronous: the answer arrives one or two frames later, so the decision uses last frame's data, and a suddenly opened door gets an occlusion fade over 100–200 ms.",
            "LOD changes quality with distance without losing the silhouette, only simplifying the small stuff. The key is not “distance to the camera” but the on-screen size (pixel size): thresholds must differ per resolution and FOV. Transitions need cross-fades or dithering, otherwise you get popping. For huge worlds use HLOD — one merged model per group of objects — plus sector streaming.",
        ],
        formula=("visible = frustum_culled · occlusion_culled · lod_selected;   screen_size ≈ (2·r·f) / (d · tan(fov/2))",
                 "d — distance, r — object radius, f — focal length in pixels. Set the LOD threshold by screen size (e.g. 64 px for the highest level)."),
        steps=[
            "Compute the on-screen size of an object and pick the LOD by it, not by distance.",
            "Group objects into a hierarchy: a culled node culls all of its descendants.",
            "For occlusion culling, pick an occluder hierarchy and render only depth for it, at low resolution.",
            "Use the occlusion result with a delay of one to two frames and add a fade for sudden reveals.",
            "Enable temporal coherence: do not recompute culling for objects that have not moved and did not move the camera.",
            "Track not only draw calls in the HUD but also “culled %” — that is the main metric of a culling system.",
        ],
        complexity=("Frustum: O(n) or O(log n) with a BVH; occlusion: O(n) with queries", "O(n) for the scene",
                    "Occlusion culling needs GPU support: on older APIs depth queries are unavailable."),
        code=("python", """import math

def extract_frustum_planes(view_proj):
    \"\"\"Six planes (nx, ny, nz, d) from a view-projection matrix (column-major).
    A plane: normal.p + d = 0; a point is inside when it is > 0.\"\"\"
    m = view_proj
    rows = [
        [m[3] + m[0], m[7] + m[4], m[11] + m[8],  m[15] + m[12]],   # left
        [m[3] - m[0], m[7] - m[4], m[11] - m[8],  m[15] - m[12]],   # right
        [m[3] + m[1], m[7] + m[5], m[11] + m[9],  m[15] + m[13]],   # bottom
        [m[3] - m[1], m[7] - m[5], m[11] - m[9],  m[15] - m[13]],   # top
        [m[3] + m[2], m[7] + m[6], m[11] + m[10], m[15] + m[14]],   # near
        [m[3] - m[2], m[7] - m[6], m[11] - m[10], m[15] - m[14]],   # far
    ]
    planes = []
    for r in rows:
        nx, ny, nz, d = r
        inv = 1.0 / math.sqrt(nx * nx + ny * ny + nz * nz)
        planes.append((nx * inv, ny * inv, nz * inv, d * inv))
    return planes

def aabb_in_frustum(planes, center, half):
    \"\"\"AABB (center, half-extents) against a list of planes.\"\"\"
    for nx, ny, nz, d in planes:
        # distance from the centre to the plane minus the projected half-extent
        dist = nx * center[0] + ny * center[1] + nz * center[2] + d
        radius = half[0] * abs(nx) + half[1] * abs(ny) + half[2] * abs(nz)
        if dist < -radius:
            return False   # the AABB is entirely behind the plane
    return True"""),
        pitfalls=[
            "Culling by the object's AABB when the model is large and far away: a conservative culler only disables more than necessary, but it never breaks the picture.",
            "Picking LOD by distance without correcting for resolution: on 4K the switch happens far too late.",
            "Doing occlusion culling synchronously: waiting for a depth query is a direct path to a freeze.",
            "Ignoring temporal coherence: recomputing culling every frame costs more than the test itself.",
            "Forgetting HLOD and sector streaming: one detail level for 200 km² is 400 MB of video memory.",
        ],
        games=["Unreal World Partition", "Unity occlusion culling", "Horizon Zero Dawn", "Ghost of Tsushima"],
    ),
    dict(
        id="dod",
        title="Data-oriented design, SIMD and cache friendliness",
        tags=["SoA", "SIMD", "cache", "alignment", "AoS"],
        summary="Most game loops are not limited by arithmetic but by memory: the processor waits for data from DRAM. Data-oriented design lays data out so traversals run linearly through memory, and SIMD processes 4–16 values per instruction.",
        detail=[
            "AoS (an array of structs) is convenient for humans: `struct Transform { vec3 pos; quat rot; }`. But a loop that “updates all transforms” reads 28 bytes per object and uses maybe 12 of them, wasting cache lines (64 bytes). SoA (a struct of arrays) splits the data by field: all positions here, all angles there. Now the loop reads a dense position array — 12 bytes per object — and SIMD instructions handle four floats at once.",
            "The second layer is alignment and prefetching. A cache line is 64 bytes; a structure should occupy a whole number of lines (padding), and arrays should be aligned to 16/32 bytes for SIMD. False sharing — two threads writing to different fields of the same cache line — destroys multithreading: an “atomic” counter without padding can be ten times slower than a plain one.",
            "The rule of the data layer: lay out first, write code second. Hot arrays (positions, velocities, HP) that are rewritten every frame are kept apart from cold ones (item descriptions, texts) that are touched rarely. Structural patterns (ECS, components, systems) are a way to express that layout in code, not an end in itself.",
        ],
        formula=("memory_time ≈ (bytes_touched / bandwidth_peak) + (cache_misses · latency),   SIMD_speedup ≤ min(n_lanes, memory_bound_ratio⁻¹)",
                 "Cache: L1 ~1–2 ns, L2 ~4–12 ns, DRAM ~80–120 ns. One cache miss costs as much as dozens of instructions — which is why the order of data matters more than the amount of arithmetic."),
        steps=[
            "Write down the hot loops (physics, AI, animation) and count the bytes they read per frame.",
            "Convert the structures to SoA for the data that is rewritten every frame.",
            "Align arrays to 32 bytes and add padding where structures are written from different threads.",
            "Enable vectorisation: unroll the loop, avoid branches inside the iteration, use fma.",
            "Check whether the loop is memory-bound: if the arithmetic is nearly free but the time is large, memory is to blame.",
            "Measure on real hardware: desktop caches are generous, consoles and mobile are not.",
        ],
        complexity=("O(n) over the entities, but the constant drops by a factor", "O(n) instead of O(n · sizeof(struct))",
                    "The SIMD gain is capped by memory bandwidth: fix the data first, then the vectors."),
        code=("csharp", """using System.Runtime.CompilerServices;
using UnityEngine;

// SoA: dense arrays instead of an array of structs.
public struct ParticleSystem
{
    public Vector3[] Position;
    public Vector3[] Velocity;
    public float[] Life;

    public int Count;

    // [MethodImpl] + AggressiveInlining only help tiny functions;
    // the real win comes from the dense linear traversal.
    public void Integrate(float dt)
    {
        for (int i = 0; i < Count; i++)
        {
            // position and velocity sit next to each other - cache lines are used fully
            Position[i] += Velocity[i] * dt;
            Life[i] -= dt;
        }
    }

    public void CompressDead()
    {
        int w = 0;
        for (int i = 0; i < Count; i++)
        {
            if (Life[i] <= 0f) continue;         // swap-remove: O(1) per element
            Position[w] = Position[i];
            Velocity[w] = Velocity[i];
            Life[w] = Life[i];
            w++;
        }
        Count = w;
    }
}"""),
        pitfalls=[
            "Measuring FPS instead of the time of the loop: “it is 60 FPS now” may mean the bottleneck simply moved.",
            "Expecting 4× from SIMD: when the loop is memory-bound the speed-up is capped by bandwidth.",
            "Forgetting false sharing: neighbouring counters in one cache line nullify multithreading.",
            "Converting everything to SoA: cold data in SoA causes more transitions than it saves.",
            "Optimising before profiling: a structural rewrite costs more than it looks.",
        ],
        games=["Unity DOTS/ECS", "Unreal Mass Entity", "Doom (1993)", "Doom Eternal"],
    ),
    dict(
        id="jobs",
        title="Multithreading and the job system",
        tags=["job system", "work stealing", "tasks", "main thread"],
        summary="One frame is hundreds of independent jobs: physics, AI, animation, particles, audio, streaming. A job system splits them into tasks and hands them to threads. The main rule: keep the main thread idle and the frame predictable.",
        detail=[
            "The classic mistake is “parallelising the game loop”: the main thread still waits for the slowest thread, and shared data needs locks. The right shape is a job system: work is split into small tasks with explicit dependencies, a scheduler distributes them across workers, and results are read after a join. Dependencies are expressed as “reads from buffer X”, which is also what lets tasks migrate to the GPU.",
            "Work stealing solves the imbalance: workers take tasks from a shared queue and, when it is empty, from their neighbours' queues. The scheduler hands out large tasks first (visibility sorting) and small ones later (updating individual particles) so no thread idles. Scheduling must be deterministic when the network needs it, or you explicitly accept non-determinism and synchronise only the result.",
            "The main thread should only assemble the frame: read input, update the camera, issue render commands. Everything that can go to a worker goes. Latency matters too: a task that should take 0.1 ms but waited 5 ms in the queue hurts control feel far more than a frame-rate dip. Hence priorities: input and camera first, streaming and prediction last.",
        ],
        formula=("T_frame ≈ max(T_main, T_work / P) + T_sync,   efficiency = Σ T_task / (P · T_frame)",
                 "P — number of workers. Amdahl: with a sequential fraction s the speed-up is at most 1/(s + (1−s)/P). The scheduler aims for balance: std(duration of tasks) → 0."),
        steps=[
            "Measure the share of the main thread: if it is above 30 %, that is the first optimisation target.",
            "Split gameplay into tasks: physics per chunk, AI per unit, animation per character.",
            "Describe dependencies explicitly (buffer → buffer) and let the scheduler reorder independent tasks.",
            "Enable work stealing and priorities: input and camera first, streaming last.",
            "Cap the number of workers: two to four on mobile, closer to the core count on consoles, without hyper-threading.",
            "Measure always in a release build with debug code off: asserts and logging eat threads.",
        ],
        complexity=("O(n) over the tasks, O(1) to distribute one", "O(n) for the task queue",
                    "Workers = hardware threads, with one or two slots spare for the main thread."),
        code=("csharp", """using System.Collections.Concurrent;
using System.Threading.Tasks;

// Minimal job system: a queue plus work stealing.
public class JobSystem
{
    readonly ConcurrentQueue<Action>[] _queues;
    readonly System.Threading.CancellationTokenSource _stop = new();

    public JobSystem(int workers)
    {
        _queues = new ConcurrentQueue<Action>[workers];
        for (int i = 0; i < workers; i++) _queues[i] = new ConcurrentQueue<Action>();
        for (int i = 0; i < workers; i++)
        {
            int id = i;
            Task.Run(() => Worker(id), _stop.Token);
        }
    }

    public void Schedule(Action job) => _queues[0].Enqueue(job);

    void Worker(int id)
    {
        var own = _queues[id];
        while (!_stop.IsCancellationRequested)
        {
            if (own.TryDequeue(out var job))
            {
                try { job(); } catch (Exception e) { /* log it, do not kill the thread */ }
                continue;
            }
            // work stealing: take somebody else's job
            bool stole = false;
            for (int k = 1; k < _queues.Length; k++)
            {
                var other = _queues[(id + k) % _queues.Length];
                if (other.TryDequeue(out job)) { try { job(); } catch { } stole = true; break; }
            }
            if (!stole) System.Threading.Thread.Sleep(0);   // idle
        }
    }

    public void Dispose() { _stop.Cancel(); }
}"""),
        pitfalls=[
            "Parallelising the whole gameplay loop: the main thread still waits for the slowest worker.",
            "Sharing global data without synchronisation: “it usually works” is a data race that shows up on another platform.",
            "Forgetting priorities: streaming assets eats the threads and adds latency to input.",
            "Creating one task per object: 5000 tasks of 2 µs is pure overhead, not work.",
            "Expecting determinism from a free order: lockstep needs a fixed order or deterministic fixpoint iterations.",
        ],
        games=["Unreal Task Graph", "Unity Job System", "Doom Eternal", "Avatar: Frontiers of Pandora"],
    ),
    dict(
        id="memory",
        title="Memory: pools, GC and asset streaming",
        tags=["object pools", "GC", "fragmentation", "streaming", "virtual texturing"],
        summary="Memory is the one resource you cannot squeeze. You can optimise frame time, but you cannot optimise an out-of-memory crash — the game simply dies. So gameplay uses pools and arena allocators, and heavy assets are streamed on demand.",
        detail=[
            "Fragmentation is the main enemy: after thousands of small allocations and frees, large blocks no longer fit even though there is plenty free. Hence the rule for the hot path: allocate nothing in the game loop. Objects come from a pool, temporary arrays come from reusable buffers (arena/buffer pools) that grow as needed and reset in O(1).",
            "In managed languages this is also about GC pauses. Even short pauses break control feel. The answers: allocate outside the frame (on the loading screen), use incremental GC, avoid allocations in input handlers, and adopt a generational approach — “hot” objects stay in generation 0 and are not promoted.",
            "Assets are a separate story. Keeping the whole world in memory is impossible: 1000 4K textures at 32 MB each is 32 GB. Three mechanisms work: distance-based streaming (load a sector when the player is close, unload it when they are far), virtual texturing (virtual address → physical pages loaded on demand) and a memory budget with priorities (what to drop first). The unload strategy matters more than the load strategy: the player must never notice a texture disappearing.",
        ],
        formula=("peak = resident + streamed + transient + fragmentation_slack,   slack ≈ 10–20 % of the budget",
                 "Typical budgets: 4–8 GB of VRAM per game on PC, 1.5–3 GB on mobile, per class on consoles. Transient memory (frame buffers) is counted separately: it grows with the number of frames in flight."),
        steps=[
            "Take a memory profile: resident (by type), transient and fragmentation — CPU and GPU separately.",
            "Remove every allocation from the hot path: pools for objects, reusable buffers for temporary data.",
            "Set a memory budget per level and per world sector; on overflow, unload by priority.",
            "Implement streaming with hysteresis: do not unload a resource if the player may return in a second.",
            "Watch the transient buffers: their count grows with the frames in flight (CPU and GPU together) and causes OOM on weak hardware.",
            "Test the behaviour under memory pressure: the game must degrade, not crash.",
        ],
        complexity=("O(1) per pool acquire, O(n) to rebuild", "O(capacity) per pool",
                    "A pool without an upper bound is the same leak, only slower."),
        code=("python", """class Pool:
    \"\"\"Object pool with no runtime allocations.\"\"\"
    __slots__ = ("_free", "_factory", "_live")

    def __init__(self, factory, initial=0):
        self._factory = factory
        self._free = [factory() for _ in range(initial)]
        self._live = set()

    def acquire(self):
        if self._free:
            obj = self._free.pop()
        else:
            obj = self._factory()      # the only runtime allocation
        self._live.add(id(obj))
        return obj

    def release(self, obj):
        self._live.discard(id(obj))
        obj.reset()                   # reset the state, do not create a new one
        self._free.append(obj)

    @property
    def live_count(self):
        return len(self._live)

# The same in C++: a fixed-size pool plus a free list, no delete
# struct Pool { std::vector<Node*> free; Node* acquire(); void release(Node*); };"""),
        pitfalls=[
            "A pool without an upper bound: “temporary” objects pile up and eat memory just like a leak.",
            "Resetting the state when handing out rather than when returning: a forgotten reset produces a zombie object.",
            "Ignoring transient memory: frame buffers (CPU and GPU) grow with the delay in flight and cause OOM on weak hardware.",
            "Unloading instantly: the player sees a low-resolution flash — you need a fade and hysteresis.",
            "Assuming GC is “not a problem”: on mobile it is a 5–15 ms pause at the worst possible moment.",
        ],
        games=["Unity Addressables", "Unreal streaming levels", "Sea of Thieves", "Ratchet & Clank"],
    ),
    dict(
        id="portals",
        title="Portals and non-Euclidean geometry",
        tags=["projective geometry", "quaternions", "recursion"],
        summary="A portal is a transform of space: the camera sees the scene through a matrix that glues two places together. Portal recursion, clipping and correct physics all require careful handling of matrices and clip planes.",
        detail=[
            "A portal is defined by two rectangles (entry and exit) with normals. The view through a portal is a render with a transformed camera: <b>M = T<sub>exit</sub> · R<sub>exit</sub> · R<sub>entry</sub><sup>−1</sup> · T<sub>entry</sub><sup>−1</sup></b> (up to scale). Texture projection uses the same matrix; for recursion it is applied repeatedly, with a depth limit.",
            "Geometrically this is a projective gluing: a space where two planes are identified by a transformation. Quaternions are convenient for orientation (no gimbal lock), but a general portal transform includes a reflection or rotation plus a translation. A mirror portal flips the orientation, which breaks triangle winding — so either avoid reflections or invert culling and normals.",
            "The problems: clipping the geometry behind the portal (oblique near plane / clip plane) so you neither render too much nor see through the wall; recursion — rendering into a texture with a reduced resolution; physics — teleporting the object with a transformed velocity and angular momentum; and carrying the “camera” across. Non-Euclidean worlds (torus, Möbius strip) need portal glues at the seams or a coordinate wrap.",
        ],
        formula=("M<sub>portal</sub> = T<sub>exit</sub>·R<sub>exit</sub>·R<sub>entry</sub><sup>−1</sup>·T<sub>entry</sub><sup>−1</sup>",
                 "Velocity after crossing: v′ = R·v, where R is the relative rotation of the portals. For a mirror, reflect the normal component as well."),
        steps=[
            "Define a pair of portals with transforms and normals.",
            "Build the transition matrix and the projection matrix for the camera.",
            "Render the view through the portal into a texture with an oblique near plane.",
            "Limit the recursion by depth and reduce the resolution each level.",
            "When an object crosses the plane, carry over its transform and velocity.",
        ],
        complexity=("O(recursion depth · scene cost)", "O(portal texture)",
                    "Eight levels of recursion is eight scene renders; in practice two or three are enough."),
        pitfalls=[
            "Without an oblique near plane the camera sees geometry behind the portal and “cuts through” the wall.",
            "Mirror portals break culling and winding — invert the sides or forbid reflections.",
            "An object stuck in the portal plane teleports back and forth — use hysteresis and a normal check.",
            "Recursion without a limit on depth and resolution eats the entire frame budget.",
        ],
        games=["Portal", "Prey", "The Witness (perspective)", "Antichamber"],
    ),
    dict(
        id="topology",
        title="Topological gameplay (torus, Möbius)",
        tags=["topology", "glues", "Euler characteristic"],
        summary="A torus is a rectangle with opposite edges identified: leave on the right and you enter on the left. A Möbius strip adds a flip when you walk around it, which breaks orientation — and therefore the usual navigation.",
        detail=[
            "The torus comes from gluing opposite sides of a square: (x, y) ~ (x + W, y) ~ (x, y + H). The implementation is modular arithmetic on coordinates plus “ghost” copies of objects near the edges for rendering and physics. Radii and neighbour queries must account for the wrap, otherwise projectiles vanish at the edge and the AI cannot see an enemy “through the wall”.",
            "The Möbius strip is a glue with a flip: (0, y) ~ (1, 1 − y). Walking along the strip returns you to the same point with a flipped orientation; after two laps you are back to normal. That means non-orientability: there is no global “up” and “down”, and local coordinates have to be carried across the seam with a flip matrix. For the player it is a puzzle; for the code it is a source of bugs in normals and cameras.",
            "Topological invariants help the design: the Euler characteristic χ = V − E + F (torus: 0, sphere: 2, Klein bottle: 0) and the genus g = (2 − χ)/2. For gameplay this means constraints on cuts and glues: you cannot cut a torus into a sphere without changing the topology — and that can be a mechanic (as in some puzzle games).",
        ],
        formula=("Torus: (x, y) ~ (x mod W, y mod H),   Möbius: (0, y) ~ (1, 1 − y)",
                 "χ = V − E + F; g = (2 − χ)/2 for a closed orientable surface. Torus: χ = 0, g = 1."),
        steps=[
            "Choose the world representation: modular coordinates or explicit seam portals.",
            "Implement the wrap for positions, velocities, queries and rendering (ghost copies).",
            "For the Möbius strip, add an orientation transfer matrix when crossing the seam.",
            "Test the camera, lighting and physics at the seams — that is where orientation breaks.",
            "Keep it simple: the more seams there are, the harder it is to debug and to explain to the player.",
        ],
        complexity=("O(1) per wrap, O(k) per neighbour query", "O(world)",
                    "Ghost copies multiply the number of rendered objects by 2–9 near the borders."),
        pitfalls=[
            "Modular arithmetic without ghost copies makes objects “vanish” at the edges.",
            "A Möbius strip breaks normals and the camera up-vector: carry the orientation, not just the position.",
            "Navigation meshes do not cover the seams — the AI gets stuck at the border.",
            "It is hard for players to build a mental map: give them a mini-map with the wrap and hints.",
        ],
        games=["Pac-Man (torus)", "Hyperbolica", "Möbius games (jam)", "Antichamber"],
    ),
    dict(
        id="entanglement",
        title="Entanglement as a game mechanic",
        tags=["tensor algebra", "Hilbert space", "Bell"],
        summary="Entanglement is a correlation that cannot be explained by local hidden variables. For a game it is a “paired object” mechanic: the state of one instantly determines the measurement result of the other — but no information can be transmitted.",
        detail=[
            "The state of two qubits lives in the tensor product of the spaces: |ψ⟩ = α|00⟩ + β|01⟩ + γ|10⟩ + δ|11⟩. An entangled state cannot be factored into |a⟩⊗|b⟩; the canonical example is Bell's singlet (|01⟩ − |10⟩)/√2. The density matrix ρ = |ψ⟩⟨ψ|, and taking the partial trace yields a mixed state for one qubit — which is exactly why it looks random locally.",
            "The key fact: measuring one qubit in the Z basis gives 0 or 1 with equal probability, but the result of the other is perfectly correlated (for the singlet, opposite). Measuring at different angles gives a correlation of −cos θ, violating Bell's inequality (CHSH: |S| ≤ 2 classically, up to 2√2 quantumically). For gameplay this becomes a puzzle: “tune the measurement basis to get the correlation you need”.",
            "Design: entangled pairs as “linked objects” — an enemy and its shadow, two locks, a door and a bridge. The player cannot send a message but can exploit correlations if they know the basis. Always explain the rules in the language of mechanics rather than physics, and never give the player instant communication — that breaks both the physics and the balance.",
        ],
        formula=("|Φ⁺⟩ = (|00⟩ + |11⟩)/√2,   E(a,b) = −cos(a−b),   |S| ≤ 2√2",
                 "CHSH: S = E(a,b) − E(a,b′) + E(a′,b) + E(a′,b′). The classical limit is 2, the quantum limit 2√2 ≈ 2.828."),
        steps=[
            "Define the entangled pairs and what exactly correlates (state, damage, position).",
            "Provide the measurement bases the player can choose (angles, tools).",
            "Implement measurement as a probabilistic draw with the −cos θ correlation.",
            "Forbid information transfer: the second result is only known after the first is measured.",
            "Check the balance: correlations must not offer a free shortcut through the level.",
        ],
        complexity=("O(2ⁿ) for n qubits", "O(2ⁿ) amplitudes",
                    "Two or three qubits fit in a table of 4–8 numbers; more needs a simulator."),
        pitfalls=[
            "“Instant information transfer” through entanglement — physically wrong and balance-breaking.",
            "If the player cannot see the measurement basis, the correlation just looks like random noise.",
            "Save/load must preserve the correlations, otherwise save-scumming breaks the puzzle.",
            "Too much maths in the UI puts people off: show angles and results, not matrices.",
        ],
        games=["Quantum Conundrum", "Antichamber", "Schrödinger's Cat", "Qubit puzzles"],
    ),
    dict(
        id="chaos",
        title="Chaos, bifurcations and attractors",
        tags=["chaos theory", "attractors", "Lyapunov exponent"],
        summary="Chaos is sensitivity to initial conditions in a deterministic system. The logistic map and the Lorenz attractor are the canonical models, and the Lyapunov exponent measures how fast nearby solutions diverge.",
        detail=[
            "The logistic map: <b>x<sub>n+1</sub> = r·x<sub>n</sub>(1 − x<sub>n</sub>)</b>. Below r = 3 there is a stable fixed point, between 3 and 3.57 a cascade of period doubling, and beyond that chaos with windows of order. The bifurcation diagram is a beautiful, understandable UI tool: the player moves r and watches the behaviour change.",
            "The Lorenz attractor: dx/dt = σ(y − x), dy/dt = x(ρ − z) − y, dz/dt = xy − βz. The trajectory never repeats but stays in a bounded region (a strange attractor) and has a fractal dimension. For visuals, fading 3D lines are enough; for gameplay, it is a “chaotic” source of motion that still stays bounded.",
            "The Lyapunov exponent λ > 0 means exponential divergence: δ(t) ≈ δ₀·e<sup>λt</sup>. The practical consequence: chaotic systems cannot be predicted over a long horizon without enormous precision. In multiplayer that is fatal for determinism; in a single-player game it is a source of uniqueness. Use chaos deliberately: for background effects, never for critical simulation.",
        ],
        formula=("x<sub>n+1</sub> = r·x<sub>n</sub>(1 − x<sub>n</sub>),   λ = lim (1/n)·Σ ln|f′(xᵢ)|",
                 "Lorenz: σ = 10, ρ = 28, β = 8/3. λ > 0 means chaos; for Lorenz λ ≈ 0.9."),
        steps=[
            "Pick the map/system and the parameter the player will change.",
            "Build a bifurcation diagram or a phase portrait to tune it.",
            "Estimate the Lyapunov exponent and the horizon of predictability.",
            "Visualise the trajectories with fading and colour by time.",
            "Never use chaos for critical networked physics; for effects, bound the amplitude.",
        ],
        complexity=("O(n) per trajectory, O(N²) for the diagram", "O(trajectory length)",
                    "A 1000×1000 bifurcation diagram is a million iterations — seconds, not a problem."),
        pitfalls=[
            "Chaos in a networked game breaks determinism — keep it in the purely visual layer.",
            "A too large integration step sends Lorenz to infinity — reduce dt.",
            "Chaotic enemy movement reads as a bug rather than a design without a visual cue.",
            "Bifurcations are sensitive to the parameter: a small error in r changes the regime completely.",
        ],
        games=["Lorenz attractor demos", "Noita (chaotic sim)", "Chaos;Head", "Fractal games"],
    ),
    dict(
        id="weaponbalance",
        title="Weapon balance analysis (regression, ANOVA)",
        tags=["regression", "ANOVA", "TTK"],
        summary="Weapon balance is not checked by eye but with metrics: time to kill, DPS adjusted for misses, win rate and pick rate. Regression shows which characteristics actually predict strength.",
        detail=[
            "Theoretical weapon strength: TTK = HP/(damage × fire rate) adjusted for reloads and misses. Effective DPS = damage·RPM/60·accuracy/(1 + reload_time/engagement_time). But the key metric is not the number in a spreadsheet — it is the outcome: the weapon's win rate with the player's skill controlled (for example, per rank).",
            "Regression: <b>winrate ~ β₀ + β₁·dps + β₂·accuracy + β₃·range + ε</b>. The coefficients show which attribute outweighs the others. ANOVA compares groups (weapons, classes) and tests whether the differences are significant at all or just sampling noise. Always compute confidence intervals: with 500 matches a 2 % win-rate difference may be indistinguishable from chance.",
            "Pick rate is the most important metric: if a weapon is taken in 60 % of matches and wins 52 %, it dominates. The feedback loop: do not nerf the damage number — nerf what makes the weapon unavoidable (versatility, the lack of counter-picks). And test changes on simulations and bots before shipping, or balance patches become a lottery.",
        ],
        formula=("TTK = HP / (DPS·accuracy),   DPS = damage·RPM/60 / (1 + reload/engagement)",
                 "Regression: y = Xβ + ε; ANOVA: F = MS<sub>between</sub>/MS<sub>within</sub>, p < 0.05 means the difference is significant."),
        steps=[
            "Define the metrics: TTK, effective DPS, win rate, pick rate, survival.",
            "Collect per-match data with skill controlled (rating or rank).",
            "Fit the regression and test the significance of the coefficients.",
            "Compare groups with ANOVA and confidence intervals.",
            "Change one parameter per patch and measure the effect on win rate and pick rate.",
        ],
        complexity=("Regression O(n·p²), ANOVA O(n)", "O(n) samples",
                    "With millions of matches, aggregate first; with thousands, a laptop is enough."),
        pitfalls=[
            "Small samples give false conclusions: 200 matches per weapon is noise, not signal.",
            "Ignoring skill: strong players take the “meta”, so the weapon looks stronger than it is.",
            "A damage nerf does not remove dominance if the problem is versatility or the absence of counter-picks.",
            "Changing several parameters at once makes it impossible to tell what worked.",
        ],
        games=["CS2", "Valorant", "Apex Legends", "Rainbow Six Siege"],
    ),
    dict(
        id="matchmaking",
        title="Matchmaking with Elo, Glicko-2 and TrueSkill",
        tags=["Elo", "Glicko-2", "TrueSkill", "Bayesian"],
        summary="Matchmaking solves two problems: estimating a player's strength and assembling a match with equal chances. Elo is simple but unstable; Glicko-2 and TrueSkill model uncertainty and team play.",
        detail=[
            "Elo: expected result <b>E = 1/(1 + 10<sup>(R<sub>opp</sub>−R)/400</sup>)</b>, update R′ = R + K(S − E). Problems: K is fixed, uncertainty is not modelled, and a newcomer and a veteran with the same rating are treated as equal. Even so, Elo works excellently as a rating “currency” and players understand it.",
            "Glicko-2 adds a rating deviation (RD) and volatility: after a long break the RD grows and the rating moves faster — the system “re-checks” the player. TrueSkill is a Bayesian model for teams: a player's strength is a Gaussian N(μ, σ²), updated by Bayes' rule, and the matchmaker minimises the expected unfairness (the draw probability).",
            "In practice the matchmaker optimises more than equal strength: wait time, region, group size, role order. It usually uses an expanding search range and treats match “quality” as a function of the spread of ratings. Smurfs and boosting are a separate problem: you need fast calibration matches and anomaly detection on progress.",
        ],
        formula=("E = 1/(1 + 10<sup>(R<sub>b</sub>−R<sub>a</sub>)/400</sup>),   R′ = R + K(S − E)",
                 "TrueSkill: match quality = 2·Φ(μ<sub>diff</sub>/√(2β² + σ<sub>a</sub>² + σ<sub>b</sub>²)), where β is the “luck scale”."),
        steps=[
            "Choose the rating model: Elo for simplicity, Glicko-2 or TrueSkill for accuracy.",
            "Define the format: 1v1, teams, roles, group size.",
            "Set the match-quality function and the weights for wait time and region.",
            "Implement the expanding search and smurf protection (calibration, detection).",
            "Monitor the rating distribution, search time and the share of unfair matches.",
        ],
        complexity=("Elo O(1), TrueSkill O(#players³) per match (naive)", "O(#players in queue)",
                    "Matchmaking is a search problem; with hundreds of thousands of players you need buckets and approximations."),
        pitfalls=[
            "A fixed K makes newbies swing wildly and veterans react slowly.",
            "Matching only on the average team rating skews the result: 1 strong + 4 weak ≠ 5 average.",
            "A long search for a perfect match hurts retention more than a “good enough” match in 30 seconds.",
            "Resetting the rating every season without preserving uncertainty ruins the first weeks.",
        ],
        games=["League of Legends", "CS2", "Dota 2", "Halo (TrueSkill)"],
    ),
    dict(
        id="trends",
        title="Time-series forecasting (ARIMA, seasonality)",
        tags=["ARIMA", "seasonality", "anomalies"],
        summary="Player and sales trends are time series with a trend, seasonality and noise. ARIMA models the autocorrelation, and seasonality captures weekly and event-driven spikes.",
        detail=[
            "Stationarity is the key condition. A series with a trend is differenced: Δyₜ = yₜ − yₜ₋₁. AR(p) describes the dependence on past values, MA(q) on past errors; ARIMA(p,d,q) combines them. Seasonality enters through seasonal differencing: SARIMA(p,d,q)(P,D,Q)s with s = 7 (days of the week) or 24 (hours).",
            "Useful game metrics: DAU/MAU, D1/D7/D30 retention, conversion, ARPPU, session length. Spikes from events and updates break the model — they must be pulled out into separate regressors or flagged as anomalies, otherwise the forecast gets smeared. Taking logs stabilises the variance of multiplicative series.",
            "Validation is strictly temporal, never a random split: train on the past, test on the future. Metrics: MAE, RMSE, MAPE — and above all business value (an error in a capacity forecast costs more than an error in a content forecast). Simple baselines (naive, seasonal-naive) often beat complex models, so always compare.",
        ],
        formula=("ARIMA(p,d,q): (1 − ΣφᵢLⁱ)(1−L)<sup>d</sup>yₜ = (1 + ΣθⱼLʲ)εₜ",
                 "L — the lag operator. SARIMA adds seasonal polynomials with period s. MAPE = (100/n)·Σ|y − ŷ|/|y|."),
        steps=[
            "Build the series and check stationarity (differencing, ADF test).",
            "Choose p and q from ACF/PACF or information criteria (AIC).",
            "Add seasonality and regressors for events and updates.",
            "Validate temporally and compare against baselines.",
            "Watch for model drift and retrain on a schedule.",
        ],
        complexity=("O(n·p·q) to fit (implementation dependent)", "O(n) series + parameters",
                    "With thousands of metrics you need automatic selection and ensembles; manual analysis does not scale."),
        pitfalls=[
            "A random train/test split on a time series leaks the future and inflates the metrics.",
            "Events and updates without regressors become “anomalies” the model explains incorrectly.",
            "MAPE explodes on values close to zero — use MAE or RMSE for such series.",
            "A forecast that ignores marketing campaigns is useless for planning.",
        ],
        games=["Steam trends analysis", "Live-ops forecasting", "GameAnalytics", "Sensor Tower"],
    ),
    dict(
        id="loot",
        title="Loot systems (Pareto, CLT, pity)",
        tags=["Pareto distribution", "CLT", "pity"],
        summary="Loot is a reward distribution with a long tail. Pareto models “the rich get richer”, the central limit theorem covers the total loot over a series, and pity mechanics bound the worst case.",
        detail=[
            "The Pareto distribution: <b>P(X > x) = (x<sub>m</sub>/x)<sup>α</sup></b>. Small α gives a heavy tail: most rewards are cheap, rare ones are very expensive. For loot that is a natural model — 90 % of drops are junk, 1 % are legendaries. But a pure Pareto can hand a jackpot in the first minute and break progression, so the tail is truncated and guarantees are added.",
            "The central limit theorem: the sum of independent identically distributed variables tends to a normal distribution. So the total loot over N openings is predictable (mean N·μ and variance N·σ²) even when the individual drops are Pareto (given finite variance). That lets you design a “reward budget” per session and check that the player stays on the progression curve.",
            "Pity and guarantees: “at most N attempts until the rare drop”, “the first 10 openings have a boosted chance”, “duplicates convert into currency”. These reduce the perceived variance but change the maths: the effective probability becomes conditional and has to be computed honestly. In many countries disclosing the odds is legally required — design the system so it can be explained to the player.",
        ],
        formula=("P(X > x) = (x<sub>m</sub>/x)<sup>α</sup>,   Σ<sub>i=1..N</sub>Xᵢ ≈ N(N·μ, N·σ²)",
                 "Pity: P(success on k) = p for k < N; 1 for k = N. Expected attempts = (1 − (1−p)<sup>N</sup>)/p."),
        steps=[
            "Define the rarities, base chances and item weights inside each rarity.",
            "Model the value distribution of the loot (Pareto / log-normal).",
            "Add pity and guarantees, then recompute the effective chances.",
            "Check the budget: how many rewards does a player get per hour or session?",
            "Publish the odds and add protection against a dry streak.",
        ],
        complexity=("O(1) per opening, O(N) to simulate the budget", "O(#items)",
                    "A Monte Carlo run over a million openings takes seconds and is mandatory before release."),
        pitfalls=[
            "A pure Pareto without truncating the tail gives a lottery jackpot early on and breaks the economy.",
            "Pity without recomputing the effective odds misleads players and breaks odds disclosure.",
            "Duplicates without conversion cause frustration; they need secondary value.",
            "Hidden “dynamic” odds per player are a reputational and legal risk.",
        ],
        games=["Genshin Impact", "Diablo IV", "Destiny 2", "Hearthstone"],
    ),
    dict(
        id="visibility",
        title="Visibility: PVS, portals, BSP",
        tags=["BSP", "PVS", "occlusion culling"],
        summary="Visibility is the culling of what does not reach the frame or is hidden. BSP splits space with planes, portals cull by room, PVS pre-computes “what is visible from this cell”.",
        detail=[
            "A BSP tree recursively splits space with planes (usually along geometry faces). It gives a correct front-to-back draw order and lets you cull whole subtrees quickly. In Quake the BSP was the backbone of rendering and collision. The downside is statics: any geometry change means a rebuild.",
            "PVS (potentially visible set): space is divided into leaves and for every leaf the list of visible leaves is computed ahead of time. At runtime you draw only those. It is a classic BSP-era technique and still used in modern engines as precomputed visibility. Portals are a different approach: rooms are connected by portals, and if the chain of portals misses the frustum, the whole room is culled.",
            "The modern stack: frustum culling (by AABB), occlusion culling (hierarchical depth buffer, hardware occlusion queries), LOD and HLOD. Important: camera culling does not replace light culling — shadows need their own set of casters. For open worlds a static PVS is nearly useless; GPU-driven culling and clusters work there.",
        ],
        formula=("Plane: n·x + d = 0,   frustum: six half-spaces",
                 "A point is visible when n·x + d ≥ 0 for all planes. For an AABB, test the positive/negative vertex."),
        steps=[
            "Split the scene into cells or rooms and build a portal graph or a BSP.",
            "Pre-compute the PVS offline if the world is static.",
            "At runtime add AABB frustum culling and occlusion queries.",
            "Tune LOD/HLOD and the draw-call budget.",
            "Configure shadow casters and light sources separately — their visibility differs.",
        ],
        complexity=("BSP build O(n log n), PVS O(#leaves²) offline", "O(geometry)",
                    "A PVS can take megabytes; compress it into bit masks and load it per zone."),
        pitfalls=[
            "A static PVS does not work in a destructible or dynamic world — you need a different approach.",
            "Occlusion queries without a frame delay make objects flicker — read the results one or two frames later.",
            "Camera culling does not cull shadows: casters behind the camera are still needed.",
            "Too coarse PVS cells leave extra objects in, too fine ones explode the data size.",
        ],
        games=["Quake", "Half-Life (BSP/PVS)", "Doom Eternal", "UE5 (Nanite + virtual shadow maps)"],
    ),
    dict(
        id="ricochet",
        title="Ricochet and reflection vectors",
        tags=["reflection", "Snell's law", "randomness"],
        summary="The ideal ricochet reflects the velocity about the normal: v′ = v − 2(v·n)n. A realistic one loses energy, adds spread and has a “no ricochet” condition that depends on the angle and the material.",
        detail=[
            "The reflection formula works for a perfectly elastic impact. In reality energy is lost: v′ = e·(v − 2(v·n)n), where e is the coefficient of restitution (0.3–0.9). Bullets also lose speed and get a deviation that depends on the roughness of the surface. At a shallow (grazing) angle a bullet ricochets more often; at a steep angle it deforms and lodges.",
            "The ricochet criterion is the angle between the velocity and the normal. If |v·n|/|v| < cos(θ<sub>crit</sub>) it ricochets, otherwise it hits. θ<sub>crit</sub> depends on material and speed: roughly 5–15° for steel, 10–20° for concrete, more for armour. That is a cheap and believable model for shooters.",
            "After the reflection the ray keeps living: you need a bounce limit, a trace of the next segment and decay. Visually, draw a tracer per segment with a temporal fade. For gameplay, ricochet prediction (bounce off a wall into a target) can be a separate mechanic — and then the criterion and the spread must be deterministic, otherwise the player cannot learn it.",
        ],
        formula=("v′ = v − 2(v·n)·n,   with loss: v′ = e·(v − 2(v·n)·n)",
                 "Ricochet condition: |v·n|/|v| < cos θ<sub>crit</sub>. For refraction (Snell): n₁sinθ₁ = n₂sinθ₂."),
        steps=[
            "Trace the ray, find the surface normal and the material.",
            "Check the ricochet criterion against the angle and the surface type.",
            "Reflect the velocity and scale its magnitude by the coefficient of restitution.",
            "Add a small random spread plus the tracer or effect.",
            "Repeat until the bounce limit is reached or the energy is gone.",
        ],
        complexity=("O(1) per bounce, O(#bounces) per projectile", "O(1)",
                    "Three to five bounces are enough; each one is a separate raycast."),
        pitfalls=[
            "Reflection without energy loss gives “rubber” bullets that fly forever.",
            "The normal from a collider can be wrong (rounded corners) — verify it on real meshes.",
            "Random spread without determinism stops the player from learning it and breaks the networked game.",
            "Infinite bounces in closed geometry — you need a limit and a timeout.",
        ],
        games=["Rainbow Six Siege", "Sniper Elite", "Wanted: Dead", "Half-Life 2"],
    ),
    dict(
        id="voxels",
        title="Voxel worlds and marching cubes",
        tags=["marching cubes", "SDF", "octree"],
        summary="A voxel world is a grid of density values. The surface is extracted with marching cubes (a polygon mesh) or rendered directly with ray marching; storage uses an octree or flat chunks.",
        detail=[
            "Marching cubes: a 2×2×2 cubic cell is sampled, the 256 sign combinations map to a table of edges and triangles. Vertices are interpolated by density, which gives a smooth surface. The algorithm is simple and parallelises well, but it produces many triangles and struggles with thin features (marching tetrahedra solves the diagonal connectivity problem).",
            "An SDF (signed distance field) is more convenient for editing: f(x) < 0 inside, > 0 outside. Union is min(f₁, f₂), subtraction is max(f₁, −f₂), a smooth union is a smooth min. Editing the world becomes composing functions instead of rebuilding the grid. Render with ray marching over the SDF; for physics use a marching-cubes mesh or an approximation.",
            "Storage: 32³ chunks in flat arrays with an octree for LOD, a block palette instead of full descriptions, a mesh cache and deferred rebuilds of only the changed chunks. For large worlds the critical parts are background generation, streaming, compression (RLE) and a cap on the triangles per frame. Meshing a 32³ chunk takes milliseconds — enough for interactive editing.",
        ],
        formula=("SDF: f(x) < 0 inside, f(x) = 0 on the surface;   union = min(f₁, f₂)",
                 "Vertex interpolation: p = p₁ + (0 − f₁)/(f₂ − f₁)·(p₂ − p₁). An octree gives LOD with a step of 2<sup>l</sup>."),
        steps=[
            "Choose the representation: blocks (Minecraft) or SDF density (Teardown/Claybook).",
            "Build the density function or palette and split the world into chunks.",
            "Extract the mesh with marching cubes and interpolated vertices.",
            "Cache the meshes, rebuild only changed chunks and add LOD.",
            "Stream the chunks around the player and compress the data (RLE / palette).",
        ],
        complexity=("Chunk mesh O(N³), octree query O(log N)", "O(N³) values per chunk",
                    "A 32³ chunk is 32 768 samples; meshing takes milliseconds, but hundreds of chunks need a queue."),
        pitfalls=[
            "Marching cubes on a 32³ chunk without optimisation generates tens of thousands of triangles — use LOD.",
            "Diagonal connectivity leaves holes in thin surfaces; marching tetrahedra fixes it.",
            "Rebuilding every chunk after one change kills the frame rate — rebuild locally.",
            "Physics on marching-cubes triangles is expensive; gameplay needs primitives or colliders.",
        ],
        games=["Minecraft", "Teardown", "No Man's Sky", "Deep Rock Galactic"],
    ),
]
