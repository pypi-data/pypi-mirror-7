from libcpp.string cimport string
#from libcpp.bool cimport bool
from libcpp.map cimport map

ctypedef map[string, string] m_dict

cdef extern from "mget.hpp" namespace "mget":
	string _time ()
	void print_string (char*)

	cppclass MGet:
		MGet()
		void print_trying(string, int, int, int)
		int print_info(m_dict)
		int best_block_size(float, float)
		float get_progress(float, float)
		float get_expected(float, float)
		string format_bytes(float)
		string format_duration(int)

