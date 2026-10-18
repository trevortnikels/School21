import sys

input = sys.stdin.read
data = input().split()

# Первая строка: N M
N = int(data[0])
M = int(data[1])

# Следующие N строк — поле
index = 2
grid = []
for i in range(N):
    row = [int(data[index + j]) for j in range(M)]
    grid.append(row)
    index += M

# Создаём dp-таблицу
dp = [[0] * M for _ in range(N)]

# Начальная клетка
dp[0][0] = grid[0][0]

# Заполняем первую строку (только вправо)
for j in range(1, M):
    dp[0][j] = dp[0][j-1] + grid[0][j]

# Заполняем первый столбец (только вниз)
for i in range(1, N):
    dp[i][0] = dp[i-1][0] + grid[i][0]

# Заполняем остальную таблицу
for i in range(1, N):
    for j in range(1, M):
        dp[i][j] = grid[i][j] + max(dp[i-1][j], dp[i][j-1])

# Ответ — значение в правом нижнем углу
print(dp[N-1][M-1])