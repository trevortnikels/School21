#include "../s21_additional_func.h"
#include "../s21_decimal.h"

// функция сравнение <
int s21_is_less(s21_decimal value_1, s21_decimal value_2) {
  return s21_is_greater(value_2, value_1);
}
