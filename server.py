# Server
import glob, BTEdb
MasterDirectory="/var/tpm-mirror"
PackagesDirectory=MasterDirectory+"/packages"
assert os.mkdir(MasterDirectory) and os.mkdir(PackagesDirectory)
master = BTEdb.Database(MasterDirectory+"/package-index.json")
def RegeneratePackageIndex():
	for packagefile in glob.glob(PackagesDirectory+"/*.tpkg"):
		try:
			package = tarfile.open(packagefile,"r:gz")
			packageInfo = tarfile.getmember("info/package.json").tobuf()
			print packageInfo
		except:
			continue