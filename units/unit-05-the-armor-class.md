# Unit 5: The Armor Class

*Concepts: table-driven tests with `pytest.mark.parametrize`, test IDs, stacked parametrize, running a subset of tests with `-k`*

## The story so far

You march down the spiral stairs with your forged papers in hand. Halfway down, a guard captain steps out of an alcove and blocks the way. His name plate reads **Captain Hale**.

He reads your papers slowly, grunts, and pulls a thick book from his belt: the **Garrison Manual** of Castle Morvussan. "Papers are fine," he says. "But every new recruit gets sparred before they get a post. Let's see how hard you are to hit."

He flips to a page full of tables. Armor class by dexterity. Hit chances by roll. The whole guard runs on rules like these, and rules like these are a gift to a tester: they're already written as tables. Your tests should be too.

## The quest log

By the end of this unit, these tests will pass:

- [ ] The Unit 1 tests collapse into a single table of ability scores and modifiers
- [ ] Armor class is 10 + the Dexterity modifier + any armor bonus
- [ ] Armor never makes a character easier to hit
- [ ] An attack hits when the roll plus the attack bonus reaches the target's armor class, except that a natural 20 always hits and a natural 1 always misses

## Before you start

Run `python tasks.py test`. You should see `38 passed`. All new files go in `game/`.

## Part 1: A table instead of a pile of tests

Open `test_abilities.py`. Back in Unit 1 you wrote three tests that look like this:

```python
def test_average_score_has_no_modifier():
    assert ability_modifier(10) == 0


def test_strong_score_gives_bonus():
    assert ability_modifier(14) == 2


def test_weak_score_gives_penalty():
    assert ability_modifier(9) == -1
```

Each one has the same shape: pass a number in, check a number out. Unit 1's side quests asked for more cases (8, 7, 20, 1), and every new case would be another near-identical function. The *interesting* part of each test is the data, and the function body is just noise around it.

Your first instinct might be a loop inside a single test:

```python
def test_modifiers():
    for score, expected in [(10, 0), (14, 2), (9, -1)]:
        assert ability_modifier(score) == expected
```

It works until something fails. The loop stops at the first bad row, so you can't see the rest, and the failure report doesn't say which row broke unless you add extra code. Pytest has a built-in tool for this problem.

### Rewrite it with `parametrize`

Replace the contents of `test_abilities.py`:

```python
import pytest

from abilities import ability_modifier


@pytest.mark.parametrize(
    "score, expected",
    [
        (1, -5),
        (8, -1),
        (9, -1),
        (10, 0),
        (11, 0),
        (12, 1),
        (14, 2),
        (20, 5),
    ],
)
def test_ability_modifier(score, expected):
    assert ability_modifier(score) == expected
```

Here's how it reads:

- `"score, expected"` names the arguments the test function receives.
- The list holds one tuple per row of the table.
- Pytest runs the test function **once per row**, as a separate test.

Run `pytest`. The count rises from 38 to 43, since three tests became eight.

### Give the rows names

Run `pytest -v` and look at the test names:

```
game/test_abilities.py::test_ability_modifier[1--5] PASSED
game/test_abilities.py::test_ability_modifier[9--1] PASSED
```

Those IDs are made of the raw values, so `1--5` means "score 1, expected -5". It's technically accurate and it's hard to read. Give each row a readable ID with `pytest.param`:

```python
@pytest.mark.parametrize(
    "score, expected",
    [
        pytest.param(1, -5, id="lowest-score"),
        pytest.param(8, -1, id="weak"),
        pytest.param(9, -1, id="odd-score-rounds-down"),
        pytest.param(10, 0, id="average"),
        pytest.param(11, 0, id="odd-score-above-average"),
        pytest.param(12, 1, id="a-little-strong"),
        pytest.param(14, 2, id="strong"),
        pytest.param(20, 5, id="highest-score"),
    ],
)
def test_ability_modifier(score, expected):
    assert ability_modifier(score) == expected
```

Use hyphens instead of spaces, because IDs end up on the command line. The row `9 → -1` now carries the lesson from Unit 1 in its name.

### Watch a table catch a bug

Remember the `int()` trap from Unit 1? Temporarily reintroduce it in `abilities.py`:

```python
    return int((score - 10) / 2)
```

Run `pytest`:

```
FAILED game/test_abilities.py::test_ability_modifier[lowest-score] - assert -...
FAILED game/test_abilities.py::test_ability_modifier[odd-score-rounds-down]
2 failed, 6 passed
```

Two rows failed, six passed, and the IDs tell you exactly which rules broke. That report tells a story that a loop never could. Now put the correct line back:

```python
    return (score - 10) // 2
```

## Part 2: Armor class

Captain Hale's manual says: **armor class = 10 + Dexterity modifier + armor bonus.** The higher the number, the harder you are to hit.

This rule is a table. Start with the table.

Create `test_combat.py`:

```python
import pytest

from combat import armor_class


@pytest.mark.parametrize(
    "dexterity, armor_bonus, expected",
    [
        pytest.param(10, 0, 10, id="average-and-unarmored"),
        pytest.param(14, 0, 12, id="nimble"),
        pytest.param(8, 0, 9, id="clumsy"),
        pytest.param(14, 3, 15, id="nimble-in-armor"),
        pytest.param(20, 5, 20, id="best-case"),
    ],
)
def test_armor_class(dexterity, armor_bonus, expected):
    assert armor_class(dexterity, armor_bonus) == expected
```

```
E   ModuleNotFoundError: No module named 'combat'
```

Create `combat.py` with the smallest thing that passes *one* row:

```python
def armor_class(dexterity, armor_bonus):
    return 10
```

Run `pytest`:

```
FAILED game/test_combat.py::test_armor_class[nimble] - assert 10 == 12
FAILED game/test_combat.py::test_armor_class[clumsy] - assert 10 == 9
FAILED game/test_combat.py::test_armor_class[nimble-in-armor] - assert 10 == 15
FAILED game/test_combat.py::test_armor_class[best-case] - assert 10 == 20
4 failed, 1 passed
```

One row is green and four are red, and the report shows how far you are from done. Now reuse your Unit 1 function:

```python
from abilities import ability_modifier


def armor_class(dexterity, armor_bonus):
    return 10 + ability_modifier(dexterity)
```

Now `nimble` and `clumsy` turn green, and the two armored rows are still red. Add the armor:

```python
def armor_class(dexterity, armor_bonus):
    return 10 + ability_modifier(dexterity) + armor_bonus
```

All five rows pass.

### Stacking tables

Some rules aren't about one specific answer. They're about **everything**. Here's one: *armor never makes you easier to hit.* Add this to `test_combat.py`:

```python
@pytest.mark.parametrize("armor_bonus", [0, 2, 5])
@pytest.mark.parametrize("dexterity", [8, 14])
def test_armor_never_makes_you_easier_to_hit(dexterity, armor_bonus):
    assert armor_class(dexterity, armor_bonus) >= armor_class(dexterity)
```

Two things happen here. First, the test calls `armor_class(dexterity)` with just one argument, so run it:

```
E   TypeError: armor_class() missing 1 required positional argument: 'armor_bonus'
```

Give `armor_bonus` a default, as you did with `limit` in Unit 3:

```python
def armor_class(dexterity, armor_bonus=0):
    return 10 + ability_modifier(dexterity) + armor_bonus
```

Second, notice that the test has **two** `parametrize` decorators. Stacking them gives you **every combination**: 2 dexterity values times 3 armor bonuses is 6 tests (`[8-0]`, `[8-2]`, `[8-5]`, `[14-0]`, `[14-2]`, `[14-5]`). When a rule should hold for all inputs, stacking lets you cover a grid with almost no code.

## Part 3: Does the attack hit?

Captain Hale's second table is the hit rule. An attacker rolls a d20 (a twenty-sided die). Add the attacker's bonus. If the total reaches the target's armor class, it's a hit. Ties go to the attacker.

There are two exceptions you'll discover as we go. Add this to `test_combat.py`, starting with just three rows:

```python
from combat import armor_class, attack_hits


@pytest.mark.parametrize(
    "roll, attack_bonus, target, expected",
    [
        pytest.param(10, 2, 12, True, id="tie-hits"),
        pytest.param(10, 1, 12, False, id="one-short-misses"),
        pytest.param(15, 0, 12, True, id="high-roll-hits"),
    ],
)
def test_attack_hits(roll, attack_bonus, target, expected):
    assert attack_hits(roll, attack_bonus, target) == expected
```

(Update the import line at the top of the file, and keep the other tests.) Then add the function to `combat.py`:

```python
def attack_hits(roll, attack_bonus, target_ac):
    return roll + attack_bonus >= target_ac
```

Green. Now the captain flips the page. "One more thing," he says. "A natural twenty always hits, no matter the armor." Add a row:

```python
        pytest.param(20, -5, 30, True, id="natural-20-always-hits"),
```

```
FAILED game/test_combat.py::test_attack_hits[natural-20-always-hits]
```

The total is 20 - 5 = 15, far below 30, so the plain rule says miss. Fix it:

```python
def attack_hits(roll, attack_bonus, target_ac):
    if roll == 20:
        return True
    return roll + attack_bonus >= target_ac
```

"And a natural one *always* misses." One more row:

```python
        pytest.param(1, 10, 5, False, id="natural-1-always-misses"),
```

```
FAILED game/test_combat.py::test_attack_hits[natural-1-always-misses]
```

A roll of 1 plus 10 is 11, which beats armor class 5, so the plain rule says hit. Add the rule:

```python
def attack_hits(roll, attack_bonus, target_ac):
    if roll == 1:
        return False
    if roll == 20:
        return True
    return roll + attack_bonus >= target_ac
```

All green. Notice what the table did for you: every new rule from the captain became **one new line of data**, and the table is now an executable copy of the rulebook. When the rules change, you change a row.

### Run just part of the suite

As the suite grows, you'll want to run a slice. The `-k` option runs only the tests whose names contain a word:

```bash
pytest -k natural
```

```
2 passed, 59 deselected
```

That's why readable IDs matter: they double as search terms.

## Refactor

Add type hints and doctests. The final `combat.py`:

```python
from abilities import ability_modifier


def armor_class(dexterity: int, armor_bonus: int = 0) -> int:
    """Return how hard a character is to hit.

    >>> armor_class(14, armor_bonus=3)
    15
    """
    return 10 + ability_modifier(dexterity) + armor_bonus


def attack_hits(roll: int, attack_bonus: int, target_ac: int) -> bool:
    """Return True if an attack roll beats the target's armor class.

    A natural 20 always hits and a natural 1 always misses.

    >>> attack_hits(roll=12, attack_bonus=2, target_ac=14)
    True
    """
    if roll == 1:
        return False
    if roll == 20:
        return True
    return roll + attack_bonus >= target_ac
```

Run everything:

```bash
python tasks.py test
```

You should see `61 passed`.

## Loot (what you learned)

- `@pytest.mark.parametrize` runs one test function against many rows of data
- `pytest.param(..., id="...")` gives each row a readable name
- A loop inside a test hides failures, while a parametrized table reports every row separately
- Stacked `parametrize` decorators test every combination
- Adding a rule to a table is one line, and the table doubles as documentation
- `pytest -k word` runs just the tests whose names match
- Edge cases (ties, natural 1 and 20) deserve their own named rows

## Side quests

- **Parametrize the narrator.** Rewrite the room and ability tests from Unit 2 as tables. Which rows would you add?
- **Every score at once.** Write a test that checks `ability_modifier` returns a value between -5 and 5 for every score from 1 to 20. Hint: `@pytest.mark.parametrize("score", range(1, 21))`.
- **Shields.** Add a `shield_bonus` parameter to `armor_class` that defaults to 0. Add table rows first.
- **Advantage.** Write `roll_with_advantage(first, second)`, which returns the higher of two rolls. Add a `roll_with_disadvantage` that returns the lower. Table-test both.
- **Armor on the sheet.** Add an `armor_bonus` field to the `Character` dataclass from Unit 4, then write a function that computes a character's armor class from their sheet.

## Next quest

Captain Hale snaps the manual shut. "You'll do. Go on down." You start to breathe again. Then something snarls in the dark below, and the captain's face changes. These aren't the castle's guards. Goblins have been let loose in the lower levels, and they don't care about papers.

To fight them you'll need more than functions. You'll need things that have **state** (hit points that go down) and **behavior** (attacks that land). In **Unit 6**, you meet classes and build your first monster.

## Save your progress

When all tests are green, commit and tag it:

```bash
git add .
git commit -m "Add unit 5"
git tag unit-05-done
git push origin main --tags
```

Then update the README's unit table with a row for Unit 5.

---

*Co-drafted with Claude, an AI assistant made by Anthropic. Edited, revised, and improved with natural, human intelligence.*
