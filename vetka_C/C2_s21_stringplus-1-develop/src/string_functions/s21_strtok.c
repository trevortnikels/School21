#include "../s21_string.h"

char *s21_strtok(char *str, const char *delim) {
  if (delim == s21_NULL) return s21_NULL;

  static char *next_token = s21_NULL;
  char *token = s21_NULL;

  if (str) next_token = str;

  if (next_token) {
    while (*next_token && s21_strchr(delim, *next_token)) next_token++;

    if (*next_token != '\0') {
      token = next_token;

      while (*next_token && !s21_strchr(delim, *next_token)) next_token++;

      if (*next_token)
        *next_token++ = '\0';
      else
        next_token = s21_NULL;
    }
  }

  return token;
}
