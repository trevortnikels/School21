#include "s21_additional_func.h"

#define S21_MAX_UINT 4294967295

s21_decimal* s21_setBit(s21_decimal* value, int pos, int bit) {
  if (pos / 32 < 4 && bit)
    value->bits[pos / 32] |= (1u << (pos % 32));
  else if (pos / 32 < 4 && !bit)
    value->bits[pos / 32] &= ~(1u << (pos % 32));
  return value;
}

int s21_addBit(s21_decimal value_1, s21_decimal value_2, s21_decimal* result) {
  int fres = 0, exp = 0;
  for (int bit = 0; bit < 96; bit += 1) {
    int bitValue_1 = !!(value_1.bits[bit / 32] & (1u << (bit % 32)));
    int bitValue_2 = !!(value_2.bits[bit / 32] & (1u << (bit % 32)));
    if (!bitValue_1 && !bitValue_2)
      exp ? s21_setBit(result, bit, (exp = 0) + 1) : s21_setBit(result, bit, 0);
    else if (bitValue_1 != bitValue_2)
      exp ? s21_setBit(result, bit, (exp = 1) - 1) : s21_setBit(result, bit, 1);
    else
      exp ? s21_setBit(result, bit, (exp = 1))
          : s21_setBit(result, bit, (exp = 1) - 1);
    int bitValue1 = !!(value_1.bits[97 / 32] & (1u << (97 % 32)));
    int bitValue2 = !!(value_2.bits[97 / 32] & (1u << (97 % 32)));
    if (bit == 95 && exp == 1 && !bitValue1 && !bitValue2) fres = 1;
  }
  return fres;
}

int s21_getBitLast(s21_decimal value) {
  int bitLast = 95;
  for (; (bitLast >= 0) &&
         (!!!(value.bits[bitLast / 32] & (1u << (bitLast % 32))));)
    bitLast -= 1;
  return bitLast;
}

s21_decimal* s21_leftShift(s21_decimal* value, int shift) {
  if (!(s21_getBitLast(*value) + shift > 95)) {
    for (int y = 0; y < shift; y += 1) {
      int bitTransfer_1 = !!(value->bits[31 / 32] & (1u << (31 % 32)));
      int bitTransfer_2 = !!(value->bits[63 / 32] & (1u << (63 % 32)));
      for (int x = 0; x < 3; x += 1) value->bits[x] <<= 1;
      if (bitTransfer_1) s21_setBit(value, 32, 1);
      if (bitTransfer_2) s21_setBit(value, 64, 1);
    }
  }
  return value;
}

s21_decimal* s21_increaseScale(s21_decimal* value, int shift) {
  int scale = (char)(value->bits[3] >> 16);
  if (scale + shift < 29) {
    scale = scale + shift;
    if (scale >= 0 && scale <= 28) {
      int sign = !!(value->bits[3] & (1u << 31));
      value->bits[3] &= ~(0xFF << 16);
      value->bits[3] |= scale << 16;
      if (sign) {
        value->bits[3] = (value->bits[3] | (1u << 31));
      }
    }
    s21_decimal auxValue_1 = *value;
    s21_decimal auxValue_2 = *value;
    if (s21_addBit(*s21_leftShift(&auxValue_1, 1),
                   *s21_leftShift(&auxValue_2, 3), value))
      s21_setBit(value, 96, 1);
  }
  return value;
}

s21_decimal* s21_decreaseScale(s21_decimal* value, int shift) {
  for (int y = 0; y < shift; y += 1) {
    unsigned long long overflow = value->bits[2];
    for (int x = 2; x >= 0; x -= 1) {
      value->bits[x] = overflow / 10;
      overflow =
          (overflow % 10) * (S21_MAX_UINT + 1) + value->bits[x ? x - 1 : x];
    }
  }
  int scale = (char)(value->bits[3] >> 16) - shift;
  if (scale >= 0 && scale <= 28) {
    int sign = !!(value->bits[3] & (1u << 31));
    value->bits[3] &= ~(0xFF << 16);
    value->bits[3] |= scale << 16;
    if (sign) {
      value->bits[3] = (value->bits[3] | (1u << 31));
    }
  }
  return value;
}

void s21_alignment_Scale(s21_decimal* value_1, s21_decimal* value_2) {
  int scale1 = (char)(value_1->bits[3] >> 16);
  int scale2 = (char)(value_2->bits[3] >> 16);
  if (scale1 != scale2) {
    if (scale1 < scale2) {
      s21_alignment_Scale(value_2, value_1);
    } else {
      int scaleLow = scale2, scaleHigh = scale1;
      int bit_2 = !!(value_2->bits[96 / 32] & (1u << (96 % 32)));
      for (; (scaleHigh - scaleLow) && !bit_2; scaleLow += 1)
        s21_increaseScale(value_2, 1);
      for (; scaleHigh - scaleLow; scaleHigh -= 1) {
        s21_decreaseScale(value_1, scaleHigh - scaleLow);
        int scale = scaleLow;
        if (scale >= 0 && scale <= 28) {
          int sign = !!(value_1->bits[3] & (1u << 31));
          value_1->bits[3] &= ~(0xFF << 16);
          value_1->bits[3] |= scale << 16;
          if (sign) {
            value_1->bits[3] = (value_1->bits[3] | (1u << 31));
          }
        }
      }
    }
  }
}
