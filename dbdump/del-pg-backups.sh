#!/bin/bash
echo "Called: $0 $1 $2 $3 Date: $(date +%Y%m%d%H%M%S)"
echo "pwd: `pwd`"
if [ -z "$1" ]; then
	echo "arg1: $1 is absent..."; exit 1
elif  [ ! -d $1 ]; then
	echo "arg1: $1 is not directory, or directory is not existed..."; exit 2
else
	echo "deleting old pf-db backups files from directory: $1"
	OLD_PWD=$(pwd)
	cd $1
	N=3   # number of backup files to be left in directory
	FILES=$(ls pfdmp-*.out 2>/dev/null)
	NFILES=$(echo $FILES | wc -w)
	if [ $NFILES -eq 0 ]; then
	    echo "No db backups in directory $(pwd)"
	    cd $OLD_PWD
	    exit 3
	fi
	FLIST=$(echo $FILES | sed -e 's/pfdmp-//g; s/.out//g;' | tr ' ' '\n' | sort | tr '\n' ' ')
	echo "Files to be left: $N, Files in directory: $NFILES"
	# echo "FLIST: $FLIST"
	ndiff=$((NFILES-N))
	if [ $ndiff -gt 0 ]
	then
	    cur_pwd=$(pwd)
	    echo "deleting $ndiff old pf-db_ backup_files from directory: $1, pwd: $cur_pwd"
	    i=0
	    for f in $FLIST
	    do
	        if [ $i -lt $ndiff ]
	        then
	            echo -n "file to be deleted: pfdmp-$f.out "
		    rm $cur_pwd/pfdmp-$f.out
		    echo " - done"
	        else
	            break
	        fi
	        i=$((i+1))
	    done
	else
	    echo "Nothing to delete..."
	fi
	cd $OLD_PWD
fi
echo "Finished: $0"
