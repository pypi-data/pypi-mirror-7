#!/usr/bin/env python3

import os, sys
import time
import socket
from .utils import *
from .downloader import *
from . import extractor

class MGetDL(FileDownloader):
	def __init__(self, opts, info):
		super(MGetDL, self).__init__(self)

		if opts.verbose: common.debug_info(info)
		self.info = info
		self.params = opts
		self.defurl = info.get('defurl')
		self.client = client.Client(info=self.info)
		self.ie_result = self.get_ie_result(self.defurl)
		self.url = self.ie_result.get('url', self.defurl)
		self.filename = self.info['filename'] = self.params.filename or \
				self.ie_result.get('filename') or info.get('def_page')
		self.cursize = self.getLocalFilesize(self.filename) or 0
		self.quitsize = self.params.quitsize
		self.site = self.ie_result.get('site')
		self.hostname = self.ie_result.get('hostname')
		self.trying = 0

	def get_ie_result(self, url):
		try: return extractor.get_info(url, self.client, self.info)
		except ExtractorError as err:
			if self.info.get('debug_mget'): common.report_error(err._trace())
			else: common.report_error(str(err))
			exit(2)

	def __downloadFile__(self, urlObj):
		self.mode = 'wb' if self.cursize == 0 else 'ab'
		start = info['start_time'] = time.time()
		try:
			with open(self.filename, self.mode) as fileObj:
				dl = MGetDownloader(urlObj, fileObj, info)
				try: dl.start()
				except (socket.timeout, socket.error) as err:
					common._error(str(err) + "\n")
					return self.__retry__()
		except KeyboardInterrupt:
			self.cursize = self.getLocalFilesize(self.filename)
			common._quitting(self.filename,self.cursize,info.get('filesize'))
			exit(1)

		except (ContentTooShortError, DownloadError) as err:
			common.report_error(err)
			if info.get('retryerror', False): self.__retry__()
			else:
				self.cursize = self.getLocalFilesize(self.filename)
				common._quitting(self.filename,self.cursize,info.get('filesize'))
				if self.info.get('ignore'): return False
				else: exit(2)

		except (TypeError, ValueError, NameError) as err:
			self.cursize = self.getLocalFilesize(self.filename)
			common._quitting(self.filename,self.cursize,info.get('filesize'))
			if self.info.get('debug_mget'):
				common.write_string(common.FormatTrace(sys.exc_info()))
			else: common.report_error(str(err))
			if self.info.get('ignore'): return False
			else: exit(2)

		finally:
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			self.cursize = self.getLocalFilesize(self.filename)
			urlObj.close()

		_opts= {
		'speed': MGet.calc_speed(time.time()-start, self.cursize-info['cursize']).decode(),
		'filename': self.filename,
		'cursize': self.cursize,
		'filesize': info.get('filesize')}

		common.done_dl(**_opts)
		return True

	def __retry__(self):
		progress = MGet.progress(float(self.cursize),float(info.get('filesize', 0)))
		if progress >= self.params.quitsize:
			common.write_string(common.FILE_EXIST)

		self.trying += 1
		self.cursize = self.getLocalFilesize(self.filename)
		MGet._trying(self.trying,self.cursize,info.get('filesize'))
		time.sleep(int(info.get('waitretry', 1)))

		if self.cursize != info.get('filesize'):
			MGet.init_(url=self.url)
			common.report("Retrying download at: %s [%s]" % \
					(self.cursize,common.format_size(self.cursize)))
			self.resume(retrying=True)
		return True

	def resume(self, retrying = False):
		if retrying:
			common.report("Re-connecting to %s..." % self.hostname)
			_info = self.client.getInfos(self.url, self.cursize)
			if _info is None: return False

			info['cursize'] = self.cursize
			info['resuming'] = True if self.cursize != 0 else False
			info.update(_info)

			MGet.print_info(info)

		self.__downloadFile__(info.get('urllibObj'))

	def start(self):
		global info
		if self.info.get('restart'): self.cursize = 0; self.mode = 'wb'
		if self.params.geturl or self.params.embedurl: common.report(self.url); return True
		if os.path.exists(self.filename) and not self.info.get('continue'):
			self.filename = common.EXFilename(self.filename)
			self.cursize = self.getLocalFilesize(self.filename) or 0

		MGet.init_(url=self.url)
		common.report("Connecting to %s..." % self.hostname)
		info = self.client.getInfos(self.url, self.cursize)

		if info is None: return False

		info['cursize'] = self.cursize
		info['resuming'] = True if self.cursize != 0 else False
		info['expected'] = \
			int(MGet.expected(float(info.get('filesize')), float(self.params.quitsize)))
		info.update(self.info)
		self.cookiejar = info.get('cookiejar')

		if info.get('dump_head'):
			common._stderr(info.get('headers'));
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			return True

		if info.get('write_info'):
			common.write_info(info);
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			return True

		MGet.print_info(info)

		if info.get('dump_info'):
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			return True

		if self.cursize - 100 < info.get('filesize') < self.cursize + 100:
				common.write_string(common.FILE_EXIST, False); return True
		if info.get('quit_size') != 100.0:
			progress = MGet.progress(self.cursize,info.get('filesize', 0))
			if progress >= self.params.quitsize:
				common.write_string(common.FILE_EXIST, False); return True

		if os.path.exists(self.filename) and info.get('continue'): self.resume()
		else: self.__downloadFile__(info.get('urllibObj'))
		return True

	def __exit__(self, *args):
		if self.params.cookiefile: self.cookiejar.save()
