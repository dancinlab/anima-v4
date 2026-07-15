#!/usr/bin/env python3
"""H_003 span-policy encoder — the one-variable lever, verified $0.

STATUS: v1 (shatter-by-token-id) is BROKEN — VERIFIED and RETAINED as the record.
The $0 verification (span_policy_verify_v1_BROKEN.out) caught that the negator's
atomic token is a frequency JAMO n-gram, not a morpheme: token 438 fires inside
아닐까, 안=286 inside 안녕/안전, 못=381 inside 연못. Shattering by token id degrades
non-negation words, breaking the one-variable property (the no-negator control
DIFFERED). The fix is to key the span policy on SYNTACTIC negation position
(standalone 안/못 eojeol, or 지-않/지-못하/지-아니 bound frames), pending. This file
is kept so the defect and its verification are reproducible; do not run it as the
drill encoder until the position-keyed policy replaces _shatter_negator_tokens.


The whole experiment rests on ONE claim about the encoding: A-atom and A-shat can
produce byte streams that are IDENTICAL everywhere EXCEPT inside matched negator
spans, where A-atom emits the negator's atomic token id and A-shat suppresses the
merges so the span becomes base-jamo singletons. If that byte-identity does not
hold, the two arms differ in more than one variable and the contrast is confounded
(adm.3). This script builds both encodings on a corpus slice and PROVES the
property by diffing the streams token-by-token — no training, no GPU, $0.

It consumes v1's jamo-BPE codec (morph2b) rather than reimplementing it (CLAUDE.md:
consume reusable implementation, own only the H_003-specific span policy here).

Run:  python3 state/h003_atomicity_fixed_codec_drill_2026-07-16/span_policy_encode.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_V1 = "/Users/mini/dancinlab/anima/state/nbind_curriculum/morph2b.py"
_NSMC = os.path.expanduser("~/g1_natem/nsmc_ratings_train.txt")

# The negators whose span policy differs between arms. Each is a jamo run that the
# frequency table already atomizes (probe.json: all four are single disjoint ids).
NEGATORS = {"안": "안", "않": "않", "못": "못", "아니": "아니"}


def load_v1_codec():
    """Import v1's morph2b as a module without running its argv parser."""
    sys.argv = ["morph2b.py", "--corpus", "/dev/null"]
    spec = importlib.util.spec_from_file_location("morph2b", _V1)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def encode_span_policy(m, line, merge_rank, tok2id, shatter: bool):
    """Encode one line to 2-byte tokens. When shatter=False (A-atom) the negator
    span merges normally → its atomic id fires. When shatter=True (A-shat) any
    eojeol that IS a bare negator (or contains one as a token) has that token's
    merges suppressed → emitted as base-jamo singleton tokens. Everything else is
    byte-identical between the two policies BY CONSTRUCTION: only eojeols matching a
    negator are touched."""
    out = bytearray()
    for syms, sp in m.eojeol_split(line):
        if sp:
            toks = [" "]
        else:
            toks = m.apply_merges(syms, merge_rank)
            if shatter:
                toks = _shatter_negator_tokens(m, toks, tok2id)
        for t in toks:
            i = tok2id.get(t)
            if i is None:
                for bb in t.replace("\x00", "").encode("utf-8", "replace"):
                    out += bytes((0, bb))
            else:
                out += bytes((i >> 8, i & 0xFF))
    return bytes(out)


def _negator_token_ids(m, tok2id):
    """The atomic token id of each negator (as the frequency table produced it)."""
    ids = {}
    for name, surf in NEGATORS.items():
        toks = m.apply_merges(m.to_jamo(surf), _MR)
        if len(toks) == 1 and toks[0] in tok2id:
            ids[name] = tok2id[toks[0]]
    return ids


def _shatter_negator_tokens(m, toks, tok2id):
    """Replace any negator atomic token with its base-jamo singleton tokens. The
    jamo singletons are the pre-merge symbols, which the codec passes through as
    OOV (2-byte-per-utf8) — the same collision-prone form raw utf-8 has, which is
    v1's stated reason the no-codec arm scored 0.617."""
    id2neg = {v: k for k, v in _NEG_IDS.items()}
    out = []
    for t in toks:
        tid = tok2id.get(t)
        if tid in id2neg:
            # expand the negator back to its base jamo symbols (singletons)
            out.extend(m.to_jamo(NEGATORS[id2neg[tid]]))
        else:
            out.append(t)
    return out


_MR = None
_NEG_IDS = None


def main() -> int:
    m = load_v1_codec()
    global _MR, _NEG_IDS

    lines = [l.split("\t")[1] for l in open(_NSMC, encoding="utf-8").read().splitlines()[1:20001]
             if len(l.split("\t")) > 2]
    merges = m.train_bpe(lines[:20000], 2048)
    merge_rank, tok2id, vocab = m.build_vocab(lines, merges)
    _MR = merge_rank
    _NEG_IDS = _negator_token_ids(m, tok2id)

    print("=" * 74)
    print("H_003 span-policy encoder — one-variable verification ($0, no training)")
    print("=" * 74)
    print(f"vocab={len(vocab)}  negator atomic ids={_NEG_IDS}")
    print()

    # Encode a sample of lines under both policies and diff.
    sample = [l for l in lines[:5000]
              if any(neg in l for neg in NEGATORS)][:2000]
    print(f"lines containing a negator (sample): {len(sample)}")

    n_ident = 0
    n_diff = 0
    total_bytes_atom = 0
    total_bytes_shat = 0
    diff_only_in_spans = True
    example = None
    for line in sample:
        a = encode_span_policy(m, line, merge_rank, tok2id, shatter=False)
        s = encode_span_policy(m, line, merge_rank, tok2id, shatter=True)
        total_bytes_atom += len(a)
        total_bytes_shat += len(s)
        if a == s:
            n_ident += 1
        else:
            n_diff += 1
            if example is None:
                example = line

    # Control: lines WITHOUT any negator must encode identically under both policies.
    no_neg = [l for l in lines[:5000] if not any(neg in l for neg in NEGATORS)][:500]
    control_identical = all(
        encode_span_policy(m, l, merge_rank, tok2id, False)
        == encode_span_policy(m, l, merge_rank, tok2id, True)
        for l in no_neg
    )

    print(f"negator lines: identical={n_ident}  differ={n_diff}")
    print(f"  (differ = the span policy changed the negator's encoding — expected)")
    print(f"CONTROL — {len(no_neg)} lines with NO negator: "
          f"{'ALL identical' if control_identical else 'SOME DIFFER (BUG)'}")
    print(f"  (this is the one-variable proof: absent a negator, the arms are byte-identical)")
    print(f"atom stream bytes={total_bytes_atom}  shat stream bytes={total_bytes_shat}"
          f"  (shat longer: jamo singletons cost more)")
    if example:
        print(f"example negator line: {example[:60]}")
    print()
    ok = control_identical and n_diff > 0
    print("VERDICT:", "one-variable lever HOLDS — arms differ ONLY inside negator spans"
          if ok else "BROKEN — arms differ outside negator spans, contrast confounded")

    out = {
        "vocab": len(vocab), "negator_atomic_ids": _NEG_IDS,
        "negator_lines_identical": n_ident, "negator_lines_differ": n_diff,
        "control_no_negator_all_identical": control_identical,
        "atom_bytes": total_bytes_atom, "shat_bytes": total_bytes_shat,
        "one_variable_holds": ok,
    }
    with open(os.path.join(_HERE, "span_policy_verify.json"), "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("wrote span_policy_verify.json")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
