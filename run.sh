#!/bin/bash

#make sure jq is installed on $SCA_SERVICE_DIR
if [ ! -f $SCA_SERVICE_DIR/jq ];
then
        echo "installing jq"
        wget https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 -O $SCA_SERVICE_DIR/jq
        chmod +x $SCA_SERVICE_DIR/jq
fi

#allows local test execution
if [ -z $SCA_SERVICE_DIR ]; then
    export SCA_SERVICE_DIR=`pwd`
fi

#pull params
t1=`$SCA_SERVICE_DIR/jq -r '.t1' config.json`
dwi=`$SCA_SERVICE_DIR/jq -r '.dwi' config.json`
bvecs=`$SCA_SERVICE_DIR/jq -r '.bvecs' config.json`
bvals=`$SCA_SERVICE_DIR/jq -r '.bvals' config.json`

module load mrtrix

#todo
mrinfo $dwi
mrinfo $t1
bvecs_cols=`cat $bvecs | head -1 | wc -w`
bvecs_rows=`cat $bvecs | wc -l`
bvals_cols=`cat $bvals | head -1 | wc -w`
bvals_rows=`cat $bvals | wc -l`
echo $bvecs_cols
echo $bvecs_rows
echo $bvals_cols
echo $bvals_rows

echo "[]" > products.json
