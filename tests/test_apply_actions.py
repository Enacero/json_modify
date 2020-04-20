import json
import os

import pytest
import yaml

from json_modify import apply_actions


def test_apply_actions(mocker):
    mocker.patch("json_modify.validate_action")
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    mocker.patch("json_modify.get_reader")
    assert apply_actions({}, [{}]) == {}


def test_apply_actions_changes_source_in_place(mocker):
    mocker.patch("json_modify.validate_action")
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    mocker.patch("json_modify.get_reader")
    test_dict = {}
    return_dict = apply_actions(test_dict, [])
    assert id(test_dict) == id(return_dict)


def test_apply_actions_copy_true_copies_source(mocker):
    mocker.patch("json_modify.validate_action")
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    mocker.patch("json_modify.get_reader")
    test_dict = {}
    return_dict = apply_actions(test_dict, [], copy=True)
    assert not id(test_dict) == id(return_dict)


def test_apply_actions_with_source_as_filename(mocker):
    mocker.patch("json_modify.validate_action")
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")

    basepath = os.path.dirname(__file__)
    json_file = os.path.join(basepath, "data/test_data.json")
    yaml_file = os.path.join(basepath, "data/test_data.yaml")

    mocker.patch("json_modify.get_reader", return_value=json.load)
    return_data = apply_actions(json_file, [])
    assert isinstance(return_data, dict)
    with open(json_file, "r") as f:
        json_data = json.load(f)
    assert json_data == return_data

    mocker.patch("json_modify.get_reader", return_value=yaml.safe_load)
    return_data = apply_actions(yaml_file, [])
    assert isinstance(return_data, dict)
    with open(yaml_file, "r") as f:
        yaml_data = yaml.safe_load(f)
    assert yaml_data == return_data


def test_apply_actions_with_actions_as_filename(mocker):
    mocker.patch("json_modify.validate_action")
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    mocker.patch("json_modify.get_reader")

    basepath = os.path.dirname(__file__)
    json_file = os.path.join(basepath, "data/actions.json")
    yaml_file = os.path.join(basepath, "data/actions.yaml")

    assert apply_actions({}, json_file) == {}

    assert apply_actions({}, yaml_file) == {}


def test_apply_actions_raises_with_wrong_type_source(mocker):
    mocker.patch("json_modify.validate_action")
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    mocker.patch("json_modify.get_reader")

    with pytest.raises(TypeError) as exc:
        apply_actions(10, [])

    expected = "source should be data dictionary or file_name with data"
    assert str(exc.value) == expected


def test_apply_actions_raises_with_wrong_type_actions(mocker):
    mocker.patch("json_modify.validate_action")
    mocker.patch("json_modify.get_section")
    mocker.patch("json_modify.apply_action")
    mocker.patch("json_modify.get_reader")

    with pytest.raises(TypeError) as exc:
        apply_actions({}, 10)

    expected = "actions should be data dictionary or file_name with actions list"
    assert str(exc.value) == expected
