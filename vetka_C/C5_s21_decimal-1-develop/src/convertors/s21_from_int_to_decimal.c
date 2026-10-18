#include "../s21_decimal.h"

/*
 * объединение для получения доступа к данным bits[3]
 * 16 бит: Биты от 0 до 15, не используются и должны быть равны нулю.
 * 8 бит: Биты с 16 по 23 должны содержать показатель степени от 0 до 28.
 * 7 бит: Биты с 24 по 30 не используются и должны быть равны нулю.
 * 1 бит: Бит 31 содержит знак; 0 означает положительный, а 1 означает
 * отрицательный. Итого 32 бита
 */
typedef union dst_bit_3 {
  int mask;
  struct {
    uint32_t empty_2 : 16;
    uint32_t degree : 8;
    uint32_t empty_1 : 7;
    uint32_t sign : 1;
  } parts;
} dst_bit_3;

int s21_from_int_to_decimal(int src, s21_decimal *dst) {
  int conversion_result = 0;

  if (!dst) {
    // Если указатель на decimal является NULL
    conversion_result = 1;
  } else {
    // зануляем dst
    dst->bits[0] = 0;
    dst->bits[1] = 0;
    dst->bits[2] = 0;
    dst->bits[3] = 0;

    int sign;

    if (src < 0) {
      sign = 1;

      // INT_MIN представляет минимально целое число со знаком, которое может
      // быть в типе данных int. -2147483648 или близко к нему для 32-битных
      // систем.
      if (src != INT_MIN) {
        src = -src;
      }
    } else {
      sign = 0;
    }

    dst->bits[0] = src;

    // Определяем знак результата, исходя из знака числа src (типа int)
    // меняемый sign устанавливаемый знак, 1 - отрицательный
    // 0 - положительный. Любой sign, отличный от 0, установит знак 1
    dst_bit_3 bits3;
    bits3.mask = dst->bits[3];
    if (sign == 0) {
      bits3.parts.sign = 0;
    } else {
      bits3.parts.sign = 1;
    }
    dst->bits[3] = bits3.mask;
  }

  return conversion_result;
}
