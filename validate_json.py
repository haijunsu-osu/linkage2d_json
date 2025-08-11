#!/usr/bin/env python3
import json, sys
from jsonschema import validate, Draft202012Validator
from jsonschema.exceptions import ValidationError

def main(schema_path: str, data_path: str) -> int:
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        validate(instance=data, schema=schema, cls=Draft202012Validator)
        print(f"VALID: {data_path} conforms to {schema_path}")
        return 0
    except ValidationError as e:
        print("INVALID JSON linkage.")
        print(f"Message : {e.message}")
        print(f"Path    : {'/'.join([str(p) for p in e.path])}")
        print(f"Schema  : {'/'.join([str(p) for p in e.schema_path])}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_json.py planar_linkage.schema.json <linkage.json>")
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
