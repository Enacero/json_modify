import pytest

from json_modify import find_section_in_list


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

    expected = ""

    assert str(exc.value) == expected


def test_find_section_in_list_value_for_marker_not_found():
    complex_section = [{"name": "a", "value": 10}, {"name": "b", "value": 20}]
    action = {"name": [{"key": "name", "value": "b"}, {"key": "value", "value": 10}]}
    with pytest.raises(IndexError) as exc:
        assert find_section_in_list(complex_section, action, "$name")

    expected = "Action {}: Value with {} filters not found".format(
        action, action["name"]
    )
    assert str(exc.value) == expected
