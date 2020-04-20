import pytest

from json_modify import validate_marker


def test_validate_marker_no_marker():
    action = {}
    key = "$a"
    with pytest.raises(KeyError) as exc:
        validate_marker(action, key)

    expected = "'Action {}: marker {} should be defined in action'".format(
        action, key[1:]
    )

    assert str(exc.value) == expected


def test_validate_marker_wrong_marker_type():
    action = {"a": 10}
    key = "$a"
    with pytest.raises(TypeError) as exc:
        validate_marker(action, key)

    expected = "Action {}: marker {} should be of type list".format(action, key[1:])

    assert str(exc.value) == expected


def test_validate_marker_wrong_marker_key_value_type():
    action = {"a": [10]}
    key = "$a"
    with pytest.raises(TypeError) as exc:
        validate_marker(action, key)

    expected = "Action {}: marker {} filters should be of type dict".format(
        action, key[1:]
    )

    assert str(exc.value) == expected


def test_validate_marker_no_key_value():
    action = {"a": [{}]}
    key = "$a"
    with pytest.raises(KeyError) as exc:
        validate_marker(action, key)

    expected = '"Action {}: for marker {} key and value should be specified"'.format(
        action, key[1:]
    )

    assert str(exc.value) == expected
