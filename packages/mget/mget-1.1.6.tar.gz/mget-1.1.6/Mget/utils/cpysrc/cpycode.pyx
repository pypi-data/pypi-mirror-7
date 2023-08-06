
cimport cpycode
import time

cdef cpycode.MGet * mget = new cpycode.MGet()

cdef class MGet:
	@staticmethod
	def _time(): return cpycode._time()

	@staticmethod
	def get_time(): return MGet._time().decode()

	@staticmethod
	def write_string(char* msg): cpycode.print_string(msg)

	@staticmethod
	def progress(float cursize, float total): return mget.get_progress(cursize, total)

	@staticmethod
	def get_progress(float cursize, float total): return mget._progress(cursize, total)

	@staticmethod
	def expected(float total, float percent): return mget.get_expected(total, percent)

	@staticmethod
	def _trying(int trying, int cursize, int filesize):
		mget.print_trying(MGet._time(), trying, cursize, filesize)

	@staticmethod
	def init_(url = None, **kwargs):
		site = kwargs.pop('site', None)
		cur_dl = kwargs.pop('cdl', None)
		wpage = kwargs.pop('wpage', False)
		epage = kwargs.pop('epage', False)

		if wpage or epage: string = "[%s] [%s] (Downloading webpage: %s)" % (MGet.get_time(), site, cur_dl)
		elif url: string = "[Mget Info] Location: %s" % (url)
		else: string = "[%s] [%s] (Download: %s)" % (MGet.get_time(), site, cur_dl)

		MGet.write_string(string.encode())

	@staticmethod
	def get_remaining(float current, float total): return mget.get_remaining(current, total)

	@staticmethod
	def format_size(float byte): return mget.format_bytes(byte).decode()

	@staticmethod
	def format_time(int duration): return mget.format_duration(duration).decode()

	@staticmethod
	def calc_speed (float dif, float bytes): return mget.calc_speed(dif, bytes)

	@staticmethod
	def calc_eta(float dif, float bytes, float current, float total): 
		return mget.calc_eta(dif, bytes, current, total)

	@staticmethod
	def best_block_size(float est_time, float bytes):
		return mget.best_block_size(est_time, bytes)

	@staticmethod
	def _error(char* msg = "", short status = 0): mget._error(msg, status)

	@staticmethod
	def done_dl(char* speed, char* filename, int cursize, int filesize):
		mget.done_dl(speed, filename, cursize, filesize)

	@staticmethod
	def print_info(info = {}):
		cdef cpycode.m_dict dic

		dic["filesize"].m_int	 = info["filesize"]
		dic["cursize"].m_int 	 = info["cursize"]
		dic["expected"].m_int 	 = info["expected"]
		dic["status"].m_int 	 = info["status"]
		dic["quit_size"].m_float = info["quit_size"]
		dic["resuming"].m_bool 	 = info["resuming"]
		dic["quiet_mode"].m_bool = info["quiet_mode"]
		dic["dump_info"].m_bool  = info["dump_info"]
		dic["filename"].m_str 	 = info["filename"].encode()
		dic["type"].m_str 	 = info["type"].encode()
		dic["proxy"].m_str 	 = info["proxy"].encode()

		mget.print_info(dic)
del mget
