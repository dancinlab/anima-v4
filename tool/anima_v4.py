"""anima_v4 — shared runnable harness for HYPOTHESES hypothesis cards.

Deterministic, dependency-free (stdlib only) primitives for the anima-v4 problem.
HYPOTHESES cards reference these functions from their per-hypothesis run scripts
under `state/<hX>/` (shared machinery lives in repo-root `tool/`, per-hypothesis
runs live in `state/`).

Every function is a closed-form public relation — no fitting, no hidden constants
beyond documented defaults. All inputs are explicit so a card's falsifiers can be
evaluated against the returned numbers. Replace the placeholder primitives below
with the domain relations this campaign actually needs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# --- domain constants (explicit, no hidden fitting) ---------------------------

# `d_acc` (the anima v1 MORPH-ATOM metric) is forced-choice discrimination
# accuracy: NLL(seed+gold) < NLL(seed+counterfactual) over a 2-way choice.
# It is an accuracy over a binary forced choice, so it is bounded and its
# chance floor is exactly 1/2. Both bounds are definitional, not measured.
D_ACC_MAX = 1.0
D_ACC_CHANCE = 0.5


# --- generic closed-form primitives -------------------------------------------

def ratio(value: float, baseline: float) -> float:
    """Improvement factor of a measured value vs a baseline: value / baseline."""
    if baseline == 0:
        raise ValueError("baseline must be non-zero")
    return value / baseline


def headroom(current: float, floor: float) -> float:
    """Reduction factor between a current value and a theoretical floor:
    current / floor (>1 means there is room to improve toward the floor)."""
    if floor <= 0:
        raise ValueError(f"floor must be > 0: {floor}")
    return current / floor


def log_ratio(x: float) -> float:
    """Natural-log primitive kept as a worked example of using `math` (a
    thermodynamic-style floor is often R·T·ln(1/x)). Replace as needed."""
    if not (0.0 < x < 1.0):
        raise ValueError(f"x must be in (0,1): {x}")
    return math.log(1.0 / x)


# --- falsifier-reachability primitives ----------------------------------------
#
# A pre-registered falsifier of the form "delta(mechanism, control) < T => DEAD"
# is only a test of the mechanism if T is arithmetically attainable. When the
# control already scores near a bounded metric's ceiling, no mechanism can clear
# T and the falsifier returns DEAD for reasons that have nothing to do with the
# mechanism. These primitives decide that question in closed form.

def max_attainable_delta(control: float, ceiling: float = D_ACC_MAX) -> float:
    """The largest delta any mechanism could possibly show over `control` on a
    metric bounded above by `ceiling`. Closed form: ceiling - control."""
    if control > ceiling:
        raise ValueError(f"control {control} exceeds ceiling {ceiling}")
    return ceiling - control


def falsifier_reachable(threshold: float, control: float,
                        ceiling: float = D_ACC_MAX) -> bool:
    """True when a pre-registered `delta >= threshold` verdict is arithmetically
    attainable against `control` on a metric bounded by `ceiling`. False means
    the falsifier is VACUOUS: it triggers DEAD for every possible mechanism, so
    running it measures nothing."""
    return threshold <= max_attainable_delta(control, ceiling)


def saturation(arm: float, leak_ceiling: float) -> float:
    """Distance from a measured arm to the panel's LEAK CEILING — the score the
    panel yields when the answer is handed to the model outright (anima v1's C3
    'V1 liveness' arm). A value near 0 means the panel is saturated: the arm is
    already scoring what a model gets for free, so the panel can no longer
    resolve anything above it. Negative means the arm beat the leak ceiling."""
    return leak_ceiling - arm


def bpe_merge_reachable(pair_count: int, min_pair_count: int) -> bool:
    """Closed-form reachability of a frequency-BPE merge. Greedy BPE only ever
    merges a symbol pair whose corpus count reaches `min_pair_count` (anima v1
    `morph2b.py` used 5). A pair below that floor is never merged at ANY vocab
    size K — enlarging K adds rarer merges from the eligible pool, it does not
    lower the eligibility floor. So atomicity of a sub-threshold morpheme is
    unreachable for frequency BPE by construction, not by tuning."""
    if min_pair_count < 1:
        raise ValueError(f"min_pair_count must be >= 1: {min_pair_count}")
    return pair_count >= min_pair_count


# --- falsifier harness --------------------------------------------------------

@dataclass
class Falsifier:
    """One pre-registered, measurable falsifier. `predicate(metrics) -> bool`
    returns True when the falsifier is TRIGGERED (hypothesis component refuted)."""

    name: str
    predicate: object  # callable(dict) -> bool
    desc: str = ""


def evaluate(metrics: dict, falsifiers: list) -> dict:
    """Run each falsifier against the measured metrics. A falsifier PASSes when
    it is NOT triggered. Returns a verdict ledger (all-stdlib, JSON-safe)."""
    results = []
    for f in falsifiers:
        triggered = bool(f.predicate(metrics))
        results.append(
            {"name": f.name, "triggered": triggered, "status": "FAIL" if triggered else "PASS"}
        )
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    return {
        "metrics": metrics,
        "falsifiers": results,
        "n_pass": n_pass,
        "n_total": len(results),
        "all_pass": n_pass == len(results),
    }
