# Various ways to read files in Python

from pathlib import Path

sample_file = Path("sample.txt")
sample_file.write_text(
    "Line 1: Hello, Python!\n"
    "Line 2: File handling is useful.\n"
    "Line 3: Practice makes perfect.\n"
    "Line 4: Keep coding!\n"
)

print("=" * 40)
print("1. read() - Read entire file at once")
print("=" * 40)
with open("sample.txt", "r") as f:
    content = f.read()
    print(content)

print("=" * 40)
print("2. readline() - Read one line at a time")
print("=" * 40)
with open("sample.txt", "r") as f:
    line = f.readline()
    while line:
        print(repr(line))
        line = f.readline()

print()
print("=" * 40)
print("3. readlines() - Read all lines into a list")
print("=" * 40)
with open("sample.txt", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, start=1):
        print(f"  Line {i}: {line.strip()}")

print()
print("=" * 40)
print("4. Iterating line by line (memory efficient)")
print("=" * 40)
with open("sample.txt", "r") as f:
    for line in f:
        print(" >", line.strip())

print()
print("=" * 40)
print("5. Reading with pathlib")
print("=" * 40)
text = Path("sample.txt").read_text()
print(text)

sample_file.unlink()
print("sample.txt removed after demo.")