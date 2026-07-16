#!/usr/bin/env python3
"""H_005 G3-a driver — LEARNED concord χ̂ replaces hand-computed χ; SUPPORT held FIXED.

H_004 (G-2) 🟢 SUPPORTED certified the parse-tension FIELD FORMAT (support × concord) as the causal
carrier of held-out honorific binding — but the concord χ was HAND-COMPUTED (gc.concord_field:
χ[i][j]=+1 if hon[i]==hon[j] else −1). G3-a asks: with the SUPPORT (proxy L→R/R→L disagreement,
gc.t_struct) held FIXED, can a TRAINED χ̂ = tanh(g(hon_i,hon_j)) learn those signs and reproduce the
field's causal power? One variable vs A-hand = the concord is learned, not hand-set.

Arms (χ̂ module/init/steps identical everywhere the field is learned):
  A-hand  : the H_004 A-duel field verbatim (numpy hand χ · anchor)
  A-χ̂     : SAME support, VALUES = tanh(g(hon_i,hon_j)) trained jointly on the drill
  C-χ̂plc  : SAME trained g, PERMUTED support (right values, wrong cells) — primary control
  C-scaf  : T̂≡0 (not-free floor) · C-perm : permuted-gold harness  (both = H_004 paths)

Metric = free-slot d_acc {0,1,2,4} (H_004 A2 amendment). Reuses train_h004 machinery verbatim.

⚠️ THE wiring risk (this session's 3-defect lesson): the χ̂ grad MUST reach g through the struct
injection. The smoke ASSERTS model.chi has a non-None gradient after one A-χ̂ drill backward — a
detached struct (silent) would leave g at init and the run would be a wiring failure, not a verdict.

Run:  python3 .../train_g3a.py --smoke          # wiring + grad-flow assert (CPU, minutes)
      python3 .../train_g3a.py --full-check      # $0 plumbing at d=64 on target device
      python3 .../train_g3a.py                    # full d=384 (ONLY after H_005 pre_register_frozen)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import numpy as np
import g1_core_check as gc
import train_h004 as H          # reuse verbatim: _item_T, _node_layout, _seq_bytes, _arm_tensor,
                                # dacc machinery, CPT, drill objective, free-slot metric, _load

ARMS_G3A = ["A-hand", "A-χ̂", "C-χ̂plc", "C-scaf", "C-perm"]


def _chi_hat(model, torch, hon, device):
    """χ̂ (n,n) = tanh(g([hon_i, hon_j])) — grad-enabled through model.chi (the learned concord g)."""
    n = len(hon)
    h = torch.tensor(np.asarray(hon), dtype=torch.float32, device=device)          # (n,)
    hi = h[:, None].expand(n, n)                                                     # (n,n) row = hon_i
    hj = h[None, :].expand(n, n)                                                     # (n,n) col = hon_j
    pair = torch.stack([hi, hj], dim=-1).reshape(n * n, 2)                           # (n*n,2)
    return torch.tanh(model.chi(pair)).reshape(n, n)                                 # (n,n) grad-enabled


def _hon_of(item):
    """The per-node honorific scalar the hand χ keys on — mirrors train_h004._item_T exactly."""
    if "conjuncts" in item:
        K = len(item["conjuncts"]); n = 3 * K + 2
        hon = np.zeros(n)
        for k, c in enumerate(item["conjuncts"]):
            hp = int(c["hp"]); pos1 = 1.0 if int(c["honored_position"]) == 1 else 0.0
            hon[3 * k] = hp; hon[3 * k + 1] = pos1; hon[3 * k + 2] = 1.0 - pos1
        return hon, n
    n = 5
    hon = np.array([item["honorific_present"],
                    1.0 if item["n1_lexeme"].endswith("님") else 0.0,
                    1.0 if item["n2_lexeme"].endswith("님") else 0.0, 0.0, 0.0])
    return hon, n


def _support(item, n):
    """The FIXED proxy-parser disagreement support (gc.t_struct) — identical to what hand χ multiplies."""
    if "conjuncts" in item:
        import build_tension as bt
        ha, hg = bt._heads()
        return gc.t_struct(n, ha, hg)
    return gc.t_struct(n, gc.HEAD_A, gc.HEAD_G)


def _struct_g3a(model, torch, item, arm, set_id, idx, seq_bytes_len, device):
    """(seq_bytes_len,64) struct rows — grad-enabled T̂ for the learned-χ̂ arms, numpy path otherwise.

    Returns (struct, gold). For A-χ̂/C-χ̂plc the struct carries grad to model.chi; the H_004 arms
    (A-hand=A-duel, C-scaf, C-perm) fall through to the sealed numpy path."""
    if arm not in ("A-χ̂", "C-χ̂plc"):
        h004_arm = {"A-hand": "A-duel", "C-scaf": "C-scaf", "C-perm": "C-perm"}[arm]
        st, gold, _ = H._struct_for(model, torch, item, h004_arm, set_id, idx, seq_bytes_len)
        return st.to(device), gold
    # learned-χ̂ arms
    hon, n = _hon_of(item)
    _, gold, _ = H._item_T(item)
    support = _support(item, n)                                                      # (n,n) numpy fixed
    if arm == "C-χ̂plc":                                                             # right values, wrong cells
        perm = np.random.default_rng(9000 + 1000 * set_id + idx).permutation(n)
        support = support[np.ix_(perm, perm)]
    sup = torch.tensor(support, dtype=torch.float32, device=device)
    That = sup * _chi_hat(model, torch, hon, device)                                 # (n,n) grad → g
    emb = model.node_embed(That)                                                     # (n,64) grad-enabled
    full = H._node_layout(item["surface"], n, gold, seq_bytes_len)
    struct = emb[torch.tensor(full, device=device)]                                 # (seq_len,64)
    return struct, gold


def _drill_batch_g3a(model, torch, items, arm, device, pad):
    """Grad-PRESERVING padded batch — struct is stacked via torch.cat (NOT in-place into a zeros leaf,
    which would silently DETACH χ̂'s gradient). tokens/targets/masks are numpy like H._drill_batch."""
    B = len(items)
    tok = np.zeros((B, pad), np.int64); tgt = np.zeros((B, pad), np.int64)
    mask = np.zeros((B, pad), np.float32); amask = np.zeros((B, pad), np.float32)
    structs = []
    for bi, (idx, item) in enumerate(items):
        surf_b, gold_b = H._seq_bytes(item)
        seq = (surf_b + gold_b)[:pad]
        st, gold = _struct_g3a(model, torch, item, arm, 0, idx, len(seq), device)    # (L,64) grad-enabled
        L = len(seq)
        tok[bi, :L] = list(seq); tgt[bi, :L - 1] = list(seq[1:]); mask[bi, :L - 1] = 1.0
        base = len(surf_b); K = len(gold_b) // 3
        a0 = max(base - 1, 0); a1 = min(base + 3 * K - 1, L - 1)
        if a1 > a0:
            amask[bi, a0:a1] = 1.0
        pad_rows = pad - st.shape[0]
        st_full = st if pad_rows <= 0 else torch.cat(
            [st, torch.zeros(pad_rows, st.shape[1], device=device)], dim=0)          # grad-preserving pad
        structs.append(st_full[:pad])
    struct = torch.stack(structs, dim=0)                                             # (B,pad,64) grad-enabled
    return (torch.tensor(tok, device=device), torch.tensor(tgt, device=device), struct,
            torch.tensor(mask, device=device), torch.tensor(amask, device=device))


def _dacc_g3a(model, torch, panel, arm, set_id, device, free_only=True):
    """free-slot d_acc using the g3a struct path (needed so A-χ̂/C-χ̂plc eval through the learned g)."""
    fs = H._panel_free_slots(panel) if free_only else None
    accs = []
    for i, it in enumerate(panel):
        surf_b, gold_b = H._seq_bytes(it); base = len(surf_b); K = len(gold_b) // 3
        seq = surf_b + gold_b
        with torch.no_grad():
            struct, gold = _struct_g3a(model, torch, it, arm, set_id, i, len(seq), device)
        slots = range(K) if fs is None else fs

        def _nll(byte_seq):
            toks = torch.tensor(list(byte_seq), dtype=torch.long, device=device)[None]
            with torch.no_grad():
                logp = torch.log_softmax(model(toks, struct=struct[None])["logits"][0], dim=0)
            return [sum(-logp[byte_seq[base + 3 * k + j], base + 3 * k + j - 1].item() for j in range(3))
                    for k in range(K)]
        ng = _nll(seq); corr = 0
        for k in slots:
            s = base + 3 * k
            alt = bytearray(seq); alt[s:s + 3] = H.ANS[1 - gold[k]].encode()
            if ng[k] <= _nll(bytes(alt))[k]:
                corr += 1
        accs.append(corr / len(list(slots)))
    return float(np.mean(accs))


def train_arm_g3a(arm, seed, cfg_tuple, drill, cpt_win, steps, device):
    torch, M, cfg, Struct = cfg_tuple
    torch.manual_seed(seed)
    model = Struct(cfg)
    model.chi = torch.nn.Sequential(torch.nn.Linear(2, 16), torch.nn.GELU(), torch.nn.Linear(16, 1))
    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=H._BASE_LR)     # includes model.chi ⇒ g trains jointly
    import torch.nn.functional as F
    cpt_steps, drill_steps = steps
    bs = 8 if device == "cpu" else 16
    for step in range(cpt_steps):
        idx = torch.randint(0, cpt_win.shape[0], (bs,)); w = cpt_win[idx].to(device)
        out = model(w[:, :-1], targets=w[:, 1:]); opt.zero_grad(); out["loss"].backward(); opt.step()
    d_items = list(enumerate(drill))
    if arm == "C-perm":
        import random
        drill_gold = [it["gold_pattern"] for _, it in d_items]
        perm = list(range(len(d_items))); random.Random(seed).shuffle(perm)
        d_items = [(idx, {**it, "gold_pattern": drill_gold[perm[i]]}) for i, (idx, it) in enumerate(d_items)]
    pad = 256 if cfg.d_model == 64 else 320
    ce_ans = torch.tensor(0.0); chi_grad_seen = False
    for step in range(drill_steps):
        bi = torch.randint(0, len(d_items), (min(bs, len(d_items)),))
        batch = [d_items[i] for i in bi.tolist()]
        tok, tgt, struct, mask, amask = _drill_batch_g3a(model, torch, batch, arm, device, pad)
        out = model(tok, struct=struct); logits = out["logits"]
        ce_tok = F.cross_entropy(logits[:, :, :-1].transpose(1, 2).reshape(-1, cfg.vocab_size),
                                 tgt[:, :-1].reshape(-1), reduction="none")
        m = mask[:, :-1].reshape(-1); am = amask[:, :-1].reshape(-1); sm = m - am
        ce_surf = (ce_tok * sm).sum() / sm.sum().clamp(min=1)
        ce_ans = (ce_tok * am).sum() / am.sum().clamp(min=1)
        loss = ce_surf + H.LAMBDA_ANS * ce_ans + out["aux_loss"]
        lr = H._drill_lr(step, drill_steps)
        for g in opt.param_groups:
            g["lr"] = lr
        opt.zero_grad(); loss.backward()
        if arm == "A-χ̂" and not chi_grad_seen:                    # wiring assert: g MUST receive grad
            chi_grad_seen = any(p.grad is not None and float(p.grad.abs().sum()) > 0
                                for p in model.chi.parameters())
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    model.eval()
    return model, float(ce_ans.item()), (chi_grad_seen if arm == "A-χ̂" else None)


def run_g3a(device, cpt_steps, drill_steps, tag, seeds=(0, 1)):
    torch, M, cfg, Struct = H._load(smoke=(drill_steps < 500))
    f2 = json.load(open(os.path.join(_HERE, "panel_f2doubleprime.json"), encoding="utf-8"))
    f1 = json.load(open(os.path.join(_HERE, "panel_f1prime.json"), encoding="utf-8"))
    drill = json.load(open(os.path.join(_HERE, "drill_grid_multi.json"), encoding="utf-8"))
    n_cpt = 2000 if tag == "check" else 120000
    cpt_win = H._cpt_windows(H._nsmc_lines(n_cpt), 128 if tag == "check" else 512, torch)
    results = {}
    for seed in seeds:
        for arm in ARMS_G3A:
            print(f"  training {arm}.s{seed} (CPT {cpt_steps} + drill {drill_steps}, d={cfg.d_model})…", flush=True)
            model, ce, chi_ok = train_arm_g3a(arm, seed, (torch, M, cfg, Struct), drill, cpt_win,
                                              (cpt_steps, drill_steps), device)
            rec = {"f2doubleprime": round(_dacc_g3a(model, torch, f2, arm, 1, device), 4),
                   "f1prime": round(_dacc_g3a(model, torch, f1, arm, 2, device), 4),
                   "drill_dacc": round(_dacc_g3a(model, torch, drill[:64], arm, 0, device), 4),
                   "ce_ans_final": round(ce, 4)}
            if chi_ok is not None:
                rec["chi_grad_seen"] = bool(chi_ok)
            results[f"{arm}.s{seed}"] = rec
            print(f"    {arm}.s{seed}: f2″={rec['f2doubleprime']} f1′={rec['f1prime']} "
                  f"drill={rec['drill_dacc']}" + (f" chi_grad={rec['chi_grad_seen']}" if chi_ok is not None else ""),
                  flush=True)
    out = {"config": {"d": cfg.d_model, "L": cfg.n_trunk_layers, "cpt_steps": cpt_steps,
                      "drill_steps": drill_steps, "tag": tag, "seeds": list(seeds), "metric": "free-slot"},
           "results": results}
    fn = "g3a_result_full.json" if tag == "full" else f"g3a_result_{tag}.json"
    with open(os.path.join(_HERE, fn), "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"wrote {fn}")
    return 0


def smoke(device="cpu"):
    """Wiring + THE grad-flow assert: after A-χ̂ drill, model.chi must have received gradient."""
    torch, M, cfg, Struct = H._load(smoke=True)
    drill = json.load(open(os.path.join(_HERE, "drill_grid_multi.json"), encoding="utf-8"))
    cpt_win = H._cpt_windows(H._nsmc_lines(2000), 128, torch)
    print("=" * 70 + "\nH_005 G3-a SMOKE — learned χ̂ wiring + grad-flow assert\n" + "=" * 70)
    model, ce, chi_ok = train_arm_g3a("A-χ̂", 0, (torch, M, cfg, Struct), drill[:32], cpt_win, (5, 30), device)
    print(f"  A-χ̂ trained 30 drill steps · ce_ans={round(ce,4)} · chi_grad_seen={chi_ok}")
    assert chi_ok, "WIRING FAILURE — model.chi received NO gradient; χ̂ is detached from the loss (g never trains)"
    # χ̂ must move a d_acc away from a fixed hand field: sanity that the two arms differ in code path
    d_chi = _dacc_g3a(model, torch, drill[:16], "A-χ̂", 0, device)
    print(f"  A-χ̂ drill-subset d_acc={round(d_chi,4)} (smoke scale; not a result)")
    print("\nSMOKE: GREEN — learned χ̂ grad reaches g (chi_grad_seen=True), struct path wired")
    return 0


def _frozen():
    card = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "HYPOTHESES", "cards",
                        "H_005_learned_chi_values.md")
    for ln in open(card, encoding="utf-8"):
        if ln.strip().startswith("pre_register_frozen:"):
            return "true" in ln.lower()
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full-check", action="store_true")
    a = ap.parse_args()
    import torch
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    if a.smoke:
        return smoke(device="cpu")
    if a.full_check:
        print(f"FULL-CHECK: run_g3a plumbing at d=64 on {device} …")
        return run_g3a(device, cpt_steps=20, drill_steps=120, tag="check", seeds=(0,))
    if not _frozen():
        print("FULL RUN refused: H_005 card pre_register_frozen != true (no-escape-hatch).")
        return 2
    print("FULL RUN — H_005 G3-a d=384 ×2seed ×5arm …", flush=True)
    return run_g3a(device, cpt_steps=8000, drill_steps=4000, tag="full", seeds=(0, 1))


if __name__ == "__main__":
    raise SystemExit(main())
