#include "../s21_decimal.h"

// функция для преобразования десятичного числа в плавающее.
int s21_from_decimal_to_float(s21_decimal src, float* dst) {
  int conversion_result = 1;

  if (dst) {
    double tmp = 0;  // Переменная для хранения значения числа.
    int exp = 0;  // Переменная для хранения показателя степени.

    // если бит в поле bits установлен, то значение переменной tmp увеличивается
    // на степень двойки, соответствующую этому биту.
    for (int i = 0; i < 96; i++) {
      if ((src.bits[i / 32] & (1 << i % 32)) != 0) {
        tmp += pow(2, i);
      }
    }

    int scale = (char)(src.bits[3] >> 16);  // получаем масштаб числа
    if ((exp = scale) > 0) {
      for (int i = exp; i > 0; i--) {
        tmp /= 10.0;
      }
    }
    *dst = (float)tmp;  // записывает полученное значение

    int sign = !!(src.bits[3] & (1u << 31));  // получаем знак числа
    // Если число отрицательное, умножаем результат на -1.
    if (sign) {
      *dst *= -1;
    }

    conversion_result = 0;
  }

  return conversion_result;
}
