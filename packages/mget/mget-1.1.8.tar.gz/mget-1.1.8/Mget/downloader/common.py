#!/usr/bin/env python3

import os, sys
import time
from ..utils import MGet, common, urlparse

class FileDownloader(object):
	def __init__(self, info = {}):
		self.params = info
		self.last_len = 0

	@staticmethod
	def getLocalFilesize(filename):
		if not os.path.exists(filename): return None
		return os.path.getsize(os.path.join('.', filename))

	def _progress_bar(self, s_dif = None, progress = None, bytes = None, dif = None, width = 46):
		term_width = common.get_term_width()
		width = term_width - width

		data_len = (self.cursize - self.resume_len)

		_res = ["%-6s" % ("{0:.1f}%".format(float(progress) * 100.0)),
			"[" + "="*int(progress*width)+">" + " "*(width-int(progress*width)) + "] ",
			"%-12s " % ("{:02,}".format(self.cursize,self.filesize)),
			"%9s " % (MGet.calc_speed(dif,bytes).decode()),
			"eta "+ MGet.calc_eta(s_dif,bytes,data_len,self.remaining).decode()]

		line = "".join(["%s" % x for x in _res])
		if self.params.get('newline'): sys.stdout.write('\n')
		else:sys.stdout.write('\r')
		if self.last_len: sys.stdout.write('\b' * self.last_len)

		sys.stderr.write("\r")
		sys.stdout.write(line)
		sys.stdout.flush()
		self.last_len = len(line)

	def get_progress(self): return MGet.get_progress(self.cursize, self.filesize)
