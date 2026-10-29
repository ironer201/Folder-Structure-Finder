<div align="center">

# 🗂️ Folder-Structure-Finder

**Turn any project directory into a clean, AI-ready tree in one click.**
Paste it into ChatGPT, Claude, or your CLI agent so it finally understands your codebase.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)
![Interface](https://img.shields.io/badge/interface-GUI%20%2B%20CLI-orange)
![License](https://img.shields.io/badge/license-MIT-green)
[![Release](https://img.shields.io/github/v/release/ironer201/Folder-Structure-Finder)](https://github.com/ironer201/Folder-Structure-Finder/releases/latest)
![Downloads](https://img.shields.io/github/downloads/ironer201/Folder-Structure-Finder/total)

<a href="https://github.com/ironer201/Folder-Structure-Finder/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/DOWNLOAD_NOW-Windows_%7C_Linux-2ea44f?style=for-the-badge&logo=github&logoColor=white" height="60" alt="Download Folder-Structure-Finder"></a>

[**🚀 Quick start**](#quick-start) · [**✨ Features**](#features) · [**📦 Releases**](https://github.com/ironer201/Folder-Structure-Finder/releases)

<img src="assets/screenshot.png" alt="Folder-Structure-Finder screenshot" width="700">

</div>

---

## Why this exists

LLMs can't see your project structure, and running `tree` dumps `node_modules`, `.git`, and caches that waste your context window. **Folder-Structure-Finder** scans a directory, filters the junk, and exports a compact `project_structure.txt` with file, line, and size stats, ready to paste into any AI tool.

```text
Python Project/
├── .gitignore
├── app_paths.py 
├── backendOption.py
├── formatter.py
├── main.py
├── ReadME.md
├── scanner.py
├── ui.py
├── README.md
└── windows.txt


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

## ⬇️ Download (no Python needed)

Ready-to-run executables for **Windows** and **Linux** are available on the release page:

<p align="center"><a href="https://github.com/ironer201/Folder-Structure-Finder/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/DOWNLOAD_NOW-Windows_%7C_Linux-2ea44f?style=for-the-badge&logo=github&logoColor=white" height="60" alt="Download Folder-Structure-Finder"></a></p>

| Platform | How to run |
|---|---|
| 🪟 **Windows** | Download the `.exe` and double-click it. If SmartScreen warns you, click *More info → Run anyway* (the app is unsigned). |
| 🐧 **Linux** | Download the file, then run `chmod +x <file>` and `./<file>` |

Prefer running from source? See [Quick start](#quick-start) below.

## Quick start

```bash
git clone https://github.com/ironer201/Folder-Structure-Finder.git
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
