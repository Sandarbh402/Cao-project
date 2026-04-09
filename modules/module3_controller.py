# ============================================================
#  Module 3: Cache Controller (Mapping Logic)
#  Developer : Sandarbh Gupta
#  Status    : Complete
#  Supports  : DIRECT | FULLY_ASSOCIATIVE | SET_ASSOCIATIVE
#  Policies  : FIFO | LRU | RANDOM
# ============================================================

from collections import OrderedDict
import random as _random


class CacheController:
    def __init__(self, config):
        self.config = config
        self._init_cache()

    def _init_cache(self):
        m = self.config.mapping_type
        if m == 'DIRECT':
            self.cache = [None] * self.config.num_blocks
        elif m == 'FULLY_ASSOCIATIVE':
            self.sets = [_Set(self.config.num_blocks, self.config.policy)]
        elif m == 'SET_ASSOCIATIVE':
            self.sets = [
                _Set(self.config.associativity, self.config.policy)
                for _ in range(self.config.num_sets)
            ]

    def access(self, tag, index):
        if self.config.mapping_type == 'DIRECT':
            return self._direct(tag, index)
        set_idx = 0 if self.config.mapping_type == 'FULLY_ASSOCIATIVE' else index
        return self.sets[set_idx].access(tag)

    def _direct(self, tag, index):
        if self.cache[index] == tag:
            return True, None
        evicted = self.cache[index]
        self.cache[index] = tag
        return False, evicted


class _Set:
    """One cache set — handles FIFO, LRU, RANDOM replacement."""

    def __init__(self, ways, policy):
        self.ways   = ways
        self.policy = policy
        self.order  = OrderedDict()   # tag → True

    def access(self, tag):
        if tag in self.order:
            if self.policy == 'LRU':
                self.order.move_to_end(tag)
            return True, None

        evicted = None
        if len(self.order) >= self.ways:
            evicted = self._evict()
        self.order[tag] = True
        return False, evicted

    def _evict(self):
        if self.policy in ('FIFO', 'LRU'):
            evicted, _ = self.order.popitem(last=False)
        else:  # RANDOM
            evicted = _random.choice(list(self.order.keys()))
            del self.order[evicted]
        return evicted
