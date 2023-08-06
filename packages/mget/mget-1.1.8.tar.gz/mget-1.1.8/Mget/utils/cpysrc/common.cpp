
// MGet Common file..

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <unistd.h>
#include <sys/ioctl.h>

#include <ctime>
#include <cstdarg>

#include "common.h"

const char* format (const char* fmt, ...) {
va_list args;
int size = 100;
char* buffer = 0;
buffer = new char[size];

va_start(args, fmt);
vsnprintf(buffer, size, fmt, args);
va_end(args);

return buffer;
}

int mget::Common::get_term_width (void) {
int cols = 80;
// lines = 24;

#ifdef TIOCGSIZE
	struct ttysize ts;
	ioctl(STDIN_FILENO, TIOCGSIZE, &ts);
	cols = ts.ts_cols;
	// lines = ts.ts_lines;

#elif defined(TIOCGWINSZ)
	struct winsize ts;
	ioctl(STDIN_FILENO, TIOCGWINSZ, &ts);
	cols = ts.ws_col;
	// lines = ts.ws_row;

#endif /* TIOCGSIZE */

return cols;
}

mget::Common::Common() { }

void mget::Common::write_string (const char* str) { std::cout << str << std::endl; }

const char* mget::Common::get_time (void ) {
std::time_t result = std::time(NULL);
std::string time = std::asctime(std::localtime(&result));

return (time.substr(0, time.size() - 1) + " IST").c_str();
}

mget::m_string<char*>::m_string (const char* s) { 
tmp_string = std::string(s);
}

mget::list mget::m_string<char*>::split(char delim = '\n') {
std::string buf = "";

for (unsigned int i = 0; i < tmp_string.length(); i++) {
	if (tmp_string[i] != delim) { buf += tmp_string[i]; }
	else if (buf.length() > 0) {
	tmp_list.push_back(buf);
	buf = "";
	}
}
tmp_list.push_back(buf);
buf = "";

return tmp_list;
}

std::string mget::m_string<char*>::join(mget::list array, std::string prefix = "") {
std::ostringstream oss;

for (unsigned int i = 0; i < array.size(); i++ ) { oss << prefix << array[i] << tmp_string; }

return oss.str();
}

