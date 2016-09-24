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
    
el=tc.read_parm(text,'el')[0]
az=tc.read_parm(text,'az')[0]
smin=np.floor(tc.read_parm(text,'min')[0])
smax=np.ceil(tc.read_parm(text,'max')[0])
nband=int(tc.read_parm(text,'nband')[0])
offset=tc.read_parm(text,'offset')
gain=tc.read_parm(text,'gain')
#number=tc.read_parm(text,'number')
tau=tc.read_parm(text,'tau')
height=tc.read_parm(text,'height')
nprm=[int(data) for data in tc.read_parm(text,'nprm')]

#print number
print tau
print height
print int(smin),int(smax)

#------------------------------
# DEM Input and INC Calculation
#------------------------------
# dem input and calc inc
os.chdir('DATA')
dem=cv2.imread('dem.tif',-1)
dem[dem < 0.0]=0.0
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
if fold.find('ETM')==0:
  tm1=cv2.imread('sat1.tif',0)
  tm2=cv2.imread('sat2.tif',0)
  tm3=cv2.imread('sat3.tif',0)
  tm4=cv2.imread('sat4.tif',0)
  tm5=cv2.imread('sat5.tif',0)
  tm7=cv2.imread('sat7.tif',0)
  tm_list=[tm1,tm2,tm3,tm4,tm5,tm7]
  num_list=[1,2,3,4,5,6]
else:
  tm1=cv2.imread('band1.tif',-1)
  tm2=cv2.imread('band2.tif',-1)
  tm3=cv2.imread('band3.tif',-1)
  tm4=cv2.imread('band4.tif',-1)
  tm_list=[tm1,tm2,tm3,tm4]
  num_list=[1,2,3,4]

ntau=len(tau)
nhigh=len(height)
nsang=int(smax-smin)+1
print ntau,nhigh,nsang
print nprm
#print text[-1]
#temp=lines[n_line-4].split()[2]
#ut.r_set0=float(temp)
ut.cosb0=np.cos((90.0-el)*np.pi/180)
print ut.cosb0

nterm=15

#exit()
#tm_list=[tm1]
#num_list=[1]
### Start Making Function List
for (band,tm) in zip(num_list,tm_list):
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

