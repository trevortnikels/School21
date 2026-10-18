#include "../s21_string.h"

char *s21_strstr(const char *destptr, const char *srcptr) {
  s21_size_t srcptrLength = s21_strlen(srcptr);
  const char *result = s21_NULL;

  if (srcptrLength != 0) {
    for (s21_size_t x = 0; result == s21_NULL && destptr[x] != '\0'; x += 1) {
      if (destptr[x] == srcptr[0]) {
        if (s21_strncmp(destptr + x, srcptr, srcptrLength) == 0)
          result = destptr + x;
      }
    }
  } else {
    result = destptr;
  }

  return (char *)result;
}