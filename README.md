# Peat-Bogs and Pythons

A test-driven text adventure that teaches Python. Every chapter is a quest: you get a failing test, write the code that fixes it, and the story moves forward.

## The story

Deep in the dungeons of Castle Morvussan, Vios, the last giant Python of an ancient line of serpents, lies in chains. King Smund and Queen Goura are draining its prophecy to power their tower. Everyone else brought a sword. You brought a test suite.

## How it works

Each unit follows the same loop:

1. **The hook:** a story beat that creates a need
2. **The quest log:** the failing tests that define the goal
3. **Green:** the minimal code to make them pass
4. **Refactor:** clean up and learn the idiom
5. **Loot:** a recap, plus optional side quests

The campaign is continuous. Each unit builds on the code from the last, so the game you write in Unit 1 is still running in the finale.

## Units

| Unit | Quest | Concepts | Status |
|------|-------|----------|--------|
| 1 | The Ability Check | Functions, ints, `//`, doctests | Done |
| 2 | The Narrator | Strings, f-strings, `join` | Done |
| 3 | The Backpack | Lists, loops | Coming soon |

Chapters live in [`units/`](units/). The game code lives in [`game/`](game/).

## Setup

You need Python 3.9 or newer and Git.

```bash
git clone https://github.com/ryanbenedetti/peat-bogs-and-pythons.git
cd peat-bogs-and-pythons
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install pytest
```

Run the tests:

```bash
cd game
pytest --doctest-modules
```

## Following along

The code is tagged at the end of every unit. If you get stuck, check out the tag for the previous unit and continue from a known-good state:

```bash
git checkout unit-02-done
```

Return to the latest with `git checkout main`.

## Credits

Inspired by [Learn Go with Tests](https://quii.gitbook.io/learn-go-with-tests) by Chris James, which pioneered learning a language by writing tests first. The units here are original writing.
