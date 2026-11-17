# Unit 1: The Ability Check

*Concepts: functions, integers, `/` vs `//`, type hints, doctests*

## The story so far

Vios, the giant Python, last of an ancient line of serpents that once included the Python of Delphi and Jörmungandr, lies chained in the dungeons of Castle Blackthorn. In the old stories, Vios's kind guarded oracles and circled the world, and every secret passed through their coils. King Smund and Queen Goura have told the kingdom that Vios is a monster that must be kept in chains, and every wall in the castle bears a warning about its fangs. In truth they are draining its prophecy to power their tower. Everyone else brought a sword. You came to unlock the chains instead. You are the only hero small enough to slip past the guards.

Rumor says something even older lies beneath the dungeon: coils that circle the whole foundation of the castle, tail in mouth, and no one has ever found the end of them.

You stand at the castle gate. The lock is old and clever. Picking it means making an **ability check**, and before you can roll anything, the game needs to know how good you are at things.

## The quest log

By the end of this unit, these tests will pass:

- [ ] A score of 10 gives a modifier of 0
- [ ] A score of 14 gives a modifier of +2
- [ ] A score of 9 gives a modifier of -1

(The rule: subtract 10 from the score, divide by 2, round **down**. Remember "round down"; it matters later.)

## Camp setup

If you skipped Unit 0, create a folder called `python_quest` and run `pip install pytest` inside it. All files in this unit go in that folder.

## Write the test first

Create `test_abilities.py`:

```python
from abilities import ability_modifier


def test_average_score_has_no_modifier():
    assert ability_modifier(10) == 0
```

## Try to run the test

```bash
pytest
```

```
E   ModuleNotFoundError: No module named 'abilities'
```

The game doesn't know your hero yet. Read the error, fix only that.

## Write the minimal amount of code

Create `abilities.py`:

```python
def ability_modifier(score):
    return 0
```

Run `pytest`. Green. Yes, it's cheating, and that's fine. A test that passes with a fake answer is a test that isn't asking enough questions yet. Let's ask more.

## A stronger hero

Add a second test:

```python
def test_strong_score_gives_bonus():
    assert ability_modifier(14) == 2
```

```
>       assert ability_modifier(14) == 2
E       assert 0 == 2
```

Now we need real logic. Update the function:

```python
def ability_modifier(score):
    return (score - 10) / 2
```

Run `pytest`. Both pass. But look closely: Python's `/` always returns a **float**, so we're really returning `2.0`, and `2.0 == 2` is `True` in Python. Our tests are happy, but something smells off. Hold that thought.

## The trap: a weak hero

Add the third test:

```python
def test_weak_score_gives_penalty():
    assert ability_modifier(9) == -1
```

```
>       assert ability_modifier(9) == -1
E       assert -0.5 == -1
E        +  where -0.5 = ability_modifier(9)
```

A half-point penalty makes no sense in the rules. Our first instinct might be to convert to an integer:

```python
def ability_modifier(score):
    return int((score - 10) / 2)
```

Run it:

```
E       assert 0 == -1
E        +  where 0 = ability_modifier(9)
```

Still wrong! `int()` doesn't round down. It **truncates toward zero**, so `-0.5` becomes `0`, not `-1`. This is a classic bug, and without the third test you'd have shipped it.

## Make it pass

Python has an operator for exactly this: `//`, floor division. It divides and rounds down, always, and gives back an `int`.

```python
def ability_modifier(score):
    return (score - 10) // 2
```

Run `pytest`. All three are green. The gate clicks open.

## Refactor

Add type hints and a docstring with a runnable example:

```python
def ability_modifier(score: int) -> int:
    """Return the modifier for an ability score.

    >>> ability_modifier(16)
    3
    """
    return (score - 10) // 2
```

Run the docstring as a test:

```bash
pytest --doctest-modules
```

Now try this experiment: temporarily change `//` back to `/` and run it again. The doctest fails because it expects `3` but gets `3.0`. Doctests notice float-versus-int differences that `==` hides.

Remember that type hints are not enforced when the code runs. They're notes for you and for tools like `mypy`.

## Loot (what you learned)

- The TDD cycle: test, fail, minimal code, pass, refactor
- `/` always gives a float; `//` rounds down and keeps ints
- `int()` truncates toward zero, which is *not* the same as rounding down
- Type hints document your code
- Doctests are examples that double as tests

## Side quests

- Add a test for a score of 8 (-1) and a score of 7 (-2). Does your function still pass?
- Add a test for the maximum score of 20 (+5) and the minimum of 1 (-5).
- These tests are repetitive. In Unit 5 you'll learn `parametrize`, which collapses them into a table.

## Next quest

The lock needs a roll to pick, but rolling a die is random, and random is hard to test. We'll tackle that properly in Unit 7. For now, in **Unit 2**, the narrator learns to describe what you see as the gate swings open.
