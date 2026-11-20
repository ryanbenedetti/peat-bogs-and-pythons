# Unit 9: The Turn Order

*Concepts: `sorted` and `.sort` with `key=` and `reverse=`, sort stability, tuple comparison, shared fixtures, `while` loops with limits, `is` versus `==`, `any` and `all`, events as data*

## The story so far

The corridor opens into a round chamber, vast and cold, with a ceiling lost in darkness. In the middle, chained to iron rings set into the floor, lies Vios. Its scales are the color of old coins, and each slow breath stirs the dust.

Two goblins and a hulking guard stand between you and the chains. They've seen you. In the next heartbeat, everyone moves at once, except that nobody can, because in a game, **somebody has to go first**.

A fight isn't a single attack. It's a series of turns, and deciding *whose* turn comes next is a rule like any other. Your game needs a turn order, and a loop that keeps the fight going until one side stands and the other doesn't.

## The quest log

By the end of this unit, these tests will pass:

- [ ] Every combatant rolls initiative, and the highest total acts first, with ties going to the higher bonus
- [ ] The hero can attack monsters, not just be attacked by them
- [ ] A fight runs round by round until one side is defeated
- [ ] Defeated fighters are skipped, and attackers pick the next enemy still standing
- [ ] A fight nobody can win stops at a round limit instead of running forever

## Before you start

Run `python tasks.py test`. You should see `100 passed`. All new files go in `game/`.

## Part 1: Who goes first?

The rule: every combatant rolls a d20 and adds an **initiative bonus**. The highest total goes first. If two totals tie, the one with the higher bonus goes first. If they're still tied, whoever was listed first goes first.

### Giving everyone an initiative bonus

Heroes and monsters both need an `initiative_bonus`. For a monster it's a plain stat. For a hero it comes from their Dexterity, just like the armor class you built in Unit 6.

Add a test to `test_character.py`:

```python
def test_initiative_bonus_comes_from_dexterity():
    assert Character("Wren", {"Dexterity": 14}).initiative_bonus == 2
```

```
E   AttributeError: 'Character' object has no attribute 'initiative_bonus'
```

Add a property to `Character` in `character.py`, and `from abilities import ability_modifier` to its imports:

```python
    @property
    def initiative_bonus(self) -> int:
        return ability_modifier(self.abilities.get("Dexterity", 10))
```

For monsters, add one line at the end of the fields in `monster.py`:

```python
    damage: int
    initiative_bonus: int = 0
```

Because it has a default, every existing `Monster(...)` call in your tests still works unchanged. Run `pytest`. Green.

Notice what's happening: `Character` and `Monster` are different classes, but both now have `name`, `initiative_bonus`, `is_defeated`, and `take_damage`. Python doesn't need them to share a parent. Code that only needs those attributes will work with either. This is called **duck typing**: if it walks like a duck and quacks like a duck, it's treated as a duck.

### Write the tests first

Create `test_initiative.py`:

```python
import pytest

from character import Character
from initiative import roll_initiative
from monster import Monster


@pytest.fixture
def wren():
    return Character("Wren", abilities={"Dexterity": 14})  # initiative +2


@pytest.fixture
def goblin():
    return Monster("Goblin", 7, 15, 4, 5, initiative_bonus=1)


@pytest.fixture
def guard():
    return Monster("Guard", 12, 16, 5, 6)  # initiative +0


@pytest.mark.parametrize(
    "rolls, expected_order",
    [
        pytest.param((5, 10, 8), ["Goblin", "Guard", "Wren"], id="highest-total-first"),
        pytest.param((7, 5, 8), ["Wren", "Guard", "Goblin"], id="bonus-is-added-to-the-roll"),
    ],
)
def test_initiative_order(wren, goblin, guard, loaded_dice, rolls, expected_order):
    order = roll_initiative([wren, goblin, guard], loaded_dice(*rolls))
    assert [fighter.name for fighter in order] == expected_order
```

The loaded dice are consumed **in the order the fighters are listed**: first Wren's roll, then the goblin's, then the guard's. In the first row, the totals are Wren 5+2=7, Goblin 10+1=11, Guard 8+0=8, so the order is Goblin, Guard, Wren.

```
E   ModuleNotFoundError: No module named 'initiative'
```

### Sorting

Python can sort any list with `sorted()`, and you control *how* with a `key` function that says what to sort on. Create `initiative.py`:

```python
from dice import Roller, roll_die


def roll_initiative(combatants, roller=roll_die):
    rolled = [(roller(20) + fighter.initiative_bonus, fighter) for fighter in combatants]
    rolled.sort(key=lambda pair: pair[0], reverse=True)
    return [fighter for _, fighter in rolled]
```

Here's how it reads:

- The first line builds a list of **pairs**: each fighter's total, next to the fighter. (It's a list comprehension, from Unit 4.)
- `rolled.sort(...)` sorts that list in place. `key=lambda pair: pair[0]` says "sort by the first item of each pair, the total", and `reverse=True` puts the biggest first.
- The last line throws the totals away and keeps just the fighters, in their new order. The `_` is the usual name for a value you don't need.

Run `pytest`. Both rows pass.

### The tie

Now the tie-break rule. The tricky part is writing a test where the *right* answer isn't also what a lazy implementation would produce by accident. In our lineup, the highest-bonus fighter always comes first in the list, so a lazy sort would pass. List the goblin first instead:

```python
def test_a_tied_total_goes_to_the_higher_bonus(wren, goblin, loaded_dice):
    order = roll_initiative([goblin, wren], loaded_dice(11, 10))
    assert [fighter.name for fighter in order] == ["Wren", "Goblin"]
```

The goblin rolls 11+1 and Wren rolls 10+2, so both total 12.

```
E       AssertionError: assert ['Goblin', 'Wren'] == ['Wren', 'Goblin']
E         At index 0 diff: 'Goblin' != 'Wren'
```

Python's sort is **stable**: items that compare equal keep their original order. So on a tie, the goblin stays ahead because he was listed first. We need the sort key to consider *two* things. A key can be a **tuple**, and Python compares tuples one position at a time: it looks at the first item, and only if those are equal does it look at the second.

```python
    rolled.sort(key=lambda pair: (pair[0], pair[1].initiative_bonus), reverse=True)
```

Run `pytest`. Green. Finally, pin down the last rule, which is that a complete tie keeps the listed order. Because sorting is stable, and `reverse=True` doesn't disturb that, this test should pass the moment you write it:

```python
def test_a_complete_tie_keeps_the_listed_order(loaded_dice):
    first = Monster("First Goblin", 7, 15, 4, 5, initiative_bonus=1)
    second = Monster("Second Goblin", 7, 15, 4, 5, initiative_bonus=1)
    order = roll_initiative([first, second], loaded_dice(10, 10))
    assert order == [first, second]
```

A test that passes immediately isn't wasted. It documents a rule and guards it against future edits.

## Part 2: The hero strikes back

So far monsters can attack heroes, but heroes can't attack back. Before the fight loop, give `Character` an attack. You've used `hero` and `goblin` fixtures in two different test files, and now a third needs them. That's the cue to move them into `conftest.py`. (If you did the Unit 8 side quest, you've already done this.) Replace `game/conftest.py`:

```python
import pytest

from character import Character
from monster import Monster


@pytest.fixture
def goblin():
    return Monster("Goblin", hit_points=7, armor_class=15, attack_bonus=4, damage=5)


@pytest.fixture
def hero():
    return Character("Wren", abilities={"Dexterity": 14}, hit_points=10)


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

Then delete the `goblin` and `hero` fixture definitions from `test_monster.py` and `test_actions.py`. Run `pytest` and confirm nothing broke. Every test still finds its fixtures, because `conftest.py` provides them to the whole folder.

### Tests for the hero's attack

Add to `test_character.py` (and extend its import with `from errors import DefeatedError, ItemNotFoundError`):

```python
def test_hero_hit_hurts_the_goblin(hero, goblin, loaded_dice):
    damage = hero.attack(goblin, roller=loaded_dice(12))
    assert damage == 4
    assert goblin.hit_points == 3


def test_hero_miss_leaves_the_goblin_unharmed(hero, goblin, loaded_dice):
    damage = hero.attack(goblin, roller=loaded_dice(11))
    assert damage == 0
    assert goblin.hit_points == 7


def test_a_defeated_hero_cannot_attack(hero, goblin, loaded_dice):
    hero.take_damage(10)
    with pytest.raises(DefeatedError, match="Wren"):
        hero.attack(goblin, roller=loaded_dice())
```

The goblin's armor class is 15. The hero's attack bonus will be +3, so a roll of 12 makes 15 (a hit) and 11 makes 14 (a miss).

```
E   AttributeError: 'Character' object has no attribute 'attack'
```

Give `Character` two new fields, `attack_bonus: int = 3` and `damage: int = 4`, after `armor_bonus`. Then add the method, along with these imports at the top of `character.py`:

```python
from dice import Roller, roll_die
from errors import DefeatedError, ItemNotFoundError
```

```python
    def attack(self, target, roller: Roller = roll_die) -> int:
        """Attack a monster and return the damage dealt (0 on a miss)."""
        if self.is_defeated:
            raise DefeatedError(f"{self.name} is defeated and cannot attack.")
        if target.is_defeated:
            raise DefeatedError(f"The {target.name} is already defeated.")
        roll = roller(20)
        if not combat.attack_hits(roll, self.attack_bonus, target.armor_class):
            return 0
        target.take_damage(self.damage)
        return self.damage
```

Run `pytest`. Green. If this looks very familiar, it is. This method is nearly a copy of `Monster.attack`, and `take_damage` is already duplicated too. We'll tolerate that for now and come back to it in the side quests. (The `target` parameter has no type hint because it can be anything monster-like. You'll fix that in a side quest too.)

## Part 3: The combat loop

Now the main event. Two design decisions will make this loop easy to test.

**First, it returns what happened instead of printing it.** A fight produces a list of **events**, one per attack. Narration can be added later as a separate layer, the same separation you used with exceptions in Unit 8. Your tests can check the events directly, and because they're dataclasses, you get equality checking for free, as you saw in Unit 4.

**Second, it takes its dice as a parameter.** You already know why.

### Write the test first

Create `test_encounter.py`. The first scenario is a duel you can follow by hand: Wren against one goblin.

```python
from encounter import AttackEvent, run_encounter
from monster import Monster


def test_the_hero_wins_a_two_round_fight(hero, loaded_dice):
    goblin = Monster("Goblin", 7, 15, 4, 5, initiative_bonus=1)
    # initiative: Wren 15+2=17, Goblin 10+1=11. Then attack rolls in turn order.
    dice = loaded_dice(15, 10, 14, 9, 12)

    result = run_encounter([hero], [goblin], dice)

    assert result.winner == "heroes"
    assert result.rounds == 2
    assert result.events == [
        AttackEvent("Wren", "Goblin", 4),
        AttackEvent("Goblin", "Wren", 5),
        AttackEvent("Wren", "Goblin", 4),
    ]
    assert hero.hit_points == 5
```

Trace the dice to see why the test expects what it does:

- **Initiative:** Wren rolls 15 and the goblin rolls 10. Wren's total is 17 and the goblin's is 11, so Wren goes first.
- **Round 1:** Wren rolls 14 (+3 = 17, beats AC 15) and hits for 4, leaving the goblin at 3. The goblin rolls 9 (+4 = 13, beats AC 12) and hits for 5, leaving Wren at 5.
- **Round 2:** Wren rolls 12 (+3 = 15, ties AC 15, which hits) for 4. The goblin is defeated, so the fight ends.

```
E   ModuleNotFoundError: No module named 'encounter'
```

### A first version

Create `encounter.py`. First the two small dataclasses:

```python
from dataclasses import dataclass, field

from dice import roll_die
from initiative import roll_initiative


@dataclass
class AttackEvent:
    attacker: str
    target: str
    damage: int


@dataclass
class EncounterResult:
    winner: str | None
    rounds: int
    events: list[AttackEvent] = field(default_factory=list)
```

Then a first, deliberately plain version of the loop:

```python
def run_encounter(heroes, monsters, roller=roll_die):
    order = roll_initiative(heroes + monsters, roller)
    events = []
    round_number = 0
    while True:
        round_number += 1
        for fighter in order:
            if fighter.is_defeated:
                continue
            if any(fighter is hero for hero in heroes):
                enemies = monsters
            else:
                enemies = heroes
            target = None
            for enemy in enemies:
                if not enemy.is_defeated:
                    target = enemy
                    break
            damage = fighter.attack(target, roller)
            events.append(AttackEvent(fighter.name, target.name, damage))
            if all(monster.is_defeated for monster in monsters):
                return EncounterResult("heroes", round_number, events)
            if all(hero.is_defeated for hero in heroes):
                return EncounterResult("monsters", round_number, events)
```

Run `pytest`. Green. A few pieces are new:

- `continue` skips the rest of this loop pass and moves on, so defeated fighters don't act.
- `any(...)` is true if **at least one** item matches. `all(...)` is true if **every** item matches. Both take the generator-expression style you met in Unit 4.
- `fighter is hero` checks whether two names point to the **very same object**. We use `is` instead of `==` on purpose: two goblins with identical stats are *equal* as dataclasses, but they're not the *same goblin*. With `==`, a goblin could mistake himself for a hero's twin.
- `break` leaves the innermost loop immediately.

### Both sides, and the other ending

Add a second scenario where the goblin wins. Wren rolls badly, and the goblin goes first:

```python
def test_the_monsters_win_when_the_hero_falls(hero, loaded_dice):
    goblin = Monster("Goblin", 7, 15, 4, 5, initiative_bonus=1)
    # initiative: Wren 3+2=5, Goblin 18+1=19, so the goblin goes first.
    dice = loaded_dice(3, 18, 10, 2, 8)

    result = run_encounter([hero], [goblin], dice)

    assert result.winner == "monsters"
    assert result.rounds == 2
    assert result.events == [
        AttackEvent("Goblin", "Wren", 5),
        AttackEvent("Wren", "Goblin", 0),
        AttackEvent("Goblin", "Wren", 5),
    ]
```

It passes without changes to the code, because the loop already handled both endings. And a third scenario that matches the story, with two goblins:

```python
def test_defeated_monsters_are_skipped_and_the_next_one_is_targeted(hero, loaded_dice):
    first = Monster("Goblin A", 3, 10, 0, 1)
    second = Monster("Goblin B", 3, 10, 0, 1)
    # initiative: Wren 20+2, both goblins 1+0 (a tie, so listed order).
    dice = loaded_dice(20, 1, 1, 10, 1, 10)

    result = run_encounter([hero], [first, second], dice)

    assert result.winner == "heroes"
    assert result.events == [
        AttackEvent("Wren", "Goblin A", 4),
        AttackEvent("Goblin B", "Wren", 0),
        AttackEvent("Wren", "Goblin B", 4),
    ]
```

Wren defeats Goblin A in one blow. Goblin A's turn is skipped because it's defeated, Goblin B swings and misses (a natural 1), and then Wren targets Goblin B, the next enemy still standing. Also green.

### The fight that never ends

Now think about what could go wrong. Suppose nobody can ever hit anything. Every attack misses, and everyone survives. Our `while True` loop would run **forever**. You met this danger in Unit 3, when the corridor had no door, and the answer is the same: a limit. Write the test first, using dice that always roll a 1 (a natural 1 always misses):

```python
def test_a_fight_nobody_can_win_stops_at_the_round_limit(hero, goblin):
    def always_one(sides):
        return 1  # a natural 1 always misses

    result = run_encounter([hero], [goblin], always_one)

    assert result.winner is None
    assert result.rounds == 50
```

Run `pytest`. **Nothing happens.** The test is stuck in the infinite loop. Press `Ctrl+C` to stop it.

Give the function a `max_rounds` limit, and replace `while True` with a loop that has a built-in end:

```python
def run_encounter(heroes, monsters, roller=roll_die, max_rounds=50):
    order = roll_initiative(heroes + monsters, roller)
    events = []
    for round_number in range(1, max_rounds + 1):
        for fighter in order:
            ...
    return EncounterResult(None, max_rounds, events)
```

(The `...` is everything inside the inner loop, unchanged.) The loop now runs at most `max_rounds` times, and if nobody won, the function returns a result with `winner=None`. Run `pytest`, and it finishes instantly. Then make the test easier to read by passing a smaller limit:

```python
    result = run_encounter([hero], [goblin], always_one, max_rounds=3)

    assert result.winner is None
    assert result.rounds == 3
    assert len(result.events) == 6
```

Three rounds with two fighters means six attacks.

### Refactor: name the pieces

The loop works, but the middle of it is a tangle of searching and checking. Tests are green, so now's the time to clean up. Pull the two ideas into named helpers:

```python
def first_standing(side: list):
    """Return the first member of a side who is still on their feet."""
    for fighter in side:
        if not fighter.is_defeated:
            return fighter
    return None


def find_winner(heroes: list, monsters: list) -> str | None:
    """Return "heroes" or "monsters" once one side is wiped out, else None."""
    if all(monster.is_defeated for monster in monsters):
        return "heroes"
    if all(hero.is_defeated for hero in heroes):
        return "monsters"
    return None
```

Now `run_encounter` reads almost like the rules:

```python
def run_encounter(
    heroes: list,
    monsters: list,
    roller: Roller = roll_die,
    max_rounds: int = 50,
) -> EncounterResult:
    """Fight until one side is defeated, or until max_rounds is reached."""
    order = roll_initiative(heroes + monsters, roller)
    events = []
    for round_number in range(1, max_rounds + 1):
        for fighter in order:
            if fighter.is_defeated:
                continue
            on_hero_side = any(fighter is hero for hero in heroes)
            target = first_standing(monsters if on_hero_side else heroes)
            damage = fighter.attack(target, roller)
            events.append(AttackEvent(fighter.name, target.name, damage))
            winner = find_winner(heroes, monsters)
            if winner:
                return EncounterResult(winner, round_number, events)
    return EncounterResult(None, max_rounds, events)
```

Run `pytest`. All five fight tests still pass, with no test edits. That's a refactor done safely.

### A fight that's already over

One more edge case. What if the hero walks into a room with no monsters in it? Add the test, using empty dice to prove that **no dice are rolled**:

```python
def test_a_fight_that_is_already_over_rolls_no_dice(hero, loaded_dice):
    result = run_encounter([hero], [], loaded_dice())
    assert result == EncounterResult("heroes", rounds=0)
```

(Add `EncounterResult` to the test file's import from `encounter`.) It fails, because the function rolls initiative first and runs straight into the empty dice. Add a check at the very top of `run_encounter`:

```python
    winner = find_winner(heroes, monsters)
    if winner:
        return EncounterResult(winner, rounds=0)
```

Run everything:

```bash
python tasks.py test
```

You should see `113 passed`.

## Final code

`initiative.py`:

```python
from dice import Roller, roll_die


def roll_initiative(combatants: list, roller: Roller = roll_die) -> list:
    """Return the combatants in the order they will act.

    Everyone rolls a d20 and adds their initiative bonus, in the order they
    are listed. The highest total goes first. Ties go to the higher bonus,
    and after that to whoever was listed first.
    """
    rolled = [(roller(20) + fighter.initiative_bonus, fighter) for fighter in combatants]
    rolled.sort(key=lambda pair: (pair[0], pair[1].initiative_bonus), reverse=True)
    return [fighter for _, fighter in rolled]
```

`encounter.py`:

```python
from dataclasses import dataclass, field

from dice import Roller, roll_die
from initiative import roll_initiative


@dataclass
class AttackEvent:
    attacker: str
    target: str
    damage: int


@dataclass
class EncounterResult:
    winner: str | None
    rounds: int
    events: list[AttackEvent] = field(default_factory=list)


def first_standing(side: list):
    """Return the first member of a side who is still on their feet."""
    for fighter in side:
        if not fighter.is_defeated:
            return fighter
    return None


def find_winner(heroes: list, monsters: list) -> str | None:
    """Return "heroes" or "monsters" once one side is wiped out, else None."""
    if all(monster.is_defeated for monster in monsters):
        return "heroes"
    if all(hero.is_defeated for hero in heroes):
        return "monsters"
    return None


def run_encounter(
    heroes: list,
    monsters: list,
    roller: Roller = roll_die,
    max_rounds: int = 50,
) -> EncounterResult:
    """Fight until one side is defeated, or until max_rounds is reached."""
    winner = find_winner(heroes, monsters)
    if winner:
        return EncounterResult(winner, rounds=0)

    order = roll_initiative(heroes + monsters, roller)
    events = []
    for round_number in range(1, max_rounds + 1):
        for fighter in order:
            if fighter.is_defeated:
                continue
            on_hero_side = any(fighter is hero for hero in heroes)
            target = first_standing(monsters if on_hero_side else heroes)
            damage = fighter.attack(target, roller)
            events.append(AttackEvent(fighter.name, target.name, damage))
            winner = find_winner(heroes, monsters)
            if winner:
                return EncounterResult(winner, round_number, events)
    return EncounterResult(None, max_rounds, events)
```

The changes to `Character` (`initiative_bonus`, `attack_bonus`, `damage`, and `attack`) and to `Monster` (`initiative_bonus`) are shown in Parts 1 and 2.

## Loot (what you learned)

- `sorted()` and `.sort()` order a list, `key=` says what to sort by, and `reverse=True` flips the order
- A tuple key breaks ties: Python compares one position at a time
- Python's sort is **stable**: equal items keep their original order
- Duck typing: different classes work together if they share the attributes the code needs
- `any()` and `all()` test whole collections, and `continue` and `break` steer loops
- `is` asks "the very same object?" while `==` asks "equal values?"
- Every `while` loop needs an exit, and a `for ... in range(limit)` loop has one built in
- Return a record of what happened (events) instead of printing it, so tests can check it and narration can come later
- Write scripted fights with loaded dice by tracing the rolls on paper first
- Refactor by extracting named helpers once the tests are green

## Side quests

- **Remove the duplicates.** `take_damage` and `attack` now exist in both `Character` and `Monster`. Extract the shared logic into one place. What are your options, and which tests prove that nothing changed? (Look up inheritance, and also weigh a shared helper function against it.)
- **Annotate the duck.** The fighter parameters in `encounter.py` have no type hints. Look up `typing.Protocol` and define a `Combatant` protocol listing the attributes they all share.
- **Tell the story.** Write `narrate_event(event)` that turns an `AttackEvent` into a sentence (`"Wren hits Goblin for 4 damage."`, `"Wren misses Goblin."`) and `narrate_encounter(result)` that returns the whole fight as readable text. Table-test it.
- **A real party.** Write a scripted fight with two heroes against two monsters. What does the dice script look like, and what does it tell you about how hard fights are to trace by hand?
- **Smarter targeting.** Right now everyone attacks the first enemy still standing. Add a rule that monsters attack the hero with the **fewest** hit points. Which test changes first?
- **Check the max.** A hero with 1 hit point and a goblin that never misses ends the fight in round 1. Write a test that `rounds` equals 1 in that case.

## Next quest

The last goblin crumples to the floor. The chamber falls quiet, except for the slow rasp of breath from the great coiled shape in the center. Vios lifts its head and looks at you for the first time.

You reach for the iron rings and the chains hum under your fingers. These aren't ordinary chains. They're bound with a spell that only King Smund and Queen Goura can lift, and above you, faintly, you hear footsteps. Heavy ones. Many of them.

You're out of time to be careful, so you do the next best thing: you stop and **save your progress**. In **Unit 10**, you'll write the game's state to a file and read it back, with JSON, the file system, and tests that never leave a mess on your disk.

## Save your progress

When all tests are green, commit and tag it:

```bash
git add .
git commit -m "Add unit 9"
git tag unit-09-done
git push origin main --tags
```

Then update the README's unit table with a row for Unit 9.

---

*Co-drafted with Claude, an AI assistant made by Anthropic. Edited, revised, and improved with natural, human intelligence.*
