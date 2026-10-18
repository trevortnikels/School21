#include "s21_test.h"

START_TEST(test_strtok_all_string_with_anouther_strat) {
  char str1[] = "/testing/with/original/string.h/";
  char str2[] = "/testing/with/original/string.h/";
  char delim[3] = "/";
  char *expected = strtok(str1, delim);
  char *str_res = s21_strtok(str2, delim);
  while (expected != s21_NULL) {
    ck_assert_pstr_eq(str_res, expected);
    expected = strtok(s21_NULL, delim);
    str_res = s21_strtok(s21_NULL, delim);
  }
}
END_TEST

START_TEST(test_strtok_combo_delim) {
  char str1[] = "++++++++";
  char str2[] = "++++++++";
  char delim[] = "+_! =";
  char *expected = strtok(str1, delim);
  char *str_res = s21_strtok(str2, delim);
  ck_assert_ptr_null(str_res);
  ck_assert_ptr_null(expected);
}
END_TEST

START_TEST(test_strtok_lower_delim) {
  char str1[] = "Aboba_Floppa_test";
  char str2[] = "Aboba_Floppa_test";
  char delim[] = "+_! =";
  char *expected = strtok(str1, delim);
  char *str_res = s21_strtok(str2, delim);
  ck_assert_uint_eq(s21_strlen(str_res), s21_strlen(expected));
  ck_assert_str_eq(str_res, expected);
  int i = 5;
  while (i) {
    expected = strtok(s21_NULL, delim);
    str_res = s21_strtok(s21_NULL, delim);
    i--;
    if (str_res || expected) {
      ck_assert_str_eq(str_res, expected);
    } else {
      ck_assert_ptr_null(str_res);
      ck_assert_ptr_null(expected);
    }
  }
}
END_TEST

Suite *test_strtok() {
  Suite *s = suite_create("\033[45m S21_STRTOK \033[0m");
  TCase *tc = tcase_create("strtok_tc");

  tcase_add_test(tc, test_strtok_all_string_with_anouther_strat);
  tcase_add_test(tc, test_strtok_combo_delim);
  tcase_add_test(tc, test_strtok_lower_delim);

  suite_add_tcase(s, tc);
  return s;
}