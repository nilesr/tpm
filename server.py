#!/usr/bin/env python3
# Server
import glob, BTEdb, os, tarfile, traceback
MasterDirectory="/var/tpm-mirror"
PackagesDirectory=MasterDirectory+"/packages"
if not os.path.isdir(MasterDirectory):
	os.mkdir(MasterDirectory)
if not os.path.isdir(PackagesDirectory):
	os.mkdir(PackagesDirectory)
master = BTEdb.Database(MasterDirectory+"/package-index.json")
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
def RegeneratePackageIndex():
	for packagefile in glob.glob(PackagesDirectory+"/*.tpkg"):
		try:
			package = tarfile.open(packagefile,"r:gz")
			#packageInfo = BTEdb.Database(MutableDatabase(package.extractfile(package.getmember("info/package.json"))))
			packageInfo = BTEdb.Database(MutableDatabase(package.extractfile(package.getmember("info/package.json")).read().decode("utf-8")))
			print(packageInfo.ListTables())
		except:
			print(traceback.format_exc())
			continue
RegeneratePackageIndex()
