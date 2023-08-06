// MGet namespace and class

#ifndef MGET_H__
#define MGET_H__

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>

#include <cstring>
#include <cmath>

struct dtypes {
int m_int;
float m_float;
bool m_bool;
std::string m_str;
};
typedef std::map<std::string, dtypes> m_dict;

namespace mget {

typedef std::map<std::string, std::string> dict;
typedef std::vector<std::string> list;

std::string _time();
void print_string(const char*);

class MGet {
struct self;
public:
	MGet();
	int best_block_size(float, float);
	float _progress(float, float);
	float get_progress (float, float);
	float get_expected (float, float);
	void print_trying (std::string, int, int, int);
	void _error(const char*, short);
	void done_dl(const char*, const char*, int, int);
	bool print_info(m_dict&);
	std::string get_remaining (float, float);
	std::string format_bytes(float);
	std::string format_duration(int);
	std::string calc_speed (float, float);
	std::string calc_eta(float, float, float, float);
};

}

#endif
