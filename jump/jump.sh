#!/bin/bash

######################################################
#
# jump
# Makes your `cd`ing lightning fast.
#
# @author: Hamish Macpherson
# @url: https://github.com/hamstu/jump
#
# See README.md for installation and usage.
#
######################################################

echo '' > ~/.jumpfile         # 1: Clear/prepare the jumpfile
jump.py $1                    # 2: Call our jump program (it outputs to the .jumpfile)
newdir=`cat ~/.jumpfile`      # 3: Get the output of our .jumpfile into a variable

if [[ X"" != X"$newdir" ]]    # 4: Jump if it's a non-empty string
  then cd `echo $newdir`;echo $newdir
fi
