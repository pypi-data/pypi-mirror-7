
// MGet main class file..

#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <map>

#include <cstring>
#include <cmath>

#include "main.h"

const char* FILE_EXIST = "\nThe file is already fully retrieved; nothing to do.\n";

std::map<int, const char*> responses { {400, "Bad Request"}, {401, "Unauthorized"},
{403, "Forbidden"}, {404, "Not Found"}, {300, "Multiple Choices"}, {301, "Moved Permanently"},
{302, "Found"}, {304, "Not Modified"}, {200, "OK"}, {201, "Created"}, {202, "Accepted"},
{204, "No Content"}, {206, "Partial Content"}, {500, "Internal Server Error"},
{501, "Not Implemented"}, {502, "Bad Gateway"}, {503, "Service Unavailable"} };

mget::MGet::MGet () { common = new Common(); }
mget::MGet::~MGet () { delete common; }

void mget::MGet::print_trying (short trying, int cursize, int filesize) {
	const char* time = common->get_time();

	std::cout << 
	format("%s Read error at byte [%d/%d] - (try: %d)", time, cursize, filesize, trying)
	<< std::endl;
}

void mget::MGet::print_error(const char* msg = NULL, short status = 0) {
	std::string err = "";
	const char* result;

	if (status != 0) { err = format("%d %s", status, responses[status]); }
	if (msg != NULL) { err = msg; }

	result = (status == 416) ? FILE_EXIST : format("\nERROR: %s", err.c_str());

common->write_string(result);
}

void mget::MGet::quitting(const char* filename, float cursize, float filesize) {
	if (cursize > filesize) { filesize = cursize; }
	const char* percent = format("%.1f%%", get_progress(cursize, filesize));
common->write_string(format("\n\nQuitting: ‘%s’ at (%s) - [%d/%d]\n",
		filename, percent, int(cursize), int(filesize)));
}

void mget::MGet::done_dl(const char* speed, const char* filename, int cursize, int filesize) {
	if (cursize > filesize) { filesize = cursize; }
	const char* percent = format("%.1f%%", get_progress(cursize, filesize));
	const char* string = format("\n\n[%s] %s at (%s) - ‘%s’ -> [%d/%d]\n",
		common->get_time(),percent,speed,filename,cursize,filesize);

common->write_string(string);
}

int mget::MGet::best_block_size (float est_time, float bytes) {
	float new_min = std::max(bytes / 2.0, 1.0);
	float new_max = std::min(std::max(bytes * 2.0, 1.0), 4194304.0);

	if (est_time < 0.001) { return int(new_max); }

	float rate = bytes / est_time;

	if (rate > new_max) { return int(new_max); }
	if (rate < new_min) { return int(new_min); }

return int(rate);
}

float mget::MGet::get_progress (float cursize, float total) { return (cursize / total * 100.0); }
float mget::MGet::get_expected (float total, float percent) { return (total * percent / 100.0); }
float mget::MGet::progress (float cursize, float total) {
	float progress = cursize / total;
	if (progress < 0) { progress = 0; }
	if (progress > 1) { progress = 1; }

return progress;
}

bool mget::MGet::print_info(m_dict &info) {
	std::string resume = "";
	mget::list result;
	mget::m_str * str = new m_str("\n");
	const char* filename = info["filename"].m_str.c_str();
	const char* proxy = info["proxy"].m_str.c_str();

	if (info["quiet_mode"].m_bool == true) {
		result.push_back(format("Filesize: [%s] -> %s", info["filesize"].m_int,filename));
		std::cout << str->join(result, "[MGet Info] ") << std::endl;
		return true;
	}
	if (strlen(proxy) > 1) result.push_back(format("Proxy: %s", proxy));

	short status = info["status"].m_int;
	int b_size = info["filesize"].m_int;
	std::string f_size = format_bytes(b_size);

	result.push_back(format("Status code: %d %s", status, responses[status]));

	if (info["resuming"].m_bool == true && info["quit_size"].m_int == 100)
	resume = get_remaining(info["cursize"].m_int, b_size);

	result.push_back(format("Filesize: %d [%s], %s [%s]", b_size,f_size.c_str(),resume.c_str(),info["type"].m_str.c_str()));
	if (info["quit_size"].m_float != 100.0) {
		int e_size = info["expected"].m_int;
		resume = (info["resuming"].m_bool) ? get_remaining(info["cursize"].m_int, e_size) : "";
		const char* e_f_size = format_bytes(e_size).c_str();
		result.push_back(format("Expecting to download: %d [%s], %s", e_size, e_f_size, resume.c_str()));
	}

	if (info["dump_info"].m_bool) { result.push_back(format("Filename: %s", filename)); }
	else result.push_back(format("Saving to: %s", filename));

	std::cout << str->join(result, "[MGet Info] ") << std::endl;

return true;
}

std::string mget::MGet::get_remaining(float current, float total) {
	int B_size = total - current;
	std::string F_size = format_bytes(B_size);
return format("%d [%s] remaining", B_size,F_size.c_str());
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

std::string mget::MGet::format_duration(int duration = 0) {
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

std::string mget::MGet::calc_speed (float dif, float bytes) {
	if (bytes == 0 or dif < 0.001) return format("%9s", "--.-K/s");

return format("%s/s", format_bytes(bytes / dif).c_str());
}

std::string mget::MGet::calc_eta(float dif, float bytes, float current, float total) {
	if (current == 0 or dif < 0.001) return "--:--";
	float rate = current / dif;
	int eta = int((total - current) / rate);
return format_duration(eta);
}

