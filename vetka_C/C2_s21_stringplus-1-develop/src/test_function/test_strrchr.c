#include "s21_test.h"

START_TEST(strrchr_1) {
  char s[] = "Hello, World!";
  int ch = 'o';
  ck_assert_pstr_eq(strrchr(s, ch), s21_strrchr(s, ch));
}
END_TEST

START_TEST(strrchr_2) {
  char s[] = "Hello, World!";
  int ch = 'l';
  ck_assert_pstr_eq(strrchr(s, ch), s21_strrchr(s, ch));
}
END_TEST

START_TEST(strrchr_3) {
  char s[] = "Hello, World!";
  int ch = '5';
  ck_assert_pstr_eq(strrchr(s, ch), s21_strrchr(s, ch));
}
END_TEST

START_TEST(strrchr_4) {
  char s[] = "Hello, World!";
  int ch = ',';
  ck_assert_pstr_eq(strrchr(s, ch), s21_strrchr(s, ch));
}
END_TEST

START_TEST(strrchr_5) {
  char s[] = "bobr kurva!";
  int ch = '!';
  ck_assert_pstr_eq(strrchr(s, ch), s21_strrchr(s, ch));
}
END_TEST

Suite *test_strrchr(void) {
  Suite *s = suite_create("\033[45m S21_STRRCHR \033[0m");
  TCase *tc = tcase_create("strrchr_tc");

  tcase_add_test(tc, strrchr_1);
  tcase_add_test(tc, strrchr_2);
  tcase_add_test(tc, strrchr_3);
  tcase_add_test(tc, strrchr_4);
  tcase_add_test(tc, strrchr_5);

  suite_add_tcase(s, tc);

  return s;
}