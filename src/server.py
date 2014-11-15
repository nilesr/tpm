#!/usr/bin/env python3
# Server
import glob, BTEdb, os, tarfile, traceback, mimetypes, wsgiref.simple_server

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
				master.Insert(PackageDatapoint["PackageName"], Filename = os.path.basename(packagefile) , *x) # Gets the filename and also appends all the elements of x to the end of the methodcall
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
	return [st.encode("utf-8")]
def serve(environ, start_response):
	if environ["PATH_INFO"] == "/":
		start_response("200 OK",  [('Content-type','text/html')])
		return fix_for_wsgiref("""<!doctype html><html><head><meta http-equiv="refresh" content="0;URL='/index.html'" /></head><body>Loading...</body></html>""")
	if environ["PATH_INFO"].lower()[-len("torrent")] == "torrent":
		start_response("200 OK", [('Content-type','application/x-bittorrent')])
		return fix_for_wsgiref("") # TODO
	if environ["PATH_INFO"].lower() == "package-index.json":
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
		return fix_for_wsgiref("""<!doctype html><html><head><title>TPM Package Repository</title></head><body><h1>404 Not Found</h1></body></html>""")

RegeneratePackageIndex()

mimetypes.init()

server = wsgiref.simple_server.make_server("",5001,serve)
server.serve_forever()
