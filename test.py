import os
from pathlib import Path
from scanner import Scanner, is_safe_symlink, matches_ignore, DEFAULT_IGNORE

root = Path.cwd()
src = root / "src"
print("root       :", root)
print("src exists :", src.exists())
print("src is dir :", src.is_dir())
print("src symlink:", src.is_symlink())
print("safe?      :", is_safe_symlink(src, root) if src.is_symlink() else "n/a")
print("ignored?   :", matches_ignore("src", DEFAULT_IGNORE))

s = Scanner()
tree = s.scan()
def walk(d, depth=0):
    print("  " * depth + "[D] " + d.name)
    for f in d.files:
        print("  " * (depth + 1) + "[F] " + f.name)
    for sub in d.dirs:
        walk(sub, depth + 1)
walk(tree)