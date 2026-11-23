from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from roblox_api import fetch_api_dump


def array_to_dictionary(table, hybrid_mode=None):
    tmp = {}
    if hybrid_mode == "adjust":
        for key, value in table.items():
            if isinstance(key, int):
                tmp[value] = True
            elif isinstance(value, dict):
                tmp[key] = array_to_dictionary(value, "adjust")
            else:
                tmp[key] = value
    else:
        for value in table:
            if isinstance(value, str):
                tmp[value] = True
    return tmp


def find_first_table(array):
    for item in array:
        if isinstance(item, dict):
            return item
    return None


Class = "Instance"


def check_superclass_inheritance(class_name, class_list):
    current_class = class_list.get(class_name)
    while current_class:
        if current_class["Name"] == Class:
            return True
        current_class = class_list.get(current_class["Superclass"])
    return False


s = "\n"


def api():
    return fetch_api_dump(prefer_full=True)


def fetch_api():
    response = api()
    api_classes = response["Classes"]
    class_list = {cls["Name"]: cls for cls in api_classes}

    global s
    for api_class in api_classes:
        class_name = api_class["Name"]

        # Check for superclass inheritance
        if not check_superclass_inheritance(class_name, class_list):
            s += f"{class_name} does not inherit from {Class}\n"

        prev_len = len(s)

        if len(s) != prev_len:
            s += "\n"


try:
    fetch_api()
    print(s)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_file_path = os.path.join(script_dir, "Dump")
    with open(output_file_path, "w") as file:
        file.write(s)
except Exception as e:
    print(f"Error: {e}")
