#!/usr/bin/env python3
# Server
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import glob, BTEdb, os, tarfile, traceback, mimetypes, wsgiref.simple_server, hashlib, json, threading, time, mako_server, configparser
import libtorrent as lt
class MutableDatabase:
	def seek(self,position,mode):
		pass
	def truncate(self):
		pass
	def __init__(self, data=""):
		self.data = data
	def write(self,data):
		self.data = data
	def flush(self):
		return False
	def read(self):
		return str(self.data)
	def close(self):
		pass

logfile = False

MasterDirectory = "/var/tpm-mirror"
PackagesDirectory = MasterDirectory + "/packages"
HTTPRoot = MasterDirectory + "/www/"

if not os.path.isdir(MasterDirectory):
	os.mkdir(MasterDirectory)
if not os.path.isdir(PackagesDirectory):
	os.mkdir(PackagesDirectory)
if not os.path.isdir(HTTPRoot):
	os.mkdir(HTTPRoot)

torrent = ""
tstatus = False

master = BTEdb.Database(MasterDirectory+"/package-index.json")
hashes = BTEdb.Database(MasterDirectory+"/hashes.json")

mako_server.config = configparser.SafeConfigParser()
mako_server.config.readfp(open(os.path.dirname(os.path.realpath(__file__))+"/config.conf"))

mako_server.root = HTTPRoot

mako_server.moduleObjects = mako_server.load_modules(os.path.dirname(os.path.realpath(__file__)) + "/modules", mako_server.config["server"]["modules"].split(mako_server.config["general"]["listDelimiter"]))

ses = lt.session()
ses.listen_on(6881, 6891)
ses.start_dht()
ses.start_upnp()
mimetypes.init()


def RegeneratePackageIndex():
	if not master.TransactionInProgress:
		master.BeginTransaction(False)
	for packagefile in glob.glob(PackagesDirectory+"/*.tpkg"):
		try:
			package = tarfile.open(packagefile,"r:gz")
			PackageInfo = BTEdb.Database(MutableDatabase(package.extractfile(package.getmember("info/package.json")).read().decode("utf-8"))) # Trust me, this probably works
			PackageDatapoint = PackageInfo.Dump("info")[0]
			if not master.TableExists(PackageDatapoint["PackageName"]):
				master.Create(PackageDatapoint["PackageName"])
			VersionsAlreadyDone = []
			for version in master.Dump(PackageDatapoint["PackageName"]):
				VersionsAlreadyDone.insert(0,version["Version"])
			packagefileobj = open(packagefile, "rb")
			if not PackageDatapoint["Version"] in VersionsAlreadyDone:
				x = []
				for y,z in PackageDatapoint.items():
					x.insert(0,[y,z]) # X becomes a list of lists, each list inside x is a key-value pair for properties of a package
				master.Insert(PackageDatapoint["PackageName"], Filename = os.path.basename(packagefile), *x) # Gets the filename and also appends all the elements of x to the end of the methodcall
			if not hashes.TableExists(os.path.basename(packagefile)):
				hashes.Create(os.path.basename(packagefile))
			if len(hashes.Dump(os.path.basename(packagefile))) == 0:
				hashes.Insert(os.path.basename(packagefile), Hash = hashlib.sha256(packagefileobj.read()).hexdigest())
			else:
				hashes.Update(os.path.basename(packagefile), hashes.Dump(os.path.basename(packagefile)), Hash = hashlib.sha256(packagefileobj.read()).hexdigest())

			packagefileobj.close()
		except:
			print(traceback.format_exc())
			continue
	master.CommitTransaction()
	GenerateLatestVersions()
def GenerateLatestVersions():
	if not master.TransactionInProgress:
		master.BeginTransaction(False)
	for package in master.ListTables():
		LatestReleaseEpoch = 0
		PackageLatestVersion = "Error"
		for version in master.Dump(package):
			if version["Version"] == "Latest":
				continue
			else:
				if version["ReleaseEpoch"] > LatestReleaseEpoch:
					LatestReleaseEpoch = version["ReleaseEpoch"]
					PackageLatestVersion = version["Version"]
		if len(master.Select(package,Version = "Latest")) == 0:
			master.Insert(package, Version = "Latest", LatestVersion = PackageLatestVersion)
		else:
			master.Update(package, master.Select(package, Version = "Latest"), LatestVersion = PackageLatestVersion)
	master.CommitTransaction()

def fix_for_wsgiref(st, encode = "utf-8"):
	if encode != False:
		return [st.encode(encode)]
	return [st] # This is because wsgiref is made for python 2 and still hasn't been updated properly

def serve(environ, start_response):
#	if environ["PATH_INFO"] == "/":
#		start_response("200 OK",  [('Content-type','text/html')])
#		return fix_for_wsgiref("""<!doctype html><html><head><meta http-equiv="refresh" content="0;URL='/index.pyhtml'" /></head><body>Redirecting...</body></html>""")
	if environ["PATH_INFO"].lower()[-len("torrent"):] == "torrent":
		start_response("200 OK", [('Content-type','application/x-bittorrent')])
		return fix_for_wsgiref(lt.bencode(torrent), False)
	if environ["PATH_INFO"].lower() == "/package-index.json":
		start_response("200 OK",  [('Content-type','application/json')])
		return fix_for_wsgiref(json.dumps(master.master)) # Only return master, don't want to send any triggers or savepoints
	if environ["PATH_INFO"].lower() == "/hashes.json":
		start_response("200 OK",  [('Content-type','application/json')])
		return fix_for_wsgiref(json.dumps(hashes.master))
	return fix_for_wsgiref(mako_server.serve(environ, start_response, packages = master.master, hashes = hashes.master))

def GenerateTorrent():
	fs = lt.file_storage()
	lt.add_files(fs, PackagesDirectory)
	t = lt.create_torrent(fs, flags = 1&8&16) # 16 does nothing right now
	#t = lt.create_torrent(fs)
	t.add_tracker("http://tpm.blogwithme.net:81/tracker")
	lt.set_piece_hashes(t,MasterDirectory)# ## Not working
	return t.generate()

def NewTorrent(pt):
	info = lt.torrent_info(pt) # This is necessary for some reason
	fs = lt.file_storage()
	lt.add_files(fs,PackagesDirectory)
	h = ses.add_torrent({"save_path": MasterDirectory, "storage_mode": lt.storage_mode_t.storage_mode_sparse, "ti": info, "storage": fs, "flags": 1})
	#h = ses.add_torrent({"save_path": PackagesDirectory, "storage_mode": lt.storage_mode_t.storage_mode_sparse, "ti": info, "storage": fs })
	print("New torrent added")
	return h

def GenerateAll():
	global torrent,tstatus
	RegeneratePackageIndex()
	torrent = GenerateTorrent()
	tstatus = NewTorrent(torrent)

print("Generating package index")
GenerateAll()
print("Generated package index")

def webserver():
	server = wsgiref.simple_server.make_server("",5001,serve)
	server.serve_forever()

def ReannounceDaemon():
	state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']
	while True:
		s = tstatus.status()
		print('\r%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, state_str[s.state]))
		print("Next announce: %s" % str(s.next_announce))
		tstatus.force_reannounce()
		time.sleep(30)
def RegenerateTimer():
	while True:
		tosleep = 12*3600 - (int(time.time()) % (12*3600))
		print("Sleeping " + str(tosleep) + " seconds")
		time.sleep(tosleep)
		print("Regenerating package index and torrentfile")
		GenerateAll()
		print("Regeneration terminated")

webthread = threading.Thread(target=webserver)
webthread.daemon = False # Important
webthread.start()
print("Serving on port 5001")

rtthread = threading.Thread(target=RegenerateTimer)
rtthread.daemon = False
rtthread.start()
print("Regenerating package index every 12 hours")

rdthread = threading.Thread(target=ReannounceDaemon)
rdthread.daemon = False
rdthread.start()
print("Regenerating package index every 12 hours")
