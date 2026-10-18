#include "../s21_string.h"

void *s21_memset(void *destination, int value, s21_size_t num) {
  unsigned char *p = (unsigned char *)destination;
  unsigned char v = (unsigned char)value;

  for (s21_size_t i = 0; i < num; i++) {
    p[i] = v;
  }

  return destination;
}