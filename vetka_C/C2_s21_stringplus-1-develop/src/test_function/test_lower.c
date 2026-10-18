#include "s21_test.h"

START_TEST(test_to_lower) {
  char *str = "HELLO, WORLD!";
  char *expected = "hello, world!";
  char *result = s21_to_lower(str);
  ck_assert_str_eq(result, expected);
  free(result);
}
END_TEST

Suite *test_lower(void) {
  Suite *s = suite_create("\033[45m S21_LOWER \033[0m");
  TCase *tc = tcase_create("lower_tc");

  tcase_add_test(tc, test_to_lower);

  suite_add_tcase(s, tc);
  return s;
}