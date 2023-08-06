
from libcpp.string cimport string
from libcpp.map cimport map

cdef extern from "main.h":
	struct dtype:
		int m_int
		short m_bool
		float m_float
		string m_str

	ctypedef map[string, dtype] m_dict

cdef extern from "main.h" namespace "mget":

	cppclass MGet:
		MGet()
		void print_trying (int, int, int)
		void print_error (const char*, short)
		void quitting (const char*, float, float)
		void done_dl (const char*, const char*, int, int)

		int best_block_size (float, float)

		short print_info (m_dict&)

		float progress (float, float)
		float get_progress (float, float)
		float get_expected (float, float)

		string get_remaining (float, float)
		string format_bytes (float )
		string format_duration (int )
		string calc_speed (float, float)
		string calc_eta (float, float, float, float)

cdef extern from "common.h" namespace "mget":

	cppclass Common:
		Common()
		int get_term_width ()
		const char* get_time()
		void write_string(const char* )

