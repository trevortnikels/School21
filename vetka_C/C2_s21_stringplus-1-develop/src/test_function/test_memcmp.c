#include "s21_test.h"

START_TEST(memcmp_1) {
  char s1[] = "ratatui!";
  char s2[] = "ratatui!";
  s21_size_t n = 0;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_2) {
  char s1[] = "yes";
  char s2[] = "yes";
  s21_size_t n = 1;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_3) {
  char s1[] = "bim";
  char s2[] = "bim";
  s21_size_t n = 2;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_4) {
  char s1[] = "Hello, world!";
  char s2[] = "Hello, world!";
  s21_size_t n = 14;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_5) {
  char s1[] = "Kurva Pinguin!";
  char s2[] = "Kurva Pinguin!";
  s21_size_t n = 14;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_6) {
  char s1[] = "123456789";
  char s2[] = "123456789";
  s21_size_t n = 0;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_7) {
  char s1[] = "123456789";
  char s2[] = "123456789";
  s21_size_t n = 1;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_8) {
  char s1[] = "123456789";
  char s2[] = "123456789";
  s21_size_t n = 9;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_9) {
  char s1[] = "123456789";
  char s2[] = "123456789";
  s21_size_t n = 10;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_10) {
  char s1[] = "123456789";
  char s2[] = "1234K6789";
  s21_size_t n = 1;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_11) {
  char s1[] = "12345 6789";
  char s2[] = "12345 6789";
  s21_size_t n = 5;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_12) {
  char s1[] = "123456789";
  char s2[] = "123456789";
  s21_size_t n = 10;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_13) {
  char s1[] = "Сравнивает первые n байтов str1 и str2.";
  char s2[] = "Сравнивает первые n байтов str1 и str2.";
  s21_size_t n = 2;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_14) {
  char s1[] = "Сравнивает первые n байтов str1\0 и str2.";
  char s2[] = "Сравнивает первые n байтов str1\0 и str2.";
  s21_size_t n = 32;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

START_TEST(memcmp_15) {
  char s1[] = "";
  char s2[] = "";
  s21_size_t n = 0;
  int n1 = memcmp(s1, s2, n);
  int n2 = s21_memcmp(s1, s2, n);
  ck_assert_int_eq(n1, n2);
}
END_TEST

Suite *test_memcmp(void) {
  Suite *s = suite_create("\033[45m S21_MEMCMP \033[0m");
  TCase *tc = tcase_create("memcmp_tc");

  tcase_add_test(tc, memcmp_1);
  tcase_add_test(tc, memcmp_2);
  tcase_add_test(tc, memcmp_3);
  tcase_add_test(tc, memcmp_4);
  tcase_add_test(tc, memcmp_5);
  tcase_add_test(tc, memcmp_6);
  tcase_add_test(tc, memcmp_7);
  tcase_add_test(tc, memcmp_8);
  tcase_add_test(tc, memcmp_9);
  tcase_add_test(tc, memcmp_10);
  tcase_add_test(tc, memcmp_11);
  tcase_add_test(tc, memcmp_12);
  tcase_add_test(tc, memcmp_13);
  tcase_add_test(tc, memcmp_14);
  tcase_add_test(tc, memcmp_15);

  suite_add_tcase(s, tc);
  return s;
}