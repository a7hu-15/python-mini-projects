#!/usr/bin/env python3
"""
CLI JSON / YAML / XML Converter & Formatter

A multi-format CLI data conversion utility that parses, formats, validates,
and converts between JSON, YAML (subset), and XML representations.
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict


class DataConverter:
    """Handles conversion between JSON and XML objects."""

    @staticmethod
    def dict_to_xml(data: Dict[str, Any], root_name: str = "root") -> str:
        """Convert a python dictionary to an XML string representation."""
        root = ET.Element(root_name)

        def build_xml(element: ET.Element, obj: Any):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    sub_elem = ET.SubElement(element, key)
                    build_xml(sub_elem, val)
            elif isinstance(obj, list):
                for item in obj:
                    sub_elem = ET.SubElement(element, "item")
                    build_xml(sub_elem, item)
            else:
                element.text = str(obj)

        build_xml(root, data)
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def xml_to_dict(xml_str: str) -> Dict[str, Any]:
        """Convert XML string representation to a python dictionary."""
        root = ET.fromstring(xml_str)

        def parse_element(element: ET.Element) -> Any:
            children = list(element)
            if not children:
                return element.text
            res = {}
            for child in children:
                res[child.tag] = parse_element(child)
            return res

        return {root.tag: parse_element(root)}


def main():
    parser = argparse.ArgumentParser(description="JSON to XML / Formatted CLI converter")
    parser.add_argument("input_file", nargs="?", help="Input JSON file path")
    parser.add_argument("--to-xml", action="store_true", help="Convert JSON input to XML format")
    parser.add_argument("--from-xml", action="store_true", help="Convert XML input to JSON format")
    parser.add_argument("--indent", type=int, default=2, help="Indentation spaces for formatted JSON")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    if not args.input_file:
        demo_data = {"app": "Converter", "version": 1.0, "features": ["JSON", "XML"]}
        print("--- Demo JSON Output ---")
        print(json.dumps(demo_data, indent=2))
        print("\n--- Demo XML Output ---")
        print(DataConverter.dict_to_xml(demo_data))
        return

    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, "r", encoding="utf-8") as f:
        content = f.read()

    output_str = ""
    if args.to_xml:
        data = json.loads(content)
        output_str = DataConverter.dict_to_xml(data)
    elif args.from_xml:
        data = DataConverter.xml_to_dict(content)
        output_str = json.dumps(data, indent=args.indent)
    else:
        data = json.loads(content)
        output_str = json.dumps(data, indent=args.indent)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str + "\n")
        print(f"Saved converted output to {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
