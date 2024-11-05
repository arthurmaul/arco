""""""


from arco.entity import Registry
from typing import Any
from copy import copy


class World:
    """"""
    def __init__(self):
        """"""
        self.registry = Registry()
        self.location_of = dict()
        self.archetype_of_type = dict()
        self.archetypes_with = dict()
        self.alias_of = dict()

        self.origin = Archetype(self, tuple())
        self.storable = self.spawn()
        self.togglable = self.spawn()
        self.wildcard = self.spawn()

    def spawn(self) -> int:
        """"""
        entity = self.registry.spawn()
        self.location_of[entity] = self.origin
        self.archetypes_with[entity] = list()
        return entity

    def despawn(self, entity) -> None:
        """"""
        for component in copy(self.location_of[entity].signature):
            drop = self.unset if self.is_storable(component) else self.remove
            drop(entity, component)
        self.location_of.pop(entity)

    def component(self) -> int:
        """"""
        entity = self.spawn()
        self.archetypes_with[entity] = list()
        self.add(entity, self.storable)
        return entity

    def Component(self, cls):
        self.alias_of[cls.__name__] = self.component()
        return cls

    def add(self, entity: int, component: int) -> None:
        """"""
        if component in self.location_of[entity].signature:
            return
        self.location_of[entity].add(entity, component)

    def remove(self, entity: int, component: int) -> None:
        """"""
        if component not in self.location_of[entity].signature:
            return
        self.location_of[entity].remove(entity, component)

    def set(self, entity: int, data: Any, component: int | None = None) -> None:
        """"""
        component = component or self.alias_of[type(data).__name__]
        self.add(entity, component)
        self.location_of[entity].set(entity, component, data)
     
    def unset(self, entity: int, component: int) -> None:
        """"""
        self.add(entity, component)
        self.location_of[entity].unset(entity, component)

    def is_storable(self, component: int) -> bool:
        """"""
        return self.storable in self.location_of[component].signature

    def is_togglable(self, component: int) -> bool:
        """"""
        return self.togglable in self.location_of[component].signature

    def has(self, entity: int, component: int) -> bool:
        """"""
        return component in self.location_of[entity].signature


class Archetype:
    """"""
    def __init__(self, world: World, signature: tuple[int, ...]) -> None:
        """"""
        self.world = world
        self.signature = signature
        self.storage_for = dict()
        self.edge_with = dict()
        self.edge_without = dict()
        for component in signature:
            self.link_component(component)

    def link_component(self, component: int) -> None:
        """"""
        self.world.archetypes_with[component].append(self)
        togglable = self.world.is_togglable(component)
        storable = self.world.is_storable(component)
        if storable and togglable:
            self.storage_for[component] = dict()
            self.storage_for[component, 0] = set()
            self.storage_for[component, 1] = set()
        if storable:
            self.storage_for[component] = dict()

    def has(self, component: int) -> bool:
        return component in self.signature

    def set(self, entity: int, component: int, data: Any) -> None:
        """"""
        if self.world.is_togglable(component):
            self.storage_for[component, 1].add(entity)
        self.storage_for[component][entity] = data

    def unset(self, entity: int, component: int) -> Any:
        """"""
        if self.world.is_togglable(component):
            if entity in self.storage_for[component, 1]:
                self.storage_for[component, 1].remove(entity)
            else:
                self.storage_for[component, 0].remove(entity)
        return self.storage_for[component].pop(entity)

    def add(self, entity: int, component: int) -> None:
        """"""
        if component not in self.edge_with:
            self.build_edge_with(component)
        destination = self.edge_with[component]
        for component in self.signature:
            if not self.world.is_storable: continue
            destination.set(entity, component, self.unset(entity, component))
        self.world.location_of[entity] = destination

    def remove(self, entity: int, component: int) -> None:
        """"""
        if component not in self.edge_without:
            self.build_edge_without(component)
        destination = self.edge_without[component]
        for component in destination.signature:
            if not self.world.is_storable: continue
            destination.set(entity, component, self.unset(entity, component))
        self.world.location_of[entity] = destination

    def get(self, entity: int, component: int) -> Any:
        return self.storage_for[component][entity]

    def build_edge_with(self, component: int):
        """"""
        signature = tuple(sorted((*self.signature, component)))
        archetype = self.get_archetype_with(signature)
        archetype.edge_without[component] = self
        self.edge_with[component] = archetype

    def build_edge_without(self, component: int):
        """"""
        signature = tuple(key for key in self.signature if key != component)
        archetype = self.get_archetype_with(signature)
        archetype.edge_with[component] = self
        self.edge_without[component] = archetype
        return archetype

    def get_archetype_with(self, signature: tuple[int, ...]) -> 'Archetype':
        """"""
        if not signature in self.world.archetype_of_type:
            self.world.archetype_of_type[signature] = Archetype(self.world, signature)
        return self.world.archetype_of_type[signature]


