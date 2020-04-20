import pytest

from json_modify import validate_action

DELIM = "/"


def test_validate_action(mocker):
    mocker.patch("json_modify.get_path", return_value=["a", "b"])
    mocker.patch("json_modify.validate_marker")

    action = {"action": "delete", "path": "a/b"}
    validate_action(action, DELIM)
    action = {"action": "add", "path": "a/b", "value": {"a": 10}}
    validate_action(action, DELIM)
    action = {"action": "replace", "path": "a/b", "value": 10}
    validate_action(action, DELIM)
    action = {"action": "rename", "path": "a/b", "value": "c"}
    validate_action(action, DELIM)


def test_validate_action_raises_no_key(mocker):
    mocker.patch("json_modify.get_path")
    mocker.patch("json_modify.validate_marker")

    action = {}
    with pytest.raises(KeyError) as exc:
        validate_action(action, DELIM)

    expected = "'Action {}: key action is required'"
    assert str(exc.value) == expected


def test_validate_action_raises_no_path(mocker):
    mocker.patch("json_modify.get_path")
    mocker.patch("json_modify.validate_marker")

    action = {"action": "add"}
    with pytest.raises(KeyError) as exc:
        validate_action(action, DELIM)

    expected = '"Action {}: key path is required"'.format(action)
    assert str(exc.value) == expected


def test_validate_action_raises_no_value(mocker):
    mocker.patch("json_modify.get_path")
    mocker.patch("json_modify.validate_marker")

    action = {"action": "add", "path": "a"}
    with pytest.raises(KeyError) as exc:
        validate_action(action, DELIM)

    expected = '"Action {}: for add action key value is required"'.format(action)
    assert str(exc.value) == expected


def test_validate_action_raises_add_on_dict_value_not_dict(mocker):
    mocker.patch("json_modify.get_path", return_value=["a"])
    mocker.patch("json_modify.validate_marker")

    action = {"action": "add", "path": "a", "value": 10}
    with pytest.raises(TypeError) as exc:
        validate_action(action, DELIM)

    expected = "Action {}: for add action on dict value should be dict".format(action)
    assert str(exc.value) == expected


def test_validate_action_raises_add_on_list_value_not_list(mocker):
    mocker.patch("json_modify.get_path", return_value=["$a"])
    mocker.patch("json_modify.validate_marker")

    action = {"action": "add", "path": "$a", "value": 10}
    with pytest.raises(TypeError) as exc:
        validate_action(action, DELIM)

    expected = "Action {}: for add action on list value should be list".format(action)
    assert str(exc.value) == expected


def test_validate_action_raises_rename_value_not_dict(mocker):
    mocker.patch("json_modify.get_path")
    mocker.patch("json_modify.validate_marker")

    action = {"action": "rename", "path": "a", "value": 10}
    with pytest.raises(TypeError) as exc:
        validate_action(action, DELIM)

    expected = "Action {}: for rename action on dict value should be string".format(
        action
    )
    assert str(exc.value) == expected
