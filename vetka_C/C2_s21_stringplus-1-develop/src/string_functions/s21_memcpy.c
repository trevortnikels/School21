#include "../s21_string.h"

void *s21_memcpy(void *destination, const void *source, s21_size_t n) {
  unsigned char *dest = (unsigned char *)destination;
  const unsigned char *src = (const unsigned char *)source;

  for (s21_size_t i = 0; i < n; i++) {
    dest[i] = src[i];
  }

  return dest;
}