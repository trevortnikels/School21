#ifndef S21_HELPER_FUNCTIONS
#define S21_HELPER_FUNCTIONS

#include "../s21_matrix.h"

int s21_validate_matrix(int matrix_amount, matrix_t* A, ...);

int s21_is_matrix_same_size(int matrix_amount, matrix_t* A, ...);

double s21_mult_matrix_res(int i, int j, matrix_t* A, matrix_t* B);

matrix_t* s21_create_minor(int excluded_row, int excluded_column, matrix_t* A);

int s21_is_matrix_square(matrix_t* A);

void s21_initialize_matrix(matrix_t* A, double start_value,
                           double iteration_step);

void s21_print_matrix(matrix_t* A);

#endif  // S21_HELPER_FUNCTIONS