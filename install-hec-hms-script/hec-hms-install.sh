#!/usr/bin/env bash

# Installing required 32-bit libraries.
sudo apt -y install libc6:i386
sudo apt -y install libstdc++6:i386
sudo apt -y install libxtst6:i386
sudo apt -y install libxrender1:i386
sudo apt -y install libgcc1:i386
sudo apt -y install libxi6:i386

# Other required libraries.
sudo apt -y install software-properties-common python-software-properties zip unzip wget build-essential net-tools gcc jq
sudo apt -y install xorg openbox

wget 'http://www.hec.usace.army.mil/software/hec-hms/downloads/hec-hms421-linux.tar.gz'
tar -xzf hec-hms421-linux.tar.gz
rm -f hec-hms421-linux.tar.gz

wget 'http://www.hec.usace.army.mil/software/hec-dssvue/downloads/hec-dssvue201-linux.bin.zip'
unzip hec-dssvue201-linux.bin.zip
yes | ./hec-dssvue201.bin
rm -f hec-dssvue201-linux.bin.zip hec-dssvue201.bin

wget 'https://excellmedia.dl.sourceforge.net/project/jython/jython/2.5.0/jython_installer-2.5.0.jar'
./hec-dssvue201/java/bin/java -jar jython_installer-2.5.0.jar -s -d ./jython

cd ./jython
cp -rf Lib lib
zip -r jythonlib.jar lib
cd ../
cp ./jython/jythonlib.jar ./hec-dssvue201/jar/sys
cp ./jython/jython.jar ./hec-dssvue201/jar/sys
rm -f ./jython_installer-2.5.0.jar
rm -rf ./jython

wget 'https://pypi.python.org/packages/fc/b0/847668a90540ad96d88a8adf48d489468fbb6dbb219567b7ed8fd4d9b8b5/simplejson-2.5.0.tar.gz'
tar -xzf simplejson-2.5.0.tar.gz
rm -f simplejson-2.5.0.tar.gz

wget "https://pypi.python.org/packages/f3/e0/8949888568534046c5c847d26c89a05c05f3151ab06728dbeca2d1621002/simplejson-2.5.2.tar.gz#md5=d7a7acf0bd7681bd116b5c981d2f7959"
tar -zxvf simplejson-2.5.2.tar.gz
rm -f simplejson-2.5.2.tar.gz

# Go into <hec-hms Home>/hec-dssvue201/hec-dssvue.sh
# Change the PROG_ROOT to point to the <hec-hms Home>/hec-dssvue201

# Since server does not have a display, add the following before where the hec-dssvue.sh check for DISPLAY
# Server Doesn't have a DISPLAY, thus this logic isn't working. Bypass
# DISPLAY=":0"


# Normally <hec-hms Home>/hec-hms-421/hec-hms.sh's shebang is not correct.
# it appears as #/bin/bash, correct it as #!/bin/bash

# Go into <hec-hms Home>/hec-hms-421/hec-hms.sh
# Change DIR to point to the <hec-hms Home>/hec-hms-421
