#!/usr/bin/env python3
"""
CLI JSON & Config Merger & Structural Diff Tool

Utility to recursively deep-merge multiple JSON configuration files, perform environment
variable substitution, and generate key structural difference reports between configuration files.
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Any, Tuple, Optional

class ConfigMerger:
    """Handles recursive deep merging of dictionary-based configurations."""

    @staticmethod
    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.
        Override values overwrite base values unless both are dictionaries,
        in which case they are merged recursively.
        """
        result = dict(base)
        for key, val in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = ConfigMerger.deep_merge(result[key], val)
            else:
                result[key] = val
        return result

    @staticmethod
    def substitute_env_vars(data: Any) -> Any:
        """
        Recursively substitute environment variables in string values formatted as ${VAR_NAME:default_value} or ${VAR_NAME}.
        """
        if isinstance(data, dict):
            return {k: ConfigMerger.substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [ConfigMerger.substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            pattern = re.compile(r"\$\{([A-Za-z0-9_]+)(?::([^}]+))?\}")

            def replacer(match):
                var_name = match.group(1)
                default_val = match.group(2) if match.group(2) is not None else ""
                return os.environ.get(var_name, default_val)

            return pattern.sub(replacer, data)
        return data

    @staticmethod
    def compute_diff(dict1: Dict[str, Any], dict2: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
        """
        Compare two dicts and return structural differences (added, removed, modified keys).
        """
        diffs = []
        all_keys = set(dict1.keys()).union(set(dict2.keys()))

        for key in sorted(all_keys):
            curr_path = f"{path}.{key}" if path else key
            if key not in dict1:
                diffs.append({"type": "ADDED", "path": curr_path, "new_val": dict2[key]})
            elif key not in dict2:
                diffs.append({"type": "REMOVED", "path": curr_path, "old_val": dict1[key]})
            else:
                v1, v2 = dict1[key], dict2[key]
                if isinstance(v1, dict) and isinstance(v2, dict):
                    diffs.extend(ConfigMerger.compute_diff(v1, v2, curr_path))
                elif v1 != v2:
                    diffs.append({"type": "MODIFIED", "path": curr_path, "old_val": v1, "new_val": v2})

        return diffs


def main():
    parser = argparse.ArgumentParser(description="Merge JSON config files & compute structural diffs.")
    parser.add_argument("files", nargs="*", help="JSON config files to merge in priority order (left to right)")
    parser.add_argument("--diff", nargs=2, help="Compare two JSON config files and display structural key differences")
    parser.add_argument("--output", "-o", help="Write merged output to JSON file")
    parser.add_argument("--no-env", action="store_true", help="Disable environment variable substitution")

    args = parser.parse_args()

    if args.diff:
        file1, file2 = args.diff
        if not os.path.exists(file1) or not os.path.exists(file2):
            print("Error: Both diff input files must exist.", file=sys.stderr)
            sys.exit(1)
        with open(file1, "r", encoding="utf-8") as f:
            d1 = json.load(f)
        with open(file2, "r", encoding="utf-8") as f:
            d2 = json.load(f)

        diffs = ConfigMerger.compute_diff(d1, d2)
        print(f"--- Config Differences ({file1} -> {file2}) ---")
        if not diffs:
            print("No differences found. Configurations are identical.")
        else:
            for diff in diffs:
                t = diff["type"]
                p = diff["path"]
                if t == "ADDED":
                    print(f"[+] {p}: {json.dumps(diff['new_val'])}")
                elif t == "REMOVED":
                    print(f"[-] {p}: {json.dumps(diff['old_val'])}")
                elif t == "MODIFIED":
                    print(f"[~] {p}: {json.dumps(diff['old_val'])} -> {json.dumps(diff['new_val'])}")
        return

    if not args.files:
        # Demo mode
        base_cfg = {"app": {"name": "DemoApp", "port": 8080}, "debug": False}
        override_cfg = {"app": {"port": 9000, "host": "localhost"}, "debug": True}
        merged = ConfigMerger.deep_merge(base_cfg, override_cfg)
        print("--- Demo Config Deep Merge ---")
        print(json.dumps(merged, indent=2))
        return

    merged_config: Dict[str, Any] = {}
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Warning: File '{file_path}' not found, skipping.", file=sys.stderr)
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
            merged_config = ConfigMerger.deep_merge(merged_config, content)

    if not args.no_env:
        merged_config = ConfigMerger.substitute_env_vars(merged_config)

    output_str = json.dumps(merged_config, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str + "\n")
        print(f"Merged configuration saved to {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
