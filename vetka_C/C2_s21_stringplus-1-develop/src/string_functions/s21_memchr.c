#include "../s21_string.h"

void *s21_memchr(const void *arr, int value, s21_size_t num) {
  const unsigned char *p = (const unsigned char *)arr;
  unsigned char v = (unsigned char)value;
  char *result = s21_NULL;

  for (s21_size_t i = 0; i < num; i++) {
    if (p[i] == v) {
      result = (char *)(p + i);
      i = num;
    }
  }

  return result;
}