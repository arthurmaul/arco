"""World implementation, alongside its helper classes Archetype and Edge."""


from typing import Any
from copy import copy
from dataclasses import dataclass as datacls, field
default = lambda constructor: field(default_factory=constructor)

from arco.entity import Registry, is_relation, is_exclusive


@datacls
class World:
    registry: Registry = default(Registry)
    archetype_of: dict = default(dict)
    archetype_with_type: dict = default(dict)
    archetypes_with: dict = default(dict)
    entities_with: dict = default(dict)
    alias_of: dict = default(dict)

    def __post_init__(self):
        self.origin = Archetype(self, tuple())
        self.storable = self._new_entity()
        self.identity = self._init_storage(self._new_entity())
        self._set_identity(self.storable)
        self._set_identity(self.identity)
        self.wildcard = self.spawn()

    def _new_entity(self):
        entity = self.registry.spawn()
        self.archetype_of[entity] = self.origin
        self.archetypes_with[entity] = list()
        self.entities_with[entity] = list()
        return entity
        
    def _set_identity(self, entity: int) -> int:
        self.set(entity, self.identity, entity)
        return entity

    def spawn(self) -> int:
        return self._set_identity(self._new_entity())

    def despawn(self, entity: int) -> None:
        for component in copy(self.archetype_of[entity].signature):
            drop = self.unset if self.is_storable(component) else self.remove
            drop(entity, component)
        self.archetype_of.pop(entity)
        self.archetypes_with.pop(entity)
        for attached in self.entities_with[entity]:
            self.remove(attached, entity)
        self.entities_with.pop(entity)

    def _init_storage(self, component: int) -> int:
        self.archetypes_with[component] = list()
        self.add(component, self.storable)
        return component

    def component(self) -> int:
        component = self.spawn()
        return self._init_storage(component)

    def datacls[T](self, cls: T) -> T:
        self.alias_of[cls.__name__] = self.component()
        return datacls(cls)

    def add(self, entity: int, component: int) -> None:
        if component in self.archetype_of[entity].signature: return
        self.archetype_of[entity].add(entity, component)

    def remove(self, entity: int, component: int) -> None:
        if component not in self.archetype_of[entity].signature: return
        self.archetype_of[entity].remove(entity, component)

    def set(self, entity: int, component: int, data: Any) -> None:
        self.add(entity, component)
        self.archetype_of[entity].set(entity, component, data)
     
    def unset(self, entity: int, component: int) -> None:
        self.add(entity, component)
        self.archetype_of[entity].unset(entity, component)

    def get(self, entity: int, component: int) -> Any:
        return self.archetype_of[entity].get(entity, component)

    def is_storable(self, component: int) -> bool:
        return self.storable in self.archetype_of[component].signature

    def is_togglable(self, component: int) -> bool:
        return self.togglable in self.archetype_of[component].signature

    def has(self, entity: int, component: int) -> bool:
        return component in self.archetype_of[entity].signature


@datacls(slots=True)
class Archetype:
    world: World
    signature: tuple[int, ...]
    storage_for: dict = default(dict)
    edges: dict = default(dict)

    def __post_init__(self):
        for component in self.signature:
            self.link_component(component)

    def link_component(self, component: int) -> None:
        self.world.archetypes_with[component].append(self)
        storable = self.world.is_storable(component)
        if storable: self.storage_for[component] = dict()

    def set(self, entity: int, component: int, data: Any) -> None:
        self.storage_for[component][entity] = data

    def unset(self, entity: int, component: int) -> Any:
        return self.storage_for[component].pop(entity)

    def add(self, entity: int, component: int) -> None:
        if not self.edges.get(component): self.build_edge_adding(component)
        destination = self.edges[component].add
        for component in self.signature:
            if not self.world.is_storable(component): continue
            destination.set(entity, component, self.unset(entity, component))
        self.world.archetype_of[entity] = destination

    def remove(self, entity: int, component: int) -> None:
        if not self.edges.get(component): self.build_edge_removing(component)
        destination = self.edges[component].remove
        for component in destination.signature:
            if not self.world.is_storable(component): continue
            destination.set(entity, component, self.unset(entity, component))
        self.world.archetype_of[entity] = destination

    def build_edge_adding(self, component: int):
        signature = tuple(sorted((*self.signature, component)))
        archetype = self.get_archetype_with(signature)
        edge = Edge(add=archetype, remove=self)
        archetype.edges[component] = self.edges[component] = edge

    def build_edge_removing(self, component: int):
        signature = tuple(key for key in self.signature if key != component)
        archetype = self.get_archetype_with(signature)
        edge = Edge(add=self, remove=archetype)
        archetype.edges[component] = self.edges[component] = edge
        return archetype

    def get_archetype_with(self, signature: tuple[int, ...]) -> 'Archetype':
        return self.world.archetype_with_type.setdefault(signature, Archetype(self.world, signature))

    def get(self, entity: int, component: int) -> Any:
        return self.storage_for[component][entity]

    def has(self, component: int) -> bool:
        return component in self.signature


@datacls(slots=True)
class Edge:
    add: Archetype
    remove: Archetype


