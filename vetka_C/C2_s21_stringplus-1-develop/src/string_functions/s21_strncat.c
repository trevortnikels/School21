#include "../s21_string.h"

char *s21_strncat(char *destination, const char *append, s21_size_t n) {
  char *dest = destination;

  while (*dest != '\0') {
    dest++;
  }

  while (*append != '\0' && n > 0) {
    *dest++ = *append++;
    n--;
  }

  *dest = '\0';
  return destination;
}