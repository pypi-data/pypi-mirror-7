// MGet main cpp
#include "mget.hpp"
#include "common.hpp"

#include <ctime>
#include <chrono>

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

// Namespace: mget

std::string mget::_time() {
using namespace std;

time_t result = time(NULL);
string time = asctime(localtime(&result));

return time.substr(0, time.size() - 1) + " IST";
}

void mget::print_string(char* str) { std::cout << str << std::endl; }

// Namespace: mget, Class: MGet

mget::MGet::MGet (void) { }

int mget::MGet::best_block_size(float est_time, float bytes) {
	float new_min = std::max(bytes / 2.0, 1.0);
	float new_max = std::min(std::max(bytes * 2.0, 1.0), 4194304.0);

	if (est_time < 0.001) return int(new_max);

	float rate = bytes / est_time;

	if (rate > new_max) return int(new_max);
	if (rate < new_min) return int(new_min);

return int(rate);
}

float mget::MGet::get_progress(float cursize, float total) { return (cursize / total * 100.0); }
float mget::MGet::get_expected(float total, float percent) { return (total * percent / 100.0); }

void mget::MGet::print_trying(std::string time, int trying, int cursize, int filesize) {
	std::cout << 
	time << " Read error at byte [" << cursize << "/" << filesize << "] - (try:" << trying << ")" 
	<< std::endl;
}

std::string mget::MGet::get_remaining(float current, float total) {
	int B_size = total - current;
	std::string F_size = mget::MGet::format_bytes(B_size);

return format("%d [%s]", B_size,F_size.c_str());
}

std::string mget::MGet::format_bytes(float bytes){
	using namespace std;
	char f_size [10];
	char UNITS[] = {'B', 'K', 'M', 'G'};

	if ( bytes > 1 ) {
	int exponent = log(bytes) / log(1024.0);
	float quotient = bytes / pow(1024, exponent);
	char unit =  UNITS[exponent];

	sprintf(f_size, (unit == 'B') ? "%.f%c" : "%.2f%c", quotient, unit);
	}
	else { return "Unknown"; }

return f_size;
}

std::string mget::MGet::format_duration(int duration) {
	using namespace std;
	char f_time [10]; 

	int mins = (duration / 60);
	int secs = (duration % 60);
	int hours = (mins / 60);
	mins = (mins % 60);

	if ( hours > 99 ) { return "--:--"; }
	else if ( hours == 0 && mins == 0 ) { snprintf(f_time, sizeof(&f_time), "    %02ds", secs); }
	else if ( hours == 0) { snprintf(f_time, sizeof(&f_time), "%02dm %02ds", mins, secs); }
	else { snprintf(f_time, sizeof(&f_time), "%02dh %02dm", hours, mins); }

return f_time;
}

int mget::MGet::print_info(mget::dict &info) {
	std::string resume = "";
	mget::list tmp, result;
	mget::m_str str = "\n";

	if (std::stoi(info["quiet_mode"].c_str()) == true) {
		result.push_back(format("Filesize: [%s] -> %s", info["filesize"].c_str(),info["filename"].c_str()));
		for (unsigned int i = 0; i < result.size(); i++) {
		tmp.push_back(format("[MGet Info] %s", result[i].c_str()));
		}
		std::cout << str.join(tmp) << std::endl;
		return true;
	}
	if (info["proxy"].c_str()) result.push_back(format("Proxy: %s", info["proxy"].c_str()));

	const char* status = info["status"].c_str();
	int b_size = std::stoi(info["filesize"].c_str());
	std::string f_size = mget::MGet::format_bytes(b_size);

	result.push_back(format("Status code: %s %s", status, responses[std::stoi(status)].c_str()));

	if (info["resuming"] == "1" && info["quit_size"] == "100")
	resume = mget::MGet::get_remaining(std::stoi(info["cursize"].c_str()), b_size);

	result.push_back(format("Filesize: %d [%s], %s [%s]", b_size,f_size.c_str(),resume.c_str(),info["type"].c_str()));
	if (std::stof(info["quit_size"]) != 100.0) {
		int e_size = std::stoi(info["expected"].c_str());
		std::string e_f_size = mget::MGet::format_bytes(e_size).c_str();
		std::string resume = (info["resuming"] == "1") ? get_remaining(std::stoi(info["cursize"].c_str()), e_size) : "";
		result.push_back(format("Expecting to download: %d [%s], %s remaining", e_size, e_f_size.c_str(), resume.c_str()));
	}

	if (info["dump_info"].c_str()) {
	result.push_back(format("Filename: %s", info["filename"].c_str()));
	}
	else result.push_back(format("Saving to: %s", info["filename"].c_str()));

	for (unsigned int i = 0; i < result.size(); i++) {
	tmp.push_back(format("[MGet Info] %s", result[i].c_str()));
	}
	std::cout << str.join(tmp) << std::endl;
return true;
}

/*
def unescapeHTML(s):
    if s is None:
        return None
    assert type(s) == compat_str

    result = re.sub(r'(?u)&(.+?);', htmlentity_transform, s)
    return result

def clean_html(html):
    """Clean an HTML snippet into a readable string"""
    # Newline vs <br />
    html = html.replace('\n', ' ')
    html = re.sub(r'\s*<\s*\/br\s/?\s*>\s*', '\n', html)
    html = re.sub(r'<\s/\s\*\/p\s*>\s*<\s*p[^>]*>', '\n', html)
    # Strip html tags
    html = re.sub('<.*?>', '', html)
    # Replace html entities
    html = unescapeHTML(html)
    return html.strip()
*/
std::string clean_html(std::string html) {
return "html";
}
