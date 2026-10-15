# §5–6 — Demo data extraction & player-perspective / fog-of-war reconstruction

Research slice C. Date of research: 2026-10-15. Target: local-first, API-powered CS2 demo-analysis & coaching system
(2000-Elo FACEIT player, ex-2400, experienced dev). Scope: **what a CS2 demo actually contains**, and **how far we can
reconstruct what a single player knew at a given tick**.

## Evidence grading used throughout

| Tag | Meaning |
| --- | --- |
| **Demonstrated** | Working, inspectable artefact (shipped code, product docs, published API) does this today. |
| **Experimental** | Code exists but is explicitly preview/beta or documented as unverified. |
| **Research-supported** | Peer-reviewed paper or first-party engine source establishes the mechanism. |
| **Plausible-untested** | Mechanism is documented but not confirmed by me against a real CS2 demo. **Verify locally.** |
| **Infeasible / not available** | No source path exists (or would require cheating-adjacent tooling). |

Verification note: no `.dem` file was available in this workspace, so every field-level claim below is grounded in
parser source/docs/engine schema rather than in my own parse output. Claims that need one real demo to settle are
flagged **VERIFY**.

---

# §5 — Field inventory: what is extractable from a CS2 demo

## 5.0 Parser landscape

| Parser | Language / output | What it is good for | Notes |
| --- | --- | --- | --- |
| **demoparser2** (`LaihoE/demoparser`) | Rust core; Python/JS/WASM bindings; pandas DataFrames | Largest documented *raw property* surface (player, weapon, usercmd, game-state props). Also `parse_voice`, `parse_chat_messages`, `parse_grenades`. | 733★, MIT, accessed 2026-10-15. Fields are queried by name; unknown names pass through as raw netprops. |
| **awpy** (`pnxenopoulos/awpy`) | Rust core (`pbdems2`) + Python/Polars | Highest-level analysis API: `rounds`, `kills`, `damages`, `shots`, `blinds`, `smokes`, `fires`, `item_events`, `snapshots`, `stats`, plus **`VisibilityChecker`** and **`map_control`** (raycast/vision/reachability, smoke-aware). | 618★, MIT, 2026-10-15. Requires Python ≥3.11 + Polars 2.x. |
| **CS2DemoKit** (`CS2OpenDev`) | .NET 10 | 270+ typed events, user-cmd **delta reconstruction**, subtick extraction, rules DSL, **`enemy_spotted` rising-edge** from baked collision geometry. | MIT, accessed 2026-10-15. Documents the two-clock trap (frame clock vs server tick). |
| **cs2parser** (`osztenkurden`) | TS/Node/browser, live GOTV + demo | **Smoke voxel seed decoding** (reverse-engineered transform). | Accessed 2026-10-15. |
| **demoinfocs-golang** (`markus-wa`) | Go | Reference semantics for game events incl. `PlayerSound`, `Footstep`, `IsSpottedBy`. | Used here as the semantic authority for ambiguous fields. |
| **cs2-tools / cs2-demo-viewer** (`skkwowee`) | Python + Next.js | Wall-clipped vision cones via raycasting; demo-replay radar. | Low star count, MIT; useful as an implementation reference, not a dependency. |

Practical conclusion: **demoparser2 (raw breadth + voice) + awpy (analysis + geometry/LOS) is the natural local
stack**; CS2DemoKit/cs2parser are the only public sources for *smoke voxels* and for *correct user-cmd/subsample
handling* — see §5.7 and §6.5.

**Data-source corollary (from the EcosystemSurvey slice, 2026-10-15):** no stats/API layer supplies positional or
tick data. FACEIT v4 round/player "stats" are schema-less string→string maps; Leetify is aggregate-only; Stratz is
Dota-only. **Positional/tick input must come from parsing the `.dem`** (or from a pre-parsed corpus — e.g. the
**CS2CD** dataset on Hugging Face: CC BY 4.0, 795 matches, tick CSVs + event JSON, produced from csstats.gg via
demoparser2). Fog-of-war work is therefore strictly downstream of the parser, and a reusable per-demo parse cache is
the load-bearing asset.

**No vendor shortcut to information state exists** (verified against Leetify's live OpenAPI 3.1.0 spec,
`api-public-docs.cs-prod.leetify.com/swagger.json`, 2026-10-15): the only awareness-adjacent fields anywhere in that
surface are `preaim` and `reaction_time_ms` — derived proxies of the *spotted → engage* transition — and they are
**strictly aggregate** (per match / per player), with no per-tick, per-encounter or directional component. Two further
consequences: (a) they cannot serve as a validation corpus for a per-tick belief stream; (b) Leetify's Developer
Guidelines §5 forbid renaming/rescaling their metrics and **§6 forbids storing API data at all**, so even those two
proxies must not be persisted in a local DB or recomputed on a different scale. **Everything in §6 must be computed
from your own parse cache** — budget validation effort accordingly (see §6.12 step 7).

## 5.1 Direct per-tick player state (networked — measured, not inferred)

Source: demoparser2's "Player data" table (`README.md`, github.com/LaihoE/demoparser) and awpy
`SNAPSHOT_PROPERTIES` (`crates/awpy-python/python/awpy/schema.py`, 2026-10-15).

| Group | Fields (verified names) | Backing netprop | Fidelity now |
| --- | --- | --- | --- |
| Identity | `player_steamid`, `player_name`, `user_id`, `entity_id`, `player_color`, `team_num`, `is_connected`, `ping`, `is_controlling_bot` | `m_steamID`, `m_iszPlayerName`, `m_iTeamNum`, … | Direct. `entity_id`+`entity_serial` is the stable identity (Source 2 **reuses slots**). |
| Position | `X`, `Y`, `Z`, `last_place_name` | `CBodyComponent.m_cell* + m_vec*` (computed) | Direct, world-space, Hammer units, Z-up. Sampled at demo tick rate (see §5.8). |
| Velocity | `velocity_X/Y/Z`, `velocity`, `fall_velo`, `max_speed`, `is_airborne`, `ground_accel_linear_frac_last_time` | `m_vecVelocity`, `m_flFallVelocity`, `m_hGroundEntity` | Direct (network-quantized). |
| Aim | `pitch`, `yaw`, `aim_punch_angle`, `aim_punch_angle_vel`, `is_scoped`, `resume_zoom`, `fov` | `m_angEyeAngles[0/1]`, `CCSPlayerPawn.m_aimPunchAngle` | Direct **per tick only**. True sub-tick motion is in `usercmd_*` (§5.7). |
| Health/armor | `health`, `armor_value`, `has_helmet`, `has_defuser`, `life_state`, `is_alive` | `m_iHealth`, `m_ArmorValue`, `m_bPawnHasHelmet/Defuser`, `m_lifeState` | Direct. |
| Movement posture | `ducked`, `ducking`, `duck_amount`, `duck_speed`, `in_crouch`, `is_walking`, `is_strafing`, `stamina`, `move_type`, `move_collide` | movement services | Direct — needed for eye-height and hitbox modeling. |
| Economy | `balance`, `start_balance`, `total_cash_spent`, `cash_spent_this_round`, `round_start_equip_value`, `current_equip_value`, `weapon_purchases_this_round/match`, `equipment_value_total`, `money_saved_total` | money/equip services | Direct. |
| Weapon (held) | `active_weapon`, `active_weapon_name`, `active_weapon_ammo`, `active_weapon_skin`, `total_ammo_left`, `is_in_reload`, `is_silencer_on`, `zoom_lvl`, `weapon_mode`, `accuracy_penalty`, `i_recoil_idx`, `fire_seq_start_time`, `last_shot_time` | weapon entity props | Direct. `accuracy_penalty` = `m_fAccuracyPenalty` → the engine's own inaccuracy state. |
| Inventory | `inventory`, `inventory_as_ids`, per-grenade counts (awpy: `smoke_grenades`, `flashbangs`, `he_grenades`, `fire_grenades`, `decoy_grenades`, `has_bomb`, `primary_weapon`, `secondary_weapon`) | `m_hMyWeapons` walk | Direct. |
| Visibility/awareness | `spotted`, `approximate_spotted_by`, `time_last_injury`, `direction_last_injury` | `m_bSpotted`, `m_bSpottedByMask`, `m_flTimeOfLastInjury` | **Direct but semantically hazardous** — see §5.6. |
| Objective/zone | `in_bomb_zone`, `which_bomb_zone`, `in_buy_zone`, `in_no_defuse_area`, `is_defusing`, `is_grabbing_hostage`, `blocking_use_in_progess` | various | Direct. |
| Flash state | `flash_duration`, `flash_max_alpha`, (awpy) `is_blinded` | `m_flFlashDuration`, `m_flFlashMaxAlpha`, `m_bFlashing` | Direct field; **semantics conflict** — awpy calls it "replicated onset duration … not a remaining-time counter", yet Source CS:GO famously decays `m_flFlashDuration`. **VERIFY** against one demo before using it as "seconds of blindness remaining" (awpy's `blinds` dataset instead reconstructs duration from the `flashbang_detonate` event). |
| Buttons (per-tick) | `FORWARD, LEFT, RIGHT, BACK, FIRE, RIGHTCLICK, RELOAD, INSPECT, USE, ZOOM, SCOREBOARD, WALK, buttons` | `m_nButtonDownMaskPrev` (bitmask; others derived) | Direct. This is the *engine's* view of held buttons, at tick granularity. |
| Skins/cosmetics | `weapon_paint_kit`, `weapon_float`, `agent_skin`, glove/knife paints, `music_kit_id`, honors | item raw values | Direct; irrelevant to coaching except identifyability. |
| Aggregate stats (1/round) | `kills_total`, `deaths_total`, `assists_total`, `damage_total`, `utility_damage_total`, `enemies_flashed_total`, `equipment_value_total`, `money_saved_total`, `cash_earned_total`, … | `m_iKills` etc. | Direct; monthly/round-granular. |

**Game-world state** (demoparser2 "Game State" table) is also fully extractable per tick: `is_freeze_period`,
`is_warmup_period`, `game_phase`, `total_rounds_played`, `round_start_time`, `round_in_progress`,
`is_bomb_planted`, `is_bomb_dropped`, `round_win_status`, `round_win_reason`, `terrorist_cant_buy`, `ct_cant_buy`,
`ct_losing_streak`, `t_losing_streak`, `num_terrorist_timeouts`, `is_valve_dedicated_server`, `spectator_slot_count`,
`hostages_remaining`, `is_matchmaking`, `match_making_mode`, etc. **Note:** this is `CCSGameRules`, so `m_iScore` is
the *side's* score and `round_win_reason` is the raw enum — awpy already maps these (`rounds.reason_name`,
`rounds.winner_side`, `rounds.is_knife_round`).

**Team-level economy** is *not* a raw field on the same table but is derived: awpy `round_economy` gives
`equipment_value` at freeze end per (round, side) with `buy_type ∈ {pistol, eco, force, full}`.

## 5.2 Events (direct, tick-stamped)

CS2 event definitions live in `game/csgo/pak01_dir/resource/mod.gameevents`
(`SteamTracking/GameTracking-CS2`). Extracted on 2026-10-15: **141 event names**. CS2DemoKit states its parser
understands **270+ typed events**, so `mod.gameevents` is the client-side subset — treat 141 as a floor, and read
`list_game_events()` / `demo.events.names` per demo for the truth.

Event families that matter for coaching, with **field-level schemas verified from `mod.gameevents`**:

| Event | Fields (verified) | Value for this project |
| --- | --- | --- |
| `player_death` | `userid, attacker, assister, assistedflash, weapon, headshot, dominated, revenge, wipe, penetrated, noscope, thrusmoke, attackerblind, distance, dmg_health, dmg_armor, hitgroup, attackerinair` | Ground truth for engagements. `thrusmoke`, `attackerblind`, `penetrated`, `attackerinair`, `noscope` are **engine-confirmed context** for decision quality (e.g. a smoke kill proves the shooter had information through smoke). |
| `player_hurt` | `userid, attacker, health, armor, weapon, dmg_health, dmg_armor, hitgroup` | Damage/armor pre-post (awpy `damages` resolves participants+positions; it warns `health_pre` is *estimated*, `post + damage` capped at 100). |
| `bullet_damage` | `victim, attacker, distance, damage_dir_x/y/z` | Direction vector of the bullet → shot-origin reasoning; **not always present** (demoinfocs warns some GOTV/broadcast demos omit ballistic data). |
| `bullet_impact` | `userid, x, y, z` | Exact impact point (wall or body) → spray/aim analysis and *audible* impact location. |
| `weapon_fire` | `userid, weapon, silenced` | Shot timing; pairs with `weapon_fire_on_empty`. Not 1:1 with impacts (shotgun pellets, bursts). |
| `player_blind` | `userid, attacker, entityid, blind_duration` | Flash effect with duration and thrower. |
| `flashbang_detonate` / `hegrenade_detonate` / `decoy_detonate` / `molotov_detonate` / `inferno_startburn` / `inferno_expire` / `smokegrenade_detonate` / `smokegrenade_expired` | position fields (`x,y,z`) + `entityid`; `userid` = thrower | Utility timeline with positions and (for smoke/fire) start **and** end. |
| `grenade_bounce` | position | Trajectory detail; audibility events. |
| `player_footstep`, `player_jump` | `userid` (+ jump has position via player state) | **Audibility events** — see §5.6/§6.6. |
| `player_sound` | `userid, radius (int), duration (float), step (bool)` | **The engine's own sound-emission event with an audible radius.** Highest-value, least-known field for fog-of-war. **Extraction caveats (peer-verified, EcosystemSurvey.ParsersLibs, 2026-10-15):** demoinfocs exposes only `PlayerSound{Player, Radius, Duration}` and reads just `userid`/`radius`/`duration` — **`step` is dropped by the Go API**, so step-vs-non-step must come from the raw event keys. awpy 3.x does not list `player_sound` in `GAME_EVENTS` and has no Rust source hit (only a 2.x-era CLI issue #396), so `demo.events.player_sound` is an **[INFERENCE]** about the generic event API, not documented behaviour; demoparser2 can name the event (string present in its binaries) but documents **no field accessor** for it. |
| `door_moving` | `userid` | Noise + geometry change (de_mirage/cache doors). |
| `weapon_reload`, `weapon_zoom`, `weapon_zoom_rifle`, `item_equip`, `item_pickup`, `item_purchase`, `item_remove`, `ammo_pickup` | `userid`, item fields | Action timeline; `item_equip`/`weapon_zoom` are largely silent → distinguish "visible action" from "private action". |
| `bomb_*` (`pickup, dropped, beginplant, abortplant, planted, begindefuse, abortdefuse, defused, exploded, beep`) | actor + site | Objective timeline. awpy `bomb` dataset normalises to 6 actions with positions. |
| `round_start`, `round_freeze_end`, `round_end`, `round_officially_ended`, `announce_phase_end`, `begin_new_match`, `cs_win_panel_*` | — | Round phase boundaries. awpy reconstructs `rounds` from `CCSGameRules` **even when round events are missing**. |
| `player_spawned`, `player_given_c4`, `player_ping`, `player_ping_stop`, `round_end_upload_stats` | — | demoinfocs annotates these as **"only present in locally recorded (POV) demos"** — i.e. their presence is itself an information-state signal. Pings are the *explicit* "I am telling my team something" marker. |
| `player_radio` | — | In-game radio commands. |
| `player_team`, `player_connect_full`, `player_disconnect`, `teamchange_pending`, `switch_team` | — | Roster churn. |

## 5.3 Projectiles, smokes, fires

* **Grenade trajectories** — demoparser2 `parse_grenades()` returns `X, Y, Z, tick, thrower_steamid, grenade_type,
  entity_id` **per tick in flight**; awpy `grenades` is the same shape with `entity_serial` and a normalised type
  enum. Documented limitation: **NA values occur on some throws** (demoparser issue #232, Nov 2024; closed as fixed
  in 0.36.0, Feb 2025 — but the class of bug shows projectile entity state can be missing).
* **Smokes** — awpy `smokes` gives one row per cloud: `start_tick/end_tick, thrower_*, entity_id, x, y, z`, with the
  window taken from `smokegrenade_detonate → smokegrenade_expired` (i.e. the *deployed cloud*, excluding flight),
  cut short when a molotov smokes it out.
* **Smoke *volume*, not just centre** — engine-side, `CSmokeGrenadeProjectile` (CS2 build 25218825, 2026-09-09)
  carries `m_vSmokeDetonationPos`, `m_nSmokeEffectTickBegin`, `m_bDidSmokeEffect`, `m_VoxelFrameData`,
  `m_nVoxelFrameDataSize`, `m_nVoxelUpdate`, `m_nRandomSeed` (CS2OpenDev schema docs). The client header confirms the
  networked types: `C_NetworkUtlVectorBase<uint8> m_VoxelFrameData; int32 m_nVoxelFrameDataSize; int32 m_nVoxelUpdate;`
  (`SteamTracking/GameTracking-CS2`, `DumpSource2/schemas/client/C_SmokeGrenadeProjectile.h` lines 8-10; server mirror
  `server/CSmokeGrenadeProjectile.h` identical — verified 2026-10-15 by EcosystemSurvey.ParsersLibs).
  `cs2parser` implements the decode: the demo networks a **voxel seed** on a `[0,32)³` grid with the verified
  transform `world = (grid − 16) · 20 + detonationPos`, per-axis signs `[−1,+1,+1]` (commit `f3e672a`, 2026; README
  section "Smokes"). **This means exact smoke occupancy is extractable from the demo** — no simulation needed.
  **Coverage check (peer-verified, 2026-10-15):** awpy has **zero `Voxel` hits** anywhere in Rust/Python/docs, and the
  field is **not in demoparser2's prop maps** (the string exists only inside its compiled wasm/node binaries and a
  bundled demo's string table). The convenient raw-dump route is **closed, not merely unverified**: in `pbdems2 0.4.0`
  (the crate awpy 3.0.0 pins), `CNetworkUtlVectorBase<T>` decodes as `FieldSpecialDescriptor::DynamicArray`, and the
  update loop stores the **element count** at the parent key with elements under **child field-path keys**
  (`src/entity/field_decoder.rs:543-556, 765-805`; `src/entity/entities.rs:314-330`) — the same mechanism that makes
  demoinfocs expose `m_bSpottedByMask.0000/.0001` as separate props. A 32³ grid would need ~32k indexed child paths,
  and `FieldValue` has no array variant beyond `String(Vec<u8>)`/`FloatVector`/`Vector2..4`/`QAngle`, so it would not
  land in a typed Polars column anyway. → **Port cs2parser's voxel decode, or keep the sphere fallback.** Status:
  **Experimental/Demonstrated in one JS parser; VERIFY** on FACEIT demos and note that the seed is what the client
  *grows* the visible cloud from.
* **Fires** — awpy `fires` (`inferno_startburn → inferno_expire`, ~7 s, plus `type`). CS2DemoKit notes it can emit
  **synthesised** entity-derived events that never appeared on the wire (payload null) — a reminder that "event
  present" ≠ "event on the wire".
* **Holes punched in smoke** — 5Stack documents that HE grenades and bomb explosions "punch holes" in the smoke cloud
  and that their replay rebuilds smoke "from CS2's own smoke simulation" (5Stack Match Replay docs, accessed
  2026-10-15). **Experimental** for us: the voxel seed + hole events is the path; nothing in awpy does it.

## 5.4 Shots, damage, accuracy

* `demo.shots` (awpy): one row per `weapon_fire` with `tick, entity_id, steamid, side, x, y, z, pitch, yaw, weapon,
  scoped, inaccuracy (networked accuracy penalty), num_bullets_remaining`.
* `demo.damages` (awpy): participants resolved with positions + `health/armor_pre/post` (**pre is an estimate**, capped
  at 100; awpy explicitly warns not to use `health_pre` to cap successive hits).
* Hitgroups: `hitgroup` byte + `hitgroup_name` on both kills and damages.
* **Accuracy states**: the engine's own `m_fAccuracyPenalty` (`accuracy_penalty`) plus per-weapon
  `i_recoil_idx/fl_recoil_idx`, `is_in_reload`, `is_silenced`/`is_silencer_on`, `zoom_lvl`, ammo. Recovery curves are
  **not** in the demo — `m_fAccuracyPenalty` is sampled, so *reconstructing* the exact inaccuracy at an arbitrary
  sub-tick instant is an interpolation (**Plausible-untested**).

## 5.5 Round / phase structure and multipart demos

awpy `rounds` reconstructs `round_num, start_tick, freeze_end_tick, end_tick, official_end_tick, winner,
winner_side, reason, reason_name, is_knife_round` **from game state, without needing round events**; `demo.rounds`
also handles overtime. Multipart (long GOTV splits) is supported but joins must be on `(part, tick)`, never tick
alone, and splits inside a live round are rejected.

## 5.6 Visibility / spotting state — the one *direct* awareness channel, and its traps

* CS2 exposes `EntitySpottedState_t { bool m_bSpotted; uint32 m_bSpottedByMask[2]; }` (64 player-slot bits) on
  `C_CSPlayerPawn` as `m_entitySpottedState` — confirmed in the CS2 client schema dump
  (`SteamTracking/GameTracking-CS2`, `DumpSource2/schemas/client/EntitySpottedState_t.h`; cross-checked 2026-10-15 by
  the EcosystemSurvey slice). demoparser2 exposes them as `spotted` and `approximate_spotted_by`.
* The **"approximate" prefix has a concrete mechanism**: demoparser2's mask↔player resolution
  (`find_spotted`/`steamids_from_mask`) maps only mask bits 0..15 to controller ids 1..16. Even the per-player
  attribution is a partial mapping of the 64-bit space, not a full one (EcosystemSurvey.ParsersLibs, 2026-10-15).
  **Worse for any correlation test: that accessor cannot produce a trustworthy negative.** `find_spotted` accepts the
  parent prop only as a single `Variant::U32` (`src/parser/src/second_pass/collect_data.rs:790-797`), then
  `steamids_from_mask` loops `for i in 0..16`, maps bit `i` → controller entity id `i+1` and resolves it with a
  **linear** scan (`game_events.rs:244-251`). Three consequences: (1) word 1 (`…0001`, slots 32–63) and bits 16–31 of
  word 0 are **never read**; (2) a set bit whose controller cannot be resolved is **dropped silently** — numerically
  indistinguishable from "nobody spotted"; (3) a resolvable controller with no steamid yields a literal `0` in the
  list. So a weak or absent agreement between this column and geometry may be the **accessor**, not the game state —
  always read the bit-level truth through the awpy dotted path in the same run (§5.6 recipe above).
* **GOTV caveat (inference, unverified):** in a GOTV demo the spotted mask most plausibly reflects the
  spectator/GOTV client's spotting rather than each player's own — so in the demos FACEIT hands you, the field may
  not be per-player ground truth at all (EcosystemSurvey.ParsersLibs). This reinforces the "corroborator only" verdict.
* **Extraction recipe (avoids a failed first test — peer-verified against `pbdems2 0.4.0` + awpy source, 2026-10-15).**
  If you read the mask through awpy, a bare `m_bSpottedByMask` **will not resolve**: `ticks(props)` maps each name
  straight to `Serializer::resolve_field_key` with no alias layer (`awpy-python/src/lib.rs:2712-2718`) and resolution
  only recurses into a sub-serializer **after a parent-prefix match** (`pbdems2 0.4.0 src/entity/serializers.rs:229-300`).
  The full nested path is required: **`m_entitySpottedState.m_bSpottedByMask.0000`** and **`…0001`**, plus
  `m_entitySpottedState.m_bSpotted` for the bool. Nested dotted names are normal in awpy (it uses
  `CBodyComponent.m_skeletonInstance.m_vecOrigin` itself) and the depth limit of 7 is not a constraint; each mask word
  is a scalar `u32`, so it lands in an ordinary Int column. Caveat: the `[2]` fixed-array index naming is
  **[INFERENCE]** until one demo run confirms it — probe with `players_only=False` + a class filter. Through
  demoparser2 the same datum is simply `approximate_spotted_by` (one call, the 16-bit mapping).
* demoinfocs' `IsSpottedBy()` carries the blunt warning: **"This is NOT 'Line of Sight' / FOV"** and "may not behave
  as expected with multiple spotters" (`pkg/demoinfocs/common/player.go`).
* Leetify (vendor engineering blog, **2020-10-04**) documented the failure modes after abandoning this signal:
  radar updates lag **0–500 ms**; spotting requires *specific* parts of the model at *specific* angles, so shoots at
  feet-under-obstacles / arms-around-corners do not register; the radar keeps a **"shadow"** of an enemy after
  visibility is lost; and AWPers often fire before the event ever triggers (they measured 421 ms and 82 ms delays in
  two examples). They replaced it with full position tracking + their own visibility computation.
* Radar UI behaviour: enemies appear on the team radar when **at least one teammate** spots them; when direct
  visibility is lost the icon becomes a **last-known "?" that does not track movement** and fades after roughly
  **3–5 s** (community/guide-level sources; **Plausible-untested**, no Valve documentation). `radarvisdistance`
  (default 1000, community-documented) is a radar-visibility threshold, *not* a proven universal spotting trace
  distance.

**No public validation prior art found.** Nothing in the literature or tooling landscape appears to validate
`m_bSpottedByMask` against geometrically computed visibility; awpy's visibility tests are synthetic/self-consistent
only, and Leetify's public account is the closest thing to an audit — and it is an account of *rejecting* the signal.
(Checked: awpy repo/docs, demoinfocs source, CS2DemoKit, 5Stack, Leetify, X-Ego, EWM; the EcosystemSurvey slice
independently reached the same "no ground-truth LOS validation anywhere" conclusion, 2026-10-15.)

**Verdict:** `spotted`/`spotting mask` is the *only* direct, demo-native awareness signal, and it is **good as a
noisy corroborator and as a "team already knows" hint, and bad as ground truth**. Use it as (a) a sanity check on a
geometric visibility engine, and (b) a feature, never as the label — and even for (a), read the **bit-level** truth
(awpy dotted path), because the convenient demoparser2 accessor cannot produce a trustworthy negative.

## 5.7 Input fidelity: ticks, subtick, user commands, buttons

* **Tick rate**: CS2 server simulation is **64 Hz**, including current FACEIT matches; Valve's Source2 telemetry docs
  describe 64 snapshots/s. "Subtick" is not 128 tick — it means user commands carry a fractional timestamp `when`
  inside a 64 Hz command interval. awpy derives `tick_rate` from demo playback and falls back to 64.
* **User commands** are in the demo (`svc_UserCmds`): CS2DemoKit measured `svc_UserCmds` as **~90% of net messages**
  (1.15 M on a 290 MB file) and reports that **since ~July 2026 (build 10896) 99.8–99.9% of commands are
  `delta_data` patches**, so a parser that reads only full `data` payloads sees a fraction of a percent of input.
  Delta reconstruction (baseline from `DEM_FullPacket`, then sequential apply) is required.
* demoparser2 exposes per-command fields as props: `usercmd_viewangle_x/y/z`, `usercmd_buttonstate_1..3`,
  `usercmd_forward_move`, `usercmd_left_move`, `usercmd_mouse_dx/dy`, `usercmd_impulse`, `usercmd_weapon_select`,
  `usercmd_input_history`, **`usercmd_subtick_moves`**, `usercmd_consumed_server_angle_changes`.
* `CSubtickMoveStep { button, pressed, when, analog_forward_delta, analog_left_delta, pitch_delta, yaw_delta }`
  (`SteamTracking/GameTracking-CS2`, `Protobufs/usercmd.proto`).
* **Buttons** as tick-level booleans (`FORWARD…WALK`, plus raw `buttons` bitmask) come from `m_nButtonDownMaskPrev`.

**Practical consequence:** for reaction-time / aim-timing claims you want `usercmd` (sub-tick, includes raw mouse
deltas); for "what was the player doing" the tick-level snapshots suffice. Two clocks exist (frame clock vs server
tick) and CS2DemoKit documents a hard warning about mixing them; awpy's `part`+`tick` model is the other convention.
Pick **one** convention and normalize on ingest.

## 5.8 Voice, chat, pings

| Channel | Extractability | Evidence |
| --- | --- | --- |
| **Voice (Opus)** | `demoparser2.parse_voice()` → per-packet `{tick, steamid, bytes}`; decode as **48 kHz mono Opus** with a per-speaker decoder state. Node: `parseVoice`; awpy example `voice_to_wav`. | demoparser docs + `DandrewsDev/CS2VoiceData` README. |
| Voice availability | **"Valve Matchmaking demos do not contain voice audio data"** (CS2VoiceData README, explicit). Community tooling claims FACEIT leaves *two* demo files, one of which carries **both teams'** voice, and that third-party voice extraction is the supported path. | CS2VoiceData README (**Demonstrated** for the negative MM case); zeroutil tool pages (**Secondary/Plausible-untested** for the FACEIT detail — VERIFY with your own FACEIT demo). |
| Text chat | awpy `demo.chat` → `tick, entity_index, name, message, channel` from `SayText`/`SayText2`/`SayTextChannel`. demoparser2 `parse_chat_messages()`. | awpy datasets docs (**Demonstrated**). |
| Pings | `player_ping` / `player_ping_stop` events — demoinfocs: **POV demos only**. | demoinfocs `game_events.go` (**Demonstrated** for POV-only). |

## 5.9 Direct vs inferred — the split that matters for coaching

| Signal | Direct (measured) | Inferred (modeled) | Notes |
| --- | --- | --- | --- |
| Position, velocity, angles, HP, armor, money, inventory | ✅ | | per tick, quantized |
| Frustum/FOV visibility of a given enemy sample point | | ✅ | raycasts vs geometry (§6.3) |
| Smoke occlusion | seed voxels ✅ (special parser) / sphere ❌ | ✅ | awpy approximates a sphere, see §6.5 |
| Flash blindness affecting vision | ✅ (`is_blinded`, `blind_duration`) | ✅ (what the player could actually resolve) | model = "no information from vision while blinded", but partial flashes are graded |
| Movement/utility sounds being *audible* | ✅ `player_sound.radius`, `player_footstep`, `grenade_bounce`, `bullet_impact` positions | ✅ (propagation/occlusion) | weapon-fire audibility is not a networked field → weapon table lookup or calibration |
| Enemy *awareness* (`spotted` mask) | ✅ (rubber-duck semantics) | | noisy, laggy, not LOS — §5.6 |
| Team comms content | ✅ if demo carries voice | ✅ (topic/timing from pings/chat) | MM demos: none. FACEIT: **VERIFY** |
| "Player *noticed* the enemy" | | ✅ (gaze/time-on-screen model, §6.9) | never directly recorded |
| "Player should have known X" | | ✅ | the coaching layer's core inference, and the hindsight-bias trap (§6.11) |

## 5.10 Known data-quality limits (checklist)

1. **Dead players keep last `equipment_value`** (awpy) — do not read economy off dead rows.
2. **`entity_id` alone is not identity** — join on `(entity_id, entity_serial)`, and on `(part, tick)` for multipart.
3. **Events may be absent** even when defined: awpy `blinds` is empty without `flashbang_detonate`; `bullet_damage`
   may be missing in GOTV/broadcast demos; awpy `chat` empty does not mean no chat (different stream).
4. **Synthetic vs wire events** (CS2DemoKit): entity-derived fires can be synthesised with null payload.
5. **`health_pre` is estimated**, `rounds.official_end_tick` may be null, `stats` treats every player as having played
   every round (approximate for joins/leaves).
6. **Warmup/timeout rows are excluded** by default, and raw events retain warmup/restart events — filter explicitly.
7. **Build drift**: demos newer than the parser produce `Degraded` health and dropped messages (CS2DemoKit's
   `Health` enum exists precisely for this). Pin parser + map-asset versions by CS2 `ClientVersion`.
8. **Field-availability drift**: e.g. `m_bStealthy` is absent in older demos → `is_silent_reloading` is null.
9. `flash_duration` semantics conflict (§5.1) — **VERIFY**.
10. Banked data claims (utility/damage) come from `player_hurt`/`weapon_fire` events: `bullet_impact` ≠ damage.

---

# §6 — Player-perspective / fog-of-war reconstruction

## 6.0 The core asymmetry

A GOTV/server demo is **omniscient**: it is the server's state machine. Nothing in it records what player *i*
rendered. Therefore:

* **World state** — directly available.
* **Visual state** (what was geometrically visible, given eye position, gaze, smoke, flash, doors) — **must be
  recomputed**. Every serious tool in this space does exactly this (Leetify 2020; awpy `map_control`; CS2DemoKit
  `enemy_spotted`; 5Stack VISION; cs2-demo-viewer vision cones).
* **Knowledge state** (what the player could plausibly know, incl. sound and teammate comms) — recomputed + modeled.
* Valve's own acknowledgement that playback ≠ experience is **TrueView** (patch 2025-11-05): it re-runs client-side
  prediction so demos "match the player's original experience much more closely", explicitly because previously
  "demo playback showed the server's view of the world, without accounting for network latency"; Valve still warns
  "there may still be some differences between what you see in the demo and what the player originally saw" and that
  TrueView **auto-disables when the demo's game version ≠ the viewing version**. → any pixel-level claim is off the
  table; any geometry-level claim is legitimate with stated tolerance.

So define visibility as a deterministic predicate over reconstructible inputs:

```
Visible(i → j, t) =
      LOS(eye_i(t), sample_k(j,t), geometry)          # walls
   ∧ ¬SmokeBlocks(eye_i(t), sample_k(j,t), t)         # smoke occupation at t
   ∧ (∃k: inside_fov(gaze_i(t), eye_i(t), sample_k(j,t)))   # FOV/aim
   ∧ ¬FullyBlind_i(t)                                  # flash
   ∧ doors_open_at(t)                                  # de_mirage/cache etc.
   ∧ own_team_filter(i, j)
```

## 6.1 Geometry sources (occlusion ground truth)

| Asset | What it is | Where it comes from | Status |
| --- | --- | --- | --- |
| **Collision mesh** (`.mesh`) | decimated, occluder-filtered, welded triangle soup derived from the map's `world_physics` glTF | `awpy-data`: steamcmd install of CS2 → extract from **VPK** (`pak01_dir.vpk`, `maps/<map>.vpk`) via **Source2Viewer-CLI**; published as GitHub Releases **pinned to `ClientVersion`**; consumed as `VisibilityChecker(map)` | **Demonstrated** (awpy), MIT scripts, assets Valve-derived. |
| **Nav mesh** (`.nav`) | walkable areas + connectivity (CS2 ships format version 36) | same pipeline (`navs.zip`) | **Demonstrated** (awpy `NavMesh`: `find_area`, `neighbors`, `find_path` with `distance`/`hops`/`size` weights). |
| **Radar image + coordinate transform** | `radars/<map>.png` (+ `_lower` for Nuke/Vertigo/Train) and `map_data.json` (`pos_x, pos_y, scale, rotate, zoom`) | same pipeline | **Demonstrated**. |
| **BVH over collision** | spatial index for ray queries | built at `VisibilityChecker` construction (awpy); CS2FOW bakes a **BVH8** file; CS2DemoKit builds a BVH over `<map>.tris` and ships the *convention* only (`CS2DEMOKIT_COLLISION_DIR`), because the geometry is Valve-derived and large | **Demonstrated**. |

Implementation guidance: **build the BVH once per map, cache next to the demo corpus, key it by `ClientVersion`**
(map geometry changes across updates; CS2FOW even CRC-checks the bake and refuses stale ones).

## 6.2 Fog-of-war technique survey

| Implementation | Approach | Blockers modeled | Reported limits | Verdict |
| --- | --- | --- | --- | --- |
| **awpy `VisibilityChecker.is_visible`** | segment vs collision BVH | static geometry only | Docs are explicit: **no smokes, moving doors, bullet penetration, player models, dynamic entities, FOV, crouch/stand eye height**; player positions ≠ eye positions (add eye height) | **Demonstrated**, low-level primitive |
| **awpy `map_control`** (`method="raycast"|"vision"|"reachability"`) | nav areas labeled ct/t/contested/neutral; LOS raycasts from player eye to nav-area points | **smokes block LOS**; **blinded players project no vision** (`flash_threshold`); fires block *reachability*; dead players excluded | vision uses yaw only (**ignores pitch**), no per-player noticing, "estimate control, not exact player perception"; vision ignores entities/doors | **Demonstrated** — the closest ready-made building block |
| awpy defaults | `eye_height 64`, `crouch_eye_height 46`, `target_height 46`, `fov 90`, `smoke_radius 144`, `smoke_height 60`, `fire_radius 150`, `flash_threshold 1.0`, `contest_margin 200` | | sphere smoke is an approximation; no doors | **Demonstrated** (tunable) |
| **CS2DemoKit `enemy_spotted`** | rules-DSL event on **rising edge** of "one player first comes into view of another", recomputed from baked collision `.tris` | static geometry; explicit "nothing on the wire says so" | engine absent → event silently never fires; geometry ships out of band | **Demonstrated** (MIT, .NET) |
| **Leetify visibility engine** | position tracking + own check: shooting-at-enemy, seen-recently, crosshair-vs-enemy delta, "**can the attacker see any part of the enemy's body or gun**" | geometry + model parts | rebuilt in 2020 specifically because radar events were wrong; public output is **aggregate only** (`preaim`, `reaction_time_ms`) and their Developer Guidelines **§6 forbids storing API data**, so it is evidence of feasibility, not an input or benchmark corpus | **Demonstrated** (production, closed source) — the product-level precedent |
| **5Stack VISION layer** | "Fog of war: dims what a side can't see and draws who can see whom, for CT, T or BOTH"; smokes rebuilt **from CS2's own smoke simulation** (fills rooms, pours off ledges, merges; HE/bomb punch holes); flashes glow for **real blind durations**; hit locations from demos | geometry + smoke volume + flash | needs current-parser reparses; older matches approximate smokes/flashes | **Demonstrated** (commercial) — best evidence that full fog-of-war at product quality is achievable |
| **cs2-demo-viewer / cs2-tools** | "wall-clipped vision cones via raycasting" on a radar canvas; kill/damage lines, shot tracers | geometry | low maturity (1★), data exported from awpy + screenshot harness driving CS2 via netcon | **Experimental** |
| **CS2FOW** | *server-side* anti-wallhack: withholds enemy entity groups from `CheckTransmit` using BVH8-raycasts from **body points, bounding-box corners and the held weapon muzzle**; movement prediction above 75 u/s (fully at 100 u/s) looking ahead **75 ms + 1.5 × recipient RTT, capped 375 ms / 96 units**; shoulder origins grow 24→128 u with RTT; 16 ms hold to kill corner flicker; **fails open** | baked static map geometry only — **"smokes, doors, breakables and moving props are not visibility blockers in the current preview"** | requires Metamod community server; not for Premier/MM | **Experimental** — but the single best public evidence for *how the engine-adjacent approximation is engineered* (multi-sample rays + latency-aware margin) |
| **cs2parser** | decodes networked **smoke voxel seed** | — | transform verified against client | **Experimental** |
| **Source-engine PVS / `CheckTransmit`** | cluster-based network culling | — | PVS is coarse; enemies behind walls are still transmitted (that is *why* wallhacks exist) → **PVS is not a fog-of-war proxy** | Not usable as ground truth |
| **Client-recorded POV demos** | the *client's* received stream → the closest thing to a demo-native information-state artefact | implicitly, whatever the client got | reported by the EcosystemSurvey slice (2026-10-15, not independently verified here): demoinfocs yields a nil grenade `Projectile` outside the player's PVS and cannot re-link a POV molotov/inferno (its issues #714/#728). Still PVS-coarse: "not present" ≠ "not perceived", and "present" ≠ "rendered" | **Experimental** — useful as a *validation* channel (POV ≈ narrow info state), not as a fog-of-war engine; also the only demo type that carries `player_ping`/`player_given_c4`/`player_spawned` |
| **X-Ego / X-Ego-CS** (arXiv 2510.19150, 2025-10-22) | 124 h, 45 pro matches, synchronized **first-person video from all players** + state-action trajectories; Cross-Ego Contrastive Learning; task = predict teammate/opponent locations from a single POV | privileged multi-POV supervision | video, not geometry | **Research-supported** — proves the *learning* framing works when you have POV video; we do not need it to build geometry-based fog-of-war, but it validates information-asymmetry metrics |
| **EgoCS-400K** (arXiv 2606.18180, 2026-06-16) | 400 k first-person videos, ~10 k h, 1000+ matches, 13 maps, 10 POVs/round, replay-rendered from demos with state/action/event alignment | — | rendering pipeline needed | **Research-supported** — the "render POV from demo" path (needs the game client) |
| **EWM** (arXiv 2610.16166, 2026-10-12) | multi-game dataset (SC2, Dota 2, CS2) explicitly about "private fog of war, shared team vision and first-person viewpoints"; for SC2 keeps **live observations vs remembered snapshots** as separate per-player records | — | — | **Research-supported** — the methodological template for the info-state model in §6.11 |
| **BotScreen** (USENIX Security 2023) | aimbot detection from observable aim patterns; monitor client only sees visible players, so it only decides when both shooter and target are observable; 30° "aiming" threshold; ~97.64 % accuracy | — | **not** a wallhack detector | **Research-supported** — establishes both the technique (visibility-limited analytics) and its ceiling: visibility-derived cheating signals are weak, and "shot at someone I can't see" needs a *geometric* pipeline, not the spotted mask |

**No public implementation found** that produces a *per-player, per-tick, labeled information state* (confirmed /
inferred / relayed / unknown) from a CS2 demo. Pieces exist (raycasts, smoke voxels, spotting masks, voice); the
assembly is the novel part of this project.

## 6.3 LOS: how to implement it defensibly

Multi-sample raycasts, not a single eye→origin ray. CS2FOW demonstrates the sample set that works in production:
**body points + bounding-box corners + held-weapon muzzle**. For analysis (offline, no latency budget) the
sufficient set is the CS2 hitbox sample set: head, chest, stomach/pelvis, both shoulders/arms, both legs, plus the
weapon silhouette. Practical recommendation:

1. Eye origin: `z + 64` standing / `z + 46` crouched (awpy defaults; matches Source eye height). Use `duck_amount`
   for continuous interpolation (**Plausible-untested** for Source 2 exactness).
2. Target samples: ~8–12 points derived from the target's **model** with crouch applied.
3. Raycast each sample (`is_visible` equivalents); a target counts as visible if ≥1 sample is clear (Leetify's rule:
   "any part of the enemy's body or gun") — but store the **count/ratio**, not a boolean, for confidence scoring.
4. Frustum test: horizontal FOV 90° (awpy exposes `fov` as a player prop: `m_iDesiredFOV`; demo values may differ
   per player), pitch matters — awpy's vision model *ignores* pitch, which is a **known false-positive source**
   (nothing above/below your aim should count). Model the true vertical FOV from the engine's aspect/zoom handling,
   or at minimum gate on `pitch` (**Plausible-untested**).
5. Team check first; dead players project nothing; **blinded players project nothing while `is_blinded`** (with graded
   alpha for partial flashes if you can resolve onset → remaining).
6. Doors/breakables: static-bake approaches (awpy, CS2FOW) do **not** model them. Doors matter on de_mirage,
   de_cache, de_train-ish geometry and on Nuke/Vertigo geometry stacking. Handle them as per-map special cases or
   accept the error and disclose it.

Performance: awpy builds a BVH per map and reuses it; CS2DemoKit reports "tenths of a second" to load large bakes and
mutual exclusivity with caching; CS2FOW casts from a background worker while `CheckTransmit` only reads the answer.
Offline budget: a 40-minute demo × 10 players × 9 opponents × ~10 samples ≈ 10^7–10^8 raycasts; a BVH makes this
minutes-scale in Rust and tens-of-minutes in pure Python. **Design implication:** compute visibility on a **stride**
(1 Hz like awpy `map_control`, or event-anchored ticks) plus a full-rate window around each engagement; cache to
Parquet.

## 6.4 Nav mesh: what it is actually good for here

Not for LOS (awpy's docs are explicit that a nav mesh alone does not determine sight). It is good for:
* **area/callout labeling** of every event and every visibility transition (kills, deaths, plants, utility);
* **reachability maps** as the third, complementary control model ("who could arrive here first") — awpy
  `reachability` with `contest_margin`, fires blocking paths;
* **occlusion-free topology shortcuts**: precomputed *nav-area-to-nav-area* visibility matrices (a one-time per-map
  computation) let you answer "is any part of area A visible from area B" without per-tick rays — the cheap path to
  a "map control" heat layer at 1 Hz. **Plausible-untested** as a CS2 implementation; standard technique.

## 6.5 Smoke occlusion — the highest-value upgrade over awpy defaults

Three levels, in increasing fidelity:

1. **Sphere** (awpy `map_control`): radius 144 u, centre 60 u above the landing point. Cheap, clearly wrong at edges
   (smokes fill rooms and pour down ledges).
2. **Voxel seed from the demo** (`m_VoxelFrameData`, transform `world = (grid−16)·20 + detonationPos`): exact
   occupancy start; grow/decay over the cloud's lifetime; subtract holes from HE/bomb. **Extraction route is
   decode-only**: awpy has no `Voxel` surface and its raw-dump path returns the array *length* rather than the payload
   (peer-verified in `pbdems2 0.4.0` — §5.3), demoparser2 has no prop-map entry, so the choice is *port cs2parser's
   decoder* or stay on the sphere. **Experimental, VERIFY.**
3. **Re-simulate like the client** (5Stack's claim): fills rooms, stops at walls, pours off ledges, merges smokes.
   **Experimental**; the seed in (2) plus geometry propagation probably gets 90 % of the value.

Also model the **inverse** signals that smokes generate: a smoke detonation is itself conspicuous information
(sound + visual), and `thrusmoke` on a kill is direct evidence that the shooter had information *through* the cloud.

## 6.6 Sound — a much better signal than commonly assumed

Two demo-native channels exist:

1. **`player_sound { userid, radius, duration, step }`** — the server's own sound-emission record with an **audible
   radius**, per event (demoinfocs maps it to `PlayerSound{Player, Radius, Duration}`). This is *not* an approximation
   we invent: it is engine data. If it is present in FACEIT demos, movement-sound audibility is nearly solved.
   **Read it from the raw event keys**, not from a typed wrapper: demoinfocs drops `step`, demoparser2 documents no
   field accessor, and awpy 3.x does not list the event in `GAME_EVENTS` (`demo.events.player_sound` is an
   **[INFERENCE]** about the generic event API — see §5.2).
   **VERIFY presence in CS2 demos** (definitions exist in `mod.gameevents`; no CS2 demo verified in this research).
   Residual use of `step`: distinguishing a footstep-class sound from other player sounds when geofencing; if it is
   unavailable, fall back to `player_footstep` events + `weapon_reload`/`item_equip`/`grenade_bounce` correlations.
2. **Positional events you can geofence yourself**: `player_footstep`, `player_jump`, `grenade_bounce`, `door_moving`,
   `bullet_impact (x,y,z)`, plus grenade detonations, `decoy_firing`, bomb beeps.

Weapon fire has **no networked radius**. `weapon_fire{weapon, silenced}` names the weapon, so audibility must come
from a weapon table. Source 1's model is documented in the Valve SDK:
`attenuation = 20/(soundlevel − 50)`, `gain = max(0, 1 − d·attenuation/1000)`, `SNDLVL_GUNFIRE = 140`
→ **zero-gain radius ≈ 4500 units** for unsilenced gunfire (`soundflags.h`, `IEngineSound.h`
`GetDistGainFromSoundLevel`). Porting this to Source 2 CS2 weapon scripts is **Plausible-untested**; calibrate
empirically (walk a bot out to the edge of audibility) rather than trusting the table.

Propagation modeling beyond distance is where it gets soft: Source's audio uses distance attenuation + DSP
occlusion filters, but the demo does **not** record per-client DSP state. So:

* **Do** model: point-source → distance gain, floor/ceiling separation (Nuke/Vertigo z-stacking), and a crude
  "sound through a wall is filtered but still localizable" rule.
* **Do not** claim: exact audibility thresholds, wall-penetration spectra, or "the player must have heard X".
* **Special cases with real coaching value**: footsteps while *walking* (`is_walking`) are silent → asymmetric
  information; a silenced weapon at close range is audible but unlocalizable; a smoke-extinguished molotov is silent;
  `player_footstep` while `is_jumping`/landing is the loudest movement cue.

## 6.7 Last-known-enemy modeling

The game itself demonstrates the pattern: radar "?" at the last-seen position, no tracking, ~3–5 s fade (community
sources, **Plausible-untested**). Mirror it in the model:

* On loss of visibility, retain `(position, tick_of_last_seen, velocity_at_last_seen, confidence)`.
* Apply a **decay** on confidence with a half-life (default ~4 s) and allow "rehearsal" decay (a stale belief that is
  re-consulted without new evidence decays faster).
* Allow **motion extrapolation as a hazard, not a belief**: the *currently occupied* region is unknown; the model
  should represent "enemy was here, could now be anywhere reachable in Δt" — this is exactly the EWM paper's
  distinction between **live observations and remembered snapshots** (arXiv 2610.16166). Failing to separate these
  is the single most common way analysis slides into omniscience.
* On any *team* sighting, update the team-shared belief, not just the individual's (radar semantics: one teammate
  spotting reveals position to everyone — with the *same* last-known mechanics).

## 6.8 Teammate relay: the gap you cannot close from geometry

Three separable components:

* **Position information a teammate had** — reconstructable by running the same engine for teammates.
* **The fact that it was relayed** — partially observable: `player_ping` (POV demos only), voice audio (if the demo
  carries it), and *behavioural* evidence (a player turning/rotating/pre-aiming a direction only a teammate could
  have seen; a player repositioning before any local stimulus).
* **The semantic content** — for voice: ASR + timing; but the demo only gives you the audio, not the intent, and MM
  demos have no audio at all.

Therefore: **model teammate relay as a separate, evidence-graded channel with lower confidence than direct vision**,
and never let it silently upgrade to "confirmed". Behavioural inference of relayed information ("why did he turn?")
is the honest framing — it is also the part of the analysis most vulnerable to hindsight bias, so it must be labeled
as inference.

## 6.9 Noticed vs available (the difference between geometry and perception)

"Visible" ≠ "noticed". A per-tick, per-enemy gaggle of 11 actors gives many opportunities to be technically visible
in the periphery. Model the gap explicitly:

* **angular distance from crosshair** (Leetify's "crosshair placement"/TTD history shows this is the industry-standard
  proxy), measured in degrees and in **pixels** (degrees × screen mapping) if you reconstruct FOV → a ~10° offset is
  a *lot*;
* **dwell time**: cumulative time the enemy was inside the FOV cone and unoccluded (≥ ~100–200 ms before "noticed" is
  plausible; the cognitive threshold should be a tunable parameter, not a claim);
* **centrality-weighted exposure**: weight by `1/(1 + (angle/θ)²)` rather than a hard cone edge;
* **motion salience**: a moving enemy at the same screen position is noticed sooner than a static one; a stationary
  enemy is exactly what pre-aiming is for;
* **flash state, scoped state, zoom level** (a scoped AWPer has ~40° effective FOV — `is_scoped` + `zoom_lvl` are
  directly available; the resulting FOV per zoom level is **Plausible-untested** and should be measured);
* **audio priming**: if a sound preceded the visual by Δt in the same direction, raise the "noticed" prior.

Output a graded `attention` score per (player, enemy, tick) rather than a boolean; downstream decisions should use
the score.

## 6.10 Achievability verdicts

| Capability | Verdict | Basis / conditions |
| --- | --- | --- |
| Reconstruct who **could** see whom, each tick, walls only | **Demonstrated** | awpy `VisibilityChecker`, CS2DemoKit, my own pipeline. Needs map bake per `ClientVersion`. |
| Add **FOV/gaze** to that | **Demonstrated** | awpy `map_control --method vision`; needs pitch handling to avoid false positives. |
| Add **flash** exclusion | **Demonstrated** | awpy (`flash_threshold`), Leetify-class practice. Graded partial flashes = Experimental. |
| Add **smoke** occlusion | **Experimental** — sphere is Demonstrated-tunable today; voxel-exact is Experimental and **decode-only** (port cs2parser; awpy/demoparser2 raw routes ruled out, §5.3) | awpy sphere default today; voxel seed path exists. |
| Add **doors/breakables** | **Experimental / map-specific** | Not in awpy or CS2FOW; needs per-map entity handling (door state exists as an entity; `door_moving` events give motion). |
| **Sound** audibility (movement) | **Demonstrated if `player_sound` present** — else Plausible-untested | `player_sound.radius` is engine data; VERIFY presence in MM/FACEIT demos. |
| **Sound** audibility (gunfire/utility) | **Plausible-untested** | Weapon-table/`soundlevel` port + empirical calibration. |
| **Radar/spotting** state | **Demonstrated (field) / Plausible-untested (meaning)** | `m_bSpottedByMask` extractable but only bits 0..15 resolve; likely GOTV-client-scoped rather than per-player; use as corroborator only (§5.6). |
| **Last-known-enemy** belief stream | **Demonstrated methodology**, buildable | EWM precedent; no CS2 implementation exists publicly. |
| **Teammate relay: position** | **Demonstrated** | Run the engine per teammate. |
| **Teammate relay: content** | **Plausible-untested, demo-dependent** | Voice: verify FACEIT demo carries it. MM: infeasible. |
| **Noticed-vs-available** grading | **Research-supported / Plausible-untested** | No CS2 ground truth exists; must be validated against POV video or self-reports. |
| **Per-pixel / what was on screen** | **Infeasible from demo alone** | TrueView exists precisely because playback ≠ POV; requires POV rendering (EgoCS-400K path). |
| **Enemy's information state** | Same engine, roles swapped | Useful for "was this actually a 50/50?" analysis. |
| **Cheat-detection-grade "he shot the unseen"** | **Plausible-untested, low-confidence** | BotScreen explicitly avoids this; geometry + spotted mask + `thrusmoke`/`penetrated` give leads, not verdicts. Do not ship verdicts. |

## 6.11 Proposed chronological information-state representation

### 6.11.1 Design principles

1. **Chronological, causal, per-player, append-only.** State at time `t` is a pure function of evidence at `≤ t`.
   No array may be indexed by future ticks (structurally enforced, not by convention).
2. **Provenance on every atom.** Each belief carries `source` (which channel produced it) and `tier`.
3. **Five tiers**, matching the acceptance criteria:

| Tier | Label | Definition | Typical producer | Confidence |
| --- | --- | --- | --- | --- |
| T0 | `omniscient` | True world state, never available to the player. Used **only** for labels/evaluation, never as model input. | demo state | 1.0 but *privileged* |
| T1 | `confirmed` | Directly experienced: the entity was in the player's FOV, unoccluded, not smoke-blocked, player not blind/blinded; **plus** engine corroboration where available (`spotted` mask bit set, `player_hurt` on the player, a kill/death they participated in). | vision engine + events | high (0.8–1.0) |
| T2 | `inferable` | Not currently visible but derivable from present evidence: sound within radius (`player_sound`, footsteps in range, gunfire within weapon range), teammate contact already relayed, bomb beep/plant phase, observed utility landing, `thrusmoke`-style direct evidence from *this* player's own action. | sound model + team share + events | medium (0.4–0.8) |
| T3 | `relayed` | Positional/semantic info attributable to a teammate (voice/ping/behavioural inference) — includes "team knows" radar semantics. | voice ASR/pings/behaviour + team-share | medium-low (0.2–0.6), and *named* as relay |
| T4 | `unknown` | Everything else, including **decayed** T1/T2/T3 beliefs: "was here at t₀, could now be within reachable region R". | decay/extrapolation | low (<0.2) |
| — | `available_but_unnoticed` | Orthogonal modifier on T1: geometrically available, attention score below threshold. | attention model | n/a |

4. **Team-shared vs private.** Two streams per team: `private(pid)` (T1/T2 evidence only that player holds) and
   `shared(team)` (union of T1/T2 over living teammates, subject to `is_blinded`/alive status), with relay lag.
   Radar semantics = `shared` with last-known decay.
5. **Belief objects, not positions.** A belief is
   `{subject, tier, source, position?, region?, velocity?, last_seen_tick, confidence, evidence_refs[]}` where
   `region` is an *unknown-but-reachable* hull for T4. Positions are never updated "as if" by omniscience.

### 6.11.2 Concrete schema (per player, per round)

```jsonc
{
  "player": {"steamid": "...", "side": "ct", "round": 7, "part": 0},
  "stream": [
    {
      "tick": 21450, "t": 335.156,
      "self": {"x": ..., "y": ..., "z": ..., "yaw": ..., "pitch": ...,
               "eye_z": ..., "fov_h": 90, "is_scoped": false,
               "is_blinded": false, "flash_remaining": 0.0, "is_walking": true},
      "team": {"alive": 4, "bomb": "carried:7656...", "shared_beliefs_digest": "..."},
      "observations": [
        {"subject": "enemy:7654...", "tier": "confirmed",
         "position": {"x":..,"y":..,"z":..}, "sample_visibility_ratio": 0.62,
         "angle_deg": 3.4, "dwell_ms": 480, "attention": 0.91,
         "sources": ["vision:geometry", "engine:m_bSpottedByMask"],
         "evidence": ["tick:21412 visible=0.0", "tick:21450 visible=0.62"]},
        {"subject": "enemy:7655...", "tier": "inferable",
         "sound": {"kind": "footstep", "radius": 1200, "distance": 780, "path_occluded": true},
         "confidence": 0.55,
         "evidence": ["event:player_sound@21448"]},
        {"subject": "enemy:7656...", "tier": "unknown",
         "region": {"nav_areas": [812, 815, 830], "reachable_in_s": 3.0},
         "last_seen_tick": 20880, "confidence": 0.08,
         "evidence": ["tick:20880 visible=0.4", "decay:hl=4.0s"]}
      ],
      "own_events": [
        {"kind": "weapon_fire", "weapon": "ak47", "aim_error_deg_to_nearest_belief": 1.2,
         "belief_tier_of_target": "confirmed", "thrusmoke": false}
      ],
      "boundary": {"frame_clock": 21450, "server_tick": 21450, "part": 0}
    }
  ],
  "omniscient_sidecar": {
    "note": "T0 world state for the same ticks, in a SEPARATE file/table.",
    "players": {"7654...": [{"tick": 21450, "x": ..., "y": ..., "z": ..., "hp": 100}]}
  }
}
```

Storage: two physically separate artefacts — `beliefs/{match}/{player}/part-*.parquet` (model-visible) and
`world/{match}/part-*.parquet` (labels only). Different credentials, different directories, different loaders. This is
the strongest available structural defense against information leakage into the coaching prompt.

### 6.11.3 Anti-hindsight-bias requirements for downstream AI

These are hard requirements; each maps to an enforceable check.

1. **No future reads.** The belief builder is a single forward pass; a leak test should assert that truncating the
   demo at tick `t` yields byte-identical beliefs for all ticks `≤ t`.
2. **Privileged-channel quarantine.** World state (T0) is a separate store; the coaching model's context builder must
   physically lack a path to it. If a privileged critic is used (training/eval only), it must be an *unbiased*
   asymmetric design — naive asymmetric critics bias policy/value estimates (arXiv 2105.11674; 2412.00985;
   2509.26000) — and must never write back into the decision-time context.
3. **No outcome leakage in prompts.** Never include final round result, later kills, damage after the decision point,
   or "he died here" in the prompt for a decision at `t`. Build the prompt from the belief stream only.
4. **No scoreboard leakage.** K/D/A and round score are *available* to the player (HUD), so they are legal — but the
   *final* score and later rounds are not. This is a per-field, per-tick legality table, not a vibe.
5. **Grade claims by tier.** Every coaching statement must cite the tier it rests on: "he was visible (confirmed)",
   "he could only have inferred from footsteps (inferable)", "a teammate had to have told him (relayed)", "the info
   was not available (unknown)". Statements about T2/T3 **must** be phrased as inference.
6. **Report the counterfactual distribution, not the hindsight.** For decision review, enumerate the *options that
   were consistent with the belief state at `t`* (e.g. "with only a footstep in B, holding A-site rotation was
   defensible"). Prefer "was this decision correct given available information" over "would this have worked".
7. **No post-hoc salience.** Do not use "the enemy was there" to explain a decision made before the information
   existed. The belief stream makes the timing explicit; the prompt builder must join on tick, not on event identity.
8. **Calibration tracking.** Log, per claim type, whether the player's action confirms the inferred belief
   (e.g. he turned toward the inferred sound within X ms). This turns the inference layer into something measurable
   instead of hand-waving — and it is the honest way to claim "unconscious habit detection".
9. **Explicit uncertainty in prompt and output.** Confidence and tier travel with every fact end-to-end, including
   into the LLM prompt; the model is instructed to hedge at the stated confidence. This matches the EWM dataset's
   live-observation vs remembered-snapshot separation (arXiv 2610.16166) and the defensive posture BotScreen takes
   about not over-claiming (USENIX Sec 2023).

### 6.11.4 What is achievable vs uncertain — summary

**Achievable now, with disclosed tolerance**
* Per-tick world state and event timeline (fully direct).
* Geometric LOS + FOV + flash + (sphere smoke) visibility graph for every player, on a stride + event-anchored ticks.
* Team-shared radar-style belief with last-known decay.
* Sound-audibility *events* (radius field) if present; geofenced approximations otherwise.
* Everything above at product quality: 5Stack VISION, Leetify, CS2DemoKit, awpy `map_control` all ship some subset.

**Achievable with visible experimental work**
* Voxel-exact smoke occlusion and growth/hole handling.
* Doors/breakables.
* Weapon-specific audibility calibrated against the real game.
* Attention ("noticed") scoring with dwell/salience/zoom-aware FOV.

**Uncertain; must be validated empirically (and never presented as fact)**
* Whether CS2 emits `player_sound` in MM/FACEIT demos (**VERIFY** — highest-leverage unknown).
* Whether FACEIT demos carry voice, and in which of the two files (**VERIFY**).
* `flash_duration` decay semantics (**VERIFY**).
* Exact FOV per zoom/scope state, exact eye height under partial crouch, hitbox geometry used by the server.
* Any claim of the form "the player must/must not have perceived X".

**Not achievable from a demo**
* Pixel-accurate reconstruction of what was rendered (TrueView + version pinning exist because playback ≠ POV).
* Audio *content* of comms in demos that do not record voice.
* Any reading of the enemy's live positions beyond what the demo's transmit filtering implies (and PVS filtering is
  coarse, so "not in the demo" ≠ "not known").

## 6.12 Recommended build order for this slice (feasibility-driven)

1. Ingest demo → normalized Parquet: ticks (stride 1), events, shots, damages, grenades, smokes, fires, economy,
   spots; pin parser + `awpy-data` release by `ClientVersion`; record `Health`/warnings per demo.
2. Map assets: `visibility.mesh` + `.nav` + radar/`map_data.json`, cached per `ClientVersion`; per-map BVH built once.
3. Visibility engine: build scripts/rays + cache `(tick, observer, target)` sample-count and angle/dwell features on a
   1 Hz stride plus a dense window around every kill/damage/first-contact.
4. Smoke layer: start with awpy's sphere; then port cs2parser's voxel-seed decode (the only route — awpy/demoparser2 raw
   paths are ruled out, §5.3) and validate against a hand-checked smoke in one match.
5. Sound layer: `player_sound` + geofenced events; calibrate weapon ranges in-game.
6. Belief stream builder (§6.11.2) with tier tagging + provenance.
7. **Validation harness**: for 5–10 self-played demos, compare predicted first-contact ticks against POV video
   (screen-share or rendered replay) — the only honest ground truth available without cheating-adjacent tools.
   **There is no external benchmark to borrow**: vendor metrics are aggregate-only *and* barred from storage by ToS
   (§5.0), and no public LOS validation exists. Budget for self-generated ground truth, and treat the first 10
   hand-labeled contacts as the acceptance fixture for the whole visibility engine.

---

## Source list (accessed 2026-10-15 unless dated)

**Parsers / data**
1. demoparser2 — field tables, function signatures, `parse_voice`, `parse_grenades`, benchmarks: https://github.com/LaihoE/demoparser and https://raw.githubusercontent.com/LaihoE/demoparser/main/documentation/python/README.md
2. demoparser2 issue #232 (`NA` grenade coordinates; fixed 0.36.0, Feb 2025): https://github.com/LaihoE/demoparser/issues/232 ; mask-accessor internals cited by EcosystemSurvey.ParsersLibs (2026-10-15): `src/parser/src/second_pass/collect_data.rs:790-797` (`find_spotted`, single `Variant::U32`) + `game_events.rs:244-251` (`steamids_from_mask`, `for i in 0..16` with a linear controller scan)
3. awpy — README, datasets, snapshots/ticks, visibility, nav, map_control, API, schema: https://github.com/pnxenopoulos/awpy ; docs at `crates/awpy-python/docs/{datasets,visibility,nav,map_control,api}.md` ; `python/awpy/schema.py`. Parse core is **pbdems2 0.4.0** (crates.io, read 2026-10-15) — cited by EcosystemSurvey.ParsersLibs for why the raw-dump smoke-voxel route fails: `src/entity/field_decoder.rs:543-556, 765-805` (dynamic arrays) + `src/entity/entities.rs:314-330` (parent key holds the element count, elements under child field-path keys) + `src/entity/serializers.rs:229-300` (name resolution recurses only after a parent-prefix match — hence the nested `m_entitySpottedState.m_bSpottedByMask.0000` path); awpy binding `awpy-python/src/lib.rs:2712-2718` (no alias layer for `ticks(props)`)
4. awpy-data — VPK extraction pipeline, asset layout, `ClientVersion` pinning: https://github.com/pnxenopoulos/awpy-data
5. CS2DemoKit — typed events, user-cmd delta reconstruction, `enemy_spotted`, two clocks, health/warnings: https://github.com/CS2OpenDev/CS2DemoKit
6. cs2parser — smoke voxel decode (`f3e672a`, 2026): https://github.com/osztenkurden/cs2parser/commit/f3e672a923157df0b849bc307d7a0e6fb9d1ed8d
7. CS2OpenDev schema — `CSmokeGrenadeProjectile` (build 25218825, 2026-09-09): https://cs2opendev.github.io/CS2OpenDev-Docs/schemas/server/CSmokeGrenadeProjectile/
8. SteamTracking/GameTracking-CS2 — `mod.gameevents` (141 events, extracted 2026-10-15), `Protobufs/usercmd.proto`, and the smoke entity headers `DumpSource2/schemas/client/C_SmokeGrenadeProjectile.h` (lines 8-10: `m_VoxelFrameData`, `m_nVoxelFrameDataSize`, `m_nVoxelUpdate`) / `server/CSmokeGrenadeProjectile.h` (verified by EcosystemSurvey.ParsersLibs, 2026-10-15): https://github.com/SteamTracking/GameTracking-CS2
9. demoinfocs-golang — `IsSpottedBy`/"NOT Line of Sight", `PlayerSound`/`Footstep` (**`PlayerSound{Player, Radius, Duration}` at `events/events.go:154-159`; `game_events.go:405-410` reads only `userid`/`radius`/`duration` — the `step` key is dropped**), POV-only events: https://github.com/markus-wa/demoinfocs-golang
10. cs2-tools / cs2-demo-viewer — wall-clipped vision cones: https://github.com/skkwowee/cs2-tools , https://github.com/skkwowee/cs2-demo-viewer
11. CS2VoiceData — voice extraction; "Valve Matchmaking demos do not contain voice audio data": https://github.com/DandrewsDev/CS2VoiceData
12. ZeroUtil — CS2/FACEIT demo voice, tick-to-time, share codes (tool-vendor docs): https://zeroutil.com/blog/cs2-hear-voice-comms-demos/ , https://zeroutil.com/tools/cs2-demo-voice-extractor/

**Fog-of-war implementations**
13. awpy `map_control` (raycast/vision/reachability, smoke sphere, flash threshold, params): docs `map_control.md` (same repo as #3)
14. CS2FOW — server-side anti-wallhack, BVH8, sample points, latency margins, smoke/doors not blockers, fail-open: https://github.com/Xsinity/CS2FOW (fork read: github.com/mfernandez4/CS2FOW)
15. 5Stack Match Replay — VISION/fog-of-war layer, smoke rebuilt from CS2's own simulation, real blind times: https://docs.5stack.gg/features/match-replay
16. Leetify — "Enemy (actually) spotted" 2020-10-04 (radar spotting failures, rebuild): https://leetify.com/blog/enemy-actually-spotted/
17. Radar last-known "?" and spotting semantics (community): https://www.tobyscs.com/csgo-radar-settings/ ; `radarvisdistance` (community command docs)
18. TrueView (Valve patch 2025-11-05) via PC Gamer, 2025-11-05: https://www.pcgamer.com/games/fps/counter-strike-2-has-a-fancy-new-feature-that-makes-demo-playbacks-match-the-players-original-experience-much-more-closely/

**Research**
19. X-Ego / X-Ego-CS — arXiv:2510.19150 (2025-10-22): https://arxiv.org/abs/2510.19150
20. EgoCS-400K — arXiv:2606.18180 (2026-06-16): https://arxiv.org/abs/2606.18180
21. Esports World Model Dataset (EWM; fog of war / team vision / remembered snapshots) — arXiv:2610.16166 (2026-10-12): https://arxiv.org/abs/2610.16166
22. Data-driven discretized CS:GO simulation env — arXiv:2509.06355 (2025)
23. BotScreen — USENIX Security 2023: https://www.usenix.org/system/files/usenixsecurity23-choi.pdf
24. Asymmetric/privileged-information RL: arXiv:2105.11674 (Baisero & Amato), arXiv:2412.00985, arXiv:2509.26000 (Ebi et al., ICML 2026)
25. Source engine sound attenuation — `soundflags.h` (`SNDLVL_GUNFIRE 140`, `20/(level−50)`), `IEngineSound.h` `GetDistGainFromSoundLevel`: https://github.com/ValveSoftware/source-sdk-2013

## Open VERIFY list (cheapest first)

1. Parse one FACEIT + one Premier demo: presence/counts/keys of `player_sound` (**including whether the raw `step`
   key survives**, since no typed wrapper exposes it), `player_footstep`, `bullet_damage`, `player_ping`, `spotted`
   mask changes.
2. **RESOLVED — negative (peer-verified, 2026-10-15).** No accessible parser surfaces `m_VoxelFrameData`: awpy has no
   `Voxel` surface and its raw-dump path returns the array **length**, not the payload (`pbdems2 0.4.0`
   `entity/field_decoder.rs:543-556, 765-805` + `entity/entities.rs:314-330`; elements live under child field-path
   keys, and `FieldValue` has no array variant that reaches a typed Polars column), and demoparser2 has no prop-map
   entry. **Decision: port cs2parser's decoder, or keep awpy's r=144 sphere.** No round trip needed.
3. **Does the GOTV spotted mask track the observing player or the GOTV client?** Correlate `m_bSpottedByMask` rising
   edges against geometrically computed visibility per player; if it does not correlate per-player, the field is
   unusable even as a corroborator. (Highest-priority de-risking item; no prior art exists either way.)
   **Script note (peer-verified):** read it as `m_entitySpottedState.m_bSpottedByMask.0000/.0001` +
   `m_entitySpottedState.m_bSpotted` via awpy `ticks(props, players_only=False)` (a bare `m_bSpottedByMask` does not
   resolve — §5.6), or as `approximate_spotted_by` via demoparser2. Confirm the `.0000` index naming on the first run
   before building on it.
   **Methodology warning:** do **not** run this correlation on demoparser2's `approximate_spotted_by` column alone —
   it reads only 16 of 64 bits, silently drops unresolvable bits, and emits literal `0`s, so it *cannot produce a
   trustworthy negative* (§5.6). Bit-level truth comes from the awpy dotted path in the same run; otherwise a weak
   result is uninterpretable. **Also verify the mask is not stale/frozen for GOTV-observed players** — read the mask
   for the *observer's* own pawn, not just for enemies, to confirm the field is live per-observer at all.
4. **LOS ground truth**: are the sample-point/FOV assumptions right? Validate first-contact ticks against POV video
   on 5–10 self-played demos (no public validation of awpy/CS2FOW/CS2DemoKit LOS exists).
5. `flash_duration` decay: plot `flash_duration` across a known flash.
6. Voice: `parse_voice()` on both FACEIT demo files of one match.
7. Measure effective FOV at each zoom level (`zoom_lvl`) and confirm eye height standing/crouched from position + LOS.
8. Confirm projectile trajectory gaps (NA) still occur on current builds.
9. Time the visibility pass on one real match (rays/s target) to size the stride policy.
