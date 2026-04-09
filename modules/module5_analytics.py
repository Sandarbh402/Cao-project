# ============================================================
#  Module 5: Analytics & Visualization Output
#  Developer : Shivansh Verma
#  Status    : Complete
# ============================================================

import csv
import os

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False


def run_simulation(config, addresses,
                   hit_time_cycles=1, miss_penalty_cycles=100):
    from modules.module2_translation import AddressTranslationEngine
    from modules.module3_controller  import CacheController
    from modules.module4_eviction    import EvictionTracker

    translator = AddressTranslationEngine(config)
    controller = CacheController(config)
    tracker    = EvictionTracker(controller)

    trace  = []
    hits = misses = 0

    for i, raw in enumerate(addresses):
        parts           = translator.translate(raw)
        is_hit, evicted = tracker.access(parts['tag'], parts['index'])
        hits   += is_hit
        misses += not is_hit
        trace.append({
            'access_no' : i + 1,
            'address'   : parts['address'],
            'tag'       : parts['tag'],
            'index'     : parts['index'],
            'offset'    : parts['offset'],
            'result'    : 'HIT' if is_hit else 'MISS',
            'evicted'   : evicted if evicted is not None else '-',
        })

    total      = hits + misses
    hit_ratio  = hits  / total if total else 0
    miss_ratio = misses / total if total else 0
    amat       = hit_time_cycles + (miss_ratio * miss_penalty_cycles)

    return {
        'trace'      : trace,
        'hits'       : hits,
        'misses'     : misses,
        'total'      : total,
        'hit_ratio'  : hit_ratio,
        'miss_ratio' : miss_ratio,
        'amat'       : amat,
        'tracker'    : tracker,
    }


def export_csv(result, filepath):
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    fields = ['access_no', 'address', 'tag', 'index', 'offset', 'result', 'evicted']
    with open(filepath, 'w', newline='') as f:
        csv.DictWriter(f, fieldnames=fields).writeheader()
        csv.DictWriter(f, fieldnames=fields).writerows(result['trace'])


def plot_comparison(configs_results, title="Cache Comparison",
                    filepath="output/comparison.png"):
    if not _HAS_MPL:
        return None
    labels     = [lr[0] for lr in configs_results]
    hit_ratios = [lr[1]['hit_ratio'] * 100 for lr in configs_results]
    amats      = [lr[1]['amat']            for lr in configs_results]
    x = range(len(labels))
    colors = ['#4C72B0','#DD8452','#55A868','#C44E52','#8172B2',
              '#937860','#DA8BC3','#8C8C8C','#CCB974','#64B5CD']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    b1 = ax1.bar(x, hit_ratios, color=colors[:len(labels)])
    ax1.set_xticks(list(x)); ax1.set_xticklabels(labels, rotation=20, ha='right', fontsize=8)
    ax1.set_ylabel("Hit Ratio (%)"); ax1.set_ylim(0, 115)
    ax1.set_title("Hit Ratio by Configuration")
    ax1.bar_label(b1, fmt='%.1f%%', padding=3, fontsize=8)

    b2 = ax2.bar(x, amats, color=colors[:len(labels)])
    ax2.set_xticks(list(x)); ax2.set_xticklabels(labels, rotation=20, ha='right', fontsize=8)
    ax2.set_ylabel("AMAT (cycles)")
    ax2.set_title("Average Memory Access Time")
    ax2.bar_label(b2, fmt='%.1f', padding=3, fontsize=8)

    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    return filepath
