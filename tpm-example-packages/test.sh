#!/bin/bash
rm *.tpkg /var/tpm-mirror/packages/*
for i in *; do
	echo $i
	test "$i" == "test.sh" && continue
	cd $i
	tar czf ../$i.tpkg *
	cd ..
done
mv *.tpkg /var/tpm-mirror/packages
