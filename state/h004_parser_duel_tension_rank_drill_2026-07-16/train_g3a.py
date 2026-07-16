#!/usr/bin/env python3
"""H_005 G3-a driver — LEARNED concord χ̂ replaces hand χ; SUPPORT held FIXED.

H_004 (G-2) 🟢 SUPPORTED certified the parse-tension FIELD FORMAT (support × concord) as the causal
carrier of held-out honorific binding — but the concord χ was HAND-COMPUTED. G3-a asks: with the
SUPPORT fixed (proxy L→R/R→L disagreement gc.t_struct), can a TRAINED χ̂ learn those signs from what
the MODEL REPRESENTS and reproduce the field's causal power?

⚠️ χ̂ reads FROZEN-CPT-TRUNK per-node states φ (NOT raw hon) — Fable fidelity review (g3a_review):
g(raw hon) is a scaffolding-certifier (learning the equality of the two scalars χ_hand compares is
trivial and cannot fail → certifies the MLP, not the mechanism). The design of record uses
φ_i = per-node pooled trunk states, g = bilinear (~2-4k params), so the "can concord be recovered
from what the model represents" question is the real, falsifiable content — and G3-0d (probe φ→hon
≥0.9) becomes a live gate that can fail.

Arms: A-hand (H_004 field verbatim, anchor) · A-χ̂ (learned χ̂=g(φ) on fixed support) ·
C-χ̂plc (same trained g, permuted support) · C-scaf (T̂≡0) · C-perm (permuted-gold harness).
F1a = d_acc(A-χ̂)−d_acc(C-χ̂plc) ≥0.15 both · F1a′ = d_acc(A-χ̂) ≥ d_acc(A-hand)−0.05 both ·
F5 (carried) = the VALUES-matter control (strip resolution → d_acc must collapse). Metric = free-slot.

Run:  python3 .../train_g3a.py --smoke        # wiring: χ̂ grad→g reaches U/V · φ-encoder FROZEN
      python3 .../train_g3a.py --full-check    # $0 plumbing at d=64 on target device
      python3 .../train_g3a.py --g3-0d         # $0 admissibility gate: probe φ→hon bit ≥0.90
      python3 .../train_g3a.py                  # full d=384 (ONLY after H_005 pre_register_frozen)
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import numpy as np
import g1_core_check as gc
import train_h004 as H

ARMS_G3A = ["A-hand", "A-χ̂", "C-χ̂plc", "C-scaf", "C-perm"]
_R_CHI = 4                                       # bilinear rank for g (U,V ∈ R^{r×d})


class ChiBilinear:
    """χ̂[i][j] = tanh((U φ_i)·(V φ_j)/√r + b) — the learned concord g (~2rd+1 params). torch module."""
    def __init__(self, torch, d, r=_R_CHI):
        self.U = torch.nn.Linear(d, r, bias=False)
        self.V = torch.nn.Linear(d, r, bias=False)
        self.b = torch.nn.Parameter(torch.zeros(1))
        self.r = r

    def as_module(self, torch):
        m = torch.nn.Module()
        m.U, m.V, m.b = self.U, self.V, self.b
        return m


def _phi_encode(fm, torch, tokens):
    """Frozen forward to the PRE-READOUT state (B,C,T) — replicates the trunk with struct=None
    (answer-blind + injection-independent, both load-bearing per the review). No grad."""
    with torch.no_grad():
        x = fm.embed(tokens)                     # (B,T,C)
        x = x.transpose(1, 2)                    # (B,C,T)
        x = fm.embed_conv(x)
        for layer in fm.trunk:
            x = layer(x)
        x, _ = fm.moe(x)
        x = fm.norm_out(x)                       # (B,C,T) — same interface G3-b's shared f will read
    return x


def _node_phi(fm, torch, item, n, device):
    """(n, d) per-node φ = mean-pool of the frozen top-layer state over each node's SURFACE bytes
    (never over gold/answer bytes). A node with no surface span → φ=0."""
    surf_b = item["surface"].encode("utf-8")
    toks = torch.tensor(list(surf_b), dtype=torch.long, device=device)[None]
    x = _phi_encode(fm, torch, toks)[0]          # (C, L)
    nob = H._node_of_byte(item["surface"], n)    # (L,) node id per surface byte
    d = x.shape[0]
    phi = torch.zeros(n, d, device=device)
    nob_t = torch.tensor(nob, device=device)
    for k in range(n):
        sel = (nob_t == k).nonzero(as_tuple=True)[0]
        if len(sel):
            phi[k] = x[:, sel].mean(dim=1)
    return phi                                   # (n,d), no grad (from frozen encoder)


def _chi_hat(model, torch, phi):
    """χ̂ (n,n) grad-enabled through model.chi (U,V,b); φ is the frozen no-grad per-node state."""
    up = model.chi.U(phi); vp = model.chi.V(phi)                 # (n,r) each — grad → U,V
    return torch.tanh(up @ vp.t() / math.sqrt(_R_CHI) + model.chi.b)   # (n,n)


def _hon_n(item):
    if "conjuncts" in item:
        return 3 * len(item["conjuncts"]) + 2
    return 5


def _support(item, n):
    if "conjuncts" in item:
        import build_tension as bt
        ha, hg = bt._heads()
        return gc.t_struct(n, ha, hg)
    return gc.t_struct(n, gc.HEAD_A, gc.HEAD_G)


def _struct_g3a(model, phi_enc, torch, item, arm, set_id, idx, seq_bytes_len, device):
    """(seq_bytes_len,64) struct — grad-enabled T̂=support⊙χ̂(g(φ)) for χ̂ arms, numpy path otherwise."""
    if arm not in ("A-χ̂", "C-χ̂plc"):
        h004_arm = {"A-hand": "A-duel", "C-scaf": "C-scaf", "C-perm": "C-perm"}[arm]
        st, gold, _ = H._struct_for(model, torch, item, h004_arm, set_id, idx, seq_bytes_len)
        return st.to(device), gold
    n = _hon_n(item)
    _, gold, _ = H._item_T(item)
    support = _support(item, n)
    if arm == "C-χ̂plc":                                          # right values, wrong cells
        perm = np.random.default_rng(9000 + 1000 * set_id + idx).permutation(n)
        support = support[np.ix_(perm, perm)]
    phi = _node_phi(phi_enc, torch, item, n, device)             # (n,d) frozen
    sup = torch.tensor(support, dtype=torch.float32, device=device)
    That = sup * _chi_hat(model, torch, phi)                     # (n,n) grad → g
    emb = model.node_embed(That)
    full = H._node_layout(item["surface"], n, gold, seq_bytes_len)
    return emb[torch.tensor(full, device=device)], gold


def _drill_batch_g3a(model, phi_enc, torch, items, arm, device, pad):
    """Grad-PRESERVING padded batch (torch.cat, not in-place into a zeros leaf → would detach g)."""
    B = len(items)
    tok = np.zeros((B, pad), np.int64); tgt = np.zeros((B, pad), np.int64)
    mask = np.zeros((B, pad), np.float32); amask = np.zeros((B, pad), np.float32)
    structs = []
    for bi, (idx, item) in enumerate(items):
        surf_b, gold_b = H._seq_bytes(item)
        seq = (surf_b + gold_b)[:pad]
        st, gold = _struct_g3a(model, phi_enc, torch, item, arm, 0, idx, len(seq), device)
        L = len(seq)
        tok[bi, :L] = list(seq); tgt[bi, :L - 1] = list(seq[1:]); mask[bi, :L - 1] = 1.0
        base = len(surf_b); K = len(gold_b) // 3
        a0 = max(base - 1, 0); a1 = min(base + 3 * K - 1, L - 1)
        if a1 > a0:
            amask[bi, a0:a1] = 1.0
        pad_rows = pad - st.shape[0]
        st_full = st if pad_rows <= 0 else torch.cat(
            [st, torch.zeros(pad_rows, st.shape[1], device=device)], dim=0)
        structs.append(st_full[:pad])
    struct = torch.stack(structs, dim=0)
    return (torch.tensor(tok, device=device), torch.tensor(tgt, device=device), struct,
            torch.tensor(mask, device=device), torch.tensor(amask, device=device))


def _dacc_g3a(model, phi_enc, torch, panel, arm, set_id, device, free_only=True):
    fs = H._panel_free_slots(panel) if free_only else None
    accs = []
    for i, it in enumerate(panel):
        surf_b, gold_b = H._seq_bytes(it); base = len(surf_b); K = len(gold_b) // 3
        seq = surf_b + gold_b
        with torch.no_grad():
            struct, gold = _struct_g3a(model, phi_enc, torch, it, arm, set_id, i, len(seq), device)
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
    chi = ChiBilinear(torch, cfg.d_model); model.chi = chi.as_module(torch)
    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=H._BASE_LR)
    import torch.nn.functional as F
    cpt_steps, drill_steps = steps
    bs = 8 if device == "cpu" else 16
    for step in range(cpt_steps):                                 # CPT (struct=None, trains the trunk)
        idx = torch.randint(0, cpt_win.shape[0], (bs,)); w = cpt_win[idx].to(device)
        out = model(w[:, :-1], targets=w[:, 1:]); opt.zero_grad(); out["loss"].backward(); opt.step()
    phi_enc = copy.deepcopy(model).eval()                         # FROZEN post-CPT trunk = φ encoder
    for p in phi_enc.parameters():
        p.requires_grad_(False)
    d_items = list(enumerate(drill))
    if arm == "C-perm":
        import random
        dg = [it["gold_pattern"] for _, it in d_items]
        perm = list(range(len(d_items))); random.Random(seed).shuffle(perm)
        d_items = [(idx, {**it, "gold_pattern": dg[perm[i]]}) for i, (idx, it) in enumerate(d_items)]
    pad = 256 if cfg.d_model == 64 else 320
    ce_ans = torch.tensor(0.0); chi_grad_seen = False; phi_frozen_ok = True
    for step in range(drill_steps):
        bi = torch.randint(0, len(d_items), (min(bs, len(d_items)),))
        batch = [d_items[i] for i in bi.tolist()]
        tok, tgt, struct, mask, amask = _drill_batch_g3a(model, phi_enc, torch, batch, arm, device, pad)
        out = model(tok, struct=struct); logits = out["logits"]
        ce_tok = F.cross_entropy(logits[:, :, :-1].transpose(1, 2).reshape(-1, cfg.vocab_size),
                                 tgt[:, :-1].reshape(-1), reduction="none")
        m = mask[:, :-1].reshape(-1); am = amask[:, :-1].reshape(-1); sm = m - am
        ce_surf = (ce_tok * sm).sum() / sm.sum().clamp(min=1)
        ce_ans = (ce_tok * am).sum() / am.sum().clamp(min=1)
        loss = ce_surf + H.LAMBDA_ANS * ce_ans + out["aux_loss"]
        for g in opt.param_groups:
            g["lr"] = H._drill_lr(step, drill_steps)
        opt.zero_grad(); loss.backward()
        if arm == "A-χ̂" and not chi_grad_seen:                   # g (U,V,b) MUST receive gradient
            chi_grad_seen = any(p.grad is not None and float(p.grad.abs().sum()) > 0
                                for p in model.chi.parameters())
            phi_frozen_ok = all(p.grad is None for p in phi_enc.parameters())   # frozen = frozen
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    model.eval()
    return model, phi_enc, float(ce_ans.item()), (chi_grad_seen if arm == "A-χ̂" else None), phi_frozen_ok


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
            model, phi_enc, ce, chi_ok, phi_ok = train_arm_g3a(
                arm, seed, (torch, M, cfg, Struct), drill, cpt_win, (cpt_steps, drill_steps), device)
            rec = {"f2doubleprime": round(_dacc_g3a(model, phi_enc, torch, f2, arm, 1, device), 4),
                   "f1prime": round(_dacc_g3a(model, phi_enc, torch, f1, arm, 2, device), 4),
                   "drill_dacc": round(_dacc_g3a(model, phi_enc, torch, drill[:64], arm, 0, device), 4),
                   "ce_ans_final": round(ce, 4)}
            if chi_ok is not None:
                rec["chi_grad_seen"] = bool(chi_ok); rec["phi_frozen_ok"] = bool(phi_ok)
            results[f"{arm}.s{seed}"] = rec
            print(f"    {arm}.s{seed}: f2″={rec['f2doubleprime']} f1′={rec['f1prime']} "
                  f"drill={rec['drill_dacc']}" + (f" chi_grad={rec['chi_grad_seen']} phi_frozen={rec['phi_frozen_ok']}"
                  if chi_ok is not None else ""), flush=True)
    out = {"config": {"d": cfg.d_model, "L": cfg.n_trunk_layers, "cpt_steps": cpt_steps,
                      "drill_steps": drill_steps, "tag": tag, "seeds": list(seeds), "metric": "free-slot",
                      "chi": "bilinear φ=frozen-trunk-pooled"},
           "results": results}
    fn = "g3a_result_full.json" if tag == "full" else f"g3a_result_{tag}.json"
    with open(os.path.join(_HERE, fn), "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"wrote {fn}")
    return 0


def g3_0d(device):
    """$0 admissibility gate: is the honorific bit recoverable (≥0.90) from the frozen d=384 CPT trunk's
    per-node φ? If not, χ̂=g(φ) has nothing to read and G3-a is UNBUILT (the gate doing its job)."""
    from sklearn.linear_model import LogisticRegression
    torch, M, cfg, Struct = H._load(smoke=False)                 # d=384 real trunk
    drill = json.load(open(os.path.join(_HERE, "drill_grid_multi.json"), encoding="utf-8"))
    cpt_win = H._cpt_windows(H._nsmc_lines(120000), 512, torch)
    torch.manual_seed(0); model = Struct(cfg)
    model.chi = ChiBilinear(torch, cfg.d_model).as_module(torch); model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=H._BASE_LR)
    print(f"g3-0d: CPT 8000 (d=384) then probe φ→hon bit … (device={device})", flush=True)
    for step in range(8000):
        idx = torch.randint(0, cpt_win.shape[0], (16,)); w = cpt_win[idx].to(device)
        out = model(w[:, :-1], targets=w[:, 1:]); opt.zero_grad(); out["loss"].backward(); opt.step()
    fm = model.eval()
    X, y = [], []
    for it in drill[:200]:
        n = _hon_n(it)
        phi = _node_phi(fm, torch, it, n, device).cpu().numpy()
        for k, c in enumerate(it["conjuncts"]):
            X.append(phi[3 * k]); y.append(int(c["hp"]))          # hp = the honorific bit at the head node
    X = np.asarray(X); y = np.asarray(y); ntr = int(0.7 * len(X))
    clf = LogisticRegression(max_iter=1000).fit(X[:ntr], y[:ntr])
    acc = float(clf.score(X[ntr:], y[ntr:]))
    ok = acc >= 0.90
    json.dump({"probe_acc": round(acc, 4), "threshold": 0.90, "pass": ok, "n": len(X)},
              open(os.path.join(_HERE, "g3_0d_result.json"), "w"), indent=2)
    print(f"\nG3-0d probe φ→hon: held-out acc={round(acc,4)} (≥0.90: {'PASS' if ok else 'FAIL'}) · "
          f"{'χ̂ can read concord ⇒ build' if ok else 'φ washes out the concord ⇒ G3-a UNBUILT'}")
    return 0 if ok else 1


def smoke(device="cpu"):
    torch, M, cfg, Struct = H._load(smoke=True)
    drill = json.load(open(os.path.join(_HERE, "drill_grid_multi.json"), encoding="utf-8"))
    cpt_win = H._cpt_windows(H._nsmc_lines(2000), 128, torch)
    print("=" * 70 + "\nH_005 G3-a SMOKE — learned χ̂=g(φ), φ=frozen-trunk-pooled\n" + "=" * 70)
    model, phi_enc, ce, chi_ok, phi_ok = train_arm_g3a(
        "A-χ̂", 0, (torch, M, cfg, Struct), drill[:32], cpt_win, (5, 30), device)
    print(f"  A-χ̂ 30 drill steps · ce_ans={round(ce,4)} · chi_grad_seen={chi_ok} · phi_frozen_ok={phi_ok}")
    assert chi_ok, "WIRING FAILURE — g (U,V,b) got NO gradient; χ̂ detached from loss"
    assert phi_ok, "WIRING FAILURE — φ-encoder received gradient; the frozen trunk is NOT frozen"
    print("\nSMOKE: GREEN — χ̂ grad reaches g AND φ-encoder stays frozen (no raw-hon shortcut)")
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
    ap.add_argument("--g3-0d", action="store_true")
    a = ap.parse_args()
    import torch
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    if a.smoke:
        return smoke(device="cpu")
    if a.g3_0d:
        return g3_0d(device)
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
