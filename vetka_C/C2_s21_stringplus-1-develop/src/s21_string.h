#ifndef SRC_S21_STRING_H
#define SRC_S21_STRING_H

#include <ctype.h>
#include <limits.h>
#include <locale.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>

typedef unsigned long s21_size_t;

#define s21_NULL ((void *)0)

void *s21_memchr(const void *arr, int value, s21_size_t num);
int s21_memcmp(const void *arr1, const void *arr2, s21_size_t num);
void *s21_memcpy(void *destination, const void *source, s21_size_t n);
void *s21_memmove(void *dest, const void *src, s21_size_t size);
void *s21_memset(void *arr, int value, s21_size_t num);
char *s21_strncat(char *destination, const char *append, s21_size_t n);
char *s21_strchr(const char *str, int symbol);
int s21_strcmp(const char *str_1, const char *str_2);
char *s21_strcpy(char *destptr, const char *srcptr);
s21_size_t s21_strcspn(const char *str, const char *sym);
char *s21_strerror(int errorNumber);
s21_size_t s21_strlen(const char *str);
int s21_strncmp(const char *str1, const char *str2, s21_size_t n);
char *s21_strncpy(char *destination, const char *source, s21_size_t n);
char *s21_strpbrk(const char *str, const char *keys);
char *s21_strrchr(const char *str, int symbol);
char *s21_strstr(const char *destptr, const char *srcptr);
char *s21_strtok(char *str, const char *delim);
char *s21_strncat(char *result, const char *str, s21_size_t size);
void *s21_to_upper(const char *str);
void *s21_to_lower(const char *str);
void *s21_insert(const char *src, const char *str, s21_size_t start_index);
void *s21_trim(const char *src, const char *trim_chars);
int s21_sprintf(char *str, const char *format, ...);
#endif