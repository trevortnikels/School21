#include "../s21_matrix.h"

int s21_calc_complements(matrix_t *A, matrix_t *result) {
  if (A == NULL || A->matrix == NULL || result == NULL) {
    return INCORRECT_MATRIX;
  } else if (A->rows == 1 || A->columns == 1) {
    return CALCULATION_ERROR;
  }

  int error_code = OK;
  error_code = s21_create_matrix(A->rows, A->columns, result);
  if (!error_code) {
    for (int i = 0; i < A->rows && error_code == OK; i++) {
      int sign = i % 2 == 0 ? 1 : -1;
      for (int j = 0; j < A->columns && error_code == OK; j++) {
        matrix_t *minor = s21_create_minor(i, j, A);
        if (minor == NULL) {
          error_code = INCORRECT_MATRIX;
        } else {
          double det = 0;
          error_code = s21_determinant(minor, &det);
          if (!isfinite(det)) {
            error_code = CALCULATION_ERROR;
          }
          if (!error_code) {
            result->matrix[i][j] = sign * det;
            sign = -sign;
          }
          s21_remove_matrix(minor);
          free(minor);
          minor = NULL;
        }
      }
    }
  }

  return error_code;
}