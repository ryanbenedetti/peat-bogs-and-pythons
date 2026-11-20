# Unit 4: The Character Sheet

*Concepts: dictionaries, `.items()`, comprehensions, dataclasses, `default_factory`*

## The story so far

At the end of the endless corridor, you find a heavy door. This time it opens.

Beyond it is the guardroom. A fire smolders in the grate. On the gaoler's desk sits a ledger, and next to it a stack of blank forms headed **Papers of Service**. A note pinned above them reads: *"New recruits arrive today. Check every set of papers. No papers, no passage."*

You see your chance. If you fill out a set of papers, the guards on the stairs below might take you for a new recruit and let you walk straight down to Vios.

But the papers want a name, a list of abilities, and an inventory of everything you carry. And as you stare at your backpack's contents, the problem from last time gets worse. The rope's name is in one list and its weight is in another, and if you ever sort one list without the other, the rope will weigh as much as the torch. Every item needs its name and weight **together**, in one place.

## The quest log

By the end of this unit, these tests will pass:

- [ ] An item remembers its name and weight together
- [ ] You can add up the weight of a list of items
- [ ] You can list the names of a list of items
- [ ] A set of abilities is narrated one per line
- [ ] A character holds a name, abilities, and a backpack, and no two characters share a backpack
- [ ] A character's papers narrate as a full sheet

## Before you start

Run `python tasks.py test` (or `pytest --doctest-modules` in `game/`). You should see `25 passed`. All new files go in `game/`.

## Part 1: Items as dictionaries

A **dictionary** stores values under names, written as `key: value` pairs inside curly braces:

```python
{"name": "rope", "weight": 3}
```

You look things up by key: `item["weight"]` gives `3`. Where a list asks "what's at position 2?", a dictionary asks "what's stored under this name?"

### Write the test first

Create `test_items.py`:

```python
from items import make_item


def test_make_item_records_name_and_weight():
    assert make_item("rope", 3) == {"name": "rope", "weight": 3}
```

```bash
pytest
```

```
E   ModuleNotFoundError: No module named 'items'
```

Create `items.py`:

```python
def make_item(name, weight):
    return {"name": name, "weight": weight}
```

Green. Now the more interesting tests. Replace `test_items.py` with:

```python
from items import carried_weight, item_names, make_item

ROPE = make_item("rope", 3)
TORCH = make_item("torch", 1)
KEY = make_item("key", 1)


def test_make_item_records_name_and_weight():
    assert ROPE == {"name": "rope", "weight": 3}


def test_carried_weight_adds_up_items():
    assert carried_weight([ROPE, TORCH, KEY]) == 5


def test_carried_weight_of_nothing_is_zero():
    assert carried_weight([]) == 0


def test_item_names_lists_every_name():
    assert item_names([ROPE, TORCH, KEY]) == ["rope", "torch", "key"]
```

```
E   ImportError: cannot import name 'carried_weight' from 'items'
```

Add the functions to `items.py`. You wrote this kind of loop in Unit 3:

```python
def carried_weight(items):
    total = 0
    for item in items:
        total += item["weight"]
    return total


def item_names(items):
    names = []
    for item in items:
        names.append(item["name"])
    return names
```

All green. Now refactor. Python has compact forms for exactly this pattern:

```python
def carried_weight(items):
    return sum(item["weight"] for item in items)


def item_names(items):
    return [item["name"] for item in items]
```

The second one is a **list comprehension**: "a list of each item's name, for each item in items." The first uses the same idea inside `sum()` and is called a **generator expression**. Run `pytest` again. Still green, so the swap was safe.

### The trap

Dictionaries have a weakness. Change one key in `carried_weight` to a typo, just to see:

```python
    return sum(item["wieght"] for item in items)
```

```
E       KeyError: 'wieght'
```

The error is clear, but it appears **only when that line runs**. Nothing warned you while you typed it, your editor can't autocomplete it, and in a bigger game, a typo in a rarely used code path could stay hidden for weeks. Fix the typo and let's keep that thought.

## Part 2: Abilities as a dictionary

Abilities are a natural fit for a dictionary: each score belongs to a name. Add this test to `test_narrator.py`:

```python
from narrator import describe_ability, describe_abilities, describe_room


def test_describe_abilities_puts_one_per_line():
    abilities = {"Strength": 8, "Dexterity": 14}
    assert describe_abilities(abilities) == "Strength 8 (-1)\nDexterity 14 (+2)"
```

(Update the import line, and keep the other tests.)

`\n` is the newline character, so this means two lines of text.

```
E   ImportError: cannot import name 'describe_abilities' from 'narrator'
```

Looping over a dictionary with `.items()` hands you each key and value as a pair, which you can unpack into two names. Add this to `narrator.py`:

```python
def describe_abilities(abilities):
    lines = []
    for name, score in abilities.items():
        lines.append(describe_ability(name, score))
    return "\n".join(lines)
```

Green. You're reusing `describe_ability` from Unit 2, which is the payoff of building in small, tested pieces. Dictionaries remember the order you inserted things, so the lines come out as `Strength`, then `Dexterity`.

Refactor it the same way as before:

```python
def describe_abilities(abilities: dict[str, int]) -> str:
    """Narrate every ability score, one per line.

    >>> print(describe_abilities({"Strength": 8, "Dexterity": 14}))
    Strength 8 (-1)
    Dexterity 14 (+2)
    """
    return "\n".join(
        describe_ability(name, score) for name, score in abilities.items()
    )
```

The doctest uses `print` so the newline shows up as a real line break.

## Part 3: Dataclasses

Back to the typo problem. What we want is a record with **named, checked fields**: something where `item.wieght` fails instantly, where a field can't be forgotten, and where printing it looks sensible. Python's **dataclass** gives you exactly that.

### Change the tests first

Edit `test_items.py` so it uses the new design before we write it:

```python
from items import Item, carried_weight, item_names

ROPE = Item("rope", 3)
TORCH = Item("torch", 1)
KEY = Item("key", 1)


def test_item_records_name_and_weight():
    assert ROPE.name == "rope"
    assert ROPE.weight == 3


def test_items_with_the_same_fields_are_equal():
    assert Item("rope", 3) == ROPE


def test_carried_weight_adds_up_items():
    assert carried_weight([ROPE, TORCH, KEY]) == 5


def test_carried_weight_of_nothing_is_zero():
    assert carried_weight([]) == 0


def test_item_names_lists_every_name():
    assert item_names([ROPE, TORCH, KEY]) == ["rope", "torch", "key"]
```

```
E   ImportError: cannot import name 'Item' from 'items'
```

Changing the tests first is a real technique: when a design changes, the tests describe the *new* design, then fail until the code catches up. Add the dataclass to `items.py`:

```python
from dataclasses import dataclass


@dataclass
class Item:
    name: str
    weight: int
```

Run `pytest`. The `Item` tests pass, but the others fail:

```
E       TypeError: 'Item' object is not subscriptable
```

Items are no longer dictionaries, so `item["weight"]` doesn't work. Dataclass fields are reached with a dot. Update the functions:

```python
def carried_weight(items):
    return sum(item.weight for item in items)


def item_names(items):
    return [item.name for item in items]
```

Delete `make_item`, since nothing uses it anymore. Run `pytest`: green.

What did `@dataclass` do? From just the field names and types, it wrote several things for you:

- An `__init__`, so `Item("rope", 3)` works
- Equality, so two items with the same fields are equal (that's what `test_items_with_the_same_fields_are_equal` checks)
- A readable display: `Item(name='rope', weight=3)`, which makes pytest failure messages much clearer

And typos now fail immediately and loudly: `item.wieght` raises `AttributeError: 'Item' object has no attribute 'wieght'`.

## Part 4: The character

Now the papers themselves. Create `test_character.py`:

```python
from character import Character, describe_sheet
from items import Item


def test_new_character_starts_with_an_empty_backpack():
    assert Character("Wren").backpack == []


def test_characters_do_not_share_backpacks():
    first = Character("Wren")
    second = Character("Corin")
    first.backpack.append(Item("rope", 3))
    assert second.backpack == []


def test_describe_sheet_lists_name_and_abilities():
    wren = Character("Wren", {"Strength": 8, "Dexterity": 14})
    assert describe_sheet(wren) == "Wren\nStrength 8 (-1)\nDexterity 14 (+2)"
```

```
E   ModuleNotFoundError: No module named 'character'
```

Create `character.py`. Your first instinct might be to give the fields default values:

```python
from dataclasses import dataclass

from items import Item


@dataclass
class Character:
    name: str
    abilities: dict[str, int] = {}
    backpack: list[Item] = []
```

```
E   ValueError: mutable default <class 'dict'> for field abilities is not allowed: use default_factory
```

Python refuses, and for good reason. A default like `[]` is created **once** and would be shared by every character, so Wren's rope would turn up in Corin's backpack. That's one of Python's classic bugs, and dataclasses catch it for you. The fix is `default_factory`, a function that builds a **fresh** list or dictionary each time:

```python
from dataclasses import dataclass, field

from items import Item


@dataclass
class Character:
    name: str
    abilities: dict[str, int] = field(default_factory=dict)
    backpack: list[Item] = field(default_factory=list)
```

Run `pytest`. The two backpack tests are green. Notice that `test_characters_do_not_share_backpacks` passed the moment the code was right. Tests that guard against a bug you might have written are worth keeping even if they never fail.

Now the sheet:

```python
from narrator import describe_abilities


def describe_sheet(character: Character) -> str:
    """Narrate a character's name and abilities.

    >>> print(describe_sheet(Character("Wren", {"Strength": 8})))
    Wren
    Strength 8 (-1)
    """
    return f"{character.name}\n{describe_abilities(character.abilities)}"
```

(Put the new import at the top of the file with the others.)

Run everything:

```bash
python tasks.py test
```

You should see `38 passed`. You've forged the papers.

## Final code

`items.py`:

```python
from dataclasses import dataclass


@dataclass
class Item:
    name: str
    weight: int


def carried_weight(items: list[Item]) -> int:
    """Return the combined weight of a list of items.

    >>> carried_weight([Item("rope", 3), Item("torch", 1)])
    4
    """
    return sum(item.weight for item in items)


def item_names(items: list[Item]) -> list[str]:
    """Return just the names of a list of items.

    >>> item_names([Item("rope", 3), Item("torch", 1)])
    ['rope', 'torch']
    """
    return [item.name for item in items]
```

`character.py`:

```python
from dataclasses import dataclass, field

from items import Item
from narrator import describe_abilities


@dataclass
class Character:
    name: str
    abilities: dict[str, int] = field(default_factory=dict)
    backpack: list[Item] = field(default_factory=list)


def describe_sheet(character: Character) -> str:
    """Narrate a character's name and abilities.

    >>> print(describe_sheet(Character("Wren", {"Strength": 8})))
    Wren
    Strength 8 (-1)
    """
    return f"{character.name}\n{describe_abilities(character.abilities)}"
```

## Loot (what you learned)

- Dictionaries store values under keys: `d["key"]`, `.items()`, insertion order
- Comprehensions and generator expressions: compact loops that build a list or feed `sum()`
- Dictionary typos fail only at runtime, which is why records deserve better
- Dataclasses give you `__init__`, equality, and a readable display from field names and types
- Mutable defaults are shared between instances, so use `field(default_factory=...)`
- Changing the tests first is how you drive a redesign

## Side quests

- **An empty sheet.** `describe_sheet(Character("Wren"))` returns `"Wren\n"` with a trailing newline. Write a test that expects just `"Wren"`, then fix it.
- **What's in the pack.** Narrate a character's backpack by combining `item_names` from this unit with `describe_backpack` from Unit 3.
- **Retire the old function.** `total_weight` in `backpack.py` is now redundant. Delete it and its tests, and let the test suite tell you what else depends on it.
- **Carrying capacity.** Add `carry_limit(character)`, which returns the Strength score multiplied by 5. Write the test first.
- **Locked in place.** Change `@dataclass` to `@dataclass(frozen=True)` on `Item`, then try `ROPE.weight = 5` in a test. What error do you get, and why might that be useful?

## Next quest

The papers pass inspection. A guard captain in heavy armor steps out of the shadows on the stairs and begins asking questions. You'll need to know how hard you are to hit, and how hard *they* are. Rules like these fill tables, and your test file is already starting to look like a table written in the most repetitive way possible. In **Unit 5**, you meet `parametrize` and turn a wall of near-identical tests into one tidy list.

## Save your progress

When all tests are green, commit and tag it:

```bash
git add .
git commit -m "Add unit 4"
git tag unit-04-done
git push origin main --tags
```

Then update the README's unit table: change Unit 3 to **Done** if you haven't, and add a row for Unit 4.

---

*Co-drafted with Claude, an AI assistant made by Anthropic. Edited, revised, and improved with natural, human intelligence.*
