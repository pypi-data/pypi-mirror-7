// MGet main cpp
#include "common.hpp"

// Namespace: mget

std::string mget::_time() {
using namespace std;

time_t result = time(NULL);
string time = asctime(localtime(&result));

return time.substr(0, time.size() - 1) + " IST";
}

void mget::print_string(const char* str) { std::cout << str << std::endl; }

// Namespace: mget, Class: MGet

mget::MGet::MGet () { }

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
float mget::MGet::_progress(float cursize, float filesize) {
	float progress = cursize / filesize;
	if (progress < 0) progress = 0;
	if (progress > 1) progress = 1;

return progress;
}

void mget::MGet::print_trying(std::string time, int trying, int cursize, int filesize) {
	std::cout << 
	time << " Read error at byte [" << cursize << "/" << filesize << "] - (try:" << trying << ")" 
	<< std::endl;
}

void mget::MGet::_error(const char* msg = NULL, short status = 0) {
	std::string res = "";

	if (status == 416) { res = FILE_EXIST; }
	else if (status != 0) { res = format("%d, %s", status, responses[status].c_str()); }
	else { res = (msg != NULL) ? msg : "MGet System Error...!"; }

	mget::print_string(format("\nERROR: %s", res.c_str()).c_str());
}

void mget::MGet::done_dl(const char* speed,const char* filename,int cursize,int filesize) {
	if (cursize > filesize) { filesize = cursize; }
	const char* percent = format("%.1f%%", get_progress(cursize ,filesize)).c_str();
	std::string string = format("\n\n[%s] %s at (%s) - ‘%s’ -> [%d/%d]\n",
		mget::_time().c_str(),percent,speed,filename,cursize,filesize);
	mget::print_string(string.c_str());
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

/*
bool mget::MGet::write_info(mget::dict info, mget::list report) {
	mget::list tmp, result;
	mget::m_str str = "\n";
	for (const auto p : report){ tmp.push_back(p); }
	std::string report = str.join(tmp);

	result.append(str.join("%s" % x for x in info.get('report')))
	result.append("Python Version %s %s\n" % (platform.python_version(),platform_name()))
	result.append("Default Url\t: %s" % info.get('defurl'))
	result.append("Url\t\t: %s" % info.get('url'))
	result.append("Proxy\t\t: %s" % ({} if info.get('proxy') == None else info.get('proxy')))
	result.append("Status\t\t: %s" % info.get('status'))
	result.append("Type\t\t: %s" % info.get('type'))
	result.append("Filename\t: %s" % info.get('filename'))
	result.append("Filesize\t: %s" % info.get('filesize'))
	result.append("Headers\t\t: %s" % (dict(info.get('headers'))))

	data = "\n".join("%s" % x for x in result)

	log_filename = info.get('log_file')
	if os.path.exists(log_filename): log_filename = EXFilename(log_filename)

	f = open(log_filename, 'w');
	f.write(data);

		mget::MGet::write_string('Done Writting information to %s\n' % info.get('log_file'))
return true;
}
*/

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

	result.push_back(format("Status code: %d %s", status, responses[status].c_str()));

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

/*
bool _progress_bar(s_dif, cursize, filesize, remaining, bytes, dif, width) {
	int data_len = (cursize - resume_len)

	std::string res = format("%.1f%%", get_progress(cursize ,filesize)).c_str();
	res += "[" + "=" *int(progress * width)+ ">" + " " *(width-int(progress * width)) + "] ";
	res += "%-12s " % ("{:02,}".format(cursize, filesize));
	res += "%9s " % calc_speed(dif, bytes);
	res += "eta " + calc_eta(s_dif, bytes, data_len, remaining);

	const char* line = res.c_str();

	if (newline) { print_string('\n'); }
	else { print_string('\r'); }

	if (last_len > 0) { print_string('\b' * last_len); }

	print_string("\r" + line);
	last_len = strlen(line);
}
*/

