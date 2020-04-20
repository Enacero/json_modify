import pytest

from json_modify import apply_to_dict

DELIM = "/"


def test_apply_to_dict_add(mocker):
    mocker.patch("json_modify.get_path")
    section = {}
    action = {"action": "add", "value": {"a": 10}}
    apply_to_dict(section, action, DELIM)
    assert section == {"a": 10}


def test_apply_to_dict_add_with_wrong_type_of_value(mocker):
    mocker.patch("json_modify.get_path")

    section = {}
    action = {"action": "add", "value": 10}

    with pytest.raises(TypeError) as exc:
        apply_to_dict(section, action, DELIM)

    expected = (
        "Action {}: value for add operation on "
        "dict should be of type dict".format(action)
    )

    assert str(exc.value) == expected


def test_apply_to_dict_replace(mocker):
    mocker.patch("json_modify.get_path", return_value=["a"])

    section = {"a": 10}
    action = {"action": "replace", "path": "a", "value": 20}
    apply_to_dict(section, action, DELIM)
    assert section == {"a": 20}


def test_apply_to_dict_replace_with_another_type(mocker):
    mocker.patch("json_modify.get_path", return_value=["a"])

    section = {"a": 20}
    action = {"action": "replace", "path": "a", "value": ["a", "b"]}
    apply_to_dict(section, action, DELIM)
    assert section == {"a": ["a", "b"]}


def test_apply_to_dict_delete(mocker):
    mocker.patch("json_modify.get_path", return_value=["a"])

    section = {"a": 20}
    action = {"action": "delete", "path": "a"}
    apply_to_dict(section, action, DELIM)
    assert section == {}


def test_apply_to_dict_delete_wrong_key(mocker):
    mocker.patch("json_modify.get_path", return_value=["b"])

    section = {"a": 20}
    action = {"action": "delete", "path": "b"}
    with pytest.raises(KeyError) as exc:
        apply_to_dict(section, action, DELIM)
    assert section == {"a": 20}

    expected = '"Action {}: no such key b"'.format(action)
    assert str(exc.value) == expected


def test_apply_to_dict_rename(mocker):
    mocker.patch("json_modify.get_path", return_value=["a"])

    section = {"a": 20}
    action = {"action": "rename", "path": "a", "value": "b"}
    apply_to_dict(section, action, DELIM)
    assert section == {"b": 20}


def test_apply_to_dict_rename_with_wrong_key(mocker):
    mocker.patch("json_modify.get_path", return_value=["b"])

    section = {"a": 20}
    action = {"action": "rename", "path": "b"}
    with pytest.raises(KeyError) as exc:
        apply_to_dict(section, action, DELIM)
    assert section == {"a": 20}

    expected = '"Action {}: no such key b"'.format(action)
    assert str(exc.value) == expected


def test_apply_to_dict_rename_with_wrong_value_type(mocker):
    mocker.patch("json_modify.get_path", return_value=["b"])

    section = {"b": 10}
    action = {"action": "rename", "path": "b"}
    with pytest.raises(TypeError) as exc:
        apply_to_dict(section, action, DELIM)

    expected = "Action {}: for rename action on dict " "value should be string".format(
        action
    )

    assert str(exc.value) == expected
