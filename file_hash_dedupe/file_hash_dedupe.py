#!/usr/bin/env python3
"""
CLI File Hash Generator & Duplicate File Finder

Computes cryptographic checksums (MD5, SHA256) for files and recursively
scans directories to detect duplicate files based on content hashes.
"""

import argparse
import hashlib
import os
import sys
from typing import Dict, List, Tuple


class FileHashDedupe:
    """Handles file hashing and directory deduplication."""

    @staticmethod
    def get_file_hash(filepath: str, algorithm: str = "sha256", chunk_size: int = 65536) -> str:
        """Compute hash checksum of a file efficiently using chunking."""
        hasher = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def find_duplicates(target_dir: str, algorithm: str = "sha256") -> Dict[str, List[str]]:
        """Find duplicate files in a directory tree."""
        hashes: Dict[str, List[str]] = {}

        for root, _, files in os.walk(target_dir):
            for file in files:
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path) and not os.path.islink(full_path):
                    try:
                        f_hash = FileHashDedupe.get_file_hash(full_path, algorithm)
                        hashes.setdefault(f_hash, []).append(full_path)
                    except (PermissionError, OSError):
                        continue

        # Return only hashes that match 2+ files
        return {h: paths for h, paths in hashes.items() if len(paths) > 1}


def main():
    parser = argparse.ArgumentParser(description="Compute file hashes & find duplicate files.")
    parser.add_argument("path", nargs="?", help="Target file or directory path")
    parser.add_argument("--algo", choices=["md5", "sha1", "sha256"], default="sha256", help="Hash algorithm")
    parser.add_argument("--dedupe", action="store_true", help="Scan directory for duplicate files")
    parser.add_argument("--delete", action="store_true", help="Delete duplicate files (keep first discovered)")

    args = parser.parse_args()

    if not args.path:
        print("Usage: python file_hash_dedupe.py <path> [--algo md5|sha256] [--dedupe] [--delete]")
        return

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if os.path.isfile(args.path):
        checksum = FileHashDedupe.get_file_hash(args.path, args.algo)
        print(f"[{args.algo.upper()}] {args.path}: {checksum}")

    elif os.path.isdir(args.path):
        if args.dedupe:
            print(f"Scanning '{args.path}' for duplicate files using {args.algo.upper()}...")
            dupes = FileHashDedupe.find_duplicates(args.path, args.algo)

            if not dupes:
                print("No duplicate files found.")
                return

            print(f"\nFound {len(dupes)} set(s) of duplicate files:\n")
            for h, paths in dupes.items():
                print(f"Hash: {h[:16]}... ({len(paths)} copies)")
                for p in paths:
                    print(f"  - {p}")

                if args.delete:
                    # Keep first, remove others
                    for p in paths[1:]:
                        os.remove(p)
                        print(f"    [DELETED] {p}")
        else:
            print(f"Directory specified. Pass --dedupe to scan '{args.path}' for duplicate files.")


if __name__ == "__main__":
    main()
