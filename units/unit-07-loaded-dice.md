# Unit 7: Loaded Dice

*Concepts: testing randomness, flaky tests, dependency injection, functions as values, `conftest.py`, fixtures that return functions*

## The story so far

The goblin's cleaver rings off the stone for the last time. It staggers, drops, and lies still. You stand in the dark with your heart pounding and a long scrape across one shoulder.

But something has been bothering you. Every roll in that fight was one **you** chose. `roll=8` hit and `roll=7` missed because you wrote the numbers yourself. In a real fight, nobody picks the roll. The dice decide, and dice are random.

Past the goblin's ledge stands an iron door, and it's locked. This is the lock you've been walking toward since the castle gate, and picking it means a real roll against a real difficulty. A game full of dice sounds impossible to test: how can you write a test for something that comes out differently every time?

The answer is to make sure the code never rolls the dice itself.

## The quest log

By the end of this unit, these tests will pass:

- [ ] A die only ever shows faces it actually has, and every face comes up
- [ ] A goblin's attack takes its roll from dice it's **handed**, so tests can load them
- [ ] A lock-picking check succeeds exactly when the roll plus the modifier meets the difficulty
- [ ] With real dice, a goblin's attack still either hits or misses

## Before you start

Run `python tasks.py test`. You should see `77 passed`. All new files go in `game/`.

## Part 1: Real dice

Start with the dice themselves. How do you test randomness? You can't predict *which* number comes up, but you can state facts that must always be true.

Create `test_dice.py`:

```python
from dice import roll_die


def test_a_roll_stays_within_the_faces():
    for _ in range(1000):
        assert 1 <= roll_die(6) <= 6
```

(Here a loop inside a test is fine. We want one check that must hold for every roll, and `_` is the Python habit for a loop variable you don't use.)

```
E   ModuleNotFoundError: No module named 'dice'
```

Create `dice.py` with the least that passes:

```python
def roll_die(sides):
    return 1
```

Green. A die that always shows 1 stays within its faces, so now we need a test that catches the cheat:

```python
def test_every_face_comes_up():
    seen = {roll_die(6) for _ in range(1000)}
    assert seen == {1, 2, 3, 4, 5, 6}
```

The braces build a **set**, a collection with no duplicates. After a thousand rolls, it should contain all six faces.

```
E       assert {1} == {1, 2, 3, 4, 5, 6}
```

Python's `random` module does the real work:

```python
import random


def roll_die(sides):
    return random.randint(1, sides)
```

`random.randint(1, sides)` picks a whole number from 1 up to and **including** `sides`. Run `pytest`. Green.

### Could that test ever fail by bad luck?

It's a fair worry. A test that fails once in a while for no reason is called **flaky**, and flaky tests are poison: people learn to ignore red. So do the math. The chance that a particular face *never* shows up in 1000 rolls is (5/6) to the power of 1000, and across six faces the total chance of failure is about 4 in 10^79. That's far less likely than a cosmic ray flipping a bit in your computer's memory during the test. For practical purposes it's deterministic, and it's the right way to test randomness directly: assert only facts that are true for *every* run, or false with astronomically small probability.

## Part 2: The goblin problem

But randomness creates a bigger problem. Imagine the goblin rolled its own dice:

```python
def attack(self, target):
    roll = random.randint(1, 20)
    ...
```

How would you write "the goblin hits Wren"? Whatever you assert, the dice might disagree, and your test passes about half the time. That's the worst kind of flaky.

There are three common ways out:

1. **Seed the generator.** `random.seed(42)` makes the sequence repeatable. But the test now depends on the exact numbers Python's generator produces. Those aren't guaranteed to stay the same across Python versions for every function, and *why* a roll of 5 is expected is a mystery to the next reader. Change the order of two rolls and every test breaks.
2. **Patch the random module.** Pytest's `monkeypatch` can replace `random.randint` during a test. It works, but your test is now welded to the *internals* of the code, so rewriting how the goblin rolls breaks it.
3. **Don't roll inside the code at all.** Make the dice something the code is **handed**.

The third option is called **dependency injection**, which is a fancy name for a simple habit: instead of reaching out and grabbing a dependency (here, the dice), a function takes it as a parameter. Real code passes real dice, and tests pass **loaded** dice.

## Part 3: Handing in the dice

Right now `Monster.attack` takes a ready-made `roll`. Let's change it so it takes **a way to roll** instead. A "way to roll" is just a function that takes the number of sides and returns a number. And in Python, functions are values you can pass around like any other.

### Change the tests first

In `test_monster.py`, update the two attack tests to hand in a dice function. A `lambda` is a tiny one-line function:

```python
def test_goblin_hit_hurts_the_hero(goblin, hero):
    damage = goblin.attack(hero, roller=lambda sides: 8)
    assert damage == 5
    assert hero.hit_points == 5


def test_goblin_miss_leaves_the_hero_unharmed(goblin, hero):
    damage = goblin.attack(hero, roller=lambda sides: 7)
    assert damage == 0
    assert hero.hit_points == 10
```

`lambda sides: 8` means "a function that ignores how many sides and always returns 8." These are the loaded dice.

```
E   TypeError: Monster.attack() got an unexpected keyword argument 'roller'
```

Now update `monster.py`. First, add `dice.py` a name for the idea of a rolling function, so type hints stay readable:

```python
import random
from collections.abc import Callable

Roller = Callable[[int], int]


def roll_die(sides: int) -> int:
    """Roll one die with the given number of sides.

    >>> 1 <= roll_die(6) <= 6
    True
    """
    return random.randint(1, sides)
```

`Callable[[int], int]` reads as "something you can call with an int that returns an int." Then change `attack` in `monster.py` (and add `from dice import Roller, roll_die` at the top):

```python
    def attack(self, target: Character, roller: Roller = roll_die) -> int:
        """Attack a character and return the damage dealt (0 on a miss)."""
        roll = roller(20)
        if not attack_hits(roll, self.attack_bonus, target.armor_class):
            return 0
        target.take_damage(self.damage)
        return self.damage
```

Look at the default value: `roller=roll_die`. If nobody hands in dice, the goblin uses real ones, so game code stays simple (`goblin.attack(hero)`) while tests can swap in anything. Run `pytest`. Green.

### A proper set of loaded dice

A lambda is fine when you need one roll. But a fight has many rolls: the goblin swings, then the hero, then the goblin again. You'd want dice that return a **sequence** of values. This is the kind of helper that every test file will want, so it belongs somewhere shared.

Pytest looks for a file called `conftest.py` and makes its fixtures available to every test in that folder, with no imports. Create `game/conftest.py`:

```python
import pytest


@pytest.fixture
def loaded_dice():
    """Build a roller that returns the given values, one per roll, in order."""

    def make_roller(*values):
        results = iter(values)

        def roller(sides):
            return next(results)

        return roller

    return make_roller
```

There's a lot packed in here, so go slowly:

- The fixture returns a **function** (`make_roller`), so tests can call `loaded_dice(8, 3, 15)` to build dice with whatever values they like.
- `*values` collects all the arguments into a tuple.
- `iter(values)` makes an iterator, something that hands out one value at a time, and `next(results)` fetches the next one.
- `roller` remembers `results` between calls, so each call returns the next loaded number.

Now use it. Update the two attack tests:

```python
def test_goblin_hit_hurts_the_hero(goblin, hero, loaded_dice):
    damage = goblin.attack(hero, roller=loaded_dice(8))
    assert damage == 5
    assert hero.hit_points == 5


def test_goblin_miss_leaves_the_hero_unharmed(goblin, hero, loaded_dice):
    damage = goblin.attack(hero, roller=loaded_dice(7))
    assert damage == 0
    assert hero.hit_points == 10
```

Run `pytest`. Still green, and the tests now read like a story: "load the dice with an 8, the goblin attacks, the hero takes 5."

## Part 4: Picking the lock

The iron door waits. Picking a lock is an **ability check**: roll a d20, add the modifier for the right ability, and compare the total to the lock's difficulty (the **DC**, short for difficulty class). Wren has Dexterity 14, a +2 modifier, and this lock is DC 15.

Write the table first. Create `test_checks.py`:

```python
import pytest

from character import Character
from checks import ability_check


@pytest.fixture
def wren():
    return Character("Wren", abilities={"Dexterity": 14})


@pytest.mark.parametrize(
    "roll, expected",
    [
        pytest.param(13, True, id="exactly-meets-the-dc"),
        pytest.param(12, False, id="one-short"),
        pytest.param(20, True, id="high-roll"),
        pytest.param(1, False, id="low-roll"),
    ],
)
def test_picking_the_lock(wren, loaded_dice, roll, expected):
    result = ability_check(wren, "Dexterity", dc=15, roller=loaded_dice(roll))
    assert result == expected
```

A roll of 13 plus 2 makes 15, which meets the DC. A roll of 12 makes 14, one short.

```
E   ModuleNotFoundError: No module named 'checks'
```

Create `checks.py`:

```python
from abilities import ability_modifier
from character import Character
from dice import Roller, roll_die


def ability_check(
    character: Character, ability: str, dc: int, roller: Roller = roll_die
) -> bool:
    """Roll a d20 plus the ability modifier and compare it to the difficulty.

    >>> wren = Character("Wren", {"Dexterity": 14})
    >>> ability_check(wren, "Dexterity", dc=15, roller=lambda sides: 13)
    True
    """
    score = character.abilities.get(ability, 10)
    total = roller(20) + ability_modifier(score)
    return total >= dc
```

Run `pytest`. All four rows pass. Three of your earlier functions just worked together: `ability_modifier` from Unit 1, the character's abilities from Unit 4, and a tested table from Unit 5. The gate to the dungeon swings open.

## Part 5: One test with real dice

Everything so far used loaded dice. We should also prove that the *default*, real dice still work when nobody injects anything. Add to the bottom of `test_monster.py`:

```python
def test_a_real_attack_either_hits_or_misses(goblin):
    for _ in range(200):
        hero = Character("Wren", abilities={"Dexterity": 14}, hit_points=10)
        assert goblin.attack(hero) in (0, goblin.damage)
```

Whatever the dice say, the damage is either 0 (a miss) or the goblin's full damage (a hit). This is a **smoke test**: it can't check exact outcomes, but it proves the real wiring runs, and it can never flake. Run everything:

```bash
python tasks.py test
```

You should see `86 passed`. Run it a few more times. It should say `86 passed` every time.

## Final code

`dice.py`, `conftest.py`, and `checks.py` are shown above. The only other change is the `attack` method in `monster.py`:

```python
    def attack(self, target: Character, roller: Roller = roll_die) -> int:
        """Attack a character and return the damage dealt (0 on a miss)."""
        roll = roller(20)
        if not attack_hits(roll, self.attack_bonus, target.armor_class):
            return 0
        target.take_damage(self.damage)
        return self.damage
```

with `from dice import Roller, roll_die` added to its imports.

## Loot (what you learned)

- Test randomness directly by asserting facts that are always true (a range, a complete set of faces)
- A test that fails by bad luck is **flaky**, so design random tests so failure is astronomically unlikely
- **Dependency injection:** hand code the things it depends on instead of letting it grab them
- Functions are values: you can pass them as arguments, give them defaults, and return them
- A default argument (`roller=roll_die`) keeps production code simple while tests substitute fakes
- `lambda` makes a tiny one-line function
- `conftest.py` shares fixtures across a whole test folder
- A fixture can return a function, which makes it a factory for test data
- A **smoke test** with real dice proves the default wiring works without asserting exact results

## Side quests

- **Honest dice.** `loaded_dice(8)` raises a confusing `StopIteration` if code rolls more times than you loaded. Make it fail with a clear message instead, so a test that rolls too often tells you exactly what went wrong.
- **Checking the die size.** Right now a bug that rolls a d6 instead of a d20 would slip through. Make the loaded dice remember the `sides` they were asked for, and add a test that an attack asks for a d20.
- **Hero's turn.** If you wrote `Character.attack` in the Unit 6 side quest, give it the same injected `roller` and test it with loaded dice.
- **Damage dice.** Replace the goblin's flat damage of 5 with a damage roll (say 1d6). Which tests change? Which don't?
- **A seeded experiment.** Just to see the difference, write a test using `random.seed(1)`. What would you have to explain to the next reader?

## Next quest

The iron door swings open on a screech of rusted hinges. Beyond it you can see torchlight and the shape of enormous coils. You're close to Vios. But the room is a wreck: overturned crates, broken chains, and a floor full of things that can go wrong. Reaching for an item you don't have. Rolling a die with no faces. Striking something that's already defeated.

In **Unit 8**, you learn what code should do when the answer is "that's not allowed." That means exceptions, `raise`, and testing for failure on purpose.

## Save your progress

When all tests are green, commit and tag it:

```bash
git add .
git commit -m "Add unit 7"
git tag unit-07-done
git push origin main --tags
```

Then update the README's unit table with a row for Unit 7.

---

*Co-drafted with Claude, an AI assistant made by Anthropic. Edited, revised, and improved with natural, human intelligence.*
