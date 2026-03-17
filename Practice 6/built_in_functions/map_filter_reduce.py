# Demonstrating map(), filter(), and reduce()

from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
words   = ["hello", "world", "python", "is", "awesome"]
prices  = [19.99, 5.50, 12.75, 3.00, 8.49]

print("=" * 40)
print("map() - Apply a function to every item")
print("=" * 40)

squares = list(map(lambda x: x ** 2, numbers))
print(f"  numbers : {numbers}")
print(f"  squares : {squares}")

upper_words = list(map(str.upper, words))
print(f"\n  words       : {words}")
print(f"  upper_words : {upper_words}")

rounded = list(map(lambda p: round(p), prices))
print(f"\n  prices  : {prices}")
print(f"  rounded : {rounded}")

a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(f"\n  a + b element-wise: {sums}")


print()
print("=" * 40)
print("filter() - Keep items that pass a test")
print("=" * 40)

evens = list(filter(lambda x: x % 2 == 0, numbers))
odds  = list(filter(lambda x: x % 2 != 0, numbers))
print(f"  numbers : {numbers}")
print(f"  evens   : {evens}")
print(f"  odds    : {odds}")

long_words = list(filter(lambda w: len(w) > 4, words))
print(f"\n  words with len > 4 : {long_words}")

affordable = list(filter(lambda p: p < 10, prices))
print(f"\n  prices under $10   : {affordable}")


print()
print("=" * 40)
print("reduce() - Aggregate a sequence to one value")
print("=" * 40)

total   = reduce(lambda acc, x: acc + x, numbers)
product = reduce(lambda acc, x: acc * x, numbers)
maximum = reduce(lambda acc, x: acc if acc > x else x, numbers)

print(f"  numbers : {numbers}")
print(f"  sum     : {total}")
print(f"  product : {product}")
print(f"  max     : {maximum}")

total_price = reduce(lambda acc, p: acc + p, prices, 0)
print(f"\n  prices      : {prices}")
print(f"  total price : {total_price:.2f}")

sentence = reduce(lambda acc, w: acc + " " + w, words)
print(f"\n  words joined: '{sentence}'")


print()
print("=" * 40)
print("Chained: sum of squares of even numbers")
print("=" * 40)
result = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x ** 2,
        filter(lambda x: x % 2 == 0, numbers))
)
print(f"  numbers          : {numbers}")
print(f"  evens            : {list(filter(lambda x: x % 2 == 0, numbers))}")
print(f"  squares of evens : {list(map(lambda x: x**2, filter(lambda x: x % 2 == 0, numbers)))}")
print(f"  sum of those     : {result}")