#include "../s21_string.h"

int s21_memcmp(const void *arr1, const void *arr2, s21_size_t num) {
  const unsigned char *p1 = (const unsigned char *)arr1;
  const unsigned char *p2 = (const unsigned char *)arr2;
  int result = 0;
  for (s21_size_t i = 0; i < num && result == 0; i++) {
    result = (int)(p1[i] - p2[i]);
  }
  return result;
}