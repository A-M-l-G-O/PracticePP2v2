# Creating, listing, and managing directories

import os
import shutil
from pathlib import Path

print("=" * 40)
print("1. Get current working directory")
print("=" * 40)
print("os.getcwd():", os.getcwd())
print("Path.cwd(): ", Path.cwd())

print()
print("=" * 40)
print("2. Create a single directory with os.mkdir()")
print("=" * 40)
if not os.path.exists("my_folder"):
    os.mkdir("my_folder")
    print("Created: my_folder")
else:
    print("my_folder already exists")

print()
print("=" * 40)
print("3. Create nested directories with os.makedirs()")
print("=" * 40)
os.makedirs("project/src/utils", exist_ok=True)
os.makedirs("project/data/raw", exist_ok=True)
os.makedirs("project/data/processed", exist_ok=True)
print("Created nested structure:")
print("  project/src/utils")
print("  project/data/raw")
print("  project/data/processed")

print()
print("=" * 40)
print("4. Create nested dirs with pathlib")
print("=" * 40)
Path("project/tests/unit").mkdir(parents=True, exist_ok=True)
print("Created: project/tests/unit via pathlib")

print()
print("=" * 40)
print("5. List directory contents with os.listdir()")

for name in ["file_a.txt", "file_b.txt", "notes.md"]:
    Path(f"my_folder/{name}").write_text(f"Content of {name}")

print("Contents of my_folder:")
for item in os.listdir("my_folder"):
    print(f"  - {item}")

print()
print("=" * 40)
print("6. Walk directory tree with os.walk()")
print("=" * 40)
for root, dirs, files in os.walk("project"):
    level = root.replace("project", "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")

print()
print("=" * 40)
print("7. List with pathlib iterdir()")
print("=" * 40)
print("my_folder contents via pathlib:")
for item in Path("my_folder").iterdir():
    kind = "DIR " if item.is_dir() else "FILE"
    print(f"  [{kind}] {item.name}")

print()
print("=" * 40)
print("8. Remove an empty directory with os.rmdir()")
print("=" * 40)
os.makedirs("empty_dir", exist_ok=True)
os.rmdir("empty_dir")
print("Removed empty_dir with os.rmdir()")

print()
print("=" * 40)
print("9. Remove directory tree with shutil.rmtree()")
print("=" * 40)
shutil.rmtree("project")
shutil.rmtree("my_folder")
print("Removed project/ and my_folder/ trees")