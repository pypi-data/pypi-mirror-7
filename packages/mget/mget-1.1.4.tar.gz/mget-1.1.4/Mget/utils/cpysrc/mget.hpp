// MGet namespace and class

#ifndef MGET_H__
#define MGET_H__

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>

#include <cstdio>
#include <cstdarg>
#include <cmath>

namespace mget {
typedef std::map<std::string, std::string> dict;
typedef std::vector<std::string> list;

std::string _time();
void print_string(char*);

class MGet {
public:
	MGet();
	int print_info(dict&);
	int best_block_size(float, float);
	float get_progress (float, float);
	float get_expected (float, float);
	void print_trying (std::string, int, int, int);
	std::string get_remaining (float, float);
	std::string format_bytes(float);
	std::string format_duration(int);
};

}

#endif
