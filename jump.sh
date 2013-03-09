#!/bin/bash

# jump
# Makes your `cd`ing lightning fast.
#
# @author: Hamish Macpherson
# @url: https://github.com/hamstu/jump
#
# See README.md for installation and usage.

rm ~/.jumpfile 2> /dev/null   # 1: Prune old .jumpfile
touch ~/.jumpfile             # 2: Ensure it's there now, but empty
jump.py $1                    # 3: Call our jump program (it outputs to the .jumpfile)
newdir=`cat ~/.jumpfile`      # 4: Get the output of our .jumpfile into a variable

if [[ X"" != X"$newdir" ]]    # 5: Jump if it's a non-empty string
  then cd `echo $newdir`;echo $newdir
fi