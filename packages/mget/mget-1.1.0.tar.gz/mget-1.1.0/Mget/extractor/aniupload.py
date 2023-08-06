#!/usr/bin/env python3

import re
from .common import InfoExtractor

class Aniupload_IE(InfoExtractor):
	_VIDEO_ID = r'^(?:https?://)?(?:www\.)?aniupload\.com/embed-([a-z-A-Z-0-9]+)'
	_VIDEO_URL = r'^(?:https?://)?(?:www\.)?aniupload\.com/(?:.*)'
	_PATTERN =  r'(?:https?://)[^\s<>"]+aniupload\.com[^\s<>"]+'

	def __init__(self, url, **kwargs):
		self.url = url
		self.client = kwargs.pop('client', None)
		self.wpage = kwargs.pop('wpage', False)

	def _dl_url(self, **kwargs):
		if not re.match(self._VIDEO_URL, self.url): return None
		video_id = self.search_regex(self._VIDEO_ID, self.url, 'aniupload')
		data = self._get_webpage(self.url, self.client, wpage=self.wpage)
		url = self.findall_regex(self._PATTERN, str(data['webpage']), 'aniupload')

		name, ext = self.getFilename(url).split('.')
		filename = "%s-%s.%s" % (name,video_id,ext)

		return {'url': url,
			'filename': filename}
