#!/bin/sh
# shell script used to copy netana examples to the
# users home directory "netana-examples"

userdir="/home/$(whoami)/netana-examples"
srcdir="netana/examples"

if [ ! -d "$srcdir" ]
then
	echo "Can't locate \"netana/examples\" directory!"
	exit 1
fi

if [ ! -d "$userdir" ]
then
	mkdir $userdir
	if [ -d "$userdir" ]
	then
		echo "Created $userdir directory."
	else
		echo "Could not create $userdir "
		exit 1
	fi
fi

echo "Copying example files to $userdir "
cp $srcdir/* $userdir/

exit 0




