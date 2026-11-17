from narrator import describe_ability, describe_room


def test_describe_ability_with_bonus():
    assert describe_ability("Dexterity", 14) == "Dexterity 14 (+2)"


def test_describe_ability_with_penalty():
    assert describe_ability("Strength", 8) == "Strength 8 (-1)"


def test_describe_room_with_two_exits():
    assert (
        describe_room("courtyard", ["north", "east"])
        == "You stand in the Courtyard. Exits: north, east."
    )


def test_describe_room_with_one_exit():
    assert (
        describe_room("dungeon", ["down"])
        == "You stand in the Dungeon. Exit: down."
    )
