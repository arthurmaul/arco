from typing import Protocol

class World(Protocol):
    registry: Registry
    archetype_of_type: dict
    location_of: dict
    archetypes_with: dict
    alias_of: dict

    origin: Archetype
    attachable: int
    storeable: int
    toggleable: int
    wildcard: int

    def spawn(self) -> int:
        ...

    def despawn(self, entity: int) -> None:
        ...

    def is_attachable(self, component: int) -> bool:
        ...

    def is_storable(self, component: int) -> bool:
        ...

    def is_togglable(self, component: int) -> bool:
        ...

    def has(self, entity: int, component: int) -> bool:
        ...

    def component(self, storable: bool = False, togglable: bool = False) -> int:
        ...

    def add(self, entity: int, component: int) -> None:
        ...

    def remove(self, entity: int, component: int) -> None:
        ...

    def set[T](self, entity: int, data: T, component: int | None = None) -> None:
        ...

    def unset(self, entity: int, component: int) -> None:
        ...

class Registry(Protocol):
    ...

class Archetype(Protocol):
    ...
