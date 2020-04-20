import pytest

from json_modify import get_path

DELIM = "/"


def test_get_path_string():
    action = {"path": "metadata/name"}
    assert get_path(action, DELIM) == ["metadata", "name"]


def test_get_path_list():
    action = {"path": ["metadata", "name"]}
    assert get_path(action, DELIM) == ["metadata", "name"]


def test_get_path_wront_path_type():
    action = {"path": 10}
    with pytest.raises(TypeError) as exc:
        get_path(action, DELIM)

    expected = "Action {}: path should be str or list of strings".format(action)

    assert str(exc.value) == expected
