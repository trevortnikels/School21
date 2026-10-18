def generate_pascal_row(prev_row):
    """Генерирует следующую строку треугольника Паскаля на основе предыдущей"""
    if not prev_row:
        return [1]
    
    new_row = [1]  # первая единица
    for i in range(len(prev_row) - 1):
        new_row.append(prev_row[i] + prev_row[i + 1])
    new_row.append(1)  # последняя единица
    
    return new_row


def main():
    # Читаем ввод
    try:
        n = input().strip()
        if not n:
            print("Natural number was expected")
            return
        
        n = int(n)
        
        if n < 0:
            print("Natural number was expected")
            return
        
        if n == 0:
            return  # ничего не выводим
        
    except ValueError:
        print("Natural number was expected")
        return
    
    # Генерируем и выводим строки
    current_row = []
    for row_num in range(n):
        current_row = generate_pascal_row(current_row)
        # Выводим строку через пробел
        print(' '.join(map(str, current_row)))


if __name__ == "__main__":
    main()
    