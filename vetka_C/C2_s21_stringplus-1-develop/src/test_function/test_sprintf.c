#include "s21_test.h"

#define BUFFER_SIZE 1024

START_TEST(test_s21_sprintf_basic) {
  char buffer[BUFFER_SIZE];
  s21_sprintf(buffer, "Hello, %s!", "world");
  ck_assert_str_eq(buffer, "Hello, world!");
}
END_TEST

START_TEST(test_s21_sprintf_integer) {
  char buffer[BUFFER_SIZE];
  s21_sprintf(buffer, "Number: %d", 42);
  ck_assert_str_eq(buffer, "Number: 42");
}
END_TEST

START_TEST(test_s21_sprintf_float) {
  char buffer[BUFFER_SIZE];
  s21_sprintf(buffer, "Pi: %.2f", 3.14159);
  ck_assert_str_eq(buffer, "Pi: 3.14");
}
END_TEST

START_TEST(test_s21_sprintf_width) {
  char buffer[BUFFER_SIZE];
  s21_sprintf(buffer, "Width: %10d", 42);
  ck_assert_str_eq(buffer, "Width:         42");
}
END_TEST

START_TEST(test_s21_sprintf_flags) {
  char buffer[BUFFER_SIZE];
  s21_sprintf(buffer, "Sign: %+d", 42);
  ck_assert_str_eq(buffer, "Sign: +42");

  s21_sprintf(buffer, "Space: % d", 42);
  ck_assert_str_eq(buffer, "Space:  42");

  s21_sprintf(buffer, "Left: %-5d", 42);
  ck_assert_str_eq(buffer, "Left: 42   ");
}
END_TEST

START_TEST(test_s21_sprintf_length) {
  char buffer[BUFFER_SIZE];
  s21_sprintf(buffer, "Short: %hd", (short)32767);
  ck_assert_str_eq(buffer, "Short: 32767");

  s21_sprintf(buffer, "Long: %ld", 1234567890L);
  ck_assert_str_eq(buffer, "Long: 1234567890");
}
END_TEST

START_TEST(test_s21_sprintf_string) {
  char buffer[BUFFER_SIZE];
  s21_sprintf(buffer, "String: %s", "test");
  ck_assert_str_eq(buffer, "String: test");
}
END_TEST

START_TEST(width_char) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *formats[] = {
      "This is a simple wide char %5c",
      "This is a simple wide char %-5c",
      "This is a simple wide char %.2c",
      "This is a simple wide char %10c",
  };
  char characters[] = {'c', 'A', '$', '\n'};
  int num_formats = sizeof(formats) / sizeof(formats[0]);
  int num_chars = sizeof(characters) / sizeof(characters[0]);
  for (int i = 0; i < num_formats; ++i) {
    for (int j = 0; j < num_chars; ++j) {
      char w = characters[j];
      char *format = formats[i];

      int a = s21_sprintf(str1, format, w);
      int b = sprintf(str2, format, w);

      ck_assert_str_eq(str1, str2);
      ck_assert_int_eq(a, b);
    }
  }
}
END_TEST

START_TEST(sprintf_wchar) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];

  char *format = "%3lc";
  wchar_t longChar = 0x77;
  s21_sprintf(str1, format, longChar);
  sprintf(str2, format, longChar);
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(d_256) {
  char str1[BUFFER_SIZE], str2[BUFFER_SIZE];
  char format[] = "Decimal %hd, %d, %ld of different sizes.";
  short var1 = 0;
  int var2 = 0;
  long int var3 = 0;
  ck_assert_int_eq(s21_sprintf(str1, format, var1, var2, var3),
                   sprintf(str2, format, var1, var2, var3));
  ck_assert_str_eq(str1, str2);
  var1 = (short)INT32_MAX;
  var2 = INT32_MAX;
  var3 = INT64_MAX;
  ck_assert_int_eq(s21_sprintf(str1, format, var1, var2, var3),
                   sprintf(str2, format, var1, var2, var3));
  ck_assert_str_eq(str1, str2);
  var1 = (short)INT32_MIN;
  var2 = INT32_MIN;
  var3 = INT64_MIN;
  ck_assert_int_eq(s21_sprintf(str1, format, var1, var2, var3),
                   sprintf(str2, format, var1, var2, var3));
  ck_assert_str_eq(str1, str2);
  ck_assert_int_eq(s21_sprintf(str1, format, var3, var3, var3),
                   sprintf(str2, format, var3, var3, var3));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(d_flags) {
  char str1[BUFFER_SIZE], str2[BUFFER_SIZE];
  int var = 21;
  char *formats[] = {"Let's test flag combinations %-40d.",
                     "Let's test flag combinations %+d."};
  for (s21_size_t i = 0; i < sizeof(formats) / sizeof(formats[0]); i++) {
    ck_assert_int_eq(s21_sprintf(str1, formats[i], var),
                     sprintf(str2, formats[i], var));
    ck_assert_str_eq(str1, str2);
  }
}
END_TEST

START_TEST(u_flags) {
  char str1[BUFFER_SIZE], str2[BUFFER_SIZE];
  char *formats[] = {"Flags %+u unsigned.", "Flags % u unsigned.",
                     "Flags %-40u unsigned."};
  unsigned var = 32;
  for (s21_size_t i = 0; i < sizeof(formats) / sizeof(formats[0]); i++) {
    ck_assert_int_eq(s21_sprintf(str1, formats[i], var),
                     sprintf(str2, formats[i], var));
    ck_assert_str_eq(str1, str2);
  }
}
END_TEST

START_TEST(f_flags) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];

  char *format = "% 20f";
  double var = 99.9999999;
  ck_assert_int_eq(s21_sprintf(str1, format, var), sprintf(str2, format, var));
  ck_assert_str_eq(str1, str2);

  var = -99.9999999;
  format = "%-40f";
  ck_assert_int_eq(s21_sprintf(str1, format, var), sprintf(str2, format, var));
  ck_assert_str_eq(str1, str2);

  format = "%+-40f";
  ck_assert_int_eq(s21_sprintf(str1, format, var), sprintf(str2, format, var));
  ck_assert_str_eq(str1, str2);

  format = "%f% -40f";
  ck_assert_int_eq(s21_sprintf(str1, format, -var, var),
                   sprintf(str2, format, -var, var));
  ck_assert_str_eq(str1, str2);

  format = "%-040f";
  ck_assert_int_eq(s21_sprintf(str1, format, var), sprintf(str2, format, var));
  ck_assert_str_eq(str1, str2);

  format = "% -+040f";
  ck_assert_int_eq(s21_sprintf(str1, format, var), sprintf(str2, format, var));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(empty_format_and_parameters) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];

  ck_assert_int_eq(s21_sprintf(str1, "abc"), sprintf(str2, "abc"));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(char_precision) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "%.5c";
  char val = 'c';
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(char_flags) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "% -5c";
  char val = 'c';
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);

  format = "%-5.3c";
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);

  format = "%-5.3c";
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(char_width) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "%15c";
  char val = 'c';
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(string) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "%s";
  char *val = "0nce upon a midnight dreary, while I pondered, weak and weary";
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(string_precision) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "%.15s";
  char *val = "Over many a quaint and curious volume of forgotten lore --";
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(string_width) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "%15s";
  char *val = "While I nodded, nearly napping, suddenly there came a tapping,";
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(string_flags) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "%-15.9s";
  char *val = "As of some one gently rapping, rapping at my chamber door—";
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(string_long) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char *format = "%s";
  char *val =
      "<<'Tis some visitor,>> I muttered, << tapping at my chamber door —";
  ck_assert_int_eq(s21_sprintf(str1, format, val), sprintf(str2, format, val));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(test_one_char) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  ck_assert_int_eq(s21_sprintf(str1, "%c", '\t'), sprintf(str2, "%c", '\t'));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_one_string) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  ck_assert_int_eq(s21_sprintf(str1, "%s", "Drop Sega PLS"),
                   sprintf(str2, "%s", "Drop Sega PLS"));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(test_one_char_with_alignment_left) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  ck_assert_int_eq(s21_sprintf(str1, "%8c", '\t'), sprintf(str2, "%8c", '\t'));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_one_char_with_alignment_right) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  ck_assert_int_eq(s21_sprintf(str1, "%-8c", '\t'),
                   sprintf(str2, "%-8c", '\t'));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_sprintf2) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "%1.1f";
  ck_assert_int_eq(s21_sprintf(str1, format, 1.1), sprintf(str2, format, 1.1));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_sprintf3) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "%8.3c";
  ck_assert_int_eq(s21_sprintf(str1, format, 'a'), sprintf(str2, format, 'a'));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_sprintf6) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "%7.7f";
  ck_assert_int_eq(s21_sprintf(str1, format, 11.123456),
                   sprintf(str2, format, 11.123456));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_sprintf7) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "%7.4s";
  ck_assert_int_eq(s21_sprintf(str1, format, "aboba floppa"),
                   sprintf(str2, format, "aboba floppa"));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_sprintf16) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "% c";
  ck_assert_int_eq(s21_sprintf(str1, format, 'a'), sprintf(str2, format, 'a'));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_sprintf17) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "% s";
  ck_assert_int_eq(s21_sprintf(str1, format, "aboba likes floppa"),
                   sprintf(str2, format, "aboba likes floppa"));
  ck_assert_str_eq(str1, str2);
}
END_TEST

START_TEST(test_sprintf25) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "%.f";
  ck_assert_int_eq(s21_sprintf(str1, format, 121.123),
                   sprintf(str2, format, 121.123));
  ck_assert_str_eq(str1, str2);
}
END_TEST
START_TEST(test_sprintf29) {
  char str1[BUFFER_SIZE];
  char str2[BUFFER_SIZE];
  char format[] = "%-.f";
  ck_assert_int_eq(s21_sprintf(str1, format, 111.111),
                   sprintf(str2, format, 111.111));
  ck_assert_str_eq(str1, str2);
}
END_TEST

Suite *test_sprintf(void) {
  Suite *s = suite_create("\033[45m S21_SPRINTF \033[0m");
  TCase *tc = tcase_create("sprintf_tc");

  tcase_add_test(tc, test_s21_sprintf_basic);
  tcase_add_test(tc, test_s21_sprintf_integer);
  tcase_add_test(tc, test_s21_sprintf_float);
  tcase_add_test(tc, test_s21_sprintf_width);
  tcase_add_test(tc, test_s21_sprintf_flags);
  tcase_add_test(tc, test_s21_sprintf_length);
  tcase_add_test(tc, test_s21_sprintf_string);
  tcase_add_test(tc, width_char);
  tcase_add_test(tc, sprintf_wchar);
  tcase_add_test(tc, d_256);
  tcase_add_test(tc, d_flags);
  tcase_add_test(tc, u_flags);
  tcase_add_test(tc, f_flags);
  tcase_add_test(tc, empty_format_and_parameters);
  tcase_add_test(tc, char_precision);
  tcase_add_test(tc, char_flags);
  tcase_add_test(tc, char_width);
  tcase_add_test(tc, string);
  tcase_add_test(tc, string_precision);
  tcase_add_test(tc, string_width);
  tcase_add_test(tc, string_flags);
  tcase_add_test(tc, string_long);
  tcase_add_test(tc, test_one_char);
  tcase_add_test(tc, test_one_string);
  tcase_add_test(tc, test_one_char_with_alignment_left);
  tcase_add_test(tc, test_one_char_with_alignment_right);
  tcase_add_test(tc, test_sprintf2);
  tcase_add_test(tc, test_sprintf3);
  tcase_add_test(tc, test_sprintf6);
  tcase_add_test(tc, test_sprintf7);
  tcase_add_test(tc, test_sprintf16);
  tcase_add_test(tc, test_sprintf17);
  tcase_add_test(tc, test_sprintf25);
  tcase_add_test(tc, test_sprintf29);
  suite_add_tcase(s, tc);

  return s;
}