"""World implementation, alongside its helper classes Archetype and Edge."""


from typing import Any
from copy import copy
from dataclasses import dataclass as datacls, field
default = lambda constructor: field(default_factory=constructor)

from arco.entity import Registry, is_relation, is_exclusive


type EntityId = int
type ComponentId = int
type Signature = tuple[ComponentId, ...]
type Column = dict[ComponentId, T]


@datacls
class World:
    registry: Registry = default(Registry)
    entity_index: dict = default(dict) # archetype_of[eid]
    archetype_index: dict = default(dict) # archetype_index[signature]
    component_index: dict = default(dict) # archetypes_with[component]
    alias_index: dict = default(dict) # alias_index[eid]

    def __post_init__(self):
        self.blank = Archetype(self, tuple())
        self.archetype_with[tuple()] = self.origin
        self.storable = self._assign_entity()
        self.identity = self._assign_storage(self._assign_entity())
        self._assign_identity(self.storable)
        self._assign_identity(self.identity)
        self.any = self.spawn()

    def __repr__(self):
        return f"World({", ".join(str(archetype) for archetype in self.composed_of.values())})"

    def _assign_eid(self):
        eid = self.registry.create()
        self.entities_with[eid] = list()
        self.archetype_of[eid] = self.blank
        self.archetypes_with[eid] = list()
        return eid
        
    def _set_identity(self, eid: int) -> int:
        self.set(eid, self.identity, eid)
        return eid

    def spawn(self) -> int:
        return self._set_identity(self._new_eid())

    def despawn(self, eid: int) -> None:
        for cid in copy(self.archetype_of[eid].signature):
            self.unset(eid, cid) if self.is_storable(cid) else self.remove(eid, cid)
        for owner in self.entities_with[eid]:
            self.remove(owner, eid)
        self.entities_with.pop(eid)
        self.archetype_of.pop(eid)
        self.archetypes_with.pop(eid)
        self.registry.despawn(eid)

    def _init_storage(self, cid: int) -> int:
        self.archetypes_with[cid] = list()
        self.add(cid, self.storable)
        return cid

    def cid(self) -> int:
        cid = self.spawn()
        return self._init_storage(cid)

    def datacls[T](self, cls: T) -> T:
        self.alias_of[cls.__name__] = self.cid()
        return datacls(cls)

    def release(self, cid: int) -> None:
        ...

    def add(self, eid: int, cid: int) -> None:
        if cid in self.archetype_of[eid].signature: return
        self.entities_with[cid].add(eid)
        self.archetype_of[eid].add(eid, cid)

    def remove(self, eid: int, cid: int) -> None:
        if cid not in self.archetype_of[eid].signature: return
        self.entities_with[cid].remove(eid)
        self.archetype_of[eid].remove(eid, cid)

    def set(self, eid: int, cid: int, data: Any) -> None:
        self.add(eid, cid)
        self.archetype_of[eid].set(eid, cid, data)
     
    def unset(self, eid: int, cid: int) -> None:
        self.add(eid, cid)
        self.archetype_of[eid].unset(eid, cid)


@datacls(slots=True)
class Archetype:
    world: World
    signature: tuple[Component, ...]
    storage_of: dict = default(dict)
    edges: dict = default(dict)

    def __post_init__(self):
        for id in self.signature:
            cid = self.world.owner_of[id]
            if cid.is_storable():
                self.storage_of[cid.id] = dict()

    def __repr__(self):
        return f"Archetype{self.signature}"

    def add(self, eid: int, cid: int) -> None:
        if not self.edges.get(cid.id): 
            signature = tuple(sorted((*self.signature, cid.id)))
            archetype = self.world.archetype_with.setdefault(signature, Archetype(self.world, signature))
            archetype.edges[cid.id] = self.edges[cid.id] = Edge(add=archetype, remove=self)
        destination = self.edges[cid.id].add
        for _cid in self.signature:
            if self.world.eid_with[_cid].is_storable():
                destination.storage_of[_cid][eid] = self.storage_of[_cid].pop(eid.id)
        eid.archetype = destination

    def remove(self, eid: int, cid: int) -> None:
        if not self.edges.get(cid.id):
            signature = tuple(key for key in self.signature if not key is cid)
            archetype = self.world.archetype_with_type.setdefault(signature, Archetype(self.world, signature))
            archetype.edges[cid.id] = self.edges[cid.id] = Edge(add=self, remove=archetype)
        destination = self.edges[cid.id].remove
        for id in destination.signature:
            if self.world.eid_with[id].is_storable():
                destination.storage_of[id][eid.id] = self.storage_of[id].pop(eid.id)
        eid.archetype = destination


@datacls(slots=True)
class Edge:
    add: Archetype
    remove: Archetype


