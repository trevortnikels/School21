def main():
    n = int(input())
    different_numbers = set()
    for _ in range(n):
        different_numbers.add(int(input()))
    print(len(different_numbers))



if __name__ == "__main__":
    main()