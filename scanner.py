"""
scanner.py

Filesystem walking, safety checks, and file statistics collection.
Only scans within the current working directory (and subdirectories).
Never follows symlinks that resolve outside the root folder.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Default ignore list (folder/file names and wildcard patterns)
DEFAULT_IGNORE = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "build", "dist", "target",
    ".idea", ".vscode", ".cache", ".gradle", ".DS_Store", "Thumbs.db",
    "*.egg-info", "project_structure.txt", "project_structure.md",
    "formatter.py", "scanner.py", "main.py", "ui.py", "backendOption.py",
    "test.py", "*.spec",
}

# Extensions considered text/code files for line counting
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".sh",
    ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".md", ".rst", ".txt", ".tex", ".csv", ".tsv",
    ".sql", ".graphql", ".proto", ".dockerfile", ".makefile", ".cmake",
    ".gitignore", ".env", ".editorconfig", ".eslintrc", ".prettierrc",
    ".vue", ".svelte", ".elm", ".ex", ".exs", ".erl", ".hrl",
    ".lua", ".r", ".m", ".mm", ".pl", ".pm", ".tcl", ".vim",
    ".tf", ".hcl", ".sol", ".clj", ".cljs", ".cljc",
    ".gradle", ".properties", ".lock", ".log",
}


def human_readable_size(size_bytes: int) -> str:
    """Convert a byte count to a human-readable string (B/KB/MB/GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def count_lines(file_path: Path) -> Optional[int]:
    """
    Count lines in a text file. Returns None if the file is binary/unreadable.
    Uses a simple heuristic: read as UTF-8 with errors='replace'.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return None


def is_text_file(path: Path) -> bool:
    """Determine if a file is likely text/code based on its extension or name."""
    name_lower = path.name.lower()
    suffix = path.suffix.lower()

    # Check exact names first (e.g., Dockerfile, Makefile)
    if name_lower in {"dockerfile", "makefile", "cmakelists.txt", "rakefile",
                      "gemfile", "procfile", "vagrantfile"}:
        return True

    # Check extension
    if suffix in TEXT_EXTENSIONS:
        return True

    # Files with no extension but common text names
    if not suffix and name_lower not in {"", "."}:
        return True

    return False


def matches_ignore(name: str, ignore_patterns: Set[str]) -> bool:
    """Check if a name matches any ignore pattern (supports * wildcards)."""
    import fnmatch
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def is_safe_symlink(path: Path, root: Path) -> bool:
    try:
        real_target = Path(os.path.realpath(str(path)))
        real_root = Path(os.path.realpath(str(root)))
        return real_target == real_root or real_target.is_relative_to(real_root)
    except (OSError, ValueError):
        return False


class FileInfo:
    """Stores metadata about a single file."""
    __slots__ = ("path", "name", "size", "lines", "is_text")

    def __init__(self, path: Path, size: int, lines: Optional[int], is_text: bool):
        self.path = path
        self.name = path.name
        self.size = size
        self.lines = lines
        self.is_text = is_text


class DirInfo:
    """Stores metadata about a directory and its contents."""
    __slots__ = ("path", "name", "files", "dirs")

    def __init__(self, path: Path, name: str):
        self.path = path
        self.name = name
        self.files: List[FileInfo] = []
        self.dirs: List["DirInfo"] = []


class Scanner:
    """
    Walks a directory tree safely, collecting file and folder information.
    Guarantees no access outside the root folder.
    """

    def __init__(
        self,
        root: Optional[Path] = None,
        max_depth: Optional[int] = None,
        extra_ignore: Optional[List[str]] = None,
        output_file: str = "project_structure.txt",
        output_path: Optional[Path] = None,
    ):
        # Root must come from user input; do not fall back to script/temp location
        if root is None:
            raise ValueError("Scanner requires an explicit root directory to scan")
        self.root = Path(root).expanduser().resolve()
        self.max_depth = max_depth
        self.ignore_patterns = set(DEFAULT_IGNORE)
        if extra_ignore:
            self.ignore_patterns.update(extra_ignore)
        # Always ignore the output report file itself
        self.ignore_patterns.add(output_file)
        if output_path is not None:
            try:
                self.ignore_patterns.add(Path(output_path).name)
            except Exception:
                pass
        # Also ensure common patterns are ignored
        self.ignore_patterns.add("__pycache__")
        self.ignore_patterns.add(".git")
        self.ignore_patterns.add("build")
        self.ignore_patterns.add("dist")
        # Ignore any .spec files
        self.ignore_patterns.add("*.spec")

        # Stats
        self.total_folders = 0
        self.total_files = 0
        self.total_lines = 0
        self.total_size = 0

    def scan(self) -> DirInfo:
        """Entry point: scan the root folder and return a DirInfo tree."""
        root_info = DirInfo(self.root, self.root.name or str(self.root))
        self.total_folders = 1  # Count the root itself
        self._scan_dir(self.root, root_info, depth=0)
        return root_info

    def _scan_dir(self, path: Path, dir_info: DirInfo, depth: int) -> None:
        """
        Recursively scan a directory. Populates dir_info.dirs and dir_info.files.
        Skips items beyond max_depth, ignored items, and unsafe symlinks.
        """
        if self.max_depth is not None and depth >= self.max_depth:
            return

        try:
            entries = list(path.iterdir())
        except PermissionError:
            print(f"  [warning] Permission denied: {path}")
            return
        except OSError as e:
            print(f"  [warning] Cannot read {path}: {e}")
            return

        # Separate dirs and files, filter ignored
        subdirs: List[Path] = []
        files: List[Path] = []

        for entry in entries:
            name = entry.name
            if matches_ignore(name, self.ignore_patterns):
                continue

            try:
                if entry.is_symlink():
                    if not is_safe_symlink(entry, self.root):
                        print(f"  [warning] Skipping unsafe symlink: {entry}")
                        continue

                if entry.is_dir():
                    subdirs.append(entry)
                elif entry.is_file():
                    files.append(entry)
            except OSError as e:
                print(f"  [warning] Cannot stat {entry}: {e}")
                continue

        # Sort alphabetically (case-insensitive for consistency)
        subdirs.sort(key=lambda p: p.name.lower())
        files.sort(key=lambda p: p.name.lower())

        # Process files
        for file_path in files:
            file_info = self._process_file(file_path)
            if file_info:
                dir_info.files.append(file_info)

        # Process subdirectories recursively
        for subdir in subdirs:
            self.total_folders += 1
            sub_info = DirInfo(subdir, subdir.name)
            self._scan_dir(subdir, sub_info, depth + 1)
            dir_info.dirs.append(sub_info)

    def _process_file(self, file_path: Path) -> Optional[FileInfo]:
        """Gather size and line count for a single file."""
        try:
            size = file_path.stat().st_size
        except OSError as e:
            print(f"  [warning] Cannot stat file {file_path}: {e}")
            return None

        is_text = is_text_file(file_path)
        lines = None
        if is_text:
            lines = count_lines(file_path)
            if lines is not None:
                self.total_lines += lines

        self.total_files += 1
        self.total_size += size

        return FileInfo(file_path, size, lines, is_text)

    def get_stats(self) -> Dict[str, object]:
        """Return a dictionary of summary statistics."""
        return {
            "total_folders": self.total_folders,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "total_size": self.total_size,
            "total_size_human": human_readable_size(self.total_size),
        }