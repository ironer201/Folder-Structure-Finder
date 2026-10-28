"""
ui.py

Simple Tkinter UI for the folder-structure scanner tool.

UI style:
    * The scan modes are shown as a vertical list of BUTTONS.
    * Navigate between the mode buttons with the Up / Down arrow keys.
    * Press Enter (or Space) to activate the highlighted mode button,
      which then triggers the scan with that mode selected.
    * The action button "Press Enter to see file structure" also runs the scan.

Scan modes:
    * Scan All folder, sub folder and Files
    * Scan only the folder and first 3 files only of every folder and sub folder
    * Scan only the folder and first 1 file only of every folder and sub folder

Run with:  python3 ui.py
Requires:  scanner.py and formatter.py in the same folder.
"""

import sys
import threading
import tkinter as tk 
from tkinter import font as tkfont

sys.dont_write_bytecode = True

from pathlib import Path

from app_paths import app_dir
from backendOption import (
    MODE_ALL,
    MODE_ALL_SHORT_NAMES,
    MODE_FIRST_1,
    MODE_FIRST_3,
    options_for_mode,
)
from scanner import Scanner
from formatter import render_tree, generate_report


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_OUTPUT = "project_structure.txt"   # .txt report as requested
WINDOW_TITLE = "Project Structure Scanner"
WINDOW_SIZE = "720x620"
BG_COLOR = "#1e1e2e"
FG_COLOR = "#e0e0e0"
SUBTLE_FG = "#a6adc8"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
BTN_ACTIVE_BG = "#74a8fc"
STATUS_LOADING = "#f9e2af"   # yellow
STATUS_OK = "#a6e3a1"        # green
STATUS_ERR = "#f38ba8"       # red

# Mode-button styling
MODE_BTN_BG = "#313244"          # idle background
MODE_BTN_FG = "#cdd6f4"          # idle foreground
MODE_BTN_HOVER_BG = "#45475a"    # hover background
MODE_BTN_SELECTED_BG = "#89b4fa" # selected background
MODE_BTN_SELECTED_FG = "#1e1e2e" # selected foreground
MODE_BTN_ACTIVE_BG = "#74a8fc"   # click flash

class ScannerUI:
    """Tkinter UI wrapper for the folder-structure scanner."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)

        # Scan target: the folder the app is currently running in
        self.project_root = Path.cwd()
        self.output_file = DEFAULT_OUTPUT
        # Report is saved next to the executable when frozen, else in the CWD
        self.output_dir = app_dir()

        # Guard so the user can't launch multiple scans at once
        self.is_scanning = False

        # Selected scan mode (default: scan everything)
        self.scan_mode = MODE_ALL
        self.scan_options = options_for_mode(self.scan_mode)

        # Ordered list of mode definitions: (mode_id, label)
        self.mode_definitions = [
            (MODE_ALL, "Scan All folder, sub folder and Files"),
            (
                MODE_FIRST_3,
                "Scan only the folder and first 3 files only "
                "of every folder and sub folder",
            ),
            (
                MODE_FIRST_1,
                "Scan only the folder and first 1 file only "
                "of every folder and sub folder",
            ),
            (
                MODE_ALL_SHORT_NAMES,
                "Scan all the folder and sub folder but shorten long names",
            ),
        ]

        # Will hold the created mode buttons (in order)
        self.mode_buttons = []
        # Index of the currently highlighted mode button
        self.selected_index = 0

        self._build_widgets()
        self._bind_keys()

        # Set initial highlight
        self._update_mode_highlight()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_widgets(self):
        """Create all widgets and lay them out."""
        title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        btn_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        status_font = tkfont.Font(family="Helvetica", size=14)
        section_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        mode_font = tkfont.Font(family="Helvetica", size=14)

        # Title
        self.title_label = tk.Label(
            self.root,
            text="Folder Structure Scanner",
            font=title_font,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        self.title_label.pack(pady=(18, 6))

        # Subtitle / hint
        self.hint_label = tk.Label(
            self.root,
            text=f"Scan target: {self.project_root}",
            font=("Helvetica", 9),
            bg=BG_COLOR,
            fg=SUBTLE_FG,
            wraplength=580,
            justify="center",
        )
        self.hint_label.pack(pady=(0, 10))

        # Output info label
        self.output_info_label = tk.Label(
            self.root,
            text=f"Output: {self.output_dir / DEFAULT_OUTPUT}",
            font=("Helvetica", 9),
            bg=BG_COLOR,
            fg=SUBTLE_FG,
            wraplength=580,
            justify="center",
        )
        self.output_info_label.pack(pady=(0, 10))

        # ------------------------------------------------------------------
        # Scan mode section (button list)
        # ------------------------------------------------------------------
        self.mode_frame = tk.LabelFrame(
            self.root,
            text=" Scan Mode  (↑ ↓ to navigate, Enter to select) ",
            font=section_font,
            bg=BG_COLOR,
            fg=FG_COLOR,
            labelanchor="nw",
            bd=1,
            relief="groove",
            padx=12,
            pady=10,
        )
        self.mode_frame.pack(fill="x", padx=24, pady=(0, 10))

        for index, (mode_id, label) in enumerate(self.mode_definitions):
            btn = tk.Button(
                self.mode_frame,
                text=label,
                font=mode_font,
                bg=MODE_BTN_BG,
                fg=MODE_BTN_FG,
                activebackground=MODE_BTN_ACTIVE_BG,
                activeforeground=MODE_BTN_SELECTED_FG,
                relief="flat",
                anchor="w",
                justify="left",
                wraplength=520,
                padx=10,
                pady=8,
                cursor="hand2",
                takefocus=True,
                command=lambda i=index: self._on_mode_clicked(i),
            )
            btn.pack(fill="x", pady=3)

            # Hover effects
            btn.bind(
                "<Enter>",
                lambda event, i=index: self._on_mode_hover(i, True),
            )
            btn.bind(
                "<Leave>",
                lambda event, i=index: self._on_mode_hover(i, False),
            )
            # Focus tracking so arrow keys know where we are
            btn.bind(
                "<FocusIn>",
                lambda event, i=index: self._set_selected_index(i),
            )

            self.mode_buttons.append(btn)

        # ------------------------------------------------------------------
        # Action button
        # ------------------------------------------------------------------
        self.scan_button = tk.Button(
            self.root,
            text="Press Enter to see file structure",
            font=btn_font,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_ACTIVE_BG,
            activeforeground=BTN_FG,
            relief="flat",
            padx=20,
            pady=12,
            cursor="hand2",
            command=self.start_scan,
        )
        self.scan_button.pack(pady=(8, 6))

        # Status label
        self.status_label = tk.Label(
            self.root,
            text="",
            font=status_font,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=580,
            justify="center",
        )
        self.status_label.pack(pady=(10, 8))

    def _bind_keys(self):
        """Bind global keys (arrow navigation + Enter)."""
        # Arrow navigation across the mode buttons
        self.root.bind("<Up>", lambda event: self._move_selection(-1))
        self.root.bind("<Down>", lambda event: self._move_selection(1))
        self.root.bind("<Left>", lambda event: self._move_selection(-1))
        self.root.bind("<Right>", lambda event: self._move_selection(1))

        # Activate the highlighted mode button with Enter/Space
        self.root.bind("<Return>", lambda event: self._activate_selected_mode())
        self.root.bind("<KP_Enter>", lambda event: self._activate_selected_mode())
        self.root.bind("<space>", lambda event: self._activate_selected_mode())

    # ------------------------------------------------------------------
    # Mode-button navigation
    # ------------------------------------------------------------------
    def _set_selected_index(self, index: int):
        """Set the highlighted index and refresh button colors."""
        if index < 0 or index >= len(self.mode_buttons):
            return
        self.selected_index = index
        self._update_mode_highlight()

    def _move_selection(self, delta: int):
        """Move highlight up (-1) or down (+1) and focus that button."""
        if not self.mode_buttons:
            return
        new_index = (self.selected_index + delta) % len(self.mode_buttons)
        self.selected_index = new_index
        self._update_mode_highlight()
        self.mode_buttons[new_index].focus_set()

    def _activate_selected_mode(self):
        """
        Apply the currently highlighted mode, then run the scan.

        This makes Enter behave like pressing the highlighted button.
        """
        if self.is_scanning:
            return
        self._apply_mode(self.selected_index)
        self.start_scan()

    def _on_mode_clicked(self, index: int):
        """Mouse click on a mode button: highlight it and apply the mode."""
        self._set_selected_index(index)
        self._apply_mode(index)

    def _on_mode_hover(self, index: int, entering: bool):
        """Change button background on hover (unless it's the selected one)."""
        if index == self.selected_index:
            return
        btn = self.mode_buttons[index]
        btn.config(bg=MODE_BTN_HOVER_BG if entering else MODE_BTN_BG)

    def _update_mode_highlight(self):
        """Apply the selected/idle colors to every mode button."""
        for i, btn in enumerate(self.mode_buttons):
            if i == self.selected_index:
                btn.config(
                    bg=MODE_BTN_SELECTED_BG,
                    fg=MODE_BTN_SELECTED_FG,
                    activebackground=MODE_BTN_ACTIVE_BG,
                    activeforeground=MODE_BTN_SELECTED_FG,
                )
            else:
                btn.config(
                    bg=MODE_BTN_BG,
                    fg=MODE_BTN_FG,
                    activebackground=MODE_BTN_ACTIVE_BG,
                    activeforeground=MODE_BTN_SELECTED_FG,
                )

    def _apply_mode(self, index: int):
        """Store the selected mode and its backend presentation settings."""
        if 0 <= index < len(self.mode_definitions):
            self.scan_mode = self.mode_definitions[index][0]
            self.scan_options = options_for_mode(self.scan_mode)

    # ------------------------------------------------------------------
    # Scan control
    # ------------------------------------------------------------------
    def start_scan(self):
        """Kick off the scan in a background thread (keeps the UI responsive)."""
        if self.is_scanning:
            return

        self.is_scanning = True
        self.scan_button.config(state="disabled")
        for btn in self.mode_buttons:
            btn.config(state="disabled")
        self.set_status("Loading...", STATUS_LOADING)

        thread = threading.Thread(target=self._run_scan, daemon=True)
        thread.start()

    def _run_scan(self):
        """Background worker: run the scanner and write the report file."""
        try:
            scanner = Scanner(
                root=self.project_root,
                max_depth=None,
                extra_ignore=None,
                output_file=self.output_file,
            )
            root_info = scanner.scan()
            stats = scanner.get_stats()

            tree_text = render_tree(
                root_info,
                show_sizes=True,
                show_lines=True,
                options=self.scan_options,
            )
            report_content = generate_report(
                tree_text, stats, project_name=self.project_root.name or "Project"
            )

            # Determine output directory (default: the program's own folder)
            try:
                if self.output_dir:
                    output_dir = Path(self.output_dir).expanduser().resolve()
                else:
                    output_dir = app_dir()
            except Exception:
                output_dir = app_dir()

            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise OSError(f"Could not create output directory {output_dir}: {e}")

            output_path = output_dir / self.output_file
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
            except PermissionError as e:
                raise PermissionError(
                    f"Permission denied while writing to {output_path}. "
                    "Try selecting a different location or check permissions."
                ) from e
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Folder not found for output: {output_dir}") from e
            except OSError as e:
                raise OSError(f"Could not write report to {output_path}: {e}") from e

            self.root.after(0, lambda p=output_path: self._on_success(p))
        except Exception as exc:  # noqa: BLE001 - report any failure to the user
            self.root.after(0, lambda e=exc: self._on_error(e))

    def _on_success(self, output_path: Path):
        """Called when the report file was created successfully."""
        self.set_status(
            f"File structure saved to: {output_path}",
            STATUS_OK,
        )
        self._finish_scan()

    def _on_error(self, exc: Exception):
        """Called when the scan failed."""
        self.set_status(f"Error: {exc}", STATUS_ERR)
        self._finish_scan()

    def _finish_scan(self):
        """Re-enable the buttons so the user can scan again."""
        self.is_scanning = False
        self.scan_button.config(state="normal")
        for btn in self.mode_buttons:
            btn.config(state="normal")
        self._update_mode_highlight()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def set_status(self, text: str, color: str = FG_COLOR):
        """Update the status label text and color."""
        self.status_label.config(text=text, fg=color)


def main():
    """Create the Tk root and start the event loop."""
    root = tk.Tk()
    ScannerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()