from lottery_smart_bets.parser import parse_combination


def test_parse_combination() -> None:
    combo = parse_combination("3 4 7 19 23 28 31 + 50")
    assert combo.main == (3, 4, 7, 19, 23, 28, 31)
    assert combo.bonus == 50
