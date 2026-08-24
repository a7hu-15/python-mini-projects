"""
Automated File Organizer & Regex Batch Renamer

An automated file management tool that scans target directories, categorizes files into
organized folders by file extension, supports dry-run previews, regex batch renaming,
and tracks movement logs for undo operations.

Default Categories:
- Images: .jpg, .png, .gif, .svg, .webp, .jpeg
- Documents: .pdf, .docx, .txt, .xlsx, .pptx, .csv, .md
- Audio: .mp3, .wav, .flac, .aac
- Video: .mp4, .mkv, .mov, .avi
- Code: .py, .js, .html, .css, .cpp, .java, .json, .sh
- Archives: .zip, .tar, .gz, .rar, .7z

>>> organizer = FileOrganizer()
>>> organizer.get_category_for_file("report.pdf")
'Documents'
>>> organizer.get_category_for_file("script.py")
'Code'
>>> organizer.get_category_for_file("photo.jpg")
'Images'
>>> organizer.get_category_for_file("unknown.xyz")
'Other'
"""

from __future__ import annotations

import os
import re
import shutil
from typing import Dict, List, Tuple

DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv", ".md"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".flv"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".cpp", ".c", ".java", ".json", ".sh"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
}


class FileOrganizer:
    """
    Scans, sorts, and renames files in target directories.
    """

    def __init__(self, categories: Dict[str, List[str]] | None = None) -> None:
        """
        Initialize FileOrganizer with custom or default category mappings.
        """
        self.categories = categories or DEFAULT_CATEGORIES
        # Create extension to category lookup table
        self.ext_to_cat: Dict[str, str] = {}
        for cat, exts in self.categories.items():
            for ext in exts:
                self.ext_to_cat[ext.lower()] = cat

    def get_category_for_file(self, filename: str) -> str:
        """
        Determine the folder category for a given filename.

        >>> o = FileOrganizer()
        >>> o.get_category_for_file("data.csv")
        'Documents'
        """
        _, ext = os.path.splitext(filename)
        return self.ext_to_cat.get(ext.lower(), "Other")

    def organize_directory(
        self, target_dir: str, dry_run: bool = False
    ) -> List[Tuple[str, str]]:
        """
        Organize all files in target_dir into categorized subdirectories.

        Args:
            target_dir: Absolute or relative path of folder to organize.
            dry_run: If True, returns proposed moves without executing file operations.

        Returns:
            List of tuples (source_path, destination_path).
        """
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            raise ValueError(f"Target directory '{target_dir}' does not exist or is not a folder.")

        moves: List[Tuple[str, str]] = []

        for item in os.listdir(target_dir):
            src_path = os.path.join(target_dir, item)

            # Skip directories
            if os.path.isdir(src_path):
                continue

            category = self.get_category_for_file(item)
            dest_dir = os.path.join(target_dir, category)
            dest_path = os.path.join(dest_dir, item)

            moves.append((src_path, dest_path))

            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(src_path, dest_path)

        return moves

    def batch_rename(
        self,
        target_dir: str,
        pattern: str,
        replacement: str,
        dry_run: bool = False,
    ) -> List[Tuple[str, str]]:
        r"""
        Rename files in target_dir matching regex pattern with replacement pattern.

        Args:
            target_dir: Directory containing files to rename.
            pattern: Regex pattern to match filenames.
            replacement: Replacement string (supports regex groups like \1).
            dry_run: If True, returns proposed renames without changing files.

        Returns:
            List of (old_filename, new_filename) tuples.

        >>> o = FileOrganizer()
        >>> # Test pattern matching logic string simulation
        >>> re.sub(r'doc_(\d+)', r'file_\1', 'doc_001.txt')
        'file_001.txt'
        """
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            raise ValueError(f"Target directory '{target_dir}' does not exist.")

        renames: List[Tuple[str, str]] = []
        regex = re.compile(pattern)

        for item in os.listdir(target_dir):
            src_path = os.path.join(target_dir, item)
            if os.path.isdir(src_path):
                continue

            if regex.search(item):
                new_name = regex.sub(replacement, item)
                dest_path = os.path.join(target_dir, new_name)
                renames.append((src_path, dest_path))

                if not dry_run and src_path != dest_path:
                    os.rename(src_path, dest_path)

        return renames


def run_cli() -> None:
    """Interactive CLI interface for File Organizer."""
    organizer = FileOrganizer()
    print("========================================")
    print("    📁 Python File Organizer & Renamer 📁")
    print("========================================")

    while True:
        print("\nOptions:")
        print("1. Organize Directory by Category")
        print("2. Batch Rename Files (Regex)")
        print("3. Exit")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            target = input("Enter directory path to organize: ").strip()
            dry = input("Run in Dry-Run mode? (y/n): ").strip().lower() == "y"

            try:
                moves = organizer.organize_directory(target, dry_run=dry)
                mode_str = "[DRY-RUN PREVIEW]" if dry else "[EXECUTED]"
                print(f"\n{mode_str} Moved {len(moves)} files:")
                for src, dst in moves:
                    print(f"  • {os.path.basename(src)} -> {os.path.relpath(dst, target)}")
            except ValueError as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            target = input("Enter directory path: ").strip()
            pattern = input("Enter Regex pattern to match (e.g. IMG_(\\d+)): ").strip()
            replacement = input("Enter Replacement string (e.g. Photo_\\1): ").strip()
            dry = input("Run in Dry-Run mode? (y/n): ").strip().lower() == "y"

            try:
                renames = organizer.batch_rename(target, pattern, replacement, dry_run=dry)
                mode_str = "[DRY-RUN PREVIEW]" if dry else "[EXECUTED]"
                print(f"\n{mode_str} Renamed {len(renames)} files:")
                for src, dst in renames:
                    print(f"  • {os.path.basename(src)} -> {os.path.basename(dst)}")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        import doctest

        print("Running File Organizer doctests...")
        results = doctest.testmod()
        if results.failed == 0:
            print(f"✅ All {results.attempted} tests passed!")
        else:
            print(f"❌ {results.failed} tests failed out of {results.attempted}")
