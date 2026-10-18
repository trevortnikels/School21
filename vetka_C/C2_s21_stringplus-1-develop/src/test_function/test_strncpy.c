#include "s21_test.h"

START_TEST(strncpy_1) {
  char s1[20] = "Kurva Ujik!";
  char s2[20] = "Kurva Ujik!";
  char s3[] = "Cool day";
  s21_size_t n = 5;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_2) {
  char s1[20] = "Kurva Ujik!";
  char s2[20] = "Kurva Ujik!";
  char s3[] = "\0";
  s21_size_t n = 1;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_3) {
  char s1[30] = "Kurva Ujik!";
  char s2[30] = "Kurva Ujik!";
  char s3[] = "maf-maf-gav";
  s21_size_t n = 1;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_4) {
  char s1[5] = "";
  char s2[5] = "";
  char s3[] = "";
  s21_size_t n = 0;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_5) {
  char s1[70] = "";
  char s2[70] = "";
  char s3[] = "bebebe bababa";
  s21_size_t n = strlen(s3);
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_6) {
  char s1[5] = "";
  char s2[5] = "";
  char s3[] = "\0";
  s21_size_t n = 1;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_7) {
  char s1[70] = "";
  char s2[70] = "";
  char s3[] = "bebebe bababa";
  s21_size_t n = 3;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_8) {
  char s1[70] = "";
  char s2[70] = "";
  char s3[] = "bulbas";
  s21_size_t n = 2;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_9) {
  char s1[70] = "";
  char s2[70] = "";
  char s3[] = "try later";
  s21_size_t n = 4;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

START_TEST(strncpy_10) {
  char s1[70] = "";
  char s2[70] = "";
  char s3[] = "bombim";
  s21_size_t n = 5;
  ck_assert_pstr_eq(strncpy(s1, s3, n), s21_strncpy(s2, s3, n));
}
END_TEST

Suite *test_strncpy(void) {
  Suite *s = suite_create("\033[45m S21_STRNCPY \033[0m");
  TCase *tc = tcase_create("strncpy_tc");

  tcase_add_test(tc, strncpy_1);
  tcase_add_test(tc, strncpy_2);
  tcase_add_test(tc, strncpy_3);
  tcase_add_test(tc, strncpy_4);
  tcase_add_test(tc, strncpy_5);
  tcase_add_test(tc, strncpy_6);
  tcase_add_test(tc, strncpy_7);
  tcase_add_test(tc, strncpy_8);
  tcase_add_test(tc, strncpy_9);
  tcase_add_test(tc, strncpy_10);

  suite_add_tcase(s, tc);
  return s;
}