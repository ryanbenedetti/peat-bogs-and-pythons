# Peat-Bogs and Pythons

A test-driven text adventure that teaches Python. Every chapter is a quest: you get a failing test, write the code that fixes it, and the story moves forward.

## The story

Somewhere in the caverns beneath Castle Morvussan, the last giant Python of an ancient line of serpents is imprisoned. His name is  Vios, and King Smund and Queen Goura are draining his enchanted energy to power their tower. Can you write the test spells that will free him?

## How it works

Each unit follows the same run:

1. **The hook:** a story beat that creates a need
2. **The quest log:** the failing tests that define the goal
3. **Green:** the minimal code to make them pass
4. **Refactor:** clean up and learn the idiom
5. **Loot:** a recap, plus optional side quests

The campaign is continuous. Each unit builds on the code from the last, so the game you write in Unit 1 is still running in the finale.

## Units

| Unit | Quest | Concepts | Status |
|------|-------|----------|--------|
| 0 | Set Up Camp | the terminal, installing Python and Git, virtual environments, pytest, reading a test failure | Done |
| 1 | The Ability Check | Functions, ints, `//`, doctests | Done |
| 2 | The Narrator | Strings, f-strings, `join` | Done |
| 3 | The Backpack | Lists, loops | Done |
| 4 | The Character Sheet | dictionaries, `.items()`, comprehensions, dataclasses, `default_factory`* | Done |

Chapters live in [`units/`](units/). The game code lives in [`game/`](game/).

## Setup

You need Python 3.12 or newer and Git. The commands below use `python`. On macOS and Linux you may need `python3` instead, and on Windows `py` also works.

```bash
git clone https://github.com/ryanbenedetti/peat-bogs-and-pythons.git
cd peat-bogs-and-pythons
python tasks.py setup
```

Run the tests:

```bash
python tasks.py test
```

If you prefer to manage the environment yourself:

```bash
python -m venv .venv
# macOS/Linux:        source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd:        .venv\Scripts\activate.bat
pip install -r requirements.txt
python -m pytest
```

## Following along

The code is tagged at the end of every unit. If you get stuck, check out the tag for the previous unit and continue from a known-good state:

```bash
git checkout unit-02-done
```

Return to the latest with `git checkout main`.

## Credits

Inspired by [Learn Go with Tests](https://quii.gitbook.io/learn-go-with-tests) by Chris James, which pioneered learning a language by writing tests first. The units were co-written with [Claude](https://claude.ai), an AI assistant made by Anthropic, and tested and edited by [@ryanbenedetti](https://github.com/ryanbenedetti).
