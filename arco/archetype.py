""" ... """
from typing import Any
from arco.protocols import World


class Archetype:
    """ ... """

    def __init__(self, world: World, signature: tuple[int, ...]) -> None:
        """ ... """
        self.world = world
        self.signature = signature
        self.storage_for: dict[int, dict] = dict()
        self.edge_with: dict[int, 'Archetype'] = dict()
        self.edge_without: dict[int, 'Archetype'] = dict()
        map(self.link_component, signature)

    def link_component(self, component: int) -> None:
        """ ... """
        self.world.archetypes_with[component].append(self)
        togglable = self.world.is_togglable(component)
        storable = self.world.is_storable(component)
        if storable and togglable:
            ...
        if storable:
            self.storage_for[component] = dict()

    def set[T](self, entity: int, component: int, data: T) -> None:
        """ ... """
        self.storage_for[component][entity] = data

    def unset(self, entity: int, component: int) -> Any:
        """ ... """
        return self.storage_for[component].pop(entity)

    def add(self, entity: int, component: int) -> None:
        """ ... """
        if component not in self.edge_with:
            destination = self.build_edge_with(component)
        else:
            destination = self.edge_with[component]
        for component in destination.signature:
            destination.set(entity, component, self.unset(entity, component))
        self.world.location_of[entity] = destination

    def remove(self, entity: int, component: int) -> None:
        """ ... """
        if component not in self.edge_without:
            destination = self.build_edge_without(component)
        else:
            destination = self.edge_without[component]
        for component in destination.signature:
            destination.set(entity, component, self.unset(entity, component))
        self.world.location_of[entity] = destination

    def build_edge_with(self, component: int) -> 'Archetype':
        """ ... """
        signature = tuple(sorted((*self.signature, component)))
        archetype = self.get_archetype_with(signature)
        archetype.edge_without[component] = self
        self.edge_with[component] = archetype
        return archetype

    def build_edge_without(self, component: int) -> 'Archetype':
        """ ... """
        signature = tuple(key for key in self.signature if key != component)
        archetype = self.get_archetype_with(signature)
        archetype.edge_with[component] = self
        self.edge_without[component] = archetype
        return archetype

    def get_archetype_with(self, signature: tuple[int, ...]) -> 'Archetype':
        """ ... """
        if not signature in self.world.archetype_of_type:
            self.world.archetype_of_type[signature] = Archetype(self.world, signature)
        return self.world.archetype_of_type[signature]

