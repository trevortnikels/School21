#include "../s21_string.h"

char *s21_strchr(const char *str, int c) {
  while (*str != '\0' && *str != c) {
    str++;
  }
  return (*str == c) ? (char *)str : s21_NULL;
}