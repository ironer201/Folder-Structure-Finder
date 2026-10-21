"""
main.py

Entry point for the folder-structure scanner tool.

Running with no arguments launches the Tkinter UI (ui.py).
Use --cli to run the command-line interface instead.
"""

import argparse
import sys

sys.dont_write_bytecode = True

from pathlib import Path

from scanner import Scanner
from formatter import render_tree, generate_report, print_tree


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Scan a user-specified folder and generate an AI-friendly project structure. "
            "The folder to scan must be provided explicitly."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 main.py                 # launch the UI\n"
            "  python3 main.py --cli --path /path/to/folder\n"
            "  python3 main.py --cli --path /path/to/folder --max-depth 2\n"
            "  python3 main.py --cli --path . --ignore *.log temp/\n"
            "  python3 main.py --cli --path ~/project --output my_structure.txt\n"
        ),
    )
    parser.add_argument(
        "--path",
        "-p",
        dest="scan_path",
        default=None,
        metavar="DIR",
        help="Directory to scan (required in CLI mode).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        metavar="N",
        help="Limit recursion depth (root = depth 0).",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        metavar="PATTERN",
        help="Extra folder/file names or wildcard patterns to skip.",
    )
    parser.add_argument(
        "--no-sizes",
        action="store_true",
        help="Hide file sizes from the tree.",
    )
    parser.add_argument(
        "--no-lines",
        action="store_true",
        help="Hide line counts from the tree.",
    )
    parser.add_argument(
        "--output",
        default="project_structure.txt",
        metavar="FILE",
        help="Output filename (default: project_structure.txt).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        metavar="DIR",
        help="Directory to save output (defaults to parent of scanned folder or user home).",
    )
    return parser.parse_args(argv)


def run_cli(argv=None) -> int:
    """Run the command-line interface."""
    args = parse_args(argv)

    # Determine the project root from user input - never from script location
    if args.scan_path:
        project_root = Path(args.scan_path).expanduser().resolve()
    else:
        print("[error] CLI mode requires --path to specify the folder to scan.")
        print("Use 'python3 main.py --cli --path /path/to/folder' or launch UI without --cli.")
        return 1

    if not project_root.exists():
        print(f"[error] Folder not found: {project_root}")
        return 1
    if not project_root.is_dir():
        print(f"[error] Not a directory: {project_root}")
        return 1

    project_name = project_root.name or "Project"

    print(f"Scanning: {project_root}")
    print(f"Ignoring: default patterns + {args.ignore if args.ignore else 'none'}")
    if args.max_depth is not None:
        print(f"Max depth: {args.max_depth}")
    print()

    # Run the scanner
    try:
        scanner = Scanner(
            root=project_root,
            max_depth=args.max_depth,
            extra_ignore=args.ignore,
            output_file=args.output,
        )
        root_info = scanner.scan()
        stats = scanner.get_stats()
    except Exception as e:
        print(f"[error] Scan failed: {e}")
        return 1

    # Render the tree
    show_sizes = not args.no_sizes
    show_lines = not args.no_lines
    tree_text = render_tree(root_info, show_sizes=show_sizes, show_lines=show_lines)

    # Print to stdout
    print_tree(tree_text, stats)

    # Generate and save the text report
    report_content = generate_report(tree_text, stats, project_name=project_name)

    # Determine output location
    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        # Save the report in the folder the program is in
        output_dir = Path.cwd()

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[error] Could not create output directory {output_dir}: {e}")
        return 1

    output_path = output_dir / args.output

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\nReport saved to: {output_path}")
    except PermissionError:
        print(f"\n[error] Permission denied while writing to {output_path}")
        print("Try choosing a different output location or check permissions.")
        return 1
    except FileNotFoundError:
        print(f"\n[error] Folder not found for output: {output_dir}")
        return 1
    except OSError as e:
        print(f"\n[error] Could not write report to {output_path}: {e}")
        return 1

    return 0


def run_gui() -> int:
    """Launch the Tkinter UI (ui.py)."""
    try:
        import tkinter as tk
        from ui import ScannerUI
    except ImportError as e:
        print(f"[error] Could not start the UI: {e}")
        print("Run 'python3 main.py --cli' for the command-line interface.")
        return 1

    root = tk.Tk()
    ScannerUI(root)
    root.mainloop()
    return 0


def main(argv=None) -> int:
    """Main entry point: UI by default, CLI when --cli is given."""
    argv = list(sys.argv[1:] if argv is None else argv)

    if any(a in ("--cli", "-c") for a in argv):
        argv = [a for a in argv if a not in ("--cli", "-c")]
        return run_cli(argv)

    return run_gui()


if __name__ == "__main__":
    sys.exit(main())