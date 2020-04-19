import json
import os

import pytest
import yaml

from json_modify import (
    get_reader,
    find_section_in_list,
    get_section,
    apply_actions,
    apply_action,
    get_path,
    apply_to_dict,
    apply_to_list,
    validate_action,
)


def test_get_reader():
    assert get_reader("test.yaml") == yaml.safe_load
    assert get_reader("test.json") == json.load
    with pytest.raises(ValueError) as exc:
        get_reader("test.cfg")
    assert str(exc.value) == "Cant determine reader for .cfg extension"


def test_find_section_in_list_with_index_marker():
    assert find_section_in_list([1, 2], {}, "$0") == 0


def test_find_section_in_list_with_filter_marker():
    complex_section = [{"name": "a", "value": 10}, {"name": "b", "value": 20}]
    action = {"name": [{"key": "name", "value": "b"}]}
    assert find_section_in_list(complex_section, action, "$name") == 1

    action["name"].append({"key": "value", "value": 20})
    assert find_section_in_list(complex_section, action, "$name") == 1


def test_find_section_in_list_without_filter_for_marker():
    complex_section = [{"name": "a", "value": 10}, {"name": "b", "value": 20}]
    action = {"name": [{"key": "name", "value": "b"}]}
    with pytest.raises(KeyError) as exc:
        find_section_in_list(complex_section, action, "$key")


def test_find_section_in_list_value_for_marker_not_found():
    complex_section = [{"name": "a", "value": 10}, {"name": "b", "value": 20}]
    action = {"name": [{"key": "name", "value": "b"}, {"key": "value", "value": 10}]}
    with pytest.raises(IndexError) as exc:
        assert find_section_in_list(complex_section, action, "$name")

    expected = "Action {}: Value with {} filters not found".format(
        action, action["name"]
    )
    assert str(exc.value) == expected


def test_get_path_string():
    action = {"path": "metadata/name"}
    assert get_path(action, DELIM) == ["metadata", "name"]


def test_get_path_list():
    action = {"path": ["metadata", "name"]}
    assert get_path(action, DELIM) == ["metadata", "name"]


DELIM = "/"
SOURCE = {
    "spec": {
        "name": "test",
        "metadata": [
            {"name": "test1", "value": "test1"},
            {"name": "test2", "value": "test2"},
        ],
        "values": {"value1": 10, "value2": 20},
    }
}


def test_get_section():

    action = {"path": "spec/name", "action": "replace"}
    assert get_section(SOURCE, action, DELIM) == SOURCE["spec"]

    action = {"path": "spec/name", "action": "add"}
    assert get_section(SOURCE, action, DELIM) == "test"

    action = {"path": "spec/values/value1", "action": "replace"}
    assert get_section(SOURCE, action, DELIM) == {"value1": 10, "value2": 20}

    action = {"path": "spec/values/value1", "action": "add"}
    assert get_section(SOURCE, action, DELIM) == 10


def test_get_section_with_marker():
    action = {
        "path": "spec/metadata/$meta_name",
        "action": "replace",
        "meta_name": [{"key": "name", "value": "test1"}],
    }
    assert get_section(SOURCE, action, DELIM) == [
        {"name": "test1", "value": "test1"},
        {"name": "test2", "value": "test2"},
    ]

    action = {
        "path": "spec/metadata/$meta_name",
        "action": "add",
        "meta_name": [{"key": "name", "value": "test1"}],
    }
    assert get_section(SOURCE, action, DELIM) == {"name": "test1", "value": "test1"}


def test_get_section_with_multiple_filters_in_marker():
    action = {
        "path": "spec/metadata/$meta_name/name",
        "action": "replace",
        "meta_name": [{"key": "name", "value": "test1"}],
    }
    assert get_section(SOURCE, action, DELIM) == {"name": "test1", "value": "test1"}

    action = {
        "path": "spec/metadata/$meta_name/name",
        "action": "add",
        "meta_name": [{"key": "name", "value": "test1"}],
    }
    assert get_section(SOURCE, action, DELIM) == "test1"


def test_get_section_with_index_marker():
    action = {"path": "spec/metadata/$0/name", "action": "replace"}
    assert get_section(SOURCE, action, DELIM) == {"name": "test1", "value": "test1"}

    action = {"path": "spec/metadata/$0/name", "action": "add"}
    assert get_section(SOURCE, action, DELIM) == "test1"


def test_get_section_with_list_as_root():
    source = [{"name": "test1"}, {"name": "test2"}]
    action = {
        "path": "$name",
        "action": "replace",
        "name": [{"key": "name", "value": "test1"}],
    }
    assert get_section(source, action, DELIM) == source

    source = [{"name": "test1"}, {"name": "test2"}]
    action = {
        "path": "$name",
        "action": "add",
        "name": [{"key": "name", "value": "test1"}],
    }
    assert get_section(source, action, DELIM) == {"name": "test1"}


def test_get_section_bad_section():
    source = [{"name": "test1"}, {"name": "test2"}]
    action = {"path": "name", "action": "add"}
    with pytest.raises(TypeError) as exc:
        get_section(source, action, DELIM)

    expected = "Action {}: section {} is not dict".format(action, source)
    assert str(exc.value) == expected

    source = {"name": "test1"}
    action = {"path": "$name", "action": "add"}
    with pytest.raises(TypeError) as exc:
        get_section(source, action, DELIM)

    expected = "Action {}: section {} is not list".format(action, source)
    assert str(exc.value) == expected


def test_get_section_with_list_path():
    source = {"metadata": {"name": "test1", "value": 10}}
    action = {"path": ["metadata", "value"], "action": "add"}
    assert get_section(source, action, DELIM) == 10


def test_get_section_with_another_delimeter():
    source = {"metadata": {"name": "test1", "value": 10}}
    action = {"path": "metadata,value", "action": "add"}
    assert get_section(source, action, ",") == 10


def test_apply_to_dict_add():
    section = {}
    action = {"action": "add", "value": {"a": 10}}
    apply_to_dict(section, action, DELIM)
    assert section == {"a": 10}


def test_apply_to_dict_add_with_wrong_type_of_value():
    section = {}
    action = {"action": "add", "value": 10}

    with pytest.raises(TypeError) as exc:
        apply_to_dict(section, action, DELIM)

    expected = (
        "Action {}: value for add operation on "
        "dict should be of type dict".format(action)
    )

    assert str(exc.value) == expected


def test_apply_to_dict_replace():
    section = {"a": 10}
    action = {"action": "replace", "path": "a", "value": 20}
    apply_to_dict(section, action, DELIM)
    assert section == {"a": 20}


def test_apply_to_dict_replace_with_another_type():
    section = {"a": 20}
    action = {"action": "replace", "path": "a", "value": ["a", "b"]}
    apply_to_dict(section, action, DELIM)
    assert section == {"a": ["a", "b"]}


def test_apply_to_dict_delete():
    section = {"a": 20}
    action = {"action": "delete", "path": "a"}
    apply_to_dict(section, action, DELIM)
    assert section == {}


def test_apply_to_dict_delete_wrong_key():
    section = {"a": 20}
    action = {"action": "delete", "path": "b"}
    with pytest.raises(KeyError) as exc:
        apply_to_dict(section, action, DELIM)
    assert section == {"a": 20}

    expected = '"Action {}: no such key b"'.format(action)
    assert str(exc.value) == expected


def test_apply_to_dict_rename():
    section = {"a": 20}
    action = {"action": "rename", "path": "a", "value": "b"}
    apply_to_dict(section, action, DELIM)
    assert section == {"b": 20}


def test_apply_to_dict_rename_with_wrong_key():
    section = {"a": 20}
    action = {"action": "rename", "path": "b"}
    with pytest.raises(KeyError) as exc:
        apply_to_dict(section, action, DELIM)
    assert section == {"a": 20}

    expected = '"Action {}: no such key b"'.format(action)
    assert str(exc.value) == expected


def test_apply_to_list_add():
    section = ["a"]
    action = {"action": "add", "value": ["b"]}
    apply_to_list(section, action, DELIM)
    assert section == ["a", "b"]


def test_apply_to_list_add_with_wrong_type_of_value():
    section = ["a"]
    action = {"action": "add", "value": 10}

    with pytest.raises(TypeError) as exc:
        apply_to_list(section, action, DELIM)

    expected = (
        "Action {}: value for add operation on list should "
        "be of type list".format(action)
    )
    assert str(exc.value) == expected


def test_apply_to_list_replace():
    section = ["a"]
    action = {"action": "replace", "value": "b", "path": "$0"}
    apply_to_list(section, action, DELIM)
    assert section == ["b"]


def test_apply_to_list_delete():
    section = ["a"]
    action = {"action": "delete", "path": "$0"}
    apply_to_list(section, action, DELIM)
    assert section == []


def test_validate_action():
    action = {"action": "delete", "path": "a/b"}
    validate_action(action, DELIM)
    action = {"action": "add", "path": "a/b", "value": {"a": 10}}
    validate_action(action, DELIM)
    action = {"action": "replace", "path": "a/b", "value": 10}
    validate_action(action, DELIM)
    action = {"action": "rename", "path": "a/b", "value": "c"}
    validate_action(action, DELIM)


def test_validate_action_raises():
    action = {}
    with pytest.raises(KeyError) as exc:
        validate_action(action, DELIM)

    expected = "'Action {}: key action is required'"
    assert str(exc.value) == expected

    action = {"action": "add"}
    with pytest.raises(KeyError) as exc:
        validate_action(action, DELIM)

    expected = '"Action {}: key path is required"'.format(action)
    assert str(exc.value) == expected

    action = {"action": "add", "path": "a"}
    with pytest.raises(KeyError) as exc:
        validate_action(action, DELIM)

    expected = '"Action {}: for add action key value is required"'.format(action)
    assert str(exc.value) == expected

    action = {"action": "add", "path": "a", "value": 10}
    with pytest.raises(TypeError) as exc:
        validate_action(action, DELIM)

    expected = "Action {}: for add action on dict value should be dict".format(action)
    assert str(exc.value) == expected

    action = {"action": "add", "path": "$a", "value": 10}
    with pytest.raises(TypeError) as exc:
        validate_action(action, DELIM)

    expected = "Action {}: for add action on list value should be list".format(action)
    assert str(exc.value) == expected

    action = {"action": "rename", "path": "a", "value": 10}
    with pytest.raises(TypeError) as exc:
        validate_action(action, DELIM)

    expected = "Action {}: for rename action on dict value should be string".format(
        action
    )
    assert str(exc.value) == expected


def test_apply_actions():
    assert apply_actions({}, []) == {}


def test_apply_actions_changes_source_in_place():
    test_dict = {}
    return_dict = apply_actions(test_dict, [])
    assert id(test_dict) == id(return_dict)


def test_apply_actions_copy_true_copies_source():
    test_dict = {}
    return_dict = apply_actions(test_dict, [], copy=True)
    assert not id(test_dict) == id(return_dict)


def test_apply_actions_with_source_as_filename(mocker):
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    basepath = os.path.dirname(__file__)
    json_file = os.path.join(basepath, "data/test_data.json")
    yaml_file = os.path.join(basepath, "data/test_data.yaml")

    return_data = apply_actions(json_file, [])
    assert isinstance(return_data, dict)
    with open(json_file, "r") as f:
        json_data = json.load(f)
    assert json_data == return_data

    return_data = apply_actions(yaml_file, [])
    assert isinstance(return_data, dict)
    with open(yaml_file, "r") as f:
        yaml_data = yaml.safe_load(f)
    assert yaml_data == return_data


def test_apply_actions_with_actions_as_filename(mocker):
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    mocker.patch("json_modify.validate_action")

    basepath = os.path.dirname(__file__)
    json_file = os.path.join(basepath, "data/actions.json")
    yaml_file = os.path.join(basepath, "data/actions.yaml")

    assert apply_actions({}, json_file) == {}

    assert apply_actions({}, yaml_file) == {}


def test_apply_actions_raises_with_wrong_type_source():
    with pytest.raises(TypeError) as exc:
        apply_actions(10, [])
    assert str(exc.value) == "source should be data dictionary or file_name with data"


def test_apply_actions_raises_with_wrong_type_actions():
    with pytest.raises(TypeError) as exc:
        apply_actions({}, 10)
    assert (
        str(exc.value)
        == "actions should be data dictionary or file_name with actions list"
    )


def test_apply_action(mocker):
    mocker.patch("json_modify.apply_to_dict")
    mocker.patch("json_modify.apply_to_list")
    apply_action({}, {}, DELIM)
    apply_action([], {}, DELIM)


def test_apply_action_raises():
    with pytest.raises(TypeError) as exc:
        apply_action(10, {}, DELIM)
    assert str(exc.value) == "Action {}: Section 10 is not of type dict or list"
