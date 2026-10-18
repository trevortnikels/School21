#include "s21_test.h"

START_TEST(strcspn_1) {
  char s1[] = "kurva ejik, kurva ejik";
  char s2[] = "kurva ejik";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

START_TEST(strcspn_2) {
  char s1[] = "kurva";
  char s2[] = "kurva";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

START_TEST(strcspn_3) {
  char s1[] = "";
  char s2[] = "kurva";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

START_TEST(strcspn_4) {
  char s1[] = "kurva";
  char s2[] = "";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

START_TEST(strcspn_5) {
  char s1[] = "kurva";
  char s2[] = "a";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}

START_TEST(strcspn_6) {
  char s1[] = "a";
  char s2[] = "kurva";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

START_TEST(strcspn_7) {
  char s1[] = "a";
  char s2[] = "a";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

START_TEST(strcspn_8) {
  char s1[] = "";
  char s2[] = "";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

START_TEST(strcspn_9) {
  char s1[] = "abc";
  char s2[] = "def";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}

START_TEST(strcspn_10) {
  char s1[] = "12345";
  char s2[] = "123";
  ck_assert_int_eq(strcspn(s1, s2), s21_strcspn(s1, s2));
}
END_TEST

Suite *test_strcspn(void) {
  Suite *s = suite_create("\033[45m S21_STRNCMP \033[0m");
  TCase *tc = tcase_create("strcspn_tc");

  tcase_add_test(tc, strcspn_1);
  tcase_add_test(tc, strcspn_2);
  tcase_add_test(tc, strcspn_3);
  tcase_add_test(tc, strcspn_4);
  tcase_add_test(tc, strcspn_5);
  tcase_add_test(tc, strcspn_6);
  tcase_add_test(tc, strcspn_7);
  tcase_add_test(tc, strcspn_8);
  tcase_add_test(tc, strcspn_9);
  tcase_add_test(tc, strcspn_10);

  suite_add_tcase(s, tc);
  return s;
}