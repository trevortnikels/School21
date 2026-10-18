#ifndef S21_ADDITIONAL_FUNC
#define S21_ADDITIONAL_FUNC

#include "s21_decimal.h"

s21_decimal *s21_setBit(s21_decimal *value, int pos, int bit);
int s21_addBit(s21_decimal value_1, s21_decimal value_2, s21_decimal *result);
int s21_getBitLast(s21_decimal value);
s21_decimal *s21_leftShift(s21_decimal *value, int shift);
s21_decimal *s21_increaseScale(s21_decimal *value, int shift);
s21_decimal *s21_decreaseScale(s21_decimal *value, int shift);
void s21_alignment_Scale(s21_decimal *value_1, s21_decimal *value_2);
int s21_add_func(s21_decimal value_1, s21_decimal value_2, s21_decimal *result);
int s21_sub_func(s21_decimal value_1, s21_decimal value_2, s21_decimal *result);
s21_decimal *s21_convert(s21_decimal *value);

#endif