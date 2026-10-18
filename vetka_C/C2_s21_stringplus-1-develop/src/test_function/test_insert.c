#include "s21_test.h"

START_TEST(test_insert_null_src) {
  char *str_res = (s21_insert(s21_NULL, "world", 0));
  ck_assert_pstr_eq(str_res, s21_NULL);
  free(str_res);
}
END_TEST

START_TEST(test_insert_at_start) {
  char *src = "world";
  char *str = "hello ";
  s21_size_t start_index = 0;
  char *expected = "hello world";
  char *str_res = s21_insert(src, str, start_index);
  ck_assert_pstr_eq(str_res, expected);
  free(str_res);
}
END_TEST

START_TEST(test_insert_at_end) {
  char *src = "hello";
  char *str = " world";
  s21_size_t start_index = 5;
  char *expected = "hello world";
  char *str_res = s21_insert(src, str, start_index);
  ck_assert_pstr_eq(str_res, expected);
  free(str_res);
}
END_TEST

START_TEST(test_insert_with_empty_src) {
  char *src = "";
  char *str = "hello";
  s21_size_t start_index = 0;
  char *expected = "hello";
  char *str_res = s21_insert(src, str, start_index);
  ck_assert_pstr_eq(str_res, expected);
  free(str_res);
}
END_TEST

START_TEST(test_insert_with_null_src) {
  char *src = s21_NULL;
  char *str = "hello";
  s21_size_t start_index = 0;
  char *str_res = s21_insert(src, str, start_index);
  ck_assert_pstr_eq(str_res, s21_NULL);
  free(str_res);
}
END_TEST

START_TEST(test_insert_with_null_str) {
  char *src = "hello";
  char *str = s21_NULL;
  s21_size_t start_index = 0;
  char *expected = s21_NULL;
  char *str_res = s21_insert(src, str, start_index);
  ck_assert_pstr_eq(str_res, expected);
  free(str_res);
}
END_TEST

START_TEST(test_whith_0) {
  char *src = "\0";
  char *str = "\0";
  s21_size_t star_index = 0;
  char *expected = "\0";
  char *str_res = s21_insert(src, str, star_index);
  ck_assert_pstr_eq(str_res, expected);
  free(str_res);
}
END_TEST

Suite *test_insert(void) {
  Suite *s = suite_create("\033[45m S21_INSERT \033[0m");
  TCase *tc = tcase_create("insert_tc");

  tcase_add_test(tc, test_insert_null_src);
  tcase_add_test(tc, test_insert_at_start);
  tcase_add_test(tc, test_insert_at_end);
  tcase_add_test(tc, test_insert_with_empty_src);
  tcase_add_test(tc, test_insert_with_null_src);
  tcase_add_test(tc, test_insert_with_null_str);
  tcase_add_test(tc, test_whith_0);

  suite_add_tcase(s, tc);
  return s;
}