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
