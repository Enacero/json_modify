import pytest

from json_modify import get_section


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


def test_get_section(mocker):
    mocker.patch("json_modify.find_section_in_list")

    mocker.patch("json_modify.get_path", return_value=["spec", "name"])
    action = {"path": "spec/name", "action": "replace"}
    assert get_section(SOURCE, action, DELIM) == SOURCE["spec"]

    action = {"path": "spec/name", "action": "add"}
    assert get_section(SOURCE, action, DELIM) == "test"

    mocker.patch("json_modify.get_path", return_value=["spec", "values", "value1"])
    action = {"path": "spec/values/value1", "action": "replace"}
    assert get_section(SOURCE, action, DELIM) == {"value1": 10, "value2": 20}

    action = {"path": "spec/values/value1", "action": "add"}
    assert get_section(SOURCE, action, DELIM) == 10


def test_get_section_with_marker(mocker):
    mocker.patch("json_modify.find_section_in_list", return_value=0)
    mocker.patch(
        "json_modify.get_path", return_value=["spec", "metadata", "$meta_name"]
    )

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


def test_get_section_with_multiple_filters_in_marker(mocker):
    mocker.patch("json_modify.find_section_in_list", return_value=0)
    mocker.patch(
        "json_modify.get_path", return_value=["spec", "metadata", "$meta_name", "name"]
    )

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


def test_get_section_with_index_marker(mocker):
    mocker.patch("json_modify.find_section_in_list", return_value=0)
    mocker.patch(
        "json_modify.get_path", return_value=["spec", "metadata", "$0", "name"]
    )

    action = {"path": "spec/metadata/$0/name", "action": "replace"}
    assert get_section(SOURCE, action, DELIM) == {"name": "test1", "value": "test1"}

    action = {"path": "spec/metadata/$0/name", "action": "add"}
    assert get_section(SOURCE, action, DELIM) == "test1"


def test_get_section_with_list_as_root(mocker):
    mocker.patch("json_modify.find_section_in_list", return_value=0)
    mocker.patch("json_modify.get_path", return_value=["$name"])

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


def test_get_section_bad_section(mocker):
    mocker.patch("json_modify.find_section_in_list")
    mocker.patch("json_modify.get_path", return_value=["name"])

    source = [{"name": "test1"}, {"name": "test2"}]
    action = {"path": "name", "action": "add"}
    with pytest.raises(TypeError) as exc:
        get_section(source, action, DELIM)

    expected = "Action {}: section {} is not dict".format(action, source)
    assert str(exc.value) == expected

    mocker.patch("json_modify.get_path", return_value=["$name"])
    source = {"name": "test1"}
    action = {"path": "$name", "action": "add"}
    with pytest.raises(TypeError) as exc:
        get_section(source, action, DELIM)

    expected = "Action {}: section {} is not list".format(action, source)
    assert str(exc.value) == expected


def test_get_section_with_list_path(mocker):
    mocker.patch("json_modify.find_section_in_list")
    mocker.patch("json_modify.get_path", return_value=["metadata", "value"])

    source = {"metadata": {"name": "test1", "value": 10}}
    action = {"path": ["metadata", "value"], "action": "add"}
    assert get_section(source, action, DELIM) == 10


def test_get_section_with_another_delimiter(mocker):
    mocker.patch("json_modify.find_section_in_list")
    mocker.patch("json_modify.get_path", return_value=["metadata", "value"])

    source = {"metadata": {"name": "test1", "value": 10}}
    action = {"path": "metadata,value", "action": "add"}
    assert get_section(source, action, ",") == 10
