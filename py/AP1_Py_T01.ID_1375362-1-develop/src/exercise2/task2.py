n = int(input())

if n < 0:
    print(False)
else:
    original = n
    reversed_n = 0
    while n > 0:
        reversed_n = reversed_n * 10 + n % 10
        n //= 10
    print(original == reversed_n)