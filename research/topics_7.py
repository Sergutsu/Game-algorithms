# -*- coding: utf-8 -*-
"""Темы 58–66: тяжёлые нагрузки и GPU-вычисления."""

TOPICS_7 = [
    dict(
        n=58, id="compute", cat="heavy", level=3,
        title="Compute shaders: перенос симуляций на GPU",
        en="Compute shaders: moving simulations to the GPU",
        tags=["compute shader", "workgroup", "dispatch", "barrier", "GPGPU"],
        summary="Compute shader — это программа, которая выполняется не как часть отрисовки, а отдельным «проходом» по сетке данных. Он идеален для задач, где миллионы элементов обрабатываются одинаково: частицы, физика, поиск пути, сортировка, генерация сеток.",
        detail=[
            "Модель вычислений простая: данные лежат в буферех, шейдер запускается на N элементов, упакованных в workgroups по 64–256 элементов. Каждый поток (invocation) читает свои данные, считает и пишет результат. Главное отличие от шейдера вершин: нет привязки к геометрии, нет растеризации — есть произвольный доступ к памяти и возможность читать и писать в один буфер (в рамках одного диспатча).",
            "Границы применимости задаёт не «GPU быстрее», а структура данных. Если каждый элемент зависит от соседей — нужен доступ к произвольным адресам, атомики и иногда глобальная синхронизация. Если есть ветвление с большим разбросом по стоимости (шум, трассировка лучей) — дивергенция warp'а съедает выигрыш: все потоки в группе идут по самой дорогой ветке. Хорошие GPU-задачи — «регулярные»: одинаковый объём вычислений на элемент, последовательный доступ к памяти, отсутствие ветвлений.",
            "Синхронизация внутри диспатча даётся барьерами (memoryBarrier, workgroupBarrier, groupMemoryBarrier). Общий барьер всего буфера — только между диспатчами (то есть между проходами). Отсюда правило разбиения: если нужен «все посчитать, потом все вместе решаем» — это два диспатча и две записи в буфер, а не один с глобальным барьером. Для данных, которые переходят между CPU и GPU, нужны pinning-флаги (mapped/coherent) и тройная буферизация, иначе будет stall.",
        ],
        formula=("dispatch(x, y, z) → workgroups = ceil(N / group_size),   total_threads = workgroups · group_size",
                 "group_size обычно 64 (AMD) или 128/256 (NVIDIA). Слишком маленькая группа — простой, слишком большая — хуже occupancy. Время ≈ N · cost_per_element / (пропускная способность GPU)."),
        steps=[
            "Выберите задачу, где элементы независимы: частицы, клеточные автоматы, поиск по сетке, морфология, свёртка.",
            "Опишите входной и выходной буферы; держите формат данных плотным (SoA, float32, без структур с padding).",
            "Напишите kernel: index = gid.x + gid.y·size.x; early-return, если index вне диапазона.",
            "Выберите group size и размер dispatch; помните, что dispatch ограничен 65535 по оси Y/Z.",
            "Разбейте зависимости на отдельные диспатчи; расставляйте барьеры только там, где они действительно нужны.",
            "Проверьте: результат с GPU должен совпадать с CPU-версией (float-эталон с допуском), иначе ищите гонки.",
        ],
        complexity=("O(N) по числу элементов, но с массовым параллелизмом", "O(N) на буферы",
                    "Выигрыш появляется при N > 10⁴ и большой доле одинаковой работы; при N < 10³ накладные расходы на dispatch съедают всё."),
        code=("glsl", """#version 450
// Compute shader: гравитация и столкновения частиц.
// WebGPU (WGSL) — та же логика, другой синтаксис.

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
    if (i >= arrayLength(src)) return;      // аккуратный выход за границы

    Particle p = src[i];
    p.vel *= damping;                      // сопротивление среды
    p.vel += vec2(0.0, -9.81) * dt;        // гравитация
    p.pos += p.vel * dt;                   // интегрирование

    // отскок от нижней границы
    if (p.pos.y < 0.0) {
        p.pos.y = -p.pos.y;
        p.vel.y = -p.vel.y * 0.8;
    }

    dst[i] = p;
}

// dispatch: ceil(count / 64) x 1 x 1
// В WGSL: @group(0) @binding(0) var<storage, read> src: array<Particle>;
//          @compute @workgroup_size(64) fn main(@builtin(global_invocation_id) gid: vec3<u32>)"""),
        pitfalls=[
            "Запускать dispatch на «всё подряд»: накладные расходы на запуск и синхронизацию больше самой работы.",
            "Писать в буфер, который одновременно читается в том же диспатче без нужды — это гонка данных.",
            "Игнорировать дивергенцию: ветвление внутри warp'а заставляет все потоки идти по самой дорогой ветке.",
            "Забыть про read-modify-write без атомиков: два потока запишут в одну ячейку и потеряют обновление.",
            "Проверять результат «на глаз»: расхождение с CPU-эталоном в 1e-3 может означать гонку, а не «погрешность float».",
        ],
        games=["Horizon Zero Dawn", "Death Stranding", "Starfield", "Unreal Niagara (GPU sim)"],
        demo="gpuparticles",
    ),
    dict(
        n=59, id="gpu-particles", cat="heavy", level=3,
        title="Миллионы частиц: GPU-симуляция и сортировка",
        en="Millions of particles: GPU simulation and sorting",
        tags=["particles", "bitonic sort", "indirect draw", "GPU particles"],
        summary="Система частиц на 100 000 элементов — это не «много объектов», а плотный массив данных. На GPU он обновляется одним диспатчем, а на экран выводится одним же инстансированным вызовом. Узкое место — не симуляция, а сортировка для прозрачности.",
        detail=[
            "CPU-подход (пул частиц, обновление в цикле, сортировка для alpha-blend) упирается в три места: обновление состояния, сортировка и вызов отрисовки. GPU-подход убирает первые две из CPU: состояние лежит в буфере, обновляется compute-шейдером, а рендер читает тот же буфер как instance-атрибуты (позиция, цвет, размер). Остаётся сортировка.",
            "Сортировка нужна только для корректного смешивания прозрачности (back-to-front). На GPU применяют bitonic sort: сортировка слиянием, параллельная по природе, O(n·log²n). Стандартный приём — «сортировка по ключу» (32-битного ключа), куда старшие биты — это сортируемое значение (например, depth), младшие — индекс частицы: ключи сортируются вместе с данными, потом данные переставляются по индексу. Для 200 000 частиц это десятки миллисекунд CPU — и миллисекунды GPU.",
            "Альтернативы сортировке: (1) additive blending — порядок не важен, но теряется корректная прозрачность; (2) weighted blended OIT — приближённый порядок-независимый прозрачный рендеринг, который сегодня стандарт для искр и дыма; (3) рендер в два прохода: сначала непрозрачные, потом прозрачные с depth-fade. Вывод: сортировку стоит делать только там, где она действительно меняет картинку, иначе — OIT.",
        ],
        formula=("bitonic_sort: O(n log²n) сравнений,   particle_cost = sim + sort + draw",
                 "Для 2^k элементов: k(k+1)/2 проходов. При 262 144 частицах (2^18) — 171 проход. Уменьшение числа до 2^16 снимает треть времени сортировки."),
        steps=[
            "Определите бюджет: сколько частиц нужно на 1 мс GPU. Начните с 10 000 и меряйте.",
            "Храните состояние в одном буфере (pos, vel, color, life) в формате SoA или плотной структуре.",
            "Обновляйте состояние compute-шейдером: один dispatch на кадр, без readback.",
            "Если нужна корректная прозрачность — сортируйте ключи (depth << 16 | index) bitonic-сортировкой.",
            "Рисуйте одним инстансированным вызовом, читая позиции из буфера, а не из CPU-структур.",
            "Ограничьте overdraw: миллион частиц на весь экран — это fill-rate, а не вычисления.",
        ],
        complexity=("Симуляция O(N); сортировка O(N log²N); отрисовка O(N)", "O(N) на GPU",
                    "Главный лимит — overdraw и пропускная способность, а не число частиц."),
        code=("glsl", """#version 450
// Отрисовка частиц из GPU-буфера одним инстансированным вызовом.

layout(location = 0) in vec2 corner;   // quad из 4 вершин
layout(location = 1) in vec2 offset;   // per-instance позиция
layout(location = 2) in vec4 color;    // per-instance цвет и размер

layout(std430, binding = 0) readonly buffer Particles {
    vec4 pos_size[];   // xy — позиция, z — размер, w — альфа
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

// Один draw call на все частицы:
// glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, particleCount);
// треугольники не сортированы — для искр используйте additive blending."""),
        pitfalls=[
            "Считать, что миллион частиц — это «много GPU»: при большом overdraw это 10 мс только на заливку.",
            "Читать позиции частиц обратно на CPU каждый кадр: readback — это синхронизация и латентность (тема 61).",
            "Сортировать прозрачные частицы всегда: для дыма и искр additive/OIT дешевле и выглядит лучше.",
            "Растить буфер с запасом «на всякий случай»: память GPU дорогая, считайте по максимуму сцены.",
            "Игнорировать «рождение и смерть»: свободные слоты надо переиспользовать, иначе буфер распухнет.",
        ],
        games=["Unreal Niagara", "Unity VFX Graph", "Ghost of Tsushima", "Doom Eternal"],
        demo="gpuparticles",
    ),
    dict(
        n=60, id="gpu-driven", cat="heavy", level=3,
        title="GPU-driven pipeline: отсечение и сборка команд на GPU",
        en="GPU-driven pipeline: GPU-side culling and command building",
        tags=["indirect draw", "GPU culling", "Hi-Z", "bindless", "compute pipeline"],
        summary="Классический кадр: CPU решает, что видно, и вызывает draw для каждой группы; GPU рисует. GPU-driven pipeline переворачивает схему: GPU сам отбирает видимые объекты и формирует список команд, а CPU отдаёт один вызов.",
        detail=[
            "Проблема классической схемы — CPU не знает, что GPU успеет отрисовать за кадр, поэтому планировать приходится на глаз, а кадр упирается в CPU. GPU-driven pipeline решает это: сцена лежит в постоянных GPU-буферах (позиции, радиусы, индексы материалов), compute-шейдер frustum-culling'ит объекты и в конце пишет список выживших в буфер, а `drawElementsIndirect`/`drawIndirect` читает этот буфер как параметры вызова.",
            "Окклюзия делается по иерархии Hi-Z: предыдущий кадр из depth-буфера строит пирамиду (max-depth reduction), и видимость объекта проверяется выборкой его AABB в пирамиде. Тот же буфер можно построить и до основного прохода (depth prepass), чтобы culling'ить по актуальной глубине.",
            "Следствия и цена. Плюсы: CPU почти не участвует в формировании списка, кадр предсказуем, отсечение точнее. Минусы: отладка сильно сложнее, «draw call» перестаёт быть видимым в профайлере, нужно думать о синхронизации и о том, как отлаживать контент. Отдельная проблема — поддержка: API вроде WebGPU дают нужные примитивы, а в WebGL2 indirect draw ограниченно доступен (ANGLE и расширения).",
        ],
        formula=("visible_list = cull(frustum, hzb) → count + instance_ids → drawIndirect(count)",
                 "Один indirect draw на (mesh, material) вместо тысяч обычных. Затраты CPU: 1 dispatch + 1 indirect draw на группу материалов."),
        steps=[
            "Перенесите сцену в постоянные GPU-буферы: позиции, радиусы, индексы мешей и материалов.",
            "Напишите compute-шейдер culling: frustum-тест по AABB, проверка по Hi-Z, запись выживших индексов.",
            "Соберите видимые объекты по ключу (меш + материал) — это даст счётчики для indirect-вызовов.",
            "Используйте drawIndirect / multi-draw с количествами из GPU-буфера.",
            "Отключите привязку состояния через bindless или через массив текстур — иначе каждый материал всё равно требует отдельного вызова.",
            "Включите debug-режим: визуализация отсечённых объектов и счётчиков в HUD, иначе чинить будет нечего.",
        ],
        complexity=("O(n) на сцене на GPU, CPU — O(1)", "O(n) в GPU-памяти",
                    "Выигрыш заметен при тысячах объектов; на сотнях — оверхед не окупается."),
        code=("glsl", """#version 450
// GPU culling: frustum + Hi-Z, запись видимых объектов в буфер.

layout(local_size_x = 64) in;

struct Object {
    vec4 center_radius;   // xyz — центр, w — радиус
    uint mesh_id;
    uint material_id;
};

layout(std430, binding = 0) readonly  buffer Objects { Object objs[]; };
layout(std430, binding = 1) writeonly buffer Visible { uint visible_ids[]; };
layout(std430, binding = 2) writeonly buffer DrawArgs { uint count; uint instance_count; uint first; uint base; };

layout(push_constant) uniform PC {
    mat4 view_proj;
    vec4 frustum[6];     // плоскости отсечения
    int  object_count;
} pc;

void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= uint(pc.object_count)) return;

    Object o = objs[i];

    // 1. Frustum: центр сферы против 6 плоскостей
    bool in_frustum = true;
    for (int p = 0; p < 6; ++p) {
        if (dot(pc.frustum[p].xyz, o.center_radius.xyz) + pc.frustum[p].w < -o.center_radius.w) {
            in_frustum = false;
            break;
        }
    }
    if (!in_frustum) return;

    // 2. Hi-Z occlusion: выборка пирамиды глубины по AABB (упрощённо — центр)
    // float depth = textureLod(hiz, uv_center, 0).r;
    // if (o.center_radius.z - o.center_radius.w > depth) return;

    // 3. Атомарно добавляем в список видимых
    uint slot = atomicAdd(drawArgs.instance_count, 1u);
    visible_ids[slot] = i;
}"""),
        pitfalls=[
            "Внедрять GPU-driven pipeline в проект с маленькими сценами: сложность отладки не окупится.",
            "Забыть, что frustum-culling на GPU не спасает от overdraw: пиксельная нагрузка остаётся.",
            "Не сделать fallback: на старых API нужен обычный путь, иначе игра не запустится у части аудитории.",
            "Считать draw call'ы по-старому: в профайлере их не видно, нужна своя телеметрия.",
            "Синхронизировать видимость с CPU каждый кадр: это возвращает ровно ту stall'ы, которых вы хотели избежать.",
        ],
        games=["Unreal UE5 (Nanite/VSM)", "Decima (Guerrilla)", "NVIDIA RTX", "AMD Radeon VII"],
    ),
    dict(
        n=61, id="readback", cat="heavy", level=3,
        title="Асинхронный readback: как не встать в stall",
        en="Async readback: avoiding GPU stalls",
        tags=["fence", "stall", "readback", "triple buffering", "PBO"],
        summary="Самый частый способ испортить производительность GPU-игры — прочитать результат с GPU обратно на CPU в том же кадре. Это называется stall: CPU ждёт, пока GPU догонит, а GPU простаивает, пока CPU ждёт. Решение — читать асинхронно, с задержкой в 1–3 кадра.",
        detail=[
            "Механика проблемы: команда `map()` или `readPixels` на буфере, который GPU ещё не отрендерил, заставляет драйвер ждать завершения работы GPU. В этот момент GPU не может делать следующий кадр, а CPU не может делать следующий кадр — оба простаивают. Время ожидания может быть 5–50 мс, и оно полностью теряется.",
            "Решение — разнести по времени. GPU пишет в буфер A; CPU ставит fence (сигнал «я закончил»), и в следующем кадре (или через 2) проверяет, сработал ли сигнал. Если да — читает данные из A (это уже не ждёт GPU) и запускает работу GPU в буфер B. Получается конвейер: пока CPU обрабатывает результат поколения N−2, GPU считает поколение N.",
            "Тонкости: тройная буферизация нужна, потому что GPU может быть на 2–3 кадра впереди; «кольцо» из буферов работает лучше одиночного; данные, которые GPU пишет часто, а CPU читает редко, стоит упаковывать (downsampling, агрегация на GPU) — иначе объём трафика убьёт всю выгоду. Отдельно: если CPU ждёт результат в том же кадре (например, для коллизии с курсором), нужен компромисс — либо предсказание на CPU, либо accept-latency.",
        ],
        formula=("stall = max(0, t_gpu_finish − t_cpu_request),   pipelined_latency ≈ k · frame_time (k = 2…3)",
                 "Хороший признак: readback занимает < 0.2 мс CPU и не блокирует GPU. Тройная буферизация: буферы A/B/C, CPU читает A, пока GPU пишет C."),
        steps=[
            "Найдите все места, где CPU ждёт GPU: readback позиций, Occlusion queries, picking, чтение счётчиков.",
            "Сделайте буферы асинхронными и заведите fence на каждый кадр.",
            "Введите кольцо из 2–3 буферов: CPU читает данные, готовые 1–2 кадра назад.",
            "Уменьшайте объём: считывайте только нужное (счётчики, позиции выбранных объектов), а не весь буфер.",
            "Если CPU нужен свежий результат в этом же кадре — считайте его параллельно на CPU или предсказывайте.",
            "Проверяйте профилировщиком: в кадре не должно быть «GPU wait».",
        ],
        complexity=("O(1) на кадр при асинхронной схеме", "O(k · buffer_size) на кольцо буферов",
                    "Латентность данных: 2–3 кадра — это нормально, но не для picking и физики от курсора."),
        code=("csharp", """using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

// Асинхронный readback: чтение данных с GPU без ожидания.
public class AsyncReader : MonoBehaviour
{
    const int Ring = 3;                       // кольцо буферов
    readonly ComputeBuffer[] _buffers = new ComputeBuffer[Ring];
    readonly GraphicsBuffer[] _queries = new GraphicsBuffer[Ring];
    int _head = 0;                            // куда пишем сейчас

    void OnEnable()
    {
        for (int i = 0; i < Ring; i++)
        {
            _buffers[i] = new ComputeBuffer(1024, sizeof(float) * 4,
                                           ComputeBufferType.Structured);
        }
    }

    // Вызывать в конце кадра: "снимите данные, когда GPU закончит".
    public void Request()
    {
        _head = (_head + 1) % Ring;
        // fence ставится сразу после диспатча: сигнал означает "буфер готов"
        GraphicsFence fence = Graphics.CreateGraphicsFence(
            GraphicsFenceType.AsyncQueueSynchronisation,
            SynchronisationStageFlags.ComputeProcessing);

        // GPU сам проверит fence перед записью — задержка в 1–2 кадра тут неявная
        _pending.Add(new Pending { Buffer = _buffers[_head], Fence = fence });
    }

    struct Pending { public ComputeBuffer Buffer; public GraphicsFence Fence; }

    readonly List<Pending> _pending = new();

    void LateUpdate()
    {
        // Забираем только те буферы, чей fence уже сработал: ждать нельзя
        for (int i = _pending.Count - 1; i >= 0; i--)
        {
            var p = _pending[i];
            if (!p.Fence.passed) continue;      // GPU ещё не закончил — пропускаем
            var data = new float[1024];
            p.Buffer.GetData(data);             // данные уже готовы, это не stall
            _pending.RemoveAt(i);
        }
    }

    void OnDisable()
    {
        foreach (var b in _buffers) b?.Release();
    }
}"""),
        pitfalls=[
            "Читать буфер в том же кадре, когда его записали: это и есть stall, даже если «всего 4 килобайта».",
            "Накапливать pending-запросы без проверки fence: память распухает, а данные приходят с задержкой в десятки кадров.",
            "Читать весь буфер, когда нужны 10 чисел: объём трафика важнее латентности.",
            "Считать, что fence «решает всё»: на некоторых драйверах проверка fence тоже стоит микросекунд, их надо мерить.",
            "Требовать данные в том же кадре в местах, где хватает прогноза (позиция курсора, предсказание попадания).",
        ],
        games=["Unity AsyncGPUReadback", "Unreal RDG", "Doom Eternal", "Cyberpunk 2077"],
    ),
    dict(
        n=62, id="gpu-meshing", cat="heavy", level=3,
        title="Процедурная геометрия на GPU: marching cubes и SDF",
        en="Procedural geometry on the GPU: marching cubes and SDF",
        tags=["marching cubes", "SDF", "isosurface", "voxelization", "mesh generation"],
        summary="Если мир задаётся полем плотности (SDF, шум, метаболы), его можно превратить в полигоны прямо на GPU. Это снимает с CPU самую тяжёлую фазу — построение сетки — и открывает дорогу к миллионам треугольников в реальном времени.",
        detail=[
            "Алгоритм marching cubes извлекает изоповерхность из воксельной сетки: в каждой ячейке 8 значений плотности, по их знакам определяется один из 256 случаев пересечения, и по таблице строится полигон. На CPU это упирается в число ячеек: 256³ = 16.7 млн ячеек — нереально за кадр. На GPU каждая ячейка — отдельный поток, и проверяются только те, где плотность пересекает изолинию (можно отсечь по min/max в блоке).",
            "SDF-подход (signed distance field) проще: поверхность — нулевой уровень функции расстояния, а геометрия получается ray marching'ом в шейдере. Это неявная геометрия: нет меша вообще, есть функция и маршray. Плюсы: бесконечная детализация, лёгкая анимация (деформация поля), простая CSG-комбинация. Минусы: дорогой рендеринг (много сэмплов на пиксель) и отсутствие данных для физики, поэтому часто комбинируют: SDF для рендера + грубая сетка для физики.",
            "Ещё один тяжёлый класс — SDF-генерация (нейросетевые модели вроде marching cubes по вокселям от 3D-генератора). Здесь GPU применяют для (1) построения вокселей, (2) marching cubes по ним, (3) сжатия сетки. Практический совет: считайте на GPU только то, что действительно массово и параллельно, а финальную сборку (сжатие, LOD, коллизии) оставляйте CPU или GPU-проходами с чтением через асинхронный readback.",
        ],
        formula=("surfaces ≈ cells_touched,   mesh_size ≈ 2.4 · cells_touched (треугольников на ячейку в среднем)",
                 "Оптимизация: сначала считаем min/max плотности в блоке 4×4×4 и отбрасываем блок целиком — экономия до 90 % потоков."),
        steps=[
            "Определите источник поля: SDF, шум, метаболы или воксели сети.",
            "Разбейте объём на блоки; для каждого блока посчитайте min/max плотности.",
            "Запустите compute-шейдер по ячейкам: ячейки вне диапазона [min, max] отбрасываются.",
            "По таблице 256 случаев (или 2D-случаям для marching squares) сгенерируйте треугольники.",
            "Сожмите вершины на GPU (если API позволяет) или выполните welding на CPU через readback.",
            "Постройте LOD и BVH для физики: сырая сетка слишком тяжёлая для коллизий.",
        ],
        complexity=("O(cells) на GPU, отсечение блоками снижает в разы", "O(triangles) на меш",
                    "Для 256³ сетки — порядка секунды на CPU и десятки миллисекунд на GPU."),
        code=("glsl", """#version 450
// Извлечение изоповерхности: одна нить = одна воксельная ячейка.
layout(local_size_x = 4, local_size_y = 4, local_size_z = 4) in;

layout(std430, binding = 0) readonly  buffer Field { float density[]; };
layout(std430, binding = 1) writeonly buffer Triangles { float vertices[]; };
layout(std430, binding = 2) buffer Counter { uint count; };

uniform ivec3 grid_size;
uniform float iso_level;

// 8 углов ячейки: смещения в порядке xyz (0..7)
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

    // быстрый выход: изолиния не пересекает ячейку
    float mn = v[0], mx = v[0];
    for (int i = 1; i < 8; ++i) { mn = min(mn, v[i]); mx = max(mx, v[i]); }
    if (iso_level < mn || iso_level > mx) return;

    // полная реализация использует таблицу 256 случаев:
    // int cubeIndex = 0;
    // for (int i = 0; i < 8; ++i) if (v[i] < iso_level) cubeIndex |= (1 << i);
    // int edges[12]; int edgeCount = 0;
    // ... интерполяция точек на рёбрах, запись треугольников ...
}"""),
        pitfalls=[
            "Гонять по всем ячейкам без отсечения блоками: в 90 % случаев поле почти пустое, а потоки тратятся впустую.",
            "Забыть про границы сетки: sampling за пределами даёт мусор на границах объёма.",
            "Строить физику по той же сетке: для коллизий нужен упрощённый convex/voxel-меш.",
            "Ожидать, что SDF-рендер бесплатен: каждый пиксель делает десятки сэмплов, это чистый fill-rate.",
            "Генерировать меш каждый кадр: генерация должна быть инкрементальной, по изменённому объёму.",
        ],
        games=["Minecraft (chunk meshing)", "Teardown", "No Man's Sky", "Hollow Knight: Silksong"],
    ),
    dict(
        n=63, id="gpu-physics", cat="heavy", level=3,
        title="Физика и broadphase на GPU",
        en="Physics and broadphase on the GPU",
        tags=["broadphase", "XPBD", "GPU physics", "сортировка контактов", "solver"],
        summary="Когда объектов тысячи, узкие места физики — broadphase (кто с кем может столкнуться) и solver (итерации решения контактов). Оба этапа хорошо параллелятся и потому давно уехали на GPU: broadphase — через сортировку по сетке, solver — через compute-шейдер.",
        detail=[
            "Broadphase на GPU строится так: позиции всех тел пишутся в буфер, сортируются по пространственной сетке (или по Morton-коду), и для каждой пары соседних ячеек генерируются кандидаты на контакт. Сортировка — тот же bitonic sort, что и для частиц. Альтернатива — compute-based broadphase через иерархический BVH, который строится или перестраивается на GPU (Morton-сортировка + построение дерева по ссылкам).",
            "Solver (решение контактов) на GPU: каждый поток решает один контакт, но контакты связаны (трение тянет соседние тела), поэтому нужен обмен данными между итерациями — обычно это «atomics + два буфера» или Jacobi-схема, где все контакты считаются по состоянию начала итерации. XPBD (position-based) хорош именно для GPU: позиции пишутся атомарно или через pull-схему, жёсткость не зависит от числа итераций.",
            "Реальность такова, что полностью на GPU живут редко: игровая логика, триггеры, коллизии с игроком и «важные» тела обычно остаются на CPU, а GPU занимается массовкой (мелкие тела, дебрис, жидкость). Практичная архитектура — гибрид: broadphase и часть solver'а на GPU, «важные» тела на CPU, а результат читается асинхронно (тема 61) и применяется с задержкой в 1–2 кадра. Задержку прячут интерполяцией.",
        ],
        formula=("contacts ≈ Σ k_density · density²,   solve_time ≈ iterations · contacts · cost_per_contact",
                 "Правило: сортировка (O(N log²N)) дешевле, чем O(N²) broadphase. Solver: меньше итераций при большем времени шага — это всегда выгоднее."),
        steps=[
            "Определите, где реально узкое место: broadphase, narrowphase или solver — меряйте отдельно.",
            "Перенесите broadphase на GPU: сортировка по сетке (Morton) + генерация кандидатов.",
            "Решайте контакты в compute-шейдере по схеме Jacobi: каждый контакт читает состояние начала итерации.",
            "Используйте XPBD: жёсткость не зависит от числа итераций, меньше итерарий — меньше трафика.",
            "Оставьте «важные» тела на CPU и синхронизируйте через асинхронный readback + интерполяцию.",
            "Валидируйте на эталоне: GPU-физика обязана сходиться к CPU-решению в пределах допуска.",
        ],
        complexity=("Broadphase O(N log²N) вместо O(N²); solver O(contacts · iterations)", "O(N + contacts)",
                    "Выигрыш проявляется при тысячах тел; при сотнях CPU быстрее из-за простоты."),
        code=("glsl", """#version 450
// XPBD-решатель контактов на GPU: одна нить = один контакт.
layout(local_size_x = 64) in;

layout(std430, binding = 0) readonly  buffer Contacts { vec4 pairs[]; };   // (i, j, rest, stiffness)
layout(std430, binding = 1) buffer Positions { vec4 pos[]; };            // xy — позиция, zw — инверсная масса
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
    float pen = c.z - len;                 // пенетрация
    if (pen <= 0.0) return;

    float wsum = pa.z + pb.z;
    if (wsum <= 0.0) return;

    // позиционная коррекция: Δx = n · pen · (w_i / Σw) · stiffness
    vec3 corr = n * (pen * c.w * (pa.z / wsum));

    // Jacobi: обе коррекции пишутся в отдельный буфер и складываются на следующем проходе
    delta[a] += vec4(corr, 0.0);
    delta[b] -= vec4(corr, 0.0);
}"""),
        pitfalls=[
            "Переносить на GPU физику, которая нужна CPU каждый кадр: латентность 1–2 кадра ломает отзывчивость.",
            "Считать, что Jacobi даёт тот же результат, что Gauss-Seidel: он сходится медленнее, зато параллелен.",
            "Писать позиции из разных контактов в один буфер без atomics: потеря обновлений.",
            "Забыть про broadphase: без него O(N²) съедает любой выигрыш от GPU-solver'а.",
            "Не проверить сходимость: «вроде работает» на 100 телах не означает корректность на 100 000.",
        ],
        games=["NVIDIA PhysX", "Bullet", "Unity PhysX", "Ragdoll physics (VR)"],
    ),
    dict(
        n=64, id="heavy-shaders", cat="heavy", level=3,
        title="Тяжёлые шейдеры: ray marching, волюметрика, SSR",
        en="Heavy shaders: ray marching, volumetrics and SSR",
        tags=["ray marching", "volumetrics", "SSR", "temporal reprojection", "denoise"],
        summary="Когда шейдер стоит дорого, виноват не код, а количество сэмплов на пиксель. Ray marching даёт десятки-сотни сэмплов на пиксель, поэтому выигрывают не микрооптимизации, а три приёма: разрешение ниже, temporal reprojection и шум вместо точного результата.",
        detail=[
            "Три класса дорогих эффектов. Volumetrics — интеграление плотности по лучу в объёме (туман, световые лучи): 20–64 сэмпла на пиксель × число источников света. SSR (screen-space reflections) — трассировка отражённого луча по экранному буферу с бинарным поиском: 20–50 шагов. Ray marching по SDF — аналогично, 50–150 сэмплов. Общая черта: стоимость пропорциональна числу сэмплов, а не сложности математики.",
            "Первое средство — рендерить эффект в пониженном разрешении (half или quarter res) и растягивать. Второе — temporal reprojection: переиспользовать результат прошлого кадра, спроецированный по матрице движения камеры, а новый кадр считать в regions of interest (где пиксель изменился сильно). Третье — трассировка в разрежённом виде ( stochastic sampling + blue-noise + temporal accumulation), а затем денойз.",
            "Денойз — обязательная часть: разрежённый ray march даёт шум, который сглаживают either пространственно (bilateral blur с учётом глубины и нормали) или временно (накопление по гистограмме). Качество «cheap SSR с блюр-денойзом» часто неотличимо от точного SSR с 64 шагами. Главное правило: любая тяжёлая техника должна иметь деградацию — отключение, упрощение или снижение частоты обновления.",
        ],
        formula=("cost ≈ pixels · samples · shader_cost,   temporal_gain ≈ f_overlap (0.5…0.95)",
                 "Half-res даёт 4× экономию fill-rate, quarter-res — 16×. Reprojection даёт тем больше, чем больше экран перекрыт (f_overlap)."),
        steps=[
            "Измерьте fill-rate: сколько сэмплов на пиксель у вашего шейдера и сколько это стоит в миллисекундах.",
            "Переведите эффект в half-res, добавьте билинейный апскейл и dither, чтобы убрать бандинг.",
            "Включите temporal reprojection: храните предыдущий результат и матрицу движения камеры.",
            "Замените детерминированный обход на стохастический (blue-noise) и добавьте денойз.",
            "Ограничьте эффект влиянием на кадр: максимальное число сэмплов на кадр и авто-деградация при перегрузе.",
            "Предусмотрите отключение: на слабом железе эффект выключается или упрощается, а не «ест» кадр.",
        ],
        complexity=("O(pixels · samples)", "O(pixels) на буферы эффекта",
                    "Fill-rate — самая частая причина просадок в 4K: качество надо снижать по разрешению."),
        code=("glsl", """#version 450
// Трассировка луча в SDF-пространстве с ранним выходом и шагом по градиенту.
float sdf(vec3 p) {
    // «пузырковая» структура: дешёвая аналитическая функция
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
        if (d < 0.001) return true;          // попали в поверхность
        dist += d;                           // шаг по SDF: без шага по градиенту
        if (dist > 40.0) break;              // вышли за границы сцены
    }
    return false;
}

// Стоимость: до max_steps сэмплов на пиксель.
// Ускорения: half-res + temporal reprojection + stochastic jitter + denoise."""),
        pitfalls=[
            "Оптимизировать математику вместо числа сэмплов: 90 % стоимости — это сэмплы.",
            "Рендерить эффект в полном разрешении «всего один кадр»: постоянная цена важнее разовой.",
            "Без денойза шум от stochastic sampling выглядит хуже, чем честный (но более гладкий) результат.",
            "Игнорировать overdraw: тяжёлый шейдер поверх тяжёлого шейдера умножает стоимость.",
            "Не тестировать в 4K: fill-rate там вчетверо выше, и эффект, «лёгкий» в 1080p, убивает кадр.",
        ],
        games=["Unreal Lumen", "God of War Ragnarök", "Alan Wake 2", "Portal RTX"],
    ),
    dict(
        n=65, id="gpu-profiling", cat="heavy", level=3,
        title="Профилирование GPU: таймстемпы, счётчики и occlusion queries",
        en="GPU profiling: timestamps, counters and occlusion queries",
        tags=["timestamp query", "GPU counter", "RenderDoc", "occlusion query", "pipeline statistics"],
        summary="На CPU видно, сколько времени занял кадр; на GPU — сколько времени занял конкретный проход. Инструменты дают это через timestamp-запросы, счётчики конвейера и occlusion queries. Без них оптимизация GPU — это гадание по одному общему таймеру.",
        detail=[
            "Timestamp query — запрос времени GPU между двумя моментами. Обычно один на проход (сцена, shadow, post) или один на кадр; результат приходит через 1–2 кадра, поэтому их копят и читают асинхронно (тема 61). На разных API имена разные (VK_EXT_calibrated_timestamps, D3D12 queries, Nsight), но смысл одинаковый.",
            "Счётчики конвейера дают то, чего нет во времени: сколько треугольников, шейдерных вызовов, переключений состояния, «stall'ов», окклюзий, «full-screen quad»'ов. Именно они показывают, что «время ушло в рендер» на самом деле означает 5000 draw call'ов и 12 миллионов треугольников. Профилировщики (RenderDoc, PIX, Nsight Graphics, Xcode) умеют считать их автоматически.",
            "Occlusion query — «стресс-тест» отсечения: сколько пикселей объект реально записал в depth-буфер. Ноль означает, что объект полностью закрыт и его можно не рисовать. Запрос асинхронный, результат приходит через несколько кадров, поэтому решение принимают с задержкой (см. тему 33). Отдельно полезна «глубина» occlusion: сколько слоёв перекрыто — по ней решают, нужен ли LOD.",
        ],
        formula=("pass_time = Σ timestamps,   efficiency = useful_pixels / shaded_pixels",
                 "Полезная метрика — не «время прохода», а «сколько работы он сделал на миллисекунду»: если шейдер пишет 10 % экрана и стоит 4 мс — он дорогой."),
        steps=[
            "Включите таймстемпы на проход: сцена, тени, тест, post, UI.",
            "Считайте ключевые счётчики: draw calls, треугольники, шейдерные вызовы, смены состояния.",
            "Сравните «рабочий экран» (shaded pixels) с «полезным экраном»: ratio ниже 50 % — кандидат на оптимизацию.",
            "Добавьте occlusion queries для крупных объектов и замерьте, сколько реально видно.",
            "Смотрите на p95/p99 по кадрам, а не на среднее: один тяжёлый проход в 30 % кадров портит всё.",
            "Сравнивайте с эталоном: «проход занял 3 мс» бессмысленно без «в 1080p/4K, с N частицами».",
        ],
        complexity=("O(1) на запрос, O(сэмплов) при сборе", "O(1)",
                    "Запросы не бесплатны: десятки timestamp-запросов на кадр сами стоят десятки микросекунд."),
        code=("python", """class GpuProfiler:
    \"\"\"Учёт проходов по timestamp-запросам и счётчиков.\"\"\"
    def __init__(self):
        self.passes = {}          # имя -> список длительностей
        self.counters = {}        # имя -> значение

    def begin_pass(self, name):
        self._t0 = time.perf_counter()   # в реальном API здесь timestamp query

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

# Пример ожидаемого вывода:
# passes: [('post', 3.1, 5.8), ('shadow', 2.0, 4.2), ('scene', 4.4, 9.1)]
# gpu_total: 19.1 мс при бюджете 16.6 → сначала чинить post и scene"""),
        pitfalls=[
            "Читать результаты timestamp-запросов в том же кадре: данные приходят с задержкой, нужен асинхронный сбор.",
            "Считать, что «GPU занят 12 мс» значит «сцена тяжёлая»: это может быть post-processing.",
            "Не смотреть счётчики: время без числа вызовов не говорит, что именно чинить.",
            "Профилировать с включённым оверлеем отладки: он сам добавляет draw call'ы и искажает картину.",
            "Забыть про разные GPU: один и тот же профиль на мобильном GPU может отличаться в разы.",
        ],
        games=["RenderDoc", "NVIDIA Nsight", "PIX", "Xcode GPU Frame Capture"],
    ),
    dict(
        n=66, id="quality-scaling", cat="heavy", level=2,
        title="Масштабирование качества и деградация на слабом железе",
        en="Quality scaling and graceful degradation",
        tags=["scalability", "dynamic resolution", "LOD bias", "fallback", "tier"],
        summary="Один и тот же контент должен работать и на мощном ПК, и на слабом ноутбуке с интегрированной графикой. Поэтому качество — не фиксированная настройка, а набор рычагов, которые движок двигает по бюджету кадра: разрешение, дальность LOD, число эффектов, качество теней.",
        detail=[
            "Архитектура деградации — это набор независимых «рычагов» и контроллер, который выбирает их значения по текущей производительности. Рычаги: render scale (0.5–1.0), LOD bias, число динамических теней, качество post-processing, объём частиц, дальность прорисовки, разрешение текстур (streaming), качество аудио. Контроллер меряет p95 времени кадра и плавно (не скачком) меняет параметры.",
            "Динамическое разрешение — самый действенный рычаг: рендерим в меньшем разрешении, а апскейлим. В масштабировании есть две стратегии: «время рендера фиксировано» (снижаем разрешение, чтобы уложиться в бюджет) и «разрешение фиксировано» (снижаем качество эффектов). Первая сохраняет отзывчивость, вторая — чёткость; в реальности используют их вместе, а hysteresis не даёт разрешению «дышать».",
            "Важнее конкретных значений — отсутствие «ступенек»: если игрок заметил переключение, он решит, что игра лагает. Поэтому: переходы постепенные (LOD fade, cross-fade теней), решения принимаются по сглаженной метрике, а не по одному кадру, а настройки не «прыгают» туда-обратно. На старте игры движок определяет класс устройства (по памяти, GPU, разрешению) и выбирает базовый набор, дальше адаптирует в рантайме.",
        ],
        formula=("scale = clamp(target_ms / measured_ms, min_scale, 1.0) — сглаженно: scale ← lerp(scale, new_scale, 0.05)",
                 "Порядок деградации: сначала разрешение, потом дальность LOD, потом тени, потом эффекты, потом качество аудио. Сначала то, что дешевле всего заметно."),
        steps=[
            "Определите целевой класс устройства по памяти, GPU и разрешению экрана.",
            "Разделите настройки качества на «визуальные» (тени, частицы) и «производительные» (разрешение, дальность LOD, число источников света).",
            "Сделайте контроллер по p95 времени кадра с медленной адаптацией (несколько секунд) и hysteresis.",
            "Добавьте плавные переходы: fade между LOD, cross-fade теней, не скачет разрешение.",
            "Разрешите игроку ручной оверрайд: авто-режим плюс несколько пресетов (низкий/средний/высокий/ультра).",
            "Соберите телеметрию по устройствам: реальные профили мощнее любых предположений.",
        ],
        complexity=("O(1) на кадр для контроллера", "O(1)",
                    "Правило: деградация должна быть незаметна в движении — иначе она хуже, чем стабильный низкий уровень."),
        code=("python", """class QualityGovernor:
    \"\"\"Поддерживает бюджет кадра, двигая рычаги качества.\"\"\"
    def __init__(self, target_ms=16.6, min_scale=0.6):
        self.target = target_ms
        self.min_scale = min_scale
        self.scale = 1.0
        self.lod_bias = 0.0        # +1 = дальние LOD
        self.shadow_quality = 1.0  # 0..1
        self._ema = target_ms

    def update(self, frame_ms):
        # сглаженная метрика: один тяжёлый кадр не должен ронять качество
        self._ema += (frame_ms - self._ema) * 0.05
        if self._ema > self.target:
            # сначала разрешение (самое дешёвое по восприятию), потом остальное
            self.scale = max(self.min_scale, self.scale - 0.02)
            self._ema = self.target  # не даём метрике улететь, пока подстраиваемся
        elif self._ema < self.target * 0.85:
            self.scale = min(1.0, self.scale + 0.01)
        return self.settings()

    def settings(self):
        return {
            "render_scale": round(self.scale, 2),
            "lod_bias": round(self.lod_bias, 2),
            "shadow_quality": round(self.shadow_quality, 2),
        }

# Порядок деградации, который не ломает ощущение:
# 1) render scale 1.0 -> 0.6 (заметно меньше)
# 2) тени: число источников и разрешение карт
# 3) дальность LOD / отсечение
# 4) объём частиц и пост-эффекты
# 5) качество звука и число голосов"""),
        pitfalls=[
            "Менять качество мгновенно: переключение видно, и игрок считает его «просадкой FPS».",
            "Снижать разрешение ниже 0.6: мыло сильнее ухудшает картинку, чем тени.",
            "Автоматика без ручного оверрайда: у каждого игрока свой вкус, авто-режим должен уступать.",
            "Добавлять новый рычаг в середине проекта: тестировать матрицу «контент × настройки» дорого.",
            "Оптимизировать только под «средний» ПК: реальные пользователи — это хвост устройств, а не середина.",
        ],
        games=["Unreal Scalability", "Unity URP volume + LOD", "God of War Ragnarök", "Death Stranding"],
    ),
]
