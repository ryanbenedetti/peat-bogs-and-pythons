# Unit 8: When Things Go Wrong

*Concepts: exceptions, `raise`, `try`/`except`, custom exception classes, exception hierarchies, `pytest.raises`, `match`*

## The story so far

The iron door groans open and you step through into what was once the dungeon's guardroom. Now it looks like a place where a fight ended badly for everyone. Crates are smashed, chains lie in loops across the floor, a dice table is flipped on its side, and the goblin you beat is still sprawled on the stairs behind you.

Beyond the wreckage, a low rumble comes through the stone. It sounds like breathing. Vios is close.

But looking around, you notice how many things in this room could go wrong in *your* game, not just in the castle. A die with no faces. An item you reach for that isn't in your pack. A creature that's already defeated getting up to swing at you again. So far, your code has assumed that everything works. Real code needs to decide what happens when it doesn't.

## The quest log

By the end of this unit, these tests will pass:

- [ ] Rolling a die with fewer than one side is refused, with a clear message
- [ ] Dropping an item you don't have raises a specific, game-flavored error
- [ ] A defeated creature can't attack, and a defeated hero can't be attacked
- [ ] Higher-level code catches those errors and narrates them instead of crashing

## Before you start

Run `python tasks.py test`. You should see `86 passed`. All new files go in `game/`.

## What is an exception?

When Python hits a problem it can't continue past, it stops and **raises an exception**, a special object describing what went wrong. You've been seeing them all book long: `ModuleNotFoundError`, `KeyError`, `TypeError`. If nothing handles an exception, the program stops and prints a traceback.

You can do two things with exceptions:

- **Raise** one yourself, with `raise`, when your code has been asked to do something it shouldn't
- **Catch** one, with `try`/`except`, when you know what to do about it

The skill is knowing *where* to do each. We'll practice both, and we'll test both.

## Part 1: The die with no faces

What happens if someone rolls a die with zero sides? Open a Python prompt, or just reason about it: `roll_die(0)` calls `random.randint(1, 0)`, and Python's own `random` module will complain. Let's see how clearly.

Add a test to `test_dice.py`, and make sure `import pytest` is at the top of the file:

```python
def test_a_die_needs_at_least_one_side():
    with pytest.raises(ValueError):
        roll_die(0)
```

`pytest.raises` is a **context manager**, which is what the `with` is for. It says: "the code inside this block must raise this kind of exception. If it does, the test passes. If it doesn't, the test fails."

Run `pytest`. It **passes immediately**, because `random.randint(1, 0)` already raises a `ValueError`. But what does the player (or the developer reading a log) actually see? Make the test stricter by checking the message:

```python
@pytest.mark.parametrize("sides", [0, -3])
def test_a_die_needs_at_least_one_side(sides):
    with pytest.raises(ValueError, match="at least 1"):
        roll_die(sides)
```

`match` checks the exception's message against a pattern. (It uses a regular expression and searches within the message, so a plain phrase works.)

```
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'at least 1'
E     Actual message: 'empty range in randrange(1, 1)'
```

There's the problem. Python's message talks about `randrange(1, 1)`, an internal detail nobody asked about. A good error tells the caller what *they* did wrong. Raise your own in `dice.py`:

```python
def roll_die(sides):
    if sides < 1:
        raise ValueError(f"A die needs at least 1 side, not {sides}.")
    return random.randint(1, sides)
```

Run `pytest`. Green for both rows.

Two things to notice. First, `ValueError` is Python's built-in exception for "the right *type* of value, but an unacceptable one", which is exactly this case. Second, the test failed in two different ways during this unit. With the plain `ValueError` test, a function that *never* raises would fail with a message like this:

```
E   Failed: DID NOT RAISE ValueError
```

That failure is as important as a pass: it proves the test can detect a function that forgot to complain.

## Part 2: Your own exceptions

Built-in exceptions work for general problems. For problems that belong to *your game*, define your own. Create `errors.py`:

```python
class GameError(Exception):
    """Base class for everything that can go wrong in the game."""


class ItemNotFoundError(GameError):
    """Raised when a character tries to use an item they are not carrying."""


class DefeatedError(GameError):
    """Raised when a defeated creature acts, or is acted upon."""
```

Here's what that means:

- A new exception is just a class that inherits from `Exception`. The name in parentheses is the **parent**, and the child gets everything the parent has.
- `ItemNotFoundError` and `DefeatedError` both inherit from `GameError`. That forms a small family tree, and it matters later, because catching `GameError` will catch *all of them*.
- The classes have no code of their own. Their value is their **name**, which says exactly what went wrong.

### Dropping what you don't have

Write the tests in `test_character.py`. You'll need these imports at the top: `from errors import ItemNotFoundError` (alongside the existing ones) and `from items import Item`.

```python
def test_drop_item_removes_it_and_returns_it():
    rope = Item("rope", 3)
    wren = Character("Wren", backpack=[rope])
    assert wren.drop_item("rope") == rope
    assert wren.backpack == []


def test_dropping_something_you_do_not_have_raises():
    wren = Character("Wren")
    with pytest.raises(ItemNotFoundError, match="rope"):
        wren.drop_item("rope")
```

```
E   AttributeError: 'Character' object has no attribute 'drop_item'
```

Add the method to `Character` in `character.py` (and `from errors import ItemNotFoundError` at the top):

```python
    def drop_item(self, name: str) -> Item:
        """Remove an item from the backpack and return it."""
        for item in self.backpack:
            if item.name == name:
                self.backpack.remove(item)
                return item
        raise ItemNotFoundError(f"You are not carrying a {name}.")
```

The loop looks for a match and returns as soon as it finds one. If the loop finishes without finding anything, execution falls through to the `raise`. Run `pytest`. Green.

You might wonder why `drop_item` doesn't just return `None` when the item is missing. Because then every caller has to remember to check, and one that forgets will quietly carry on with nothing. An exception **can't be ignored by accident**. It travels up until somebody deals with it. Python programmers call this style "easier to ask forgiveness than permission": try the thing, and handle failure if it happens.

## Part 3: Striking the defeated

In Unit 6 you gave monsters an `is_defeated` property. The hero needs one too, and then we can enforce a simple rule: **defeated creatures can't fight, and can't be fought.**

First the property. Add to `test_character.py`:

```python
def test_new_character_is_not_defeated():
    assert not Character("Wren").is_defeated


def test_character_at_zero_hit_points_is_defeated():
    wren = Character("Wren")
    wren.take_damage(10)
    assert wren.is_defeated
```

And add to `Character`:

```python
    @property
    def is_defeated(self) -> bool:
        return self.hit_points == 0
```

Now the attack rules. Add to `test_monster.py` (with `from errors import DefeatedError` in the imports):

```python
def test_a_defeated_monster_cannot_attack(goblin, hero, loaded_dice):
    goblin.take_damage(7)
    with pytest.raises(DefeatedError, match="Goblin"):
        goblin.attack(hero, roller=loaded_dice())


def test_cannot_attack_a_defeated_hero(goblin, hero, loaded_dice):
    hero.take_damage(10)
    with pytest.raises(DefeatedError, match="Wren"):
        goblin.attack(hero, roller=loaded_dice())
```

Notice `loaded_dice()` with **no values**. Those dice raise an error if anyone rolls them at all. So these tests also prove something subtle: the check happens **before** the roll. A defeated goblin shouldn't even touch the dice.

```
E   StopIteration
```

That's the empty dice complaining, because the goblin tried to roll them. The test is red for exactly the right reason: nothing stops a defeated goblin from swinging. Update `attack` in `monster.py`, and add `from errors import DefeatedError` at the top:

```python
    def attack(self, target: Character, roller: Roller = roll_die) -> int:
        """Attack a character and return the damage dealt (0 on a miss)."""
        if self.is_defeated:
            raise DefeatedError(f"The {self.name} is defeated and cannot attack.")
        if target.is_defeated:
            raise DefeatedError(f"{target.name} is already defeated.")
        roll = roller(20)
        if not attack_hits(roll, self.attack_bonus, target.armor_class):
            return 0
        target.take_damage(self.damage)
        return self.damage
```

These two `if` blocks at the top are called **guard clauses**. They reject bad situations first, so the rest of the method can assume everything is fine. Run `pytest`. Green.

## Part 4: Catching the errors

So far we've only *raised* exceptions. But a game that crashes every time the player does something silly is no fun. Somewhere closer to the player, something has to catch these errors and turn them into something readable.

This is the key design idea of the unit: **low-level code raises, high-level code decides what to do about it.** `drop_item` doesn't know whether it's being called by a game, a test, or a robot, so it just refuses. A layer above it knows there's a player reading, so it narrates.

Create `test_actions.py`:

```python
import pytest

from actions import drop, narrate_attack
from character import Character
from items import Item
from monster import Monster


@pytest.fixture
def goblin():
    return Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)


@pytest.fixture
def hero():
    return Character("Wren", abilities={"Dexterity": 14}, hit_points=10)


def test_dropping_an_item_is_narrated():
    wren = Character("Wren", backpack=[Item("rope", 3)])
    assert drop(wren, "rope") == "You drop the rope."


def test_dropping_a_missing_item_is_narrated_not_raised():
    assert drop(Character("Wren"), "rope") == "You are not carrying a rope."


def test_a_hit_is_narrated(goblin, hero, loaded_dice):
    result = narrate_attack(goblin, hero, loaded_dice(8))
    assert result == "The Goblin hits Wren for 5 damage."


def test_a_miss_is_narrated(goblin, hero, loaded_dice):
    result = narrate_attack(goblin, hero, loaded_dice(7))
    assert result == "The Goblin swings at Wren and misses."


def test_an_impossible_attack_is_narrated_not_raised(goblin, hero, loaded_dice):
    goblin.take_damage(7)
    result = narrate_attack(goblin, hero, loaded_dice())
    assert result == "The Goblin is defeated and cannot attack."
```

(The two fixtures repeat the ones in `test_monster.py`. That duplication is a hint that they belong in `conftest.py`. The first side quest asks you to move them.)

```
E   ModuleNotFoundError: No module named 'actions'
```

Create `actions.py`:

```python
from character import Character
from dice import Roller, roll_die
from errors import GameError, ItemNotFoundError
from monster import Monster


def drop(character: Character, item_name: str) -> str:
    """Drop an item and narrate what happened.

    >>> drop(Character("Wren"), "rope")
    'You are not carrying a rope.'
    """
    try:
        item = character.drop_item(item_name)
    except ItemNotFoundError as error:
        return str(error)
    return f"You drop the {item.name}."


def narrate_attack(
    monster: Monster, target: Character, roller: Roller = roll_die
) -> str:
    """Resolve a monster's attack and narrate the outcome."""
    try:
        damage = monster.attack(target, roller)
    except GameError as error:
        return str(error)
    if damage == 0:
        return f"The {monster.name} swings at {target.name} and misses."
    return f"The {monster.name} hits {target.name} for {damage} damage."
```

Walk through the pieces:

- The code inside `try:` runs normally. If it raises something that matches the `except`, Python jumps there and carries on afterward.
- `except ItemNotFoundError as error` catches only that exception and names it `error`. `str(error)` gives its message.
- `except GameError` in `narrate_attack` catches **any** `GameError`, including `DefeatedError` and any exceptions you add later. That's the payoff of the family tree from Part 2.
- Anything that isn't a `GameError`, such as a real bug like a `TypeError`, still goes straight through and crashes loudly, which is exactly what you want.

Run everything:

```bash
python tasks.py test
```

You should see `100 passed`.

### Two rules for `except`

- **Catch the narrowest exception you can handle.** `except GameError` is fine because you know what to do with those. A bare `except:` or `except Exception: pass` swallows *every* error, including your own typos, and hides bugs for weeks.
- **Don't catch what you can't fix.** If your code has nothing sensible to do, let the exception travel up to something that does.

## Final code

`errors.py` and `actions.py` appear in full above. The other changes:

`dice.py`:

```python
import random
from collections.abc import Callable

Roller = Callable[[int], int]


def roll_die(sides: int) -> int:
    """Roll one die with the given number of sides.

    >>> 1 <= roll_die(6) <= 6
    True
    """
    if sides < 1:
        raise ValueError(f"A die needs at least 1 side, not {sides}.")
    return random.randint(1, sides)
```

In `character.py`, add `from errors import ItemNotFoundError` to the imports, then these inside `Character`:

```python
    @property
    def is_defeated(self) -> bool:
        return self.hit_points == 0

    def drop_item(self, name: str) -> Item:
        """Remove an item from the backpack and return it."""
        for item in self.backpack:
            if item.name == name:
                self.backpack.remove(item)
                return item
        raise ItemNotFoundError(f"You are not carrying a {name}.")
```

And `attack` in `monster.py` now starts with the two guard clauses shown in Part 3.

## Loot (what you learned)

- An exception is an object that stops normal execution until someone handles it
- `raise` signals that your code can't do what it was asked
- `try`/`except` catches an exception and lets the program carry on
- Custom exceptions are classes, and an inheritance family lets you catch a whole group with one parent
- `pytest.raises(SomeError)` asserts that code raises, and **fails** if it doesn't
- `match="..."` checks the message, which keeps errors helpful
- Guard clauses reject bad input at the top of a function
- Raising an exception can't be ignored by accident, but returning `None` can
- Low-level code raises, and high-level code decides how to respond
- Catch the narrowest exception possible, and never silently swallow everything

## Side quests

- **Shared fixtures.** `goblin` and `hero` are defined in two test files. Move them into `conftest.py` and delete the duplicates. What does pytest do if a test file defines a fixture with the same name?
- **A fuller `try`.** Look up the `else` and `finally` clauses of `try`. Rewrite `drop` using `else`. What does `finally` guarantee?
- **Unknown abilities.** `ability_check` quietly treats a missing ability as a score of 10. Should asking for `"Charisma"` on a character without one raise instead? Decide, write the test first, then implement it.
- **Negative damage.** Make `take_damage` raise a `ValueError` when given a negative amount (a "damage" of -5 would secretly heal). Table-test the boundary: -1, 0, 1.
- **Check the family tree.** Write a test asserting that `ItemNotFoundError` and `DefeatedError` are both subclasses of `GameError`. Hint: `issubclass`.
- **Whose fault?** Rewrite one of the error messages from the viewpoint of a *developer* debugging at 2 a.m. instead of a *player*. How would the two differ, and where would each belong?

## Next quest

You've picked your way through the guardroom, and ahead the corridor opens into a vast, round chamber. At its center, chained to iron rings in the floor, lies a creature larger than any you've seen, with scales the color of old coins. Vios.

But Vios isn't alone. Two goblins and a hulking guard stand between you and the chains, and they've all noticed you. A fight with one goblin is a handful of tests. A fight with four creatures needs **an order**: who acts first, and then who?

In **Unit 9**, you'll sort combatants by initiative and build the combat loop.

## Save your progress

When all tests are green, commit and tag it:

```bash
git add .
git commit -m "Add unit 8"
git tag unit-08-done
git push origin main --tags
```

Then update the README's unit table with a row for Unit 8.

---

*Co-drafted with Claude, an AI assistant made by Anthropic. Edited, revised, and improved with natural, human intelligence.*
