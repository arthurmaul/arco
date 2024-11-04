"""
"""

from entity import Registry


class World:
    """
    """

    def __init__(self):
        """"""
        self.registry = Registry()
        self.archetype_of_type = dict()
        self.location_of = dict()
        self.archetypes_with = dict()
        self.alias_of = dict()

        self.origin = Archetype(self, tuple())
        self.attachable = self.registry.spawn()
        self.storeable = self.registry.spawn()
        self.toggleable = self.registry.spawn()
        self.wildcard = self.registry.spawn()

    def spawn(self) -> int:
        """"""
        entity = self.registry.spawn()
        self.location_of[entity] = self.origin
        return entity

    def despawn() -> None:
        ...

    def is_attachable(self, component: int) -> bool:
        """"""
        return self.attachable in self.location_of[component].signature

    def is_storable(self, component: int) -> bool:
        """"""
        return self.storable in self.location_of[component].signature

     def is_toggleable(self, component: int) -> bool:
        """"""
        return self.toggleable in self.location_of[component].signature

    def has(self, entity: int, component: int) -> bool:
        """"""
        return component in self.location_of[entity].signature

    def component(self, storeable: bool = True, toggleable: bool = False) -> Entity:
        """"""
        entity = self.spawn()
        self.archetypes_with[entity] = dict()
        if storeable:
            self.add(entity, self.storeable)
        if toggleable:
            self.add(entity, self.toggleable)
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

