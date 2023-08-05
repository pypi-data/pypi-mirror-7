#!/bin/bash

# This script will build your TASTE system.

# You should check it before running it to make it fit with your context:
# 1) You may need to fix some paths and filenames (path to interface/deployment views)
# 2) You may need to specify additional paths for the compiler to find .h file
#    (e.g. "export C_INCLUDE_PATH=/usr/include/xenomai/analogy/:$C_INCLUDE_PATH")
# 3) You may need to link with pre-built libraries, using the -l option
#    (e.g. -l /usr/lib/libanalogy.a,/usr/lib/librtdm.a)
# 4) You may need to change the runtime (add -p flag to select PolyORB-HI-C)
# etc.

# Note: TASTE will not overwrite your changes - if you need to update some parts
#       you will have to merge the changes with the newly-created file.

if [ -z "$DEPLOYMENTVIEW" ]
then
    DEPLOYMENTVIEW=DeploymentView.aadl
fi

SKELS="./"

cd "$SKELS"
rm -f orchestrator.zip
zip orchestrator orchestrator/*
rm -f passivefunction.zip
zip passivefunction passivefunction/*
cd "$OLDPWD"

[ ! -z "$CLEANUP" ] && rm -rf binary

echo 'Building the system with the Ada runtime (add -p in the build script to replace with C)'
assert-builder-ocarina.py \
	--fast \
	--debug \
	--aadlv2 \
	--keep-case \
	--interfaceView InterfaceView.aadl \
	--deploymentView "$DEPLOYMENTVIEW" \
	-o binary \
	--subAda orchestrator:"$SKELS"/orchestrator.zip \
	--subC passivefunction:"$SKELS"/passivefunction.zip \
	$ORCHESTRATOR_OPTIONS
