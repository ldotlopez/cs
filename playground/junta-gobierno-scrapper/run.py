#!/usr/bin/env python3

import os
from urllib import request, parse
from os import path
import os
import bs4
import urllib
import subprocess
import re


class Storage:
	def __init__(self, storage):
		self.storage = path.realpath(storage)

	def open(self, name, mode='rb', *args, **kwargs):
		fullpath = self.get_path(name)

		if 'w' in mode:
			os.makedirs(path.dirname(fullpath), exist_ok=True)

		return open(fullpath, mode, *args, **kwargs)

	def get_path(self, name, create_dirs=False):
		fullpath = self.storage + '/' + name
		fullpath = path.realpath(fullpath)
		if (not fullpath or
				fullpath == self.storage or 
				not fullpath.startswith(self.storage + '/')):
			raise ValueError(name)

		return fullpath

	def walk(self):
		for dirpath, dirnames, filenames in os.walk(self.storage):
			yield dirpath[len(self.storage):] or '/', dirnames, filenames

	def load(self, name, mode='rb', *args, **kwargs):
		fh = self.open(name, mode, *args, **kwargs)
		buff = fh.read()
		fh.close()
		return buff

	def save(self, name, buff):
		fh = self.open(name, 'wb')
		buff = fh.write(buff)
		fh.close()

	def get_info(self, name):
		return os.stat(self.get_path(name))

class Fetcher:
	def __init__(self, headers=None):
		self.headers = {}
		if headers:
			self.headers.update(headers)

		lc_headers = {k.lower(): v for (k, v) in headers.items()}
		self.referer = lc_headers.get('referer')

	def fetch(self, url, headers=None):
		req = request.Request(url)

		req_headers = {}
		req_headers.update(self.headers)
		if headers:
			req_headers.update(headers)

		for (k, v) in req_headers.items():
			req.add_header(k, v)

		if self.referer:
			req.add_header('Referer', self.referer)

		with request.urlopen(req) as resp:
			self.referer = url
			return resp.read(), resp.info().items()


class Config:
	FETCHER_HEADERS = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36'
	}
	PDF_INDEX = 'http://www.castello.es/web30/pages/contenido_web20.php?cod0=7&cod1=48&cod2=164&idcont=1180'
	STORAGE_PATH = path.realpath(path.dirname(__file__)) + '/storage/'
	PDF_TO_TEXT = '/usr/bin/pdftotext'
	MATCHES = [
		'pelayo',
		'f.elix\s+breva',
		'lepanto',
		'jorge\s+juan',
		'barrachina',
		'v.zquez\s+mella',
		'arquitecto\s+ros',
		'rep.blica\s+argentina',
		'sidro\s+vilar+oig',
		'pintor\s+camar.n',
		'figueroles',
		'gran\s+v.a'
	]

storage = Storage(Config.STORAGE_PATH)
fetcher = Fetcher(headers=Config.FETCHER_HEADERS)


def get_available_pdfs(remote=Config.PDF_INDEX):
	buff, headers = fetcher.fetch(remote)
	soup = bs4.BeautifulSoup(buff, "html.parser")
	hrefs = [x.attrs.get('href') for x in soup.select('a')]
	hrefs = [x for x in hrefs if x and 'JGL' in x]
	return hrefs

def fix_url(url):
	parsed = parse.urlparse(url)
	parsed = parsed._replace(path=parse.quote(parsed.path))
	return parse.urlunparse(parsed)

def exists_and_has_content(x):
	try:
		info = storage.get_info(x)
		return info.st_size > 0
	except FileNotFoundError:
		return False

# Download all available PDFs
for pdf in get_available_pdfs():
	name = path.basename(pdf)
	if exists_and_has_content(name):
		print("{pdf} already downloaded".format(pdf=pdf))
		continue


	try:
		buff, dummy = fetcher.fetch(fix_url(pdf))
	except urllib.error.HTTPError as e:
		print("Error downloading {url}: {e}".format(url=pdf, e=str(e)))
		continue

	print("Downloaded {pdf} ({x} bytes)".format(pdf=pdf, x=len(buff)))
	storage.save(name, buff)


# Convert pdfs into text
for dirpath, dirnames, filenames in storage.walk():
	filenames = [x for x in filenames if x.lower().endswith('.pdf')]

	for filename in filenames:
		txtfilename = dirpath + filename[:-3] + 'txt'
		if exists_and_has_content(txtfilename):
			continue

		subprocess.check_call([
			Config.PDF_TO_TEXT, 
			storage.get_path(dirpath + filename),
		])

# Check text
for dirpath, dirnames, filenames in storage.walk():
	filenames = [x for x in filenames if x.lower().endswith('.txt')]

	for filename in sorted(filenames):
		buff = storage.load(filename, 'r')
		for m in Config.MATCHES:
			if re.search(m, buff, re.IGNORECASE | re.MULTILINE):
				print("'{m}: {f}'".format(m=m, f=filename))
