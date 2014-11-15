#!/usr/bin/env python3
# Server
import glob, BTEdb, os, tarfile, traceback, mimetypes, wsgiref.simple_server, hashlib, json, threading, time
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

MasterDirectory = "/var/tpm-mirror"
PackagesDirectory = MasterDirectory + "/packages"
HTTPRoot = MasterDirectory + "/www"

if not os.path.isdir(MasterDirectory):
	os.mkdir(MasterDirectory)
if not os.path.isdir(PackagesDirectory):
	os.mkdir(PackagesDirectory)
if not os.path.isdir(HTTPRoot):
	os.mkdir(HTTPRoot)

torrent = ""

master = BTEdb.Database(MasterDirectory+"/package-index.json")

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
			if not PackageDatapoint["Version"] in VersionsAlreadyDone:
				x = []
				for y,z in PackageDatapoint.items():
					x.insert(0,[y,z]) # X becomes a list of lists, each list inside x is a key-value pair for properties of a package
				packagefileobj = open(packagefile, "rb")
				master.Insert(PackageDatapoint["PackageName"], Filename = os.path.basename(packagefile), Hash = hashlib.sha256(packagefileobj.read()).hexdigest() , *x) # Gets the filename and also appends all the elements of x to the end of the methodcall
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

def fix_for_wsgiref(st):
	return [st.encode("utf-8")] # This is because wsgiref is made for python 2 and still hasn't been updated properly
def serve(environ, start_response):
	if environ["PATH_INFO"] == "/":
		start_response("200 OK",  [('Content-type','text/html')])
		return fix_for_wsgiref("""<!doctype html><html><head><meta http-equiv="refresh" content="0;URL='/index.html'" /></head><body>Loading...</body></html>""")
	if environ["PATH_INFO"].lower()[-len("torrent"):] == "torrent":
		start_response("200 OK", [('Content-type','application/x-bittorrent')])
		return fix_for_wsgiref(lt.bencode(torrent))
	if environ["PATH_INFO"].lower() == "/package-index.json":
		start_response("200 OK",  [('Content-type','application/json')])
		return fix_for_wsgiref(json.dumps(master.master)) # Only return master, don't want to send any triggers or savepoints
	filename = HTTPRoot + environ["PATH_INFO"]
	if os.path.exists(filename):
		mime = mimetypes.guess_type(filename)[0]
		if not mime:
			mime = "text/text"
		start_response("200 OK", [('Content-type',mime)])
		fileObj = open(filename)
		returnvalue = fileObj.read()
		fileObj.close()
		return fix_for_wsgiref(returnvalue)
	else:
		start_response("404 Not Found", [('Content-type',"text/html")])
		return fix_for_wsgiref("""<!doctype html><html><head><title>TPM Package Repository</title></head><body><h1>404 Not Found</h1><pre>"""+environ["PATH_INFO"]+"""</pre> was not found</body></html>""")

def GenerateTorrent():
	fs = lt.file_storage()
	lt.add_files(fs, "/var/tpm-mirror/packages/")
	t = lt.create_torrent(fs, flags = 1&8&16) # 16 does nothing right now as lt.set_piece_hashes isn't being called
	t.add_tracker("udp://tracker.publicbt.com:80")
	#lt.set_piece_hashes(t,"/var/tpm-mirror/packages/") # Not working
	return t.generate()


mimetypes.init()

def webserver():
	server = wsgiref.simple_server.make_server("",5001,serve)
	server.serve_forever()

webthread = threading.Thread(target=webserver)
webthread.daemon = False # Important
webthread.start()
print("Serving on port 5001")

def RegenerateTimer():
	print("Generating package index")
	RegeneratePackageIndex()
	torrent = GenerateTorrent()
	print("Generated package index")
	tosleep = 12*3600 - (int(time.time()) % (12*3600))
	print("Sleeping " + str(tosleep) + " seconds")
	time.sleep(tosleep)
	while True:
		time.sleep(12*3600) # 12 hours
		print("Regenerating package index and torrentfile")
		RegeneratePackageIndex()
		torrent = GenerateTorrent()
		print("Regeneration terminated")

rthread = threading.Thread(target=RegenerateTimer)
rthread.daemon = False
rthread.start()
print("Regenerating package index every 12 hours")
