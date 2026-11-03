from breezehunt.scoring import classify_swell


def test_very_high_swell():
    assert classify_swell(6, 14) == 3


def test_high_swell():
    assert classify_swell(4, 13) == 2


def test_moderate_swell():
    assert classify_swell(3, 12) == 1


def test_low_swell():
    assert classify_swell(2.9, 12) == 0


def test_both_conditions_are_required():
    assert classify_swell(6, 13.9) == 2
    assert classify_swell(2.9, 14) == 0


def test_missing_data():
    assert classify_swell(None, 14) is None
    assert classify_swell(3, None) is None