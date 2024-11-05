""""""


from arco.entity import Registry
from typing import Any
from copy import copy


class World:
    """"""
    def __init__(self):
        """"""
        self.registry = Registry()
        self.archetype_of_type = dict()
        self.location_of = dict()
        self.archetypes_with = dict()
        self.alias_of = dict()

        self.origin = Archetype(self, tuple())
        self.attachable = self.registry.spawn()
        self.storable = self.registry.spawn()
        self.togglable = self.registry.spawn()
        self.wildcard = self.registry.spawn()

    def spawn(self) -> int:
        """"""
        entity = self.registry.spawn()
        self.location_of[entity] = self.origin
        return entity

    def despawn(self, entity) -> None:
        """"""
        for component in copy(self.location_of[entity].signature):
            if self.is_storable(component):
                self.unset(entity, component)
            else:
                self.remove(entity, component)
        self.location_of.pop(entity)

    def is_attachable(self, component: int) -> bool:
        """"""
        return self.attachable in self.location_of[component].signature

    def is_storable(self, component: int) -> bool:
        """"""
        return self.storable in self.location_of[component].signature

    def is_togglable(self, component: int) -> bool:
        """"""
        return self.togglable in self.location_of[component].signature

    def has(self, entity: int, component: int) -> bool:
        """"""
        return component in self.location_of[entity].signature

    def component(self, storable: bool = True, togglable: bool = False) -> int:
        """"""
        entity = self.spawn()
        self.archetypes_with[entity] = dict()
        if storable:
            self.add(entity, self.storable)
        if togglable:
            self.add(entity, self.togglable)
        self.add(entity, self.attachable)
        return entity

    def add(self, entity: int, component: int) -> None:
        """"""
        if component not in self.location_of[entity].signature:
            return
        self.location_of[entity].add(entity, component)

    def remove(self, entity: int, component: int) -> None:
        """"""
        if component not in self.location_of[entity].signature:
            return
        self.location_of[entity].remove(entity, component)

    def set[T](self, entity: int, data: Any, component: int | None = None) -> None:
        """"""
        component = component or self.alias_of[type(data)]
        self.add(entity, component)
        self.location_of[entity].set(entity, component, data)
     
    def unset(self, entity: int, component: int) -> None:
        """"""
        self.add(entity, component)
        self.location_of[entity].unset(entity, component)


class Archetype:
    """"""
    def __init__(self, world: World, signature: tuple[int, ...]) -> None:
        """"""
        self.world = world
        self.signature = signature
        self.storage_for: dict[int, dict] = dict()
        self.edge_with: dict[int, 'Archetype'] = dict()
        self.edge_without: dict[int, 'Archetype'] = dict()
        map(self.link_component, signature)

    def link_component(self, component: int) -> None:
        """"""
        self.world.archetypes_with[component].append(self)
        togglable = self.world.is_togglable(component)
        storable = self.world.is_storable(component)
        if storable and togglable:
            ...
        if storable:
            self.storage_for[component] = dict()

    def set[T](self, entity: int, component: int, data: T) -> None:
        """"""
        self.storage_for[component][entity] = data

    def unset(self, entity: int, component: int) -> Any:
        """"""
        return self.storage_for[component].pop(entity)

    def add(self, entity: int, component: int) -> None:
        """"""
        if component not in self.edge_with:
            destination = self.build_edge_with(component)
        else:
            destination = self.edge_with[component]
        for component in destination.signature:
            destination.set(entity, component, self.unset(entity, component))
        self.world.location_of[entity] = destination

    def remove(self, entity: int, component: int) -> None:
        """"""
        if component not in self.edge_without:
            destination = self.build_edge_without(component)
        else:
            destination = self.edge_without[component]
        for component in destination.signature:
            destination.set(entity, component, self.unset(entity, component))
        self.world.location_of[entity] = destination

    def build_edge_with(self, component: int) -> 'Archetype':
        """"""
        signature = tuple(sorted((*self.signature, component)))
        archetype = self.get_archetype_with(signature)
        archetype.edge_without[component] = self
        self.edge_with[component] = archetype
        return archetype

    def build_edge_without(self, component: int) -> 'Archetype':
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


