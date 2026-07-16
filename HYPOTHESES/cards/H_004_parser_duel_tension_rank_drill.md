---
id: H_004
ssot: ARCHITECTURE.json → next-gate.*, mech-1.* (this card is the pre-register SEED, not yet frozen)
slug: parser-duel-tension-rank-drill
title: the per-edge parse-disagreement FIELD T (A=L→R parser vs G=R→L parser) — as a field, NOT its rank-1 scalar summary — CAUSES held-out honorific-binding resolution; one variable = post-parse tension policy (full T vs rank-1 T), predicted Δd_acc ≥ 0.15 on a HON-BIND panel whose heuristics sit at 0.5
domain: verification-design (causal drill · pre-register SEED)
status: pre-register-seed
exploration_method: research-gate delegated to Fable 5 under fable-mode (literature scan + one-variable lever + admissibility arithmetic); absorbed locally
verification_method: deterministic panel audits (F7 · closed-form) + trained-arm falsifiers (F1–F7, with L1 eff-rank as F4 and L2 union-substitution as F5) with a rank-1 control, a placebo, and a leak-ceiling arm
pre_register_frozen: false
frozen_at: null (NOT frozen — G-0 closed-form panel/rank audit + G-1 $0 CPU probe must pass first; only then do E-values become anchors and the arms train)
deterministic: false
llm: none in the eval path (design only; the model is trained, the scoring is deterministic forced-choice)
---

# H_004 — parser duel: does the parse-disagreement FIELD (not its rank-1 summary) CAUSE binding?

> **SSOT**: the design tree is `ARCHITECTURE.json` — this card is the pre-register SEED (Fable-5
> research-gate output, absorbed). The mechanism lives at `mech-1.*`; the next-gate pointer at
> `next-gate`. Raw seed: `state/h004_parser_duel_tension_rank_drill_2026-07-16/DESIGN_fable5_seed.md`.
> Human viewer: `python3 serve.py`. **NOT FROZEN — no number here is a result; G-0/G-1 gate it.**

## Status — PRE-REGISTER SEED (2026-07-16); G-0 panel+F7 PASS, NOT FROZEN

The next mechanism after mech-3's four-part death (H_003 🔴). Chosen off the codec axis: mech-1 파서
결투 (binding) over mech-7 (반사실 편집자), because mech-7 is mech-3's corpus-axis twin in the same
strategy family (`fake-diversity` audit) and would inherit mech-3's just-measured failure mode. This
card is a **seed**: the design is admissibility-pre-checked on arithmetic, and the panel half of G-0
is now built and gated — but the freeze is NOT taken.

**G-0 panel gate = PASS** (2026-07-16, $0, verified by our own `build_hon_bind.py` run — not the
design's self-report; commons `verify-done`). The HON-BIND panel (SPEC_hon_bind_panel_fable5.md) is
implemented and F7 measures **every heuristic at exactly 0.5** on f2′ (n=192) and f1′ (n=64):
presence-attach · locality · lexical-lookup(6 groupings) · marker-position · template ·
worst-suffix(L≤10) · verbform-prefix(gated) · char-length — with all structural asserts holding
(per-cell equal · 도 particle constant · every stratum balanced 0.5 · task-conjunction sanity 1.0).
The fixed-L prefix curve is report-only (hits 1.0 at L≥6 — short verb forms cross into a drill-absent
N1 lexeme; the prefix analog of H_003's long-suffix over-count, not a learnable leak). G-1 grammar =
PROVISIONAL LLM PASS (`g1_grammar_provisional.md`): surfaces grammatical, +시 cells hard grammar, −시
cells rest on the drilled categorical-agreement convention (documented asymmetry).

**G-1 core designed + arithmetic-MEASURED at $0 (2026-07-16)** — `state/h004_parser_duel_tension_
rank_drill_2026-07-16/DESIGN_g1_core_fable5.md` (numbers from our own `g1_core_check.py` run):
honorific-blind proxy parsers P_A (L→R nearest-head) / P_G (R→L maximal-head) disagree on exactly ONE
edge on this frame, so the concord field collapses to `T ≡ s·(E12+E13)`, s = 1−2·gold_flip — one
signed scalar (v1's emit-bit in a 5×5 costume). Measured consequences on the built panel: **G-0
rank-mass = 0.000 < 0.20 (F4-DEAD as pre-registered) · G-1 probe(vec)=probe(rank-1)=1.000 ⇒
separation 0.000 ≤ 0.05 ⇒ the pre-registered STOP fires**; permuted-T probe = 1.000 ⇒ F6 void; F1
itself is inadmissible on single-bind items (A-rank1 receives ≈ A-duel's tensor ⇒ DEAD by
construction). The XOR shield is confirmed (unary token features exactly 0.500 via concave linear
probe; one T cell = the cross-edge product = 1.000). **Fix, arithmetic-checked on the full 4^6
factorial: MULTI-BIND K=6** (six stacked HON-BIND conjuncts, 6 answer slots, chance 0.5/slot):
off-top 0.8333 ✓ · probe(vec) 1.000 ✓ · probe(rank-1) 0.5833 ≤ 0.60 ✓ (exact, K=6 minimal) ·
separation 0.4167 ✓ · perm-placebo 0.711 ⇒ F6 headroom 0.289 ✓. f1′ stays liveness; f2′ becomes
report-only diagnostic; F1 moves to f2″ with E[A-rank1]=0.62.

**Remaining before `pre_register_frozen: true`**: (1) native-operator confirm of the PL-cell
normativity + 2 flagged genitive orders + lexeme-pool expansion 4→6 pairs for MULTI-BIND; (2) build
f2″ MULTI-BIND (K=6, n=192) + F7″ audit + the drill grid with its lexeme-disjointness check (F7
disjointness currently PENDING); (3) re-run G-0 rank-mass + G-1 probe-separation on the BUILT f2″
(predictions above are exact and falsifiable); (4) re-anchor F1 E-values on f2″.

## Hypothesis

A = LM with an L→R parser; G = an R→L parser. The opposition computes **binding** — the two parse
directions disagree per edge, producing a tension field `T` (n×n over token pairs). The claim: T **as
a field** (its full structure), not its rank-1 scalar summary, is causal for a held-out binding
operation the trunk cannot do cheaper. This replaces mech-1's broken falsifier clause (3) (trivially
passable — a mirror of the H_001 defect); the standing L1 (effective-rank > 1) and L2 (ablate the
channel) become F4 and F5 in the verdict, not appendix checks.

**Predicted**: `Δd_acc = d_acc(A-duel, f2′) − d_acc(A-rank1, f2′) ≥ 0.15` on the HON-BIND OOD panel.

## The one-variable lever — post-parse tension policy

H_003's lever was a post-encode span policy (atomic vs shattered); the analog here is a **policy on
the tensor T handed to the resolver R**. Both parser towers run in every arm; corpus, vocab, model,
steps, seed byte-identical — the corpus delta between arms is **zero** (cleaner than H_003's 3–5%).

| arm | resolver input | isolates |
|---|---|---|
| **A-duel** | T = per-edge disagreement(P_A, P_G), untouched | the mechanism |
| **A-rank1** | best rank-1 approx of T (per sentence, Frobenius-matched) | **control** — v1 died rank-1; if the scalar summary does as well, the "field" is an emit-bit with extra steps |
| **C-plc** | P·T·Pᵀ, fixed random conjugate permutation per sentence (spectrum preserved, edge-alignment destroyed) | placebo — shape/spectrum vs edge-aligned content |
| **C-scaf** | T ≡ 0 (resolver still in graph) | leak / not-free floor |
| **C-perm** | A-duel on permuted gold | harness check |

Conditional 6th arm on F1 pass (H_003's C-syl role): **A-self** — T from two same-direction seeds of
A, testing whether the *direction* opposition matters or any parser pair does.

## The panel — HON-BIND (binding visible, heuristics at 0.5)

Prenominal-RC attachment forced choice, disambiguated **only** by honorific binding. Frame
`[RC-verb(±시)] N1-의 N2-가 …`, exactly one of {N1,N2} honored (선생님-class vs 아이-class), position
counterbalanced. `gold = honorific(-시- in RC-verb) XOR position-of-honored-noun` — H_003's XOR
construction transplanted from depth-parity to attachment. Presence ("-시- ⇒ attach high"), locality
(nearest noun), and lexical-lookup heuristics each land at **0.500** on a 50/50 panel; all three
verified closed-form by an F7 audit before training (reuse `build_panels.py` discipline). Resolving it
requires connecting a verbal morpheme to the correct head across an ambiguous edge — an entry of T.
**No negator anywhere** (keeps distance from the closed codec axis).

- **f2′** (verdict, OOD): held-out honored-noun lexeme × both attachment heights × both honorific
  settings, fully crossed, 50/50 per cell, **n=192** (σ≈0.036). `f1`/`f2` are PANEL names; metric is
  `d_acc` (chance 0.5, ceiling 1.0).
- **f1′** (liveness): drilled nouns, held-out conjugation, n=64; f1′(A-duel) < 0.85 ⇒ measurement DEAD.

## Falsifiers + admissibility pre-check (arithmetic, before any code)

Anchors from H_003 (`state/h003_atomicity_fixed_codec_drill_2026-07-16/verdict.json`): a trained-but-
crippled arm (A-shat) measured 0.6094–0.6823; scaffold (C-scaf) 0.4948–0.5000. Estimates: E[A-rank1
f2′] = **0.60** (scalar summary retained), E[ceiling A-duel f1′] = **0.90**. E-values are NOT anchors
until G-1 confirms them (`adm.4`).

- **F1 (primary)**: Δ = d_acc(A-duel,f2′) − d_acc(A-rank1,f2′). SUPPORTED iff Δ ≥ 0.15 both seeds;
  DEAD iff Δ < 0.05 both; else PARTIAL.
  - *reachable*: 0.15 ≤ ceiling − control = 0.90 − 0.60 = **0.30** ✓ (2× inside headroom; H_001's dead gate was 0.083 < 0.1 ✗).
  - *not-free*: the bar is a gap over a trained, both-towers-running control; F3 checks the floor empirically.
  - *one variable*: arms differ in a single per-sentence projection of one tensor ✓.
- **F2 (liveness)**: f1′(A-duel) < 0.85 ⇒ DEAD, no F1 verdict.
- **F3 (not-free)**: f2′(C-scaf) > 0.60 (chance + 2.8σ) ⇒ grid leaks ⇒ no verdict.
- **F4 (= standing L1, made causal)**: descriptive eff-rank(T) on held-out ≤ 1 ⇒ DEAD ($0 pre-run).
- **F5 (= standing L2)**: resolver→union substitution at inference, ΔCE < 0.01 AND Δd_acc(f2′) < 0.05
  ⇒ the decoder never needed the resolution ⇒ DEAD.
- **F6 (placebo)**: d_acc(A-duel) − d_acc(C-plc) ≤ 0.05 ⇒ placebo void ⇒ no SUPPORTED verdict.
- **F7**: closed-form heuristic audit of both panels pre-freeze.

## Cheapest-first path (실측전 research satisfied; gates are $0 before any training)

- **G-0 ($0, closed-form)**: generate panels; F7 heuristic audit; verify rank-1 projection removes
  mass (report fraction of ‖T‖² off the top singular direction on sample parses — the analog of
  H_003's 3–5% corpus-delta audit; < 20% off-top ⇒ T already near-rank-1 ⇒ F4-dead at $0).
- **G-1 ($0–$ε, CPU, no mechanism training — H_001/H_002-style)**: two cheap directional proxy parses
  (deterministic head-final L→R vs R→L automata, or minutes-scale taggers), compute T on the panel,
  fit three logistic probes for the gold bit: **probe(vec T)** vs **probe(rank-1 T)** vs **probe(‖T‖)**.
  - probe(vec T) ≤ probe(rank-1 T)+0.05 → the field carries nothing beyond its scalar even before
    learning → premise unsupported at $0; stop or redesign (proxies ≠ the learned duel, so this is a
    spend-justification gate, not automatic mechanism death).
  - probe(vec T) ≥ 0.75 while probe(rank-1 T) ≤ 0.60 → headroom real; training spend justified.
- **G-2 (training, only after G-0/G-1 green)**: H_003's exact envelope — d=384 L=4, 2 seeds × 5 arms,
  local MPS, ~6h, $0 cash. Resolver R = small bilinear head over T → structure embedding; decoder
  conditioned **only** on resolved structure (`mech-1.l2-defense`).

## Honest Limits — the three ways this is secretly the old corpse

- **L1 secretly mech-3 (codec in a trenchcoat)**: on jamo input the two directions disagree mostly at
  morpheme boundaries, so T is a segmentation signal and R re-does the codec. Tell: MI(T; boundary)
  ≈ MI(T; everything); masking boundary-adjacent cells leaves Δd_acc unchanged; gain reappears on a
  boundary panel but dies on HON-BIND. Any ⇒ codec axis re-entered; stop.
- **L2 secretly rank-1 (v1's death)**: A-duel − A-rank1 < 0.05 both seeds while A-duel − C-scaf ≥ 0.15.
  This IS F1's DEAD reading (the most likely failure is the primary measurement, not a confound).
  Early $0 tell: G-1 probe separation ≤ 0.05, or G-0 off-top mass < 20%.
- **L3 secretly free (capacity, not content)**: C-scaf > 0.60 (F3) or A-duel − C-plc ≤ 0.05 (F6) — any
  tensor of that shape regularizes the decoder into the answer; the falsifier would certify the
  resolver's capacity, not binding. ⇒ measurement dead, tighten bottleneck/panel, re-freeze.

**Family propagation** (`fd.family-structure-conflict`): mech-1 and mech-6 are the same family (learned
resolver settles conflicting structure proposals, N=2 vs N>2). A DEAD here — especially via L2 or L3 —
is pre-declared to count as half a verdict on mech-6, so the fake-diversity audit can't be re-litigated.

## Cross-Links

- **architecture**: `next-gate`, `mech-1.tension`, `mech-1.falsifier` (broken clause 3, replaced here),
  `necessary-conditions` (nc1–nc5), `verification.admissibility-gate`
- **prior H**: [H_003](H_003_atomicity_fixed_codec_drill.md) (the template + the anchors + the panel trap),
  [H_001](H_001_mech3_falsifier_vacuity.md) (the admissibility discipline)
- **design seed**: `state/h004_parser_duel_tension_rank_drill_2026-07-16/DESIGN_fable5_seed.md`

## Verdict

_None — pre-register SEED, NOT frozen. G-0 (closed-form panel + rank-mass audit) and G-1 ($0 CPU probe
separation) must pass before `pre_register_frozen: true`; only then do the E-values become anchors and
the arms train. No number in this card is a result._
