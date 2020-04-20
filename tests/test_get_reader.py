import json

import pytest
import yaml

from json_modify import get_reader


def test_get_reader():
    assert get_reader("test.yaml") == yaml.safe_load
    assert get_reader("test.json") == json.load
    with pytest.raises(ValueError) as exc:
        get_reader("test.cfg")
    assert str(exc.value) == "Cant determine reader for .cfg extension"
