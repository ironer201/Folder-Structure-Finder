"""Backend settings for the scanner UI modes."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScanOptions:
    """Presentation options applied after the complete tree is scanned."""

    files_per_folder: Optional[int] = None
    truncate_names: bool = False
    max_name_length: int = 9


MODE_ALL = "all"
MODE_FIRST_3 = "first_3"
MODE_FIRST_1 = "first_1"
MODE_ALL_SHORT_NAMES = "all_short_names"


def options_for_mode(mode: str) -> ScanOptions:
    """Return the backend settings for a UI scan mode."""
    options = {
        MODE_ALL: ScanOptions(),
        MODE_FIRST_3: ScanOptions(files_per_folder=3),
        MODE_FIRST_1: ScanOptions(files_per_folder=1),
        MODE_ALL_SHORT_NAMES: ScanOptions(truncate_names=True),
    }
    try:
        return options[mode]
    except KeyError as exc:
        raise ValueError(f"Unknown scan mode: {mode}") from exc


def display_name(name: str, options: ScanOptions) -> str:
    """Shorten a displayed name while keeping the configured suffix."""
    if not options.truncate_names or len(name) <= options.max_name_length:
        return name
    if options.max_name_length <= 3:
        raise ValueError("max_name_length must be greater than 3")
    return name[: options.max_name_length - 3] + "..."