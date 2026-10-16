# Modern CS2 Strategy, Roles & Competitive Meta — Research Summary

**Scope:** contemporary high-level Counter-Strike 2, patch window Oct 2024 – Oct 2026.
**Status:** research only. No detectors, no code, no verdict rules.
**Owner:** `research/gameplay/01-modern-meta/`. Parent `research/gameplay/` index intentionally untouched.

## Navigation

- `concepts.md` — 41 tactical concepts with stable IDs (`META-R/T/C/D/P/X`).
  Each concept carries the 9-point schema: meaning, objective, when appropriate,
  when questionable, reasonable information, alternatives, demo manifestation,
  not-demo-inferable, stable-vs-patch-dependent.
- `cases.md` — verifiable professional cases (team / players / map / event / date /
  round-or-timestamp + source). No invented examples.
- `sources.md` — annotated bibliography: author, title, URL, date, patch period,
  evidence type, limitations.

## Key conclusions

1. **Roles are situational responsibilities, not permanent labels.** Peer-reviewed
   CS2 evidence (Paskiv et al. 2026, data 08/2025–07/2026, 1052 players / 222 teams):
   tactical roles form a **graded, not discrete** structure (ARI ≈ 0.08); **63%** of
   T-side lurkers anchor on CT (77% reverse); attacking entry maps onto defending
   rotator; IGL is a **tag over a playstyle**, not a playstyle. A demo can label
   *actions per round/side* ("took first duel", "held small site alone"); it cannot
   reliably label a player's *role* from position averages. (`META-R09`)
2. **T-side pro play is tempo management over a structured default.** Spread for
   info/space, punish CT aggression, deny CT timings; commit to executes only with a
   utility/clock/rotation edge. Lurker distance is functional (survive the opening,
   hear rotations, arrive before resolution). Conditioning works across a half, not
   a round. (`META-T01`–`META-T10`)
3. **CT anchoring is time-buying, not kill-farming; rotations are probability
   judgments.** The anchor's life and delay outweigh a kill (Refrag 2025; BLAST 2024).
   Refusing to rotate vs a fake and over-rotating into one look identical in a demo
   without comms — the single largest blind spot in CT demo analysis. (`META-C03`,
   `META-C04`)
4. **Retakes fail ~3 in 4 at tier 1; the save/retake trade is arithmetic, not courage.**
   Reported 23.1% overall conversion, 59.0% only as full CT vs T-eco (EsportsOdds
   2026 dataset, secondary). Post-July-2025 CT $50/kill award and the July-2026 C4
   shockwave rework moved the numbers without changing the principle. (`META-C06`,
   `META-C07`)
5. **Trading is opportunity → attempt → success; following a teammate is not trading.**
   Position determines tradeability: anchor spots (Nuke Ramp, Mirage/Dust2 B) are the
   least-traded CT deaths (HLTV 2024). Low trade involvement is expected for entries,
   lurkers, AWPers — never a standalone demerit. (`META-D01`)
6. **Most pro principles transfer to ranked as skills, not as plans.** Entry duels,
   extremity patience, sightline ownership, survival-under-execute transfer; defaults,
   execute timing, rotate discipline, IGL repositioning require protocols + comms that
   do not exist in a pug. Grading a ranked demo against a pro playbook is the core
   coaching failure mode. (`META-P01`–`META-P03`)
7. **The meta moved CT-ward across the window**: pool-wide CT share 50.0% (Feb 2024)
   → 52.6% (Aug 2026) over 2,073 tier-1 matches (cs2metahistory). Six-month Premier
   season cadence rotated one map each season; economy/utility/ammo/C4 changes were
   incremental but analysis-relevant. (`META-X01`, `META-X02`)

## Central reasoning rule (for future developers/agents)

> For any observed action, ask: **"What tactical purpose could this have served,
> and under which circumstances would it actually represent a mistake?"**
> Judge decisions ex ante (information at the time), never by round outcome.
> State the assumed information set; separate demo-inferable facts from
> comms-dependent claims; never assert what voice comms carried.
> (Outcome-bias basis: Baron & Hershey 1988; see `sources.md` S-G01.)

## Contradictions found

- **Stats vs eye test is live and unresolved.** kassad ("stats aren't that important")
  vs ash/valens (data filters, demo decides) vs DeMarsDeRover (analysts lack the eye
  test) — HLTV 2024-10-28. No study measures which produces better outcomes.
- **IGL-as-rotator vs IGL-as-anchor.** Trend toward supportive-rotator IGLs for map
  vision (HLTV 2024) coexists with anchor-IGLs (karrigan) who accept the info cost.
  Both are attested; neither is "correct".
- **Star-anchors vs specialist-anchors.** 2024–2026 meta increasingly parks stars
  (ropz, KSCERATO) in anchor spots to shield weak anchors from lurks — contradicting
  the older "anchor = passive specialist" model.
- **Retake contest rate vs retake win rate.** Pros contest ~9 in 10 planted rounds
  they lose despite ~23% conversion (EsportsOdds 2026) — aggression the arithmetic
  calls wasteful but the scene treats as standard. Do not "fix" this with a rule.

## Unresolved gaps

1. Round-level 2026 T-side teardowns with VOD timestamps (available mid-2024 HLTV
   Meta Mondays predate the window; used with `[pre-window]` labels).
2. HLTV 44128 reload-patch primary text (rate-limited); ammo figures via secondary.
3. Exact C4-shockwave tactical effect (11 days of data at last reading — "within noise").
4. No peer-reviewed pug-vs-official role study; transfer matrix rests on first-person
   pro statements + inference.
5. Mauisnake force-buy-meta video claim (cited, not watched).
6. CS:GO-era save numbers (NER0cs 2023) are `[unverified-transfer]` to CS2 MR12.
7. Two HLTV leads (40128 data-revolution, 41932 apEX) never re-fetched — not cited.

## Method note

Four parallel read-only scout slices (Valve patches/maps; T-side; CT-side/teamplay;
roles/pro-vs-ranked) read primary sources directly. `counter-strike.net` and HLTV
were intermittently JS-blocked/rate-limited; Valve notes were verified via
cs2metahistory verbatim transcriptions carrying Valve's Steam announcement links.
Search snippets were leads only. No match example was invented; thin cases were
omitted rather than guessed. Per-concept confidence and transfer labels are inline
in `concepts.md`.
