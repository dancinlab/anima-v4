---
id: H_008
ssot: ARCHITECTURE.json → campaign-result.cr.reopen-conditions, next-gate.ng.h008-budget-band-gate
slug: supervision-budget-sample-efficiency
title: under a scarce, arm-identical, coverage-complete few-shot answer budget k*, an irreconcilable role-swap co-objective CAUSES higher held-out SWAP-XOR-B composition than the compute/param/gradient-matched duplicate-objective control — Δd_acc ≥ 0.10 both seeds at a budget where the trained control is MEASURED sub-ceiling in [0.60, 0.80]
domain: verification-design (supervision-budget axis · sample-efficiency · pre-register SEED)
exploration_method: research-gate delegated to Fable 5 after the TERMINAL campaign result — instantiates reopen door [b] of CAMPAIGN_RESULT.md §4; OPEN-gated, not frozen
verification_method: deterministic forced-choice d_acc (free-slot, recomputed on SWAP-XOR-B) at a frozen answer budget; controls-first G-1.5 band-existence pre-run at target scale is MANDATORY-BLOCKING before any mechanism arm
pre_register_frozen: false
frozen_at: null
deterministic: false
llm: none in the eval path (design only; trunk trained, scoring deterministic forced-choice)
---

# H_008 — supervision budget: does objective conflict buy SAMPLE EFFICIENCY the duplicate control does not?

> **SSOT**: `ARCHITECTURE.json → campaign-result.cr.reopen-conditions · next-gate.ng.h008-budget-band-gate`.
> Full pre-register detail: `state/h008_supervision_budget_sample_efficiency_2026-07-17/DESIGN_fable5_seed.md`.
> **STATUS: ⚪ PRE-REGISTERED — SEED ONLY, NOT FROZEN.** Freeze is blocked, in order, on: lit-verify (2
> MEMORY rows) → G-0b panel+budget audit exit 0 → G-1.5a band existence (seed-0 sweep, kill-capable ~1.5h)
> → G-1.5b cross-seed stability + plateau → G-1.5c placebo/scaffold pricing. The campaign stays CONCLUDED
> unless every gate is green; a K1/K1b close seals this card near-$0 and changes nothing else.

## The one-variable lever

H_007's two-head rig verbatim (d=384 L=4, CPT 3000 + drill 4000 steps, head-A forced-choice free-slot
d_acc), plus ONE new constant: the answer budget **B(k)** — a deterministic, seed/arm-independent, nested,
coverage-complete subset of k = 24·r drill items that carry the answer suffix; all other items are
answer-TRUNCATED (no gold byte in any arm's input). head-G's surface-only target is NEVER rationed. Arms:
A-tug (swap(x)) · C-dup (duplicate forward — THE control) · C-shuf (placebo) · C-scaf (λ_G=0) · C-perm
(GLOBAL-derangement harness, fixing H_007's flagged per-batch defect 0.5938/0.5208). Only head-G's target
varies; B(k*), steps, init, sampling byte-identical across arms.

## Why the H_007 panel was NOT reused (new measured fact, 2026-07-17)

Computed from frozen artifacts: f2 subjects {사장,교수,학생,친구} vs drill subjects
{교수,부장,회장,친구,동생,이웃} — 사장/학생 have ZERO answered subject occurrences, yet C-dup.s0 f2 =
1.0000 (`state/h007_.../verdict_g2.json`) ⇒ a budget-INDEPENDENT class channel exists (shared-syllable
byte families 장/생 + NSMC CPT semantics of real nouns). An answer-budget knob on that panel would ration
only part of the class-grounding channel. **SWAP-XOR-B** rebuilds it: byte-orthogonal synthetic pseudo-noun
pools (48 distinct syllables, none in CPT, no status morphology), symmetric coverage-complete grid
(f2-subjects ⊆ drill-subjects, k_min = 24), full G-0 audit suite re-run + A7 class-byte-orthogonality +
B1–B6 budget audits.

## Falsifiers (frozen text in the seed §4; bar b = 0.10, band [0.60, 0.80])

- **F1**: Δ(A-tug − C-dup) at k* ≥ 0.10 both seeds; DEAD < 0.05 both; split ⇒ INCONCLUSIVE-CONSOLIDATE.
  Headroom ≥ 2b guaranteed by the band condition — anchors are the G-1.5 measurements themselves.
- **F2**: budget-fit d_acc(B(k*)) ≥ 0.95 per arm/seed. **F3**: C-dup ∈ [0.60,0.80] AND C-scaf ≤ 0.80.
- **F4 (L1)**: A-tug probes subj/obj > 0.65, |cos| < 0.8; mechanism-route claim needs probe surplus vs
  C-dup ≥ 0.10 (free-ingredient trap: H_007 measured F4 pass in BOTH arms at full budget).
- **F5 (L2)**: INLP-style iterative erasure (≤ rank 16, probes → ≤ 0.55) then Δd_acc ≥ 0.05 + random-rank
  and C-dup specificity controls (H_007's single rank-2 projection measured Δ = 0.0 — instrument too weak).
- **F6 (co-primary placebo)**: Δ(A-tug − C-shuf) ≥ 0.05 both seeds; E[C-shuf@k*] ≤ 0.80 priced BEFORE the
  mechanism arm (scarce-label aux transfer is the best-attested boring story).
- **F7**: G-0b closed-form suite exit 0. **Harness**: C-perm ∈ [0.45,0.55]. **P-conflict**: veto-only
  (role-specificity of the instrument was REFUTED by H_007: C-shuf differential +0.5390 > A-tug +0.3285).
- Preconds: FLOP parity · plateau (C-dup f2 drift ≤ 0.05 over last 40% of drill steps).

## Kill criteria

K1 no stable band (≤8-run hard cap, no knee-fishing) ⇒ CLOSE near-$0, measured wall. K1b placebo
saturates the band ⇒ CLOSE pre-mechanism. K2 band holds + F1 DEAD ⇒ mech-5 family MEASURED-NULL (seal the
red). K3 green but F6 fails ⇒ generic-aux verdict, PARTIAL, no tension claim. K4 no conflict ⇒ aux-transfer
scope. K5 F4/F5 fail/void ⇒ no mechanism-route claim. K-scope: even full green = SAMPLE-EFFICIENCY only —
mech-5's forced-code claim stays retired, mech-1's seal and the PARTIAL thesis boundary unmoved.

## Cross-Links

- CAMPAIGN_RESULT.md §4 reopen [b] — the door this instantiates · `verification.trained-control-ceiling`
  (G-1.5, satisfied by construction) · H_007 ⚫ (rig + every trained-control anchor) · H_005 (ungrounded
  mode + probe-ceiling limits) · H_003 (seed-spread pricing 0.1614) · H_004 🟢 (sealed, untouched).

## Verdict

*(none — pre-registered, gates pending; freeze order in the seed §5)*
