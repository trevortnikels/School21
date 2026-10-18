#include "../s21_string.h"

s21_size_t s21_strcspn(const char *str, const char *sym) {
  s21_size_t i;

  for (i = 0; str[i] && !s21_strchr(sym, str[i]); i++)
    ;
  return i;
}