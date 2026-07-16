---
id: H_005
ssot: ARCHITECTURE.json → next-gate.mech1.g3-research-gate (this card is the pre-register SEED for G3-a)
slug: learned-chi-values
title: a LEARNED concord χ̂ = g(φᵢ,φⱼ) on the FIXED proxy-parser support reproduces the hand-computed field's causal power on held-out honorific binding — i.e. the FIELD VALUES (signs), not just the format, can be trained; one variable = χ policy (hand χ vs learned χ̂), support held fixed
domain: verification-design (causal drill · learned-values stage G3-a · pre-register SEED)
status: pre-register-seed
exploration_method: research-gate delegated to Fable 5 (DESIGN_g3_research_gate_fable5.md, literature-verified) — G3-a is the run-first, cheapest-decisive half of the learned-duel extension after H_004 🟢 SUPPORTED
verification_method: deterministic forced-choice d_acc (free-slot {0,1,2,4}) on the H_004 f2″/f1′/drill panels; a learned χ̂ module trained jointly on the drill, with a same-g wrong-support placebo (C-χ̂plc) + the H_004 controls carried verbatim
pre_register_frozen: false
deterministic: false
llm: none in the eval path (design only; χ̂ is trained, scoring is deterministic forced-choice)
---

# H_005 — G3-a: can a LEARNED χ̂ reproduce the hand-computed concord field's causal power?

> **SSOT**: design tree `ARCHITECTURE.json → ng.mech1.g3-research-gate`. This card is the pre-register
> SEED absorbed from Fable's G-3 research-gate (`state/h004_.../DESIGN_g3_research_gate_fable5.md`).
> **NOT FROZEN** — the $0 admissibility gate (G3-0d) + the d=64 smoke must pass before `pre_register_frozen`.
> H_004 (G-2, the FIELD FORMAT claim) stays SEALED 🟢; H_005 only extends its scope from FORMAT→VALUES.

## Why this hypothesis (the caveat H_004's own verdict names)

H_004 SUPPORTED certifies the parse-tension FIELD FORMAT (edge-aligned support × concord values) as the
causal carrier of held-out honorific binding — but the concord χ (which sign each contested cell carries)
was **hand-computed** (`gc.concord_field`: χ[i][j] = +1 if hon[i]==hon[j] else −1). G3-a asks the next
falsifiable question with the SUPPORT held fixed (the proxy L→R/R→L disagreement `gc.t_struct`, unchanged):
**can a trained χ̂ = g(φᵢ,φⱼ) learn those signs from node honorific features and reproduce the field's
causal power?** This is the field's VALUES half; the harder SUPPORT half (trained parser opposition) is
H_006/G3-b, gated behind this.

## The one-variable lever — χ policy (hand χ vs learned χ̂), support FIXED

- **A-hand** — the H_004 A-duel field verbatim: T = t_struct(support) ⊙ χ_hand(hon). The anchor (E≈0.95 free-slot).
- **A-χ̂** — SAME support t_struct, but VALUES from a trained module: T̂ = t_struct(support) ⊙ χ̂, where
  χ̂[i][j] = tanh((Uφᵢ)·(Vφⱼ)/√r + b) is a BILINEAR g (U,V ∈ R^{4×d}, ~2–4k params), and **φᵢ = per-node
  mean-pooled state of the FROZEN post-CPT trunk** over node i's SURFACE bytes (answer-blind, struct-free —
  the same top-layer interface G3-b's shared readout will read). g trains jointly on the drill (χ̂ is IN the
  resolver's forward graph); φ is frozen (no grad). One variable vs A-hand: the concord is learned from what
  the model REPRESENTS instead of hand-set; support/panel/model/steps/seed byte-identical. **Why φ=trunk not
  raw hon** (Fable fidelity review g3a_review): g(raw hon) cannot fail — learning the equality of the two
  scalars χ_hand compares is trivial, so A-χ̂≡A-hand and F1a/K2/K3 become unreachable; it would certify the
  MLP, not the mechanism (the exact `dont`). Reading trunk φ makes "is concord recoverable from the model's
  representation" the real, falsifiable content, and keeps G3-a a genuine kill-gate for G3-b (which reads
  learned tower states).
- **C-χ̂plc** (primary control) — the SAME trained g, but on per-item-PERMUTED support (right learned values,
  wrong cells). Isolates alignment-not-capacity. (The VALUES-matter control is **F5 carried** — the
  strip-resolution substitution on A-χ̂ must collapse d_acc, as H_004 measured 1.0→0.5.)
- **C-scaf** (T̂≡0) · **C-perm** (permuted-gold harness) — carried verbatim from H_004.

## Falsifiers + admissibility (arithmetic, before any training)

- **F1a (primary)**: Δ = d_acc(A-χ̂, f2″) − d_acc(C-χ̂plc, f2″). SUPPORTED iff Δ ≥ 0.15 both seeds;
  DEAD iff Δ < 0.05 both. Admissibility: E-anchor A-χ̂≈0.95 (matches A-hand ceiling) vs C-χ̂plc≈0.63
  (H_004's measured C-plc, same spectrum-preserved-but-misaligned floor) ⇒ headroom 0.32 = 2× the bar ✓.
- **F1a′ (non-inferiority)**: d_acc(A-χ̂) ≥ d_acc(A-hand) − 0.05 both seeds — the learned values must not
  be materially worse than the hand ones (else G3-a reports the measured COST of removing the hand, K3).
- **F2 liveness** f1′(A-χ̂) ≥ 0.85 both · **precond** drill d_acc(A-χ̂) ≥ 0.95 both · **F3 not-free**
  f2″(C-scaf) < 0.60 · **harness** f2″(C-perm) ∈ [0.45,0.55] · **F4 eff-rank** A-χ̂ offtop ≥ 0.20 ·
  **F5 union** A-χ̂ union ΔCE ≥ 0.01 OR Δd_acc ≥ 0.05 — carried from H_004 (all on free-slot d_acc {0,1,2,4}).
  (No standalone F6: in G3-a the **C-χ̂plc arm IS the placebo** — same learned χ̂, spectrum-matched but
  edge-misaligned support — so F1a already tests A-χ̂ against a matched-magnitude placebo; the H_004 F6
  vs C-plc does not apply and is deliberately dropped, not omitted.)

## $0 gate before training (G3-0d) — must pass before freeze

Logistic probe: is the honorific bit recoverable (≥0.90, held-out split) from the FROZEN d=384 CPT trunk's
per-node φ? If the trunk does not represent the concord, χ̂ = g(φ) has nothing to read and G3-a is UNBUILT
(the gate doing its job, not a setback). No H_004 checkpoint needed — G3-a's OWN CPT stage is the same
recipe; run one CPT per seed and probe (tens of minutes, $0 cash). `train_g3a.py --g3-0d`.

## Honest-limit (Fable fidelity review) — when G3-a is STILL a scaffolding-certifier

Even rewired, name it on the frozen record: (a) if G3-0d probes ≈1.0 because the templatic drill register
preserves byte identity nearly verbatim in top-layer states, then g(φ) is one linear unmix from g(raw hon)
and a green F1a certifies "concord is recoverable from trunk representations **on the drill register**,
nothing about learned SUPPORT" — scope it, and RECORD the probe's actual number; (b) if F5 on A-χ̂ fails to
collapse d_acc, the signs were epiphenomenal on this rig and the "values" framing is vacuous regardless of F1a.

## Honest kill criteria (Fable K2/K3 — G-2 is a defensible resting place)

- **K2**: F1a fails (Δ < 0.05 both seeds) ⇒ learned values work equally on WRONG support ⇒ it is capacity,
  not binding ⇒ STOP and consolidate at H_004's FORMAT claim; do NOT proceed to G3-b (strictly harder).
- **K3**: F1a′ fails (A-χ̂ < A-hand − 0.15, precond met) ⇒ trained values cannot reproduce hand concord at
  this scale ⇒ same stop; report the gap as the measured cost of removing the hand.

## Cross-Links

- H_004 (SEALED 🟢) — the FORMAT claim this extends. `ARCHITECTURE.json → ng.mech1.g2-precond-failed`.
- H_006 / G3-b (trained parser opposition = SUPPORT half) — gated behind G3-a green + $0 gates G3-0a/b/c.
- Design: `state/h004_parser_duel_tension_rank_drill_2026-07-16/DESIGN_g3_research_gate_fable5.md`.

## Verdict

⚪ PRE-REGISTER SEED (2026-07-17). No number here is a result. Next: G3-0d $0 gate + d=64 smoke of the
learned-χ̂ arm (device + injection-path + one-variable audit, per this session's 3-defect discipline) →
`pre_register_frozen: true` → ~4h d=384 ×2seed ×5arm run → collect_verdict.
