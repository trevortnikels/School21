#include "../s21_string.h"

void *s21_to_lower(const char *str) {
  int i = 0;
  char *buff = (char *)malloc(s21_strlen(str) + 1);
  while (buff != s21_NULL && str[i] != '\0') {
    if (str[i] >= 'A' && str[i] <= 'Z')
      buff[i] = str[i] + 32;
    else
      buff[i] = str[i];
    i++;
  }
  buff[i] = '\0';
  return buff;
}