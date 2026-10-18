#include "s21_test.h"

START_TEST(test_trim_with_correct_input) {
  char *src = "   hello world   ";
  char *trim_chars = " ";
  char *expected = "hello world";
  char *result = s21_trim(src, trim_chars);
  ck_assert_str_eq(result, expected);
  free(result);
}
END_TEST

START_TEST(test_trim_with_no_trim_chars) {
  char *src = "hello world";
  char *trim_chars = " ";
  char *expected = "hello world";
  char *result = s21_trim(src, trim_chars);
  ck_assert_str_eq(result, expected);
  free(result);
}
END_TEST

START_TEST(test_trim_with_all_trim_chars) {
  char *src = "   ";
  char *trim_chars = " ";
  char *expected = "";
  char *result = s21_trim(src, trim_chars);
  ck_assert_str_eq(result, expected);
  free(result);
}
END_TEST

START_TEST(test_trim_with_empty_string) {
  char *src = "";
  char *trim_chars = " ";
  char *expected = "";
  char *result = s21_trim(src, trim_chars);
  ck_assert_str_eq(result, expected);
  free(result);
}
END_TEST

START_TEST(test_trim_with_null_src) {
  char *src = NULL;
  char *trim_chars = " ";
  char *result = s21_trim(src, trim_chars);
  ck_assert_ptr_eq(result, NULL);
}
END_TEST

Suite *test_trim(void) {
  Suite *s = suite_create("\033[45m S21_TRIM \033[0m");
  TCase *tc = tcase_create("trim_tc");

  tcase_add_test(tc, test_trim_with_correct_input);
  tcase_add_test(tc, test_trim_with_no_trim_chars);
  tcase_add_test(tc, test_trim_with_all_trim_chars);
  tcase_add_test(tc, test_trim_with_empty_string);
  tcase_add_test(tc, test_trim_with_null_src);

  suite_add_tcase(s, tc);
  return s;
}
