# Unit 2: The Narrator

*Concepts: strings, f-strings, format specs, `join`, `title`, conditional expressions*

## The story so far

The lock clicks and the gate of Castle Morvussan swings open. Somewhere far below, chains rattle. Vios is still down there, and King Smund and Queen Goura's guards are between you and the dungeon stairs.

You step into the courtyard. Torches flicker. But right now the game can't tell you any of that. It has no voice. In this unit you build the **narrator**: the code that turns raw game data into sentences a player can read.

## The quest log

By the end of this unit, these tests will pass:

- [ ] Dexterity 14 is narrated as `Dexterity 14 (+2)`
- [ ] Strength 8 is narrated as `Strength 8 (-1)`
- [ ] A courtyard with two exits is narrated as `You stand in the Courtyard. Exits: north, east.`
- [ ] A room with one exit says `Exit`, not `Exits`

## Before you start

Your `python_quest` folder should have `abilities.py` and `test_abilities.py` from Unit 1. Run `pytest` once to make sure they're still green. New code must never break old code, and the tests are how you know.

## Write the test first

Create `test_narrator.py`:

```python
from narrator import describe_ability


def test_describe_ability_with_bonus():
    assert describe_ability("Dexterity", 14) == "Dexterity 14 (+2)"
```

## Try to run the test

```bash
pytest
```

```
E   ModuleNotFoundError: No module named 'narrator'
```

You know the drill. Create `narrator.py` with the least code that can fix this error. Since the narrator needs to exist before it can say anything, we start by making it say exactly what the test wants:

```python
def describe_ability(name, score):
    return "Dexterity 14 (+2)"
```

Run `pytest`. Green again, and again it's a cheat. Let's catch it.

## Triangulate

Add a second test with different values:

```python
def test_describe_ability_with_penalty():
    assert describe_ability("Strength", 8) == "Strength 8 (-1)"
```

```
E       AssertionError: assert 'Dexterity 14 (+2)' == 'Strength 8 (-1)'
```

Now the function has to use its inputs. We already wrote a function that computes the modifier, so let's reuse it. We also need to join the pieces into one string. Your first instinct might be concatenation with `+`:

```python
from abilities import ability_modifier


def describe_ability(name, score):
    modifier = ability_modifier(score)
    return name + " " + score + " (" + modifier + ")"
```

```
E   TypeError: can only concatenate str (not "int") to str
```

Python won't glue numbers to text for you. You could wrap each number in `str()`, but the result is ugly and easy to get wrong. Python has a better tool: the **f-string**.

```python
from abilities import ability_modifier


def describe_ability(name, score):
    modifier = ability_modifier(score)
    return f"{name} {score} ({modifier})"
```

An f-string starts with `f` before the opening quote. Anything inside `{}` is evaluated as Python and converted to text. Run `pytest`:

```
E       AssertionError: assert 'Dexterity 14 (2)' == 'Dexterity 14 (+2)'
E         - Dexterity 14 (+2)
E         ?                +
E         + Dexterity 14 (2)
```

Close. pytest even marks the missing `+` for you. Python doesn't show a plus sign on positive numbers unless you ask. You ask with a **format spec**: put a colon after the value, then a code.

```python
    return f"{name} {score} ({modifier:+d})"
```

`:+d` means "show this integer (`d`) with its sign (`+`)". Run `pytest`. Both ability tests pass, and Unit 1's tests still pass too.

## Describing a room

Add a test for the courtyard:

```python
from narrator import describe_ability, describe_room


def test_describe_room_with_two_exits():
    assert (
        describe_room("courtyard", ["north", "east"])
        == "You stand in the Courtyard. Exits: north, east."
    )
```

(The updated import line replaces the one at the top of the file.)

```
E   ImportError: cannot import name 'describe_room' from 'narrator'
```

Two string methods will do most of the work here:

- `"courtyard".title()` gives `"Courtyard"` (capitalizes each word)
- `", ".join(["north", "east"])` gives `"north, east"` (glues a list of strings together, with the string you call it on as the separator)

```python
def describe_room(name, exits):
    exit_list = ", ".join(exits)
    return f"You stand in the {name.title()}. Exits: {exit_list}."
```

Run `pytest`. Green.

## The singular problem

A dungeon cell has only one way out. Add the test:

```python
def test_describe_room_with_one_exit():
    assert (
        describe_room("dungeon", ["down"])
        == "You stand in the Dungeon. Exit: down."
    )
```

```
E       AssertionError: assert 'You stand in the Dungeon. Exits: down.' == ...
```

We need the label to depend on how many exits there are. Python has a compact way to pick between two values, called a **conditional expression**:

```python
def describe_room(name, exits):
    exit_list = ", ".join(exits)
    label = "Exit" if len(exits) == 1 else "Exits"
    return f"You stand in the {name.title()}. {label}: {exit_list}."
```

Read it aloud: "label is `Exit` if there is one exit, otherwise `Exits`." Run `pytest`. All green.

## Refactor

Add type hints and doctests to both functions. The final `narrator.py`:

```python
from abilities import ability_modifier


def describe_ability(name: str, score: int) -> str:
    """Narrate an ability score with its modifier.

    >>> describe_ability("Wisdom", 10)
    'Wisdom 10 (+0)'
    """
    modifier = ability_modifier(score)
    return f"{name} {score} ({modifier:+d})"


def describe_room(name: str, exits: list[str]) -> str:
    """Narrate the room the hero is standing in.

    >>> describe_room("great hall", ["north"])
    'You stand in the Great Hall. Exit: north.'
    """
    exit_list = ", ".join(exits)
    label = "Exit" if len(exits) == 1 else "Exits"
    return f"You stand in the {name.title()}. {label}: {exit_list}."
```

Run everything:

```bash
pytest --doctest-modules
```

Notice that doctests display strings **with quotes** (`'Wisdom 10 (+0)'`). That's how Python shows you that the value is a string and not a number. Also notice that a score of 10 gives `+0`, which is correct per our format spec.

## Loot (what you learned)

- f-strings: `f"{value}"` evaluates code and builds text
- Format specs: `{n:+d}` controls how a value is displayed
- `str.title()` and `str.join()` for cleaning up and combining text
- Conditional expressions: `a if condition else b`
- Triangulation: use a second test to force a fake implementation to become real
- Regression: old tests keep guarding old code while you build new code

## Side quests

- **No way out.** Add a test for a room with an empty exits list. The narration should be `You stand in the Cellar. There is no way out.` What does your function do now?
- **The apostrophe trap.** Try `describe_room("witch's hut", ["south"])`. `.title()` produces `Witch'S Hut`. Write a failing test for the correct result, then look up `string.capwords` to fix it.
- **A scrambled inscription.** Over the castle gate, an inscription reads as nonsense. Write `is_anagram("listen", "silent")`, which returns `True` when two strings use exactly the same letters. Hints: `sorted()`, `.lower()`, and `.replace(" ", "")`. Keep this function. The names carved around Morvussan are hiding a secret.

## Next quest

You can describe the world, but you can't carry anything out of it. In **Unit 3**, you open your backpack and learn lists and loops. Rumor has it there's a corridor beneath the castle that never seems to end...

---

*Co-written with Claude, an AI assistant made by Anthropic.*
