#include "../s21_additional_func.h"
#include "../s21_decimal.h"

// Округляет Decimal до ближайшего целого числа.
int s21_round(s21_decimal value, s21_decimal* result) {
  if (!s21_truncate(value, result) && !s21_is_equal(value, *result)) {
    int sign = !!(value.bits[3] & (1u << 31));
    if (sign) {
      s21_sub(value, ((s21_decimal){{5, 0, 0, 65536}}), &value);
    } else {
      s21_add(value, ((s21_decimal){{5, 0, 0, 65536}}), &value);
      s21_truncate(value, result);
    }
  }
  return 0;
}
