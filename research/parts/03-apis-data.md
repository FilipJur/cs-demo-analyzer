# 03 — Data-Access & API Layer (demo acquisition + match metadata)

**Scope.** How a *local-first* CS2 coaching system can programmatically (a) obtain demos and
(b) obtain match metadata, without a server farm. Covers FACEIT, Steam/Valve, GC/share-code
tooling, third-party aggregators, and pro-demo sources.
**Research date:** 2026-10-15. Recency window: 2024 → Oct 2026.
**Method:** primary sources only (live API specs fetched and parsed, repo `commits/` pages,
official docs). Where a claim rests on secondary sources it is labelled.
**Confidence tags:** `Demonstrated` (worked/observed in a primary artefact) · `Experimental`
(works but fragile/undocumented) · `Research-supported` (peer-reviewed or dataset-backed) ·
`Plausible-untested` · `Infeasible`.

---

## 0. Executive answer (read this first)

| Question | Verified answer |
|---|---|
| Can FACEIT Data API v4 give me a downloadable demo URL? | Only an **opaque private `demo_url` resource reference**; the actual bytes require the **Downloads API**, which is **application-gated (≤30 day review)**. `Demonstrated` |
| Does FACEIT expose positional / tick / per-round-event data? | **No.** Per-round + per-player stats are **untyped `string→string` maps** (`additionalProperties: {}`). No coordinates, no ticks, no events. `Demonstrated` (OpenAPI 2.0 spec parsed) |
| Can Steam Web API give me CS2 Premier match history? | **No.** There is no `GetMatchHistory` for AppID 730. The only CS2-relevant method is `ICSGOPlayers_730/GetNextMatchSharingCode`. `Demonstrated` |
| Can I get a demo without a CS2 client session? | **Yes — via the GCPD page**, which needs only a Steam **web session** (refresh token / `steamLoginSecure` cookie), no CS2 launch and no GC. The GC route additionally requires a Steam (bot) login. Decoding is offline either way. `Demonstrated` (302→login verified 2026-10-15; mechanism peer-verified) |
| Is the demo window unbounded? | **Partly.** The **~last 8** cap is a property of the **GC message**, not of Valve's storage. The **GCPD page paginates** via a continue-token, so reachable depth is bounded by **demo retention (~1 month)**, not by 8. Replay links **expire ~1 month** regardless. `Demonstrated` |
| How many independent Valve demo surfaces are there? | **Two**: (1) **GC** — credential-free-ish, but 8-cap unless a share-code cursor is refreshed monthly; (2) **GCPD** — full paginated history in the retention window, but HTML scraping behind a Steam web session. `Demonstrated` |
| Is there a maintained share-code library? | **Yes** — `akiver/csgo-sharecode` v7.0.1, pushed **2026-10-05**. `Demonstrated` |
| Is there any official Valve public demo API? | **No.** `Infeasible` |
| Best aggregate stat API for a hobby project? | **Leetify** — but its Developer Guidelines **forbid storing data**, which conflicts with local-first persistence. `Demonstrated` |
| Can I scrape HLTV for pro demos? | **Contractually prohibited** since ToS 2025-01-27 ("data mining or web scraping", "commercial exploit", "similar or competitive… service"). `Demonstrated` |

**Bottom line for a local-first design:** the only self-serve paths that yield real CS2 `.dem`
files at personal scale are **Valve's two surfaces** — GC (bot account + share code; 8-cap) and
**GCPD** (Steam web session; paginated, no 8-cap) — both restricted to *official
matchmaking/Premier* and ~1-month retention. **GC is the more defensible choice contractually;
GCPD is the more capable but is HTML scraping of a Valve page** (shipped by Leetify and `claabs`
regardless). FACEIT demos are technically obtainable but require an approved Downloads API token;
community tooling proves it is *one HTTP call* once approved. Everything else (HLTV, GRID,
PandaScore, Abios) is either prohibited, paid, or supplies aggregate data you could not derive
from the demo anyway. The original slice assumed a single Valve surface and an unavoidable 8-match
cap; that assumption is corrected in §2.3.2.

---

## 1. FACEIT

### 1.1 FACEIT Data API v4

| Field | Finding |
|---|---|
| **Name** | FACEIT Data API v4 (`open.faceit.com/data/v4`) |
| **What it does** | REST JSON read API for players, teams, hubs, championships, tournaments, matches, match stats, games, queues, leaderboards, rankings, search |
| **CS2 demo support (verified how)** | Match object carries `demo_url` as `array of string`. Verified by fetching and parsing `https://open.faceit.com/data/v4/docs/swagger.json` (2026-10-15). It is a **private cloud resource reference**, not a public file URL. |
| **Maintenance status** | Live and served on 2026-10-15. Spec version string `"4"`, `swagger: 2.0`, license `"Property of FACEIT LTD"`, 64 paths / 173 definitions. No deprecation notice on the Data API itself; only `GET /tournaments` is annotated *"Retrieve tournaments v1 (no longer used)"*. |
| **Architecture** | Single hosted REST service, Akamai/CDN-fronted, server-side or client-side API keys |
| **Data exposed** | `Match` = `match_id, game, region, status, scheduled_at, started_at, finished_at, best_of, round, competition_*, organizer_id, results, detailed_results, teams{→Faction}, voting, **demo_url[]**, faceit_url, instances[]`. `MatchStats` = `rounds[]` → `RoundStats{round_stats:object(any), teams[]→TeamStatsSimple{team_stats:object(any), players[]→PlayerStatsSimple{player_stats:object(any)}}}`. `PlayerStats{rating, skillLevel{average,range}, winProbability}` for ranking-type endpoints. `MatchHistory` items = `match_id, game_id, game_mode, match_type, finished_at, teams, results, faceit_url, organizer_id, competition_id/name/type, max_players, playing_players, region, started_at, status, teams_size` (**no `demo_url`**). |
| **Programmatic integration** | Easy. `curl -H "Authorization: Bearer $KEY" https://open.faceit.com/data/v4/matches/$MATCH_ID`. Pagination via `offset`/`limit`. Generated clients exist (`mconnat/go-faceit`, `mconnat/faceit_api` Py, `0xka13b/faceit-sdk` TS) — secondary source. |
| **Auth** | API key (Bearer). Two key classes: **server-side** and **client-side** (`docs.faceit.com/getting-started/authentication/api-keys`, read 2026-10-15). Separately, **FACEIT Connect** OAuth2 (PKCE auth-code flow) for acting *on behalf of a user*; discovery at `api.faceit.com/auth/v1/openid_configuration` (`docs.faceit.com/getting-started/authentication/oauth2`, read 2026-10-15). Data API keys work fine for a personal data-collection script. |
| **Rate limits** | **No numeric quota published.** Every endpoint in the spec documents a `429 Too many requests` response. The "40 req/s" figure circulates for the **separate CDP partner integration** (`docs.faceit.com/getting-started/partner-integration-guide/cdp-integration`), *not* the Data API — secondary source, treat as `Plausible-untested` for Data API keys. Budget ~1 rps and honour `Retry-After`. |
| **ToS / legal** | Data API is explicitly for "all publicly available information on faceit.com". FACEIT's Organizer Code of Conduct states organizers **must not use internal APIs**, only the Open API. Scraping `faceit.com` HTML / calling undocumented `api.faceit.com` endpoints should be treated as unauthorised. Developer Terms live at `developers.faceit.com/terms` (JS-rendered; text not retrievable by the fetch tool — **gap**). |
| **Open/closed + license** | Closed. `"Property of FACEIT LTD"` in the spec; no redistribution licence. |
| **Linux compat** | N/A (HTTP). |
| **Reusability** | High for *metadata*; the schema is machine-generated and stable. Reuse directly. |
| **AI real vs marketing** | N/A — deterministic stats API, not an AI product. |
| **Unsolved problems** | No positional/tick/event data. No bulk endpoint for "give me all matches with demos". No published rate limit ⇒ capacity planning must be empirical. No rate-limit headers documented. `demo_url` presence is match-dependent (not every match has one) — `[INFERENCE]` from schema optionality; not observed live. |

### 1.2 FACEIT Downloads API (the only route to FACEIT demo bytes)

| Field | Finding |
|---|---|
| **Name** | FACEIT Downloads API — `POST /download/v2/demos/download` |
| **What it does** | Exchanges a private cloud `resource_url` for a short-lived **signed** download URL |
| **CS2 demo support (verified how)** | `Demonstrated` from `docs.faceit.com/getting-started/Guides/download-api` (read 2026-10-15). Request `{"resource_url":"https://demos.faceit.com/csgo/1-cb038819-….dem.gz"}` → `{"payload":{"download_url":"<signed_url>"}}`. |
| **Maintenance status** | Live; docs page current. **Access is application-gated**: form at `https://fce.gg/downloads-api-application`, expected response **≤30 days**. |
| **Architecture** | Separate service + **separate access token** with an exclusive "Downloads API" OAuth scope (Bearer). Demo objects live in object storage (S3-compatible). |
| **Data exposed** | A signed URL valid for a short TTL. Container seen in the wild: **`.dem.zst`** on Backblaze B2 — Leetify's doc example (2025-08-04) shows `demos-europe-central-faceit-cdn.s3.eu-central-003.backblazeb2.com/cs2/1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-1-1.dem.zst?X-Amz-Algorithm=…&X-Amz-Signature=…`. Older docs example is `.dem.gz`. **Format migration gz→zst happened at some point between the two docs.** |
| **Programmatic integration** | Trivial *once approved*: 1 POST + 1 GET. |
| **Auth** | Exclusive Downloads-API-scoped access token. |
| **Rate limits** | Not published. `cs-demo-manager.com/docs/guides/downloads` states FACEIT granted **"a server-side API key with the maximum rate limit"** — implying tiers exist (`Demonstrated`, CS:DM docs read 2026-10-15). |
| **ToS / legal** | Fine for own matches; bulk/personal-data retention into a local DB is the same grey area as the Data API. Demos are the property of the platform/organizer. |
| **Reusability** | **This is the single most valuable FACEIT primitive for the project.** Third-party proof of feasibility: Leetify accepts the presigned URL directly (`POST api.cs-prod.leetify.com/api/faceit-demos/submit-demo-download-url`), and CS:DM built a backend around it. |
| **AI real vs marketing** | N/A. |
| **Unsolved problems** | 30-day gate = the project's critical path. No public SLA on signed-URL TTL. Whether approvals are granted to *personal* (non-commercial) apps is **unknown** — plan a fallback. |

> **Corroborating negative evidence:** `cs-demo-manager.com` (the most-established FOSS CS2 demo
> manager) **removed in-app FACEIT downloads** because of this change: *"FACEIT restricted demo
> downloads to a private API and provided us a server-side API key with the maximum rate limit.
> This requires us to set up and maintain our own backend service… There is no ETA for restoring
> in-app downloads."* — read 2026-10-15. This is the cleanest available proof that (a) the
> restriction is real and recent and (b) a third party with standing still needs a backend.

### 1.3 FACEIT Webhooks (`match_demo_ready`)

`Demonstrated` from `docs.faceit.com/docs/webhooks` + `…/Guides/download-api` (read 2026-10-15).
Event list includes `match_demo_ready`, `match_status_finished`, `match_object_created`, etc.
Subscription types: **Organizer / User / Game**; scopes: "My user", "Static list of other users",
"Static list of my organizers", "Static list of my games". Callback = your HTTPS endpoint, optional
header/query auth. **Ideal trigger** for a local ingest worker: webhook → fetch match → `demo_url` →
Downloads API → download → parse. Caveats: requires a **publicly reachable HTTPS endpoint** (a home
LAN box needs a tunnel/relay), and the payload schema for `match_demo_ready` is **not documented**
(design tolerantly). *This is a "reverse-direction" dependency that a strictly local-first design
should treat as optional.*

### 1.4 FACEIT "v1" (older API) and legacy surface

- `https://open.faceit.com/data/v1/...` appears in old wrappers (`AMPDevelopment/FACEITCSharp`) —
  **legacy base path**. There is **no official v1 documentation** on `docs.faceit.com` (sitemap
  fetched 2026-10-15 lists only `data-api`, `data-api/data`, `webhooks`, auth and partner guides).
  Status: **superseded, unsupported**; no formal shutdown date was found (`[INFERENCE]`: gradual
  retirement rather than a hard cutover).
- Inside *current* v4, `GET /tournaments` is literally titled **"Retrieve tournaments v1 (no longer
  used)"** — the list must come from `/championships` or `/search/tournaments`. `Demonstrated`.
- Other FACEIT products keep independent versioning: `api.faceit.com/auth/v1` (OAuth2),
  `api.faceit.com/account-integration/v1` (account linkage), `download/v2` (Downloads API).
  **Do not** assume a uniform `/v1 → /v4` rename.

### 1.5 FACEIT-published datasets

**None found.** No official public bulk demo corpus, no Kaggle/HF FACEIT demo dump. The
well-known public CS2 combat dataset (`CS2CD`, HF, CC BY 4.0, 795 matches / 52.6 GB) is scraped
from **csstats.gg** with `demoparser2` — explicitly **not** FACEIT. `Demonstrated` negative.

### 1.6 ⚠️ Explicit gap list — what the FACEIT API cannot give us

| # | Gap | Consequence for this project |
|---|---|---|
| 1 | **No positional data** (no X/Y/Z, no view angles, no per-tick state) | Cannot compute crossfire coverage, trade geometry, rotation distance, map-control heatmaps from the API. **Must parse the demo.** |
| 2 | **No event stream** (no kills, damage, utility, economy, bomb events as structured objects) | No first-blood timing, no utility exchange, no economy state from API — the round-level maps are opaque strings. **Must parse the demo.** |
| 3 | **`round_stats` / `player_stats` / `team_stats` are schema-less `object` (`additionalProperties: {}`)** | Field names/units are not contractual; FACEIT can change them silently. Any API-sourced metric needs defensive parsing + validation. |
| 4 | **No tick rate, no demo file metadata** | Cannot know tickrate/version before downloading; must read the `.info`/header after download. |
| 5 | **`demo_url` not exposed on `/players/{id}/history`** | Ingest = 1 history call + **N** match calls (rate-limit amplification). |
| 6 | **No bulk/batch match endpoint, no webhook replay** | Backfill of historical matches is O(N) sequential requests. |
| 7 | **No published rate limit** | Cannot size a local ingest budget a priori. |
| 8 | **No public demo bytes without a separate, gated token** (≤30 d review) | This is the single biggest schedule risk in the whole project. |
| 9 | **No utility/grenade data, no flash durations (API), no KAST/ADR breakdown by segment** | These are Leetify-*derived* metrics, not FACEIT-exposed. |
| 10 | **Demo does not include the coach's own POV/sprays or voice** | POV demos are a client-side recording, not an API artefact. |
| 11 | **No FACEIT demo for matches where the demo was never uploaded / expired** | Coverage is incomplete; the local store must tolerate missing demos. |
| 12 | **Cannot redistribute demo bytes or API-derived data** (spec licence: "Property of FACEIT LTD") | Any future sharing/sync feature is legally constrained. |

---

## 2. Steam / Valve

### 2.1 Steam Web API — interfaces actually relevant to CS2

**`ICSGOPlayers_730`** (`Demonstrated`: read `steamapi.xpaw.me/ICSGOPlayers_730`, 2026-10-15 —
generated from `GetSupportedAPIList` + client protobufs). Methods: **`GetNextMatchSharingCode`,
`GetPlayerProfile`, `GetPlayerProfileCoin`**. That's it.

- `GetNextMatchSharingCode/v1` params: `key` (Steam Web API key), `steamid` (SteamID64),
  **`steamidkey`** = the player's *"Access to Your Match History"* **Game Authentication Code**,
  `knowncode` = an already-known `CSGO-…` share code. Returns `{result:{nextcode}}`.
  Verified against `SteamTracking/SteamTracking`'s `API/ICSGOPlayers_730.json` (secondary-but-canonical).
- It is **undocumented by Valve** (absent from the official Web API reference) ⇒ `Experimental`.

**`IPlayerService`** (`Demonstrated`: read `partner.steamgames.com/doc/webapi/IPlayerService`,
2026-10-15). Methods: `GetRecentlyPlayedGames`, `GetSingleGamePlaytime`, `GetOwnedGames`,
`GetSteamLevel`, `GetBadges`, `GetCommunityBadgeProgress`. **No match history, no match details.**
`GetRecentlyPlayedGames` only proves "played app 730 in the last 2 weeks".

**`ISteamUserStats/GetUserStatsForGame`** — lifetime aggregate counters (kills, wins, etc.) for
`appid=730`. Not per-match. (secondary source: Steamworks reference + multiple confirmations).

**`ICSGOServers_730`** (`Demonstrated` list from xpaw): `GetGameServersStatus` (service health),
`GetGameMapsPlaytime`, `GetMonthlyPlayerCount`, `GetLeaderboardEntries`. **`GetMatchmakingStats`
does not exist as a Web API method** — verified negative. `GetGameServersStatus` returns
`services{SessionsLogon, SteamCommunity, IEconItems}, matchmaking{scheduler, online}` — useful as
a "is CS2 down?" pre-check, nothing more.

**`GetMatchHistory` / `GetMatchHistoryBySequenceNum` for 730: `Infeasible`.** These are
`IDOTA2Match_570` (**Dota 2**) methods; the interface name embeds the app id and is not
parameterisable. Valve's reference lists **no** CS2 match-history interface. `Demonstrated` negative.

**`SteamDatagramCertificate`:** **not a Web API.** It is a `SteamNetworkingSockets` artefact:
clients call `GetCertificateRequest()` → your GC signs via `SteamDatagram_CreateCert()` → client
`SetCertificate()`. `ISteamApps` exposes only `GetSDRConfig`. Irrelevant to a demo-analysis project.
`Demonstrated` (GameNetworkingSockets `isteamnetworkingsockets.h` + Steamworks SDR page).

### 2.2 Steam Web API Terms of Use — the clauses that matter

`Demonstrated` — read `steamcommunity.com/dev/apiterms` (still "Last updated July 2010", fetched
2026-10-15). Key restrictions:

1. **100,000 calls/day per key.** (Adequate for personal use; not for a shared service.)
2. *"You will only retrieve Steam Data about a Steam end user as requested by the end user."* —
   You may not crawl arbitrary users' data. **This forbids bulk player-scraping designs.**
3. Must post a privacy policy covering non-public end-user data and the countries where you store it.
4. Keep the key confidential; licence is personal to your Application.
5. *"You may not… create any technology… that may give a user an unfair competitive advantage when
   playing multiplayer versions of any Steam game."* — **This is the clause that makes a
   real-time in-match coaching overlay legally risky**, and it is a genuine constraint for a
   personal-coaching product. Post-match analysis is not "in-game advantage"; live assistance is.
6. Key-holder must not intercept/store the user's **Steam password**.
7. Valve may terminate at will, without notice.
8. Governor: Washington State law.

> **Design consequence:** account-scoped, opt-in data (`steamidkey` supplied by the user) sits
> comfortably inside the ToS. A "scrape everyone's matches" design does not.

### 2.3 Demo acquisition — two independent Valve surfaces (GC and GCPD)

#### 2.3.1 The Game Coordinator (GC) route

**Verified GC protocol surface** (primary source: `SteamDatabase/Protobufs`
`csgo/cstrike15_gcmessages.proto`, fetched 2026-10-15):

```proto
message CMsgGCCStrike15_v2_MatchListRequestFullGameInfo {
    optional uint64 matchid = 1;
    optional uint64 outcomeid = 2;
    optional uint32 token = 3;
}
message CMsgGCCStrike15_v2_MatchListRequestRecentUserGames { optional uint32 accountid = 1; }
message CMsgGCCStrike15_v2_MatchListRequestCurrentLiveGames { }
message CMsgGCCStrike15_v2_MatchList {                       // the reply
    optional uint32 msgrequestid = 1;
    optional uint32 accountid = 2;
    optional uint32 servertime = 3;
    repeated .CDataGCCStrike15_v2_MatchInfo matches = 4;
    ...
}
message CDataGCCStrike15_v2_MatchInfo {
    optional uint64 matchid = 1;
    optional uint32 matchtime = 2;
    optional .WatchableMatchInfo watchablematchinfo = 3;
    optional .CMsgGCCStrike15_v2_MatchmakingServerRoundStats roundstats_legacy = 4;
    repeated .CMsgGCCStrike15_v2_MatchmakingServerRoundStats roundstatsall = 5;
}
message WatchableMatchInfo {
    optional uint32 server_ip = 1;
    optional uint32 tv_port = 2;
    ...
    optional uint64 server_id = 11;
    optional uint64 match_id = 12;
    optional uint64 reservation_id = 13;
}
```

**Mapping the share code onto these messages** — `[INFERENCE]`, strongly supported but **not
independently verified**: `csgo-sharecode` decodes a match share code to
`{matchId, reservationId, tvPort}`, and `CMsgGCCStrike15_v2_MatchListRequestFullGameInfo` carries
`{matchid, outcomeid, token}` = the same arity/types from the same subsystem, while the reply's
`WatchableMatchInfo` exposes `{match_id, reservation_id, tv_port}`. The consistent reading is
`outcomeid ↔ reservationId` and `token ↔ tvPort`, i.e. the share code is a packed
`FullGameInfo` request and the reply's `WatchableMatchInfo` is what libraries surface as the GOTV
address. Two of the three names are identical (`matchid`/`matchId`, `outcomeid`←→`reservationId`
is the weak link). **No upstream doc states this mapping**; it is an equality-by-shape argument
between three separately-observed surfaces. Verify empirically (decode a known share code, send
it, compare ids in the reply) before relying on it.

**Tooling status:**

| Tool | Status (verified) | Notes |
|---|---|---|
| **`SteamRE/SteamKit2`** | **Active** — commits 2026-10-13/14 (proto generation, LZMA in depot chunks). `Demonstrated` (read `commits/master`) | The reference .NET Steam client-protocol library. **Not** a CS2 demo downloader; you generate protobufs from `SteamTracking/GameTracking-CS2` and speak GC yourself. Highest-quality foundation, heaviest integration. |
| **`DoctorMcKay/node-globaloffensive`** | **Low activity** — last commit **2026-03-17** (v3.3.0); prior release 2024-10-03. `Demonstrated` (read `commits/master`) | Node GC client. Scope is *inventory/items*; `requestGame(shareCode)` exists for match requests. Open issue #113 (Aug 2025) "outdated CS2 protobuf definitions". |
| **`sak0a/node-cs2`** | **Active fork** — 154 commits, "synced with GameTracking-CS2 **through September 25, 2026**". `Demonstrated` (read repo) | Drop-in `globaloffensive` replacement. **Self-declared AI-generated port with partial verification** ("Large portions of this library were generated with the assistance of AI… may not have been thoroughly tested"). Also item-centric. |
| **`mandreasen/CSGOCoordinator`** | **Dead** — CS:GO-era `node-steam` plugin, old protobufs | Do not use for CS2. `Demonstrated`. |
| **`Cludch/csgo-demodownloader`** | **Archived 2021-01-24**, v1.1.0 | Historical reference for the auth-code flow (README documents the exact config: SteamID64 + Web API key + match history auth code + known share code + separate bot account). Useful as *documentation of the flow*. |
| **`claabs/cs-demo-downloader`** | **Active** — pushed **2026-08-04**, 27 commits, Docker image `ghcr.io/claabs/cs-demo-downloader:latest`. `Demonstrated` (read repo) | **Best off-the-shelf component.** TS/Node, two strategies: **(a) GCPD mode** — log into Steam and scrape `steamcommunity.com/my/gcpd/730`; **(b) auth-code mode** — bot account + GC + user's match-history auth code (explicitly "like Leetify does"). Premier/competitive/wingman. |
| **`akiver/cs-demo-manager`** | Active (see part 05) | GC tab: "the last 8 Valve Matchmaking matches"; share-code download; **demo link expires 1 month after the match**; Linux: must **not** be a Flatpak Steam install. `Demonstrated` (docs read 2026-10-15). |

**Hard limits of the GC path (`Demonstrated`):**
- **Recent-game list = last 8 matches.** This is a property of the **GC message**
  (`CMsgGCCStrike15_v2_MatchListRequestRecentUserGames` → last 8), **not** of Valve's storage —
  see the GCPD surface below for a non-capped route. "Only the last 8 matches are available
  because the Steam Game Coordinator only provides this data" (CS:DM docs).
- **Replay URLs expire ~1 month** (true for both surfaces; demo retention, not an API limit).
- **One GC session per Steam account**, and it must be *the* account (or use a bot account +
  the user's auth code). If the account is in-game elsewhere, the session is refused.
- GC connection requires launching CS2 briefly (or emulating the ClientHello — `node-globaloffensive`
  explicitly "Send version and other stuff in ClientHello in accordance with real CS2 client").

#### 2.3.2 The GCPD page (second, independent surface — no 8-cap)

`steamcommunity.com/my/gcpd/730`. A Steam *Community* page listing that
account's matchmaking demos with download links. **This is a second, independent Valve surface,
not the GC**, and it is the more capable one:

- **Login-gated but no CS2 launch and no GC session.** Verified here 2026-10-15:
  `GET /my/gcpd/730?tab=matchhistorypremier` → `302 → /login/home/?goto=/my/gcpd/730?tab=matchhistorypremier`
  (and the same for the bare path). Authenticate with a Steam **web session** — `steam-session`
  `LoginSession` + stored refresh token, or an existing `steamLoginSecure` cookie. No Steam client,
  no bot account, no `gamesPlayed([730])`.
- **Tabs:** `matchhistorypremier`, `matchhistorycompetitive`, `matchhistorywingman`,
  `matchhistoryscrimmage`, `matchhistorycompetitivepermap` *(peer-verified; the tab param is
  demonstrably passed through by the redirect)*.
- **Rows carry the replay URL directly**, and the URL's components are now **identified, not
  guessed** (see the verification note below):
  `http://replay<server_ip>.valve.net/730/<reservation_id>_<tv_port>.dem.bz2`
  + `YYYY-MM-DD HH:MM:SS GMT` on the same row.
- ✅ **VERIFIED (own primary evidence, 2026-10-15): the URL is
  `replay<server_ip>.valve.net/730/<reservation_id>_<tv_port>.dem.bz2`.** Method: fetched
  `akiver/cs-demo-manager`'s 7 `.dem.info` fixtures
  (`src/node/valve-match/fixtures/`), parsed each as a protobuf, and compared the filename produced
  by CS:DM's `buildMatchName(reservationId, tvPort, serverIp)` against the replay URL **embedded in
  the file body**. Results:
  - 6 of 7 fixtures contain an embedded URL. **5 agree on all three components**, e.g.
    name `match730_003498492722937856210_1557600280_214` ↔
    URL `replay214/730/003498492722937856210_1557600280.dem.bz2`; name
    `match730_003189280594026561777_1796106830_900` ↔ `replay900/…/003189280594026561777_1796106830`.
  - **The protobuf fields independently confirm the semantics**, not just the string agreement:
    for the first fixture `watchablematchinfo.server_ip` = `136` and `watchablematchinfo.tv_port` =
    `1662707805`, matching the filename's 3rd and 2nd components and the URL's host index and 2nd
    component exactly. Same for `_1796106830_900` (server_ip `900`, tv_port `1796106830`).
  - 1 outlier (`…_1729175012_271` ↔ URL `replay273/730/003668148000611369297_1331187857`) shares no
    component ⇒ a **mislabelled/copied fixture**, excluded.
  - The fields now have **names, not just numbers** (verified against Valve's
    `cstrike15_gcmessages.proto`): in `CMsgGCCStrike15_v2_MatchmakingServerRoundStats`,
    **`field1 = reservationid` (uint64)** and **`field3 = map` (string)** — and that `map` string is
    literally where CS2 puts the **replay URL**. So `reservation_id` appears as
    `roundstatsall[].reservationid` (e.g. `3668537425296097309` = filename component 1) and the URL
    as `roundstatsall[].map` — i.e. **the `.info` file records its own provenance URL**, which is
    also exactly what CS:DM relies on (`const demoUrl = lastRoundMessage.map`). Two independent
    methods (my varint walk, CS:DM's typed decode) agree on the same wire field.
  - Consequence: **the URL's first component IS the 64-bit `reservationId`, the same value a share
    code carries as `reservationId`.** So URL ↔ share code *is* joinable — **via `reservationId`
    only**: `matchid` is absent from the URL entirely.
- ⚠️ **The 2nd component provably cannot come from the share code — CLOSED, in the negative.**
  This is now a *bit-budget* argument, not an observation. The share-code container is a fixed
  25-char / **18-byte** base-57 encoding, and `csgo-sharecode` splits it **8 + 8 + 2**, so the third
  field has a **hard 16-bit budget** (`int16ToBytes` masks to 16 bits; decode reads only bytes
  16–18). Meanwhile `watchablematchinfo.tv_port` is a **u32** whose observed values are
  1662707805 / 1796106830 / 2104686856 — all ≫ 65535. The library's own README proves the loss
  without noticing it: encode example `tvPort: 599906796` (30 bits) vs decode example
  `tvPort: 55788`, and **`599906796 & 0xFFFF = 55788` exactly** (arithmetic checked here;
  likewise `2104686856 & 0xFFFF = 63752` is what a round-trip would silently yield). So:
  **the share code cannot carry the replay URL's `tv_port`.** Consequence, unchanged and now
  evidence-backed: **never synthesise a replay URL from a share code** — take `reservationId` from
  the share code for the join, and get `tv_port` / `server_ip` from the GC reply, the `.dem.info`'s
  `roundstatsall[].map`, or the GCPD row.
- *Correction history:* an earlier revision asserted the pair was `(matchId, outcomeId)` — an
  unverified inference from notation, withdrawn. The `AcquisitionAutomation` slice then
  over-corrected to "URL carries no usable identity"; that is **also** withdrawn, replaced by the
  verification above (they matched a subset of the same fixtures after this exchange; our
  conclusions now converge on `reservationId`+`tvPort`+`serverIp`).
- **Paginated — so NOT 8-capped:** initial HTML carries `g_sGcContinueToken`; then
  `?continue_token=<n>&sessionid=<sid>&ajax=1` → JSON `{html, continue_token}`. The walk terminates
  at rows with no URL cell, i.e. reachable depth is bounded by **demo retention (~1 month)**.
- **Working reference:** `claabs/cs-demo-downloader` `src/gcpd.ts` (+ `src/steam.ts` for
  `steam-session` login, `src/download.ts` axios → `unbzip2-stream` → atomic rename). Its DOM parser
  credits **Leetify's `leetify-gcpd-upload`** parser — i.e. Leetify ships this same mechanism to end
  users via a browser extension.

Status: **undocumented HTML scraping of a Steam Community page** ⇒ out of contract *in spirit*
(though the ToS text does not name this page, and Valve's own client uses it), `Experimental`
technically, `Demonstrated` in practice by two independent shipped products.
**This is the most robust personal-scale ingest mechanism** — no GC message drift, no 8-cap,
no game launch — at the cost of being the most legally exposed.

### 2.4 Share codes and the "match authentication code"

| Item | Verified status |
|---|---|
| **`akiver/csgo-sharecode`** | **v7.0.1, pushed 2026-10-05**; 93 commits; MIT; ESM. `Demonstrated` (read repo + `commits/main`). |
| Match share-code format | **Still `CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx`** (5×5, 25 chars, `CSGO-` prefix). Decodes → `{matchId: bigint, reservationId: bigint, tvPort: number}`. `Demonstrated` (README example + `WatchableMatchInfo` cross-check). |
| **Crosshair** share codes | **Different container.** `legacy` = `CSGO-…` (CS2 **no longer accepts on import**); CS2 today emits **`CS` + no dashes** (e.g. `CSvbPubOq37zTGqtsPTP5QTrp5CB4xFXiKRLfzJsm49ZRe`). Formats: `legacy-v1`, `legacy-v3` (23/09/2026), `legacy-v4` (24/09/2026), **`cs2-v1` (30/09/2026)**. The `legacy` container is **closed**; the client rejects any version below 3. `Demonstrated` — this library is the single best-maintained evidence that **Valve mutates these formats on a weeks timescale** (three format changes in the last 3 weeks of Sept 2026 alone). |
| Other implementations | `ValvePython/csgo` (`decode`/`encode` → `matchid, outcomeid, token`; Python 2.7/3.4-era, maintained-ish); `Cludch/...utils` (Go, archived); `csgowtf/csgowtfd` (Go); C#/PHP/Java/browser ports, all ≥2023 and stale. **No maintained Rust crate found.** |
| **`boilerplate`** | **Not found.** GitHub repo search (2026-10-15, API) for `boilerplate csgo match` and `boilerplate sharecode` returns **0 results**; `csgo sharecode` returns 9 repos, none named boilerplate. `closest concept` = the **Game Authentication Code** (`steamidkey`, a.k.a. "Access to Your Match History") supplied by the user at `help.steampowered.com/…appid=730&issueid=128`. The term in the brief most likely means *repeated community copy-paste snippets*, not a library. `Demonstrated` negative. |
| **`steamid`** | Conversions (SteamID2/3/64) are trivial and available in every language (`xPaw/SteamID.php`, `ValvePython/steam/steamid.py`). Not a bottleneck. Note the API requires **SteamID64**, not `STEAM_x:y:z`. `Demonstrated` |
| **Older `matched`/`steam://` URL** | `steam://rungame/730/0/+csgo_download_match%20<SHARECODE>` and the console `csgo_download_match <SHARECODE>` both still exist in CS2 — but they require a **running game client**, so they are user-facing UX, not a headless automation path. `Experimental` (widely reported; not headless-verifiable here). |

### 2.5 Valve's stance

- **No public CS2 demo API. No public CS2 match API. No GC API documentation.** `Infeasible` —
  verified by inspecting the official Web API reference index (no CS2 match interface) and by the
  absence of any demo endpoint in any Valve property.
- Valve's ToS forbids building tech that gives unfair in-game advantage (§2.2 #5) and requires
  end-user-initiated retrieval. Valve reserves the right to kill any key at any time.
- **Practical reading:** post-match, account-scoped, user-consented analysis is the safe zone.
  Anything resembling a public "CS2 demo CDN" or live in-match coach is not.

---

## 3. Third-party aggregated APIs

### 3.1 Leetify Public API

| Field | Finding |
|---|---|
| **Verified endpoints** | `GET /v3/profile?steam64_id|id`, `GET /v3/profile/matches`, `GET /v2/matches/{gameId}`, `GET /v2/matches/{dataSource}/{dataSourceId}`, plus `GET /api-key/validate`. Read from the live OpenAPI **3.1.0** document (`api-public-docs.cs-prod.leetify.com/swagger.json`, fetched 2026-10-15). Server: `https://api-public.cs-prod.leetify.com`. |
| **Auth** | Optional API key via `Authorization: Bearer <key>` **or** `_leetify_key` header; key issued at `leetify.com/app/developer`. Unauthenticated requests work but with **"increased rate limits"** (Leetify's wording). |
| **Rate limits** | **No numbers published.** Only the FACEIT-demo-submit endpoint documents a 429 policy (wait **300 s**). `Plausible-untested` for the rest. |
| **Data exposed** | `ProfileResponse{privacy_mode, winrate, total_matches, first_match_date, name, bans[], steam64_id, id, ranks{leetify, premier, faceit, faceit_elo, wingman, renown, competitive[]}, rating{aim, positioning, utility, clutch, opening, ct_leetify, t_leetify}, stats{accuracy_enemy_spotted, accuracy_head, counter_strafing_good_shots_ratio, ct/t_opening_aggression_success_rate, ct/t_opening_duel_success_percentage, flashbang_*, he_*, preaim, reaction_time_ms, spray_accuracy, traded_deaths_success_percentage, trade_kill_opportunities_per_round, utility_on_death_avg}, recent_matches[], recent_teammates[]}`; `MatchDetailsResponse{id, finished_at, data_source, map_name, has_banned_player, team_scores[], stats[]→PlayerStats{steam64_id, name, mvps, preaim, reaction_time, accuracy*, shots_*, utility_*, flashbang_*, counter_strafing_*, spray_accuracy, total_kills, total_deaths, …}}`. |
| **Per-round data?** | **No.** All schemas are **aggregate match/player level**. No round array, no event stream, no positions anywhere in the spec. `Demonstrated` (full schema key enumeration). |
| **Demo access** | Only the *reverse* direction: `POST /api/faceit-demos/submit-demo-download-url` accepts **your** presigned FACEIT URL (2025-08-04 post, modified 2025-08-04) and returns Leetify's match id. **You push to them; they do not give you demos.** |
| **ToS — the killer** | Developer Guidelines (published **2025-07-20**, page modified **2025-12-17**), §6 **"Do not store data"**: *"we ask that you please refrain from storing any data sent by our API… Should you have stored data from us, and that data ceases to be available from the API, you must delete that data from any copies you have."* Also: mandatory "Data Provided by Leetify" logo/link, no renaming or rescaling metrics, no implying affiliation, Leetify may cancel/modify the API at any time. |
| **Verdict for this project** | **Integrate for enrichment only, never as the system of record.** The "no storage" rule is fundamentally incompatible with a local-first longitudinal DB (which is the whole point of the coaching system). Options: (a) use Leetify purely to *validate* locally-computed metrics in a session-scoped, non-persisted view; (b) ask Leetify for written permission; (c) ignore and compute the same metrics locally from demos. Option (c) is the honest one. |

### 3.2 Scope.gg

`docs.faceit.com`-style public API: **none**. `scope.gg/match-history/` markets automatic
Steam/FACEIT download + analysis as a *product*; no endpoint docs, keys, scopes or SDK
(`Demonstrated` negative by search, 2026-10-15). They clearly do GC + FACEIT ingestion
(`[INFERENCE]` — same mechanism Leetify documents). No partner/data-export program advertised.
**Ignore** (unless a partnership is negotiated).

### 3.3 csstats.gg / csgostats.gg

**No official public API.** Only third-party scraping wrappers (`parse.bot` marketplace listings,
which self-describe as unofficial). `csgostats.gg` is fed by *uploaded* share codes. The CS2CD
research dataset (52.6 GB, 795 matches, cheater labels, CC BY 4.0) scrapes csstats.gg with
`demoparser2` — evidence that the site is a legit source of *data* but not of a *supported API*.
**Ignore as an integration; optionally consume CS2CD as research data.**

### 3.4 Stratz

**Dota 2 only.** GraphQL API (`stratz.com`), Dota-specific schema; REST API was deprecated/migrated
to GraphQL. **No CS2 support of any kind.** `Demonstrated` negative. **Ignore.**

### 3.5 bo3.gg (and community wrappers)

Base `https://api.bo3.gg/api/v1` (undocumented, private-frontend API; requires browser-like
`Origin`/`Referer` headers). Wrappers: `tommhe14/CS2API` (Py), `bol10x/bol10` (REST proxy).
Endpoints for matches/teams/players/stats/transfers/streams; `discipline_id=1` = CS2.
**Esports metadata + broadcast stats only — no demos, no tick data.** Unstable/undocumented ⇒
`Experimental`. Useful only if you need *pro* fixture/team metadata to attach to pro demos.

### 3.6 HLTV

**Prohibited.** ToS **effective 2025-01-27** (`hltv.org/terms`, read 2026-10-15). §2.2: no
"commercially exploit the Website or any of its content"; no "conduct, facilitate or organize **data
mining or web scraping**"; no "construct and build a **similar or competitive** website, product, or
service". §3.2: business use needs a licence. Governing law: Denmark. Practical obstacles:
Cloudflare + IP bans (the `hltv` npm package — v3.5.0, ~3 years old — warns of exactly this).
Demo download limits were removed in 2022, but that was an *availability* change, **not** a grant of
redistribution rights. **Ignore for automation.** If pro demos are needed, prefer an
organizer-licensed route or a public dataset mirror (§4).

### 3.7 Commercial esports data vendors (GRID / PandaScore / Abios)

`Demonstrated` from vendor docs/pricing pages (2026-10-15), varying levels of verification:

| Vendor | CS2 data | Raw `.dem`? | Pricing | Rate limits |
|---|---|---|---|---|
| **PandaScore** | fixtures, match history, player/team stats, live frames/events, play-by-play; legacy `/csgo/` paths for CS2; Live Replay API (`POST live.pandascore.co/api/csgo/replay`) = **API replay of their processed frames**, not the `.dem` | **No** (documented as processed data) | Fixtures €0/game/mo; Historical **from €400/game/mo**; Live Basic **from €1,000/game/mo**; Live Pro custom | not published |
| **GRID** | official in-game data, live feeds, historical, prediction/stats feeds, structured events/state; **File Download API** exposes *GRID State (JSON)* + *GRID Events (compressed JSONL)* + "selected official files" | **Unconfirmed** — docs show state/events files, not generic CS2 `.dem`. Must be negotiated contractually. | custom quote (free non-commercial may exist) | n/a |
| **Abios** | live scores, tournament/team/roster/player, live + historical play-by-play, **player coordinates for supported games** | **No** | sales-led, no public price | **10 req/s, 20-request bursts**, ≤365 days history (per their packaging page) |

**Relevance:** none of these are demo sources. Abios is the only one advertising *player
coordinates* — i.e. it could substitute for demo parsing on *covered pro* matches only, at
enterprise pricing and tournament-dependent availability. **Ignore** for a personal project.

### 3.8 Miscellaneous commercial/skin APIs

- **steamwebapi.com** — CS2 **items/market/inventory/float** data, commercial use on paid plans,
  €20–€50/mo, e.g. 2 req/min free tier. **Not** a match-stats API. **Ignore.**
- **`@cs2watch/api`** (npm, v0.2.0) — demo → rendered MP4 clips (tick/round clips, multi-kill,
  POTG) via a typed TS client, credit-based. **Relevant only if the project wants video clips**;
  it consumes demos you supply. **Integrate-later / optional.**

---

## 4. Pro-demo sources & legal position

| Source | What it is | Status / verification |
|---|---|---|
| **HLTV per-match demos** | Events archive → event → match → *Rewatch → Demo download*. No bulk ZIP. | Exists and works manually; **automation prohibited** by ToS §2.2. `Demonstrated` |
| **HuggingFace `blanchon/cs2_dataset_demo_test`** | Mirrored HLTV `.dem` files + metadata + analysis JSON | `Demonstrated` listing; **redistribution legality is the mirrorer's problem, not a licence grant to you** |
| **HuggingFace `Vasy7777/cs2-demo-archive`** | ~113 GB community archive of pro CS2 demos | `Demonstrated` (reported size via `vast7777/cs2-demo-to-dataset`) |
| **`vast7777/cs2-demo-to-dataset`** | Pipeline: HLTV demos → per-round `events.parquet` + per-player `state.parquet` + video. Its README **advises getting HLTV links via a normal browser rather than bypassing anti-bot controls.** | Active-ish; honest about the constraint ⇒ good architectural reference |
| **CS2CD** (HuggingFace, DOI `10.57967/hf/5654`, CC BY 4.0) | 795 matches / ≈734.9 M rows / 52.6 GB; tick CSVs + event JSON; VAC-based `cheater` labels; from **csstats.gg** via `demoparser2`. Paper: Loo, Lužkov & Burelli, *AntiCheatPT* (arXiv 2508.06348, 2025) → 89.17 % acc / 93.36 % AUC. | `Research-supported`. Caveat: labels are noisy (VAC false negatives; only the VAC-positive subset was manually checked). **Processed data, not `.dem` files.** |
| **PureSkill CSDS** | >60,000 matchmaking + FACEIT matches, telemetry/timestamped events, AWS Data Exchange (sample on Kaggle) | `Demonstrated` listing; commercial marketplace |
| **BLAST / ESL / other organizer archives** | Not systematically public | `Plausible-untested` — would require organiser contact |

**Legal/licensing of pro demos (`Demonstrated` for the constraints, `[INFERENCE]` for the
characterisation):** demo files are recordings of Valve's game produced by the tournament organiser
or platform. HLTV's ToS does not grant a redistribution licence; "download limits removed" ≠
"licensed to mirror". Valve's demo EULA/ToS position is not explicit in any primary source located,
so treat bulk mirroring/redistribution as **legally unresolved** and keep everything local +
personal. The safest bulk-pro-data route that *is* licensed is a **CC BY 4.0 dataset (CS2CD)** or a
vendor contract.

---

## 5. Comparison table

| # | Item | CS2 demo bytes? | CS2 metadata? | Positions/ticks? | Auth | Rate limit (published) | Cost | Open? | Linux | Maintenance (Oct 2026) | AI real? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FACEIT Data API v4 | ❌ (ref only) | ✅ rich | ❌ | API key / OAuth2 | ❌ none (429 only) | free | Closed | ✅ | Live 2026-10-15 | n/a |
| 2 | FACEIT Downloads API | ✅ via signed URL | — | — | Scoped token (**gated**) | ❌ (tiers implied) | free (gated) | Closed | ✅ | Live | n/a |
| 3 | FACEIT Webhooks | — | ✅ trigger | ❌ | app config | n/a | free | Closed | ✅ (needs public HTTPS) | Live | n/a |
| 4 | Steam `ICSGOPlayers_730` | ❌ (share code only) | ⚠️ codes only | ❌ | key + **user auth code** | ❌ (100 k/day overall) | free | Closed | ✅ | Live, undocumented | n/a |
| 5 | Steam `IPlayerService`/`ISteamUserStats` | ❌ | ⚠️ playtime/lifetime | ❌ | key | 100 k/day | free | Closed | ✅ | Live | n/a |
| 6 | Steam GC (protobuf/SteamKit2) | ✅ GOTV URL | ✅ match info | ❌ | Steam login (bot) + CS2 launch | ⚠️ **8-cap is GC-message-specific**, 1-mo links | free | Open (SteamKit2) | ✅ .NET/Node | SteamKit2 **2026-10-14** | n/a |
| 7 | **GCPD page** (`/my/gcpd/730`) | ✅ direct `replay<server_ip>.valve.net/730/<reservation_id>_<tv_port>.dem.bz2` (components **wire-verified** — §2.3.2) | ⚠️ per-match | ❌ | Steam **web session** (refresh token / `steamLoginSecure`) | ❌ none; **paginated by continue-token ⇒ no 8-cap**, bounded only by ~1-mo retention | free | Scrape of a Valve page | ✅ | shipped in `claabs` 2026-08 + Leetify extension | n/a |
| 8 | `claabs/cs-demo-downloader` | ✅ | ⚠️ | ❌ | Steam login or bot+auth code | cron-driven | free | Open, Docker | ✅ | pushed **2026-08-04** | no |
| 9 | `akiver/csgo-sharecode` | ❌ | ✅ code ↔ ids | ❌ | none | n/a | free (MIT) | Open | ✅ | **v7.0.1, 2026-10-05** | no |
| 10 | Leetify Public API | ❌ (push-only) | ✅ rich aggregate | ❌ | key (optional) | ❌ none | free | Closed | ✅ | spec live 2026-10-15 | derived ML metrics, real |
| 11 | Scope.gg | ❌ | ❌ (no API) | ❌ | — | — | product only | Closed | — | n/a | marketing |
| 12 | csstats.gg / csgostats.gg | ❌ | ⚠️ via scrapers | ❌ | none official | — | free site | Closed | ✅ | steady | n/a |
| 13 | Stratz | ❌ | ❌ (Dota only) | — | — | — | free tier | Closed | ✅ | active (Dota) | n/a |
| 14 | bo3.gg | ❌ | ✅ pro fixtures | ❌ | none (private API) | ❌ | free | Closed | ✅ | active | "ai_predictions" field — unverified |
| 15 | HLTV | ✅ per match (manual) | ✅ | ❌ | Cloudflare | ❌ | free | Closed | ✅ | active | n/a |
| 16 | GRID / PandaScore / Abios | ❌ (GRID unconfirmed) | ✅ licensed | ⚠️ Abios coords | contract | Abios 10 rps | €400–1 000+/mo | Closed | ✅ | active | predictions = vendor ML |
| 17 | steamwebapi.com | ❌ | ❌ (skins) | ❌ | key | 2–40 rpm by tier | €20–50/mo | Closed | ✅ | active | n/a |
| 18 | `@cs2watch/api` | ❌ (consumes yours) | ❌ | ❌ | token/credits | credits | pay-per-clip | Closed | ✅ | v0.2.0 | render, not AI-analysis |
| 19 | CS2CD dataset | ❌ (processed) | ✅ research | ✅ **ticks** | none | n/a | free (CC BY 4.0) | Open | ✅ | published 2025 | no |
| 20 | Steam Web API ToS | — | — | — | — | 100 k/day | — | — | — | last updated 2010 | — |

---

## 6. Reuse / integrate / ignore verdicts

| Item | Verdict | Rationale |
|---|---|---|
| **FACEIT Data API v4** | **INTEGRATE** (metadata only) | Stable, free, machine-readable; the only source of your match list. Treat all `*_stats` maps as opaque and validate. |
| **FACEIT Downloads API** | **INTEGRATE — highest priority action item** | Submit the application **first** (≤30 d). Without it there is no FACEIT demo path for a local system. Design a fallback that degrades to "user downloads demo manually" (exactly what CS:DM does today). |
| **FACEIT Webhooks** | **INTEGRATE, optional** | Great trigger, but needs a public HTTPS endpoint ⇒ weakens "local-first". Make it an opt-in mode; default to polling `/players/{id}/history`. |
| **Steam `GetNextMatchSharingCode`** | **INTEGRATE** | Free, official-enough, the *only* sanctioned way to enumerate an account's own matchmaking history. Requires the user to paste their Game Authentication Code. |
| **`claabs/cs-demo-downloader`** | **REUSE (as component/container)** | Solves a genuinely hard problem (Steam web-session / GC login + GCPD pagination + cron + Docker) and is maintained (2026-08). **Prefer its GCPD mode**: no CS2 launch, no bot account, no 8-cap. Wrap it or lift `src/gcpd.ts` + `src/steam.ts`. |
| **SteamKit2** | **INTEGRATE if you build your own GC client**; otherwise ignore | Best-quality protocol layer; overkill for demo-download only. |
| **`node-globaloffensive` / `node-cs2`** | **INTEGRATE with caution** | Node is convenient; both are item-centric and sparse (`node-cs2` self-declares AI-generated partial verification). Verify the `requestGame`/match-list path yourself before depending on it. |
| **`akiver/csgo-sharecode`** | **REUSE** | Small, MIT, actively tracking Valve format churn — including three crosshair-format changes in Sept 2026. Pin the version; watch the repo. |
| **Leetify Public API** | **INTEGRATE — enrichment only, never persist** | Its "do not store data" rule is incompatible with a longitudinal local DB. Use for cross-checking metrics in-session, or write to Leetify, not read. |
| **Scope.gg / csstats.gg / Stratz** | **IGNORE** | No supported public API; Stratz is Dota-only. |
| **bo3.gg** | **IGNORE** (or OPTIONAL pro-metadata) | Undocumented private API, no demos. |
| **HLTV scraping / `hltv` npm** | **IGNORE — ToS violation** | Explicit "no data mining or web scraping" since 2025-01-27. |
| **GRID / PandaScore / Abios** | **IGNORE** for v1 | Enterprise pricing for data that does not replace a parser; revisit only if pro-coaching becomes a paid product. |
| **CS2CD / pro-demo mirrors** | **INTEGRATE as test fixtures / benchmarking corpus** | CC BY 4.0 tick-level data + a real paper is a free ground-truth set for validating your own parser and metrics. |
| **`@cs2watch/api`** | **IGNORE for v1** | Nice-to-have clip rendering; adds a paid external dependency. |

---

## 7. Cross-cutting notes (gaps, duplicate work, tensions)

**Tensions with the project's stated goal (local-first, API-powered):**

1. **Every demo path is either gated, expiring, or prohibited — but Valve is *not* 8-capped.**
   FACEIT = 30-day gate; Valve = two surfaces: **GC** (8-cap, CS2 launch, bot account) and **GCPD**
   (paginated, web session, no 8-cap) — both bounded by ~1-month retention; HLTV = ToS-prohibited;
   vendors = paid and don't give `.dem`. There is
   **no** "just fetch any CS2 demo via API" design. The system *must* be architected around
   **opportunistic ingest + user-supplied files** as a first-class input, not an edge case.
2. **"Local-first" vs webhooks**: the FACEIT `match_demo_ready` trigger assumes a public HTTPS
   endpoint. Either accept a relay, or poll — polling multiplies the undocumented rate limit.
3. **Persistence vs third-party ToS**: Leetify explicitly forbids storage; FACEIT's spec is
   "Property of FACEIT LTD"; HLTV forbids commercial exploitation. A local longitudinal DB built
   from FACEIT metadata + self-parsed demos is the *least* fraught design. Keep raw third-party
   API responses out of the permanent store where feasible; store *derived* facts you computed.
4. **The API layer cannot supply the coaching signal.** FACEIT gives no positions, no events, no
   per-tick anything; abstract `string→string` stat maps are the ceiling. **100 % of the
   interesting coaching metrics must be computed from the parsed demo.** The API layer's job is
   reduced to: *discover matches, fetch metadata, fetch the demo file.* Plan the architecture
   accordingly — the API client should be a thin, replaceable "ingest" module.
5. **Valve GC knowledge is undocumented and format-unstable.** Three crosshair-share-code format
   changes in the final 3 weeks of September 2026 (`legacy-v3`, `legacy-v4`, `cs2-v1`) is strong
   evidence that Valve mutates these wire formats on a **weeks** cadence. Any GC-level code needs a
   fast update path and a pinned-with-watch dependency.
6. **Steam ToS clause §5 ("unfair competitive advantage")** should be a written design constraint
   for any live/interactive coaching feature — worth an explicit product decision now, because it
   retro-fits badly.
7. **Container formats differ per source — plan the ingest decompressor as a pluggable stage.**
   FACEIT → **`.dem.zst`** (Zstd, on Backblaze B2); Valve GC/GCPD →
   **`.dem.bz2`** (`replay<NNN>.valve.net/730/<21-digit>_<10-digit>.dem.bz2`); HLTV/pro archives →
   plain `.dem` inside `.zip`/`.rar`/`.bz2`; many third-party tools accept either. The API layer
   must not assume one compressed container.
8. **Cross-surface identity: one join *is* available, but keep content hashing authoritative.**
   The project will hold at least four ID namespaces: **FACEIT** `match_id` (GUID), **Valve**
   `matchid` (uint64), **Valve `reservationId`** (uint64 — carried by the share code *and* by the
   GCPD replay URL, now wire-verified: §2.3.2), and **HLTV/bo3** ids for pro matches. So:
   - **`reservationId` is a real cross-surface join** between a Valve share code and a Valve replay
     URL. Use it as the *optional* id-based shortcut.
   - **`matchid` and the FACEIT GUID have no observed mapping to anything else.** Within Valve, the
     share-code↔`FullGameInfo`↔`WatchableMatchInfo` equivalence is still only shape-inferred
     (§2.3.1), and the share code's 16-bit `tvPort` provably ≠ the `.info`'s 32-bit `tv_port`.
   - **Therefore keep the local store content-addressed**: compute a **SHA-256 of the decompressed
     `.dem`** as the authoritative dedupe/reconciliation key, with all platform ids stored as
     *attributes* of that blob. This is surface-independent, survives re-downloads from different
     sources, prevents double-analysis when the same match arrives via FACEIT *and* Valve *and* a
     mirror, and lets a user-supplied demo file be matched to metadata later. The id-based
     `reservationId` shortcut complements it; it does not replace it.
   - **Never synthesise a replay URL from a share code** (see §2.3.2).
   *(Adopted from the `AcquisitionAutomation` slice, who made SHA-256 the authoritative
   reconciliation key in their design.)*

**Duplicate work / overlap with sibling research slices (avoid double effort):**
- Demo *parsing* internals (`demoparser2`, `demoinfocs-golang`, `demofile-net`, `cs2parser`) →
  owned by the parsers slice; this document only references them as the mandatory next stage.
- 2D/3D viewers and radar geometry → owned by the viewers/map-geometry slices.
- Positional "fog of war" / stores analysis → owned by that slice; the API layer explicitly
  **cannot** supply the inputs (gap #1/#2 above).
- Mistake taxonomy/metrics definitions → separate slice; note that Leetify's metric **names and
  scales** are contractually frozen by their guidelines (§5) if you ever present them.

**Open questions this slice could not close (need a live key or account, out of scope here):**
- Actual FACEIT Data API/Downloads API rate limits for a non-partner key (no header documented).
- Whether the Downloads API is granted to hobbyists (30-day review, unknown acceptance rate).
- Exact `match_demo_ready` webhook payload schema (undocumented).
- Long-term stability of the GCPD page under Valve UI changes — it is at least *currently*
  production-used by two independent shipped products (Leetify's browser extension,
  `claabs/cs-demo-downloader`), which is stronger evidence than "login required to verify", but
  it remains an undocumented surface with no compatibility guarantee.
- **CLOSED 2026-10-15** — GCPD replay-URL components:
  `replay<server_ip>.valve.net/730/<reservation_id>_<tv_port>.dem.bz2` (proto names:
  `CMsgGCCStrike15_v2_MatchmakingServerRoundStats.reservationid` / `.map`), verified by parsing
  `cs-demo-manager`'s `.dem.info` fixtures (§2.3.2). The sub-question is also closed: the share
  code's 16-bit `tvPort` **provably cannot** carry the URL's 32-bit `tv_port`
  (`599906796 & 0xFFFF = 55788` matches `csgo-sharecode`'s own encode/decode examples), hence the
  rule "never synthesise a replay URL".
- HLTV / Valve EULA position on demo redistribution (no primary source found).
