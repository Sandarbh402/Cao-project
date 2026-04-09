# ============================================================
#  Module 1: Input & Configuration Manager
#  Developer : Romit Raman
#  Status    : Complete
# ============================================================
import math

class CacheConfig:
    VALID_POLICIES = ['FIFO', 'LRU', 'RANDOM']
    VALID_MAPPINGS = ['DIRECT', 'FULLY_ASSOCIATIVE', 'SET_ASSOCIATIVE']

    def __init__(self, cache_size_kb, block_size_bytes,
                 mapping_type, replacement_policy, associativity=1):
        self.cache_size    = cache_size_kb * 1024
        self.block_size    = block_size_bytes
        self.mapping_type  = mapping_type.upper()
        self.policy        = replacement_policy.upper()
        self.associativity = associativity
        self._validate()
        
        self.num_blocks  = self.cache_size  // self.block_size
        
        # ---> ADD THESE 4 LINES BACK IN <---
        if self.mapping_type == 'DIRECT':
            self.associativity = 1
        elif self.mapping_type == 'FULLY_ASSOCIATIVE':
            self.associativity = self.num_blocks
        # -----------------------------------
            
        self.num_sets    = self.num_blocks  // self.associativity
        self.offset_bits = int(math.log2(self.block_size))
        self.index_bits  = int(math.log2(self.num_sets)) if self.num_sets > 1 else 0

    def _validate(self):
        if self.block_size > self.cache_size:
            raise ValueError(
                f"Block size ({self.block_size}B) must be smaller than "
                f"cache size ({self.cache_size}B).")
        if not (self.block_size > 0 and (self.block_size & (self.block_size - 1)) == 0):
            raise ValueError(
                f"Block size ({self.block_size}) must be a power of 2 (e.g. 16, 32, 64).")
        if self.mapping_type not in self.VALID_MAPPINGS:
            raise ValueError(
                f"Invalid mapping '{self.mapping_type}'. Choose: {self.VALID_MAPPINGS}")
        if self.policy not in self.VALID_POLICIES:
            raise ValueError(
                f"Invalid policy '{self.policy}'. Choose: {self.VALID_POLICIES}")
        if self.mapping_type == 'SET_ASSOCIATIVE' and self.associativity < 2:
            raise ValueError("Set Associative mapping requires associativity >= 2.")

    def summary(self):
        return (
            f"Cache Size    : {self.cache_size} bytes ({self.cache_size//1024} KB)\n"
            f"Block Size    : {self.block_size} bytes\n"
            f"Total Blocks  : {self.num_blocks}\n"
            f"Total Sets    : {self.num_sets}\n"
            f"Mapping       : {self.mapping_type}\n"
            f"Policy        : {self.policy}\n"
            f"Associativity : {self.associativity}-way\n"
            f"Offset bits   : {self.offset_bits}\n"
            f"Index bits    : {self.index_bits}"
        )
