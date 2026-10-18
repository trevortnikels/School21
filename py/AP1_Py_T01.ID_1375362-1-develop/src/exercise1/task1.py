import sys

# Читаем две строки из stdin
input_data = sys.stdin.read().strip().splitlines()

# Парсим первую строку в координаты первого вектора
vector1 = list(map(float, input_data[0].split()))

# Парсим вторую строку в координаты второго вектора
vector2 = list(map(float, input_data[1].split()))

# Вычисляем скалярное произведение
dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1] + vector1[2] * vector2[2]

# Выводим результат
print(dot_product)