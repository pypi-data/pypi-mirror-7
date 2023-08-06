from libcpp.string cimport string
#from libcpp.bool cimport bool
from libcpp.map cimport map

cdef extern from "mget.hpp":
	struct dtypes:
		int m_int
		int m_bool
		float m_float
		string m_str

	ctypedef map[string, dtypes] m_dict

cdef extern from "mget.hpp" namespace "mget":
	string _time ()
	void print_string (char*)

	cppclass MGet:
		MGet()
		void print_trying(string, int, int, int)
		void _error(const char*, short)
		void done_dl(const char*, const char*, int, int)
		int print_info(m_dict&)
		int best_block_size(float, float)
		float _progress(float, float)
		float get_progress(float, float)
		float get_expected(float, float)
		string format_bytes(float)
		string format_duration(int)
		string get_remaining (float, float)
		string calc_speed (float, float)
		string calc_eta(float, float, float, float)

