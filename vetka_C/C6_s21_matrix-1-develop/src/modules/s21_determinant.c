#include "../s21_matrix.h"

int s21_determinant(matrix_t *A, double *result) {
  if (A == NULL || A->matrix == NULL || result == NULL) {
    return INCORRECT_MATRIX;
  } else if (!s21_is_matrix_square(A)) {
    return CALCULATION_ERROR;
  }

  int error_code = OK;

  if (A->rows == 1) {
    *result = A->matrix[0][0];
  } else if (A->rows == 2) {
    *result =
        A->matrix[0][0] * A->matrix[1][1] - A->matrix[1][0] * A->matrix[0][1];
  } else if (A->rows > 2) {
    int sign = 1;
    *result = 0;
    for (int i = 0; i < A->columns && error_code == OK; i++) {
      matrix_t *minor = s21_create_minor(0, i, A);
      if (minor == NULL) {
        error_code = INCORRECT_MATRIX;
      } else {
        double minor_det = 0;
        error_code = s21_determinant(minor, &minor_det);
        if (!error_code) {
          *result += sign * A->matrix[0][i] * minor_det;
          sign = -sign;
        }
        s21_remove_matrix(minor);
        free(minor);
        minor = NULL;
      }
    }
  }

  return error_code;
}