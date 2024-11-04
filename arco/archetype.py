""" Archetype class """

type ComponentStorage = dict[int, dict] | dict[tuple[int, int], dict]
type EdgeMapping = dict[int, Archetype]
type Signature = tuple[int]

class Archetype:
    """ ... """

    def __init__(self, world, signature: tuple[int]):
        """ ... """
        self.world = world
        self.signature: Signature = signature
        self.storage_for: ComponentStorage = dict()
        self.edge_with: EdgeMapping = dict()
        self.edge_without: EdgeMapping = dict()
        map(self.link_component, signature)

    def link_component(self, component: int) -> None:
        """ ... """
        self.world.archetypes_with[component].append(self)
        togglable = self.world.is_togglable(component)
        storable = self.world.is_storable(component)
        if storable and togglable:
            self.storage_for[component, 0] = dict()
            self.storage_for[component, 1] = dict()
        if storable:
            self.storage_for[component] = dict()

    def set[T](self, entity: int, component: int, data: T) -> T:
        """ ... """
        self.storage_for[component][entity] = data

    def unset[T](self, entity: int, component: int) -> T:
        """ ... """
        self.storage_for[component].pop(entity)

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

    def build_edge_with(self, component: int) -> None:
        """ ... """
        signature = tuple(sorted((*self.signature, component)))
        archetype = self.get_archetype_with(signature)
        archetype.edge_without[component] = self
        self.edge_with[component] = archetype

    def build_edge_without(self, component: int) -> None:
        """ ... """
        signature = tuple(key for key in self.signature if key != component)
        archetype = self.get_archetype_with(signature)
        archetype.edge_with[component] = self
        self.edge_without[component] = archetype

    def get_archetype_with(self, signature: tuple[int]) -> 'Archetype':
        """ ... """
        if not signature in self.world.archetype_of_type:
            self.world.archetype_of_type[signature] = Archetype(self.world, signature)
        return self.world.archetype_of_type[signature]

