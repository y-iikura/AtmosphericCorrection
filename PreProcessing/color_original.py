#!/usr/bin/env python
# coding:utf-8
# cd /Volumes/Transcend/SCAN_PROGRAM2
# python PROGRAM/color_original.py SceneFolderName

import numpy as np
import os
import cv2
import sys

os.chdir('Utility')
cwd=os.getcwd()
sys.path.append(cwd)
import tcor_util as tc
os.chdir('..')
fold=sys.argv[1]
print "* Target folder : "+fold
os.chdir(fold+'/DATA')
if fold.find('OLI') == -1:
  tm1=cv2.imread('sat1.tif',0)
  tc.jmax,tc.imax=tm1.shape
  tm2=cv2.imread('sat2.tif',0)
  tm3=cv2.imread('sat3.tif',0)
else:
  tm1=cv2.imread('band2.tif',0)
  tc.jmax,tc.imax=tm1.shape
  tm2=cv2.imread('band3.tif',0)
  tm3=cv2.imread('band4.tif',0)

imax=tc.imax/2; jmax=tc.jmax/2

rc1=tc.percent(tm1,0.05,0.98); print rc1
rc2=tc.percent(tm2,0.05,0.98); print rc2
rc3=tc.percent(tm3,0.05,0.98); print rc3
csat=np.zeros((jmax,imax,3),np.uint8)
csat[:,:,0]=tc.display0(tm1,imax,jmax,rc1[0],rc1[1])
csat[:,:,1]=tc.display0(tm2,imax,jmax,rc2[0],rc2[1])
csat[:,:,2]=tc.display0(tm3,imax,jmax,rc3[0],rc3[1])
#cv2.imshow('ref',csat)

if fold.find('OLI') == -1:
  cv2.imwrite('../tm321.png',csat)
else:
  cv2.imwrite('../oli432.png',csat)


if fold.find('AVN')!=-1 : exit()

if fold.find('OLI') == -1:
  tm4=cv2.imread('sat4.tif',0)
  tm5=cv2.imread('sat5.tif',0)
  tm7=cv2.imread('sat7.tif',0)
else:
  tm4=cv2.imread('band5.tif',0)
  tm5=cv2.imread('band6.tif',0)
  tm7=cv2.imread('band7.tif',0)

rc4=tc.percent(tm4,0.05,0.98); print rc4
rc5=tc.percent(tm5,0.05,0.98); print rc5
rc7=tc.percent(tm7,0.05,0.98); print rc7
csat2=np.zeros((jmax,imax,3),np.uint8)
csat2[:,:,0]=tc.display0(tm7,imax,jmax,rc7[0],rc7[1])
csat2[:,:,1]=tc.display0(tm5,imax,jmax,rc5[0],rc5[1])
csat2[:,:,2]=tc.display0(tm4,imax,jmax,rc4[0],rc4[1])
#cv2.imshow('ref2',csat2)

if fold.find('OLI') == -1:
  cv2.imwrite('../tm457.png',csat2)
else:
  cv2.imwrite('../oli567.png',csat2)

#cv2.destroyWindow('ref')

exit()

