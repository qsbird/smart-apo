#ifndef SMART_APO_FREESTANDING_STRING_H
#define SMART_APO_FREESTANDING_STRING_H
/* The subset actually implemented in runtime/string.c. No hosted libc needed. */
#include <stddef.h>
void *memcpy(void *restrict dst, const void *restrict src, size_t n);
void *memset(void *dst, int value, size_t n);
int memcmp(const void *a, const void *b, size_t n);
#endif
