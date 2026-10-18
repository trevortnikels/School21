
#include "../s21_matrix.h"

int s21_mult_number(matrix_t *A, double number, matrix_t *result) {
  if (A == NULL || A->matrix == NULL || result == NULL) {
    return INCORRECT_MATRIX;
  } else if (!isfinite(number)) {
    return CALCULATION_ERROR;
  }

  int error_code = OK;
  error_code = s21_create_matrix(A->rows, A->columns, result);
  if (!error_code) {
    for (int i = 0; i < A->rows && error_code == OK; i++) {
      for (int j = 0; j < A->columns && error_code == OK; j++) {
        result->matrix[i][j] = A->matrix[i][j] * number;
        if (!isfinite(result->matrix[i][j])) {
          error_code = CALCULATION_ERROR;
        }
      }
    }
  }

  return error_code;
}
