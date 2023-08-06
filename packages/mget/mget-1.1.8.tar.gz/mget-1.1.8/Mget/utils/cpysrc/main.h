
#ifndef _MGET_H__
#define _MGET_H__

#include "common.h"

struct dtypes {
	int m_int;
	float m_float;
	bool m_bool;
	std::string m_str;
};

typedef std::map<std::string, dtypes> m_dict;

namespace mget {

class MGet {
public:
	MGet();
	~MGet();
	void print_trying (short, int, int);
	void print_error(const char*, short);
	void quitting(const char*, float, float);
	void done_dl(const char*, const char*, int, int);

	int best_block_size(float, float);

	float progress(float, float);
	float get_progress (float, float);
	float get_expected (float, float);

	bool print_info(m_dict&);

	std::string get_remaining (float, float);
	std::string format_bytes(float );
	std::string format_duration(int );
	std::string calc_speed (float, float);
	std::string calc_eta(float, float, float, float);

private:
	struct class_options {
		int cursize;
		int filesize;
	};
	mget::Common * common;
};

}

#endif /* _MGET_H__ */ 
