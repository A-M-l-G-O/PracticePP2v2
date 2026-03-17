# Finding files by extension, moving and copying between directories

import os
import shutil
from pathlib import Path

demo = Path("demo_workspace")
demo.mkdir(exist_ok=True)

sample_files = {
    "report.txt": "Annual report content.",
    "notes.txt": "Meeting notes here.",
    "photo.jpg": "JPEG binary data (simulated)",
    "diagram.jpg": "Another JPEG (simulated)",
    "script.py": "print('hello')",
    "helper.py": "def add(a, b): return a + b",
    "data.csv": "name,age\nAlice,30\nBob,25",
}

for name, content in sample_files.items():
    (demo / name).write_text(content)

print("Files created in demo_workspace:")
for f in sorted(demo.iterdir()):
    print(f"  {f.name}")

print()
print("=" * 40)
print("1. Find files by extension using pathlib glob()")
print("=" * 40)

for ext in [".txt", ".jpg", ".py", ".csv"]:
    matches = list(demo.glob(f"*{ext}"))
    print(f"  {ext}: {[f.name for f in matches]}")

print()
print("=" * 40)
print("2. Find files recursively with rglob()")
print("=" * 40)

sub = demo / "subdir"
sub.mkdir(exist_ok=True)
(sub / "buried.txt").write_text("Found recursively!")

all_txt = list(demo.rglob("*.txt"))
print("All .txt files (including subdirs):")
for f in all_txt:
    print(f"  {f.relative_to(demo)}")

print()
print("=" * 40)
print("3. Copy files to a new directory")
print("=" * 40)
txt_dest = Path("txt_files")
txt_dest.mkdir(exist_ok=True)

for f in demo.glob("*.txt"):
    shutil.copy(f, txt_dest / f.name)
    print(f"  Copied {f.name} -> txt_files/")

print()
print("=" * 40)
print("4. Move files to organised directories")
print("=" * 40)
organised = Path("organised")
organised.mkdir(exist_ok=True)

ext_map = {".txt": "documents", ".jpg": "images", ".py": "scripts", ".csv": "data"}

for f in demo.glob("*.*"):
    if f.is_file():
        folder = ext_map.get(f.suffix, "other")
        dest = organised / folder
        dest.mkdir(exist_ok=True)
        shutil.move(str(f), dest / f.name)
        print(f"  Moved {f.name} -> organised/{folder}/")

print()
print("=" * 40)
print("5. Final organised structure")
print("=" * 40)
for root, dirs, files in os.walk("organised"):
    level = root.replace("organised", "").count(os.sep)
    print("  " * level + os.path.basename(root) + "/")
    for file in files:
        print("  " * (level + 1) + file)


for d in [demo, txt_dest, organised]:
    shutil.rmtree(d, ignore_errors=True)
print("\nAll demo directories cleaned up.")