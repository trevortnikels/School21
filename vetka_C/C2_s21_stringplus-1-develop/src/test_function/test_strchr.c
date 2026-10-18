#include "s21_test.h"

START_TEST(strchr_1) {
  char str_src[] = "Kurva Pinguin!";
  int ch = 'v';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_2) {
  char str_src[] = "Kurva Pinguin!";
  int ch = '\0';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_3) {
  char str_src[] = "Kurva Pinguin!";
  int ch = '!';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_4) {
  char str_src[] = "Kurva Pinguin!";
  int ch = 33;
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_5) {
  char str_src[] = "Kurva Pinguin!";
  int ch = 'P';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_6) {
  char str_src[] = "Kurva Pinguin!";
  int ch = 'w';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_7) {
  char str_src[] = "Kurva Pinguin!";
  int ch = '0';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_8) {
  char str_src[] = "Kurva Pinguin!";
  int ch = 'm';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_9) {
  char str_src[] = "Kurva Pinguin!";
  int ch = 'l';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

START_TEST(strchr_10) {
  char str_src[] = "Kurva Pinguin!";
  int ch = 'd';
  ck_assert_pstr_eq(strchr(str_src, ch), s21_strchr(str_src, ch));
}
END_TEST

Suite *test_strchr(void) {
  Suite *str_src = suite_create("\033[45m S21_STRCHR \033[0m");
  TCase *tc = tcase_create("strchr_tc");

  suite_add_tcase(str_src, tc);
  tcase_add_test(tc, strchr_1);
  tcase_add_test(tc, strchr_2);
  tcase_add_test(tc, strchr_3);
  tcase_add_test(tc, strchr_4);
  tcase_add_test(tc, strchr_5);
  tcase_add_test(tc, strchr_6);
  tcase_add_test(tc, strchr_7);
  tcase_add_test(tc, strchr_8);
  tcase_add_test(tc, strchr_9);
  tcase_add_test(tc, strchr_10);

  suite_add_tcase(str_src, tc);
  return str_src;
}