#include "../s21_matrix.h"

int s21_mult_matrix(matrix_t *A, matrix_t *B, matrix_t *result) {
  if (s21_validate_matrix(2, A, B) || result == NULL) {
    return INCORRECT_MATRIX;
  } else if (A->columns != B->rows) {
    return CALCULATION_ERROR;
  }

  int error_code = OK;
  error_code = s21_create_matrix(A->rows, B->columns, result);
  if (!error_code) {
    for (int i = 0; i < result->rows && error_code == OK; i++) {
      for (int j = 0; j < result->columns && error_code == OK; j++) {
        result->matrix[i][j] = s21_mult_matrix_res(i, j, A, B);
        if (!isfinite(result->matrix[i][j])) {
          error_code = CALCULATION_ERROR;
        }
      }
    }
  }

  return error_code;
}