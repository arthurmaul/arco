""""""
from ctypes import c_uint32 as u32


ENTITY_LIMIT = 0x7fffffff # 31 bits can be used without interfering with relationship type flags
BOTTOM = 0xffffffff # a mask to extract the bottom half of a 64 bit integer
HALF = 0x20 # 32 bits or half of a 64 bit integer
LAST = 0x1f # the last bit of a half, 31 bits
FLAG = 0x80000000 # a mask to flip the last bit of a half

NONE_FREE = 0 # Comparison value for Registry


class EntityLimitReached(Exception):
    pass


class Registry:
    """"""

    def __init__(self):
        """"""
        self.next_free = 0
        self.id_of = [None]

    def new(self) -> int:
        """"""
        if len(self.id_of) > ENTITY_LIMIT:
            raise EntityLimitReached("You have reached the maximum amount of living entities for this registry.")
        self.id_of.append(entity := len(self.id_of))
        return entity

    def recycled(self) -> int:
        """"""
        entity, generation = unpack(self.id_of[self.next_free])
        self.next_free, entity = entity, self.next_free
        self.id_of[entity] = pack(entity, generation)
        return self.id_of[entity]
        
    def spawn(self) -> int:
        """"""
        if self.next_free != NONE_FREE:
            return self.recycled()
        return self.new()

    def despawn(self, entity: int) -> None:
        """"""
        entity, generation = unpack(entity)
        self.next_free, previous_slot = entity, self.next_free
        self.id_of[entity] = pack(previous_slot, generation + 1)


def lower_half_of(entity: int) -> int:
    """"""
    return entity & BOTTOM


def upper_half_of(entity: int) -> int:
    """"""
    return entity >> HALF


def flag_of(half: int) -> int:
    """"""
    return half >> LAST


def is_relation(relation: int) -> bool:
    """"""
    return bool(flag_of(upper_half_of(relation)))


def is_exclusive(relation: int) -> bool:
    """"""
    return bool(flag_of(lower_half_of(relation)))


def pack(entity: int, generation: int) -> int:
    """"""
    return entity | generation << 32


def unpack(entity: int) -> int:
    """"""
    return lower_half_of(entity), upper_half_of(entity)


def relation(type: int, target: int, exclusive: bool = False) -> int:
    """"""
    type_entity = lower_half_of(type)
    target_entity = lower_half_of(target)
    if exclusive:
        return pack(type_entity | FLAG, target_entity | FLAG)
    return pack(type_entity, target_entity | FLAG)

