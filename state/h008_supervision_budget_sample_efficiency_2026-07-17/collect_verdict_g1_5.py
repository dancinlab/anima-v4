#!/usr/bin/env python3
"""H_008 G-1.5 band-existence verdict — reads g1_5_result.json, applies the FROZEN band logic ($0).

The trained-control-ceiling gate's decision:
  - a budget k* is a BAND CANDIDATE iff C-dup f2_dacc ∈ [0.60, 0.80] at that k, BOTH seeds present.
  - cross-seed STABILITY: |f2(s0) − f2(s1)| ≤ 0.1614 (H_003's measured spread) AND both in band.
  - K1 (CLOSE near-$0): no k* is a cross-seed-stable band candidate ⇒ the band does not exist ⇒ H_008
    closes, campaign stays CONCLUDED. (This is the honest measured shut of the reopen door.)
  - K1b (CLOSE): a band k* exists but at it C-shuf > 0.80 OR C-scaf > 0.80 ⇒ the scarce-label
    generic-aux transfer story has no headroom for the mechanism separation.
  - PROCEED-TO-FREEZE: a cross-seed-stable band k* exists AND C-scaf ≤ 0.80 AND C-shuf ≤ 0.80 at k*.
    Then E-anchors are instantiated from these runs and the verdict run may be frozen.
"""
from __future__ import annotations

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_R = os.path.join(_HERE, "g1_5_result.json")
BAND = (0.60, 0.80)
SPREAD = 0.1614


def _by(jobs, arm):
    d = {}
    for r in jobs:
        if r["arm"] == arm:
            d.setdefault(r["k"], {})[r["seed"]] = r["f2_dacc"]
    return d


def main() -> int:
    if not os.path.exists(_R):
        print(f"NO RESULT YET — {_R} missing. Run train_g1_5.py --phase a first.")
        return 2
    data = json.load(open(_R))
    jobs = data["jobs"]
    cdup, cscaf, cshuf = _by(jobs, "C-dup"), _by(jobs, "C-scaf"), _by(jobs, "C-shuf")

    print("=" * 78 + "\nH_008 G-1.5 band-existence verdict\n" + "=" * 78)
    print(f"band=[{BAND[0]},{BAND[1]}] · cross-seed stability ≤ {SPREAD}\n")
    print("C-dup f2_dacc by budget:")
    band_candidates = []
    for k in sorted(cdup):
        seeds = cdup[k]
        vals = " ".join(f"s{s}={seeds[s]}" for s in sorted(seeds))
        both = len(seeds) >= 2
        in_band = all(BAND[0] <= v <= BAND[1] for v in seeds.values())
        stable = both and (max(seeds.values()) - min(seeds.values())) <= SPREAD
        tag = ""
        if in_band and both and stable:
            tag = "← STABLE BAND CANDIDATE"; band_candidates.append(k)
        elif in_band:
            tag = "← in band (needs 2nd seed / stability)"
        print(f"  k={k:>3}: {vals}  {tag}")

    verdict, kstar = None, None
    if not any(BAND[0] <= v <= BAND[1] for k in cdup for v in cdup[k].values()):
        verdict = ("K1 (CLOSE near-$0) — NO budget places the trained control in [0.60,0.80]; the band does "
                   "not exist on this panel/scale. H_008 reopen door shut MEASURED; campaign stays CONCLUDED.")
    elif not band_candidates:
        verdict = ("INCOMPLETE / K1-leaning — some k in band on one seed but no CROSS-SEED-STABLE candidate "
                   "yet. Run --phase b at the in-band k. If no k stabilizes in band ⇒ K1.")
    else:
        kstar = band_candidates[0]
        sc = cscaf.get(kstar, {}); sh = cshuf.get(kstar, {})
        if not sc or not sh:
            verdict = (f"BAND FOUND at k*={kstar} (C-dup stable in band) — run --phase c (C-scaf + C-shuf @ "
                       f"k*) to price the placebo before any mechanism arm.")
        elif max(sh.values()) > 0.80 or max(sc.values()) > 0.80:
            verdict = (f"K1b (CLOSE) — band at k*={kstar} but C-scaf={sc} / C-shuf={sh} exceeds 0.80: "
                       f"scarce-label generic-aux transfer leaves no headroom for the mechanism separation.")
        else:
            verdict = (f"PROCEED-TO-FREEZE — cross-seed-stable band at k*={kstar}, C-scaf={sc} ≤ 0.80, "
                       f"C-shuf={sh} ≤ 0.80. Instantiate E-anchors from these runs; the verdict run may freeze.")

    print("\nVERDICT:", verdict)
    json.dump({"verdict": verdict, "k_star": kstar, "band_candidates": band_candidates,
               "cdup": cdup, "cscaf": cscaf, "cshuf": cshuf},
              open(os.path.join(_HERE, "verdict_g1_5.json"), "w"), indent=2, ensure_ascii=False)
    print("wrote verdict_g1_5.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
