#   MIT License
#
#   Copyright (c) 2020 Oleksii Petrenko
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.


from copy import deepcopy
import json
import typing
import os

import yaml

__version__ = "1.0.1"
__license__ = "MIT"

__all__ = (
    "apply_actions",
    "apply_to_list",
    "apply_to_dict",
    "validate_action",
    "validate_marker",
    "apply_action",
    "get_path",
    "get_section",
    "get_reader",
    "find_section_in_list",
)


def get_reader(
    file_name: str,
) -> typing.Callable[[typing.Any], typing.Iterable[typing.Any]]:
    """
    Determine reader for file.
    :param file_name: name of the file with source data
    :return: function to read data from file
    """
    ext = os.path.splitext(file_name)[-1]
    if ext in [".yaml", "yml"]:
        return yaml.safe_load
    elif ext == ".json":
        return json.load
    raise ValueError("Cant determine reader for {} extension".format(ext))


def find_section_in_list(
    section: typing.List[typing.Any], action: typing.Dict[str, typing.Any], key: str
) -> int:
    """
    Find index of section in list
    :param section: list, where we want to search
    :param action: action dictionary
    :param key: the key marker
    :return: index of searched section
    """
    key = key[1:]
    if key.isdigit():
        return int(key)
    if key not in action:
        raise KeyError("Action {}: marker {} not found in action".format(action, key))
    compares = action[key]

    for index, section in enumerate(section):
        if all(section[compare["key"]] == compare["value"] for compare in compares):
            return index
    raise IndexError(
        "Action {}: Value with {} filters not found".format(action, compares)
    )


def get_path(action: typing.Dict[str, typing.Any], path_delim: str) -> typing.List[str]:
    """
    Get path from action
    :param action: action object
    :param path_delim: delimiter to be used to split path into keys.
        (Not used when path is list)
    :return: list of keys
    """
    path = action["path"]
    if isinstance(path, str):
        keys = [str(key) for key in action["path"].split(path_delim)]
        return keys
    elif isinstance(path, typing.List) and all(isinstance(key, str) for key in path):
        return path
    else:
        raise TypeError(
            "Action {}: path should be str or list of strings".format(action)
        )


def get_section(
    source_data: typing.Iterable[typing.Any],
    action: typing.Dict[str, typing.Any],
    path_delim: str,
) -> typing.Iterable[typing.Any]:
    """
    Get section descried by action's path.
    :param source_data: source data where to search
    :param action: action object
    :param path_delim: delimiter to be used to split path into keys.
        (Not used when path is list)
    :return: section from source_data described by path
    """
    section = source_data
    path = get_path(action, path_delim)

    if not action["action"] == "add":
        path = path[:-1]

    for key in path:
        key = key.strip()
        if key.startswith("$"):
            if not isinstance(section, typing.List):
                raise TypeError(
                    "Action {}: section {} is not list".format(action, section)
                )
            section_index = find_section_in_list(section, action, key)
            section = section[section_index]
        else:
            if not isinstance(section, typing.Dict):
                raise TypeError(
                    "Action {}: section {} is not dict".format(action, section)
                )
            section = section[key]
    return section


def apply_to_dict(
    section: typing.Dict[str, typing.Any],
    action: typing.Dict[str, typing.Any],
    path_delim: str,
) -> None:
    """
    Apply action to dictionary.
    :param section: section on which action should be applied
    :param action: action object that should be applied
    :param path_delim: delimiter
    """
    action_name = action["action"]
    value = action.get("value")

    if action_name == "add":
        if isinstance(value, typing.Dict):
            section.update(value)
        else:
            raise TypeError(
                "Action {}: value for add operation on dict should "
                "be of type dict".format(action)
            )
    else:
        path = get_path(action, path_delim)
        key = path[-1].strip()

        if action_name == "replace":
            section[key] = value
        elif action_name == "delete":
            if key not in section:
                raise KeyError("Action {}: no such key {}".format(action, key))
            del section[key]
        elif action_name == "rename":
            if key not in section:
                raise KeyError("Action {}: no such key {}".format(action, key))
            elif isinstance(value, str):
                section[value] = section[key]
                del section[key]
            else:
                raise TypeError(
                    "Action {}: for rename action on dict value "
                    "should be string".format(action)
                )


def apply_to_list(
    section: typing.List[typing.Any],
    action: typing.Dict[str, typing.Any],
    path_delim: str,
) -> None:
    """
    Apply action to list.
    :param section: section on which action should be applied
    :param action: action object that should be applied
    :param path_delim: delimiter
    """
    action_name = action["action"]
    value = action.get("value")

    if action_name == "add":
        if isinstance(value, list):
            section.extend(value)
        else:
            raise TypeError(
                "Action {}: value for add operation on list should "
                "be of type list".format(action)
            )
    else:
        path = get_path(action, path_delim)
        key = path[-1].strip()
        section_index = find_section_in_list(section, action, key)
        if action_name == "replace":
            section[section_index] = value
        elif action_name == "delete":
            section.pop(section_index)


def apply_action(
    section: typing.Iterable[typing.Any],
    action: typing.Dict[str, typing.Any],
    path_delim: str,
) -> None:
    """
    Apply action to selected section.
    :param section: section to be modified
    :param action: action object
    :param path_delim: path delimiter. default is '/'
    """
    if isinstance(section, typing.Dict):
        apply_to_dict(section, action, path_delim)
    elif isinstance(section, typing.List):
        apply_to_list(section, action, path_delim)
    else:
        raise TypeError(
            "Action {}: Section {} is not of type dict or list".format(action, section)
        )


def validate_marker(action: typing.Dict[str, typing.Any], key: str) -> None:
    """
    Validate marker from action's path.
    :param action: action object
    :param key: key that is used as marker
    """
    key = key[1:]
    marker = action.get(key)
    if not marker:
        raise KeyError(
            "Action {}: marker {} should be defined in action".format(action, key)
        )
    if not isinstance(marker, typing.List):
        raise TypeError(
            "Action {}: marker {} should be of type list".format(action, key)
        )
    for search_filter in marker:
        if not isinstance(search_filter, typing.Dict):
            raise TypeError(
                "Action {}: marker {} filters should be of type dict".format(
                    action, key
                )
            )

        filter_key = search_filter.get("key")
        filter_value = search_filter.get("value")
        if not filter_key or not filter_value:
            raise KeyError(
                "Action {}: for marker {} key and value should be specified".format(
                    action, key
                )
            )


def validate_action(action: typing.Dict[str, typing.Any], path_delim: str) -> None:
    """
    Validate action.
    :param action: action object
    :param path_delim: path delimiter
    """
    action_name = action.get("action")
    if not action_name:
        raise KeyError("Action {}: key action is required".format(action))

    path = action.get("path")
    if not path:
        raise KeyError("Action {}: key path is required".format(action))

    path = get_path(action, path_delim)

    for key in path:
        if key.startswith("$") and not key[1:].isdigit():
            validate_marker(action, key)

    value = action.get("value")

    if action_name in ["add", "replace", "rename"] and not value:
        raise KeyError(
            "Action {}: for {} action key value is required".format(action, action_name)
        )

    if action_name == "add":
        key = path[-1]
        if key.startswith("$") and not isinstance(value, typing.List):
            raise TypeError(
                "Action {}: for add action on list value should be list".format(action)
            )
        elif not isinstance(value, typing.Dict):
            raise TypeError(
                "Action {}: for add action on dict value should be dict".format(action)
            )
    elif action_name == "rename":
        if not isinstance(value, str):
            raise TypeError(
                "Action {}: for rename action on dict value should be string".format(
                    action
                )
            )


def apply_actions(
    source: typing.Union[typing.Dict[str, typing.Any], str],
    actions: typing.Union[typing.List[typing.Dict[str, typing.Any]], str],
    copy: bool = False,
    path_delim: str = "/",
) -> typing.Iterable[typing.Any]:
    """
    Apply actions on source_data.
    :param source: dictionary or json/yaml file with data that should be modified
    :param actions: list or json/yaml file with actions, that should be applied to
        source
    :param copy: should source be copied before modification or changed in place
        (works only when source is dictionary not file). default is False
    :param path_delim: path delimiter. default is '/'
    :return: source modified after applying actions
    """
    if isinstance(source, str):
        reader = get_reader(source)
        with open(source, "r") as f:
            source_data = reader(f)
    elif isinstance(source, typing.Dict):
        if copy:
            source_data = deepcopy(source)
        else:
            source_data = source
    else:
        raise TypeError("source should be data dictionary or file_name with data")

    if isinstance(actions, str):
        reader = get_reader(actions)
        with open(actions, "r") as f:
            actions_data = reader(f)
    elif isinstance(actions, typing.List):
        actions_data = actions
    else:
        raise TypeError(
            "actions should be data dictionary or file_name with actions list"
        )

    for action in actions_data:
        validate_action(action, path_delim)

    for action in actions_data:
        section = get_section(source_data, action, path_delim)
        apply_action(section, action, path_delim)

    return source_data
