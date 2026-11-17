from abilities import ability_modifier


def test_average_score_has_no_modifier():
    assert ability_modifier(10) == 0


def test_strong_score_gives_bonus():
    assert ability_modifier(14) == 2


def test_weak_score_gives_penalty():
    assert ability_modifier(9) == -1
