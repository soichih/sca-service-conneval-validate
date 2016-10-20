#!/bin/env python

import os
import json
import re
import subprocess

# Things that this script checks
# 
# * make sure mrinfo runs successfully on specified dwi file
# * make sure dwi is 4d
# * raise warning if dwi transformation matrix isn't unit matrix (identity matrix)
#
# * make sure mrinfo runs successfully on specified t1 file
# * make sure t1 is 3d
# * raise warning if t1 transformation matrix isn't unit matrix (identity matrix)
#
# * make sure bvecs and bvals can be read
# * make sure bvecs's cols count matches dwi's 4th dimension number
# * make sure bvecs has 3 rows
# * make sure bvals's cols count matches dwi's 4th dimension number
# * make sure bvals has 1 row

with open('config.json') as config_json:
    config = json.load(config_json)

results = {"errors": [], "warnings": []}

#parse dwi mrinfo
try: 
    #print("module load mrtrix && mrinfo "+config['dwi'])
    info = subprocess.check_output("module load mrtrix && mrinfo "+config['dwi'], shell=True)
    results['dwi_mrinfo'] = info
    info_lines = info.split("\n")
    #print info_lines

    #check dimentions
    dim=info_lines[3]
    dims=dim.split("x")
    if len(dims) != 4:
        results['errors'].append("DWI file specified doesn't have 4 dimentions")
    directions = int(dims[3])
    if directions < 10: 
        results['errors'].append("DWI's 4D seems too small",directions)

    #check transform
    tl = info_lines[9:12]
    tl[0] = tl[0][12:] #remove "Transform:"
    m = []
    for line in tl:
        line = line.strip()
        strs = re.split('\s+', line)
        ml = []
        for s in strs:
            ml.append(int(s))   
        m.append(ml)

    if m[0][0] == 1 and m[0][1] == 0 and m[0][1] == 0 and m[0][0] == 1 and m[0][1] == 0 and m[0][1] == 0 and m[0][0] == 1 and m[0][1] == 0 and m[0][1] == 0:  
        None #good
    else:
        results['warnings'].append("DWI has non-optimal transformation matrix. It should be 1 0 0 / 0 1 0 / 0 0 1")
    
except subprocess.CalledProcessError as err:
    results['errors'].append("mrinfo failed on dwi. error code: "+err.returncode)

#parse t1 mrinfo
try: 
    info = subprocess.check_output("module load mrtrix && mrinfo "+config['t1'], shell=True)
    results['t1_mrinfo'] = info
    info_lines = info.split("\n")
    #print info_lines

    #check dimentions
    dim=info_lines[3]
    dims=dim.split("x")
    if len(dims) != 3:
        results['errors'].append("T1 should be 3D")

    #check transform
    tl = info_lines[9:12]
    tl[0] = tl[0][12:] #remove "Transform:"
    m = []
    for line in tl:
        line = line.strip()
        strs = re.split('\s+', line)
        ml = []
        for s in strs:
            ml.append(int(s))   
        m.append(ml)

    if m[0][0] == 1 and m[0][1] == 0 and m[0][1] == 0 and m[0][0] == 1 and m[0][1] == 0 and m[0][1] == 0 and m[0][0] == 1 and m[0][1] == 0 and m[0][1] == 0:  
        None #good
    else:
        results['warnings'].append("T1 has non-optimal transformation matrix. It should be 1 0 0 / 0 1 0 / 0 0 1")
    
except subprocess.CalledProcessError as err:
    results['errors'].append("mrinfo failed on t1. error code: "+err.returncode)

#check bvecs and bvals
try: 
    bvecs = open(config['bvecs'])
    bvecs_rows = bvecs.readlines()
    bvecs_cols = bvecs_rows[0].split(" ") 
except IOError:
    results['errors'].append("Couldn't read bvecs")
try: 
    bvals = open(config['bvals'])
    bvals_rows = bvals.readlines()
    bvals_cols = bvals_rows[0].split(" ") 
except IOError:
    results['errors'].append("Couldn't read bvals")

if directions != len(bvecs_cols):
    results['errors'].append("bvecs column count doesn't match dwi's 4d number",directions)
if directions != len(bvals_cols):
    results['errors'].append("bvals column count doesn't match dwi's 4d number",directions)
if  len(bvecs_rows) != 3:
    results['errors'].append("bvecs should have 3 rows but it has "+str(len(bvecs_rows)))
if  len(bvals_rows) != 1:
    results['errors'].append("bvals should have 1 row but it has "+str(len(bvals_rows)))

with open("products.json", "w") as fp:
    json.dump([{"type": "conneval-validation-result", "results": results}], fp)

