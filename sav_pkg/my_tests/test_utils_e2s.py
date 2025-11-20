# sav_pkg/my_tests/test_utils_e2s.py

import json
from pathlib import Path

from sav_pkg.utils.utils import get_export_to_some_dict

class DummyPolicy:
    name = "Dummy E2S"

def test_get_export_to_some_dict_tmp_path(tmp_path):
    # Prepare a fake JSON file
    data = {"64500": {"64510": 0.7, "64520": 0.3}}
    json_path = tmp_path / "e2s.json"
    json_path.write_text(json.dumps(data))

    export_dict = get_export_to_some_dict(DummyPolicy, json_path=json_path)

    # Keys should be ints, values should be the policy class itself
    assert 64500 in export_dict
    assert export_dict[64500] is DummyPolicy
