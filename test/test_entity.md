# Entities

The entity module contains a Registry class, a set of constants in seximal, and a set of helper functions and predicates.

The use of the module will primarily be through a registry instance, which every world will own.
For the sake of illustration, we will use an instance directly.

```py

>>> from arco import entity
>>> registry = entity.Registry()

```

 ---

## 1 Creation and Deletion

Entities can be created and deleted at any point.

Entities will also be resused once deleted

#### 1.1 Spawning

Creation of entities is done with the spawn method.

```py

>>> e = registry.spawn()
>>> e
1

```

#### 1.2 Checking ownership

Once created, you can check if the registry has the entity with the `.has` method:

```py

>>> registry.has(e)
True
  
```

#### 1.3 Deletion

Deleting entities is done with the `.despawn` method.

Once deleted, the entity will be recycled into the new entity.
It will have the same entity but with its generation incremented

```py

>>> registry.despawn(e)
>>> registry.has(e)
False

```

## 2 Entity Composition

Each entity is an int with 64 significant bits, divided in two halves.

The lower half is the entity itself, the bottom  half is a generation encoded in the identifier.

You can access both with the `.unpack` method:

```py

>>> e = registry.spawn()
>>> entity.unpack(e)
(1, 1)

```

Or individually with the `lower_half_of` and `upper_half_of` functions respectively:

```py

>>> entity.lower_half_of(e)
1

>>> entity.upper_half_of(e)
1

```

## 3 Relations

Each half of an entity reserves its most significant bit as a flag so they can be used as relations.

The lower half reserves a flag for exclusive relations, and the top half reserves a flag to mark the relation itself.

#### 3.1 Creation

Relations are created outside of a registry. This is because they will be managed by the world.

Creation is done with the `.relation` method:

```py

>>> e = registry.spawn()
>>> likes = registry.spawn()
>>> likes_e = entity.relation(likes, e)

```

Any entity can be used as either part of a relation.

#### 3.2 Exclusive Relations

Exclusive relation are relations that are only allowed to present on an entity with one target.
In the case of this example:

```py

>>> child_of = registry.spawn()
>>> child_of_e = entity.relation(child_of, e, exclusive=True)

```

...an entity with a `child_of` relation could only be the child of one entity at a time.

#### 3.3 Predicates

The library provides predicate functions for 2
- whether an entity is a relation
- whether a relation is exclusive

these are the `is_relation` and `is_exclusive` respectively:
  
```py

>>> entity.is_relation(e)
False

>>> entity.is_relation(likes_e)
True

>>> entity.is_exclusive(likes_e)
False

>>> entity.is_relation(child_of_e)
True

>>> entity.is_exclusive(child_of_e)
True

```

