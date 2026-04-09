# ============================================================
#  Module 2: Address Translation Engine
#  Developer : Romit Raman
#  Status    : Complete
# ============================================================

class AddressTranslationEngine:
    def __init__(self, config):
        self.config = config

    def translate(self, address):
        if isinstance(address, str):
            address = int(address, 16)

        offset_mask = (1 << self.config.offset_bits) - 1
        index_mask  = (1 << self.config.index_bits)  - 1

        offset = address & offset_mask
        index  = (address >> self.config.offset_bits) & index_mask
        tag    = address >> (self.config.offset_bits + self.config.index_bits)

        return {
            'address' : hex(address),
            'raw'     : address,
            'tag'     : tag,
            'index'   : index,
            'offset'  : offset,
        }

    def translate_many(self, addresses):
        return [self.translate(a) for a in addresses]
