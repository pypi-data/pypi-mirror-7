
#ifndef _COMMON_H__
#define _COMMON_H__

#include <vector>

const char* format(const char*, ...);

namespace mget {
typedef std::map<std::string, std::string> dict;
typedef std::vector<std::string> list;

template<class> class m_string;
template<> class m_string<char*> {
public:
	m_string (const char* );
	list split(char );
	std::string join(mget::list, std::string);
private:
	std::string tmp_string;
	list tmp_list;
};

class Common {
public:
	Common();
	int get_term_width (void);
	const char* get_time(void );
	void write_string(const char* );
};

typedef m_string<char*> m_str;

}

#endif /* _COMMON_H__ */
