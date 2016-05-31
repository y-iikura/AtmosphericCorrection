#!/usr/bin/env python
# coding:utf-8
# cd /Volumes/Transcend/SCAN_PROGRAM2
# python PROGRAM/tcor_function.py FoderName ParameterFile
#       FolderName: ETM02063010832,...
#	ParameterFile: Mar20, Con00, ...

import os
import os.path as path
import sys
import cv2
import numpy as np

os.chdir('Utility')
cwd=os.getcwd()
sys.path.append(cwd)
import rtc_util as ut
import tcor_util as tc
os.chdir('..')
fold=sys.argv[1]
os.chdir(fold)

#----------------------------
#  Initialize
#----------------------------
print "#### Initialize ####"
# parameter input

fname=sys.argv[2]

f=open('aparm.txt')
text=f.readlines()
f.close()
    
el=tc.read_parm(text,'el',1)[0]
az=tc.read_parm(text,'az',1)[0]
nband=int(tc.read_parm(text,'nband',1)[0])
offset=tc.read_parm(text,'offset',nband)
gain=tc.read_parm(text,'gain',nband)


#------------------------------
# DEM Input and INC Calculation
#------------------------------
# dem input and calc inc
os.chdir('DATA')
dem=cv2.imread('dem.tif',-1)
#dem=tc.read_tif(fold+'/'+'dem.tif')
tc.jmax,tc.imax=dem.shape
inc=tc.incident(dem,el,az,30.0,30.0)
slp=tc.slope(dem,30.0,30.0)
s_ang=np.load('sangle.npy')
#veg=np.ones(tc.imax*tc.jmax,dtype=np.uint16).reshape(tc.jmax,tc.imax)

#---------------------------------
# SAT Image Input
#-------------------------------
#tm1=tc.read_tif('sat1.tif')
#tm2=tc.read_tif('sat2.tif')
#tm3=tc.read_tif('sat3.tif')
tm1=cv2.imread('sat1.tif',0)
tm2=cv2.imread('sat2.tif',0)
tm3=cv2.imread('sat3.tif',0)


f=open(fname+'_1.txt')
lines=f.readlines()
f.close()
n_line=len(lines)
temp=lines[n_line-5].split()[1:4]
print temp
ntau=int(temp[0])+1
nhigh=int(temp[1])+1
nsang=int(temp[2])+1
print ntau,nhigh,nsang
#temp=lines[n_line-4].split()[2]
#ut.r_set0=float(temp)
ut.cosb0=np.cos((90.0-el)*np.pi/180)
print ut.cosb0

nterm=15

### Start Making Function List
#for (band,tm) in zip([3],[tm3]):
for (band,tm) in zip([1,2,3],[tm1,tm2,tm3]):
  print "#### Processing of Band "+str(band)+" ####"
  data=ut.read_data(fname+'_'+str(band)+'.txt',ntau,nhigh,nterm,nsang)
  ut.set_data(data,ntau,nhigh,nsang)
  # initial data
  tmx=gain[band-1]*tm+offset[band-1]
  #print "--- function list ---"
  t=cv2.getTickCount() 
  f_list=ut.mk_list(tc.jmax,tc.imax,tmx,inc,dem,s_ang)
  print (cv2.getTickCount()-t)/cv2.getTickFrequency()
  np.save('f'+fname+'_'+str(band),f_list)


exit()
'''

exit()
'''
