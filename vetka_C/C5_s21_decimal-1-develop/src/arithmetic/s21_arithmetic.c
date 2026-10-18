#include "./../s21_arithmetic_lib.h"
#include "./../s21_decimal.h"

int s21_add(s21_decimal value_1, s21_decimal value_2, s21_decimal *result) {
  normalise_fraction(&value_1, &value_2);
  int overflow = 0;
  int err = 0;

  set_power(result, get_power(value_1));

  if (get_sign(value_1) == 1 && get_sign(value_2) == -1) {
    simple_subtract(value_1, value_2, result);
  } else if (get_sign(value_1) == -1 && get_sign(value_2) == 1) {
    simple_subtract(value_2, value_1, result);
  } else {
    overflow = simple_addition(value_1, value_2, result);
    // попытка при переполнении округлить дробную часть
    if (overflow && get_power(value_1) > 0) {
      s21_descale_by10_with_round(&value_1, 1);
      s21_descale_by10_with_round(&value_2, 1);
      err = s21_add(value_1, value_2, result);
      overflow = 0;
    }
    if (get_sign(value_1) == -1 && get_sign(value_2) == -1) {
      set_sign(result, 1);
    }
  }

  if (err != 0 || overflow != 0) {
    if (get_sign(*result) > 0) {
      err = TO_LARGE_NUM;
    } else {
      err = TO_LESS_NUM;
    }
    s21_clear_decimal(result);
  }
  return err;
}

int s21_sub(s21_decimal value_1, s21_decimal value_2, s21_decimal *result) {
  int overflow = 0;
  int err = 0;
  normalise_fraction(&value_1, &value_2);
  set_power(result, get_power(value_1));

  if (get_sign(value_1) * get_sign(value_2) < 0) {
    overflow = simple_addition(value_1, value_2, result);
    if (overflow && get_power(value_1) > 0) {
      s21_descale_by10_with_round(&value_1, 1);
      s21_descale_by10_with_round(&value_2, 1);
      err = s21_add(value_1, value_2, result);
      overflow = 0;
    }

    if (get_sign(value_1) == -1) set_sign(result, 1);

  } else if (get_sign(value_1) == -1 && get_sign(value_2) == -1) {
    simple_subtract(value_2, value_1, result);
  } else {
    simple_subtract(value_1, value_2, result);
  }

  if (err != 0 || overflow != 0) {
    if (get_sign(*result) > 0) {
      err = TO_LARGE_NUM;
    } else {
      err = TO_LESS_NUM;
    }
    s21_clear_decimal(result);
  }

  return err;
}

int s21_mul(s21_decimal value_1, s21_decimal value_2, s21_decimal *result) {
  int overflow = 0;
  int err = 0;
  normalise_fraction(&value_1, &value_2);

  s21_clear_decimal(result);
  set_power(result, get_power(value_1) + get_power(value_2));

  overflow = simple_multiplication(value_1, value_2, result);
  if (overflow && get_power(value_1) > 0) {
    s21_descale_by10_with_round(&value_1, 1);
    s21_descale_by10_with_round(&value_2, 1);
    err = s21_mul(value_1, value_2, result);
    overflow = 0;
  }

  if (get_sign(value_1) * get_sign(value_2) < 0) {
    set_sign(result, 1);
  }

  if (err != 0 || overflow != 0) {
    if (get_sign(*result) > 0) {
      err = TO_LARGE_NUM;
    } else {
      err = TO_LESS_NUM;
    }
    s21_clear_decimal(result);
  }

  return err;
}

int s21_div(s21_decimal dec1, s21_decimal dec2, s21_decimal *res) {
  int err = 0;
  // int overflow = 0;
  if (is_null(dec2)) {
    err = ZERO_DIVISION;  // Возвращаем ошибку, если делитель равен 0
  } else {
    s21_clear_decimal(res);
    normalise_fraction(&dec1, &dec2);

    s21_decimal quotient, remainder;
    s21_clear_decimal(&quotient);
    s21_clear_decimal(&remainder);
    // Остаток от деления

    remainder = simple_remainder_decimal(dec1, dec2, &quotient);

    // Проверка и вычисление дробной части
    s21_decimal temp_quotient;
    int shift_count = 0;
    int scale_overflow = 0;
    while (!is_null(remainder)) {
      scale_overflow = s21_scale_by10(&remainder, 1);
      if (scale_overflow) {
        s21_descale_by10_with_round(&dec2, 1);
      }
      s21_clear_decimal(&temp_quotient);

      remainder = simple_remainder_decimal(remainder, dec2, &temp_quotient);
      if (s21_scale_by10(&quotient, 1) != 0) break;
      shift_count++;
      if (simple_addition(quotient, temp_quotient, &quotient) != 0) break;
    }

    *res = quotient;
    set_power(res, shift_count);
    if (get_sign(dec1) * get_sign(dec2) < 0) {
      set_sign(res, 1);
    }
  }
  return err;
}
