#!/bin/bash

absscript=`readlink -f $0`
myfolder=`dirname $absscript`
echo Script launch in folder $myfolder

script=$myfolder/changeparamorder.pl
tempf=.__temp~
rm -f $tempf

files=`grep -e "$1\s*(" -lr .`
for file in $files; do
	echo $file
	cat $file | $script $@ > $tempf
	state=$?
	if [ $state != '0' ]; then
		echo $script quited with error state: $state
		break
	fi
	less $tempf
	echo -n "Is That OK? (Y/n/q): "
	read yesorno
	if [ -z $yesorno ]; then
		yesorno=y
	fi
	if [ $yesorno = 'n' ]; then
		echo "Abort Operation"
	elif [ $yesorno = 'q' ]; then
		break	
	else
		echo "Make it happen"
		cp -f $tempf $file
	fi
done

rm -f $tempf
