# -*- coding: utf-8 -*-
"""English content for topics 58–66: heavy workloads and GPU compute."""

TOPICS_EN_6 = [
    dict(
        id="compute",
        title="Compute shaders: moving simulations to the GPU",
        tags=["compute shader", "workgroup", "dispatch", "barrier", "GPGPU"],
        summary="A compute shader is a program that runs not as part of a draw but as a separate pass over a grid of data. It is ideal for tasks where millions of elements are processed identically: particles, physics, pathfinding, sorting, mesh generation.",
        detail=[
            "The model is simple: the data lives in buffers, the shader is launched over N elements packed into workgroups of 64–256, and each invocation reads its data, computes and writes the result. The main difference from a vertex shader is that there is no geometry and no rasterisation — there is arbitrary memory access and the ability to read and write the same buffer (within one dispatch).",
            "The limits of applicability are set not by “GPUs are faster” but by the data structure. If every element depends on its neighbours you need random access, atomics and sometimes a global barrier. If there is branching with a large spread in cost (noise, ray tracing), warp divergence eats the win: every thread in the group follows the most expensive branch. Good GPU tasks are “regular”: the same amount of work per element, sequential memory access, no branching.",
            "Synchronisation inside a dispatch comes from barriers (memoryBarrier, workgroupBarrier, groupMemoryBarrier). A global barrier across the whole buffer only exists between dispatches — that is, between passes. Hence the rule: if you need “everyone computes, then everyone decides together”, that is two dispatches and two writes, not one with a global barrier. Data that travels between CPU and GPU needs pinned (mapped/coherent) flags and triple buffering, otherwise you get a stall.",
        ],
        formula=("dispatch(x, y, z) → workgroups = ceil(N / group_size),   total_threads = workgroups · group_size",
                 "group_size is usually 64 (AMD) or 128/256 (NVIDIA). Too small a group wastes time, too large hurts occupancy. Time ≈ N · cost_per_element / (GPU bandwidth)."),
        steps=[
            "Pick a task where the elements are independent: particles, cellular automata, grid search, morphology, convolution.",
            "Describe the input and output buffers; keep the data format dense (SoA, float32, no padded structs).",
            "Write the kernel: index = gid.x + gid.y·size.x; return early if the index is out of range.",
            "Choose the group size and the dispatch size; remember that dispatch is limited to 65535 on Y and Z.",
            "Split dependencies into separate dispatches; place barriers only where they are really needed.",
            "Verify against a CPU reference (float tolerance) — otherwise you are hunting races.",
        ],
        complexity=("O(N) over the elements, but with massive parallelism", "O(N) for the buffers",
                    "The win appears at N > 10⁴ with a large share of identical work; below 10³ the dispatch overhead eats it."),
        code=("glsl", """#version 450
// Compute shader: gravity and collisions for particles.
// WebGPU (WGSL) has the same logic in a different syntax.

layout(local_size_x = 64) in;

struct Particle {
    vec2 pos;
    vec2 vel;
};

layout(std430, binding = 0) readonly  buffer In  { Particle src[]; };
layout(std430, binding = 1) writeonly buffer Out { Particle dst[]; };

uniform float dt;
uniform float damping;

void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= arrayLength(src)) return;      // leave the range cleanly

    Particle p = src[i];
    p.vel *= damping;                      // air resistance
    p.vel += vec2(0.0, -9.81) * dt;        // gravity
    p.pos += p.vel * dt;                   // integration

    // bounce off the floor
    if (p.pos.y < 0.0) {
        p.pos.y = -p.pos.y;
        p.vel.y = -p.vel.y * 0.8;
    }

    dst[i] = p;
}

// dispatch: ceil(count / 64) x 1 x 1
// In WGSL: @group(0) @binding(0) var<storage, read> src: array<Particle>;
//          @compute @workgroup_size(64) fn main(@builtin(global_invocation_id) gid: vec3<u32>)"""),
        pitfalls=[
            "Launching a dispatch for “everything”: the launch and synchronisation overhead exceeds the work itself.",
            "Writing to a buffer that is read in the same dispatch without need — that is a data race.",
            "Ignoring divergence: branching inside a warp forces every thread down the most expensive path.",
            "Forgetting atomics for read-modify-write: two threads write to the same cell and one update is lost.",
            "Checking the result “by eye”: a 1e-3 difference from the CPU may mean a race, not float noise.",
        ],
        games=["Horizon Zero Dawn", "Death Stranding", "Starfield", "Unreal Niagara (GPU sim)"],
    ),
    dict(
        id="gpu-particles",
        title="Millions of particles: GPU simulation and sorting",
        tags=["particles", "bitonic sort", "indirect draw", "GPU particles"],
        summary="A 100 000-element particle system is not “many objects” but a dense array of data. On the GPU it is updated by a single dispatch and drawn with a single instanced call. The bottleneck is not the simulation but the sorting for transparency.",
        detail=[
            "The CPU approach (a particle pool, a loop over it, sorting for alpha blending) hits three walls: updating the state, sorting, and issuing the draw. The GPU approach takes the first two off the CPU: the state lives in a buffer, a compute shader updates it, and the render reads the same buffer as instance attributes (position, colour, size). Sorting remains.",
            "Sorting is only needed for correct alpha blending (back to front). On the GPU you use a bitonic sort: a merge sort that is parallel by nature, O(n·log²n). The standard trick is to sort 32-bit keys, where the high bits are the sort value (say depth) and the low bits are the particle index; the keys are sorted along with the data, then the data is permuted by the index. For 200 000 particles that is tens of milliseconds on the CPU — and milliseconds on the GPU.",
            "Alternatives to sorting: (1) additive blending, where the order does not matter but correct transparency is lost; (2) weighted blended OIT, an approximate order-independent transparency that is the modern standard for sparks and smoke; (3) a two-pass render: opaque first, then transparent with depth fade. The conclusion: sort only where it actually changes the picture, otherwise use OIT.",
        ],
        formula=("bitonic sort: O(n log²n) comparisons,   particle_cost = sim + sort + draw",
                 "For 2^k elements: k(k+1)/2 passes. With 262 144 particles (2^18) that is 171 passes. Dropping to 2^16 removes a third of the sorting time."),
        steps=[
            "Set the budget: how many particles fit into 1 ms of GPU. Start at 10 000 and measure.",
            "Keep the state in a single buffer (pos, vel, colour, life) in SoA or a dense struct layout.",
            "Update it with a compute shader: one dispatch per frame, no readback.",
            "If correct transparency is needed, sort keys (depth << 16 | index) with a bitonic sort.",
            "Draw with a single instanced call, reading the positions from the buffer instead of CPU structs.",
            "Cap overdraw: a million particles across the whole screen is a fill-rate problem, not a compute problem.",
        ],
        complexity=("Simulation O(N); sorting O(N log²N); drawing O(N)", "O(N) on the GPU",
                    "The real limit is overdraw and bandwidth, not the particle count."),
        code=("glsl", """#version 450
// Draw the particles from a GPU buffer with one instanced call.

layout(location = 0) in vec2 corner;   // quad of 4 vertices
layout(location = 1) in vec2 offset;   // per-instance position
layout(location = 2) in vec4 color;    // per-instance colour and size

layout(std430, binding = 0) readonly buffer Particles {
    vec4 pos_size[];   // xy - position, z - size, w - alpha
    vec4 color[];
};

out vec4 v_color;

void main() {
    uint i = gl_InstanceID;
    vec4 ps = pos_size[i];
    vec2 world = ps.xy + corner * ps.z;
    gl_Position = vec4(world, 0.0, 1.0);
    v_color = color[i];
}

// One draw call for all particles:
// glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, particleCount);
// the triangles are not sorted - for sparks use additive blending."""),
        pitfalls=[
            "Assuming a million particles is “a lot for the GPU”: with heavy overdraw that is 10 ms of fill alone.",
            "Reading particle positions back to the CPU every frame: readback is synchronisation and latency (topic 61).",
            "Always sorting transparent particles: for smoke and sparks, additive/OIT is cheaper and looks better.",
            "Growing the buffer “just in case”: GPU memory is expensive, size it for the worst case.",
            "Ignoring spawn and death: free slots have to be recycled or the buffer inflates.",
        ],
        games=["Unreal Niagara", "Unity VFX Graph", "Ghost of Tsushima", "Doom Eternal"],
    ),
    dict(
        id="gpu-driven",
        title="GPU-driven pipeline: GPU-side culling and command building",
        tags=["indirect draw", "GPU culling", "Hi-Z", "bindless", "compute pipeline"],
        summary="The classic frame: the CPU decides what is visible and issues a draw per group, the GPU draws. A GPU-driven pipeline flips the scheme: the GPU picks the visible objects and builds the command list, while the CPU issues a single call.",
        detail=[
            "The problem with the classic scheme is that the CPU does not know what the GPU will finish in a frame, so planning is guesswork and the frame is bounded by the CPU. A GPU-driven pipeline solves it: the scene lives in permanent GPU buffers (positions, radii, mesh and material indices), a compute shader does the frustum culling and writes the surviving list into a buffer, and `drawElementsIndirect` / `drawIndirect` reads that buffer as the draw arguments.",
            "Occlusion is done with a Hi-Z hierarchy: the previous frame's depth buffer is reduced into a pyramid (max-depth reduction), and an object's visibility is tested by sampling its AABB in the pyramid. The same buffer can be built before the main pass (depth prepass) to cull against the current depth.",
            "The consequences and the price. Upside: the CPU barely participates in building the list, the frame becomes predictable, culling is more accurate. Downside: debugging is much harder, “draw calls” disappear from the profiler, and you have to think about synchronisation and about how to debug content. A separate problem is support: APIs like WebGPU expose the needed primitives, while WebGL2's indirect draw is only available through extensions.",
        ],
        formula=("visible_list = cull(frustum, hzb) → count + instance_ids → drawIndirect(count)",
                 "One indirect draw per (mesh, material) instead of thousands of normal draws. CPU cost: 1 dispatch + 1 indirect draw per material group."),
        steps=[
            "Move the scene into permanent GPU buffers: positions, radii, mesh and material indices.",
            "Write the culling compute shader: frustum test on the AABB, Hi-Z check, write the surviving indices.",
            "Group the visible objects by key (mesh + material) — that gives the counts for the indirect draws.",
            "Use drawIndirect / multi-draw with the counts from the GPU buffer.",
            "Drop per-draw state binding through bindless or texture arrays — otherwise every material still needs its own call.",
            "Add a debug mode: visualise the culled objects and the counters, or there is nothing to debug.",
        ],
        complexity=("O(n) over the scene on the GPU, O(1) on the CPU", "O(n) in GPU memory",
                    "The win shows with thousands of objects; with hundreds the overhead does not pay off."),
        code=("glsl", """#version 450
// GPU culling: frustum + Hi-Z, writing the visible objects into a buffer.

layout(local_size_x = 64) in;

struct Object {
    vec4 center_radius;   // xyz - centre, w - radius
    uint mesh_id;
    uint material_id;
};

layout(std430, binding = 0) readonly  buffer Objects { Object objs[]; };
layout(std430, binding = 1) writeonly buffer Visible { uint visible_ids[]; };
layout(std430, binding = 2) writeonly buffer DrawArgs { uint count; uint instance_count; uint first; uint base; };

layout(push_constant) uniform PC {
    mat4 view_proj;
    vec4 frustum[6];     // culling planes
    int  object_count;
} pc;

void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= uint(pc.object_count)) return;

    Object o = objs[i];

    // 1. Frustum: sphere centre against the six planes
    bool in_frustum = true;
    for (int p = 0; p < 6; ++p) {
        if (dot(pc.frustum[p].xyz, o.center_radius.xyz) + pc.frustum[p].w < -o.center_radius.w) {
            in_frustum = false;
            break;
        }
    }
    if (!in_frustum) return;

    // 2. Hi-Z occlusion: sample the depth pyramid by the AABB (simplified to the centre)
    // float depth = textureLod(hiz, uv_center, 0).r;
    // if (o.center_radius.z - o.center_radius.w > depth) return;

    // 3. Atomically add to the list of visible objects
    uint slot = atomicAdd(drawArgs.instance_count, 1u);
    visible_ids[slot] = i;
}"""),
        pitfalls=[
            "Introducing a GPU-driven pipeline into a project with small scenes: the debugging cost is not repaid.",
            "Forgetting that GPU frustum culling does not remove overdraw: the pixel cost stays.",
            "No fallback: on older APIs you need the normal path, or part of your audience cannot launch the game.",
            "Counting draw calls the old way: they are invisible in the profiler, so you need your own telemetry.",
            "Synchronising the visibility list with the CPU every frame: that brings back exactly the stalls you wanted to avoid.",
        ],
        games=["Unreal UE5 (Nanite/VSM)", "Decima (Guerrilla)", "NVIDIA RTX", "AMD Radeon VII"],
    ),
    dict(
        id="readback",
        title="Async readback: avoiding GPU stalls",
        tags=["fence", "stall", "readback", "triple buffering", "PBO"],
        summary="The fastest way to ruin the performance of a GPU game is to read a result back to the CPU in the same frame. That is a stall: the CPU waits for the GPU and the GPU waits for the CPU. The fix is asynchronous reading with a delay of one to three frames.",
        detail=[
            "How the problem works: a `map()` or `readPixels` on a buffer the GPU has not finished with makes the driver wait for the GPU to complete. During that wait the GPU cannot start the next frame and the CPU cannot start the next frame — both sit idle. The wait can be 5–50 ms, and all of it is wasted.",
            "The solution is to separate them in time. The GPU writes into buffer A; the CPU sets a fence (a “I am done” signal) and on the next frame (or two) checks whether the signal fired. If it did, it reads the data from A (which no longer waits for the GPU) and starts the GPU working in buffer B. You end up with a pipeline: while the CPU processes generation N−2, the GPU computes generation N.",
            "The details: triple buffering is needed because the GPU can be two or three frames ahead; a ring of buffers beats a single one. Data the GPU writes often but the CPU reads rarely should be packed (downsampling, aggregation on the GPU) — otherwise the bandwidth kills the whole benefit. And if the CPU needs the result in the same frame (for example, a cursor collision), you need a compromise: predict on the CPU, or accept the latency.",
        ],
        formula=("stall = max(0, t_gpu_finish − t_cpu_request),   pipelined_latency ≈ k · frame_time (k = 2…3)",
                 "A good sign: the readback costs < 0.2 ms of CPU and does not block the GPU. Triple buffering: buffers A/B/C, the CPU reads A while the GPU writes C."),
        steps=[
            "Find every place where the CPU waits for the GPU: position readbacks, occlusion queries, picking, counter reads.",
            "Make the buffers asynchronous and attach a fence to each frame.",
            "Introduce a ring of two or three buffers: the CPU reads data that is one or two frames old.",
            "Reduce the volume: read only what you need (counters, the positions of selected objects), not the whole buffer.",
            "If the CPU needs a fresh result in the same frame, compute it in parallel on the CPU or predict it.",
            "Verify with a profiler: there should be no “GPU wait” in the frame.",
        ],
        complexity=("O(1) per frame with the asynchronous scheme", "O(k · buffer_size) for the ring",
                    "Data latency of 2–3 frames is normal, but not for picking or cursor physics."),
        code=("csharp", """using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

// Async readback: reading GPU data without waiting.
public class AsyncReader : MonoBehaviour
{
    const int Ring = 3;                       // a ring of buffers
    readonly ComputeBuffer[] _buffers = new ComputeBuffer[Ring];
    int _head = 0;                            // where we write now

    void OnEnable()
    {
        for (int i = 0; i < Ring; i++)
        {
            _buffers[i] = new ComputeBuffer(1024, sizeof(float) * 4,
                                           ComputeBufferType.Structured);
        }
    }

    // Call at the end of the frame: "capture the data once the GPU is done".
    public void Request()
    {
        _head = (_head + 1) % Ring;
        // the fence is set right after the dispatch: the signal means "the buffer is ready"
        GraphicsFence fence = Graphics.CreateGraphicsFence(
            GraphicsFenceType.AsyncQueueSynchronisation,
            SynchronisationStageFlags.ComputeProcessing);

        _pending.Add(new Pending { Buffer = _buffers[_head], Fence = fence });
    }

    struct Pending { public ComputeBuffer Buffer; public GraphicsFence Fence; }

    readonly List<Pending> _pending = new();

    void LateUpdate()
    {
        // Only take buffers whose fence has fired: waiting is not allowed
        for (int i = _pending.Count - 1; i >= 0; i--)
        {
            var p = _pending[i];
            if (!p.Fence.passed) continue;      // the GPU is not done yet - skip it
            var data = new float[1024];
            p.Buffer.GetData(data);             // the data is ready, this is not a stall
            _pending.RemoveAt(i);
        }
    }

    void OnDisable()
    {
        foreach (var b in _buffers) b?.Release();
    }
}"""),
        pitfalls=[
            "Reading a buffer in the same frame you wrote it: that is the stall, even for “only 4 kilobytes”.",
            "Accumulating pending requests without checking the fence: memory grows and the data arrives dozens of frames late.",
            "Reading the whole buffer when you need ten numbers: the volume of traffic matters more than the latency.",
            "Assuming a fence “solves everything”: on some drivers checking a fence also costs microseconds — measure it.",
            "Demanding same-frame data where a prediction would do (cursor position, shot prediction).",
        ],
        games=["Unity AsyncGPUReadback", "Unreal RDG", "Doom Eternal", "Cyberpunk 2077"],
    ),
    dict(
        id="gpu-meshing",
        title="Procedural geometry on the GPU: marching cubes and SDF",
        tags=["marching cubes", "SDF", "isosurface", "voxelization", "mesh generation"],
        summary="If the world is defined by a density field (SDF, noise, metaballs), you can turn it into polygons right on the GPU. That removes the heaviest phase — mesh building — from the CPU and opens the door to millions of triangles in real time.",
        detail=[
            "Marching cubes extracts an isosurface from a voxel grid: each cell has eight density values, their signs pick one of 256 intersection cases, and a table builds the polygon. On the CPU this is bounded by the number of cells: 256³ = 16.7 million cells is not a per-frame task. On the GPU every cell is a thread, and only the cells where the density crosses the isolevel have to be evaluated (you can reject blocks by their min/max).",
            "The SDF approach (signed distance field) is simpler: the surface is the zero level of a distance function, and the geometry comes out of ray marching in a shader. That is implicit geometry: there is no mesh at all, only a function and a ray. Upsides: infinite detail, easy deformation (edit the field), trivial CSG. Downsides: expensive rendering (many samples per pixel) and no data for physics — so you often combine them: SDF for rendering plus a coarse grid for physics.",
            "Another heavy class is SDF generation (neural models such as marching cubes over the voxels of a 3D generator). Here the GPU is used for (1) building the voxels, (2) marching cubes over them and (3) mesh compression. The practical rule: compute on the GPU only what is genuinely massive and parallel, and leave the final assembly (compression, LOD, collisions) to the CPU or to GPU passes that read back asynchronously.",
        ],
        formula=("surfaces ≈ cells_touched,   mesh_size ≈ 2.4 · cells_touched (triangles per cell on average)",
                 "Optimisation: first compute the min/max density of a 4×4×4 block and discard the whole block — that saves up to 90 % of the threads."),
        steps=[
            "Define the field source: SDF, noise, metaballs or network voxels.",
            "Split the volume into blocks; for each block compute the min/max density.",
            "Run the compute shader over the cells: cells outside [min, max] are discarded.",
            "Use the 256-case table (or the 2D cases for marching squares) to generate the triangles.",
            "Compress the vertices on the GPU if the API allows, or weld them on the CPU after a readback.",
            "Build LOD and a BVH for physics: the raw mesh is far too heavy for collisions.",
        ],
        complexity=("O(cells) on the GPU, block rejection cuts it by a factor", "O(triangles) for the mesh",
                    "For a 256³ grid the order is seconds on the CPU and tens of milliseconds on the GPU."),
        code=("glsl", """#version 450
// Isosurface extraction: one thread per voxel cell.
layout(local_size_x = 4, local_size_y = 4, local_size_z = 4) in;

layout(std430, binding = 0) readonly  buffer Field { float density[]; };
layout(std430, binding = 1) writeonly buffer Triangles { float vertices[]; };
layout(std430, binding = 2) buffer Counter { uint count; };

uniform ivec3 grid_size;
uniform float iso_level;

// The 8 corners of a cell: offsets in xyz order (0..7)
const ivec3 CORNER[8] = ivec3[8](
    ivec3(0,0,0), ivec3(1,0,0), ivec3(0,1,0), ivec3(1,1,0),
    ivec3(0,0,1), ivec3(1,0,1), ivec3(0,1,1), ivec3(1,1,1)
);

float sample(ivec3 c) {
    if (any(lessThan(c, ivec3(0))) || any(greaterThanEqual(c, grid_size))) return 0.0;
    return density[c.x + c.y * grid_size.x + c.z * grid_size.x * grid_size.y];
}

void main() {
    ivec3 cell = ivec3(gl_GlobalInvocationID.xyz);
    if (any(greaterThanEqual(cell, grid_size - 1))) return;

    float v[8];
    for (int i = 0; i < 8; ++i) v[i] = sample(cell + CORNER[i]);

    // quick exit: the isolevel does not cross this cell
    float mn = v[0], mx = v[0];
    for (int i = 1; i < 8; ++i) { mn = min(mn, v[i]); mx = max(mx, v[i]); }
    if (iso_level < mn || iso_level > mx) return;

    // the full implementation uses the 256-case table:
    // int cubeIndex = 0;
    // for (int i = 0; i < 8; ++i) if (v[i] < iso_level) cubeIndex |= (1 << i);
    // int edges[12]; int edgeCount = 0;
    // ... interpolate the points on the edges, write the triangles ...
}"""),
        pitfalls=[
            "Running over every cell without block rejection: in 90 % of cases the field is nearly empty and the threads are wasted.",
            "Forgetting the grid boundaries: sampling outside produces garbage at the volume's edge.",
            "Building physics from the same grid: collisions need a simplified convex or voxel mesh.",
            "Expecting SDF rendering to be free: every pixel takes dozens of samples, which is pure fill-rate.",
            "Generating the mesh every frame: generation has to be incremental, over the changed volume only.",
        ],
        games=["Minecraft (chunk meshing)", "Teardown", "No Man's Sky", "Deep Rock Galactic"],
    ),
    dict(
        id="gpu-physics",
        title="Physics and broadphase on the GPU",
        tags=["broadphase", "XPBD", "GPU physics", "contact sorting", "solver"],
        summary="When there are thousands of objects, the physics bottlenecks are broadphase (who can hit whom) and the solver (iterations that resolve the contacts). Both parallelise well and have long moved to the GPU: broadphase through grid sorting, the solver through a compute shader.",
        detail=[
            "GPU broadphase works like this: the positions of all bodies are written into a buffer, sorted by a spatial grid (or by Morton code), and candidate contacts are generated for each pair of neighbouring cells. The sort is the same bitonic sort used for particles. The alternative is a compute-based broadphase with a hierarchical BVH that is built or refitted on the GPU (Morton sort plus a tree built through references).",
            "The solver on the GPU: each thread solves one contact, but contacts are coupled (friction pulls on neighbouring bodies), so data has to be exchanged between iterations — usually with atomics plus two buffers, or a Jacobi scheme where every contact reads the state at the start of the iteration. XPBD (position-based) suits the GPU particularly well: positions are written atomically or through a pull scheme, and stiffness does not depend on the iteration count.",
            "Reality is that fully GPU-resident physics is rare: game logic, triggers, collisions with the player and “important” bodies usually stay on the CPU, while the GPU handles the mass (small debris, liquid). A workable architecture is hybrid: broadphase and part of the solver on the GPU, the important bodies on the CPU, and the result read back asynchronously (topic 61) and applied with a delay of one to two frames. The delay is hidden with interpolation.",
        ],
        formula=("contacts ≈ Σ k_density · density²,   solve_time ≈ iterations · contacts · cost_per_contact",
                 "The rule: sorting (O(N log²N)) is cheaper than an O(N²) broadphase. Solver: fewer iterations at a larger time step is always a win."),
        steps=[
            "Find the real bottleneck: broadphase, narrowphase or solver — measure them separately.",
            "Move the broadphase to the GPU: sort by grid (Morton) and generate the candidates.",
            "Solve the contacts in a compute shader with the Jacobi scheme: every contact reads the state at the start of the iteration.",
            "Use XPBD: stiffness is independent of the iteration count, so fewer iterations mean less traffic.",
            "Keep the “important” bodies on the CPU and synchronise via an async readback plus interpolation.",
            "Validate against a reference: GPU physics must converge to the CPU solution within tolerance.",
        ],
        complexity=("Broadphase O(N log²N) instead of O(N²); solver O(contacts · iterations)", "O(N + contacts)",
                    "The win shows with thousands of bodies; with hundreds the CPU is faster because it is simpler."),
        code=("glsl", """#version 450
// XPBD contact solver on the GPU: one thread per contact.
layout(local_size_x = 64) in;

layout(std430, binding = 0) readonly  buffer Contacts { vec4 pairs[]; };   // (i, j, rest, stiffness)
layout(std430, binding = 1) buffer Positions { vec4 pos[]; };            // xy - position, zw - inverse mass
layout(std430, binding = 2) buffer Corrections { vec4 delta[]; };

uniform float dt;
uniform int contact_count;

void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= uint(contact_count)) return;

    vec4 c = pairs[i];
    uint a = uint(c.x), b = uint(c.y);
    vec4 pa = pos[a];
    vec4 pb = pos[b];

    vec3 d = pb.xy - pa.xy;
    float len = length(d);
    if (len < 1e-6) return;

    vec3 n = d / len;
    float pen = c.z - len;                 // penetration
    if (pen <= 0.0) return;

    float wsum = pa.z + pb.z;
    if (wsum <= 0.0) return;

    // positional correction: dx = n * pen * (w_i / sum w) * stiffness
    vec3 corr = n * (pen * c.w * (pa.z / wsum));

    // Jacobi: both corrections go into a separate buffer and are summed on the next pass
    delta[a] += vec4(corr, 0.0);
    delta[b] -= vec4(corr, 0.0);
}"""),
        pitfalls=[
            "Moving physics to the GPU when the CPU needs the result every frame: 1–2 frames of latency ruins control feel.",
            "Assuming Jacobi gives the same result as Gauss–Seidel: it converges more slowly but runs in parallel.",
            "Writing positions from different contacts into one buffer without atomics: updates get lost.",
            "Forgetting the broadphase: without it, O(N²) eats any gain from the GPU solver.",
            "Not checking convergence: “it seems to work” on 100 bodies does not mean it is correct on 100 000.",
        ],
        games=["NVIDIA PhysX", "Bullet", "Unity PhysX", "Ragdoll physics (VR)"],
    ),
    dict(
        id="heavy-shaders",
        title="Heavy shaders: ray marching, volumetrics and SSR",
        tags=["ray marching", "volumetrics", "SSR", "temporal reprojection", "denoise"],
        summary="When a shader is expensive, it is not the code but the number of samples per pixel. Ray marching costs dozens to hundreds of samples per pixel, so what wins is not micro-optimisation but three tricks: a lower resolution, temporal reprojection, and noise instead of an exact result.",
        detail=[
            "Three classes of expensive effect. Volumetrics integrate the density along a ray through a volume (fog, god rays): 20–64 samples per pixel multiplied by the number of lights. SSR (screen-space reflections) traces a reflected ray through the screen buffer with a binary search: 20–50 steps. Ray marching an SDF is similar: 50–150 samples. The common trait: the cost scales with the sample count, not with the complexity of the maths.",
            "The first remedy is to render the effect at a lower resolution (half or quarter) and upscale it. The second is temporal reprojection: reuse last frame's result projected along the camera motion, and compute the new frame only in the regions of interest (where the pixel changed a lot). The third is to trace in a sparse way (stochastic sampling + blue noise + temporal accumulation) and then denoise.",
            "Denoising is a mandatory part: sparse ray marching produces noise that is smoothed either spatially (a bilateral blur that respects depth and normals) or temporally (accumulation over a neighbourhood). “Cheap SSR with a blur-denoise” is often indistinguishable from exact SSR with 64 steps. The main rule: every expensive technique needs a degradation path — disable it, simplify it, or lower its update rate.",
        ],
        formula=("cost ≈ pixels · samples · shader_cost,   temporal_gain ≈ f_overlap (0.5…0.95)",
                 "Half res gives a 4× fill-rate saving, quarter res 16×. Reprojection gains more the more of the screen is covered (f_overlap)."),
        steps=[
            "Measure the fill rate: how many samples per pixel your shader takes and what that costs in milliseconds.",
            "Move the effect to half resolution, add bilinear upscaling and dithering to remove banding.",
            "Enable temporal reprojection: keep the previous result and the camera motion matrix.",
            "Replace the deterministic traversal with a stochastic one (blue noise) and add denoising.",
            "Cap the effect's influence: a maximum number of samples per frame and automatic degradation under load.",
            "Provide a switch: on weak hardware the effect is disabled or simplified, not left to eat the frame.",
        ],
        complexity=("O(pixels · samples)", "O(pixels) for the effect buffers",
                    "Fill rate is the most common cause of drops in 4K: quality has to scale with the resolution."),
        code=("glsl", """#version 450
// Ray tracing through an SDF with an early exit and gradient stepping.
float sdf(vec3 p) {
    // a "bubble" structure: a cheap analytic function
    p = abs(p);
    return length(p) - 1.0 + 0.25 * sin(3.0 * p.x) * sin(3.0 * p.y) * sin(3.0 * p.z);
}

vec3 sdfNormal(vec3 p) {
    const vec2 e = vec2(1.0, -1.0) * 0.0015;
    return normalize(
        e.xyy * sdf(p + e.xyy) + e.yyx * sdf(p + e.yyx) +
        e.yxy * sdf(p + e.yxy) + e.xxx * sdf(p + e.xxx));
}

bool raymarch(vec3 ro, vec3 rd, out float t, int max_steps) {
    float dist = 0.0;
    t = 0.0;
    for (int i = 0; i < max_steps; ++i) {
        vec3 p = ro + rd * dist;
        float d = sdf(p);
        if (d < 0.001) return true;          // hit the surface
        dist += d;                           // step along the SDF
        if (dist > 40.0) break;              // left the scene bounds
    }
    return false;
}

// Cost: up to max_steps samples per pixel.
// Speed-ups: half-res + temporal reprojection + stochastic jitter + denoise."""),
        pitfalls=[
            "Optimising the maths instead of the sample count: 90 % of the cost is the samples.",
            "Rendering the effect at full resolution “just this once”: the constant cost matters more than the one-off.",
            "Without denoising, the noise from stochastic sampling looks worse than an honest but smooth result.",
            "Ignoring overdraw: an expensive shader on top of an expensive shader multiplies the cost.",
            "Not testing in 4K: the fill rate is four times higher and an effect that is “light” at 1080p kills the frame.",
        ],
        games=["Unreal Lumen", "God of War Ragnarök", "Alan Wake 2", "Portal RTX"],
    ),
    dict(
        id="gpu-profiling",
        title="GPU profiling: timestamps, counters and occlusion queries",
        tags=["timestamp query", "GPU counter", "RenderDoc", "occlusion query", "pipeline statistics"],
        summary="On the CPU you see how long a frame took; on the GPU you see how long a specific pass took. Tools give you that through timestamp queries, pipeline counters and occlusion queries. Without them, GPU optimisation is guessing from one overall timer.",
        detail=[
            "A timestamp query asks the GPU for the time between two moments. Usually one per pass (scene, shadow, test, post) or one per frame; the result arrives one or two frames later, so you accumulate them and read them asynchronously (topic 61). The names differ per API (VK_EXT_calibrated_timestamps, D3D12 queries, Nsight) but the meaning is the same.",
            "Pipeline counters give you what the time alone cannot: how many triangles, shader invocations, state switches, stalls, occlusions and full-screen quads. They are what turns “the time went into rendering” into “5000 draw calls and 12 million triangles”. Profilers (RenderDoc, PIX, Nsight Graphics, Xcode) can count them for you.",
            "Occlusion queries are a stress test for the culling: how many pixels did the object actually write into the depth buffer? Zero means it is fully hidden and can be skipped. The query is asynchronous and the result arrives several frames later, so the decision is made with a delay (see topic 33). The occlusion depth is useful too: how many layers cover it — that decides whether an LOD is needed.",
        ],
        formula=("pass_time = Σ timestamps,   efficiency = useful_pixels / shaded_pixels",
                 "The useful metric is not “the pass took 3 ms” but “how much work it did per millisecond”: a shader that shades 10 % of the screen and costs 4 ms is expensive."),
        steps=[
            "Enable timestamps per pass: scene, shadows, test, post, UI.",
            "Count the key metrics: draw calls, triangles, shader invocations, state changes.",
            "Compare the “worked screen” (shaded pixels) with the “useful screen”: a ratio below 50 % is an optimisation candidate.",
            "Add occlusion queries for large objects and measure how much is really visible.",
            "Look at p95/p99 across frames, not the average: one heavy pass in 30 % of frames ruins everything.",
            "Compare against a reference: “the pass took 3 ms” means nothing without “at 1080p/4K, with N particles”.",
        ],
        complexity=("O(1) per query, O(samples) to collect", "O(1)",
                    "Queries are not free: dozens of timestamp queries per frame cost tens of microseconds themselves."),
        pitfalls=[
            "Reading timestamp results in the same frame: the data arrives with a delay, so collect it asynchronously.",
            "Assuming “the GPU is busy for 12 ms” means “the scene is heavy”: it might be the post-processing.",
            "Not looking at the counters: time without a call count does not tell you what to fix.",
            "Profiling with the debug overlay enabled: it adds draw calls of its own and distorts the picture.",
            "Forgetting the hardware difference: the same profile on a mobile GPU can be orders of magnitude worse.",
        ],
        games=["RenderDoc", "NVIDIA Nsight", "PIX", "Xcode GPU Frame Capture"],
    ),
    dict(
        id="quality-scaling",
        title="Quality scaling and graceful degradation",
        tags=["scalability", "dynamic resolution", "LOD bias", "fallback", "tier"],
        summary="The same content has to run on a powerful PC and on a laptop with integrated graphics. So quality is not a fixed setting but a set of levers that the engine moves according to the frame budget: resolution, LOD distance, number of effects, shadow quality.",
        detail=[
            "The architecture of degradation is a set of independent “levers” plus a controller that picks their values from the current performance. Levers: render scale (0.5–1.0), LOD bias, the number of dynamic shadow casters, post-processing quality, the particle budget, the draw distance, texture resolution (streaming), audio quality. The controller measures the p95 frame time and changes the parameters smoothly, never in a jump.",
            "Dynamic resolution is the most effective lever: you render at a lower resolution and upscale. There are two strategies: “render time is fixed” (drop the resolution to fit the budget) and “resolution is fixed” (drop the quality of the effects). The first preserves responsiveness, the second preserves sharpness; in practice you combine them and add hysteresis so the resolution does not “breathe”.",
            "More important than the exact values is the absence of “steps”: if the player notices the switch, they will read it as lag. So the transitions are gradual (LOD fades, shadow cross-fades, the resolution does not jump), decisions are made on a smoothed metric rather than a single frame, and the settings do not oscillate. At startup the engine detects the device class (memory, GPU, resolution) and picks a baseline set, then adapts at runtime.",
        ],
        formula=("scale = clamp(target_ms / measured_ms, min_scale, 1.0) — smoothed: scale ← lerp(scale, new_scale, 0.05)",
                 "Degradation order: resolution first, then LOD distance, then shadows, then effects, then audio quality. Start with what the player notices least."),
        steps=[
            "Define the target device class by memory, GPU and screen resolution.",
            "Split the quality settings into “visual” (shadows, particles) and “performance” (resolution, LOD distance, light count).",
            "Make the controller work on the p95 frame time with slow adaptation (a few seconds) and hysteresis.",
            "Add smooth transitions: fades between LODs, cross-faded shadows, no jumping resolution.",
            "Allow a manual override: an auto mode plus a few presets (low / medium / high / ultra).",
            "Collect telemetry per device: real profiles beat any assumption.",
        ],
        complexity=("O(1) per frame for the controller", "O(1)",
                    "The rule: degradation must be invisible in motion — otherwise it is worse than a stable low setting."),
        code=("python", """class QualityGovernor:
    \"\"\"Keeps the frame budget by moving the quality levers.\"\"\"
    def __init__(self, target_ms=16.6, min_scale=0.6):
        self.target = target_ms
        self.min_scale = min_scale
        self.scale = 1.0
        self.lod_bias = 0.0        # +1 = further LODs
        self.shadow_quality = 1.0  # 0..1
        self._ema = target_ms

    def update(self, frame_ms):
        # a smoothed metric: one heavy frame must not drop the quality
        self._ema += (frame_ms - self._ema) * 0.05
        if self._ema > self.target:
            # resolution first (the least noticeable), then everything else
            self.scale = max(self.min_scale, self.scale - 0.02)
            self._ema = self.target  # keep the metric from running away while we adapt
        elif self._ema < self.target * 0.85:
            self.scale = min(1.0, self.scale + 0.01)
        return self.settings()

    def settings(self):
        return {
            "render_scale": round(self.scale, 2),
            "lod_bias": round(self.lod_bias, 2),
            "shadow_quality": round(self.shadow_quality, 2),
        }

# A degradation order that does not break the feel:
# 1) render scale 1.0 -> 0.6 (noticeably softer)
# 2) shadows: number of casters and map resolution
# 3) LOD distance / culling
# 4) particle volume and post effects
# 5) audio quality and voice count"""),
        pitfalls=[
            "Changing quality instantly: the switch is visible and the player reads it as a frame-rate drop.",
            "Dropping the resolution below 0.6: the blur is worse than missing shadows.",
            "Automation without a manual override: every player has their own taste and the auto mode has to yield.",
            "Adding a new lever in the middle of the project: testing the matrix of “content × setting” is expensive.",
            "Optimising only for the “average” PC: real users are the tail of the devices, not the middle.",
        ],
        games=["Unreal Scalability", "Unity URP volume + LOD", "God of War Ragnarök", "Death Stranding"],
    ),
]
