class EntityLimitReached(Exception):
    pass

class Registry:
    def __init__(self):
        self.vacant = 0
        self.slots = [None]

    def new(self) -> int:
        if self.vacant:
            old_vacancy, generation = unpack(self.slots[self.vacant])
            self.vacant, entity = old_vacancy, self.vacant
            self.slots[entity] = pack(entity, generation)
            return self.slots[entity]
        if len(self.slots) > 0x7fffffff:
            raise EntityLimitReached("You have reached the maximum amount of living entities for this registry.")
        self.slots.append(entity := len(self.slots))
        return entity

    def recycle(self, entity: int) -> None:
        new_vacancy, generation = unpack(entity)
        self.vacant, old_vacancy = new_vacancy, self.vacant
        self.slots[new_vacancy] = pack(old_vacancy, generation + 1)

    def alive(self, entity: int) -> bool:
        slot = lower_32_bits_of(entity)
        return self.slots[slot] == entity

def lower_32_bits_of(entity: int) -> int:
    return entity & 0xffffffff 

def upper_32_bits_of(entity: int) -> int:
    return entity >> 0x20

def flag_of(half: int) -> int:
    return half >> 0x1f

def enable(half: int) -> int:
    return half | 0x80000000

def disable(half: int) -> int:
    return half & 0x1f

def is_relation(relation: int) -> bool:
    return bool(flag_of(upper_32_bits_of(relation)))

def is_exclusive(relation: int) -> bool:
    return bool(flag_of(lower_32_bits_of(relation)))

def pack(entity: int, generation: int) -> int:
    return entity | generation << 32

def unpack(entity: int) -> tuple[int, int]:
    return lower_32_bits_of(entity), upper_32_bits_of(entity)

def rel(type: int, target: int) -> int:
    return pack(enabled(lower_32_bits_of(entity)), enabled(lower_32_bits_of(target)))

def exrel(type: int, target: int) -> int:
    return pack(lower_32_bits_of(entity), enabled(lower_32_bits_of(target)))



