#include <stddef.h>

#include "../s21_string.h"

#define BUFFER_SIZE 1024

typedef struct {
  int left_justify;
  int force_sign;
  int space;
  int width;
  int precision;
  int length_l;
  int length_h;
} format_specifier_t;

void parse_format(const char **format, format_specifier_t *fs);
void *s21_memmove(void *dest, const void *src, s21_size_t n);
void handle_padding(char *buffer, format_specifier_t *fs, int content_length,
                    char pad_char);

void parse_format(const char **format, format_specifier_t *fs) {
  const char *ptr = *format;

  s21_memset(fs, 0, sizeof(format_specifier_t));
  fs->precision = -1;

  while (*ptr == '-' || *ptr == '+' || *ptr == ' ') {
    if (*ptr == '-') fs->left_justify = 1;
    if (*ptr == '+') fs->force_sign = 1;
    if (*ptr == ' ') fs->space = 1;
    ptr++;
  }

  if (isdigit(*ptr)) {
    fs->width = atoi(ptr);
    while (isdigit(*ptr)) ptr++;
  }

  if (*ptr == '.') {
    ptr++;
    fs->precision = atoi(ptr);
    while (isdigit(*ptr)) ptr++;
  }

  if (*ptr == 'l') {
    fs->length_l = 1;
    ptr++;
  } else if (*ptr == 'h') {
    fs->length_h = 1;
    ptr++;
  }

  *format = ptr;
}

void *s21_memmove(void *dest, const void *src, s21_size_t n) {
  unsigned char *d = (unsigned char *)dest;
  const unsigned char *s = (const unsigned char *)src;

  if (d == s) {
    return dest;
  }

  if (d < s) {
    while (n--) {
      *d++ = *s++;
    }
  } else {
    d += n;
    s += n;
    while (n--) {
      *--d = *--s;
    }
  }

  return dest;
}

void handle_padding(char *buffer, format_specifier_t *fs, int content_length,
                    char pad_char) {
  int padding = fs->width - content_length;
  if (padding > 0) {
    if (fs->left_justify) {
      s21_memset(buffer + content_length, pad_char, padding);
    } else {
      s21_memmove(buffer + padding, buffer, content_length);
      s21_memset(buffer, pad_char, padding);
    }
  }
}

int s21_sprintf(char *str, const char *format, ...) {
  va_list args;
  va_start(args, format);
  char *buf_ptr = str;

  while (*format) {
    if (*format == '%') {
      format++;
      format_specifier_t fs;
      parse_format(&format, &fs);

      char temp[BUFFER_SIZE];
      s21_memset(temp, 0, BUFFER_SIZE);
      char *temp_ptr = temp;

      switch (*format) {
        case 'c': {
          char c = (char)va_arg(args, int);
          *temp_ptr++ = c;
          *temp_ptr = '\0';
          handle_padding(temp, &fs, 1, ' ');
          break;
        }
        case 'd': {
          int len;
          if (fs.length_l) {
            long val = va_arg(args, long);
            len = sprintf(temp, "%ld", val);
          } else if (fs.length_h) {
            short val = (short)va_arg(args, int);
            len = sprintf(temp, "%hd", val);
          } else {
            int val = va_arg(args, int);
            len = sprintf(temp, "%d", val);
          }
          if (fs.force_sign && temp[0] != '-') {
            s21_memmove(temp + 1, temp, len + 1);
            temp[0] = '+';
          } else if (fs.space && temp[0] != '-') {
            s21_memmove(temp + 1, temp, len + 1);
            temp[0] = ' ';
          }
          handle_padding(temp, &fs, s21_strlen(temp), ' ');
          break;
        }
        case 'u': {
          if (fs.length_l) {
            unsigned long val = va_arg(args, unsigned long);
            sprintf(temp, "%lu", val);
          } else if (fs.length_h) {
            unsigned short val = (unsigned short)va_arg(args, unsigned int);
            sprintf(temp, "%hu", val);
          } else {
            unsigned int val = va_arg(args, unsigned int);
            sprintf(temp, "%u", val);
          }
          handle_padding(temp, &fs, s21_strlen(temp), ' ');
          break;
        }
        case 'f': {
          double val = va_arg(args, double);
          if (fs.precision == -1) {
            fs.precision = 6;
          }
          sprintf(temp, "%.*f", fs.precision, val);
          handle_padding(temp, &fs, s21_strlen(temp), ' ');
          break;
        }
        case 's': {
          const char *val = va_arg(args, const char *);
          int pres = fs.precision;
          s21_strncpy(temp, val,
                      fs.precision > 0 ? (s21_size_t)pres : s21_strlen(val));
          temp[fs.precision > 0 ? (s21_size_t)pres : s21_strlen(val)] = '\0';
          s21_strncpy(temp, val,
                      fs.precision > 0 ? (s21_size_t)pres : s21_strlen(val));
          temp[fs.precision > 0 ? (s21_size_t)pres : s21_strlen(val)] = '\0';
          handle_padding(temp, &fs, s21_strlen(temp), ' ');
          break;
        }
        default:
          *temp_ptr++ = '%';
          *temp_ptr++ = *format;
          *temp_ptr = '\0';
          break;
      }

      s21_strncpy(buf_ptr, temp, BUFFER_SIZE);
      buf_ptr += s21_strlen(temp);
    } else {
      *buf_ptr++ = *format;
    }
    format++;
  }

  *buf_ptr = '\0';
  va_end(args);
  return buf_ptr - str;
}