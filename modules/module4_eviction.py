# ============================================================
#  Module 4: Eviction & Replacement Manager
#  Developer : Sandarbh Gupta
#  Status    : Complete
# ============================================================


class EvictionTracker:
    """
    Wraps CacheController and records every eviction event.
    Provides per-set eviction counts and a full eviction log.
    """

    def __init__(self, controller):
        self.controller        = controller
        self.eviction_log      = []
        self.evictions_per_set = {}

    def access(self, tag, index):
        is_hit, evicted = self.controller.access(tag, index)
        if evicted is not None:
            self.eviction_log.append({
                'set_or_line' : index,
                'evicted_tag' : evicted,
                'loaded_tag'  : tag,
            })
            self.evictions_per_set[index] = \
                self.evictions_per_set.get(index, 0) + 1
        return is_hit, evicted

    @property
    def total_evictions(self):
        return len(self.eviction_log)

    def policy_summary(self):
        top   = sorted(self.evictions_per_set.items(),
                       key=lambda x: x[1], reverse=True)[:5]
        lines = [
            f"Replacement Policy : {self.controller.config.policy}",
            f"Total Evictions    : {self.total_evictions}",
        ]
        if top:
            lines.append("Most-Evicted Sets/Lines:")
            for k, v in top:
                lines.append(f"  Set/Line {k:4d} → {v} eviction(s)")
        return "\n".join(lines)
