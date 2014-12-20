#!/bin/bash
rm *.tpkg
for i in *; do
	echo $i
	test "$i" == "test.sh" && continue
	cd $i
	tar czf ../$i.tpkg *
	cd ..
done
cp *.tpkg /var/tpm-mirror/packages
