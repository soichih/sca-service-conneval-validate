#!/usr/bin/env python

import os
import json
import re
import nibabel

# Things that this script checks
# 
# (for t1)
# * make sure mrinfo runs successfully on specified t1 file
# * make sure t1 is 3d
# * raise warning if t1 transformation matrix isn't unit matrix (identity matrix)
#
# (for dwi)
# * make sure mrinfo runs successfully on specified dwi file
# * make sure dwi is 4d
# * raise warning if dwi transformation matrix isn't unit matrix (identity matrix)
# * make sure bvecs and bvals can be read
# * make sure bvecs's cols count matches dwi's 4th dimension number
# * make sure bvecs has 3 rows
# * make sure bvals's cols count matches dwi's 4th dimension number
# * make sure bvals has 1 row

#display where this is running
import socket
print(socket.gethostname())

with open('config.json') as config_json:
    config = json.load(config_json)

results = {"errors": [], "warnings": []}
directions = None

def check_affine(affine):
    if affine[0][1] != 0: results['warnings'].append("affine matrix 0.1 is non 0")
    if affine[0][2] != 0: results['warnings'].append("affine matrix 0.2 is non 0")
    if affine[1][0] != 0: results['warnings'].append("affine matrix 1.0 is non 0")
    if affine[1][2] != 0: results['warnings'].append("affine matrix 1.2 is non 0")
    if affine[2][0] != 0: results['warnings'].append("affine matrix 2.0 is non 0")
    if affine[2][1] != 0: results['warnings'].append("affine matrix 2.1 is non 0")
    if affine[3][0] != 0: results['warnings'].append("affine matrix 3.0 is non 0")
    if affine[3][1] != 0: results['warnings'].append("affine matrix 3.1 is non 0")
    if affine[3][2] != 0: results['warnings'].append("affine matrix 3.2 is non 0")
    if affine[3][3] != 1: results['warnings'].append("affine matrix 3.3 is non 1")

if 't1' in config:
    if config['t1'] is None:
        results['errors'].append("t1 not set")
    else:
        print("checking t1")
        try: 
            img = nibabel.load(config['t1'])
            results['t1_headers'] = str(img.header)
            results['t1_base_affine'] = str(img.header.get_base_affine())

            #check dimentions
            if img.header['dim'][0] != 3:
                results['errors'].append("T1 should be 3D but has "+img.header['dim'][0])

            check_affine(img.header.get_base_affine())

        except Exception as e:
            results['errors'].append(str(e))

if 'dwi' in config:
    #check dwi
    if config['dwi'] is None: 
        results['errors'].append("dwi not set")
    else:
        directions = None

        print("checking dwi")
        try: 
            img = nibabel.load(config['dwi'])
            results['dwi_headers'] = str(img.header)
            results['dwi_base_affine'] = str(img.header.get_base_affine())

            #check dimentions
            if img.header['dim'][0] != 4:
                results['errors'].append("DWI should be 4D but has "+img.header['dim'][0])

            #check 4d size
            directions = img.header['dim'][4]
            if directions < 10:
                results['warnings'].append("DWI's 4D is too small "+str(directions))

            #check affine
            check_affine(img.header.get_base_affine())

        except Exception as e:
            results['errors'].append(str(e))

        print("checking bvecs")
        if config['bvecs'] is None: 
            results['errors'].append("bvecs not set")
        else:
            try: 
                bvecs = open(config['bvecs'])
                bvecs_rows = bvecs.readlines()
                bvecs_cols = bvecs_rows[0].strip().replace(",", " ")

                #remove double spaces
                bvecs_cols_clean = re.sub(' +', ' ', bvecs_cols) 
                bvecs_cols = bvecs_cols_clean.split(' ')		

                #bvecs should have same col num as directions
                if directions != len(bvecs_cols):
                    results['errors'].append("bvecs column count which is "+str(len(bvecs_cols))+" doesn't match dwi's 4d number:"+str(directions))

                #bvecs should ahve 3 row
                if len(bvecs_rows) != 3:
                    results['errors'].append("bvecs should have 3 rows but it has "+str(len(bvecs_rows)))

            except IOError:
                print "failed to load bvecs:"+config['bvecs']
                results['errors'].append("Couldn't read bvecs")

        print("checking bvals")
        if config['bvals'] is None: 
            results['errors'].append("bvals not set")
        else:
            try: 
                bvals = open(config['bvals'])
                bvals_rows = bvals.readlines()
                bvals_cols = bvals_rows[0].strip().replace(",", " ")

                #remove double spaces
                bvals_cols_clean = re.sub(' +', ' ', bvals_cols) 
                bvals_cols = bvals_cols_clean.split(" ") 

                if directions != len(bvals_cols):
                    results['errors'].append("bvals column count which is "+str(len(bvals_cols))+" doesn't match dwi's 4d number:"+str(directions))

                if  len(bvals_rows) != 1:
                    results['errors'].append("bvals should have 1 row but it has "+str(len(bvals_rows)))

            except IOError:
                print "failed to load bvals:"+config['bvals']
                results['errors'].append("Couldn't read bvals")


#debug..
print results

with open("product.json", "w") as fp:
    json.dump({"type": "conneval-validation-result", "results": results}, fp)



