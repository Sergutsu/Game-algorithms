# -*- coding: utf-8 -*-
"""Part III, layers 01–02: transport, topology, sync models (topics 87–93)."""

TOPICS_EN_NET_A = [
    dict(
        id="nettransport",
        title="Transport: UDP, TCP, QUIC and WebTransport",
        tags=["UDP", "TCP", "QUIC", "MTU"],
        summary="Transport decides what you can build at all. TCP gives ordering and reliability at the cost of head-of-line blocking, UDP gives full control and full responsibility, QUIC gives multiplexed reliable streams over UDP, and WebTransport brings that to the browser.",
        detail=[
            "TCP is convenient for lobbies, HTTP APIs, stores and chat: it handles retransmits, ordering and congestion control. It is bad for real time: one lost segment stalls <b>everything</b> behind it (head-of-line blocking), while Nagle and delayed ACK add tens of milliseconds to small packets. In a shooter that feels like a rubber-banded world.",
            "UDP guarantees nothing — no delivery, no order, no size. In exchange the application decides what to resend and what to drop: a player position is stale in 100 ms, while a “shot fired” event must arrive. The path MTU is usually 1500 bytes; a safe datagram is <b>1200 bytes</b>, anything larger is fragmented and lost as a whole. Ready-made layers: ENet, GameNetworkingSockets, KCP, QUIC.",
            "QUIC is UDP + TLS 1.3 + multiplexed streams + connection migration: streams do not block each other, the handshake is 1-RTT (0-RTT on resume) and encryption is mandatory. In browsers QUIC arrives via WebTransport (HTTP/3), while WebRTC data channels give SCTP over DTLS. In practice: HTTP/WebSocket for the control plane, UDP/QUIC for real time; separate channels for reliable events and unreliable state; measure p50/p95 RTT, loss and jitter, not the average.",
        ],
        formula=("goodput ≈ (1 − loss) · cwnd / RTT,   datagram ≤ 1200 B,   "
                 "rate ≈ tick_hz · snapshot_bytes · players",
                 "Throughput is bounded by window and RTT; games care about p99 latency, not the mean. A higher tick and bigger snapshots raise the bandwidth every player needs."),
        steps=[
            "Split traffic: lobby, store and chat over reliable HTTP/WebSocket; the game world over UDP/QUIC.",
            "Create channels: reliable-ordered (events), reliable-unordered (files, inventory), unreliable (positions, angles).",
            "Keep datagrams under 1200 bytes and fragment larger messages at the application level.",
            "Instrument RTT p50/p95/p99, loss, jitter, reorder and send-queue depth.",
            "Pick a ready-made layer (ENet, GNS, KCP, QUIC) and test it on real networks, not localhost.",
        ],
        complexity=("O(1) per datagram; O(log n) per QUIC stream", "O(send and receive buffers)",
                    "A game server with 200–1000 players moves tens of MB/s; the bottleneck is bandwidth and p99, almost never CPU."),
        code=("python", """def choose_transport(realtime, needs_order, browser, lossy_network):
    # Returns the transport and its main trade-off.
    if not realtime:
        return "TCP/HTTP", "order and reliability matter more than latency"
    if browser:
        if needs_order:
            return "WebSocket", "TCP in the browser: simple but HOL-blocking"
        return "WebRTC data channel", "SCTP/DTLS, unreliable mode over UDP"
    if needs_order and not lossy_network:
        return "QUIC", "streams without HOL, TLS 1.3, but encryption costs CPU"
    return "UDP + own layer", "ENet/KCP/GNS: full control, full responsibility"
"""),
        pitfalls=[
            "Sending positions over TCP: one loss stalls everything and latency spikes.",
            "Sending packets above the MTU: one lost fragment loses the whole packet.",
            "One stream for everything: voice, chat and the world compete for one queue and one congestion window.",
            "Ignoring Nagle/delayed ACK and measuring latency only on localhost.",
        ],
        games=["Counter-Strike 2", "Valorant", "Rocket League", "Fortnite"],
    ),
    dict(
        id="netreliable",
        title="Reliability over UDP: sequence, ACK, RTO and congestion control",
        tags=["ACK", "RTO", "congestion", "retransmit"],
        summary="Reliability is not “resend until it arrives”, it is a contract: which messages must arrive, in what order and by when. Sequence numbers, ACK bitfields, smoothed RTT and RTO provide predictability; congestion control stops your game from killing someone else's Wi-Fi.",
        detail=[
            "Every packet gets a number and a send time. The receiver ACKs the last delivered number plus a 32-bit bitmap of the ones before it, so one ACK confirms a batch. The sender keeps a window of unacknowledged packets, measures RTT and retransmits on <b>RTO</b> or after three duplicate ACKs (fast retransmit).",
            "RTO cannot be fixed: a mobile network changes RTT by a factor of ten. The classic recipe (RFC 6298): <b>SRTT</b> smoothed by 7/8, <b>RTTVAR</b> by 3/4, RTO = SRTT + 4·RTTVAR with a 100–200 ms floor. Games often shorten RTO and add per-message reliability: a stale position is not resent, the next fresh one replaces it.",
            "Congestion control is the other half: without it retransmits make loss worse. Plain AIMD doubles the window on start and halves it on loss; better options are pacing and bandwidth estimation (GCC, BBR). Production games keep the reliable channel separate from the unreliable one: events and inventory are acknowledged, snapshots are not. That is why “UDP + custom reliability” beats TCP for shooters at 1–3 % loss.",
        ],
        formula=("SRTT ← 7/8·SRTT + 1/8·RTT,   RTTVAR ← 3/4·RTTVAR + 1/4·|SRTT − RTT|,   "
                 "RTO = SRTT + 4·RTTVAR,   cwnd ← cwnd + 1/cwnd per ACK, cwnd ← cwnd/2 on loss",
                 "Smoothing absorbs jitter; RTTVAR sets the safety margin. RTO is a trade-off: too small causes retransmit storms, too large stalls after a single loss."),
        steps=[
            "Number reliable messages; keep a send window and a buffer of unacknowledged packets.",
            "ACK the last number plus a 32-bit bitmap; handle duplicates.",
            "Compute SRTT/RTTVAR and RTO per RFC 6298; clamp them at both ends.",
            "Add fast retransmit on three duplicate ACKs and pace outgoing packets.",
            "Split channels: reliable events, latest-wins state; enable congestion control.",
        ],
        complexity=("O(1) per packet, O(w) per window", "O(w) buffers + ACK bitmap",
                    "A window of 256–1024 packets is plenty; at 5 % loss the game traffic should degrade smoothly, not collapse."),
        code=("python", """import collections, time

class ReliableChannel:
    def __init__(self):
        self.next_id = 0
        self.sent = collections.OrderedDict()   # id -> (payload, send_time)
        self.srtt, self.rttvar = 0.1, 0.05
        self.window = 64

    def send(self, payload):
        pid = self.next_id
        self.next_id += 1
        self.sent[pid] = (payload, time.monotonic())
        return pid, payload

    def on_ack(self, last, bitfield, now):
        send_time = self.sent.get(last, (None, now))[1]
        sample = now - send_time
        for i in range(32):                     # bitmap of earlier packets
            if bitfield >> i & 1:
                self.sent.pop(last - i - 1, None)
        self.sent.pop(last, None)
        self.srtt += (sample - self.srtt) / 8
        self.rttvar += (abs(sample - self.srtt) - self.rttvar) / 4

    def due_retransmits(self, now):
        rto = max(0.1, self.srtt + 4 * self.rttvar)
        return [pid for pid, (_, t) in self.sent.items() if now - t > rto]"""),
        pitfalls=[
            "A fixed RTO: on mobile it either spams retransmits or stalls.",
            "Acknowledging and resending everything, including stale positions — more traffic, no benefit.",
            "Not distinguishing duplicates from new packets: events apply twice (double damage, double purchase).",
            "Forgetting congestion control: your game creates the loss it then blames on the network.",
        ],
        games=["Quake III", "Counter-Strike 2", "Overwatch", "Apex Legends"],
    ),
    dict(
        id="nettopology",
        title="Topologies: dedicated, listen, P2P, relay and mesh",
        tags=["dedicated", "listen", "P2P", "relay"],
        summary="Topology answers “who writes the truth”. A dedicated server removes host advantage and cheating, a listen server is cheaper and simpler, P2P saves servers, and a relay rescues NAT and asymmetric routes. The choice is a budget of trust and money.",
        detail=[
            "Dedicated: a separate process owns the simulation, clients only send input. Pros — fairness, anti-cheat, predictable load; cons — server bills and the extra “client → server → client” hop. Competitive games default to it: <b>128 ticks</b> in CS2/Valorant, servers in the player's region.",
            "Listen server: one player hosts the world. Cheap and great for co-op, but the host sees everything, has zero latency and the match dies with them. Raw P2P without a dedicated authority suits casual games but needs consensus or a host and suffers from cheaters: every client knows the full state.",
            "Relay is the compromise: clients connect through a neutral node that forwards or simulates. It solves NAT, evens out routes (relayed RTT is often lower than a bad direct peering path) and hides IPs. Mesh (everyone to everyone) scales as O(n²) and only works for 4–8 players. Real productions are hybrids: P2P lobbies, dedicated matches, relayed voice.",
        ],
        formula=("L_dedicated = (RTT_client→server + RTT_server→client) / 2 ≈ RTT/2 + tick,   "
                 "L_p2p = RTT/2,   L_relay = RTT(client→relay) + RTT(relay→client)",
                 "A client sees its own motion instantly (prediction) but others with the topology's latency. A listen host has a one-RTT advantage."),
        steps=[
            "Decide who is authoritative: server, host or consensus, and write it into the protocol.",
            "Budget dedicated cost per CCU against cheat risk and host advantage.",
            "Choose the path: direct P2P, relay or dedicated; for 5v5 use dedicated plus relayed voice.",
            "Design host migration for listen servers: world snapshot, new host election, reconnection.",
            "Measure latency and loss on real routes between regions, not inside one network.",
        ],
        complexity=("O(n) outbound on the server, O(n²) in mesh", "O(n) state per node",
                    "One dedicated process holds 16–64 shooter players or hundreds in an MMO zone; mesh above 8 players chokes upload."),
        code=("python", """def route(packet, topology, sender, authority):
    # Returns the recipients of an input/state packet.
    if topology == "dedicated":
        return [authority] if sender != authority else list(packet.listeners)
    if topology == "listen":
        host = authority                      # one of the players
        return [host] if sender != host else list(packet.listeners)
    if topology == "relay":
        return [packet.relay]                 # the relay decides the next hop
    if topology == "mesh":
        return [p for p in packet.listeners if p != sender]
    raise ValueError(topology)"""),
        pitfalls=[
            "Giving a listen host full authority in a competitive game — players feel the advantage.",
            "Building a 16-player mesh: upload and connection count grow quadratically.",
            "Forgetting host migration: one player leaving kills the match.",
            "Assuming direct P2P always beats a relay: bad peering can be worse than a data centre.",
        ],
        games=["Valorant", "Deep Rock Galactic", "Among Us", "Elden Ring"],
    ),
    dict(
        id="netnat",
        title="NAT, STUN, TURN, ICE and hole punching",
        tags=["NAT", "STUN", "TURN", "ICE"],
        summary="NAT exists to save IPv4 and it breaks inbound connections. Hole punching opens a path through two NATs at once, STUN reports the public address, TURN relays traffic when punching fails, and ICE tries every candidate and picks the best one.",
        detail=[
            "A client behind NAT does not know its public address or port. A STUN server answers “from the outside you look like 203.0.113.7:51820”. If both clients send to each other at the same time, each NAT creates state and inbound packets start flowing — that is <b>hole punching</b>. It works for cone NATs; a symmetric NAT allocates a new port per destination, which is hard to predict.",
            "ICE collects candidates: local addresses, STUN addresses, TURN relays, and tests pairs in priority order (direct first, relay last). TURN is a relay with bandwidth and a bill: all traffic goes through it, including voice and video. That is why TURN lives separately and is enabled only when a direct path fails.",
            "Games use the same dance: the lobby exchanges candidates, the match runs peer-to-peer, and if NAT wins, traffic goes through relay servers. IPv6 is slowly removing the problem, but CGNAT and mobile carriers bring it back. Practical secrets: several STUN/TURN servers per region, port 443 to survive strict networks, no IP logging without a reason, and an always-available “play via relay” fallback.",
        ],
        formula=("public_endpoint = STUN(client),   "
                 "hole_punch_success ≈ P(cone NAT)²,   "
                 "RTT_relay = RTT(client→relay) + RTT(relay→peer)",
                 "A symmetric NAT defeats port prediction; only TURN remains. A relay adds latency and bandwidth cost, so it is chosen last."),
        steps=[
            "Collect local candidates and ask STUN for the public address.",
            "Exchange candidates through a signalling server (WebSocket/HTTP).",
            "Fire simultaneous outbound packets at each other and check connectivity.",
            "Add TURN relays as a fallback with bandwidth and region limits.",
            "Log which path was chosen (direct/relay) and why — it is the key network metric.",
        ],
        complexity=("O(k²) candidate checks in ICE", "O(k) candidates per connection",
                    "A direct path costs no extra servers; a relay costs bandwidth for every player and adds RTT. Keep TURN away from game servers."),
        code=("python", """def punch(local_port, stun, signal, turn=None):
    # 1. Ask STUN for the public address.
    public = stun.request(local_port)          # ("203.0.113.7", 51820)
    # 2. Exchange candidates through the signalling channel.
    peer = signal.exchange(public)
    # 3. Simultaneous outbound packets open both NATs.
    for _ in range(5):
        socket.sendto(b"PUNCH", peer)
        if socket.recv(timeout=0.05):
            return ("direct", peer)
    # 4. Failed — go through TURN and pay in latency.
    return ("relay", turn.allocate(peer)) if turn else (None, None)"""),
        pitfalls=[
            "Relying on STUN alone: symmetric NAT and CGNAT break the direct path.",
            "Putting TURN in the lobby region instead of close to players.",
            "Not refreshing NAT state: the connection dies after 30–120 seconds of silence.",
            "Ignoring IPv6 and port 443 — the simplest ways through strict networks.",
        ],
        games=["Call of Duty", "Destiny 2", "Rocket League", "Nintendo Switch Online"],
    ),
    dict(
        id="netbrowser",
        title="Browsers and mobile networks: WebSocket, WebRTC and radio",
        tags=["WebSocket", "WebRTC", "mobile", "battery"],
        summary="Browsers have no raw UDP: what remains is WebSocket (TCP), WebRTC data channels (SCTP/DTLS) and WebTransport (HTTP/3). On a phone you also get radio states, network switches and an energy budget — the network becomes probabilistic rather than stable.",
        detail=[
            "WebSocket is TCP: fine for lobbies, turn-based games and chat, but head-of-line blocking and growing latency under loss are real. WebRTC data channels offer unreliable, unordered delivery — the closest thing to UDP in a browser; the price is signalling, ICE and complexity. WebTransport brings QUIC and HTTP/3 to the browser, but support and infrastructure are not yet uniform.",
            "A mobile network is not “slow Wi-Fi”. The radio moves between idle and connected states in tens to hundreds of milliseconds, and every packet can keep it awake. Short frequent sends drain the battery; batching, backoff and fewer pings help. Switching Wi-Fi ↔ LTE breaks the connection: you need fast reconnect and session resume.",
            "In practice: keep a small input channel, cap snapshot sizes, pause on `visibilitychange`, treat `navigator.connection` as a hint rather than truth, and survive 2–3 seconds of complete packet loss without kicking the player to the menu. For cloud streaming, the control channel and the video stream are separate: a lost frame must not delay input.",
        ],
        formula=("battery_cost ≈ E_radio · (tail_time · packet_rate),   "
                 "effective_latency = RTT/2 + radio_wakeup + jitter_buffer",
                 "The radio tail after a transmission can last seconds. Fewer, larger sends are often cheaper in energy than frequent tiny ones."),
        steps=[
            "Pick the channel: WebSocket for lobby/chat, WebRTC or WebTransport for real time.",
            "Make the protocol survive 2–3 s of loss: buffering, reconnect and session tokens.",
            "Batch input and state: 20–30 sends per second is usually enough.",
            "Listen to `visibilitychange` and `online/offline`; pause the game instead of dropping the session.",
            "Test on real LTE/3G and in a subway, not only on office Wi-Fi.",
        ],
        complexity=("O(1) per message", "O(buffers) inside the tab",
                    "A tab can be frozen by the browser: never keep critical state only in JS timers."),
        code=("python", """def browser_channel(needs_unreliable, has_webrtc, has_webtransport):
    # The server decides what to offer the client.
    if needs_unreliable and has_webtransport:
        return "webtransport"        # HTTP/3, QUIC streams and datagrams
    if needs_unreliable and has_webrtc:
        return "webrtc-datachannel"  # SCTP/DTLS, maxRetransmits=0
    return "websocket"               # TCP: simple, but HOL-blocking"""),
        pitfalls=[
            "Using WebSocket for real-time positions and blaming “lag”.",
            "Pinging every 100 ms on mobile — the battery dies before the match ends.",
            "Dropping the session when Wi-Fi switches to LTE and restarting the match.",
            "Relying on background-tab timers: browsers throttle them.",
        ],
        games=["Krunker", "Slither.io", "Agar.io", "Xbox Cloud Gaming"],
    ),
    dict(
        id="netrollback",
        title="Rollback netcode: resimulation for fighting games",
        tags=["rollback", "GGPO", "prediction", "determinism"],
        summary="Rollback does not wait for the opponent: the client applies a predicted input immediately and, when the real one arrives, rewinds a few frames and resimulates. It turns RTT into invisible latency, but demands a cheap simulation and full determinism.",
        detail=[
            "In a fighting game a frame is 16.7 ms and one frame of delay changes combos. Rollback keeps a ring buffer of states (usually 7–8 frames) and saves a snapshot every frame. If the opponent's input is missing, the last known one is reused; when the real one arrives, the state is restored from a snapshot and every frame is resimulated with the correct input.",
            "The cost is CPU: at 100 ms RTT and 60 fps the rollback reaches 6 frames, i.e. up to 6 resimulations per frame. The simulation must therefore be small and side-effect free: no randomness, no allocations inside the frame, no platform-dependent floating-point physics. Input is timestamped, the RNG is seeded, iteration order is deterministic.",
            "Secrets: input delay and rollback are combined (1–2 frames of delay remove part of the rewinds); sound and VFX run outside the simulation; state must be <b>memcpy-able</b>; desync checks hash the state every N frames. Spectators and replays store the input log, not the state — it replays deterministically.",
        ],
        formula=("R = clamp(ceil(RTT / frame_time) + input_delay, 0, R_max),   "
                 "cost ≈ R · sim_step,   state_size ≤ a few KB",
                 "R is the rollback depth in frames. A higher RTT and a smaller buffer mean more resimulations; R_max is usually 7–10 frames, beyond that raise input delay."),
        steps=[
            "Make the simulation a pure function: state + input → new state, with no platform floats.",
            "Save a state snapshot into a ring buffer on every frame.",
            "Apply predicted input and remember it; compare with the real one when it arrives.",
            "On mismatch, restore the snapshot and resimulate up to the current frame.",
            "Check desync with a state hash and keep input delay as a safety net on bad networks.",
        ],
        complexity=("O(R · sim_step) per frame", "O(R · state_size)",
                    "R ≤ 8 and state ≤ 4 KB is normal; eight 0.2 ms sim steps fit into a 16 ms frame."),
        code=("python", """class Rollback:
    def __init__(self, sim, state, r_max=8):
        self.sim, self.state = sim, state
        self.history = []                 # (frame, state, inputs)
        self.r_max = r_max

    def save(self, frame, inputs):
        self.history.append((frame, self.state.copy(), inputs))
        if len(self.history) > self.r_max:
            self.history.pop(0)

    def advance(self, frame, local, remote):
        self.save(frame, (local, remote))
        self.state = self.sim.step(self.state, local, remote)

    def on_remote_input(self, frame, real_input):
        for i, (f, st, (lo, ro)) in enumerate(self.history):
            if f == frame and ro != real_input:
                self.state = st.copy()    # rollback
                for f2, st2, (lo2, _) in self.history[i:]:
                    self.state = self.sim.step(self.state, lo2, real_input)
                self.history[i] = (f, st, (lo, real_input))
                return True
        return False"""),
        pitfalls=[
            "Storing state with pointers or allocations: snapshot and restore break.",
            "Floating point and a different iteration order cause desync after a few minutes.",
            "A buffer that is too small: at 120 ms RTT the rollback hits the cap and the game teleports.",
            "Playing sound and particles inside the simulation: after a rollback they duplicate.",
        ],
        games=["Street Fighter 6", "Guilty Gear Strive", "Skullgirls", "Rocket League"],
    ),
    dict(
        id="netdeterminism",
        title="Determinism and serialisation: fixed point, quantisation, bit packing",
        tags=["fixed-point", "quantisation", "bitpacking", "checksum"],
        summary="Determinism means the same input produces the same state on every machine. It is impossible with raw floats and requires fixed point, stable iteration order and seeded RNG. Serialisation is the other half: send state cheaply without losing meaning.",
        detail=[
            "Floats are great for graphics and terrible for simulation: different CPUs, compilers and operation orders give different results. Fixed point <b>Q16.16</b> or integer millimetres and thousandths of a degree are bit-identical. You also need a deterministic entity order, no hash-map iteration order, an explicit seeded RNG and no standard-library `rand()`.",
            "Quantisation cuts traffic: a position in a 4 km world at 1 cm precision needs 19 bits per axis, an angle 12 bits, health 10 bits. Deltas against the previous snapshot encode only changes; a bit stream packs flags and fields without alignment. Compression (zstd/LZ4) suits large snapshots but not small packets, where overhead eats the gain.",
            "Desync is caught with checksums: CRC32/xxHash of the state every N ticks, compared between server and client. On mismatch you need the input log and the ability to replay the match. Protocol versioning is mandatory: a field inserted in the middle breaks compatibility. And determinism has a price — sometimes sending the state is cheaper than chasing bit-exactness.",
        ],
        formula=("x_q = round(x · 2^Q),   error ≤ 2^(−Q−1),   "
                 "bits = ⌈log₂(range / step)⌉,   desync = (hash(server) ≠ hash(client))",
                 "Q is the number of fractional bits. A 1 cm position in a 4 km world needs 19 bits; preserving meaning matters more than bit-exact graphics."),
        steps=[
            "Move the simulation to integers/fixed point; remove platform floats and `rand()`.",
            "Fix the entity iteration order and conflict-resolution rules.",
            "Design the schema: mandatory fields, deltas, quantisation, bit flags.",
            "Hash the state and compare server/client every N ticks.",
            "Version the protocol and keep input logs to reproduce desync.",
        ],
        complexity=("O(1) per field, O(n) per snapshot", "O(state) + ring buffer",
                    "Quantisation cuts 50–80 % of traffic; CRC32 over 1 KB of state costs microseconds."),
        code=("python", """SCALE = 1 << 16                 # Q16.16

def to_fixed(x):
    return int(round(x * SCALE))

def mul(a, b):
    return (a * b) >> 16            # fixed point without floats

def quantize(value, lo, hi, bits):
    step = (hi - lo) / ((1 << bits) - 1)
    q = int(round((value - lo) / step))
    return max(0, min((1 << bits) - 1, q))

def pack_state(entity):
    # 19 bits per axis, 12 bits angle, 10 bits HP
    x = quantize(entity.x, -2048.0, 2048.0, 19)
    y = quantize(entity.y, -2048.0, 2048.0, 19)
    a = quantize(entity.angle % 360.0, 0.0, 360.0, 12)
    hp = quantize(entity.hp, 0, 1000, 10)
    return (x << 41) | (y << 22) | (a << 10) | hp"""),
        pitfalls=[
            "Assuming floats are identical across platforms and builds.",
            "Using hash maps with unpredictable iteration order inside the simulation.",
            "Quantising too coarsely: the character jitters and cannot fit through doors.",
            "Changing the packet format without a version — old clients break silently.",
        ],
        games=["StarCraft II", "Age of Empires IV", "Factorio", "Dota 2"],
    ),
]
