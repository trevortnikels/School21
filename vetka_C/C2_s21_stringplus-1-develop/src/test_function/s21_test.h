#ifndef SRC_TESTS_ME_H
#define SRC_TESTS_ME_H

#include <check.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>

#include "../s21_string.h"

Suite *test_memchr(void);
Suite *test_memcmp(void);
Suite *test_memcpy(void);
Suite *test_memset(void);
Suite *test_strncat(void);
Suite *test_strncmp(void);
Suite *test_strchr(void);
Suite *test_strncpy(void);
Suite *test_strcspn(void);
Suite *test_strerror(void);
Suite *test_strlen(void);
Suite *test_strpbrk(void);
Suite *test_strrchr(void);
Suite *test_strstr();
Suite *test_strtok();

Suite *test_lower();
Suite *test_trim();
Suite *test_upper();
Suite *test_insert();

Suite *test_sprintf();

#endif