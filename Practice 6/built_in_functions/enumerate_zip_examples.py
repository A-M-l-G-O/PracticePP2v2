# enumerate(), zip(), sorted(), len(), sum(), min(), max()


fruits   = ["apple", "banana", "cherry", "date", "elderberry"]
scores   = [88, 72, 95, 61, 83]
subjects = ["Math", "Science", "English", "History", "Art"]
prices   = [1.50, 0.75, 2.20, 3.10, 0.99]

print("=" * 45)
print("enumerate() - Index + value pairs")
print("=" * 45)

print("  Default (start=0):")
for i, fruit in enumerate(fruits):
    print(f"    [{i}] {fruit}")

print("\n  Starting at 1:")
for i, fruit in enumerate(fruits, start=1):
    print(f"    {i}. {fruit}")

print("\n  Student scores:")
for i, (subj, score) in enumerate(zip(subjects, scores), start=1):
    print(f"    {i}. {subj}: {score}")


print()
print("=" * 45)
print("zip() - Combine multiple iterables")
print("=" * 45)

print("  Fruit + Price pairs:")
for fruit, price in zip(fruits, prices):
    print(f"    {fruit:<12} ${price:.2f}")

fruit_price_dict = dict(zip(fruits, prices))
print(f"\n  As dict: {fruit_price_dict}")

print("\n  Three-way zip:")
for subj, score, fruit in zip(subjects, scores, fruits):
    print(f"    {subj:<10} {score}  ({fruit})")

print("\n  zip stops at shortest list:")
short = [1, 2, 3]
long  = ["a", "b", "c", "d", "e"]
print(f"    {list(zip(short, long))}")

zipped = [(1, "a"), (2, "b"), (3, "c")]
nums, letters = zip(*zipped)
print(f"\n  Unzip: nums={nums}, letters={letters}")


print()
print("=" * 45)
print("Aggregation & sorting built-ins")
print("=" * 45)

print(f"  scores  : {scores}")
print(f"  len()   : {len(scores)}")
print(f"  sum()   : {sum(scores)}")
print(f"  min()   : {min(scores)}")
print(f"  max()   : {max(scores)}")
print(f"  avg     : {sum(scores) / len(scores):.2f}")

print(f"\n  sorted ascending : {sorted(scores)}")
print(f"  sorted descending: {sorted(scores, reverse=True)}")

print(f"\n  fruits sorted by length : {sorted(fruits, key=len)}")
print(f"  fruits sorted alpha     : {sorted(fruits)}")

students = [("Alice", 92), ("Bob", 78), ("Charlie", 85)]
by_score = sorted(students, key=lambda s: s[1], reverse=True)
print(f"\n  students by score (desc): {by_score}")


print()
print("=" * 45)
print("Type conversion & checking")
print("=" * 45)

print(f"  int('42')      = {int('42')}")
print(f"  int(3.99)      = {int(3.99)}  (truncates)")
print(f"  int('0b1010',2)= {int('0b1010', 2)}  (binary)")

print(f"\n  float('3.14')  = {float('3.14')}")
print(f"  float(7)       = {float(7)}")

print(f"\n  str(100)       = '{str(100)}'")
print(f"  str(3.14)      = '{str(3.14)}'")
print(f"  str(True)      = '{str(True)}'")

print(f"\n  bool(0)        = {bool(0)}")
print(f"  bool(1)        = {bool(1)}")
print(f"  bool('')       = {bool('')}")
print(f"  bool('hi')     = {bool('hi')}")
print(f"  bool([])       = {bool([])}")
print(f"  bool([1,2])    = {bool([1, 2])}")

sample = (1, 2, 2, 3, 3, 3)
print(f"\n  tuple          : {sample}")
print(f"  list(tuple)    : {list(sample)}")
print(f"  set(tuple)     : {set(sample)}  (unique only)")

values = [42, 3.14, "hello", True, [1, 2], {"a": 1}]
print()
print("  type() check:")
for v in values:
    print(f"    {str(v):<15} -> {type(v).__name__}")

print()
print("  isinstance() check:")
print(f"    isinstance(42, int)        = {isinstance(42, int)}")
print(f"    isinstance(3.14, (int,float)) = {isinstance(3.14, (int, float))}")
print(f"    isinstance('hi', str)      = {isinstance('hi', str)}")