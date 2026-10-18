#include "../s21_decimal.h"

typedef union {
  int ui;
  float fl;
} fbits;

int s21_from_float_to_decimal(float src, s21_decimal *dst) {
  int conversion_result = 1;
  // Извлечение экспоненты из представления числа с плавающей запятой
  int exp = ((*((int *)&src) & ~(1u << 31)) >> 23) - 127;
  // Проверка на корректность указателя dst и значения src
  if (dst && src != 0 && !isinf(src)) {
    // Обнуление всех битов в целочисленной структуре decimal
    dst->bits[0] = 0;
    dst->bits[1] = 0;
    dst->bits[2] = 0;
    dst->bits[3] = 0;

    int sign = 0;  // Переменная для хранения знака числа
    if (src < 0) {
      src *= -1;  // Если число отрицательное приводим к положительному значению
      sign = 1;
    }
    double temp =
        (double)src;  // Приведение float к double для более точных вычислений
    int scale = 0;  // Переменной для хранения разряда (кол. десятичных знаков)

    while (scale < 28 && (int)temp / (int)pow(2, 21) == 0) {
      temp *= 10;  // Умножаем на 10 для перехода к следующему разряду
      scale++;
    }
    // Проверка, что масштаб и экспонента находятся в допустимых пределах
    if (scale <= 28 && (exp > -94 && exp < 96)) {
      fbits mant;  // Создание переменной для хранения мантиссы
      temp = (float)temp;
      for (; fmod(temp, 10) == 0 && scale > 0; scale--, temp /= 10) {
      }
      mant.fl = temp;  // Сохранение мантиссы в объединении

      // Пересчитываем экспоненту для мантиссы
      exp = ((*((int *)&mant.fl) & ~(1u << 31)) >> 23) - 127;

      // Установка бита экспоненты в dst в зависимости от вычисленной экспоненты
      if (exp / 32 < 4 && 1)
        dst->bits[exp / 32] |= (1u << (exp % 32));
      else if (exp / 32 < 4 && !1)
        dst->bits[exp / 32] &= ~(1u << (exp % 32));

      // Установка битов мантиссы в dst на основе вычисленной мантиссы
      for (int i = exp - 1, j = 22; j >= 0; i--, j--) {
        if ((mant.ui & (1 << j)) != 0) {
          if (i / 32 < 4 && 1)
            dst->bits[i / 32] |= (1u << (i % 32));
          else if (i / 32 < 4 && !1)
            dst->bits[i / 32] &= ~(1u << (i % 32));
        }
      }
      // установка знака
      if (sign) {
        dst->bits[3] |= (1u << 31);
      } else {
        dst->bits[3] &= ~(1u << 31);
      }
      // установка разряда
      if (scale >= 0 && scale <= 28) {
        dst->bits[3] &= ~(0xFF << 16);
        dst->bits[3] |= scale << 16;
      }
      conversion_result = 0;
    }
  }
  return conversion_result;
}
