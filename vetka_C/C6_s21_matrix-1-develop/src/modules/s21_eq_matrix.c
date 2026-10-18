#include "../s21_matrix.h"

int s21_eq_matrix(matrix_t *A, matrix_t *B) {
  if (!s21_is_matrix_same_size(2, A, B) || s21_validate_matrix(2, A, B)) {
    return FAILURE;
  }

  int comparison_status = SUCCESS;

  for (int i = 0; i < A->rows && comparison_status == SUCCESS; i++) {
    for (int j = 0; j < A->columns && comparison_status == SUCCESS; j++) {
      if ((fabs(A->matrix[i][j] - B->matrix[i][j])) >= 1e-7) {
        comparison_status = FAILURE;
      }
    }
  }

  return comparison_status;
}