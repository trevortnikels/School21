#include "../s21_additional_func.h"
#include "../s21_decimal.h"

//  Функция сравнения >
int s21_is_greater(s21_decimal value_1, s21_decimal value_2) {
  int res = 0;
  int sign_a = !!(value_1.bits[3] & (1u << 31));
  int sign_b = !!(value_2.bits[3] & (1u << 31));
  int is_null_1 = !value_1.bits[0] && !value_1.bits[1] && !value_1.bits[2];
  int is_null_2 = !value_2.bits[0] && !value_2.bits[1] && !value_2.bits[2];
  if (!(is_null_1 && is_null_2)) {
    if (sign_a != sign_b) {
      if (sign_a == 0) {
        res = 1;
      } else {
        res = 0;
      }
    } else {
      s21_alignment_Scale(&value_1, &value_2);
      for (int bit = 95; bit >= 0; bit--) {
        int bit_1 = !!(value_1.bits[bit / 32] & (1u << (bit % 32)));
        int bit_2 = !!(value_2.bits[bit / 32] & (1u << (bit % 32)));
        if (bit_1 != bit_2) {
          if (bit_1 != 0) {
            res = (sign_a == 0) ? 1 : 0;
            break;
          } else {
            res = (sign_a == 0) ? 0 : 1;
            break;
          }
        }
      }
    }
  }
  return res;
}
