# Unit 0: Setting Up Camp

*Concepts: the terminal, installing Python and Git, virtual environments, pytest, reading a test failure*

## The story

Dusk falls. Fog lifts from the peat bog. Castle Morvussan looms in the distance. In its dungeons, Vios, the last of the great Pythons is caged. The Royals who hold him there have convinced nearly all of their subjects that Vios is a dangerous and cunning monstrosity.

But you know better. You've packed your lantern, your rope and pinions, and your tome of spells. Set up camp at the edge of the bog. Commit more spells to memory. There are tests to pass to open the way -- The Code of the Python.

## How this book works

Every unit follows the same pattern of test-driven development:

1. **Red:** write a test, a problem to solve with Python code. It fails.
2. **Green:** write the smallest amount of code to get that test to pass.
3. **Refactor:** sharpen the code while the tests keep you on guard.

Type the code yourself, even when it's short snippets. And read the failures. In this adventure, a failing test isn't a mistake, it's the next instruction.

## What you'll need

- A computer running macOS, Linux, or Windows
- About 30 minutes
- Python 3.12 or newer
- Git
- A text editor (any will do, but [Visual Studio Code](https://code.visualstudio.com/) is free and works well)

## Step 1: Open a terminal

You'll type commands into a terminal throughout this book.

- **macOS:** press `Cmd + Space`, type **Terminal**, and press Enter.
- **Linux:** open your terminal app (often `Ctrl + Alt + T`).
- **Windows:** open the Start menu and search for **PowerShell** (or Windows Terminal).

When a command appears in this book, type it and press Enter. Lines starting with `#` are comments for you, not part of the command.

## Step 2: Install Python

Check whether you already have a recent Python:

```bash
python3 --version      # macOS and Linux
python --version       # Windows
```

If you see `Python 3.12` or higher (3.13, 3.14, and so on), skip to Step 3.

Careful on macOS: a bare Mac often reports an **older** `python3` (such as 3.9). That's too old for this book, so install a newer one.

- **Windows and macOS:** download the installer from [python.org/downloads](https://www.python.org/downloads/) and run it. **On Windows, tick the "Add python.exe to PATH" box** on the first screen of the installer.
- **Linux:** use your package manager, for example `sudo apt install python3 python3-venv` on Debian or Ubuntu. If your distribution ships something older than 3.12, install a newer version with your distribution's instructions or a tool such as `pyenv` or `uv`.

Close and reopen your terminal, then check again. Which command works depends on your system:

- macOS and Linux: `python3 --version`
- Windows: `python --version` (or `py --version`)

**A note on command names.** This book writes `python` in its commands. If that doesn't work on your machine, substitute `python3` (macOS and Linux) or `py` (Windows). Once your virtual environment is active in Step 5, plain `python` works everywhere.

## Step 3: Install Git

Git tracks your changes, so you can save your progress after every unit and always get back to a working state.

```bash
git --version
```

If that prints a version, you're done. If not, download Git from [git-scm.com](https://git-scm.com/downloads) and install it with the default options. Reopen your terminal and check again.

## Step 4: Make your camp

Choose a place for your project and create a folder:

```bash
mkdir peat-bogs-and-pythons
cd peat-bogs-and-pythons
```

(Feel free to name it anything. This book uses `peat-bogs-and-pythons`.)

Now create a **virtual environment**: a private box of Python tools that belongs only to this project, so nothing you install can interfere with the rest of your computer.

```bash
python -m venv .venv
```

Use `python3` or `py` instead of `python` if that's what worked in Step 2. This creates a hidden folder called `.venv`.

**Activate** it. The command depends on your system:

- macOS and Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows Command Prompt: `.venv\Scripts\activate.bat`

Your prompt should now start with `(.venv)`. That means the environment is active, and plain `python` now refers to the right Python on every system. (To leave it later, run `deactivate`.)

Now install **pytest**, the testing tool we'll use all book long:

```bash
python -m pip install pytest
```

Finally, make the folder where your game will live:

```bash
mkdir game
```

## Step 5: Configure the project

Open the `peat-bogs-and-pythons` folder in your editor. (With VS Code installed, `code .` opens the current folder.)

Create a file in the project root called `pyproject.toml` with this content:

```toml
[project]
name = "peat-bogs-and-pythons"
version = "0.1.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
testpaths = ["game"]
pythonpath = ["game"]
addopts = "--doctest-modules"
```

What the lines do:

- `requires-python` states the minimum Python version.
- `testpaths` tells pytest to look for tests in `game/`.
- `pythonpath` lets your tests import the code in `game/`.
- `addopts = "--doctest-modules"` also runs the examples written inside docstrings, which you'll meet in Unit 1.

Then create `.gitignore` in the same place, so Git skips files it shouldn't track:

```
.venv/
__pycache__/
.pytest_cache/
```

## Step 6: Your first test

Time to follow the rhythm. Create `game/test_camp.py`:

```python
from camp import welcome


def test_welcome_greets_the_hero():
    assert welcome("Wren") == "Welcome to the camp, Wren."
```

pytest finds files named `test_*.py` and runs every function named `test_*`. A bare `assert` is all a test needs: if the statement is false, the test fails.

### Red: the code doesn't exist

Run the tests from the project root:

```bash
pytest
```

```
E   ModuleNotFoundError: No module named 'camp'
```

(You may see the error twice, because of the doctest option. That's fine.) Read it, because it tells you exactly what's missing. The test wants a module called `camp`. Create `game/camp.py`, but write it **wrong** on purpose:

```python
def welcome(name):
    return "Hello"
```

Run `pytest` again:

```
>       assert welcome("Wren") == "Welcome to the camp, Wren."
E       AssertionError: assert 'Hello' == 'Welcome to the camp, Wren.'
E         - Welcome to the camp, Wren.
E         + Hello
```

This is how to read a pytest failure:

- The line starting with `>` is the line that failed.
- The lines starting with `E` explain why. The `-` line is what the test expected, and the `+` line is what your code actually returned.

That's a *useful* red: the code runs, but gives the wrong answer. Seeing the test fail first proves the test can actually catch a bug.

### Green: make it pass

```python
def welcome(name):
    return f"Welcome to the camp, {name}."
```

(The `f` before the quote makes it an f-string. Anything inside `{}` is replaced by its value. Unit 2 explains the details.) Run `pytest`:

```
game/test_camp.py .                                                      [100%]

============================== 1 passed in 0.01s ==============================
```

Your first green. The camp is ready.

## If something goes wrong

- **`python: command not found` (macOS or Linux):** use `python3` until your environment is active.
- **`python` opens the Microsoft Store (Windows):** the installer from python.org either didn't finish or didn't add Python to PATH. Rerun it and tick "Add python.exe to PATH", or use `py` instead.
- **`running scripts is disabled on this system` (PowerShell):** run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again. Or use Command Prompt and `.venv\Scripts\activate.bat`.
- **`ensurepip is not available` (Debian or Ubuntu):** run `sudo apt install python3-venv`, delete the `.venv` folder, and repeat the `venv` step.
- **`pytest: command not found`:** your environment isn't active. Look for `(.venv)` at the start of your prompt. As a fallback, `python -m pytest` also works.
- **`no tests ran`:** pytest didn't find your test file. Check that it's named `test_camp.py`, sits in the `game/` folder, and that you're running the command from the project root.

## Loot (what you learned)

- The terminal, and how to check what's installed
- Virtual environments keep each project's tools separate
- pytest finds `test_*.py` files and reads plain `assert` statements
- Red, green, refactor: write a failing test, make it pass, then tidy up
- How to read a failure: `>` marks the failing line, and the `E` lines say what was expected and what happened

## Side quests

- **Break it on purpose.** Change the expected text in the test and run `pytest`. Read the failure carefully, then put it back.
- **Say it louder.** Run `pytest -v` to see test names listed individually.
- **More than one hero.** Add a second test that greets `"Corin"`. Does your function pass without any changes? Why?
- **Make it yours.** Change the greeting to mention the peat bog. Change the test first, watch it fail, then update the code.

## Next quest

You leave camp and hike up through the bog to the castle gate. It's locked, and it's guarded by an old, clever mechanism that wants a roll to pick it. But before you can roll anything, the game needs to know how good you are at things. In **Unit 1**, you build the ability check.

## Save your progress

Turn your project into a Git repository and save the camp:

```bash
git init -b main
git add .
git commit -m "Set up camp"
git tag unit-00-done
```

If Git complains that it doesn't know who you are, tell it once and repeat the commit:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

From now on, finish each unit by committing and tagging it (`unit-01-done`, `unit-02-done`, and so on). If a later unit goes wrong, you can always return to a tag where everything worked.
