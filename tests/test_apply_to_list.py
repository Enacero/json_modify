import pytest

from json_modify import apply_to_list

DELIM = "/"


def test_apply_to_list_add(mocker):
    mocker.patch("json_modify.get_path")
    mocker.patch("json_modify.find_section_in_list")

    section = ["a"]
    action = {"action": "add", "value": ["b"]}
    apply_to_list(section, action, DELIM)
    assert section == ["a", "b"]


def test_apply_to_list_add_with_wrong_type_of_value(mocker):
    mocker.patch("json_modify.get_path")
    mocker.patch("json_modify.find_section_in_list")

    section = ["a"]
    action = {"action": "add", "value": 10}

    with pytest.raises(TypeError) as exc:
        apply_to_list(section, action, DELIM)

    expected = (
        "Action {}: value for add operation on list should "
        "be of type list".format(action)
    )
    assert str(exc.value) == expected


def test_apply_to_list_replace(mocker):
    mocker.patch("json_modify.get_path", return_value=["$0"])
    mocker.patch("json_modify.find_section_in_list", return_value=0)

    section = ["a"]
    action = {"action": "replace", "value": "b", "path": "$0"}
    apply_to_list(section, action, DELIM)
    assert section == ["b"]


def test_apply_to_list_delete(mocker):
    mocker.patch("json_modify.get_path", return_value=["$0"])
    mocker.patch("json_modify.find_section_in_list", return_value=0)

    section = ["a"]
    action = {"action": "delete", "path": "$0"}
    apply_to_list(section, action, DELIM)
    assert section == []
