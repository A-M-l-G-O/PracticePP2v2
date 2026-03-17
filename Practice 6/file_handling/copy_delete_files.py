# Copying, backing up, and deleting files

import os
import shutil
from pathlib import Path

# Setup: create a sample file
Path("original.txt").write_text(
    "This is the original file.\nIt has important data.\nHandle with care!\n"
)

print("=" * 40)
print("1. Copy a file with shutil.copy()")
print("=" * 40)
shutil.copy("original.txt", "copy_of_original.txt")
print("Copied: original.txt -> copy_of_original.txt")
print("Copy contents:", Path("copy_of_original.txt").read_text())

print("=" * 40)
print("2. Copy with metadata using shutil.copy2()")
print("=" * 40)
shutil.copy2("original.txt", "copy2_of_original.txt")
print("Copied with metadata: original.txt -> copy2_of_original.txt")

print("=" * 40)
print("3. Create a backup directory and back up the file")
print("=" * 40)
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
shutil.copy("original.txt", backup_dir / "original_backup.txt")
print(f"Backup saved to: {backup_dir / 'original_backup.txt'}")

print("=" * 40)
print("4. Rename / move a file with shutil.move()")
print("=" * 40)
Path("to_move.txt").write_text("I will be moved.\n")
shutil.move("to_move.txt", "moved_file.txt")
print("Moved: to_move.txt -> moved_file.txt")
print(f"  'to_move.txt' exists: {Path('to_move.txt').exists()}")
print(f"  'moved_file.txt' exists: {Path('moved_file.txt').exists()}")

print()
print("=" * 40)
print("5. Delete a file safely with os.remove()")
print("=" * 40)
Path("to_delete.txt").write_text("Delete me!\n")
if os.path.exists("to_delete.txt"):
    os.remove("to_delete.txt")
    print("Deleted: to_delete.txt")

print("=" * 40)
print("6. Delete with pathlib (unlink)")
print("=" * 40)
p = Path("also_delete.txt")
p.write_text("Delete me too!\n")
p.unlink()
print(f"Deleted via pathlib: {p.name}")

print()
print("=" * 40)
print("7. Check file info before deleting")
print("=" * 40)
info_file = Path("info_file.txt")
info_file.write_text("Some content here.\n")
stat = info_file.stat()
print(f"  Name:  {info_file.name}")
print(f"  Size:  {stat.st_size} bytes")
print(f"  Exists: {info_file.exists()}")
info_file.unlink()
print(f"  After delete, exists: {info_file.exists()}")

for f in ["original.txt", "copy_of_original.txt", "copy2_of_original.txt", "moved_file.txt"]:
    Path(f).unlink(missing_ok=True)
shutil.rmtree("backups", ignore_errors=True)
print("\nAll demo files cleaned up.")