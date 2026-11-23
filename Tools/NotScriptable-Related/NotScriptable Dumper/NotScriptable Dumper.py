from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
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


s = "\n"
filtered_properties = []


def api():
    return fetch_api_dump(prefer_full=True)


def fetch_api():
    response = api()
    api_classes = response["Classes"]

    global s, filtered_properties
    for api_class in api_classes:
        class_name = api_class["Name"]
        class_members = api_class["Members"]

        prev_len = len(s)
        enum_members = {}

        for member in class_members:
            member_name = member["Name"]
            member_type = member["MemberType"]
            if member_type == "Property":
                serialization = member["Serialization"]
                member_tags = member.get("Tags")
                original_tags = member_tags
                special = False
                if member_tags:
                    member_tags = array_to_dictionary(member_tags)
                    special = member_tags.get("NotScriptable")

                if serialization["CanLoad"] and serialization["CanSave"] and special:
                    value_type = member["ValueType"]["Name"]
                    value_category = member["ValueType"]["Category"]
                    if value_category == "Enum":
                        enum_members[value_type] = member_name
                    s += f"{class_name}.{member_name} {'{BinaryString}' if value_type == 'BinaryString' else ''}"
                    table_found = find_first_table(original_tags)
                    if table_found:
                        descriptor_name = table_found.get("PreferredDescriptorName")
                        if isinstance(descriptor_name, str) and descriptor_name:
                            s += f"{{PreferredDescriptorName: {descriptor_name}}}"
                    s += "\n"

                if re.search(r"xml|internal|serial", member_name, re.IGNORECASE):

                    str = f"{class_name}.{member_name}"
                    if not special:
                        str += " {Scriptable}"
                    if not (
                        serialization.get("CanLoad", True)
                        and serialization.get("CanSave", True)
                    ):
                        str += " {Serialize: False}"

                    filtered_properties.append(str)

        for enum_type, real_member_name in enum_members.items():
            for member in class_members:
                member_name = member["Name"]
                member_type = member["MemberType"]
                if member_name != real_member_name and member_type == "Property":
                    value_category = member["ValueType"]["Category"]
                    if value_category == "Enum":
                        value_type = member["ValueType"]["Name"]
                        if value_type == enum_type:
                            s += f"{real_member_name} -> {member_name}\n"

        if len(s) != prev_len:
            s += "\n"

    if filtered_properties:
        s += "\nPotential Proxy Properties:\n"
        s += "\n".join(filtered_properties) + "\n"


try:
    fetch_api()
    print(s)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_file_path = os.path.join(script_dir, "Dump")
    with open(output_file_path, "w") as file:
        file.write(s)
except Exception as e:
    print(f"Error: {e}")
