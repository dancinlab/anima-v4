# Changelog

All notable changes to anima-v4. Append-only; newest on top.

## 2026-07-16 — the bet's falsifier was audited before it was built, and it failed (H_001 🟢)

- Ran the **실측전 research** rule against `mech-3.falsifier` before renting anything. The audit is
  closed-form arithmetic over anima v1's already-measured record — stdlib, deterministic, $0 — and
  it kills the clause. `H_001` SUPPORTED, 7/7 falsifiers PASS, incl. a negative control that proves
  the audit discriminates rather than condemning every comparison.
- **The bet's clause (2) cannot return a verdict.** "fixed-BPE substitution ΔF2 < 0.1 ⇒ DEAD"
  ablates G down to a fixed BPE-jamo codec — but that codec is v1's arm M and it scores d_acc
  0.9083/0.9167. d_acc is a binary forced-choice accuracy bounded at 1.0, so the largest delta any
  mechanism can show over it is 0.0833–0.0917, strictly below the 0.1 required. DEAD was fixed
  before the experiment existed.
- **Recovered four facts the divergence pass had lost** to a one-line compression of L4
  ("M F2 0.908 vs control 0.617"), and distilled them into `salvage.L4` children:
  (1) "F2" is not an F-measure — it is the NAME of eval panel `eval_f2.json`; the metric is `d_acc`,
  and it is *bounded*, which is what makes a threshold checkable in the first place;
  (2) the 0.617 control is arm C1 = **no codec at all** (raw utf-8), not a weak codec — so every
  "vs 0.617" clause in the tree silently varies the alphabet alongside the mechanism;
  (3) the panel has a measured **leak ceiling** (arm C3, all 4 negators collapsed to one token id =
  answer handed over) of 0.9167, and the fixed codec sits exactly on it at seed 7 — ~0.01 of
  headroom, not 0.38;
  (4) the result was **cemented at 2 seeds** (4302, 7), so mech-3's clause (3) spends a debt v1 had
  already paid.
- **Same lost fact, opposite symptoms**, which is why reading alone never caught it: mech-3 compares
  to the strong arm and is UNPASSABLE; `mech-1` clause (3) compares to the weak arm and is TRIVIALLY
  PASSABLE (any codec clears +0.15 unaided, parser duel or no parser duel). Recorded as
  `evidence-integrity.ei.opposite-symptoms-one-cause`.
- **The bet rests on its own null.** L4b's +0.29/+0.34 was produced by a FIXED, frequency-trained,
  label-blind codec — no adversary, no learning, no tension. That artifact is not mech-3's evidence;
  it is mech-3's null hypothesis, already measured, sitting on the panel's leak ceiling. Two of the
  three grounds in `mech-3.why-bet` are simply false besides: the falsifier is the *most* expensive
  in the set (needs a 303M `base.pt` that exists nowhere + a rented 4090 at ~2h/arm), and L2 does
  reach it. `why-bet` → WITHDRAWN AS STATED. mech-3 is **un-bet, not refuted** — H_001 kills a
  falsifier, not an idea.
- Read C2/C3 for what they actually say (`salvage.L4.what-was-actually-causal`): the causal factor
  is **atomicity** of the negator token and nothing else — not identity (C3 collapses all 4 negators
  to one id and scores the same), not pretraining exposure (C2 scrubs the held-out stem from
  pretraining entirely and scores the same).
- Found the crack the static method itself admits (`salvage.L4.atomicity-was-luck-not-method`):
  v1's codec searches a K-ladder for a K whose *frequency* merges happen to leave the stems
  token-disjoint, and `morph2b.py:15-16` writes the contingency down — "if 아니 can't fuse even at
  K=16384 → switch primary held-out to 못". K=2048 got lucky. Frequency BPE cannot **target**
  atomicity, and never merges a pair below its min-count floor at any K. That is where a learned
  codec would have room, and the headroom there is the full C1→M gap.
- Added `verification.admissibility-gate` — the prerequisite to the inherited L1/L2 gates and the
  cheapest gate in the campaign, since it runs on arithmetic before any code exists: a falsifier is
  admissible only if it can return both answers (reachable · not-free · one-variable · name-the-arm).
- Harness: `tool/anima_v4.py` gained the closed-form admissibility primitives the audit runs on —
  `max_attainable_delta`, `falsifier_reachable`, `saturation`, `bpe_merge_reachable`, plus the
  definitional `D_ACC_MAX`/`D_ACC_CHANCE`.

## 2026-07-16 — divergence: an A<->G whose tension IS the thinking (7 mechanisms)

- Framed the campaign from the owner's ask ("실제로 생각하는 A<->G 가 필요해"): the two-engine
  premise is KEPT, the emit-controller it degenerated into is rejected.
- Imported the `anima` (v1) autopsy into `ARCHITECTURE.json` -> `salvage` (L1..L9) as the only
  inheritance; the evidence trail stays in the `anima` repo.
- Recorded the diagnosis of WHY a two-engine tension generically collapses to 1 bit, in five
  clauses: a scalar kills structure · unconsumed bits die · a gradient-free engine is decoration ·
  a fixed point is an incinerator · side channels get eaten. Conclusion: the defect is not the
  engine count, it is that the coupling had dimension 1.
- Derived five necessary conditions for a tension that can carry thought (structured object ·
  iteratively resolved with per-step loss · resident in loss/data/codec · both engines get
  gradient on incompatible objectives · resolver serialized into inference) and used them as the
  admission gate for every candidate.
- Ran a divergence pass (Fable 5) and recorded 7 mechanisms, each answering "what does the
  opposition COMPUTE?" with a cognitive operation: mech-1 parser-duel (binding) · mech-2
  reverse-sculptor (abstraction) · mech-3 codec-war (which units exist) · mech-4
  contradiction-court (contradiction resolution) · mech-5 gradient-tug-of-war (forced formation
  of a recombinable code) · mech-6 constraint-market (constraint-satisfaction search) · mech-7
  counterfactual-editor (causal abstraction). Each carries its tension object, objective
  placement, L2 defense, minimal falsifier and the purity principle it breaks.
- Recorded the fake-diversity audit in the SSOT: mech-1/6 are one family (learned resolver over
  conflicting structure), mech-2/4 one verb (residual rewrites state), mech-3/7 one strategy
  (G writes A's training environment). Only three independent axes + mech-5 on a fourth.
- Named the bet: mech-3 codec-war — the only mechanism standing on a lever already measured green
  (L4 MORPH-ATOM delta +0.291), the cheapest falsifier (existing protocol reuse), and structurally
  out of L1/L2's reach because its tension writes the input alphabet instead of reading anything.
- Fixed the two non-negotiable falsifier gates (L1 effective-rank check · L2 ablation check).
  Retained exactly one v1 principle: p7 (perplexity is never truth).
- Preserved the verbatim divergence + the brief that produced it under
  `state/diverge_ag_thinking_2026-07-16/` as the seed of record.
- STAGE = DIVERGENCE: no mechanism selected, no code, nothing in the tree is a claim.

## 2026-07-15 — repo scaffold

- Initialized `anima-v4` from the sidecar `lab init` skeleton: `src/`, `state/`,
  `ARCHITECTURE.json` + `architecture.html` viewer + `serve.py`, `CLAUDE.md`,
  `README.md`, `CHANGELOG.md`, `.gitignore`, `.harness/`.
- Scaffolded the hypothesis-verification system `HYPOTHESES/` (`CLAUDE.md`, empty
  `REGISTRY.jsonl`, `cards/_TEMPLATE.md`) + the repo-root shared harness
  `tool/anima_v4.py` (stdlib-only `Falsifier`/`evaluate` ledger).
- Authored a placeholder `ARCHITECTURE.json` SSOT (overview / components / data-flow /
  verification) — fill the tree from the campaign's design.
