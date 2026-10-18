#include "../s21_decimal.h"

/*
 * объединение для получения доступа к данным bits[3]
 * 16 бит: Биты от 0 до 15, не используются равны нулю.
 * 8 бит: Биты с 16 по 23 содержат показатель степени от 0 до 28.
 * 7 бит: Биты с 24 по 30 не используются и равны нулю.
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

// Возвращает результат умножения value на -1.
int s21_negate(s21_decimal value, s21_decimal *result) {
  int conversion_result = 0;

  if (!result) {
    // Если указатель на decimal является NULL
    conversion_result = 1;
  } else {  // В остальных случаях меняем знак
    *result = value;

    dst_bit_3 bits3;
    bits3.mask = value.bits[3];
    // Получаем знак
    int sign = bits3.parts.sign;
    // Проверяме знак
    if (sign == 0) {
      bits3.parts.sign = 1;
    } else {
      bits3.parts.sign = 0;
    }
    // Записывем знак
    result->bits[3] = bits3.mask;

    // Проверяем корректность данных в bits[3]
    if (bits3.parts.empty_1 != 0 || bits3.parts.empty_2 != 0) {
      conversion_result = 1;
    } else {
      int power = bits3.parts.degree;
      if (power < 0 || power > 28) {
        conversion_result = 1;
      }
    }
  }

  return conversion_result;
}
