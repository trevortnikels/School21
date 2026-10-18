#include "s21_test.h"

START_TEST(test_s21_to_upper) {
  char *str = "Hello, world!";
  char *expected = "HELLO, WORLD!";
  char *result = s21_to_upper(str);
  ck_assert_str_eq(result, expected);
  free(result);
}
END_TEST

Suite *test_upper(void) {
  Suite *s = suite_create("\033[45m S21_UPPER \033[0m");
  TCase *tc = tcase_create("upper_tc");

  tcase_add_test(tc, test_s21_to_upper);

  suite_add_tcase(s, tc);
  return s;
}