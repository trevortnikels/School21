#include "s21_arithmetic_lib.h"

int get_sign(s21_decimal dec) { return (dec.bits[3] >> 31) == 1 ? -1 : 1; }

void set_sign(s21_decimal *dst, int sign) { dst->bits[3] |= sign << 31; }

int is_null(s21_decimal dec) {
  int res = 1;
  if (dec.bits[0] != 0 || dec.bits[1] != 0 || dec.bits[2] != 0) res = 0;
  return res;
}

int get_bit(s21_decimal dec, int bit_num) {
  int block_num = bit_num / 32;
  bit_num %= 32;

  return (dec.bits[block_num] >> bit_num) & 1;
}

int set_bit(s21_decimal *dec, int bit_num, int bit) {
  int err = 0;
  if (bit_num >= 0 && bit_num < 96) {
    int block_num = bit_num / 32;
    bit_num %= 32;

    uint32_t mask = (1 << bit_num);
    dec->bits[block_num] &= ~mask;
    dec->bits[block_num] |= (bit << bit_num);
  } else {
    err = 1;
  }
  return err;
}

int set_power(s21_decimal *dec, int power) {
  int res = 0;

  if ((0 <= power) && (power <= 28)) {
    dec->bits[3] &= ~SCALE_MASK;  // зануление прошлого числа
    dec->bits[3] |= power << 16;
  } else {
    res = 1;
  }
  return res;
}

int get_power(s21_decimal dec) { return (dec.bits[3] & SCALE_MASK) >> 16; }

int shift_left(s21_decimal *dec, int shift) {
  int err = 0;
  int available_space = 96 - get_start_bit_num(*dec) - 1;
  if (shift <= available_space) {
    for (int i = 0; i < shift; i++) {
      int carry = 0;
      for (int j = 0; j < 3; j++) {
        unsigned int new_carry = (dec->bits[j] & 0x80000000) ? 1 : 0;
        dec->bits[j] <<= 1;
        dec->bits[j] |= carry;
        carry = new_carry;
      }
    }
  } else {
    err = 1;
  }
  return err;
}

int shift_right(s21_decimal *dec, int shift) {
  for (int i = 0; i < shift; i++) {
    int borrow = 0;
    for (int j = 3; j >= 0; j--) {
      unsigned int new_borrow = (dec->bits[j] & 1) ? 0x80000000 : 0;
      dec->bits[j] >>= 1;
      dec->bits[j] |= borrow;
      borrow = new_borrow;
    }
  }
  return 0;
}

int simple_subtract(s21_decimal value_1, s21_decimal value_2,
                    s21_decimal *result) {
  if (simple_compare(value_1, value_2) < 0) {
    s21_decimal temp = value_1;
    value_1 = value_2;
    value_2 = temp;
    set_sign(result, 1);
  }
  int mem = 0;
  int bit_res;
  for (int i = 0; i < 96; i++) {
    int bit1 = get_bit(value_1, i);
    int bit2 = get_bit(value_2, i) + mem;

    if (bit1 >= bit2) {
      bit_res = bit1 - bit2;
      mem = 0;
    } else {
      bit_res = (bit1 + 2) - bit2;  // Заем в двоичной системе
      mem = 1;
    }
    set_bit(result, i, bit_res);
  }

  return 0;
}

int simple_multiplication(s21_decimal value_1, s21_decimal value_2,
                          s21_decimal *result) {
  s21_clear_decimal(result);
  int err;
  int start_val2_bit = get_start_bit_num(value_2);
  for (int i = 0; i <= start_val2_bit; i++) {
    if (get_bit(value_2, i) == 1) {
      if ((err = simple_addition(*result, value_1, result) != 0)) break;
    }
    if (shift_left(&value_1, 1) != 0 && i != start_val2_bit) {
      err = 1;
      break;
    }
  }
  return err;
}

int simple_division(s21_decimal dec1, s21_decimal dec2, s21_decimal *res) {
  s21_clear_decimal(res);
  int err = 0;
  // Проверка деления на ноль
  if (is_null(dec2)) {
    err = -1;  // Возвращаем ошибку, если делитель равен 0
  } else {
    // Определяем стартовые биты для делимого и делителя
    int dividend_start_bit_num = get_start_bit_num(dec1);
    int divider_start_bit_num = get_start_bit_num(dec2);

    // Если делимое меньше делителя, результат будет 0
    if (dividend_start_bit_num >= divider_start_bit_num) {
      s21_decimal divider = dec2;
      s21_decimal dividend = dec1;

      int shift_count = dividend_start_bit_num - divider_start_bit_num;
      shift_left(&divider, shift_count);

      for (int i = shift_count; i >= 0; i--) {
        if (simple_compare(divider, dividend) <= 0) {
          // Вычитаем делитель из делимого
          simple_subtract(dividend, divider, &dividend);
          // Устанавливаем соответствующий бит результата
          set_bit(res, i, 1);
        }
        // Сдвигаем делитель вправо на одну позицию
        shift_right(&divider, 1);
      }
    }
  }
  return err;
}

s21_decimal simple_remainder_decimal(s21_decimal dec1, s21_decimal dec2,
                                     s21_decimal *res) {
  s21_decimal remainder;
  s21_clear_decimal(res);
  s21_clear_decimal(&remainder);

  if (!is_null(dec2)) {
    s21_decimal temp_res;
    s21_clear_decimal(&temp_res);
    simple_division(dec1, dec2, res);
    simple_multiplication(*res, dec2, &temp_res);
    simple_subtract(dec1, temp_res, &remainder);
  }
  if (get_sign(dec1) * get_sign(dec2) < 0) set_sign(res, 1);
  return remainder;
}

int simple_remainder_int(s21_decimal dec1, s21_decimal dec2, s21_decimal *res) {
  s21_decimal dec_rem = simple_remainder_decimal(dec1, dec2, res);
  int int_rem = dec_rem.bits[0];
  return int_rem;
}

int simple_addition(s21_decimal value_1, s21_decimal value_2,
                    s21_decimal *result) {
  int mem = 0;
  int err = 0;
  for (int i = 0; i < 96; i++) {
    int bit1 = get_bit(value_1, i) + mem;
    int bit2 = get_bit(value_2, i);
    int addition = bit1 + bit2;
    int bit_res = addition & 0x00000001;
    mem = (addition & 0x00000002) >> 1;
    set_bit(result, i, bit_res);
  }
  if (mem != 0) err = 1;

  return err;
}

void s21_clear_decimal(s21_decimal *decimal) {
  decimal->bits[0] = 0;
  decimal->bits[1] = 0;
  decimal->bits[2] = 0;
  decimal->bits[3] = 0;
}

int s21_scale_by10(s21_decimal *dec, int tens_count) {
  int pow = get_power(*dec);
  int err;
  s21_decimal dec_backup = *dec;
  for (int ten = 1; ten <= tens_count; ten++) {
    // умножаем x*10 как x*8+x*2 = x*2^3 + x*2^1
    s21_decimal temp1 = *dec;
    s21_decimal temp2 = *dec;
    if ((err = shift_left(&temp1, 3) != 0)) break;  // x*2^3
    shift_left(&temp2, 1);                          // x*2^1

    if ((err = simple_addition(temp1, temp2, dec) != 0))
      break;  // x*2^3 + x*2^1
    pow++;
  }
  err += (set_power(dec, pow) != 0);
  if (err) *dec = dec_backup;
  return err;
}

int s21_descale_by10_with_round(s21_decimal *dec, int tens_count) {
  int err = 0;
  const s21_decimal dec10 = {.bits = {10, 0, 0, 0}};
  s21_decimal trash;
  int pow = get_power(*dec);

  for (int ten = 1; ten <= tens_count; ten++) {
    s21_decimal round_unit = {.bits = {0, 0, 0, 0}};
    int remainder = simple_remainder_int(*dec, dec10, dec);
    if (remainder == 5) {
      int next_digit = simple_remainder_int(*dec, dec10, &trash);
      if (next_digit % 2 != 0) {
        round_unit.bits[0] = 1;
      }
    } else if (remainder > 5) {
      round_unit.bits[0] = 1;
    }
    simple_addition(*dec, round_unit, dec);
    pow--;
  }

  if (pow >= 0) {
    set_power(dec, pow);
  } else {
    set_power(dec, 0);
    err = 1;
  }
  return err;
}

int get_start_bit_num(s21_decimal dec) {
  int res = 0;
  for (int i = 95; i > 0; i--) {
    if (get_bit(dec, i) == 1) {
      res = i;
      break;
    }
  }
  return res;
}

int normalise_fraction(s21_decimal *dec1, s21_decimal *dec2) {
  int pow1 = get_power(*dec1);
  int pow2 = get_power(*dec2);
  // s21_decimal dec1_backup = *dec1;
  // s21_decimal dec2_backup = *dec2;
  int overflow;

  if (pow1 < pow2) {
    overflow = s21_scale_by10(dec1, (pow2 - pow1));
    if (overflow) {
      // округление на один знак
      // рекурсивный вызов нормализации
      s21_descale_by10_with_round(dec2, 1);
      normalise_fraction(dec1, dec2);
    }
  } else if (pow1 > pow2) {
    overflow = s21_scale_by10(dec2, (pow1 - pow2));
    if (overflow) {
      s21_descale_by10_with_round(dec1, 1);
      normalise_fraction(dec1, dec2);
    }
  }

  return 0;
}

int simple_compare(s21_decimal dec1, s21_decimal dec2) {
  // dec1 < dec2 = - 1
  // dec1 = dec2 = 0
  // dec1 > dec2 = 1
  int res = 0;
  int i;
  for (i = 95; i >= 0; i--) {
    if (get_bit(dec1, i) > get_bit(dec2, i)) {
      res = 1;
      break;
    } else if (get_bit(dec1, i) < get_bit(dec2, i)) {
      res = -1;
      break;
    }
  }
  return res;
}

// char *s21_decimal_to_string(s21_decimal dec) {
//   const s21_decimal dec10 = {.bits = {10, 0, 0, 0}};
//   static char
//       out[40];  // static чтобы вернуть указатель на локальную переменную
//   int remainder;
//   int index = 0;

//   int pow = get_power(dec);
//   int pow_bool = pow > 0 ? 1 : 0;

//   while (index < 39) {
//     remainder =
//         simple_remainder_int(dec, dec10, &dec);  // Остаток от деления на 10

//     // Записываем остаток в строку как символ
//     out[index++] = '0' + remainder;
//     pow--;
//     if (pow_bool && pow == 0) {
//       out[index++] = '.';  // Записываем точку в строку
//       pow_bool = 0;
//     }
//     if (is_null(dec) && pow <= 0) {
//       if (out[index - 1] == '.') out[index++] = '0';
//       break;
//     };  // Уменьшаем степень для отслеживания позиции точки
//   }

//   if (get_sign(dec) == -1) {
//     out[index++] = '-';  // Записываем знак минус для отрицательных чисел
//   }

//   out[index] = '\0';  // Завершаем строку нулевым символом

//   // Реверс строки
//   int start = 0;
//   int end = strlen(out) - 1;
//   while (start < end) {
//     char temp = out[start];
//     out[start] = out[end];
//     out[end] = temp;
//     start++;
//     end--;
//   }

//   return out;
// }
