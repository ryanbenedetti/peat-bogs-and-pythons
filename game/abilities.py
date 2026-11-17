def ability_modifier(score: int) -> int:
    """Return the modifier for an ability score.

    >>> ability_modifier(16)
    3
    """
    return (score - 10) // 2
