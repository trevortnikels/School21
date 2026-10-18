#include "../s21_matrix.h"

int s21_inverse_matrix(matrix_t *A, matrix_t *result) {
  if (A == NULL || A->matrix == NULL || result == NULL) {
    return INCORRECT_MATRIX;
  }

  int error_code = OK;
  double det = 0;
  error_code = s21_determinant(A, &det);
  if (!error_code && det != 0 && s21_is_matrix_square(A)) {
    if (A->rows == 1) {
      error_code = s21_create_matrix(A->rows, A->columns, result);
      if (!error_code) {
        result->matrix[0][0] = 1 / A->matrix[0][0];
      }
    } else {
      matrix_t temp_algebraic_complements = {0};
      matrix_t transposed_temp_algebraic_complements = {0};
      error_code = s21_calc_complements(A, &temp_algebraic_complements);
      if (!error_code) {
        error_code = s21_transpose(&temp_algebraic_complements,
                                   &transposed_temp_algebraic_complements);
      }
      if (!error_code) {
        error_code = s21_mult_number(&transposed_temp_algebraic_complements,
                                     1 / det, result);
      }
      s21_remove_matrix(&temp_algebraic_complements);
      s21_remove_matrix(&transposed_temp_algebraic_complements);
    }
  } else {
    error_code = CALCULATION_ERROR;
  }

  return error_code;
}