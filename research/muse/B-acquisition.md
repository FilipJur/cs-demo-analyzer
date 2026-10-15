# §4 — Automatic demo acquisition (FACEIT + Valve/Steam)

Research date: 2026-10-15. Scope: how a local-first, single-user CS2 analysis system can obtain its own match demos with as little human action as possible. Non-goal: demo parsing internals.

Evidence labels used throughout: **[Demonstrated]** = working reference implementation or reproduced behaviour; **[Experimental]** = works but fragile/unofficial; **[Research-supported]** = primary documentation states it; **[Plausible-untested]** = consistent with the evidence, not directly verified by us; **[Infeasible]**.

---

## 0. Verdict summary

| Platform / case | Automation level realistically achievable | Key constraint |
|---|---|---|
| **FACEIT — with approved Downloads API access** | **[Demonstrated]** fully automatic (webhook/poll → `demo_url` → signed URL → file) | Access is application-gated, expected 30-day review, commercially priced; CS:DM (most mature OSS consumer) still cannot ship it |
| **FACEIT — without approval (normal user)** | **semi-automatic** — user clicks “Watch demo” in the match room; all post-download work automatic (extension/native host or folder watcher). No sanctioned unattended path. | `demo_url` is a private cloud resource; signed URLs are short-lived; FACEIT policy forbids internal APIs |
| **FACEIT — older than 30 days** | **[Infeasible]** on FACEIT | Match-room demos are only offered for ~30 days |
| **Valve MM/Competitive/Wingman/Premier — GCPD web page, own account** | **[Demonstrated]** fully automatic, **walks the full retained match history (not capped at 8)**, no CS2 launch needed | Needs a Steam **web session** (password + Steam Guard secret once, then a stored refresh token / cookies); it is website scraping of `steamcommunity.com/my/gcpd/730` |
| **Valve — GC path, last 8 matches, same machine as Steam** | **[Demonstrated]** fully automatic | Steam must be running + logged in; CS2 must be installed and is briefly launched to hold a GC session |
| **Valve — beyond last 8 via GC only** | semi-automatic | GC exposes only the last 8; older matches need a share code the user copies out of the client at least once per month |
| **Valve — headless GC (no Steam client), own account** | **[Experimental]** fully automatic | Requires `node-steam-user` + logged-in session (credentials/refresh token), plus monthly share code for >8 matches |
| **Valve — no credentials, no GC (UI-download watcher)** | semi-automatic (user clicks Download in “Watch → Your Matches”) | Only last 8 matches, ~30-day availability |
| **Valve — older than ~30 days** | **[Infeasible]** (unless captured earlier) | `replay*.valve.net` 404s / “Match demo has expired” |

Practical bottom line: **Valve is the only platform where end-to-end unattended acquisition is achievable today for a personal setup. Two mechanisms exist: (a) the GCPD web page with a Steam web session — no CS2 launch, no 8-match cap, bounded only by demo retention; (b) the Game Coordinator (local Steam client or a headless login) — no credentials on disk, but capped at 8 matches unless a share-code cursor is refreshed monthly. FACEIT is inherently semi-manual for individuals: the file itself must originate from a logged-in browser session (or an approved/paid API).** Design the acquisition layer so that “human hands over one file or one URL” is a first-class input, not a failure path.

---

## 1. FACEIT

### 1.1 Endpoints and auth

| Purpose | Endpoint | Auth | Notes |
|---|---|---|---|
| Player’s match list | `GET https://open.faceit.com/data/v4/players/{player_id}/history?game=cs2&from=<unix>&to=<unix>&offset=<≤1000>&limit=<≤100>` | `Authorization: Bearer <API key>` | `from` defaults to 1 month ago, `to` to now. Response items (`MatchHistory`) contain `match_id`, `finished_at`, `status`, `started_at` — **no demo field** |
| Match details | `GET https://open.faceit.com/data/v4/matches/{match_id}` | same | Response contains `demo_url` (array of strings) and `instances[].demos` |
| Match stats | `GET https://open.faceit.com/data/v4/matches/{match_id}/stats` | same | Round stats; used by CS:DM to build scoreboards |
| Demo → signed URL | `POST https://open.faceit.com/download/v2/demos/download` body `{"resource_url":"<demo_url entry>"}` → `{"payload":{"download_url":"<signed>"}}` | **separate access token with the Downloads API scope** (Bearer) | Requires applying via the form (`https://fce.gg/downloads-api-application`); docs state expected response ≈ **30 days** |

Sources: Data API docs + OpenAPI spec <https://open.faceit.com/data/v4/docs/swagger.json> (fetched 2026-10-15; `Match.demo_url` is `"type":"array"`, `MatchInstance.demos` array, `MatchHistory` has no demo field; history `limit` max 100, `offset` max 1000), <https://docs.faceit.com/docs/data-api/data/>, <https://docs.faceit.com/getting-started/Guides/download-api/>, <https://docs.faceit.com/getting-started/authentication/api-keys/>.

API keys are created per app in App Studio and are of “client side” / “server side” kind; keys can be rotated/revoked at will. The normal Data API key does **not** grant demo downloads — the Downloads API requires a token with an exclusive scope. **[Research-supported]**

### 1.2 Event notifications (webhooks)

* Events relevant here: **`match_demo_ready`**, `match_status_finished`, `match_status_aborted`, … full list in <https://docs.faceit.com/docs/webhooks>.
* Subscription types: Organizer / **User** / Game. “User → My user” is the fitting scope for a personal tool; subscriptions are configured in the Developer Portal (App Studio) and call back to a single configured REST endpoint. Callback authentication is optional (static header and/or query param) and implemented by the developer.
* **The webhook body schema is not published.** Community implementations read the match id from `payload.id` (e.g. Faceit-Volunteer-Dev-Team/Webhooks-Template `index.js`), and then fetch `/data/v4/matches/{id}` to obtain `demo_url`. **[Plausible-untested]** — log the first real payload before relying on it.
* The Download API guide explicitly recommends subscribing to `match_demo_ready` “to get updates when a demo is uploaded in the cloud storage”.
* Practical caveat for a **local-first** system: a webhook needs a publicly reachable HTTPS endpoint. Without a tunnel, polling is the local-friendly equivalent.

### 1.3 Rate limits

* The Data API documents HTTP **429** on every endpoint but publishes **no numeric quota** (window, per key/app/IP all unspecified).
* The only official numeric figure found is **40 requests/second**, and it belongs to the **CDP partner integration**, *not* the public Data API (<https://docs.faceit.com/getting-started/partner-integration-guide/cdp-integration/>).
* Practical guidance from the ecosystem: conservative request volume, cache aggressively, paginate, back off on 429 (honour `Retry-After` when present). **[Plausible-untested]**
* Extra limit tier observed in the field: CS:DM documented that FACEIT gave it “a server-side API key with the maximum rate limit”, i.e. rate limits are tiered per credential and not headroom-free (<https://cs-demo-manager.com/docs/guides/downloads>).

### 1.4 Demo availability, URL shape, expiry

* **Retention: ~30 days.** FACEIT support: “Ensure that the match took place within the last 30 days” before using *Watch Demo* (<https://support.faceit.com/hc/en-us/articles/10622392832412-How-to-download-and-watch-a-CS2-demo>, updated 2023-09-28). Independently confirmed by Leetify in 2024: “these links expire after 30 days” (<https://leetify.com/blog/demo-storage-changes/>, 2024-02-05).
* Hosts observed over time (do **not** construct URLs; always take what the API/browser returns):
  * `https://demos.faceit.com/csgo/1-<uuid>-1-1.dem.gz` (docs example)
  * `https://demos-europe-central.backblaze.faceit-cdn.net/cs2/1-<uuid>-1-1.dem.gz` (CS:DM issue #920 logs, 2024-08-26 — host no longer resolved: `getaddrinfo ENOTFOUND`)
  * `https://demos-europe-central-faceit-cdn.s3.eu-central-003.backblazeb2.com/cs2/1-<uuid>-1-1.dem.zst?X-Amz-Algorithm=…&X-Amz-Expires=…&X-Amz-Signature=…` (Leetify’s published example, 2025-08-04)
* Consequences: the browser “Watch demo” link is an **S3/Backblaze SigV4 presigned URL** carried in query parameters; it is short-lived (`X-Amz-Expires`, in seconds; Backblaze examples use 3600 s, the FACEIT value was not observable → **[Plausible-untested]**) and host-bound (the signature covers the host — never rewrite the hostname). Presigned URLs must be consumed immediately or re-acquired.
* Format: CS2 demos arrive as `.dem.zst` (current) or `.dem.gz` (older); both are single-stream archives → stream-decompress (zstd / gzip), never buffer whole file.

### 1.5 What actually happened to FACEIT demo access (timeline = the real limit story)

| Date | Event | Source |
|---|---|---|
| 2023-09-28 | Support: demo available only for matches within 30 days | support.faceit.com |
| 2023-11-24 | CS:DM: “FACEIT demos links are now private and require access to the Downloads API… I sent an access request the 24/11/2023 but in the meantime FACEIT downloads will not work.” (code comment in `src/node/faceit/fetch-faceit-match.ts`) | cs-demo-manager source |
| 2024-02/03 | FACEIT moved demo downloads to a **paid model**, rate-limited Leetify with days of notice; quoted ≈ **€270 000/year** | <https://leetify.com/blog/faceit-changes/> (2024-03-11) |
| 2024-07 → 2025-08 | Leetify pivots to **browser extension + user-submitted presigned URL** (`POST https://api.cs-prod.leetify.com/api/faceit-demos/submit-demo-download-url`, 429 → wait 300 s) | <https://leetify.com/blog/faceit-demo-upload-api/> (2025-08-04), <https://leetify.com/blog/faceit-browser-extensions/> |
| 2026-04-09 | FACEIT Season 8 **Match Insights** (Premium): round-by-round 2D radar, kill/death coords, utility detonations, timeline charts — in the browser, “removing the requirement to download a demo file for basic match analysis”. No public API documented. | support.faceit.com (2026-04-09, upd. 2026-05-26) |
| current (2026-10) | CS:DM still cannot download FACEIT demos in-app: “FACEIT restricted demo downloads to a private API… There is no ETA for restoring in-app downloads; in the meantime, please download demos from your browser (one extra click).” | <https://cs-demo-manager.com/docs/guides/downloads> |

Interpretation: the Download API exists and works, but access is **commercial/partner-gated**. For an individual, assume it will not be granted. Everything labelled “automatic FACEIT demo download” in the wild today is a browser-context workaround (extension/native host) or a paid third-party API.

### 1.6 Policy / ToS

* FACEIT **Organizer Code of Conduct** (published 2025-09-04, updated 2026-03-17): *“Organizers must not use any internal APIs, unless an explicit exception is granted. You may only use Open API …”* — <https://support.faceit.com/hc/en-us/articles/22144515168412-FACEIT-Organizer-Code-of-Conduct>. Organizer-scoped wording, but it states the platform’s stance clearly.
* The general FACEIT ToS is not machine-readable from outside (Cloudflare 403 on `https://www.faceit.com/terms`; the 2026-10-09 Wayback snapshot renders its body client-side), so the following wording is **secondary**: ToS;DR’s index of FACEIT’s terms records prohibitions against gaining unauthorised access to the Site’s systems, interfering with the Site’s communications/procedures/performance, and using “automatic, macro, bots, automated programs, screen analysis utilities … or similar methods” — <https://edit.tosdr.org/points/86619>, snapshot index <https://web.archive.org/web/20261009110859/https://www.faceit.com/en/terms>.
* Practical reading: **documented Open API = fine; scraping internal endpoints or automating the website = not authorised**. Replicating the browser’s “Watch demo” request with the user’s own session cookie is technically trivial but sits outside the published contract; treat it as personal-use-risk, keep it opt-in, keep it local, and don’t redistribute the resulting credentials.
* Note the second-order risk: the sanction for ToS breach is account-level (the user’s own FACEIT account), not just app-level. This matters when choosing how much automation to ship.

### 1.7 FACEIT asset formats worth knowing

* `GET /matches/{id}` also returns `results`, `teams`, `voting`, `configured_at`, `faceit_url` — enough to key a match record without the demo.
* `GET /matches/{id}/stats` returns per-round `round_stats` with `Map`, `Score`, `Team Win`, `First Half Score`, `Overtime score`, `Team`, and per-player `player_stats` (Kills, Assists, Deaths, Headshots %, K/D, K/R, MVPs, multi-kill counts). CS:DM derives its FACEIT scoreboard from `rounds[0]` only. This is a **no-demo fallback signal source** if a demo is unobtainable.

---

## 2. Valve / Steam (CS2 matchmaking: Competitive, Wingman, Premier)

### 2.1 Path A (Game Coordinator) and Path B (share-code cursor)

**Path A — Steam Game Coordinator.** No *Steam Web API* method returns the demo URL: `ICSGOPlayers_730` exposes exactly three methods (`GetNextMatchSharingCode`, `GetPlayerProfile`, `GetPlayerProfileCoin`) per <https://steamapi.xpaw.me/ICSGOPlayers_730>. The GC is one of two surfaces that do return it (the other is the GCPD web page, §2.2); GC is the one the game client itself uses and the one that works without scraping HTML.

Relevant messages (from Valve’s own protobuf dump, `GameTracking-CS2/Protobufs/cstrike15_gcmessages.proto`):

```
k_EMsgGCCStrike15_v2_MatchListRequestRecentUserGames = 9141
k_EMsgGCCStrike15_v2_MatchListRequestFullGameInfo   = 9147

message CMsgGCCStrike15_v2_MatchListRequestFullGameInfo {
  optional uint64 matchid = 1; optional uint64 outcomeid = 2; optional uint32 token = 3; }

message CMsgGCCStrike15_v2_MatchList { repeated .CDataGCCStrike15_v2_MatchInfo matches = 4; … }

message CDataGCCStrike15_v2_MatchInfo {
  optional uint64 matchid = 1; optional uint32 matchtime = 2;
  optional .WatchableMatchInfo watchablematchinfo = 3;
  optional .CMsgGCCStrike15_v2_MatchmakingServerRoundStats roundstats_legacy = 4;
  repeated .CMsgGCCStrike15_v2_MatchmakingServerRoundStats roundstatsall = 5; }

message CMsgGCCStrike15_v2_MatchmakingServerRoundStats { … optional string map = 3; … }  // CS2: holds the demo URL
```

* Reference implementation (`akiver/cs-demo-manager`, current `main`): `const demoUrl = lastRoundMessage.map;` where `lastRoundMessage = roundstatsLegacy ?? last(roundstatsall)` (`src/node/valve-match/get-valve-match-from-match-info-protobuf-message.ts`). Corroborated by its `.dem.info` fixtures and snapshots which decode to `http://replay273.valve.net/730/003668537425296097309_2104686856.dem.bz2` (and `replay214/900/190/273/271…`).
* 2026-era example URLs are the same shape: `http://replay145.valve.net/730/003818616508322415524_1028609600.dem.bz2`, `http://replay187.valve.net/730/003751427519560024544_0081877035.dem.bz2` (reports 2025/2026).
* Download is a **plain GET** (no auth, HTTP not HTTPS), then decompress bzip2 → `.dem`. There is no directory listing; the URL must come from GC.
* **Hard limit of the GC list: the last 8 matches** — “Only the last 8 matches are available because the Steam Game Coordinator only provides this data.” (<https://cs-demo-manager.com/docs/guides/downloads>). This limit is a property of the GC message, **not** of Valve’s storage: the GCPD web page (§2.2) pages back much further.

**Path B — Steam Web API share-code cursor (for enumeration / older matches).**

Valve’s official doc (archived 2026-08-30): <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Access_Match_History>

```
GET https://api.steampowered.com/ICSGOPlayers_730/GetNextMatchSharingCode/v1
    ?key=<Steam Web API key>&steamid=<SteamID64>&steamidkey=<Game Authentication Code>&knowncode=<CSGO-…>
```

* `steamidkey` = user-created **Game Authentication Code** (Steam support wizard `help.steampowered.com/en/wizard/HelpWithGameIssue/?appid=730&issueid=128`), revocable by the user.
* **200 OK** → `{"result":{"nextcode":"CSGO-…"}}`; **202 Accepted** → `"n/a"` (known code is the newest); **412 Precondition Failed** → `knowncode` invalid/not owned by that user (stop until user supplies a fresh code); **403 Forbidden** → invalid `steamidkey`; **429/503** → strict rate limiting, reduce RPS; repeated invalid `steamidkey` at high rate triggers 503 even for valid pairs; **500/504** → retry later.
* Valve’s 2023-08-31 release notes (verified text from the official announcement JSON): *“Access to match history granted to third-party websites will now cover Competitive, Wingman, and Premier matches”* and *“GetNextMatchSharingCode API used by third-party websites must now supply a match sharing code that is no more than 1 month old…”* (<https://store.steampowered.com/news/app/730/view/3687939575937546143>). Same notes added Competitive/Wingman/Premier to the in-game “Your Matches” menu.
* **This endpoint yields share codes, not demos.** A share code carries three fields, verified from library source: `akiver/csgo-sharecode` v7.0.1 (`src/match.ts`, published 2026-10-05) exposes `decodeMatchShareCode(): { matchId, reservationId, tvPort }` and encodes exactly `8 bytes matchId ‖ 8 bytes reservationId ‖ 2 bytes tvPort` (18 bytes → share-code alphabet); its own docstring says these come from `CDataGCCStrike15_v2_MatchInfo`. https://github.com/akiver/csgo-sharecode
* **The naming bridge from that tuple to the GC request is an inference, not documentation.** GC expects `CMsgGCCStrike15_v2_MatchListRequestFullGameInfo { matchid, outcomeid, token }`. The mapping used by shipped code is `matchId→matchid`, `reservationId→outcomeid`, `tvPort→token` (cs-demo-manager passes `[matchId, reservationId, tvPort]` into `boiler-writter`’s documented `[matchId outcomeId tokenId]` argument list, and its share-code→download flow demonstrably works). Treat it as **functionally supported inference**, not a documented equivalence — and note it is now known to be lossy in the third slot (see next bullet).
* **The share code’s third field has a hard 16-bit budget and cannot carry a replay URL’s tv port.** The container is fixed at 25 characters / 18 bytes and `csgo-sharecode` splits it `8 + 8 + 2`; `int16ToBytes` masks the value to 16 bits and decode reads back only bytes 16–18. The library’s own README demonstrates the loss without noticing: its *encode* example uses `tvPort: 599906796` (30 bits) while its *decode* example shows `tvPort: 55788` — and `599906796 mod 65536 = 55788` exactly. Verified arithmetic: 599906796 & 0xFFFF = 55788; the replay URL component seen in the field is 31 bits (e.g. 2104686856). ⇒ **the share-code `tvPort` is provably not the URL’s second component**; get `tv_port`/`server_ip` from the GC reply, the `.dem.info` sidecar, or the GCPD row. Concrete failure mode if that rule is broken: a silent round-trip of the observed `tv_port` `2104686856` yields `63752` (= value & 0xFFFF), so code that reconstructs a replay URL from a share code would confidently request a *different* (almost certainly 404) file rather than failing loudly.
* Real-world field note: users who stop playing for weeks hit 412 because their stored cursor is older than a month; the fix is a fresh code from the client (claabs/cs-demo-downloader issue #5, opened 2025-05-01, still open).

### 2.2 Path C — GCPD web page (own account; no GC, no CS2 launch, no 8-match cap)

`https://steamcommunity.com/my/gcpd/730` is Valve’s **Game Coordinator Public Data** page on the Steam Community site. Unauthenticated requests 302 to `steamcommunity.com/login/home/?goto=%2Fmy%2Fgcpd%2F730…` (verified 2026-10-15) — i.e. it is real, live, and login-gated.

* **Tabs**: `?tab=matchhistorycompetitive`, `matchhistorypremier`, `matchhistoryscrimmage`, `matchhistorywingman`, `matchhistorycompetitivepermap` — i.e. Premier, Competitive, Wingman, Scrimmage each have their own list.
* **The page carries the replay URLs themselves**: each row links `http(s)://replay<NNN>.valve.net/730/<reservationId>_<tvPort>.dem.bz2`, plus a `YYYY-MM-DD HH:MM:SS GMT` match date. Rows with no URL mean “no demo retained” — reference implementations stop paginating there. (Component semantics: see the evidence bullet below.)
* **Paginated, deeper than 8**: the initial HTML embeds `g_sGcContinueToken = '<n>'` (and `g_sessionID`); further pages are fetched with `?tab=…&continue_token=<n>&sessionid=<sid>&ajax=1`, which returns JSON `{html, continue_token}`. So the reachable depth is bounded by Valve’s demo retention, **not** by the GC’s 8-slot list.
* **Auth**: a Steam **web session**. `claabs/cs-demo-downloader` obtains it with `steam-session` (`LoginSession`, `EAuthTokenPlatformType.WebBrowser`) using account name + password + TOTP (`steam-totp`) — and then persists the **refresh token**, reusing it on later runs; the same refresh token also feeds `steam-user` in the bot mode. In a browser-first design, the equivalent is reusing the user’s existing `steamLoginSecure` cookie via a local helper rather than storing a password.
* **Reference implementation**: `claabs/cs-demo-downloader` (master branch; v1.2.0 in tree, last push reported 2026-08-04), Docker image, `cronSchedule` (default hourly) + `runOnStartup`; it parses the DOM with jsdom (the parser cites Leetify’s own `leetify-gcpd-upload` DOM parser as inspiration), downloads with `axios` stream → `unbzip2-stream` → atomic `rename`, sets the file mtime to the match date, and skips matches whose target filename already exists. It also keeps a `lastContinueToken` watermark so re-runs only page back to the last seen point.
* **Status: [Demonstrated]**, running in production form today. Caveats: HTML/selector fragility (any Steam Community markup change breaks the parse — the parser even bails out when a row lacks a date in the expected format), it is a Steam Community page rather than the documented Web API (so the 100k-call ToU budget does not literally apply, but website automation of Valve properties is still outside any published contract — and it is the same mechanism Leetify ships to users via its browser extension).
* **Practical consequence for design**: GCPD is the cheapest *unattended* Valve source (no Steam client running, no CS2 install, no GC contention). Combined with the GC path it gives redundancy: GCPD for breadth, GC for freshness/low-latency.
* **Contract vs capability tradeoff** (recorded as a tradeoff, not a recommendation): the **GC route is more defensible** — it is what the game client itself does, it needs no credential beyond the user’s local Steam session, and no HTML scraping; the **GCPD route is more capable** (any depth, headless) but is website scraping of a Valve property with no published contract and a brittle DOM dependency. Pick per risk appetite; a design that keeps GCPD as an *optional adapter* and GC + folder-watching as the baseline gets both.
* **What the two numbers in a replay URL are (corrected, evidence-based).** Measured against `akiver/cs-demo-manager`’s `src/node/valve-match/fixtures/*.dem.info` — each fixture carries the URL that produced it — the name/URL relationship is exact in **5 of the 6** fixtures with a detectable URL:

  | fixture name (built by CS:DM as `match730_<reservationId:21>_<tvPort:10>_<serverIp>`) | embedded URL |
  |---|---|
  | `match730_003189280594026561777_1796106830_900` | `http://replay900.valve.net/730/003189280594026561777_1796106830.dem.bz2` |
  | `match730_003189870870709403769_1988138084_900` | `http://replay900.valve.net/730/003189870870709403769_1988138084.dem.bz2` |
  | `match730_003496718345246343373_0093428724_190` | `http://replay190.valve.net/730/003496718345246343373_0093428724.dem.bz2` |
  | `match730_003498492722937856210_1557600280_214` | `http://replay214.valve.net/730/003498492722937856210_1557600280.dem.bz2` |
  | `match730_003668537425296097309_2104686856_273` | `http://replay273.valve.net/730/003668537425296097309_2104686856.dem.bz2` |
  | (outlier) `match730_003668313874395824202_1729175012_271` | `http://replay273.valve.net/730/003668148000611369297_1331187857.dem.bz2` — neither pair nor host agrees; evidently a mislabelled/copied file |

  **Layout: `replay<server_ip>.valve.net/730/<reservation_id>_<tv_port>.dem.bz2` — confirmed at field level, not just by string agreement.** Parsing the fixture bodies as protobuf (`CDataGCCStrike15_v2_MatchInfo`) shows `watchablematchinfo.server_ip` = the host number and `watchablematchinfo.tv_port` = the second component — e.g. `…_1729175012_271` aside, for `…_1662707805_136`: `server_ip = 136`, `tv_port = 1662707805`; for `…_1796106830_900`: `server_ip = 900`, `tv_port = 1796106830`. (Independently reproduced by peer agent `EcosystemSurvey.ApisData` with its own varint walker, 2026-10-15; the same parse finds `roundstatsall[].reservationid` = the URL’s first component and `roundstatsall[].map` = the URL string itself — i.e. field 1 / field 3 of `CMsgGCCStrike15_v2_MatchmakingServerRoundStats`, matching the proto in §2.1.)
* **Padding is load-bearing — never normalise a replay URL.** `tv_port = 93428724` appears as `0093428724` in *both* the CS:DM filename and Valve’s URL (`…/003496718345246343373_0093428724.dem.bz2`); the host and id components are zero-padded too. Download the URL string verbatim.
* **The match id is not in the URL at all**, and the tv-port question is now closed in the negative rather than left open: the share code physically lacks the bits for a 31-bit tv port (§2.1), so the share code and the URL cannot be joined on that field. The only viable *id-based* join between a share code/GC record and a replay URL is `reservationId`.
* **Consequences.** (a) Never construct a replay URL — always take it from GC/GCPD. (b) The only viable *id-based* join between a URL and a share code/GC record is `reservationId` (present in both, at full 64-bit width in the share code); `matchid` must come from GC/`.dem.info`, and `tvPort` must not be used as a join key. (c) Valve documents none of this, one fixture disagrees, and the format may change again — so the pipeline keeps a **content-hash** reconciliation key rather than trusting ids (§3.1). (d) Corroboration that no shipped client relies on URL parsing for identity: `claabs/cs-demo-downloader` never equates GCPD-derived ids with share-code/GC ids (GCPD mode dedupes on URL + `lastContinueToken` watermark; only auth-code mode compares share-code `matchId` with GC `match.matchid`) — it uses the URL only as a filename/dedupe handle.

### 2.3 How to hold a GC session (three viable mechanisms)

| Mechanism | Credentials needed | Requirements | Status |
|---|---|---|---|
| **Local Steam client + Steamworks SDK** — `akiver/boiler-writter` (C++, based on *Boiler*) writes the raw `CMsgGCCStrike15_v2_MatchList` protobuf to a file. Takes optional `matchId outcomeId token` args for a specific match. | none (uses the running Steam client’s logged-in session) | Steam running + logged in on the same machine; CS2 installed; CS:DM “will briefly launch CS2 in the background automatically to fetch data”; prebuilt binaries for Win/Linux/macOS published | **[Demonstrated]** — shipped in CS:DM |
| **`node-steam-user` + `globaloffensive`** (Headless bots) — `client.logOn(...)`, `client.gamesPlayed(730)`, then `csgo.requestRecentGames(steamid)` / `csgo.requestGame(shareCode)`; `connectedToGC` event gates all calls | Steam login (refresh token / credentials) | nothing else | **[Experimental]** — `globaloffensive` v3.3.0 published **2026-03-17**, `steam-user` v5.3.0 **2025-12-04** ⇒ maintained; but credentials-on-disk and ToS friction |
| **In-game client (manual)** — Watch → Your Matches → Share/Download | none | user clicks | **[Demonstrated]** — writes `.dem` + `.dem.info` to `…/game/csgo/replays/` |

CS:DM UX facts worth copying (they are the failure surface): “Steam must be running and connected to your account”; “CS2 will be briefly launched in the background”; “You are already connected to the CS game coordinator” = account in-game elsewhere; Steam restart required in some states; **Flatpak Steam is unsupported on Linux**; only the currently logged-in Steam account’s matches are visible.

### 2.4 Local file locations (for a folder-watching strategy)

* CS2: `…/steamapps/common/Counter-Strike Global Offensive/game/csgo/` (root demo folder) and `…/game/csgo/replays/` (downloaded matchmaking replays). CS:DM defaults its demo folders and its download folder to these two (`get-default-counter-strike-folders.ts`, CS:DM log line: `Starting game with command "... +playdemo "E:/Steam/.../game/csgo/replays/1-…-1-1.dem""`). **[Demonstrated]**
* Files downloaded by the game client ship with a **`.dem.info` sidecar** = serialized `CDataGCCStrike15_v2_MatchInfo`, which itself contains the demo URL, match time, reservation id, tv port, server ip, player SteamIDs and per-player round stats. Sidecars are also a *de facto* “already downloaded” marker (CS:DM treats `demo + info` pair as `Downloaded`).
* Naming convention for Valve demos: `match730_<reservationId:21 zero-padded>_<tvPort:10 zero-padded>_<serverIp>` — and this is exactly the triple the replay URL encodes (`replay<serverIp>/730/<reservationId>_<tvPort>`), confirmed in 5 of 6 fixtures (§2.2).
* Steam download failure modes seen in the field: “Download incomplete”, “download container is corrupt”, and a stale `.dem.info` making the client report “Match demo has expired” for a demo that is still on Valve’s servers (workaround: move the `.dem.info` away and retry).

### 2.5 Claimed availability window

* CS:DM (current docs): “The demo’s download link for a match expires **1 month** after the match ends.” Leetify (2024-02): “as of writing, these links expire after 30 days” (Valve *and* FACEIT). Some guides report shorter windows. Valve publishes **no** retention guarantee → treat ~30 days as an empirical budget, capture fast, and treat a 404 as terminal. **[Demonstrated empirically / not documented by Valve]**

### 2.6 Valve limits and policy

* Steam Web API ToU (<https://steamcommunity.com/dev/apiterms>): **max 100 000 API calls/day**; key must stay confidential and is personal to you; may not “create or assist third parties … [in] any technology or functionality that may give a user an unfair competitive advantage when playing multiplayer versions of any Steam game”; Valve may suspend/terminate access at any time without notice. For a private self-coaching tool consuming *your own* demos this is a defensible position, but it is a clause to keep in mind before productising anything.
* Rate limiting on `GetNextMatchSharingCode` is explicit in Valve’s own doc (“strict rate-limiting … should be prepared to handle 429/503”), plus the 503-amplification trap for invalid `steamidkey`.
* GC side: one GC session per Steam account; a session is taken when the account plays elsewhere; Valve can require a Steam restart; the write-capable client path effectively needs the game on the same machine (or a headless Steam login).

---

## 3. Pipeline design (acquisition layer)

### 3.1 Reference data model

```
source        : FACEIT | VALVE
match_key      : "faceit:1-<uuid>" | "valve:<matchid>"            -- primary dedupe key
sub_key        : "" | "<reservationId>"                           -- multi-part matches (GC `outcomeid` slot)
demo_url       : resolved URL (expiring)
url_acquired_at, url_expires_at (if derivable)
state          : see 3.2
attempts, last_error_class, next_attempt_at
file_sha256    : hash of the *decompressed* .dem (content dedupe)
bytes, duration_s, map_name, played_at, players[]
artifacts      : { dem_path, info_path?, parsed? }
```

Dedupe keys, in order: (1) `source + match_id` — the only stable identity both platforms give you; (2) **content hash of the decompressed demo stream** as a global unique index (CS:DM does exactly this: demo checksum with a unique constraint, plus a separate `download_history(match_id)` table). The content hash also catches the “same demo re-downloaded through two paths” case (e.g. Chrome download + in-game download) and the FACEIT/Valve duplicate for the same physical match if you play both.

**Cross-surface caveat (Valve).** `source + match_id` is only as good as the identifier each surface hands you. The GC gives a real `matchid`; a GCPD row gives a URL that encodes `reservationId` + `tvPort` but **not** `matchid` (§2.2), while a share code carries `matchId` + `reservationId` + a lossy 2-byte `tvPort`. So the only viable id-based bridge between a replay URL and a GC/share-code record is `reservationId`; `matchid` is absent from the URL. Concretely: key GC-sourced records on `matchid`, key GCPD-sourced records on the URL digest (with `reservationId`, when arrived at, stored as an attribute), and make the **decompressed-demo content hash the single authoritative reconciliation key** that collapses GC-, GCPD-, in-game-download- and manually-dropped copies of the same match into one record. FACEIT has no such ambiguity — `1-<uuid>` is stable across API, download and file name.

### 3.2 State machine

```
DISCOVERED ─▶ PENDING_DEMO ──(url available)──▶ QUEUED ─▶ DOWNLOADING ─▶ VERIFYING ─▶ DECOMPRESSED ─▶ PARSE_QUEUED ─▶ DONE
                  │                                ▲            │
                  ├─(window elapsed, no url)─▶ UNAVAILABLE      ├─ 404/403 URL-level ─▶ EXPIRED_URL ─(re-resolve)─┘
                  └─(auth/quota failure)────▶ AUTH_BLOCKED      ├─ 4xx auth ─▶ AUTH_BLOCKED (halt + surface to user)
                                                                ├─ 429/503/5xx/timeout ─▶ RETRY_WAIT (backoff)
                                                                └─ hash/decompress failure ─▶ CORRUPT (quarantine file)
```

* `PENDING_DEMO` is a **first-class state**, not an error: FACEIT’s `demo_url` can be absent for a while after the match ends (docs: “when available”), and Valve’s GC can return a match before its demo is processed.
* `EXPIRED_URL` must never be retried with the same URL — re-resolve the URL from the source (FACEIT: re-read `demo_url`; Valve: re-request GC) before retrying.
* Terminal-vs-retryable classification is HTTP-status driven and mechanical: `404` → expired (terminal, but see above), `401/403` → auth (halt the whole source, notify), `429` → honour `Retry-After`, else exponential backoff with jitter, `5xx`/socket timeout → backoff, decompression/checksum mismatch → corrupt (bounded retries, then quarantine + report).
* Idempotency: one worker per `match_key`; a durable job row per match; the download lands on a temp path (`*.part`) and is `rename()`d only after decompression + hash succeed (atomic cutover). A queue entry is only cleared when the parsed-demo row exists.

### 3.3 Triggers / scheduling

| Trigger | Platform | Mechanism | Notes |
|---|---|---|---|
| **Game exit** | Valve | poll the CS2 process every ~30 s; when it transitions running→stopped after a ≥20 min session, run the GC fetch | CS:DM does exactly this (`listen-for-counter-strike-closed.ts`, 30 s poll, 20 min minimum runtime gate) — it avoids the “you are already connected to the CS game coordinator” conflict and avoids downloading while bandwidth/GC are needed |
| **Post-session / interval poll** | FACEIT | after a session or on a 5–10 min timer: `GET /players/{id}/history?game=cs2` → diff `match_id`s → `GET /matches/{id}` for new ones | cheap: 1 history call per poll; match-detail calls only for unseen ids |
| **GCPD poll (cron)** | Valve | hourly (or on game exit): load `steamcommunity.com/my/gcpd/730?tab=<premier\|competitive\|wingman\|scrimmage>` with the stored web session, page back via `continue_token` until `lastContinueToken` watermark, collect `replay*.valve.net` URLs | no Steam client, no CS2, no GC contention, no 8-match cap; watermark prevents re-paging (pattern: `claabs/cs-demo-downloader`) |
| **Re-resolve sweep** | both | every N minutes, for rows in `PENDING_DEMO`/`EXPIRED_URL` inside the availability window | FACEIT: bounces back once the demo finishes uploading; Valve: GC/GCPD-driven |
| **Folder watcher** | Valve (and FACEIT files dropped by hand) | watch `…/game/csgo/replays/` (and the user’s Downloads dir) for `*.dem`/`*.dem.info`/`*.dem.zst`; settle by size-stability check | zero credentials, zero GC, catches the manual path automatically |
| **Native-messaging handoff** | FACEIT | browser extension posts the presigned URL (or the finished file path) to a local daemon | the only real “automation” available to a non-partner today; also the mechanism Leetify/CSNades/FACEIT-Vision use |
| (optional) **Webhook** | FACEIT | `match_demo_ready` → fetch match → demo_url | needs a public HTTPS endpoint; not local-first friendly without a tunnel |
| **Parser handoff** | both | DONE → enqueue parse job | parse workers are CPU-heavy; do not co-schedule with downloads |

Concurrency policy: **1–2 concurrent downloads**, one per host; never download while CS2 is running; never run GC fetches while the game is running.

### 3.4 Download mechanics

1. Resolve URL (FACEIT: `demo_url[0]` → `POST /download/v2/demos/download`; Valve: GC `map` string as-is).
2. `GET` with streaming read, `Accept-Encoding: identity` (the payload is already compressed), `Range` resume only if the server advertises support; keep the query string byte-exact for signed URLs.
3. Decompress **on the stream** (`zstd` | `gzip` | `bzip2`; `zip` → single-entry extract), writing directly to the temp `.dem`.
4. Compute `sha256` during decompression; verify the archive’s own integrity signal implicitly by letting the decompressor error (bz2/gzip have CRC32; zstd has optional content checks).
5. Validate the demo header (first bytes / magic) before committing; then atomic rename into the canonical path `demos/<source>/<match_key>.dem`; write `meta/<match_key>.json`; keep Valve `.dem.info` when supplied.
6. Insert the dedupe row (`match_key`, `file_sha256`) and enqueue for parsing.

Bandwidth/storage arithmetic: a CS2 match demo is roughly 200–500 MB decompressed (compressed `.bz2`/`.zst` typically ~1/3). At 1 match/day that is ~100–200 GB/year → decide retention up front (e.g. keep demos for N days, keep derived features forever).

### 3.5 Rate-limit budget

| Call | Volume for 1 user | Constraint |
|---|---|---|
| FACEIT history poll | 1 per 5–10 min while active | undocumented 429; cache; single-flight |
| FACEIT match detail | 1 per new match; retries while `demo_url` empty | cap retries (e.g. every 2 min for 30 min, then hourly for the 30-day window) |
| FACEIT downloads API | 1 signed URL per demo (short-lived → immediate use) | gated credential; no published quota |
| Valve GC | 1 request per match-finish event (batch: one `MatchList` covers 8 matches) | GC session contention, not quota |
| `GetNextMatchSharingCode` | ≤ a handful per hour | “strict” rate limiting; 429/503; 100 k/day Web API cap; 503 amplification on bad `steamidkey` |
| Steam player-name/avatar enrichment | 1 per new player (batched `GetPlayerSummaries`, 100 ids/call) | 100 k/day |

### 3.6 Failure modes to design for (the ones that will actually happen)

**Valve**
* Steam not running / not logged in; CS2 not installed; **Flatpak Steam** (unsupported by the reference tool).
* “You are already connected to the CS game coordinator” — account in-game on another machine; requires closing the game there and restarting Steam here.
* Steam restart required mid-flow; GC messages time out.
* **Only 8 matches** — anything older silently disappears from the list.
* Share-code cursor older than 1 month → **412** (stop, ask user for a fresh code); invalid `steamidkey` → **403**, and repeated bad attempts → **503 for everyone**.
* Replay URL 404 after ~30 days → terminal. Stale `.dem.info` causing a false “Match demo has expired”; client-side “download incomplete/corrupt”.
* Replay hosts are plain HTTP and per-region; a specific `replayNNN` host can be slow/unreachable → retry elsewhere via re-resolution is not possible (URL is host-specific).

**FACEIT**
* Downloads API not granted (most likely outcome for an individual) → entire automatic path unavailable.
* `demo_url` empty until FACEIT finishes uploading; may stay empty for particular matches.
* Presigned URL expires quickly → cannot queue URLs; resolve → download must be near-atomic.
* Historic demo URLs (`*.backblaze.faceit-cdn.net`) not resolvable publicly → never assume `demo_url` is fetchable; always exchange it.
* 30-day retention → matches not captured are gone.
* Webhook needs public infra; undocumented payload schema → log-first.
* Policy: internal APIs prohibited; website automation is out of contract; account-level risk.

**Shared**
* Partial downloads, corrupt archives, demo truncated mid-round (parse-side failure, out of scope here but it is the same class).
* Two writers for the same match (extension + GC + manual) → must be resolved by `match_key` + content hash, not by path.

---

## 4. Alternatives where acquisition is restricted

* **FACEIT Match Insights** (Premium, launched 2026-04-22): round-by-round 2D radar with kill/death coordinates, utility detonations, ADR/entry timeline — in the browser without a demo. No public API documented ⇒ **not integrable**, but it is the pragmatic fallback for “post-match review” and a strong hint of where FACEIT wants analysis to live.
* **Third-party analysis upload paths**: Leetify’s `POST /api/faceit-demos/submit-demo-download-url` (2025-08-04) accepts a presigned FACEIT URL and returns a match id. Useful as a reference for the extension→local handoff shape; not an acquisition source in itself.
* **Third-party commercial APIs**: e.g. better-cs-api.com advertises “FACEIT API: download demos without … restrictive limits” plus HLTV access (<https://better-cs-api.com/docs>). Works-around the gate; unknown provenance, ToS/ToS-adjacent risk, and the usual API-key/uptime dependency. **[Plausible-untested]**
* **Other platforms are easier than FACEIT/Valve** — CS:DM ships downloaders for 5EPlay, Perfect World Arena, Renown; `cs-demo-downloader` (pypi v1.3.0, MIT) implements 5EPlay + PWA + Steam share-code sources for exactly this reason. If the user also plays elsewhere, those paths are cheaper than FACEIT’s.
* **Valve demos from third-party archives**: HLTV (pro matches) and the in-game client remain the only sources once Valve’s ~30-day window closes.

---

## 5. Category table (per claim)

| Claim | Category |
|---|---|
| FACEIT Data API returns `demo_url`, requires Downloads API to exchange it for a signed URL | **Research-supported** (official docs + OpenAPI) |
| FACEIT Downloads API access is gated by application (≈30-day expected review) and, in practice, commercially priced | **Demonstrated** (docs + CS:DM + Leetify’s €270k/yr account) |
| FACEIT `match_demo_ready` webhook exists for User-scoped subscriptions; payload shape undocumented; community uses `payload.id` | Research-supported (event exists) / **Plausible-untested** (payload) |
| FACEIT demos are retained ~30 days | **Demonstrated** (support article + Leetify) |
| FACEIT browser “Watch demo” = short-lived S3/Backblaze presigned URL | **Research-supported** (Leetify’s published example with SigV4 fields) |
| FACEIT internal-API use prohibited | **Research-supported** (Organizer CoC; ToS secondary) |
| Valve demo URL comes only from the GC (`roundstatsall[].map` since CS2) | **Demonstrated** (proto + CS:DM code + fixtures) — *plus* the GCPD web page, which is the second, independent source |
| Valve GC exposes only the last 8 matches | **Demonstrated** (CS:DM docs; consistent with every report). Scoped to the GC: the GCPD page is not capped at 8 |
| GCPD page (`steamcommunity.com/my/gcpd/730`) exposes per-queue match history with direct `replay*.valve.net` demo links and `continue_token` pagination | **Demonstrated** (`claabs/cs-demo-downloader` `src/gcpd.ts`, v1.2.0 tree, last push reported 2026-08-04; unauthenticated request 302s to Steam login — verified 2026-10-15) |
| GCPD mode fetches demos older than the GC’s 8-match window, bounded by demo retention | **Plausible-untested** — implied by pagination + `finished` stop-on-missing-URL logic; the exact depth was not measured here |
| Share code layout = 8 B `matchId` ‖ 8 B `reservationId` ‖ 2 B `tvPort`, fields sourced from `CDataGCCStrike15_v2_MatchInfo` | **Research-supported** (`akiver/csgo-sharecode` v7.0.1 `src/match.ts`, 2026-10-05) |
| Share-code `reservationId` ≡ GC `outcomeid`, `tvPort` ≡ GC `token` | **Functionally supported inference** (cs-demo-manager’s working share-code→boiler argument mapping; no Valve documentation) |
| Replay URL layout = `replay<server_ip>.valve.net/730/<reservation_id>_<tv_port>.dem.bz2`; `matchid` absent | **Demonstrated** — filename/URL agreement in 5 of 6 CS:DM fixtures (1 outlier) **plus field-level protobuf verification**: `watchablematchinfo.server_ip`/`tv_port` equal the host/second component, `roundstatsall[].reservationid` = first component, `roundstatsall[].map` = the URL (2 independent parses: this slice + `EcosystemSurvey.ApisData`, 2026-10-15) |
| Share-code `tvPort` cannot carry a 31-bit replay tv port (fixed 18-byte container split 8+8+2; `int16ToBytes` masks to 16 bits) | **Research-supported** — and demonstrated by the library’s own README: encode example `599906796` vs decode example `55788`, and `599906796 & 0xFFFF = 55788` |
| Replay-URL components are zero-padded and must be used verbatim (`93428724` → `0093428724`) | **Demonstrated** (fixture `…_003496718345246343373_0093428724_190`) |
| `GetNextMatchSharingCode` semantics (200/202/403/412/429/503) and 1-month code freshness | **Research-supported** (Valve’s own wiki page + official 2023-08-31 release notes) |
| Local credential-free GC acquisition via the Steam client (Steamworks/Boiler) | **Demonstrated** (boiler-writter shipped in CS:DM) |
| Headless GC via `node-steam-user` + `globaloffensive` | **Experimental** (libs actively maintained 2025–2026; credential handling required) |
| Valve demo retention ~30 days | **Demonstrated empirically**, not documented by Valve |
| Fully unattended FACEIT acquisition for a non-partner | **Infeasible** within policy |
| Recovering demos older than the respective 30-day windows | **Infeasible** on both platforms |

---

## 6. Open items to settle empirically (cheap experiments, no code needed yet)

1. **FACEIT presigned URL TTL**: read `X-Amz-Expires` off one real “Watch demo” URL from a logged-in session (determines how aggressively the resolver must be scheduled).
2. **FACEIT `demo_url` behaviour today**: confirm, with a real API key, whether `/matches/{id}` still returns `demo_url` for a normal user’s recent match and whether the returned host is resolvable (2024 evidence says the legacy Backblaze host was dead).
3. **`match_demo_ready` payload**: subscribe with a throwaway public endpoint and log one payload (settles both shape and latency vs `match_status_finished`).
4. **GC 8-match list stability**: confirm whether Wingman/Premier entries share the same 8-slot budget.
5. **GCPD depth and staleness**: with a logged-in web session, page `?tab=matchhistorypremier` to exhaustion and record (a) how far back the list reaches, (b) whether rows stop carrying `replay*.valve.net` links at Valve’s ~30-day retention boundary, (c) whether a single `continue_token` chain is stable across runs, and (d) whether the `replay<NNN>` host number is stable per match (the fixture evidence in §2.2 says the host equals `watchablematchinfo.serverIp`, which is per-match, so a match served from `replay273` may later be unreachable if that cluster is retired).
6. **GCPD login durability**: confirm how long `LoginSession` refresh tokens / web cookies last for `steamcommunity.com` before re-authentication (2FA) is required — this decides whether the unattended Valve path needs human intervention monthly or quarterly.
7. **Whether current CS2 still honours the in-game console command** `csgo_download_match <share code>` (would give a credential-free path for matches dropped from the 8-slot list, still bounded by Valve’s retention).
