#include "../s21_additional_func.h"
#include "../s21_decimal.h"

// Округляет указанное Decimal число до ближайшего целого числа в сторону
// отрицательной бесконечности.
int s21_floor(s21_decimal value, s21_decimal* result) {
  for (int x = 0; x < 4; x += 1) result->bits[x] = 0;
  int sign = !!(value.bits[3] & (1u << 31));
  if (!s21_truncate(value, result) && sign && !s21_is_equal(*result, value))
    s21_sub(*result, ((s21_decimal){{1, 0, 0, 0}}), result);
  return 0;
}
