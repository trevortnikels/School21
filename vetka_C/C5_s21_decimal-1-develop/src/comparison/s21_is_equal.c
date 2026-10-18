#include "../s21_additional_func.h"
#include "../s21_decimal.h"

// Функция сравнения равенства ==
int s21_is_equal(s21_decimal value_1, s21_decimal value_2) {
  int res = 1;
  int sign_1 = !!(value_1.bits[3] & (1u << 31));
  int sign_2 = !!(value_2.bits[3] & (1u << 31));
  int is_null_1 = !value_1.bits[0] && !value_1.bits[1] && !value_1.bits[2];
  int is_null_2 = !value_2.bits[0] && !value_2.bits[1] && !value_2.bits[2];
  if (sign_1 == sign_2) {
    s21_alignment_Scale(&value_1, &value_2);
    for (int bit = 95; bit >= 0; bit--) {
      int bit_1 = !!(value_1.bits[bit / 32] & (1u << (bit % 32)));
      int bit_2 = !!(value_2.bits[bit / 32] & (1u << (bit % 32)));
      if (bit_1 != bit_2) {
        res = 0;
        break;
      }
    }

  } else if (!(is_null_1 && is_null_2)) {
    res = 0;
  }
  return res;
}
