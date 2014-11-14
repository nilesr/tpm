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
	if not master.TransactionInProgress:
		master.BeginTransaction(False)
	for packagefile in glob.glob(PackagesDirectory+"/*.tpkg"):
		try:
			package = tarfile.open(packagefile,"r:gz")
			PackageInfo = BTEdb.Database(MutableDatabase(package.extractfile(package.getmember("info/package.json")).read().decode("utf-8"))) # Trust me, this probably works
			PackageDatapoint = PackageInfo.Dump("info")[0]
			#print(PackageDatapoint)
			if not master.TableExists(PackageDatapoint["PackageName"]):
				master.Create(PackageDatapoint["PackageName"])
			if not PackageDatapoint["Version"] in master.Dump(PackageDatapoint["PackageName"]):
				master.Insert(PackageDatapoint["PackageName"], [PackageDatapoint["Version"],PackageDatapoint])
		except:
			print(traceback.format_exc())
			continue
	master.CommitTransaction()
	GenerateLatestVersions()
	print(master)
def GenerateLatestVersions():
	if not master.TransactionInProgress:
		master.BeginTransaction(False)
	for package in master.ListTables():
		LatestReleaseEpoch = 0
		for version in master.Dump(package):
			if version["Version"] == "Latest":
				continue
			else:
				if version["ReleaseEpoch"] > LatestReleaseEpoch:
					LatestReleaseEpoch = version["ReleaseEpoch"]
					PackageLatestVersion = version["Version"]
		if len(db.Select(package,Version = "Latest")) == 0:
			db.Insert(package, Version = "Latest", LatestVersion = PackageLatestVersion)
		else:
			db.Update(package, db.Select(package, Version = "Latest"), LatestVersion = PackageLatestVersion)
	master.CommitTransaction()
RegeneratePackageIndex()
