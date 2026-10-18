#include "s21_test.h"

int main(void) {
  int failed = 0;
  Suite *s21_string[] = {

      test_memchr(),  test_memcmp(),   test_memcpy(), test_memset(),
      test_strncat(), test_strncmp(),  test_strchr(), test_strncpy(),
      test_strcspn(), test_strerror(), test_strlen(), test_strpbrk(),
      test_strrchr(), test_lower(),    test_trim(),   test_upper(),
      test_insert(),  test_strstr(),   test_strtok(), test_sprintf(),
      s21_NULL};

  for (int i = 0; s21_string[i] != s21_NULL; i++) {
    SRunner *sr = srunner_create(s21_string[i]);

    srunner_set_fork_status(sr, CK_NOFORK);
    srunner_run_all(sr, CK_NORMAL);

    failed += srunner_ntests_failed(sr);
    srunner_free(sr);
  }
  printf("========= FAILED: %d =========\n", failed);

  return failed == 0 ? 0 : 1;
}