def find_derivative(pow: int, x: float) -> float:
    result = 0.0
    for p in range(pow, -1, -1):
        coef = float(input())          
        result += p * coef * x ** (p - 1)
    
    return result


def main():
    pow_str, x_str = input().split()
    pow = int(pow_str)
    x = float(x_str)
    
    derivative = find_derivative(pow, x)
    
  
    print(f"{derivative:.3f}")
 


if __name__ == "__main__":
    main()