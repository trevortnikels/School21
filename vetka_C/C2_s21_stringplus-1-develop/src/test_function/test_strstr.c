#include "s21_test.h"

START_TEST(test_strstr_find_word) {
  char *expected = strstr("Hello world!", "world");
  char *str_res = s21_strstr("Hello world!", "world");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_dont_find_word) {
  char *expected = strstr("Hello world!", "boba");
  char *str_res = s21_strstr("Hello world!", "boba");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_empty_searchword) {
  char *expected = strstr("Hello world!", "");
  char *str_res = s21_strstr("Hello world!", "");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_more_than_one) {
  char *expected = strstr("hi hi hi", "hi");
  char *str_res = s21_strstr("hi hi hi", "hi");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_not_same_case) {
  char *expected = strstr("hi hi hi", "Hi");
  char *str_res = s21_strstr("hi hi hi", "Hi");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_all_empty) {
  char *expected = strstr("", "");
  char *str_res = s21_strstr("", "");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_empty_first) {
  char *expected = strstr("", "Hello");
  char *str_res = s21_strstr("", "Hello");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_high_case) {
  char *expected = strstr("ABCabc", "AB");
  char *str_res = s21_strstr("ABCabc", "AB");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_high_one) {
  char *expected = strstr("H", "H");
  char *str_res = s21_strstr("H", "H");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_long_high) {
  char *expected = strstr("qwertyuiopQWERTYUIOP{}|\":<>?", "YTREWQ");
  char *str_res = s21_strstr("qwertyuiopQWERTYUIOP{}|\":<>?", "YTREWQ");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_terminator) {
  char *expected = strstr("Hello\0world", "world");
  char *str_res = s21_strstr("Hello\0world", "world");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_digit) {
  char *expected = strstr("12345", "34");
  char *str_res = s21_strstr("12345", "34");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_symbols) {
  char *expected = strstr("!@#$", "@");
  char *str_res = s21_strstr("!@#$", "@");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

START_TEST(test_strstr_tab) {
  char *expected = strstr("Hello\tworld", "world");
  char *str_res = s21_strstr("Hello\tworld", "world");
  ck_assert_pstr_eq(str_res, expected);
}
END_TEST

Suite *test_strstr() {
  Suite *s = suite_create("\033[45m S21_STRSTR \033[0m");
  TCase *tc = tcase_create("strstr_tc");

  tcase_add_test(tc, test_strstr_find_word);
  tcase_add_test(tc, test_strstr_dont_find_word);
  tcase_add_test(tc, test_strstr_empty_searchword);
  tcase_add_test(tc, test_strstr_more_than_one);
  tcase_add_test(tc, test_strstr_not_same_case);
  tcase_add_test(tc, test_strstr_all_empty);
  tcase_add_test(tc, test_strstr_empty_first);
  tcase_add_test(tc, test_strstr_high_case);
  tcase_add_test(tc, test_strstr_high_one);
  tcase_add_test(tc, test_strstr_long_high);
  tcase_add_test(tc, test_strstr_terminator);
  tcase_add_test(tc, test_strstr_digit);
  tcase_add_test(tc, test_strstr_symbols);
  tcase_add_test(tc, test_strstr_tab);

  suite_add_tcase(s, tc);
  return s;
}