def parse_float(s):
    """
    Парсит строку в вещественное число вручную.
    Возвращает (число, True) при успехе или (None, False) при ошибке.
    """
    s = s.strip()
    if not s:
        return None, False

    # Убираем знак в начале
    sign = 1
    if s[0] in '+-':
        if s[0] == '-':
            sign = -1
        s = s[1:]

    # Разделяем на целую и дробную часть
    if '.' in s:
        parts = s.split('.', 1)
        if len(parts) != 2:
            return None, False
        integer_part, fractional_part = parts
    else:
        integer_part = s
        fractional_part = ''

    # Проверяем, что остались только цифры
    if not integer_part.isdigit() or not fractional_part.isdigit():
        return None, False

    # Считаем целую часть
    value = 0.0
    for digit in integer_part:
        value = value * 10 + int(digit)

    # Считаем дробную часть
    frac_value = 0.0
    divisor = 1.0
    for digit in fractional_part:
        divisor *= 10
        frac_value = frac_value * 10 + int(digit)

    if divisor > 1:
        value += frac_value / divisor

    return sign * value, True

def main():
    try:
        s = input().strip()

        number, success = parse_float(s)

        if not success:
            print("Invalid input")
            return

        result = number * 2
        print(f"{result:.3f}")

    except Exception:
        print("Invalid input")


if __name__ == "__main__":
    main()