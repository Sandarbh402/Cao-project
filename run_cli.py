#!/usr/bin/env python3
"""
Cache Memory Performance Simulator — CLI
Run:  python run_cli.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.module1_config    import CacheConfig
from modules.module5_analytics import run_simulation, export_csv, plot_comparison

W = 62

def bar(c='─'): print(c * W)
def title(t):   bar('═'); print(f"  {t}"); bar('═')
def section(t): print(f"\n── {t} {'─'*(W-len(t)-4)}")

def ask(prompt, default=None):
    sfx = f" [{default}]" if default is not None else ""
    v = input(f"  {prompt}{sfx}: ").strip()
    return v if v else (str(default) if default is not None else v)

def ask_int(prompt, default=None, lo=None, hi=None):
    while True:
        try:
            v = int(ask(prompt, default))
            if lo is not None and v < lo: print(f"  ✗  Minimum is {lo}"); continue
            if hi is not None and v > hi: print(f"  ✗  Maximum is {hi}"); continue
            return v
        except ValueError:
            print("  ✗  Enter a whole number.")

def ask_choice(prompt, choices, default=None):
    while True:
        v = ask(f"{prompt} ({'/'.join(choices)})", default)
        if v.upper() in [c.upper() for c in choices]:
            return v.upper()
        print(f"  ✗  Choose: {'/'.join(choices)}")

def parse_addr(raw):
    raw = raw.strip()
    return int(raw, 16) if raw.lower().startswith("0x") else int(raw)

# ── Step 1: Config ──────────────────────────────────────────
def get_config():
    title("STEP 1 — Cache Configuration")
    while True:
        try:
            cache_kb = ask_int("Cache size (KB)", 4, 1)
            block_b  = ask_int("Block size (bytes, must be power of 2)", 16, 1)
            m = ask_choice("Mapping type", ["DIRECT","FA","SA"], "DIRECT")
            mapping = {"DIRECT":"DIRECT","FA":"FULLY_ASSOCIATIVE","SA":"SET_ASSOCIATIVE"}[m]
            assoc = 1
            if mapping == "SET_ASSOCIATIVE":
                assoc = ask_int("Associativity (ways, e.g. 2/4/8)", 4, 2)
            policy = ask_choice("Replacement policy", ["FIFO","LRU","RANDOM"], "LRU")
            cfg = CacheConfig(cache_kb, block_b, mapping, policy, assoc)
            print(f"\n  ✓  Config accepted\n")
            print(cfg.summary()); print()
            return cfg
        except ValueError as e:
            print(f"\n  ✗  {e}\n")

# ── Step 2: Addresses ────────────────────────────────────────
def get_addresses():
    title("STEP 2 — Memory Address Sequence")
    print("  Formats accepted: hex  →  0x1A3F   |   decimal  →  6719")
    print("  Type DONE or press Enter on blank line to finish.\n")
    addrs, i = [], 1
    while True:
        raw = input(f"  Address #{i}: ").strip()
        if raw == "" or raw.upper() == "DONE":
            if not addrs: print("  ✗  Need at least one address."); continue
            break
        try:
            a = parse_addr(raw)
            addrs.append(a)
            print(f"      ✓  {hex(a)}  ({a} decimal)")
            i += 1
        except ValueError:
            print("  ✗  Bad format. Use 0x1A3F or a plain integer.")
    print(f"\n  {len(addrs)} address(es) loaded.")
    return addrs

# ── Step 3: Timing ───────────────────────────────────────────
def get_timing():
    title("STEP 3 — Timing Parameters")
    print("  AMAT = Hit Time + (Miss Rate × Miss Penalty)\n")
    h = ask_int("Hit time    (cycles)", 1, 1)
    m = ask_int("Miss penalty (cycles)", 100, 1)
    return h, m

# ── Step 4: Results ──────────────────────────────────────────
def show_results(cfg, result):
    title("STEP 4 — Simulation Results")
    trace = result['trace']
    hdr = f"{'#':>4}  {'Address':>10}  {'Tag':>8}  {'Idx':>5}  {'Off':>5}  {'Result':>5}  {'Evicted':>8}"
    bar(); print(hdr); bar()
    for r in trace:
        marker = "◀ HIT" if r['result'] == 'HIT' else ""
        print(f"{r['access_no']:>4}  {r['address']:>10}  {r['tag']:>8}  "
              f"{r['index']:>5}  {r['offset']:>5}  {r['result']:>5}  "
              f"{str(r['evicted']):>8}  {marker}")
    bar()
    print(f"\n  Total     : {result['total']}")
    print(f"  Hits      : {result['hits']}  ({result['hit_ratio']*100:.2f}%)")
    print(f"  Misses    : {result['misses']}  ({result['miss_ratio']*100:.2f}%)")
    print(f"  AMAT      : {result['amat']:.4f} cycles")
    print(f"\n{result['tracker'].policy_summary()}\n")

# ── Step 5: Export ───────────────────────────────────────────
def do_export(result, all_results):
    title("STEP 5 — Export")
    if ask_choice("Save trace to CSV?", ["YES","NO"], "NO") == "YES":
        fn = ask("Filename", "trace.csv")
        if not fn.endswith(".csv"): fn += ".csv"
        os.makedirs("output", exist_ok=True)
        export_csv(result, f"output/{fn}")
        print(f"  ✓  Saved to output/{fn}")

    if len(all_results) > 1:
        if ask_choice("Generate comparison chart?", ["YES","NO"], "YES") == "YES":
            p = plot_comparison(all_results, filepath="output/comparison.png")
            print(f"  ✓  Chart saved to {p}" if p else "  ✗  matplotlib not installed.")

# ── Main ─────────────────────────────────────────────────────
def main():
    print()
    title("CACHE MEMORY PERFORMANCE SIMULATOR")
    print("  Team: Romit Raman | Sandarbh Gupta | Shivansh Verma\n")

    all_results = []
    while True:
        cfg       = get_config()
        addrs     = get_addresses()
        ht, mp    = get_timing()
        result    = run_simulation(cfg, addrs, ht, mp)
        show_results(cfg, result)

        label = ask("Label for this run (for comparison chart)", cfg.mapping_type)
        all_results.append((label, result))

        do_export(result, all_results)

        print()
        if ask_choice("Run another simulation?", ["YES","NO"], "YES") == "NO":
            print("\n  Goodbye!\n"); break

if __name__ == "__main__":
    main()
