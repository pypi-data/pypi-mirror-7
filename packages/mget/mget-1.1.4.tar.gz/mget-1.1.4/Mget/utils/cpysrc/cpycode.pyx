cimport cpycode
import time

cdef cpycode.MGet * mget = new cpycode.MGet()

cdef class MGet:
	@staticmethod
	def _time(): return cpycode._time()

	@staticmethod
	def get_time(): return MGet._time().decode('utf-8')

	@staticmethod
	def write_string(char* msg): cpycode.print_string(msg)

	@staticmethod
	def progress(float cursize, float total): return mget.get_progress(cursize, total)

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

		if wpage or epage: string = "[%s] [%s] (Download: %s) Downloading webpage" % (MGet.get_time(), site, cur_dl)
		elif url: string = "[Mget Info] Location: %s" % (url)
		else: string = "[%s] [%s] (Downloading webpage: %s)" % (MGet.get_time(), site, cur_dl)

		MGet.write_string(string.encode('utf-8'))

	@staticmethod
	def get_remaining(float current, float total):
		B_size = total - current
		F_size = mget.format_bytes(B_size).decode('utf-8')
		return "%.f [%s]" % (B_size,F_size)

	@staticmethod
	def format_size(float byte): return mget.format_bytes(byte).decode('utf-8')

	@staticmethod
	def format_time(int duration): return mget.format_duration(duration).decode('utf-8')

	@staticmethod
	def best_block_size(float est_time, float bytes):
		return mget.best_block_size(est_time, bytes)

	@staticmethod
	def print_info(info = {}):
		t1 = time.time()
		mget.print_info({k.encode('utf-8'):v.encode('utf-8') for k, v in info.items()})
		t2 = time.time()
		print(t2 - t1)

del mget
