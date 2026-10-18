#ifndef S21_DECIMAL_LIB
#define S21_DECIMAL_LIB

#include "s21_decimal.h"

#define SCALE_MASK 16711680
#define TO_LARGE_NUM 1
#define TO_LESS_NUM 2
#define ZERO_DIVISION 3

typedef struct {
  unsigned int bits[7];
} s21_decimal_long;

int get_sign(s21_decimal dec);
void set_sign(s21_decimal *dst, int sign);
int is_null(s21_decimal dec);
int get_bit(s21_decimal dec, int bit_num);
int set_power(s21_decimal *dec, int power);
int get_power(s21_decimal dec);
void s21_clear_decimal(s21_decimal *dec);
int set_bit(s21_decimal *dec, int bit_num, int bit);
int shift_left(s21_decimal *dec, int shift);
int shift_right(s21_decimal *dec, int shift);
int s21_scale_by10(s21_decimal *dec, int tens_count);
int s21_descale_by10_with_round(s21_decimal *dec, int tens_count);
int simple_addition(s21_decimal value_1, s21_decimal value_2,
                    s21_decimal *result);
int simple_subtract(s21_decimal value_1, s21_decimal value_2,
                    s21_decimal *result);

int simple_division(s21_decimal dec1, s21_decimal dec2, s21_decimal *res);
int simple_multiplication(s21_decimal value_1, s21_decimal value_2,
                          s21_decimal *result);
int simple_compare(s21_decimal dec1, s21_decimal dec2);
s21_decimal simple_remainder_decimal(s21_decimal dec1, s21_decimal dec2,
                                     s21_decimal *res);
int simple_remainder_int(s21_decimal dec1, s21_decimal dec2, s21_decimal *res);

int get_start_bit_num(s21_decimal dec);
int normalise_fraction(s21_decimal *dec1, s21_decimal *dec2);

// char *s21_decimal_to_string(s21_decimal dec);

#endif
