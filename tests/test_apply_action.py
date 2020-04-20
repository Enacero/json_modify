import pytest

from json_modify import apply_action

DELIM = "/"


def test_apply_action(mocker):
    mocker.patch("json_modify.apply_to_dict")
    mocker.patch("json_modify.apply_to_list")
    apply_action({}, {}, DELIM)
    apply_action([], {}, DELIM)


def test_apply_action_raises(mocker):
    mocker.patch("json_modify.apply_to_dict")
    mocker.patch("json_modify.apply_to_list")
    with pytest.raises(TypeError) as exc:
        apply_action(10, {}, DELIM)
    assert str(exc.value) == "Action {}: Section 10 is not of type dict or list"
