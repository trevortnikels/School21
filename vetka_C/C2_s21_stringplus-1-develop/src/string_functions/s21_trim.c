#include "../s21_string.h"

void *s21_trim(const char *src, const char *trim_chars) {
  char *res = s21_NULL;

  if (src) {
    if (trim_chars && *trim_chars) {
      int indx_start = 0;
      int indx_end = s21_strlen(src) - 1;

      while (src[indx_start] && s21_strchr(trim_chars, src[indx_start]))
        indx_start++;

      if (src[indx_start]) {
        while (s21_strchr(trim_chars, src[indx_end])) indx_end--;

        res = calloc(indx_end - indx_start + 2, sizeof(char));

        for (int i = 0; indx_start <= indx_end; i++, indx_start++)
          res[i] = src[indx_start];
      } else
        res = calloc(1, sizeof(char));
    } else
      res = s21_trim(src, "\t\n ");
  }
  return res;
}