#!/usr/bin/env python3
"""H_004 G-2 training driver — parse-tension resolver + 5 arms (DESIGN_g2_training_fable5.md).

trunk = H_003 CLMConvMoE (d=384 L=4) on RAW UTF-8 (codec axis closed, H_003 🔴); a small resolver
R (32.5k params) ingests the per-item n×n tension field T by relative OFFSET bucket and injects a
per-node structure embedding PRE-trunk (nc5: R is an input of the same forward used at eval). The
five arms differ in EXACTLY ONE thing — the map `T_item → tensor handed to R`:
    A-duel  T            A-rank1  rank1_tiebreak(T)    C-plc  Π T Πᵀ
    C-scaf  0            C-perm   T (+ drill gold shuffled)

⚠️ RUN GATE: this driver's ~5h d=384 run is gated on native-operator G-1 + `pre_register_frozen`.
The `--smoke` d=64 path is $0 wiring verification only and needs no freeze.

Run:  python3 .../train_h004.py --smoke      # wiring (minutes)
      python3 .../train_h004.py               # full d=384 (ONLY after freeze)
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ANIMA = "/Users/mini/dancinlab/anima"
_NSMC = os.path.join(_ANIMA, "state", "nbind_curriculum", "ratings_train.txt")
sys.path.insert(0, _HERE)
sys.path.insert(0, _ANIMA)

import numpy as np
import g1_core_check as gc          # t_struct · concord_field · rank1_tiebreak · offtop · HEAD_A/HEAD_G
import build_tension as bt          # _heads() for K=6

ANS = ("앞", "뒤")
AP, TU = ANS[0].encode(), ANS[1].encode()      # 3 bytes each; differ at byte 0
assert len(AP) == len(TU) == 3 and AP[0] != TU[0]


# ---------------------------------------------------------------- tension per item
def _item_T(item):
    """(T ndarray (n,n), gold_flips list, n) for a multi (conjuncts) or single-bind item."""
    if "conjuncts" in item:                         # K=6 multi
        K = len(item["conjuncts"]); n = 3 * K + 2
        ha, hg = bt._heads()
        hon = np.zeros(n)
        gold = []
        for k, c in enumerate(item["conjuncts"]):
            hp = int(c["hp"]); pos1 = 1.0 if int(c["honored_position"]) == 1 else 0.0
            hon[3 * k] = hp; hon[3 * k + 1] = pos1; hon[3 * k + 2] = 1.0 - pos1
            gold.append(int(c["gold_flip"]))
        T = gc.concord_field(gc.t_struct(n, ha, hg), hon)
        return T, gold, n
    # single-bind f1' (K=1, n=5)
    n = 5
    hon = np.array([item["honorific_present"],
                    1.0 if item["n1_lexeme"].endswith("님") else 0.0,
                    1.0 if item["n2_lexeme"].endswith("님") else 0.0, 0.0, 0.0])
    T = gc.concord_field(gc.t_struct(n, gc.HEAD_A, gc.HEAD_G), hon)
    return T, [int(item["gold_flip"])], n


def _arm_tensor(T, arm, set_id, idx):
    if arm in ("A-duel", "C-perm"):
        return T
    if arm == "A-rank1":
        return gc.rank1_tiebreak(T)
    if arm == "C-scaf":
        return np.zeros_like(T)
    if arm == "C-plc":
        n = T.shape[0]
        perm = np.random.default_rng(9000 + 1000 * set_id + idx).permutation(n)
        return T[np.ix_(perm, perm)]
    raise ValueError(arm)


# ---------------------------------------------------------------- byte↔node alignment
def _node_of_byte(surface, n):
    """Map each byte index of surface.encode() (+ answer region) to its node id (0..n-1)."""
    eojeols = surface.split(" ")
    # surface = "e0 e1 ... e_{n-2} " ends with '=> ' → split gives n tokens + trailing '' (from final space)
    toks = [t for t in eojeols if t != ""]
    assert len(toks) == n, (len(toks), n, surface)
    b = surface.encode("utf-8")
    node = np.full(len(b), n - 1, dtype=np.int64)     # default → ANS node (answer region maps here too)
    pos = 0
    for i, tok in enumerate(toks):
        piece = (tok + " ").encode("utf-8")           # each eojeol owns its trailing space
        node[pos:pos + len(piece)] = i
        pos += len(piece)
    return node                                        # length == len(surface bytes); answer bytes handled by caller


# ---------------------------------------------------------------- model (subclass)
def _load(smoke):
    import torch
    import core.model as M
    d, L, E = (64, 2, 2) if smoke else (384, 4, 3)
    cfg = M.CLMConfig(vocab_size=256, d_model=d, n_trunk_layers=L, n_experts=E)

    class CLMConvMoEStruct(M.CLMConvMoE):
        def __init__(self, cfg):
            super().__init__(cfg)
            self.r_out = torch.nn.Embedding(19, 32)
            self.r_in = torch.nn.Embedding(19, 32)
            self.rmlp = torch.nn.Sequential(torch.nn.Linear(32, 64), torch.nn.GELU(),
                                            torch.nn.Linear(64, 64))
            self.rproj = torch.nn.Linear(64, cfg.d_model)

        def node_embed(self, T):                       # T: (n,n) tensor → (n,64)
            n = T.shape[0]
            delta = torch.arange(n)[None, :] - torch.arange(n)[:, None]
            b = (delta.clamp(-9, 9) + 9).to(T.device)
            h = (T.unsqueeze(-1) * self.r_out(b)).sum(1) + (T.t().unsqueeze(-1) * self.r_in(b)).sum(1)
            return self.rmlp(h)                         # (n,64)

        def forward(self, tokens, targets=None, struct=None):
            import torch.nn.functional as F
            x = self.embed(tokens)                      # (B,T,C)
            if struct is not None:
                x = x + self.rproj(struct)              # THE injection (pre-trunk)
            x = x.transpose(1, 2)
            x = self.embed_conv(x)
            for layer in self.trunk:
                x = layer(x)
            x, stats = self.moe(x)
            x = self.norm_out(x)
            logits = self.readout(x)                    # (B,V,T)
            out = {"logits": logits, "aux_loss": stats.aux_loss}
            if targets is not None:
                ce = F.cross_entropy(logits.transpose(1, 2).reshape(-1, self.cfg.vocab_size),
                                     targets.reshape(-1))
                out["loss"] = ce + stats.aux_loss
                out["ce_loss"] = ce
            return out

    return torch, M, cfg, CLMConvMoEStruct


# ---------------------------------------------------------------- struct tensor for an item
def _struct_for(model, torch, item, arm, set_id, idx, seq_bytes_len):
    """(seq_bytes_len, 64) struct rows: node_embed(arm_tensor(T)) scattered by node_of_byte."""
    T, gold, n = _item_T(item)
    Ta = _arm_tensor(T, arm, set_id, idx)
    emb = model.node_embed(torch.tensor(Ta, dtype=torch.float32))    # (n,64)
    surf = item["surface"]
    nob = _node_of_byte(surf, n)                                     # len == len(surf bytes)
    full = np.full(seq_bytes_len, n - 1, dtype=np.int64)            # default → ANS node
    full[:len(nob)] = nob
    # answer byte for slot k → its own conjunct verb node (3k), so the answer position carries
    # slot-k's RESOLVED structure directly (a short read), not a ~200-byte propagation through a
    # causal trunk. A-duel gets all 6 slots' signs; A-rank1 only slot 0's (row-0 truncation);
    # C-scaf gets the zero-field. The arm separation is preserved; the injection becomes testable.
    base = len(surf.encode("utf-8"))
    K = len(gold)
    node_k = (lambda k: 3 * k) if K > 1 else (lambda k: 0)
    for k in range(K):
        # positions [base+3k-1 .. base+3k+2]: the position that PREDICTS answer byte k (base+3k-1,
        # whose hidden state feeds logits[:, that pos] for seq[base+3k]) AND the 3 answer bytes.
        lo = max(base + 3 * k - 1, 0)
        full[lo: base + 3 * k + 3] = node_k(k)
    struct = emb[torch.tensor(full)]                                # (seq_bytes_len, 64)
    return struct, gold, T


# ---------------------------------------------------------------- forced-choice d_acc
def _seq_bytes(item):
    return item["surface"].encode("utf-8"), item["gold_pattern"].encode("utf-8") if "gold_pattern" in item \
        else item["gold_token"].encode("utf-8")


def _dacc_item(model, torch, item, arm, set_id, idx, device):
    surf_b, gold_b = _seq_bytes(item)
    base = len(surf_b)
    K = len(gold_b) // 3
    seq = surf_b + gold_b
    struct, gold, _ = _struct_for(model, torch, item, arm, set_id, idx, len(seq))
    struct = struct.to(device)

    def _nll_slots(byte_seq):
        toks = torch.tensor(list(byte_seq), dtype=torch.long, device=device)[None]
        with torch.no_grad():
            out = model(toks, struct=struct[None])
        logp = torch.log_softmax(out["logits"][0], dim=0)           # (V,T)
        nll = []
        for k in range(K):
            s = base + 3 * k
            tot = 0.0
            for j in range(3):                                      # 3 bytes of the candidate
                tot += -logp[byte_seq[s + j], s + j - 1].item()     # predict byte at pos p from p-1
            nll.append(tot)
        return nll
    nll_gold = _nll_slots(seq)
    correct = 0
    for k in range(K):
        s = base + 3 * k
        flip = ANS[1 - gold[k]].encode("utf-8")
        alt = bytearray(seq); alt[s:s + 3] = flip
        nll_alt_k = _nll_slots(bytes(alt))[k]
        if nll_gold[k] <= nll_alt_k:
            correct += 1
    return correct / K


def dacc_panel(model, torch, panel, arm, set_id, device):
    return float(np.mean([_dacc_item(model, torch, panel[i], arm, set_id, i, device)
                          for i in range(len(panel))]))


# ---------------------------------------------------------------- CPT (raw utf-8 concat)
def _nsmc_lines(n):
    if not os.path.exists(_NSMC):
        return ["영화 재미있다 좋다"] * n            # smoke fallback if corpus absent
    raw = open(_NSMC, encoding="utf-8").read().splitlines()[1:]
    return [l.split("\t")[1] for l in raw if len(l.split("\t")) > 2][:n]


def _cpt_windows(lines, seq_len, torch):
    stream = ("\n".join(lines)).encode("utf-8")
    arr = np.frombuffer(stream, dtype=np.uint8)
    nwin = len(arr) // seq_len
    return torch.tensor(arr[:nwin * seq_len].reshape(nwin, seq_len).astype(np.int64))


# ---------------------------------------------------------------- drill (per-item padded)
def _drill_batch(model, torch, items, arm, seed, device, pad):
    """One padded batch: (tokens, targets, struct, mask) for masked external CE."""
    B = len(items)
    tok = np.zeros((B, pad), np.int64); tgt = np.zeros((B, pad), np.int64)
    mask = np.zeros((B, pad), np.float32)
    struct = torch.zeros(B, pad, 64, device=device)
    for bi, (idx, item) in enumerate(items):
        surf_b, gold_b = _seq_bytes(item)
        seq = (surf_b + gold_b)[:pad]
        st, gold, _ = _struct_for(model, torch, item, arm, 0, idx, len(seq))
        L = len(seq)
        tok[bi, :L] = list(seq)
        tgt[bi, :L - 1] = list(seq[1:])
        mask[bi, :L - 1] = 1.0                            # predict-next positions
        struct[bi, :st.shape[0]] = st.to(device)
    return (torch.tensor(tok, device=device), torch.tensor(tgt, device=device),
            struct, torch.tensor(mask, device=device))


def train_arm(arm, seed, cfg_tuple, panels, drill, cpt_win, steps, device):
    torch, M, cfg, Struct = cfg_tuple
    torch.manual_seed(seed)
    model = Struct(cfg).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=3e-4)
    import torch.nn.functional as F
    # CPT (struct=None, identical for all arms)
    cpt_steps, drill_steps = steps
    bs = 8 if device == "cpu" else 16
    for step in range(cpt_steps):
        idx = torch.randint(0, cpt_win.shape[0], (bs,))
        w = cpt_win[idx].to(device)
        out = model(w[:, :-1], targets=w[:, 1:])
        opt.zero_grad(); out["loss"].backward(); opt.step()
    # drill (per-item padded, external masked CE; per-arm struct)
    d_items = list(enumerate(drill))
    drill_gold = [it["gold_pattern"] for _, it in d_items]
    if arm == "C-perm":
        perm = list(range(len(d_items)))
        random.Random(seed).shuffle(perm)
        d_items = [(d_items[i][0], dict(d_items[j], gold_pattern=drill_gold[j]))
                   for i, j in enumerate(perm)]  # shuffle gold across items (whole 6-tok units)
    pad = 256 if cfg.d_model == 64 else 320    # must fit the longest K=6 drill item (~250 bytes)
    for step in range(drill_steps):
        bi = torch.randint(0, len(d_items), (min(bs, len(d_items)),))
        batch = [d_items[i] for i in bi.tolist()]
        tok, tgt, struct, mask = _drill_batch(model, torch, batch, arm, seed, device, pad)
        out = model(tok, struct=struct)
        logits = out["logits"]                                       # (B,V,T)
        ce = F.cross_entropy(logits[:, :, :-1].transpose(1, 2).reshape(-1, cfg.vocab_size),
                             tgt[:, :-1].reshape(-1), reduction="none")
        ce = (ce * mask[:, :-1].reshape(-1)).sum() / mask[:, :-1].sum().clamp(min=1)
        loss = ce + out["aux_loss"]
        opt.zero_grad(); loss.backward(); opt.step()
    model.eval()
    return model, float(ce.item())


# ---------------------------------------------------------------- smoke wiring checks
def smoke(device="cpu"):
    torch, M, cfg, Struct = _load(smoke=True)
    f2 = json.load(open(os.path.join(_HERE, "panel_f2doubleprime.json"), encoding="utf-8"))
    f1 = json.load(open(os.path.join(_HERE, "panel_f1prime.json"), encoding="utf-8"))
    drill = json.load(open(os.path.join(_HERE, "drill_grid_multi.json"), encoding="utf-8"))
    print("=" * 70); print("H_004 G-2 driver — SMOKE (wiring only, $0)"); print("=" * 70)

    # WIRING-1 alignment
    for name, panel, K in [("f2''", f2, 6), ("drill", drill, 6), ("f1'", f1, 1)]:
        it = panel[0]
        n = 3 * K + 2
        toks = [t for t in it["surface"].split(" ") if t != ""]
        assert len(toks) == n, (name, len(toks), n)
        if "conjuncts" in it:
            for k, c in enumerate(it["conjuncts"]):
                assert " ".join(toks[3 * k:3 * k + 3]) == c["surface"], (name, k)
        print(f"  WIRING-1 {name}: {len(toks)} eojeols == {n} nodes ✓")

    # WIRING-2 slots
    assert len(AP) == len(TU) == 3
    it = f2[0]; base = len(it["surface"].encode()); gp = it["gold_pattern"].encode()
    for k in range(6):
        assert gp[3 * k:3 * k + 3] in (AP, TU)
    print("  WIRING-2 slots: 앞/뒤 = 3 bytes, tile gold_pattern ✓")

    torch.manual_seed(0)
    model = Struct(cfg).to(device); model.eval()
    # untrained scorer in [0.3,0.7]
    dac = _dacc_item(model, torch, f2[0], "A-duel", 1, 0, device)
    print(f"  WIRING-2 untrained d_acc(item)= {round(dac,3)} (expect ~0.5)")

    # WIRING-3 injection liveness: flip T[0,1] sign moves A-duel logits, not C-scaf, not CPT
    it = f2[0]; surf_b, gold_b = _seq_bytes(it); seq = surf_b + gold_b
    st, gold, T = _struct_for(model, torch, it, "A-duel", 1, 0, len(seq))
    Tf = T.copy(); Tf[0, 1] = -Tf[0, 1]
    emb0 = model.node_embed(torch.tensor(T, dtype=torch.float32))
    emb1 = model.node_embed(torch.tensor(Tf, dtype=torch.float32))
    dmax = float((emb0 - emb1).abs().max())
    st_scaf, _, _ = _struct_for(model, torch, it, "C-scaf", 0, 0, len(seq))
    sc = st_scaf.detach().numpy()
    scaf_const = bool(np.allclose(sc, sc[0]))       # C-scaf = node_embed(0) = mlp(0): a CONSTANT (not zero)
    print(f"  WIRING-3 T[0,1] sign-flip moves node_embed by {round(dmax,4)} (>0 ✓) · "
          f"C-scaf struct constant across positions (=mlp(0), invariant to T): {scaf_const} ✓")

    # WIRING-5 harness: rank1_tiebreak nnz==2 on row 0; C-plc Π reproducible + conjugate
    r1 = gc.rank1_tiebreak(T)
    nz = np.argwhere(np.abs(r1) > 1e-9)
    row0 = all(r == 0 for r, _ in nz)
    print(f"  WIRING-5 rank1_tiebreak nnz={len(nz)} (expect 2), all on row 0: {row0} ✓")
    p1 = _arm_tensor(T, "C-plc", 1, 0); p2 = _arm_tensor(T, "C-plc", 1, 0)
    spec_ok = np.allclose(np.sort(np.linalg.svd(p1, compute_uv=False)),
                          np.sort(np.linalg.svd(T, compute_uv=False)), atol=1e-6)
    print(f"  WIRING-5 C-plc Π reproducible: {np.array_equal(p1,p2)} · spectrum preserved: {spec_ok} ✓")

    # WIRING-4 injection-path liveness: A-duel must overfit 16 drill items to ~1.0 (the field is
    # injected at the answer-prediction position ⇒ the model can read the sign bits). This is the
    # H_003-windower analog — if A-duel CANNOT overfit, the struct↔prediction-position alignment or
    # the slot indexing is broken. (C-scaf/A-rank1 overfit ~0.75 by MEMORIZING 16 surfaces; that is
    # NOT the field-necessity test — F3 on held-out f2″ is. So WIRING-4 gates A-duel only.)
    print("  WIRING-4 overfit A-duel on 16 drill items × 600 steps (d=64)…")
    model2, ce = train_arm("A-duel", 0, (torch, M, cfg, Struct), {"f2": f2, "f1": f1},
                           drill[:16], _cpt_windows(_nsmc_lines(1500), 128, torch),
                           (30, 600), device)
    dac_drill = float(np.mean([_dacc_item(model2, torch, drill[i], "A-duel", 0, i, device)
                               for i in range(16)]))
    print(f"  WIRING-4 A-duel drill-subset d_acc = {round(dac_drill,3)} (target ≥ 0.9; drill CE {round(ce,3)})")
    ok = (dmax > 0 and scaf_const and row0 and spec_ok and 0.2 <= dac <= 0.8 and dac_drill >= 0.9)
    print("\nSMOKE:", "wiring GREEN — alignment · injection-path (A-duel overfits) · slots · arm-tensors verified"
          if ok else "wiring RED — inspect above (esp. WIRING-4: injection/slot-alignment bug, H_003-windower class)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    import torch
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    if a.smoke:
        return smoke(device="cpu")     # smoke on cpu for determinism/speed at d=64
    print("FULL RUN is gated on native-operator G-1 + pre_register_frozen. "
          "Freeze the card first; then wire the full loop here. Refusing to spend ~5h unfrozen.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
