#!/usr/bin/env python3

import os, sys
import time
import socket
from .utils import *
from .downloader import *
from . import extractor

class MGet(FileDownloader):
	def __init__(self, opts, info):
		super(MGet, self).__init__(self)

		if opts.verbose: details.debug_info(info)
		self.info = info
		self.params = opts
		self.defurl = info.get('defurl')
		self.client = client.Client(info=self.info)
		self.ie_result = self.get_ie_result(self.defurl)
		self.url = self.ie_result.get('eurl') or self.ie_result.get('url', self.defurl)
		self.filename = self.info['filename'] = self.params.filename or \
				self.ie_result.get('filename') or info.get('def_page')
		self.cursize = self.getLocalFilesize(self.filename) or 0
		self.quitsize = self.params.quitsize
		self.hostname = self.ie_result.get('hostname')
		self.trying = 0

	def get_ie_result(self, url):
		try: return extractor.get_info(url, self.client, self.info)
		except ExtractorError as err:
			if self.info.get('debug_mget'): details.report_error(err._trace())
			else: details.report_error(str(err))
			exit(2)

	def __downloadFile__(self, urlObj):
		self.mode = 'wb' if self.cursize == 0 else 'ab'
		start = info['start_time'] = time.time()
		try:
			info['filename'], fileObj = common.open_stream(self.filename, self.mode)
			dl = MGetDownloader(urlObj,fileObj,info)
			try: dl.start()
			except (socket.timeout, socket.error) as err:
				details._error(str(err) + "\n")
				self.__retry__()
		except KeyboardInterrupt:
			self.cursize = self.getLocalFilesize(self.filename)
			details._quitting(self.filename,self.cursize,info.get('filesize'))
			exit(1)

		except (ContentTooShortError, DownloadError) as err:
			self.cursize = self.getLocalFilesize(self.filename)
			details._quitting(self.filename,self.cursize,info.get('filesize'))
			if self.info.get('debug_mget'): details.write_string(err._trace())
			else: details.report_error(err)
			if self.info.get('ignore'): return False
			else: exit(2)

		except (TypeError, ValueError, NameError) as err:
			self.cursize = self.getLocalFilesize(self.filename)
			details._quitting(self.filename,self.cursize,info.get('filesize'))
			if self.info.get('debug_mget'): details.FormatTrace(sys.exc_info())
			else: details.report_error(str(err))
			if self.info.get('ignore'): return False
			else: exit(2)

		finally:
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			self.cursize = self.getLocalFilesize(self.filename)
			fileObj.close(); urlObj.close()

		_opts= {'speed': self.calc_speed(time.time()-start, self.cursize-info['cursize']),
			'filename': self.filename,
			'cursize': self.cursize,
			'filesize': info.get('filesize')}

		details.done_dl(**_opts)
		return True

	def __retry__(self):
		progress = common.progress(self.cursize, info.get('filesize', 0))
		if progress >= self.params.quitsize:
			details.write_string(details.FILE_EXIST)

		self.trying += 1
		self.cursize = self.getLocalFilesize(self.filename)
		details.trying(self.trying,self.cursize,info.get('filesize'))
		time.sleep(int(info.get('waitretry', 1)))

		if self.cursize != info.get('filesize'):
			details.init_(url=self.url)
			details.report("Retrying download at: %s [%s]" % \
					(self.cursize,common.format_size(self.cursize)))
			self.resume(retrying=True)

	def resume(self, retrying = False):
		if retrying:
			details.report("Re-connecting to %s..." % self.hostname)
			_info = self.client.getInfos(self.url, self.cursize)
			if _info is None: return False

			info['cursize'] = self.cursize
			info['resuming'] = True if self.cursize != 0 else False
			info.update(_info)

			details.print_info(info)

		return self.__downloadFile__(info.get('urllibObj'))

	def start(self):
		global info
		if self.info.get('restart'): self.cursize = 0; self.mode = 'wb'
		if self.params.geturl or self.params.embedurl:
			details.report(self.url); return True
		if os.path.exists(self.filename) and not self.info.get('continue'):
			self.filename = self.EXFilename(self.filename)
			self.cursize = self.getLocalFilesize(self.filename) or 0

		details.init_(url=self.url)
		details.report("Connecting to %s..." % self.hostname)
		info = self.client.getInfos(self.url, self.cursize)

		if info is None: return False

		info['cursize'] = self.cursize
		info['resuming'] = True if self.cursize != 0 else False
		info.update(self.info)

		details.print_info(info)

		if self.params.dump_headers: details.write_string(str(info.get('headers', {})))
		if self.params.write_info: common.write_info(info)
		if self.params.dump_info: return True

		if self.params.quitsize != 100.0:
			progress = common.progress(self.cursize,info.get('filesize', 0))
			if progress >= self.params.quitsize:
				details.write_string(details.FILE_EXIST, False)
				return True

		self.cookiejar = info.get('cookiejar', None)
		if os.path.exists(self.filename) and info.get('continue'): return self.resume()

		return self.__downloadFile__(info.get('urllibObj'))

	def __exit__(self, *args):
		if self.params.cookiefile: self.cookiejar.save()
