"""
formatter.py

Tree rendering, statistics, and Markdown report generation.
No per-file sizes or line counts are shown in the tree.
"""

from pathlib import Path
from typing import Dict, List, Optional

from backendOption import ScanOptions, display_name
from scanner import DirInfo, FileInfo, human_readable_size


def render_tree(
    root: DirInfo,
    options: Optional[ScanOptions] = None,
    show_sizes: bool = False,
    show_lines: bool = False,
) -> str:
    """
    Render a Unicode tree of the directory structure.
    Folders are listed first, then files, both sorted alphabetically.
    No sizes or line counts are shown.

    ``show_sizes`` and ``show_lines`` are accepted for backward
    compatibility with existing callers; the tree intentionally never
    displays per-file sizes or line counts.
    """
    options = options or ScanOptions()
    lines: List[str] = []
    lines.append(display_name(root.name, options) + "/")

    dir_children = sorted(
        [(True, d.name, d) for d in root.dirs], key=lambda x: x[1].lower()
    )
    file_children = sorted(
        [(False, f.name, f) for f in root.files], key=lambda x: x[1].lower()
    )
    if options.files_per_folder is not None:
        file_children = file_children[: options.files_per_folder]

    _render_children(dir_children + file_children, "", lines, options)
    return "\n".join(lines)


def _render_children(
    children: List[tuple],
    prefix: str,
    lines: List[str],
    options: ScanOptions,
) -> None:
    """Recursively render children with proper tree connectors."""
    for i, (is_dir, name, obj) in enumerate(children):
        is_last = i == len(children) - 1
        connector = "└── " if is_last else "├── "
        extension = "/" if is_dir else ""
        label = display_name(name, options) + extension
        lines.append(f"{prefix}{connector}{label}")

        if is_dir:
            sub_dirs = sorted(
                [(True, d.name, d) for d in obj.dirs], key=lambda x: x[1].lower()
            )
            sub_files = sorted(
                [(False, f.name, f) for f in obj.files], key=lambda x: x[1].lower()
            )
            if options.files_per_folder is not None:
                sub_files = sub_files[: options.files_per_folder]
            sub_children = sub_dirs + sub_files

            new_prefix = prefix + ("    " if is_last else "│   ")
            _render_children(sub_children, new_prefix, lines, options)


def format_stats(stats: Dict[str, object]) -> str:
    """Format the summary statistics as a readable string."""
    lines = [
        "Summary:",
        f"  Total folders : {stats['total_folders']}",
        f"  Total files   : {stats['total_files']}",
        f"  Total lines   : {stats['total_lines']}",
        f"  Total size    : {stats['total_size_human']}",
    ]
    return "\n".join(lines)


def generate_report(
    tree_text: str,
    stats: Dict[str, object],
    project_name: str = "Project Structure",
) -> str:
    """
    Generate a plain-text report with a title, stats, and the tree.
    Ready to paste directly into an AI chat.
    """
    header = project_name
    separator = "=" * len(header)
    txt_lines = [
        header,
        separator,
        "",
        "Statistics",
        "----------",
        f"Total folders : {stats['total_folders']}",
        f"Total files   : {stats['total_files']}",
        f"Total lines   : {stats['total_lines']}",
        f"Total size    : {stats['total_size_human']}",
        "",
        "Directory Tree",
        "--------------",
        "",
        tree_text,
        "",
    ]
    return "\n".join(txt_lines)


def print_tree(
    tree_text: str,
    stats: Dict[str, object],
) -> None:
    """Print the tree and stats to stdout."""
    print(tree_text)
    print()
    print(format_stats(stats))