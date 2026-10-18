#include "s21_test.h"

START_TEST(strlen_1) {
  char str[] = "kurva bobr";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_2) {
  char str[] = "";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_3) {
  char str[] = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_4) {
  char str[] = "a";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_5) {
  char str[] = "aaaaaa";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_6) {
  char str[] = "1234567890";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_7) {
  char str[] = "\0";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_8) {
  char str[] = "abc\0def";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_9) {
  char str[] = "abc\0def\0ghi";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_10) {
  char str[] = "\t\tn";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

START_TEST(strlen_11) {
  char str[] = "    123456    !@#$=^&*()_+  ";
  ck_assert_int_eq(strlen(str), s21_strlen(str));
}
END_TEST

Suite *test_strlen(void) {
  Suite *s = suite_create("\033[45m S21_STRNCAT \033[0m");
  TCase *tc = tcase_create("strlen_tc");

  tcase_add_test(tc, strlen_1);
  tcase_add_test(tc, strlen_2);
  tcase_add_test(tc, strlen_3);
  tcase_add_test(tc, strlen_4);
  tcase_add_test(tc, strlen_5);
  tcase_add_test(tc, strlen_6);
  tcase_add_test(tc, strlen_7);
  tcase_add_test(tc, strlen_8);
  tcase_add_test(tc, strlen_9);
  tcase_add_test(tc, strlen_10);
  tcase_add_test(tc, strlen_11);

  suite_add_tcase(s, tc);
  return s;
}
