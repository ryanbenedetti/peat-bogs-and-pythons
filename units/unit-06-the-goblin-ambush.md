# Unit 6: The Goblin Ambush

*Concepts: classes, `__init__` and `self`, methods, `@property`, pytest fixtures, dataclasses with behavior, objects working together*

## The story so far

Captain Hale's boots fade behind you as you descend into the lower levels. The torches here are older and farther apart. The air smells of wet stone and something sour.

Then a shape drops from a ledge above the stairs. A goblin, all knees and teeth, with a rusty cleaver in one fist. King Smund and Queen Goura keep packs of them down here to guard the dungeon, and this one has noticed you.

You've fought with *functions* so far: an armor class here, a hit check there. But a goblin isn't a calculation. It has hit points that go down, and it does things. It attacks. It can be defeated. It's a thing with **state** and **behavior**, and Python has a tool for exactly that: the **class**.

## The quest log

By the end of this unit, these tests will pass:

- [ ] A monster knows its name, hit points, armor class, attack bonus, and damage
- [ ] Taking damage lowers a monster's hit points, but never below zero
- [ ] A monster knows when it has been defeated
- [ ] The hero has hit points and an armor class computed from their sheet
- [ ] A goblin's attack either hits or misses, and a hit hurts the hero

## Before you start

Run `python tasks.py test`. You should see `61 passed`. All new files go in `game/`.

## Part 1: Your first class

In Unit 4, `@dataclass` wrote a lot of code for you behind the scenes. This time you'll write that code by hand once, so you know what the decorator was doing.

### Write the test first

Create `test_monster.py`:

```python
from monster import Monster


def test_new_monster_starts_at_full_health():
    goblin = Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)
    assert goblin.hit_points == 7
```

```
E   ModuleNotFoundError: No module named 'monster'
```

Create `monster.py`:

```python
class Monster:
    def __init__(self, name, hit_points, armor_class, attack_bonus, damage):
        self.name = name
        self.hit_points = hit_points
        self.armor_class = armor_class
        self.attack_bonus = attack_bonus
        self.damage = damage
```

Run `pytest`. Green. Here's what you wrote:

- `class Monster:` defines a **blueprint**. Writing `Monster(...)` builds one **object** from it.
- `__init__` is a special method that runs automatically when an object is built. It sets the object up.
- `self` is the object being built (or later, the object a method was called on). Python passes it to every method as the first argument.
- `self.hit_points = hit_points` stores a value **on the object**, so it's remembered.

## Part 2: Behavior

Fighting means hit points go down. Add a test:

```python
def test_take_damage_lowers_hit_points():
    goblin = Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)
    goblin.take_damage(3)
    assert goblin.hit_points == 4
```

```
E   AttributeError: 'Monster' object has no attribute 'take_damage'
```

A function defined inside a class is called a **method**. Add one to `monster.py`, indented inside the class:

```python
    def take_damage(self, amount):
        self.hit_points -= amount
```

Green. The method changes the object's own hit points, and that's what makes the object more than a bag of data. It carries **state** and the **behavior** that updates it.

Now the edge case. Hit points can't go negative. Add a test:

```python
def test_hit_points_stop_at_zero():
    goblin = Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)
    goblin.take_damage(10)
    assert goblin.hit_points == 0
```

```
E       assert -3 == 0
```

The fix uses the built-in `max()`, which returns the larger of its arguments:

```python
    def take_damage(self, amount):
        self.hit_points = max(0, self.hit_points - amount)
```

Green again.

### Knowing when it's over

Add a test that a fresh goblin isn't defeated:

```python
def test_healthy_monster_is_not_defeated():
    goblin = Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)
    assert not goblin.is_defeated
```

```
E   AttributeError: 'Monster' object has no attribute 'is_defeated'
```

Add it as a method:

```python
    def is_defeated(self):
        return self.hit_points == 0
```

Run `pytest`:

```
>       assert not goblin.is_defeated
E       assert not is_defeated
E        +  where is_defeated = <monster.Monster object at 0x...>.is_defeated
```

It fails, and the test was right to. We forgot the parentheses. Without them, `goblin.is_defeated` isn't the *answer*, it's the **method itself**, and a method object is always truthy. If we'd only written a test for the defeated case (`assert goblin.is_defeated`), it would have passed by accident while the code was broken. That's why the healthy-goblin test matters.

You could write `goblin.is_defeated()` in the test. But `goblin.is_defeated` reads better, as a fact about the goblin rather than an action. Python lets you have that with the `@property` decorator, which makes a method look like an attribute:

```python
    @property
    def is_defeated(self):
        return self.hit_points == 0
```

Green. Now add the other half of the rule:

```python
def test_monster_at_zero_hit_points_is_defeated():
    goblin = Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)
    goblin.take_damage(7)
    assert goblin.is_defeated
```

Passes.

## Part 3: Fixtures

Look at your test file. Every test builds the same goblin on its own line, and that line is long. Pytest has a tool for shared setup, the **fixture**: a function whose result is handed to any test that asks for it by name.

Rewrite `test_monster.py`, using a fixture for the goblin and a table (from Unit 5) for the damage cases:

```python
import pytest

from monster import Monster


@pytest.fixture
def goblin():
    return Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)


def test_new_monster_starts_at_full_health(goblin):
    assert goblin.hit_points == 7


@pytest.mark.parametrize(
    "damage, expected",
    [
        pytest.param(3, 4, id="scratch"),
        pytest.param(7, 0, id="exactly-enough"),
        pytest.param(10, 0, id="overkill-stops-at-zero"),
    ],
)
def test_take_damage_lowers_hit_points(goblin, damage, expected):
    goblin.take_damage(damage)
    assert goblin.hit_points == expected


def test_healthy_monster_is_not_defeated(goblin):
    assert not goblin.is_defeated


def test_monster_at_zero_hit_points_is_defeated(goblin):
    goblin.take_damage(7)
    assert goblin.is_defeated
```

Notice that a test just lists `goblin` as a parameter, and pytest runs the fixture and passes in the result. **Every test gets a fresh goblin**, so one test's damage can't leak into the next. Run `pytest`. All green.

## Part 4: Back to dataclasses

Your `Monster` class works, but `__init__` is five lines of repetition, and printing a goblin shows nothing useful:

```
<monster.Monster object at 0x7f3d...>
```

This is exactly what `@dataclass` was built to remove. Replace the top of `monster.py` so the class keeps its methods but loses the hand-written `__init__`:

```python
from dataclasses import dataclass


@dataclass
class Monster:
    """Something hostile with hit points and a weapon.

    >>> goblin = Monster("Goblin", 7, 15, 4, 5)
    >>> goblin.take_damage(3)
    >>> goblin.hit_points
    4
    """

    name: str
    hit_points: int
    armor_class: int
    attack_bonus: int
    damage: int

    def take_damage(self, amount: int) -> None:
        self.hit_points = max(0, self.hit_points - amount)

    @property
    def is_defeated(self) -> bool:
        return self.hit_points == 0
```

Run `pytest`. **Every test still passes without changing a single line**, because the tests check *what a monster does*, not *how it's built*. That's the reward for testing behavior. A goblin now prints as `Monster(name='Goblin', hit_points=7, ...)`, which makes failure messages much easier to read.

So the rule of thumb is: use a plain class when you need unusual setup, and a dataclass when a class is mostly data with some behavior added. Most of the time, in games like this one, that's a dataclass.

## Part 5: Giving the hero hit points

A goblin that attacks needs someone to attack. In Unit 4 you built `Character`, which has a name, abilities, and a backpack, but nothing that can be hurt. Add tests to the bottom of `test_character.py`, and make sure `import pytest` is at the top of the file:

```python
def test_new_character_starts_with_ten_hit_points():
    assert Character("Wren").hit_points == 10


@pytest.mark.parametrize(
    "damage, expected",
    [
        pytest.param(3, 7, id="scratch"),
        pytest.param(10, 0, id="exactly-enough"),
        pytest.param(25, 0, id="overkill-stops-at-zero"),
    ],
)
def test_take_damage_lowers_hit_points(damage, expected):
    wren = Character("Wren")
    wren.take_damage(damage)
    assert wren.hit_points == expected


@pytest.mark.parametrize(
    "abilities, armor_bonus, expected",
    [
        pytest.param({"Dexterity": 14}, 0, 12, id="nimble"),
        pytest.param({"Dexterity": 14}, 3, 15, id="nimble-in-armor"),
        pytest.param({}, 0, 10, id="no-dexterity-listed-means-average"),
    ],
)
def test_armor_class_comes_from_the_sheet(abilities, armor_bonus, expected):
    wren = Character("Wren", abilities, armor_bonus=armor_bonus)
    assert wren.armor_class == expected
```

Run `pytest` and work through the red messages in turn, adding fields and methods as each one demands:

```
E   AttributeError: 'Character' object has no attribute 'hit_points'
E   AttributeError: 'Character' object has no attribute 'take_damage'
E   TypeError: Character.__init__() got an unexpected keyword argument 'armor_bonus'
E   AttributeError: 'Character' object has no attribute 'armor_class'
```

When you're done, `character.py` looks like this:

```python
from dataclasses import dataclass, field

import combat
from items import Item
from narrator import describe_abilities


@dataclass
class Character:
    name: str
    abilities: dict[str, int] = field(default_factory=dict)
    backpack: list[Item] = field(default_factory=list)
    hit_points: int = 10
    armor_bonus: int = 0

    def take_damage(self, amount: int) -> None:
        self.hit_points = max(0, self.hit_points - amount)

    @property
    def armor_class(self) -> int:
        dexterity = self.abilities.get("Dexterity", 10)
        return combat.armor_class(dexterity, self.armor_bonus)


def describe_sheet(character: Character) -> str:
    """Narrate a character's name and abilities.

    >>> print(describe_sheet(Character("Wren", {"Strength": 8})))
    Wren
    Strength 8 (-1)
    """
    return f"{character.name}\n{describe_abilities(character.abilities)}"
```

Two details are worth a look:

- **`self.abilities.get("Dexterity", 10)`** is the dictionary's safe lookup. If the key is missing, you get the default (10, an average score) instead of a `KeyError`.
- **`import combat`** followed by `combat.armor_class(...)` avoids a name clash. Inside `Character`, we define a property called `armor_class`, and importing the function with the same name would be confusing. Importing the module keeps the two apart.

Also notice that `take_damage` now exists in two classes, with identical code. That duplication is fine for now, and the side quests come back to it.

## Part 6: The ambush

At last the goblin swings. The goblin's attack needs two things: a roll, and a target. For now, **we'll hand the roll in ourselves**. Real dice are random, and random is hard to test. Unit 7 is all about that.

Add to `test_monster.py`:

```python
from character import Character
from monster import Monster


@pytest.fixture
def hero():
    return Character("Wren", abilities={"Dexterity": 14}, hit_points=10)


def test_goblin_hit_hurts_the_hero(goblin, hero):
    damage = goblin.attack(hero, roll=8)
    assert damage == 5
    assert hero.hit_points == 5


def test_goblin_miss_leaves_the_hero_unharmed(goblin, hero):
    damage = goblin.attack(hero, roll=7)
    assert damage == 0
    assert hero.hit_points == 10
```

The numbers: Wren's armor class is 12 (10 plus a +2 Dexterity modifier). The goblin has a +4 attack bonus. A roll of 8 gives a total of 12, a tie, which hits. A roll of 7 gives 11, which misses.

```
E   AttributeError: 'Monster' object has no attribute 'attack'
```

Add the method to `Monster`, and import the hit rule you wrote in Unit 5:

```python
from combat import attack_hits
```

```python
    def attack(self, target: Character, roll: int) -> int:
        """Attack a character and return the damage dealt (0 on a miss)."""
        if not attack_hits(roll, self.attack_bonus, target.armor_class):
            return 0
        target.take_damage(self.damage)
        return self.damage
```

(Also add `from character import Character` at the top of `monster.py`, for the type hint.)

Run `pytest`. Green. Look at what happened: `Monster.attack` asks the target for its `armor_class`, then tells it to `take_damage`. The goblin doesn't know *how* the hero computes armor, and the hero doesn't know *how* the goblin decides to swing. They cooperate through small, tested interfaces. You didn't re-test the natural 1 and natural 20 rules either, because `attack_hits` already has them covered. Small pieces that are tested separately combine safely.

## Final code

`monster.py`:

```python
from dataclasses import dataclass

from character import Character
from combat import attack_hits


@dataclass
class Monster:
    """Something hostile with hit points and a weapon.

    >>> goblin = Monster("Goblin", 7, 15, 4, 5)
    >>> goblin.take_damage(3)
    >>> goblin.hit_points
    4
    """

    name: str
    hit_points: int
    armor_class: int
    attack_bonus: int
    damage: int

    def take_damage(self, amount: int) -> None:
        self.hit_points = max(0, self.hit_points - amount)

    @property
    def is_defeated(self) -> bool:
        return self.hit_points == 0

    def attack(self, target: Character, roll: int) -> int:
        """Attack a character and return the damage dealt (0 on a miss)."""
        if not attack_hits(roll, self.attack_bonus, target.armor_class):
            return 0
        target.take_damage(self.damage)
        return self.damage
```

Run everything:

```bash
python tasks.py test
```

You should see `77 passed`.

## Loot (what you learned)

- A class bundles **state** (data stored on the object) with **behavior** (methods)
- `__init__` sets an object up, and `self` is the object itself
- A method that changes `self` is how an object updates its own state
- `@property` lets a method read like an attribute, and forgetting it (or the parentheses) gives you a method object that's always truthy
- Pytest fixtures provide shared setup, and every test gets a fresh copy
- `@dataclass` removes the `__init__` boilerplate, and you can still add methods
- Testing behavior rather than structure lets you refactor freely
- Objects cooperate through small interfaces: ask for `armor_class`, say `take_damage`
- `dict.get(key, default)` is the safe way to read an optional key

## Side quests

- **Hero strikes back.** Add `attack(target, roll)` to `Character`, with an `attack_bonus` and `damage` on the sheet. Write the tests first, and reuse `attack_hits`.
- **Remove the duplicate.** `take_damage` appears in two classes. Extract the shared logic into one small function both classes call. Then look up how inheritance would solve it, and think about whether a `Character` really *is a kind of* `Monster`.
- **Hero down.** Give `Character` an `is_defeated` property, and make sure a hero at zero hit points can't be attacked further.
- **Healing.** Add `heal(amount)`. It needs a `max_hit_points` so healing can't exceed it. Table-test the edge cases.
- **A whole pack.** Write a fixture that returns three goblins, and a test that one attack on one goblin doesn't change the others.

## Next quest

The goblin's cleaver clangs off the stone, and for one long moment you stand toe to toe in the dark. You've been choosing the rolls yourself: `roll=8`, `roll=7`. But in a real fight, the dice decide, and nobody gets to pick them. How do you test a game whose outcomes are random?

In **Unit 7**, you build real dice, and then learn the most important trick in testing: swapping them for **loaded** ones.

---

*Co-drafted with Claude, an AI assistant made by Anthropic. Edited, revised, and improved with natural, human intelligence.*
