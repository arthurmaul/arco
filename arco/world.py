"""World implementation, alongside its helper classes Archetype and Edge."""


from typing import Any
from copy import copy
from dataclasses import dataclass as datacls, field
default = lambda constructor: field(default_factory=constructor)

from arco.entity import Registry, is_relation, is_exclusive


@datacls
class World:
    _registry: Registry = default(Registry)
    _entity_index: dict = default(dict)
    _archetype_index: dict = default(dict)
    _component_index: dict = default(dict)
    _alias_index: dict = default(dict)

    def __post_init__(self):
        self.storable = self._assign_entity()
        self.identity = self._assign_storable(self._assign_entity())
        self._assign_identity(self.storable)
        self._assign_identity(self.identity)

    def __repr__(self):
        return f"World({", ".join(str(archetype) for archetype in self._archetype_index.values())})"

    def _assign_entity(self):
        entity = self.registry.new()
        blank = self._archetype_index.setdefault(tuple(), _Archetype(self, tuple()))
        self._entity_index[entity] = blank
        self._blank.entities.add(entity)
        self._component_index[entity] = set()
        return entity
        
    def _assign_identity(self, entity: int) -> int:
        self.set(entity, entity, self.identity)
        return entity

    def _assign_storable(self, component: int) -> int:
        self.add(component, self.storable)
        return component

    def spawn(self, alias: str | None = None) -> int:
        if alias and alias in self.alias_index:
            return self.alias_index[alias]
        entity = self._assign_identity(self._assign_entity())
        if alias:
            self.alias_index[entity] = alias
        return entity

    def component(self, alias: str | None) -> int:
        return self._assign_storable(self.spawn(alias))

    def despawn(self, entity: int) -> None:
        for signature in self._component_index[entity]:
            archetype = self._archetype_index[signature]
            for owner in archetype.entities:
                self.drop(owner, entity)
            archetype._drop()
        for component in self._entity_index[entity].signature:
            self.drop(entity, component)
        self._entity_index.pop(entity)
        self._component_index.pop(entity)
        self._registry.recycle(entity)

    def datacls[T](self, cls: T) -> T:
        self._alias_index[cls.__name__] = self.component()
        return datacls(cls)

    def add(self, entity: int, component: int) -> None:
        if component in self.entity_index[entity].signature:
            return
        self.entity_index[entity]._add(entity, component)

    def remove(self, entity: int, component: int) -> None:
        if component not in self.entity_index[entity].signature:
            return
        self._entity_index[entity]._remove(entity, component)

    def set(self, entity: int, data: Any, component: int | None = None) -> None:
        component = component or self.alias_index[type(data).__name__]
        self.add(entity, component)
        self._entity_index[entity]._components[component][entity] = data
     
    def unset(self, entity: int, component: int) -> None:
        self.add(entity, component)
        self._entity_index[entity]._components[component].pop(entity)

    def drop(self, entity: int, component: int) -> None:
        if self.storable in self._entity_index[component]._signature:
            self.unset(entity, component)
        else:
            self.remove(entity, component)

    def get(self, entity: int, component: int) -> Any:
        return self._entity_index[entity]._components[component][entity]
        

@datacls
class _Archetype:
    _world: World
    _signature: tuple[int, ...]
    _components: dict = default(dict)
    _entities: set = default(set)
    _edges: dict = default(dict)

    def __post_init__(self):
        for component in self._signature:
            if self._world.storable in self._world.entity_index[component]._signature:
                self._components[component] = dict()
            self._world.component_index[component].add(self._signature)

    def __repr__(self):
        return f"_Archetype{self._signature}"

    def _add(self, entity: int, component: int) -> None:
        if not self._edges.get(component): 
            signature = tuple(sorted((*self._signature, component)))
            archetype = self._world.archetype_index.setdefault(signature, _Archetype(self._world, signature))
            archetype._edges[component] = self._edges[component] = Edge(add=archetype, remove=self)
        destination = self._edges[component].add
        for component_type in self._signature:
            if self._world.storable in self._world.entity_index[component_type]._signature:
                destination._components[component_type][entity] = self._components[component_type].pop(entity)
        self._entities.remove(entity)
        destination._entities.add(entity)
        self._world.entity_index[entity] = destination

    def _remove(self, entity: int, component: int) -> None:
        if not self._edges.get(component): 
            signature = tuple(key for key in self._signature if not key is component)
            archetype = self._world.archetype_index.setdefault(signature, _Archetype(self._world, signature))
            archetype._edges[component] = self._edges[component] = Edge(add=self, remove=archetype)
        destination = self._edges[component].remove
        for component_type in destination._signature:
            if self._world.storable in self._world.entity_index[component_type]._signature:
                destination._components[component_type][entity] = self._components[component_type].pop(entity)
        self._entities.remove(entity)
        destination._entities.add(entity)
        self._world.entity_index[entity] = destination
        if not self._entities:
            self.drop()

    def _drop(self):
        for component, edge in self._edges.items():
            if edge.add is self:
                edge.remove._edges.pop(component)
            else:
                edge.add._edges.pop(component)
        self._world.archetype_index.pop(self._signature)


@datacls
class Edge:
    add: _Archetype
    remove: _Archetype


