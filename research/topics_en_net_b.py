# -*- coding: utf-8 -*-
"""Part III, layers 03–04: real time, scale and operations (topics 94–104)."""

TOPICS_EN_NET_B = [
    dict(
        id="netinterp",
        title="Interpolation, extrapolation and jitter buffers",
        tags=["interpolation", "jitter", "buffer", "snapshots"],
        summary="Snapshots arrive unevenly: one after 30 ms, the next after 110. Rendering them directly makes the world stutter. The fix is to render 1–3 ticks in the past and interpolate between known states; extrapolation adds smoothness but lies about the future.",
        detail=[
            "The client keeps a buffer of snapshots sorted by server time. Rendering happens at <b>now − delay</b>: two snapshots around that point are interpolated for positions, angles (along the shortest arc) and states. A 100–200 ms delay hides jitter but adds latency, so it is made adaptive.",
            "Extrapolation (dead reckoning) continues motion from the last velocity when data has not arrived. It works well for bullets, vehicles and predictable trajectories, but a sharp turn produces rubber-banding and teleports. The rule: extrapolate no longer than 100–250 ms, and when the real snapshot disagrees, correct smoothly rather than snap.",
            "A jitter buffer can be estimated as “2×jitter + 2 ticks” and adjusted from p95 inter-packet intervals. In a low-tick MMO interpolation is mandatory even on a perfect network: 10 Hz means 100 ms between states. Secret: interpolate animation phases too, or feet slide; and flag teleports and respawns so they are not smoothed across half the map.",
        ],
        formula=("t_render = now − delay,   α = (t_render − t₀) / (t₁ − t₀),   "
                 "p = lerp(p₀, p₁, α),   delay ≈ 2 · jitter + 2 · tick",
                 "delay trades smoothness for input latency. For a 60 Hz shooter it is 2–3 ticks; for a 10 Hz MMO, 200–300 ms."),
        steps=[
            "Receive snapshots with server timestamps and push them into a buffer.",
            "Pick the render point = now − delay and find the two neighbouring snapshots.",
            "Interpolate positions, angles and parameters; flag teleports for instant jumps.",
            "Estimate jitter from p95 and adapt the delay.",
            "Add bounded extrapolation and smooth correction on mismatch.",
        ],
        complexity=("O(log n) buffer lookup, O(1) per entity", "O(buffer · entities)",
                    "8–16 buffered snapshots are plenty; interpolating 1000 entities costs fractions of a millisecond."),
        code=("python", """import bisect

def sample(buffer, t_render, entity):
    keys = [s.t for s in buffer]
    i = bisect.bisect_right(keys, t_render) - 1
    if i < 0:
        return buffer[0].entities[entity]
    if i >= len(buffer) - 1:
        return buffer[-1].entities[entity]          # extrapolation is separate
    a, b = buffer[i], buffer[i + 1]
    alpha = (t_render - a.t) / max(1e-6, b.t - a.t)
    pa, pb = a.entities[entity], b.entities[entity]
    return (
        pa.x + (pb.x - pa.x) * alpha,
        pa.y + (pb.y - pa.y) * alpha,
        pa.angle + shortest_arc(pb.angle - pa.angle) * alpha,
    )"""),
        pitfalls=[
            "Showing the latest snapshot immediately — the world jerks on every packet.",
            "A buffer that is too large: smooth, but controls lag by half a second.",
            "Extrapolating forever: when the player stops, they slide through walls.",
            "Interpolating angles with a plain linear formula — the character spins through 360°.",
        ],
        games=["Overwatch", "Battlefield", "World of Warcraft", "Rocket League"],
    ),
    dict(
        id="netlagcomp",
        title="Lag compensation: rewind and hit validation",
        tags=["rewind", "hitscan", "latency", "anti-cheat"],
        summary="Players aim at what they see, and they see the past by RTT/2 plus interpolation. Lag compensation rewinds server hitboxes to the moment of the shot, validates the hit and restores the state. Without it “headshot” becomes “miss”.",
        detail=[
            "The server keeps a position history (usually 0.5–1 s) for all entities. On a fire command it restores hitboxes to <b>t = now − (RTT/2 + interp_delay)</b>, traces the ray and applies damage. The rewind depth is capped at 200–300 ms: more becomes shooting through walls.",
            "The trade-off: “favor the shooter” gives fair hits to the attacker, but the victim can take damage after reaching cover. “Favor the defender” breaks the shooter's feel. Most competitive shooters choose the former and cap the rewind; projectiles need no rewind at all — the server simulates the bullet and decides where it lands.",
            "Secrets: rewind hitboxes only, never the whole physics world; store history compactly (position + pose + flags); validate that the shot was possible (ammo, cooldown, rate of fire); log “shot behind wall” cases when tuning; and do not rewind more than a frame or two for high-precision AWP-like mechanics.",
        ],
        formula=("t_rewind = t_now − (RTT/2 + interp_delay),   "
                 "clamp(t_rewind, now − 0.3 s, now),   "
                 "hit = ray(origin, dir) ∩ hitboxes(t_rewind)",
                 "RTT/2 is the trip to the server; interp_delay is the client's render delay. A 300 ms cap prevents shooting too far into the past."),
        steps=[
            "Store position and pose history with server timestamps for 0.5–1 s.",
            "Accept a shot with its client timestamp and clamp the rewind window.",
            "Restore hitboxes at that time and test the ray/sphere.",
            "Validate the shot: weapon, ammo, cooldown, line of sight.",
            "Log discrepancies (a hit on a target already behind cover) and tune the window.",
        ],
        complexity=("O(log h + k) per shot", "O(history · entities)",
                    "One second of history at 60 Hz is 60 snapshots; store only what hitboxes need."),
        code=("python", """def rewind_hit(history, shooter_time, origin, direction, max_ms=300):
    t = max(shooter_time, history[-1].t - max_ms / 1000.0)
    snapshot = history.closest(t)                # nearest frame at or before t
    for box in snapshot.hitboxes:
        if ray_hits_box(origin, direction, box):
            return box.owner                    # hit registered
    return None

def validate_shot(server, player, shot):
    if shot.client_time > server.time + 0.05:
        return "future timestamp"
    if player.ammo <= 0 or server.time < player.next_shot_at:
        return "rate limit"
    if not server.visible(player, shot.origin):
        return "origin mismatch"
    return None"""),
        pitfalls=[
            "Rewinding half a second or more: victims take damage behind cover.",
            "Rewinding all physics and other players — double hits and desync.",
            "Not limiting fire rate: the client “fires” a whole burst in one frame.",
            "Forgetting client interpolation and rewinding only RTT/2 — a systematic miss.",
        ],
        games=["Counter-Strike 2", "Valorant", "Overwatch", "Battlefield 2042"],
    ),
    dict(
        id="netaoi",
        title="Interest management: AOI, grids and relevance",
        tags=["AOI", "spatial hash", "relevance", "MMO"],
        summary="An MMO cannot send every player to everyone: 5,000 players × 1,000 entities is millions of updates. Interest management decides what a player actually sees and what matters, and replicates only that. AOI is the main secret of MMO scale.",
        detail=[
            "The simplest AOI is a radius: the client receives entities within r (say 100–200 m) plus “important” objects (quest givers, friends, vehicles). A spatial index (grid, quadtree, octree, BVH) answers “who is nearby” in O(log n + k) instead of O(n). Radii differ by type: players 150 m, NPCs 80 m, projectiles 40 m.",
            "A radius alone is not enough: importance depends on view angle, distance, entity type, state (idle/moving), friendship and quests. Relevance score = w₁·proximity + w₂·facing + w₃·type + w₄·recent events. The per-client budget is finite (say 8 KB/s), so when it overflows the least important data is dropped, not random data.",
            "MMO secrets: <b>hysteresis</b> (enter at 150 m, leave at 165 m) so entities do not flicker at the border; dormancy for far NPCs; updates grouped by zone; state handed to neighbours when crossing a zone boundary. And always: the client must never receive positions it should not see, otherwise a wallhack is trivial.",
        ],
        formula=("N_relevant ≈ ρ · π r²,   traffic ≈ N_relevant · S · tick,   "
                 "score = w₁·(1 − d/r) + w₂·facing + w₃·type + w₄·events",
                 "ρ is entity density and S the snapshot size per entity. Doubling the radius quadruples traffic, so the radius follows the budget."),
        steps=[
            "Build a spatial index (grid/quadtree) and update it on movement.",
            "Define radii and importance weights per entity type.",
            "Compute relevance and fit it into the client's bit budget.",
            "Add hysteresis and dormancy to remove flicker and idle ticks.",
            "Hide out-of-AOI entities at the protocol level, not only in rendering.",
        ],
        complexity=("O(log n + k) per query", "O(n) index + O(k) per client",
                    "10,000 entities and 2,000 players is a normal zone scale; a 32–64 m grid keeps k in the dozens."),
        code=("python", """def visible_entities(grid, player, radius=120.0, budget=400):
    candidates = grid.query_circle(player.x, player.y, radius)
    scored = []
    for e in candidates:
        d = dist(player, e)
        score = (1.0 - d / radius) * 2.0
        score += 1.0 if e.kind in ("quest", "party", "vehicle") else 0.0
        score += 0.5 if player.facing(e) else 0.0
        scored.append((score, e))
    scored.sort(reverse=True)
    return [e for _, e in scored[:budget]]      # a budget, not everything"""),
        pitfalls=[
            "Replicating every player in the zone and hoping compression saves you — traffic grows quadratically.",
            "Hard enter/leave without hysteresis — entities flicker at the border.",
            "Sending hidden entities “just in case” — a ready-made wallhack.",
            "One radius for everything: projectiles, NPCs and players have different value.",
        ],
        games=["World of Warcraft", "EVE Online", "New World", "Albion Online"],
    ),
    dict(
        id="netclock",
        title="Clock and tick synchronisation: offsets, ticks and timelines",
        tags=["clock", "tick", "NTP", "timeline"],
        summary="The network has no shared “now”: every client has its own clock and jitter. The server defines the tick and timeline, clients estimate offset and RTT, and the simulation runs on server time — otherwise prediction, rewind and interpolation fall apart.",
        detail=[
            "The classic estimate (as in NTP/Cristian): the client sends t0, the server replies with t1 (receive) and t2 (send), the client records t3. Then RTT = (t3 − t0) − (t2 − t1) and offset = ((t1 − t0) + (t2 − t3)) / 2. A single sample is noisy: take the minimum RTT of a series and the median offset, then slew the clock instead of jumping.",
            "Game time is best counted in ticks: the server tick is an integer and the client knows which tick a snapshot belongs to. Separately there is frame time (rendering) and input time (when the player pressed). All three must be distinguished: binding input to a server tick is the basis of fair rewind.",
            "Secrets: use monotonic clocks (`performance.now`), never the system clock; do not trust client timestamps without bounds; an offset can jump when the network changes — smooth it; fix a match epoch so replays and logs line up. In distributed MMOs server clocks are synchronised with NTP/PTP, otherwise events cannot be ordered causally in logs.",
        ],
        formula=("RTT = (t₃ − t₀) − (t₂ − t₁),   "
                 "offset = ((t₁ − t₀) + (t₂ − t₃)) / 2,   "
                 "server_tick = round((client_now + offset) · tick_hz)",
                 "t0 is the client send, t1/t2 the server receive/reply, t3 the client receive. The minimum RTT gives the best offset estimate."),
        steps=[
            "Measure time with monotonic clocks and send a ping with t0 and the server's t1/t2.",
            "Compute RTT and offset; reject outliers, use the median and the minimum RTT.",
            "Slew the offset smoothly instead of jumping.",
            "Bind player input to a server tick and keep the match timeline.",
            "Synchronise servers with NTP/PTP and log drift.",
        ],
        complexity=("O(1) per sample", "O(1) per connection + sample history",
                    "20–30 samples at match start are enough; after that, rare keepalives and adaptive correction."),
        code=("python", """class ClockSync:
    def __init__(self):
        self.samples = []          # (rtt, offset)
        self.offset = 0.0

    def add(self, t0, t1, t2, t3):
        rtt = (t3 - t0) - (t2 - t1)
        offset = ((t1 - t0) + (t2 - t3)) / 2
        self.samples.append((rtt, offset))
        if len(self.samples) > 30:
            self.samples.pop(0)
        best = min(self.samples, key=lambda s: s[0])
        target = best[1]
        self.offset += (target - self.offset) * 0.05   # smooth slew
        return rtt, self.offset"""),
        pitfalls=[
            "Using `Date.now()`: clock changes and NTP jumps break the timeline.",
            "Averaging all offsets — outliers ruin the estimate.",
            "Changing the offset abruptly: the world teleports and interpolation breaks.",
            "Mixing frame time, server tick and input time — rewind and prediction lie.",
        ],
        games=["Valorant", "Overwatch", "World of Warcraft", "EVE Online"],
    ),
    dict(
        id="netbudget",
        title="Bandwidth budget: prioritisation, deltas and quantisation",
        tags=["bandwidth", "priority", "delta", "quantisation"],
        summary="Every player has a budget: 5–10 KB/s in a shooter, 1–3 KB/s in an MMO — headers included. Inside that budget you must fit what matters: nearby, threatening, recently changed. Bandwidth is a resource just like frame time.",
        detail=[
            "Count the budget downwards: a 100 Mbit/s server for 200 players is 62 KB/s each, minus headers and service traffic; the real game budget will be 10–20 KB/s. Inside it, priorities rule: events (shot, death, loot) always go out; state goes by relevance and freshness; cosmetics (emotes, skins) go last.",
            "Delta encoding: keep the last acknowledged snapshot per client and send only changes. Quantisation: 19 bits for a position, 12 for an angle, 10 for health. Flags become a bitmask, arrays get a length prefix. Do not compress small packets with a general compressor: overhead and latency eat the gain; LZ4/zstd make sense for big snapshots.",
            "The algorithm: collect candidates with priorities, sort, send until the budget is exhausted, carry the rest to the next tick. Add <b>aging</b>: if an entity has not been updated for too long, its priority grows, otherwise a distant but important object freezes. And always measure real on-the-wire bytes, not in-memory structs.",
        ],
        formula=("budget = rate · tick,   send while Σ size_i ≤ budget,   "
                 "priority = relevance · freshness + aging",
                 "rate is the target bitrate per client and tick the snapshot period. Deltas and quantisation cut size_i several-fold."),
        steps=[
            "Derive the per-client bitrate from server bandwidth and reserve room for headers.",
            "Split traffic into events (reliable) and state (budgeted).",
            "Compute priority from relevance, freshness and aging.",
            "Encode deltas against the acknowledged snapshot and quantise fields.",
            "Log real bytes per second and budget hits; tune against p95.",
        ],
        complexity=("O(n log n) sorting, O(n) packing", "O(n) per client",
                    "8 KB/s at 20 Hz is 400 bytes per snapshot: enough for 10–20 entities with deltas."),
        code=("python", """def build_snapshot(entities, last_ack, budget_bytes=400):
    items = []
    for e in entities:
        delta = e.delta_from(last_ack.get(e.id))
        prio = e.relevance * (1.5 if delta else 0.5) + e.aging
        items.append((prio, delta.size, e.id, delta))
    items.sort(reverse=True)
    out, used = [], 0
    for prio, size, eid, delta in items:
        if used + size > budget_bytes:
            continue
        out.append((eid, delta))
        used += size
    return out, used"""),
        pitfalls=[
            "Counting the budget without UDP/IP headers and service traffic — the wire shows more.",
            "Sending everything “just in case” and hoping compression saves you.",
            "Forgetting aging: a distant important entity stops updating and freezes.",
            "Compressing every tiny packet — latency and overhead exceed the savings.",
        ],
        games=["World of Warcraft", "EVE Online", "PlanetSide 2", "Overwatch"],
    ),
    dict(
        id="netshard",
        title="Sharding, zones and seamless worlds",
        tags=["sharding", "zones", "handoff", "MMO"],
        summary="One process cannot hold a million players. The world is cut into zones, instances and shards, each with its own simulation process and budget; seamlessness is an illusion maintained by state transfer, neighbour caches and prefetching at the border.",
        detail=[
            "Sharding comes in flavours: by region (US/EU/Asia), by zone (forest, city, dungeon), by instance (raid, PvP match), by population layer for overflow. Each shard is a process/container with a hard entity limit; gateways hold connections while the world lives in separate services. A typical zone holds 500–3,000 players, a raid instance 10–40.",
            "Seamlessness: as a player approaches a border they are “handed over” to the neighbouring zone. Input is frozen, a snapshot is transferred, ownership changes and input resumes; meanwhile the next zone renders from cache. A slow handoff is felt as a hitch. The secret is subscribing to neighbouring entities early (prefetch) and keeping borders “thick”: AOI must cross them rather than stop.",
            "Shared objects are a separate problem: auction house, chat, guilds, mail. They cannot be sharded per zone or you get inconsistent copies, so they become dedicated services with their own databases and caches, called with idempotent APIs. Balance zones with consistent hashing over zone_id and virtual nodes so a crashed process only loses its own zones, not the world.",
        ],
        formula=("shards = ⌈CCU / capacity⌉,   handoff_time = freeze + state_transfer + resume,   "
                 "load(shard) = Σ entities · tick_cost + network",
                 "capacity is how many players a process holds at the target tick. handoff_time must fit into 100–300 ms, or players feel a hitch."),
        steps=[
            "Cut the world into zones/instances and fix a capacity per process.",
            "Separate gateways (connections) from simulation and shared services.",
            "Implement ownership transfer: freeze, snapshot, transfer, resume.",
            "Prefetch neighbouring zones and cache across the border.",
            "Balance zones with consistent hashing and monitor overload.",
        ],
        complexity=("O(1) per handoff, O(log n) to pick a shard", "O(zone) state + caches",
                    "A zone with 2,000 players and 20,000 entities is a typical limit for one game process."),
        code=("python", """import hashlib

def shard_for(zone_id, shards):
    # consistent hashing: a failed node only moves its own share
    ring = sorted((hashlib.md5(f"{s}".encode()).hexdigest(), s) for s in shards)
    h = hashlib.md5(str(zone_id).encode()).hexdigest()
    for point, shard in ring:
        if h <= point:
            return shard
    return ring[0][1]

def handoff(player, from_zone, to_zone, snapshot):
    player.freeze()                 # input is not applied
    to_zone.adopt(player, snapshot) # ownership and state
    from_zone.release(player)
    player.resume()                 # the client receives a new tick"""),
        pitfalls=[
            "One process for the whole world and hoping vertical scaling saves you.",
            "Thin zone borders: AOI stops abruptly and players see a wall of fog.",
            "Shared services (auction, chat) in every zone — desync and duplication.",
            "A slow handoff: players freeze at the border and lose control.",
        ],
        games=["World of Warcraft", "EVE Online", "New World", "RuneScape"],
    ),
    dict(
        id="netsession",
        title="Sessions, lobbies, matchmaking and reconnect",
        tags=["session", "matchmaking", "lobby", "reconnect"],
        summary="A match is not just a server, it is state: who is in it, on which ticket, in which region, and what happens when someone disconnects. A session service survives game-process restarts: it issues tickets, builds lobbies, matches players and returns them to the fight after a drop.",
        detail=[
            "Separate the roles: the gateway holds the WebSocket/UDP connection, the session service stores the session (player, match, token, region, rights), the matchmaker builds lobbies, the game server simulates. Clients never talk to the matchmaker directly — they get a ticket and wait for an event. This lets services restart without losing players.",
            "Matchmaking is multi-criteria: MMR/rank, party size, region, latency, queue time, backfill after a leaver. Hard filters (region/ping) apply immediately, soft filters (rank) relax over time as the ticket ages. Otherwise top players wait for hours.",
            "Reconnect: the player has a session token and a match slot for 60–120 s; the server keeps their entity “on leave” rather than deleting it. On return the client receives a full snapshot and continues from the current tick. Secrets: prevent ghosting (two clients on one session), make login idempotent, run regional queues and make backfill fair so a newcomer is not fed to a stacked team.",
        ],
        formula=("wait ≈ queue_len / match_rate,   quality = f(ΔMMR, Δping, party),   "
                 "ticket_age → relax(ΔMMR) and relax(Δping)",
                 "The matchmaker trades quality against time. Relaxing filters as tickets age is the main way to avoid endless queues."),
        steps=[
            "Create a session service: token, region, match, rights, lifetime.",
            "Separate gateway from game server; clients talk only to the gateway.",
            "Design the matchmaking ticket: hard and soft filters, aging.",
            "Implement a reconnect slot (60–120 s) and a full snapshot on return.",
            "Log wait times, match quality and ticket cancellation reasons.",
        ],
        complexity=("O(log n) queue search", "O(players) + queue",
                    "Peak online means tens of thousands of tickets; the matchmaker must scale horizontally and stay stateless."),
        code=("python", """import time

def try_match(ticket, pool, now):
    ticket.age = now - ticket.created
    mmr_window = 50 + ticket.age * 25          # soft filter relaxes
    for other in pool:
        if other.player == ticket.player:
            continue
        if abs(other.mmr - ticket.mmr) > mmr_window:
            continue
        if abs(other.ping - ticket.ping) > 80:  # hard region/ping filter
            continue
        return (ticket, other)
    return None

def reconnect(session, slot_ttl=90):
    if session.left_at and time.time() - session.left_at > slot_ttl:
        return "slot expired"
    return {"tick": session.match.tick, "snapshot": session.match.snapshot(session.player)}"""),
        pitfalls=[
            "Keeping the match only in game-process memory: a crash loses everything.",
            "Matchmaking without aging — top players wait forever.",
            "Deleting the player entity immediately on disconnect — reconnect becomes impossible.",
            "Allowing two clients on one session — ghosting and cheating.",
        ],
        games=["Counter-Strike 2", "League of Legends", "Apex Legends", "Fortnite"],
    ),
    dict(
        id="netpersist",
        title="MMO persistence: databases, caches, transactions and event sourcing",
        tags=["database", "redis", "transactions", "event sourcing"],
        summary="In an MMO items and gold are money, and money cannot be lost when a process crashes. Persistence is transactions, idempotency and ordering: who owns the record, what is the source of truth, and how to survive a restart without dupes or vanished bags.",
        detail=[
            "The classic setup: a relational database (PostgreSQL/MySQL) for inventory, characters and the auction house; Redis for hot data and locks; the game process keeps dirty objects in memory and flushes in batches. The danger is the flush moment: if the process dies between debiting gold and granting a sword, one player loses. The fix is a database transaction, not two independent UPDATEs.",
            "For distributed operations use a saga/outbox: write the event into an outbox in the same transaction, apply it asynchronously, and make retries safe with an <b>idempotency key</b>. Event sourcing stores an event log and derives state as a fold, which enables rollback, auditing and recovery. The cost is volume and schema evolution.",
            "Secrets: shard by player_id, not by guild; cache with TTL and version; locks need timeouts and fencing tokens; never trust “I had that item” from a client; the auction house and mail are separate services with their own transactions; backups and restore drills are part of gameplay, not just DevOps. And remember: item duplication is almost always born from retries without idempotency.",
        ],
        formula=("state = fold(events),   write_conflict = version mismatch,   "
                 "retries → idempotency_key → exactly-once effect",
                 "Record versions (optimistic locking) prevent lost updates; an idempotency key turns a retry into a no-op."),
        steps=[
            "Separate hot state (memory/Redis) from cold state (DB) and define ownership.",
            "Make operations transactional: debit and grant in one transaction.",
            "For cross-service operations use outbox/saga and idempotency keys.",
            "Shard by player_id and add versioning and locks with fencing tokens.",
            "Regularly test restore from backup and event replay.",
        ],
        complexity=("O(1) per operation, O(log n) per index", "O(players) per shard + cache",
                    "Thousands of writes per second per shard is normal; p99 commit time matters more than average TPS."),
        code=("python", """def transfer_item(conn, from_id, to_id, item_id, idem_key):
    with conn.transaction():
        seen = conn.execute(
            "SELECT 1 FROM idempotency WHERE key = %s", (idem_key,)).fetchone()
        if seen:
            return "already applied"          # retry is safe
        cur = conn.execute(
            "UPDATE items SET owner = %s WHERE id = %s AND owner = %s",
            (to_id, item_id, from_id))
        if cur.rowcount != 1:
            raise ValueError("item not owned by sender")
        conn.execute(
            "INSERT INTO idempotency(key, applied_at) VALUES (%s, now())", (idem_key,))
    return "ok\""""),
        pitfalls=[
            "Two independent UPDATEs without a transaction: gold debited, item never granted.",
            "Retries without an idempotency key — duplicated items and currency.",
            "The cache as the source of truth without invalidation — desync and phantom bags.",
            "Locks without timeout/fencing tokens — permanent deadlocks after a crash.",
        ],
        games=["World of Warcraft", "EVE Online", "Albion Online", "RuneScape"],
    ),
    dict(
        id="netsecurity",
        title="Security: DDoS, rate limits, auth and encryption",
        tags=["DDoS", "rate limit", "auth", "encryption"],
        summary="A network service lives on the internet, so it will be attacked, flooded and reverse-engineered. Defence is layered: anycast and scrubbing for volumetric attacks, limits and queues for L7, tokens and TLS against spoofing, and server-side validation against cheating input.",
        detail=[
            "DDoS comes in three flavours: volumetric (L3/L4, gigabits), protocol (SYN/QUIC floods) and application (L7, expensive requests). Infrastructure: anycast, CDN/scrubbing centres, per-IP/account limits, proof-of-work under suspicion, login queues. Game servers must not expose their real IPs: clients connect to an edge proxy that holds the session.",
            "Authentication: short-lived tokens bound to an account/device, TLS/DTLS for transport, nonce/sequence against replay. Never trust the client: validate speed, cooldowns, distance, line of sight and item ownership. Encryption does not stop cheats, but it protects against MITM and simplifies trust.",
            "Rate limiting: token buckets per account/IP/connection, separate limits for expensive operations (chat, auction, crafting), backoff and ban waves. Secrets: log rejection metrics but store no unnecessary personal data; keep secrets in a KMS, not the repository; validate match tickets on the server (a client cannot “join” someone else's match); and during an attack degrade features rather than lose every player.",
        ],
        formula=("allowed(t) = min(cap, tokens + rate·t),   "
                 "request_cost ≤ tokens,   "
                 "valid = signature ∧ freshness ∧ ownership ∧ cooldown",
                 "A token bucket caps the average rate while allowing bursts; server-side validation is the last line of defence against cheating input."),
        steps=[
            "Hide game servers behind an edge proxy; enable anycast/scrubbing.",
            "Issue short-lived session tokens bound to the account.",
            "Rate-limit per IP/account/operation and protect expensive endpoints.",
            "Validate everything on the server: movement, damage, economy, ownership.",
            "Monitor anomalies and rehearse a degradation plan for launch peaks.",
        ],
        complexity=("O(1) per token check", "O(1) per connection + counters",
                    "Signature and limit checks take microseconds; the bottleneck is attack bandwidth and scrubbing cost."),
        code=("python", """import time

class TokenBucket:
    def __init__(self, rate=20, cap=60):
        self.rate, self.cap = rate, cap
        self.tokens, self.last = cap, time.monotonic()

    def allow(self, cost=1):
        now = time.monotonic()
        self.tokens = min(self.cap, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True

def validate_intent(player, intent, now):
    if intent.ts > now + 0.05 or intent.ts < now - 0.5:
        return "stale timestamp"
    if not player.owns(intent.item):
        return "not owned"
    if player.cooldown(intent.skill) > now:
        return "cooldown"
    return None"""),
        pitfalls=[
            "Exposing game-server IPs — an attack finds the target directly.",
            "Trusting client-side speed/damage checks — the first cheat breaks the economy.",
            "One global rate limit: a legitimate spike blocks everyone.",
            "Logging tokens and personal data in plain text.",
        ],
        games=["Valorant", "EVE Online", "World of Warcraft", "Roblox"],
    ),
    dict(
        id="netops",
        title="Operations: metrics, SLOs, traces and live ops",
        tags=["observability", "SLO", "metrics", "live-ops"],
        summary="Networks break in the tails, not the averages: p99 RTT, 2 % loss on one route, a login queue at peak. Operations means a dashboard, SLOs and controlled degradation instead of “fix it after release”.",
        detail=[
            "Metrics: RTT p50/p95/p99 per region, loss, reorder, jitter, server tick time, snapshot size, queue depth, CCU, auth errors, matchmaking time. Metrics without region/version/platform breakdowns are useless: a 40 ms average RTT can hide a region at 200 ms.",
            "An SLO defines the error budget: for example 99 % of matches with p95 RTT < 80 ms and 99.9 % successful logins. Alerts fire on burn rate, not on a single spike. Traces link a match, a session and database queries by one id; logs are structured and sampled so you do not drown.",
            "Live ops: feature flags, canary releases, content and balance rollbacks without a patch, regional switches, degradation (disable cosmetics/voice, lower the tick), status communication. Load bots must play like humans: move, shoot, join matches; synthetic metrics without behaviour miss the bottlenecks. After an incident, run a blameless postmortem with concrete actions.",
        ],
        formula=("error_budget = 1 − SLO,   burn_rate = observed_error / allowed_error,   "
                 "p99 ≠ 3·p50 (heavy tail)",
                 "An SLO is a contract with players. Burn-rate alerts catch sustained degradation instead of a random spike."),
        steps=[
            "Define 5–7 key SLIs: latency, loss, login success, tick time, matchmaking.",
            "Break metrics down by region, platform, version and network type.",
            "Alert on burn rate and build dashboards for the on-call engineer.",
            "Add feature flags, canary releases and a degradation plan.",
            "Run load bots and postmortems regularly.",
        ],
        complexity=("O(1) per metric write", "O(series × retention)",
                    "Metric cardinality is the main enemy: never put player_id into labels."),
        code=("python", """import statistics

def slo_report(samples, slo=0.99, target_ms=80):
    lat = sorted(samples)
    p95 = lat[int(len(lat) * 0.95)]
    good = sum(1 for x in lat if x <= target_ms) / len(lat)
    budget = 1.0 - slo
    burn = (1.0 - good) / budget if budget else 0.0
    return {"p95_ms": p95, "good": good, "burn_rate": burn,
            "alert": burn > 2.0}          # 2× is sustained degradation"""),
        pitfalls=[
            "Looking only at averages: the p99 tail is the player experience.",
            "Metrics without region/platform breakdowns hide entire outages.",
            "Alerting on everything: on-call stops reacting.",
            "Load bots that stand still: they never find the bottlenecks.",
        ],
        games=["Riot Games", "Blizzard", "EVE Online", "Roblox"],
    ),
    dict(
        id="nettest",
        title="Network testing: netem, chaos and load bots",
        tags=["netem", "chaos", "load test", "replay"],
        summary="Netcode cannot be tested on localhost. You need controlled delay, jitter, loss, reorder and duplicates — as on real networks; deterministic replays to reproduce bugs; bots that behave like humans; and chaos tests that break services on purpose.",
        detail=[
            "Linux `tc netem` supports delay, jitter, loss, duplicate, reorder, corrupt and rate; Windows/macOS have equivalents (clumsy, Network Link Conditioner). Inside the engine it helps to have your own deterministic network simulator: delay packets by N ticks, drop by probability, reorder — reproducibly, so a bug repeats in CI. Profiles: 3G (200 ms RTT, 2 % loss), bad Wi-Fi (50 ms jitter), intercontinental (150 ms RTT).",
            "Replays: recorded inputs + seed + version = a reproducible match. That is how you debug desync, rollback and lag compensation without live players. Chaos tests: kill the game process, drop Redis, add 500 ms to the database, cut the connection at a zone border — and verify the player returns and the economy stays intact.",
            "Load bots must imitate behaviour: movement, shooting, purchases, chat, reconnects; otherwise TPS looks great while p99 dies on live players. Secrets: test in production at night with a small percentage, use shadow traffic, compare metrics before/after a release, keep test regions with real RTT, and always test mobile networks — a browser emulator will not show you radio behaviour.",
        ],
        formula=("coverage = delay × jitter × loss × reorder × duplicates,   "
                 "replay = (inputs, seed, version),   "
                 "bot_fidelity = actions / second × state coverage",
                 "The condition matrix matters more than one “bad” profile. Without a replay a network bug cannot be reproduced; without bots it cannot be found."),
        steps=[
            "Add a deterministic network simulator to the engine (delay/jitter/loss/reorder).",
            "Define real-network profiles: 3G, bad Wi-Fi, intercontinental, mobile.",
            "Record input replays and run them in CI on every build.",
            "Deploy load bots with behaviour and reconnects.",
            "Run chaos tests and a postmortem for every failure found.",
        ],
        complexity=("O(1) per packet in the simulator", "O(simulator buffer + replays)",
                    "An in-engine simulator is cheaper and more reproducible than external netem; netem is for testing the real stack."),
        code=("python", """import random, heapq

class NetSim:
    def __init__(self, delay=0.1, jitter=0.02, loss=0.02, seed=1):
        self.delay, self.jitter, self.loss = delay, jitter, loss
        self.rng, self.q, self.now = random.Random(seed), [], 0.0

    def send(self, payload):
        if self.rng.random() < self.loss:
            return                      # dropped
        d = max(0.0, self.delay + self.rng.uniform(-1, 1) * self.jitter)
        heapq.heappush(self.q, (self.now + d, payload))

    def tick(self, dt):
        self.now += dt
        out = []
        while self.q and self.q[0][0] <= self.now:
            out.append(heapq.heappop(self.q)[1])
        return out                      # reorder possible with different d"""),
        pitfalls=[
            "Testing only on localhost and perfect Wi-Fi.",
            "Manual network checks without profiles and without reproducible replays.",
            "Bots that do not move or shoot: the load does not resemble live traffic.",
            "Chaos tests without guardrails: they take production down for everyone.",
        ],
        games=["Riot Games", "Overwatch", "Valorant", "EVE Online"],
    ),
]
