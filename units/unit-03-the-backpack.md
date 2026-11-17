# Unit 3: The Backpack

*Concepts: lists, `append`, `in`, truthiness, `for` loops, `while` loops, `%`, `None`, default arguments*

## The story so far

You slip past the courtyard guards and into the castle's storeroom. Shelves of dusty supplies line the walls: rope, torches, a rusty key. You can't take it all, and you need a way to keep track of what you carry.

Beyond the storeroom, a stairway spirals down toward Vios. But rumor says the corridor at the bottom has no end. People who walked in with a torch never came back out. Some say the walls are not stone at all, but the coils of something enormous that has been biting its own tail since before the castle was built.

You'll need a backpack, and a plan for the corridor.

## The quest log

By the end of this unit, these tests will pass:

- [ ] An empty backpack is narrated as `Your backpack is empty.`
- [ ] A backpack with items is narrated as `You carry: rope, torch.`
- [ ] Adding an item puts it in the backpack
- [ ] You can ask whether the backpack contains an item
- [ ] You can add up the weight of everything you carry
- [ ] Walking the corridor finds the door, wraps around the ends, and gives up if there's no door

## Before you start

Run `pytest --doctest-modules` in the `game/` folder. Everything from Units 1 and 2 should be green. All the new files in this unit go in `game/` too.

## Part 1: The backpack

### Write the test first

Create `test_backpack.py`:

```python
from backpack import describe_backpack


def test_empty_backpack_is_narrated():
    assert describe_backpack([]) == "Your backpack is empty."
```

A **list** is an ordered collection written with square brackets. `[]` is an empty one.

```bash
pytest
```

```
E   ModuleNotFoundError: No module named 'backpack'
```

Create `backpack.py` with the least code that passes:

```python
def describe_backpack(items):
    return "Your backpack is empty."
```

Green. Now the second test, which will force the real logic:

```python
from backpack import describe_backpack


def test_empty_backpack_is_narrated():
    assert describe_backpack([]) == "Your backpack is empty."


def test_backpack_with_items_is_narrated():
    assert describe_backpack(["rope", "torch"]) == "You carry: rope, torch."
```

```
E       AssertionError: assert 'Your backpack is empty.' == 'You carry: rope, torch.'
```

You met `", ".join(...)` in Unit 2. Now we need to choose between two sentences:

```python
def describe_backpack(items):
    if not items:
        return "Your backpack is empty."
    item_list = ", ".join(items)
    return f"You carry: {item_list}."
```

`if not items` works because Python treats an **empty list as false** and any non-empty list as true. This idiom is called *truthiness*, and you'll see it everywhere in Python code. Run `pytest`. Green.

### Filling the pack

Add a test that checks the list itself:

```python
from backpack import add_item, describe_backpack


def test_add_item_puts_it_in_the_pack():
    backpack = []
    add_item(backpack, "rope")
    assert backpack == ["rope"]
```

(Update the import line at the top of the file, and keep the other tests.)

```
E   ImportError: cannot import name 'add_item' from 'backpack'
```

```python
def add_item(backpack, item):
    backpack.append(item)
```

Notice what this function does *not* do: it doesn't return anything. It **changes the list you pass in**. That's called mutation, and it's why the test checks `backpack` afterward instead of checking a return value. Keep this in mind. Some functions return new values, and some change what you hand them. Knowing which kind you're writing prevents a lot of bugs.

### Is it in the pack?

```python
from backpack import add_item, describe_backpack, has_item


def test_has_item_finds_what_is_inside():
    assert has_item(["rope", "torch"], "rope")


def test_has_item_misses_what_is_not_inside():
    assert not has_item(["rope", "torch"], "key")
```

```python
def has_item(backpack, item):
    return item in backpack
```

The `in` operator asks "is this value somewhere in the list?" and gives back `True` or `False`.

### Counting the weight with a loop

Each item has a weight. For now, the weights are just a list of numbers. (Hold that thought. It's going to feel awkward soon.)

```python
from backpack import add_item, describe_backpack, has_item, total_weight


def test_total_weight_adds_everything_up():
    assert total_weight([2, 5, 1]) == 8


def test_total_weight_of_empty_pack_is_zero():
    assert total_weight([]) == 0
```

```
E   ImportError: cannot import name 'total_weight' from 'backpack'
```

A `for` loop visits every item in a list, one at a time:

```python
def total_weight(weights):
    total = 0
    for weight in weights:
        total += weight
    return total
```

`total += weight` is shorthand for `total = total + weight`. Run `pytest`. Green, including the empty pack, because the loop simply never runs and `total` stays `0`.

### Refactor

Python already knows how to add up a list. Replace the loop with the built-in:

```python
def total_weight(weights):
    return sum(weights)
```

Run `pytest`. Still green. This is the quiet superpower of tests: you wrote the loop to learn how loops work, then swapped the whole implementation for a better one, and the tests told you nothing broke.

## Part 2: The endless corridor

The corridor is a circle of rooms. Some are plain stone. One might have a door. You start somewhere and walk forward one room at a time. When you reach the last room, the corridor loops you back to the first.

We need a function that counts how many steps it takes to reach a door.

### Write the test first

Create `test_corridor.py`:

```python
from corridor import steps_to_exit


def test_walks_forward_to_the_door():
    assert steps_to_exit(["stone", "stone", "door"], start=0) == 2
```

Start in room 0, step to room 1, step to room 2, and there's the door: 2 steps.

```
E   ModuleNotFoundError: No module named 'corridor'
```

Create `corridor.py`:

```python
def steps_to_exit(corridor, start):
    position = start
    steps = 0
    while corridor[position] != "door":
        position += 1
        steps += 1
    return steps
```

A `while` loop repeats **as long as its condition is true**. Here: keep walking while the current room is not a door. Run `pytest`. Green.

### Wrapping around

Add a test where the door is *behind* you:

```python
def test_wraps_around_the_end_of_the_corridor():
    assert steps_to_exit(["door", "stone", "stone"], start=2) == 1
```

From room 2, one step forward loops back to room 0, where the door is.

```
E   IndexError: list index out of range
```

We walked off the end of the list. The fix is the **modulo operator** `%`, which gives the remainder after division. `3 % 3` is `0`, `4 % 3` is `1`, so `% len(corridor)` wraps any position back into range:

```python
def steps_to_exit(corridor, start):
    position = start
    steps = 0
    while corridor[position] != "door":
        position = (position + 1) % len(corridor)
        steps += 1
    return steps
```

Run `pytest`. Both green.

### The corridor that never ends

Now the dangerous test. What if there is no door at all?

```python
def test_a_corridor_with_no_door_never_ends():
    assert steps_to_exit(["stone", "stone", "stone"]) is None
```

(For now this will also fail because `start` is required. Give it a default in your function signature: `def steps_to_exit(corridor, start=0):`, then run the tests.)

```bash
pytest
```

**Nothing happens.** The terminal just sits there. Our `while` loop is waiting for a door that doesn't exist, so it will walk the coils forever. This is an **infinite loop**. Press `Ctrl+C` to escape:

```
!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!
```

You've just met the corridor. The way out is to give the loop a **limit**: a number of steps after which we give up. A function can have **default arguments**, values used when the caller doesn't provide one:

```python
def steps_to_exit(corridor, start=0, limit=100):
    position = start
    steps = 0
    while steps <= limit:
        if corridor[position] == "door":
            return steps
        position = (position + 1) % len(corridor)
        steps += 1
    return None
```

Three things changed:

- The loop condition is now `steps <= limit`, so it ends no matter what.
- The door check moved inside the loop, where it can `return` early.
- If the loop finishes without finding a door, we return `None`, Python's value for "nothing here."

Always check for `None` with `is None`, not `== None`. Run `pytest`. All green, and fast.

### Testing the limit itself

```python
def test_limit_gives_up_early():
    corridor = ["stone", "stone", "door"]
    assert steps_to_exit(corridor, limit=1) is None
    assert steps_to_exit(corridor, limit=2) == 2
```

The door is 2 steps away, so a limit of 1 isn't enough but a limit of 2 is. This test pins down the edge, which is where loop bugs love to hide.

## Refactor

Add type hints and a docstring to `corridor.py`. Because the function may return an `int` or `None`, the return type is written `int | None`, read as "an int or None":

```python
def steps_to_exit(
    corridor: list[str], start: int = 0, limit: int = 100
) -> int | None:
    """Count the steps to reach a door, or return None if there isn't one.

    The corridor wraps around, so walking past the last room brings
    you back to the first.

    >>> steps_to_exit(["stone", "stone", "door"])
    2
    """
    position = start
    steps = 0
    while steps <= limit:
        if corridor[position] == "door":
            return steps
        position = (position + 1) % len(corridor)
        steps += 1
    return None
```

Add type hints and doctests to `backpack.py` too. The final version:

```python
def describe_backpack(items: list[str]) -> str:
    """Narrate what the hero is carrying.

    >>> describe_backpack(["rope", "torch"])
    'You carry: rope, torch.'
    """
    if not items:
        return "Your backpack is empty."
    item_list = ", ".join(items)
    return f"You carry: {item_list}."


def add_item(backpack: list[str], item: str) -> None:
    """Put an item in the backpack (changes the list in place)."""
    backpack.append(item)


def has_item(backpack: list[str], item: str) -> bool:
    """Return True if the item is in the backpack.

    >>> has_item(["rope", "torch"], "rope")
    True
    """
    return item in backpack


def total_weight(weights: list[int]) -> int:
    """Return the combined weight of everything carried.

    >>> total_weight([2, 5, 1])
    8
    """
    return sum(weights)
```

Run everything:

```bash
cd game
pytest --doctest-modules
```

You should see `15 passed`.

## Loot (what you learned)

- Lists: `[]`, `append`, `in`, `len`
- Truthiness: `if not items` checks for an empty list
- Mutation: some functions change their arguments instead of returning something
- `for` loops visit every item; `while` loops repeat until a condition fails
- Every `while` loop needs a way to end, or a limit
- `%` wraps numbers around a range
- `None` means "nothing found," and you check it with `is None`
- Default arguments make a function flexible without breaking existing callers
- Tests let you replace a hand-written loop with a built-in and know nothing broke

## Side quests

- **A heavy load.** The backpack can only hold 5 items. Make `add_item` return `False` when the pack is full and `True` when the item was added. Write the failing test first.
- **A numbered list.** Narrate the backpack as `1. rope`, `2. torch`. Look up `enumerate`.
- **A shorter corridor loop.** Rewrite `steps_to_exit` using a `for` loop over `range(limit + 1)` instead of a `while`. Do the tests still pass? Which version reads better to you?
- **Stuck forever.** Try deleting `limit` from the `while` condition and running the no-door test again. Then install `pytest-timeout` (`pip install pytest-timeout`) and run `pytest --timeout=2`. Now the test fails after two seconds instead of hanging.

## Next quest

The corridor ends at a heavy door, and behind it, a prison cell. But as you pick up the rope and the key, you notice something awkward. The item names live in one list, their weights in another, and keeping them lined up is going to cause trouble. Every item needs a name, a weight, and maybe more, all together in one place.

In **Unit 4**, you meet dictionaries and dataclasses, and build the character sheet.

## Save your progress

When your tests are green, commit and tag it:

```bash
git add .
git commit -m "Add unit 3"
git tag unit-03-done
git push --tags origin main
```
