<div align="center">

# 🗂️ Folder-Structure-Finder

**Turn any project directory into a clean, AI-ready tree in one click.**
Paste it into ChatGPT, Claude, or your CLI agent so it finally understands your codebase.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)
![Interface](https://img.shields.io/badge/interface-GUI%20%2B%20CLI-orange)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## Why this exists

LLMs can't see your project structure, and running `tree` dumps `node_modules`, `.git`, and caches that waste your context window. **Folder-Structure-Finder** scans a directory, filters the junk, and exports a compact `project_structure.txt` with file, line, and size stats, ready to paste into any AI tool.

```text
my-project/
├── 📁 src/
│   ├── 📁 utils/
│   │   └── helpers.py
│   ├── app.py
│   └── config.py
├── 📁 tests/
│   └── test_app.py
└── README.md

Folders: 3 | Files: 5 | Lines: 1,284 | Size: 86.4 KB
```

## Features

- 🖥️ **GUI and CLI:** Tkinter interface by default, scriptable CLI with `--cli`
- 🌳 **Clean Unicode tree:** folders first, alphabetical, deterministic output
- 🧹 **Smart ignoring:** sensible defaults plus custom `--ignore` patterns
- 📏 **Depth control:** keep prompts small with `--max-depth`
- 📊 **Stats:** counts files, folders, lines (text files), and sizes
- 🔒 **Symlink-safe:** the scan never escapes the root directory
- 💾 **Portable output:** saves next to the executable or in the current directory
- 📦 **Zero dependencies:** pure Python standard library

## Quick start

```bash
git clone https://github.com/<your-username>/Folder-Structure-Finder.git
cd Folder-Structure-Finder
python main.py                                  # launch the GUI
python main.py --cli --path . --max-depth 3     # or use the CLI
python main.py --cli --path . --ignore dist --ignore "*.log"
```

| Flag | Description |
|---|---|
| `--cli` | Run without the GUI |
| `--path <dir>` | Directory to scan |
| `--max-depth <n>` | Maximum depth to display |
| `--ignore <pattern>` | Extra pattern to skip (repeatable) |

## Project structure

```text
main.py            Entry point: routes to GUI or CLI
scanner.py         Safe directory walk, ignore rules, file/line/size counting
formatter.py       Unicode tree rendering, stats, generate_report()
ui.py              Tkinter GUI
app_paths.py       Output paths (executable- and CWD-aware)
backendOption.py   Options and helpers
test.py            Tests
```

## Engineering highlights

- **Security-minded traversal:** blocks symlinks that point outside the root, avoiding path escapes and circular loops.
- **One backend, two frontends:** GUI and CLI share the same core, so behavior never drifts.
- **Separation of concerns:** the scanner knows nothing about presentation; the formatter knows nothing about the filesystem.
- **Self-aware:** automatically ignores its own report and source files.

## Testing

```bash
python test.py
```

## Roadmap

- [ ] JSON / Markdown export
- [ ] `.gitignore`-aware filtering
- [ ] Copy-to-clipboard button
- [ ] LLM token-count estimate

## Contributing

Issues and pull requests are welcome. Fork the repo, create a feature branch, and open a PR.

## License

MIT. See `LICENSE`.

<div align="center">

**If this saved you time, give it a ⭐**

</div>
