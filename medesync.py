#!/usr/bin/python
# vim: ft=python columns=123 foldmethod=marker foldmarker=<<<,>>>
# Released under the terms of the BSD license, outlined below:

# Copyright (c) 2010, Davyd McColl
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution.
# * Neither the name of Davyd McColl nor the names of any other contributors 
#   may be used to endorse or promote products derived from this software 
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import ftplib
import time
import re
from opts import Options

try:
	import fcntl, termios, struct, os
	COLS = None
except:
	COLS = 78 # fallback

class SmartSync:
	def __init__(self): #<<<
		self.connected = False
		self.ftp = None
		self.__err__ = None
		self.show_status = True
		self.current_transfer = None
		self.host = None
		self.user = "anonymous"
		self.port = 21
		self.passwd = "foo@bar.com"
		self.ftp_conns = []
		self.io_chunk = 8192
		self.current_transfer = dict()
		self.current_transfer["total"] = 0
		self.current_transfer["bytes"] = 0
		self.current_transfer["name"] = "foobar"
		self.overall_transfers = dict()
		self.overall_transfers["total"] = 0
		self.overall_transfers["bytes"] = 0
		self.overall_transfers["start"] = None
		self.copy_errors = 0
		self.spinner = "|"
		self.last_progress = time.time()
		self.last_listing = []
		self.status_ticks = 0
		self.attempts = 120
#>>>
	def __deinit__(self):#<<<*/
		for conn in self.ftp_conns:
			try:
				conn.close()
			except Exception as e:
				pass
#>>>*/
	def spin(self):#<<<*/
		spinchars = ["|", "/", "-", "\\"]
		idx = spinchars.index(self.spinner)
		idx += 1
		if idx >= len(spinchars):
			idx = 0
		self.spinner = spinchars[idx]
		return self.spinner
#>>>*/
	def get_terminal_size(self):#<<<*/
		global COLS
		if COLS != None:
			return COLS, 25
		def ioctl_GWINSZ(fd):
			try:
				cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
			except:
				print("FAIL")
				return None
			return cr
		cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
		if not cr:
			try:
				fd = os.open(os.ctermid(), os.O_RDONLY)
				cr = ioctl_GWINSZ(fd)
				os.close(fd)
			except:
				pass
		if not cr:
			try:
				cr = (env['LINES'], env['COLUMNS'])
			except:
				cr = (25, 80)
		return int(cr[1]), int(cr[0])
#>>>*/
	def set_last_error(self, descr, err): #<<<
		self.__err__ = dict()
		self.__err__["description"] = descr
		self.__err__["exception"] = err
		if self.show_status:
			print("%s:\n  %s" % (descr, str(err)))
#>>>
	def feedback(self, fstr):#<<<
		self.cols, tmp = self.get_terminal_size()
		if self.show_status:
			maxlen = self.cols-6
			fstr = self.shorten(fstr, maxlen)
			if fstr.count("\n") == 0:
				while (len(fstr) < maxlen):
					fstr += " "
			sys.stdout.write(fstr)
			sys.stdout.flush()
#>>>
	def show_ok(self):#<<<
		if self.show_status:
			print("[ OK ]")
	#>>>
	def show_fail(self):#<<<
		if self.show_status:
			print("[FAIL]")
#>>>
	def get_last_error(self):#<<<
		if self.__err__ != None:
			return self.err["description"], self.err["exception"]
		else:
			return "", None
#>>>
	def clear_last_error(self):#<<<
		self.__error__ = None
#>>>
	def connect(self, host, user, passwd):#<<<
		if self.ftp != None:
			self.ftp.quit()
		else:
			self.ftp = ftplib.FTP()
		try:
			self.feedback("Connecting to %s" % (host))
			self.ftp.connect(host, 21, 60)
			self.show_ok()
			self.feedback("Logging in...")
			self.ftp.login(user, passwd)
			self.show_ok()
			self.feedback("Setting PASV")
			self.ftp.set_pasv(True)
			self.show_ok()
			self.connected = True
		except Exception as e:
			self.show_fail()
			self.set_last_error("Unable to connect to FTP host", e)
		return self.connected
#>>>
	def split_uri(self, uri):#<<<
		parts = uri.split("://")
		ret = dict()
		if len(parts) > 1:
			ret["protocol"] = parts[0].lower()
			uri = "://".join(parts[1:])
		else:
			ret["protocol"] = "file"
			uri = parts[0]
		if ret["protocol"] == "file":
			ret["host"] = None
			ret["path"] = uri
		else:
			parts = uri.split("/")
			ret["host"] = parts[0]
			if len(parts) == 0:
				ret["path"] = ""
			else:
				ret["path"] = "/".join(parts[1:])
			parts = ret["host"].split("@")
			if len(parts) == 0:
				ret["user"] = None
				ret["password"] = None
			else:
				ret["host"] = parts[-1]
				tmp = "@".join(parts[0:-1])
				parts = tmp.split(":")
				ret["user"] = parts[0]
				ret["password"] = ":".join(parts[1:])
			parts = ret["host"].split(":")
			if len(parts) == 1:
				ret["port"] = None
			else:
				ret["port"] = int(parts[-1])
				ret["host"] = parts[0:-1]
		if ret["protocol"] == "ftp":
			ret["timeout"] = 30
			ret["passive"] = True
			ret["path"] = ret["path"].replace(os.sep, "/")
		return ret
#>>>
	def ls_R(self, path, include_dirs = False, prepend_dirname = True):#<<<
		uri_parts = self.split_uri(path)
		if uri_parts["protocol"] == "file":
			return self.ls_R_local(uri_parts["path"], include_dirs, prepend_dirname)
		elif uri_parts["protocol"] == "ftp":
			return self.ls_R_ftp(uri_parts, include_dirs, prepend_dirname)
		else:
			print("Can't ls-r on %s" % (path))
			return []
#>>>
	def resolvebool(self, opts, key, default):#<<<
		if list(opts.keys()).count(key) > 0:
			return opts[key]
		else:
			return default
#>>>
	def remove_ignored(self, l, regex):#<<<*/
		if len(regex) == 0:
			return l
		out = []
		for f in l:
			m = re.match(regex, f)
			if m == None:
				out.append(f)
		return out
#>>>*/
	def sync(self, options):#<<<
		self.dummy = self.resolvebool(options, "dummy", False)
		self.overwrite = self.resolvebool(options, "overwrite", True)
		to_copy = []
		to_remove = []
		to_archive = []
		if self.dummy:
			self.feedback("! Dummy operation !\n")
		# get a listing of all files and dirs under local_src
		local_files = self.remove_ignored(self.ls_R(options["src"], True, False), options["ignore"])
		# get a listing of all files and dirs under remote_dst
		remote_files = self.ls_R(options["dst"], True, False)
		if options["archive"] != None:
			watched_files = []
			for f in remote_files:
				if remote_files.count(f + ".t") > 0:
					# add this file to the archive list
					to_archive.append(f)
			dotparts = f.split(".")
			if dotparts[-1] == "t" and remote_files.count(".".join(dotparts)) == 0:
				# remove orphaned watched file indicators
				to_remove.append(f)
			tmp = []
			# remove watched markers from remote listing
			for f in remote_files:
				if to_remove.count(f) == 0:
					tmp.append(f)
			remote_files = tmp
		remote_files = self.remove_ignored(remote_files, options["ignore"])
		# create a list of all files missing from remote_dst
		#		also create a list of all files missing from src (to del)
		idx = 0
		total_files = len(local_files)
		for f in local_files:
			spinner = self.spin()
			perc = (idx * 100.0) / total_files
			idx += 1
			self.status("Calculating workload [ %2i %%] %s" % (perc, spinner))
			if self.isdir(options["src"], f):
				continue
			src_size = self.filesize(options["src"], f)
			if remote_files.count(f) == 0:
				self.overall_transfers["total"] += src_size
				if self.dummy:
					self.status("")
					print("Missing: %s" % f)
				to_copy.append(f)
				continue
			dst_size = self.filesize(options["dst"], f)
			if src_size == -1 or dst_size == -1:
				return False
			if src_size != dst_size:
				if self.dummy:
					self.status("")
					print("%s: %i vs %i" % (f, src_size, dst_size))
				self.overall_transfers["total"] += src_size
				to_copy.append(f)
		for f in remote_files:
			if local_files.count(f) == 0:
				to_remove.append(f)
		self.status("")
		self.feedback("Calculating workload")
		self.show_ok()
		if len(to_remove) == 0 and len(to_copy) == 0 and len(to_archive) == 0:
			self.status("%s up to date\n" % (options["dst"]))
			return True
		# archive watched files; push these files onto the to_remove stack
		for f in to_archive:
			# perform local move (may be a rename, may be a copy-and-delete)
			if self.move_file(options["src"], f, options["archive"], f):
				# add the remote file to the to_remote list
				to_remove.append(f)
			# add watched indicator file to to_remove list
				to_remove.append(f + ".t")

		# remove extra remote files first (perhaps need the space)
		for f in sorted(to_remove, reverse=True):
			if self.remove(options["dst"], f):
				self.status("")
				self.feedback("Remove remote: %s" % (f))
				self.show_ok()
			else:
				self.status("")
				self.feedback("Remove remote: %s" % (f))
				self.show_fail()
		# copy missing remote files
		self.overall_transfers["start"] = time.time()
		print("Overall transfer size: " + str(self.overall_transfers["total"]))
		for f in to_copy:
			if self.isdir(options["src"], f):
				continue
			if self.copy_file(options["src"], options["dst"], f):
				self.status("")
				self.feedback("Copy file: %s" % (f))
				self.show_ok()
			else:
				self.status("")
				self.feedback("Copy file: %s" % (f))
				self.show_fail()
		# archive src files which have disappeared from the dst, if required
		if list(options.keys()).count("archive") > 0:
			pass
	print("")
#>>>
	def move_file(self, uri_from, relative_from, uri_to, relative_to):
		uri_parts_from = self.split_uri(uri_from)
		uri_parts_to = self.split_uri(uri_to)
		self.feedback("Archiving %s" % (relative_from))
		if uri_parts_from["protocol"] != uri_parts_to["protocol"]:
			self.show_fail()
			print("(Can't move files across protocols)")
			return False
		if uri_parts_to["protocol"] == "ftp":
			dirname = "/".join(relative_to.split("/")[:-1])
			if not self.ensure_dir_exists(uri_to, dirname):
				self.show_fail()
				print("(Can't make dest dir at %s)" % (dirname))
				return False
			try:
				ftp = self.mkftp2(uri_parts_to)
				if ftp == None:
					self.show_fail()
					print("(Can't get FTP connection)")
					return False
				if not self.dummy:
					ftp.rename(relative_from, relative_to)
				self.show_ok()
				return True
			except Exception as e:
				self.show_fail()
				print("Can't move file %s at ftp://%s to %s: %s" % (relative_from, uri_parts_to["host"], relative_to, str(e)))
				return False
		elif uri_parts_to["protocol"] == "file":
			dirname = os.sep.join(relative_to.split(os.sep)[:-1])
			_from = os.path.join(uri_from, relative_from)
			_to = os.path.join(uri_to, relative_to)
			if not self.ensure_dir_exists(uri_to, dirname):
				self.show_fail()
				print("Can't make dest dir at %s" % (dirname))
				return False
			try:
				if not self.dummy:
					os.rename(_from, _to)
				else:
					print("\nrename: %s => %s" % (_from, _to))
				self.show_ok()
				return True
			except Exception as e:
				try:
					if not self.dummy:
						open(_to, "wb").write(open(_from, "rb").read())
						os.remove(_from)
					self.show_ok()
					return True
				except Exception as e:
					print("Can't copy-and-del %s to %s: %s" % (_from, _to, str(e)))
					self.show_fail()
					return False
		else:
			print("%s: unsupported protocol for file_move" % (uri_parts_to["protocol"]))
			# unsupported protocol
			return False

	def isdir(self, uri_base, relative_path):
		uri_parts = self.split_uri(uri_base)
		if uri_parts["protocol"] == "file":
			sep = os.sep
		else:
			sep = "/"
		fullpath = uri_parts["path"] + sep + relative_path
		if uri_parts["protocol"] == "file":
			return os.path.isdir(fullpath)
		else:
			ftp = self.mkftp2(uri_parts)
			if ftp == None:
				return False
			return self.is_ftp_dir(ftp, fullpath)

	def remove(self, uri_base, relative_path):#<<<
		if self.dummy:
			return True
		uri_parts = self.split_uri(uri_base)
		if uri_parts["protocol"] == "file":
			try:
				f = os.path.sep.join([uri_parts["path"], relative_path])
				if self.dummy:
					self.feedback("local remove: %s" % (f))
				else:
					if os.path.isdir(f):
						os.rmdir(f)
					else:
						os.remove(f)
			except Exception as e:
				self.set_last_error("Unable to remove file %s" % uri_parts["path"], e)
				return False
		elif uri_parts["protocol"] == "ftp":
			ftp = self.mkftp2(uri_parts)
			if ftp == None:
				return False
			try:
				f = "/".join([uri_parts["path"], relative_path])
				if self.dummy:
					self.feedback("remote remove: %s" % (f))
				else:
					f_sane = f #self.sanitise_ftp_path(f)
					if self.is_ftp_dir(ftp, f_sane):
						ftp.cwd("/")
						ftp.rmd(f)
					else:
						if self.filesize(uri_base, relative_path) > -1:
							ftp.delete(f_sane)
				return True
			except Exception as e:
				self.set_last_error("Unable to remove file %s :: %s" % (uri_base, relative_path), e)
				return False
		else:
			return False
#>>>
	def ensure_dir_exists(self, uri_base, relative_path):#<<<
		up = self.split_uri(uri_base)
		if up["protocol"] == "file":
			return self.ensure_dir_exists_local(os.sep.join([up["path"], relative_path]))
		elif up["protocol"] == "ftp":
			return self.ensure_dir_exists_ftp(up, relative_path)
		else:
			return False
#>>>
	def ensure_dir_exists_local(self, path):#<<<
		parts = os.path.split(path)
		test = ""
		if self.dummy:
			self.feedback("! Check local dir: %s\n" % (path))
			return True
		for part in parts:
			if len(test) > 0: test += os.sep
			test += part
			if not os.path.isdir(test):
				try:
					os.path.mkdir(test)
				except Exception as e:
					self.set_last_error("Unable to make dir %s" % test, e)
					return False
		return True
#>>>
	def ensure_dir_exists_ftp(self, uri_parts, relative_path):#<<<
		ftp = self.mkftp2(uri_parts)
		if ftp == None:
			return False
		relative_path = relative_path.replace(os.sep, "/")
		parentdir = "/".join(relative_path.split("/")[:-1])
		path = uri_parts["path"]
		if len(parentdir) > 0:
			path += "/" + parentdir
		parts = path.split("/")
		test = ""
		if self.dummy:
			self.feedback("! Check remote dir: %s\n" % (path))
			return True
		for part in parts:
			if len(test) > 0: test += "/"
			test += part
			if not self.is_ftp_dir(ftp,test):
				try:
					ftp.mkd(test)
				except Exception as e:
					self.set_last_error("Unable to make dir %s on %s" % (test, uri_parts["host"]), e)
					return False
		return True	
#>>>
	def show_progress(self, label, fraction):
		cols, rows = self.get_terminal_size()
		label = self.shorten(label, int(float(cols) * 0.90))
		rem = cols - len(label) - 4
		bars = int(fraction * rem)
		draw_arrow = False
		if (bars > 0): 
			bars -= 1
			draw_arrow = True
		label += " [" + (bars * "=") 
		if draw_arrow:
			label += ">"
			rem -= 1
		label += ((rem - bars) * " ")	+ "]"
		self.status(label, False)

	def copy_file(self, src_base, dst_base, relative_path):#<<<
		up_src = self.split_uri(src_base)
		up_dst = self.split_uri(dst_base)

		# ensure that the remote dir exist
		if not(self.ensure_dir_exists(dst_base, relative_path)):
			return False
		
		# copy the file
		if up_src["protocol"] == "file":
			if up_dst["protocol"] == "file":
				return self.copy_file_local_to_local(src_base, dst_base, relative_path)
			elif up_dst["protocol"] == "ftp":
				return self.copy_file_local_to_ftp(src_base, dst_base, relative_path)
		elif up_src["protocol"] == "ftp":
			print("FTP source not supported (yet)")
			return False
		else:
			print("Protocol %s not supported (yet)" % up_src["protocol"])
			return False
#>>>
	def copy_file_local_to_ftp(self, src, dst, rel):#<<<
		for i in range (self.attempts):
			srcpath = os.path.join(src, rel)
			dstpath = "/".join([dst, rel])
			uri_parts = self.split_uri(dstpath)
			if self.dummy:
				self.feedback("! copy: %s\n" % (rel))
				print("! dst:  %s\n" % uri_parts["path"])
				return True
			ftp = self.mkftp2(uri_parts)
			ftp.cwd("/")
			if ftp == None:
				print("Can't copy %s: Can't get ftp object")
				return False
			parentdir = "/".join(rel.split("/")[:-1])
			if not self.ensure_dir_exists(dst, parentdir):
				print("Can't make dir %s" % (parentdir))
			try:
				self.current_transfer["total"] = os.stat(srcpath).st_size
				self.current_transfer["start"] = time.time()
				if self.is_ftp_dir(ftp, uri_parts["path"]):
					ftp.rmd(uri_parts["path"])
				else:
					rsize = None
					try:
						rsize = ftp.size(uri_parts["path"])
					except:
						pass
					if rsize != None and rsize != self.current_transfer["total"]:
						ftp.delete(uri_parts["path"])
				self.current_transfer["bytes"] = 0
				self.current_transfer["name"] = uri_parts["path"].split("/")[-1]
				if self.current_transfer["total"] > 0:
					fpsrc = open(srcpath, "rb")
					#print("STOR %s" % (uri_parts["path"].replace(" ", "%20")))
					ftp.cwd("/")
					ftp.storbinary("STOR %s" % (uri_parts["path"]), fpsrc, self.io_chunk, self.ftp_status)
					fpsrc.close()
				return True
			except Exception as e:
				if Exception == KeyboardInterrupt:
					sys.exit(1)
				print("Can't copy %s: %s" % (rel, str(e)))
			time.sleep(1)
		print("Giving up on %s" % (rel))
		return False

	def humanreadable(self, b, s):
		suf = ["b", "Kb", "Mb"]
		rate = float(b) / float(s)
		for i in range(len(suf)):
			if rate < 1024:
				return "%.2f%s/s" % (rate, suf[i])
			rate /= 1024.0
		return "%.2f%s/s" % (rate, suf[-1])

	def human_readable_time(self, secs):
		s = secs % 60
		m = int(secs / 60) % 60
		h = int(secs / 3600)
		if h > 0:
			return "%02i:%02i:%02i" % (h,m,s)
		elif m > 0:
			return "%02i:%02i" % (m,s)
		else:
			return "%2is" % (s)

	def ftp_status(self, b):
		chunk = len(b)
		now = time.time()
		self.overall_transfers["bytes"] += chunk
		self.current_transfer["bytes"] += chunk
		spinner = self.spin()
		if now - self.last_progress < 0.3:
			return
		self.last_progress = now
		perc = float(self.current_transfer["bytes"]) / float(self.current_transfer["total"])
		r = self.humanreadable(self.current_transfer["bytes"], (now - self.current_transfer["start"]))
		rbytes = float(self.current_transfer["bytes"]) / (float(now - self.current_transfer["start"]))
		#overall_r = float(self.overall_transfers["bytes"]) / (now - self.overall_transfers["start"])
		etr = int((float(self.overall_transfers["total"] - self.overall_transfers["bytes"]) / rbytes))
		hetr = self.human_readable_time(etr)
		label = "%s [%s %s] %s" % (self.current_transfer["name"], r, hetr, spinner)
		self.show_progress(label, perc)
#>>>
	def copy_file_local_to_local(self, src, dst, rel):#<<<
		if self.dummy:
			self.feedback("! copy: %s\n" % (rel))
		srcpath = os.path.join(src, rel)
		dstpath = os.path.join(dst, rel)
		if not self.ensure_dir_exists(dst, os.path.dirname(rel)):
			print("Can't make dir: %s" % (os.path.dirname(dstpath)))
			return False
		try:
			fpsrc = fopen(srcpath, "rb")
			fpdst = fopen(dstpath, "wb")
			total = os.stat(fpsrc).st_size
			transferred = 0
			while not fpsrc.eof():
				self.show_progress(rel, float(transferred) / float(total))
				chunk = fpsrc.read(self.io_chunk)
				fpdst.write(chunk)
				fpdst.flush()
				transferred += self.io_chunk
			self.feedback("Copy %s" % (rel))
			self.show_ok()
			return True
		except Exception as e:
			print("Copy %s fails: %s" % (rel, str(e)))
			return False
#>>>
	def shorten(self, checkstr, maxlen = None):#<<<
		if maxlen == None:
			maxlen, rows = self.get_terminal_size()
		if len(checkstr) >= maxlen:
			newstr = checkstr[:(maxlen/2)-3] + "..." 
			newstr += checkstr[(len(checkstr) - (maxlen/2))+3:]
			checkstr = newstr
		return checkstr
#>>>
	def status_callback(self, blocks):#<<<
		if not self.show_status:
			return
#>>>
	def status(self, statusstr, autofit = True):#<<<
		if not self.show_status:
			return
		cols, rows = self.get_terminal_size()
		if autofit:
			statusstr = self.shorten(statusstr)
		sys.stdout.write("\r%s\r%s" % ((cols * " "), statusstr))
		sys.stdout.flush()
#>>>
	def clear_status(self): #<<<
		sys.stdout.write("\r%s\r" % (78 * " "))
		sys.stdout.flush()
#>>>
	def ls_R_local(self, dirname, include_dirs=False, prepend_dirname = True): #<<<
		self.feedback("Listing local dir: %s" % (dirname))
		stack = [dirname]
		ret = []
		items = 0
		while stack:
			thisdir = stack.pop(0)
			for f in sorted(os.listdir(thisdir)):
				items += 1
				path = os.path.join(thisdir, f)
				if os.path.isdir(path):
					if include_dirs:
						if prepend_dirname:
							ret.append(path)
						else:
							ret.append(path[len(dirname)+1:])
					stack.append(path)
					continue
				if prepend_dirname:
					ret.append(path)
				else:
					ret.append(path[len(dirname)+1:])
		self.show_ok()
		return ret
#>>>
	def mkftp2(self, uri_parts):#<<<
		return self.mkftp(uri_parts["host"],uri_parts["user"],uri_parts["password"],\
			uri_parts["port"],uri_parts["timeout"],uri_parts["passive"])
#>>>
	def mkftp(self, host, user, password, port = None, timeout=None, passive=None):#<<<
		if host == None: host = "localhost"
		if user == None: user = "anonymous"
		if port == None: port = 21
		if password == None: password = "foo@bar.com"
		if timeout == None: timeout = 30
		if passive == None: passive = True
		# look for a matching conn in the pool
		ftp = None
		for f in self.ftp_conns:
			if f["host"] == host and \
					f["user"] == user and \
					f["password"] == password and \
					f["port"] == port and \
					f["timeout"] == timeout and \
					f["passive"] == passive:
				#test if ftp object is still alive
				try:
					ftp = f["client"]
					ftp.cwd(".")
					return ftp
				except:
					ftp.close()
				break
		try:
			if ftp == None:
				ftp = ftplib.FTP()
			ftp.connect(host, port, timeout)
			ftp.login(user, password)
			ftp.set_pasv(passive)
			# cache connection
			f = {"host":host, "user":user, "password":password, "port": port, "timeout":timeout, "passive":passive, "client":ftp}
			self.ftp_conns.append(f)
			return ftp
		except Exception as e:
			self.set_last_error("Unable to connect to ftp://%s:%s@%s:%i" % (user, password, host, port), e)
			return None
		#>>>
	def filesize(self, base_uri, relative_path):
		uri_parts = self.split_uri(base_uri)
		if uri_parts["protocol"] == "file":
			try:
				return os.stat(os.sep.join([uri_parts["path"], relative_path])).st_size
			except Exception as e:
				self.set_last_error("filesize: can't stat %s%s%s" % (base_uri, os.sep, relative_path), e)
				return 0
		elif uri_parts["protocol"] == "ftp":
			ftp = self.mkftp2(uri_parts)
			if ftp == None:
				self.set_last_error("filesize: can't get ftp object for %s/%s" % (base_uri, relative_path), None)
				return -1
			if True:
			#try:
				self.last_listing = []
				path = self.sanitise_ftp_path("/".join([uri_parts["path"], relative_path]))
				ftp.dir(path, self.catch_dir)
				if len(self.last_listing) == 0:
					return 0
				parts = self.get_non_empty(self.last_listing[0].split(" "))
				self.last_listing = []
				return int(parts[4])
				#return ftp.size("/".join([uri_parts["path"], relative_path]))
			#except Exception as e:
			else:
				return 0
		else:
			return -1

	def sanitise_ftp_path(self, p):
		return p.replace("[", "\[").replace("]", "\]")

	def catch_dir(self, line):
		self.last_listing.append(line)

	def get_non_empty(self, l):
		out = []
		for item in l:
			if len(item) > 0:
				out.append(item)
		return out

	def ls_R_ftp(self, uri_parts, include_dirs = False, prepend_dirname = True):#<<<
		ftp = self.mkftp(uri_parts["host"], uri_parts["user"], \
			uri_parts["password"], uri_parts["port"], uri_parts["timeout"], \
			uri_parts["passive"])
		if ftp == None:
			return[]
		stack = [uri_parts["path"]]
		ret = []
		items = 0
		while stack:
			thisdir = stack.pop(0)
			self.feedback("Listing remote dir: %s" % (thisdir))
			ftp.cwd("/")
			contents = sorted(ftp.nlst(thisdir))
			#print("\ncontents: " + str(contents))
			for f in contents:
				items += 1
				#print("%i: %s" % (items, f))
				path = "/".join([thisdir, f])
				if self.is_ftp_dir(ftp, path):
					#print("\nrdir: %s" % path)
					if include_dirs:
						if prepend_dirname:
							ret.append(path)
						else:
							ret.append(path[len(uri_parts["path"])+1:])
					stack.append(path)
					#print("\nstack: " + str(stack))
				else:
					#print("\nrfile: %s" % f)
					if prepend_dirname:
						ret.append(path)
					else:
						ret.append(path[len(uri_parts["path"])+1:])
			self.show_ok()
		ftp.close()
		del ftp
		return ret
#>>>
	def is_ftp_dir(self, ftp, dirname):#<<<
		# TODO: find a faster way to do this
		current = ftp.pwd()
		try:
			if len(dirname) == 0:
				return False
			ftp.cwd(dirname)
			ftp.cwd(current)
			return True
		except:
			ftp.cwd(current)
			return False
#>>>

if __name__ == "__main__":
	opts = Options()
  #def add_opt(self, opt, help = "(no help)", aliases = [], consumes = 0, 
  #    consumes_help = "", default="", short_help="", required=False, datatype="string"):
	opts.add_opt("-s", help = "Source directory", aliases=["-src", "--src"], consumes = 1, \
		consumes_help = "<source url/path>", required = True)
	opts.add_opt("-d", help="Destination directory", aliases=["-dst", "--dst"], consumes=1, \
		consumes_help="<destination url/path>", required=True)
	opts.add_opt("-a", help="Files which have been copied in a previous run and are now "\
													+ "found to be missing are archived to this location", \
													short_help="Archive location", aliases=["-archive", "--archive"], consumes=1, \
													required=False)
	opts.add_opt("-dummy", help="Prints out information about what would be done, but doesn't actually do it", \
		aliases = ["--dummy"], consumes=0,short_help="Dummy run")
	opts.add_opt("-i", "Regular expression to match source and destination paths not to bother synchronising" \
											+ " (default matches watched indicator files on mede8er players)", \
		aliases = ["-ignore", "--ignore"], consumes=1, short_help="Ignore paths matching regex",\
			default=".*\\.t$", consumes_help = "<regular expression>")
	opts.parseargs()
	if opts.required_missing():
		sys.exit(1)

	f = SmartSync()
	cmdopts = dict()
	cmdopts["src"] = opts.value("-s")
	cmdopts["dst"] = opts.value("-d")
	if opts.selected("-a"):
		cmdopts["archive"] = opts.value("-a")
	else:
		cmdopts["archive"] = None
	cmdopts["dummy"] = opts.selected("-dummy")
	cmdopts["ignore"] = opts.value("-i")
	#opts = {"src":"/mnt/piggy/%s/new" % base,\
	#				"dst":"ftp://daf:h4xx0r@mede8er/%s" % base,\
	#				"name":base, \
	#				"dummy":False,
	#				"ignore":".*\\.t$"}
	try:
		f.sync(cmdopts)
	except KeyboardInterrupt:
		print("\n>> user abort <<")

