// MGet Common..!
#include <iostream>
#include <cstdio>
#include <cstdarg>

std::string format(const char* fmt, ...) {
va_list args;
int size = 100;
char* buffer = 0;
buffer = new char[size];

va_start(args, fmt);
vsnprintf(buffer, size, fmt, args);
va_end(args);

return buffer;
}

