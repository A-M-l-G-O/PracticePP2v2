# Writing and appending to files

from pathlib import Path

print("=" * 40)
print("1. Write mode 'w' - Creates or overwrites")
print("=" * 40)
with open("notes.txt", "w") as f:
    f.write("First line written.\n")
    f.write("Second line written.\n")
print("Written to notes.txt")

with open("notes.txt", "r") as f:
    print(f.read())

print("=" * 40)
print("2. Append mode 'a' - Adds to existing file")
print("=" * 40)
with open("notes.txt", "a") as f:
    f.write("Third line appended.\n")
    f.write("Fourth line appended.\n")
print("Appended to notes.txt")

with open("notes.txt", "r") as f:
    print(f.read())

print("=" * 40)
print("3. Exclusive create mode 'x' - Fails if file exists")
print("=" * 40)
new_file = Path("brand_new.txt")
if new_file.exists():
    new_file.unlink()

try:
    with open("brand_new.txt", "x") as f:
        f.write("This file was just created!\n")
    print("brand_new.txt created successfully.")
except FileExistsError:
    print("File already exists!")

print("=" * 40)
print("4. Writing a list of lines with writelines()")
print("=" * 40)
students = ["Alice\n", "Bob\n", "Charlie\n", "Diana\n"]
with open("students.txt", "w") as f:
    f.writelines(students)
print("students.txt written with writelines()")

with open("students.txt", "r") as f:
    print(f.read())

print("=" * 40)
print("5. Writing with pathlib")
print("=" * 40)
Path("pathlib_demo.txt").write_text("Written using pathlib!\nSimple and clean.")
print(Path("pathlib_demo.txt").read_text())

for fname in ["notes.txt", "brand_new.txt", "students.txt", "pathlib_demo.txt"]:
    Path(fname).unlink(missing_ok=True)
print("\nAll demo files cleaned up.")