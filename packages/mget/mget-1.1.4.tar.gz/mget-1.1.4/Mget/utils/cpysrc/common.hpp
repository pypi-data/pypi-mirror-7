// MGet common..!

#include <sstream>
#include <vector>
#include <map>

std::map<int, std::string> responses { {400, "Bad Request"}, {401, "Unauthorized"},
{403, "Forbidden"}, {404, "Not Found"}, {300, "Multiple Choices"}, {301, "Moved Permanently"},
{302, "Found"}, {304, "Not Modified"}, {200, "OK"}, {201, "Created"}, {202, "Accepted"},
{204, "No Content"}, {206, "Partial Content"}, {500, "Internal Server Error"},
{501, "Not Implemented"}, {502, "Bad Gateway"}, {503, "Service Unavailable"} };

namespace mget {

template<class> class m_string;
template<> class m_string<char*> {
	std::string tmp_string;
	std::vector<std::string> tmp_list;
public:
	m_string (const char* s) { tmp_string = std::string(s); }

	std::vector<std::string> split(char delim) {
	std::string buf = "";
	for (unsigned int i = 0; i < tmp_string.length(); i++) {
		if (tmp_string[i] != delim) buf += tmp_string[i];
		else if (buf.length() > 0) {
		tmp_list.push_back(buf);
		buf = "";
		}
	}
	tmp_list.push_back(buf);
	buf = "";

	return tmp_list;
	}

	std::string join(list array) {
	std::ostringstream oss;
	for (unsigned int i = 0; i < array.size(); i++ ) { oss << array[i] << tmp_string; }
	return oss.str();
	}
};

typedef m_string<char*> m_str;

}
