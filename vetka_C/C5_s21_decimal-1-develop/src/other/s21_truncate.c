#include "../s21_decimal.h"
// Константа используется для ограничения максимального значения числа
#define S21_MAX_UINT 4294967295

// Возвращает целые цифры указанного Decimal числа; любые дробные цифры
// отбрасываются, включая конечные нули.
int s21_truncate(s21_decimal value, s21_decimal *result) {
  int fun_result = 0;

  int scale = (char)(value.bits[3] >> 16);  // вычисляет масштаб числа
  if (scale) {
    for (int y = 0; y < scale; y += 1) {
      unsigned long long overflow = value.bits[2];
      for (int x = 2; x >= 0; x -= 1) {
        value.bits[x] = overflow / 10;
        overflow =
            (overflow % 10) * (S21_MAX_UINT + 1) + value.bits[x ? x - 1 : x];
      }
    }
    scale = scale - scale;  // обнуляет scale
    if (scale >= 0 && scale <= 28) {
      int sign = !!(value.bits[3] & (1u << 31));  // получает знак
      value.bits[3] &= ~(0xFF << 16);
      value.bits[3] |= scale << 16;
      if (sign) {
        value.bits[3] =
            (value.bits[3] | (1u << 31));  // устанавливает знаковый бит
      }
    }
    for (int x = 0; x < 4; x += 1) result->bits[x] = 0;  // обнуляет result
    for (int x = 0; x < 4; x += 1)
      result->bits[x] = value.bits[x];  // копирует значение в result

  } else {
    for (int x = 0; x < 4; x += 1) result->bits[x] = 0;  ////обнуляет result
    for (int x = 0; x < 4; x += 1)
      result->bits[x] = value.bits[x];  ////копирует значение в result
  }

  return fun_result;
}
