#!/usr/bin/env python3
"""H_003 panel builder + F7 audit — the pre-training don't-run gate.

Deterministic, stdlib-only, $0. Builds the H_003 depth-parity panels (f1', f2')
from a frozen verb inventory and template set, then runs the F7 audit from
`tool/anima_v4.py`: a panel is admissible only if the presence heuristic and the
template-shape heuristic BOTH score exactly 0.5 on it, and every polarity cell is
50/50. If F7 fails, NOTHING trains — the grid is rebuilt.

This runs BEFORE any GPU spend and BEFORE `frozen_at` is stamped. It does not
train anything; it validates that the panel cannot be solved without individuating
the negator token.

Run:  python3 state/h003_atomicity_fixed_codec_drill_2026-07-16/build_panels.py
"""

from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))


def _harness():
    sys.path.insert(0, os.path.join(_ROOT, "tool"))
    import anima_v4

    return anima_v4


# --- FROZEN inventory (resolved from measurement, see openparams.json) ---------
#
# Verbs: 8 positive-polarity + 8 negative-polarity stems, each rendered with a
# predicate span. Polarity is the review sentiment the bare predicate carries.
# These are the G-1 survivors; every stem must be 못-compatible (volitional) and
# read naturally in every template cell. Marked provisional until an operator
# grammar pass — but the F7 audit does not depend on the verbs' naturalness, only
# on the parity structure, so it can run now and gate the grid.
POS_VERBS = ["즐기", "몰입하", "집중하", "공감하", "추천하", "이해하", "기대하", "감탄하"]
NEG_VERBS = ["졸", "하품하", "딴생각하", "딴짓하", "후회하", "실망하", "지루해하", "짜증내"]

# Negators by attachment. FREE = pre-posed standalone adverb; BOUND = fused suffix.
# Held-out stem for f2' = 못 (measured 888 occurrences in NSMC ≥ 500; 아니 bound
# form measured 32 = too rare, so 못 is the held-out negator per the source
# contingency comment). Drilled = 안/않/아니.

# A panel item's gold_flip = number of negators mod 2. depth-2 = net no-flip.
# The template is the surface tail SHARED across depths so shape cannot leak parity.


def render(verb, cell):
    """Surface + (negator_count, template) for a (verb, cell).

    KEY CONSTRUCTION (why the earlier grid leaked and this one does not): D1 and
    D2 must SHARE their surface tail so no suffix-reader can recover the parity
    bit. We do that by placing the SECOND negator of a depth-2 item as a PRE-POSED
    FREE prefix, leaving the tail byte-identical to its depth-1 partner. The ONLY
    difference between the paired cells is the interior negator token — exactly the
    thing the atomicity hypothesis says a model must individuate. Suffix-neutrality
    is then verified over the REAL surface at every length by worst_suffix_leak.

    Two families, each a shared-tail minimal pair:
      FAMILY A (tests FREE held-out 못):  tail S1 = `…지는 않았다`
        A1 (D1, 1 neg 않):        이 영화 {V}지는 않았다
        A2 (D2, 못free + 않):     이 영화 못 {V}지는 않았다   ← held-out 못, free
      FAMILY B (tests BOUND held-out 못): tail S2 = `…지 못했다`
        B1 (D1, 1 neg 못-bound):  이 영화 {V}지 못했다        ← held-out 못, bound
        B2 (D2, 안free + 못-bd):  이 영화 안 {V}지 못했다
    """
    if cell == "A1":
        return f"이 영화 {verb}지는 않았다 => ", 1, "지는 않았다"
    if cell == "A2":
        return f"이 영화 못 {verb}지는 않았다 => ", 2, "지는 않았다"
    if cell == "B1":
        return f"이 영화 {verb}지 못했다 => ", 1, "지 못했다"
    if cell == "B2":
        return f"이 영화 안 {verb}지 못했다 => ", 2, "지 못했다"
    # f1' liveness families use only drilled negators (안/않), same shared-tail trick
    if cell == "L1":
        return f"이 영화 {verb}지는 않았다 => ", 1, "지는 않았다"
    if cell == "L2":
        return f"이 영화 안 {verb}지는 않았다 => ", 2, "지는 않았다"
    raise ValueError(f"unknown cell {cell}")


def build_panel(cells):
    """One item per (verb, polarity, cell). gold_flip = negator_count % 2. F7
    audits the FLIP structure (what the heuristics attack); the sentiment gold is
    pol XOR flip at eval time."""
    items = []
    for pol, verbs in ((1, POS_VERBS), (0, NEG_VERBS)):
        for v in verbs:
            for cell in cells:
                surface, ncount, tail = render(v, cell)
                items.append({
                    "cell": cell,
                    "verb": v,
                    "verb_polarity": pol,
                    "template": tail,
                    "negator_count": ncount,
                    "gold_flip": ncount % 2,
                    "balance_cell": f"{'D2' if ncount == 2 else 'D1'}|pol{pol}",
                    "surface": surface,
                })
    return items


# f2' = OOD verdict: held-out 못 free (A) and bound (B), each a shared-tail
# minimal pair. 2 D1 (A1,B1) + 2 D2 (A2,B2) → presence = 0.5.
F2_CELLS = ["A1", "A2", "B1", "B2"]
# f1' = liveness/ceiling: drilled negators only, same shared-tail trick.
F1_CELLS = ["L1", "L2"]


def main() -> int:
    h = _harness()
    f2 = build_panel(F2_CELLS)
    f1 = build_panel(F1_CELLS)

    report = {}
    ok = True
    for name, items in (("f2prime", f2), ("f1prime", f1)):
        # Balance keyed on the PARITY-neutral cell (polarity within depth).
        bal = h.label_balance(items, cell_key="balance_cell")
        presence = h.presence_heuristic_score(items)
        suffix = h.worst_suffix_leak(items)
        # depth split — presence heuristic only hits 0.5 if D1:D2 is balanced
        d1 = sum(1 for it in items if it["negator_count"] == 1)
        d2 = sum(1 for it in items if it["negator_count"] == 2)
        panel_ok = (
            abs(presence - 0.5) <= 0.02
            and abs(suffix["worst_suffix_score"] - 0.5) <= 0.02
            and all(abs(b - 0.5) <= 0.02 for b in bal.values())
        )
        ok = ok and panel_ok
        report[name] = {
            "n": len(items),
            "presence_heuristic": round(presence, 4),
            "worst_suffix_leak": suffix,
            "depth_split_D1_D2": [d1, d2],
            "balance_per_polarity_cell": {k: round(v, 4) for k, v in bal.items()},
            "F7_pass": panel_ok,
        }

    print("=" * 74)
    print("H_003 F7 panel audit — pre-training don't-run gate ($0, closed-form)")
    print("=" * 74)
    for name, r in report.items():
        print()
        print(f"[{name}] n={r['n']}  D1:D2={r['depth_split_D1_D2']}")
        print(f"  presence-heuristic score = {r['presence_heuristic']}  (must be 0.500 ± 0.02)")
        print(f"  worst surface-suffix leak = {r['worst_suffix_leak']['worst_suffix_score']}"
              f" (at len {r['worst_suffix_leak']['suffix_len']}, must be 0.500 ± 0.02)")
        print(f"  balance per polarity×depth cell: {r['balance_per_polarity_cell']}")
        print(f"  F7 {'PASS' if r['F7_pass'] else 'FAIL — grid must be rebuilt, nothing trains'}")
    print()
    print("F7 VERDICT:", "PASS — panel is heuristic-neutral, arms may be built"
          if ok else "FAIL — panel leaks a countable cue, DO NOT TRAIN")

    out = {"F7_pass": ok, "panels": report,
           "note": "gold_flip audited here = negator parity; sentiment gold = pol XOR flip at eval"}
    with open(os.path.join(_HERE, "f7_audit.json"), "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    # also emit the panels themselves for the freeze
    with open(os.path.join(_HERE, "panel_f2prime.json"), "w") as fh:
        json.dump(f2, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(_HERE, "panel_f1prime.json"), "w") as fh:
        json.dump(f1, fh, indent=2, ensure_ascii=False)
    print()
    print("wrote f7_audit.json, panel_f2prime.json, panel_f1prime.json")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
