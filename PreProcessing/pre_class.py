#!/usr/bin/env python
# coding:utf-8
# cd /Volumes/Transcend/SCAN_PROGRAM3
# python PROGRAM/tcor_class.py SceneName Number Type Weight
#	SceneName: ETM02063010832,...
#	Number: number of class, 320, 640, 1280
#	Type: I,J,K,V, ...
#		I: band 7 for ETM+, band 4 for AVNIR2
#		J: jaxa class
#		K: jaxa class with unique number for water zone
#	Weight: weight for third component 10,20,...

import os
import sys
import cv2
import numpy as np

os.chdir('Utility')
cwd=os.getcwd()
sys.path.append(cwd)
import tcor_util as tc
os.chdir('..')

fscene=sys.argv[1]
os.chdir(fscene)

#----------------------------
#  class name and setting
#----------------------------
nmax=int(sys.argv[2])
type=sys.argv[3]
weight=int(sys.argv[4])

#nmax=640
#weight=10

cls_name='cls'+str(nmax)+type+'_'+str(weight)
print cls_name

f=open('aparm.txt')
text=f.readlines()
f.close()
    
el=tc.read_parm(text,'el')[0]
az=tc.read_parm(text,'az')[0]

#------------------------------
# DEM Input and INC Calculation
#------------------------------
# dem input and calc inc
os.chdir('DATA')
dem=cv2.imread('dem.tif',-1)
#dem=tc.read_tif('dem.tif')
tc.jmax,tc.imax=dem.shape
inc=tc.incident(dem,el,az,30.0,30.0)
slp=tc.slope(dem,30.0,30.0)

print np.mean(inc),np.std(inc)
print np.mean(slp),np.std(slp)
#incx=tc.display0(inc,600,600,0.0,1.0)
#cv2.imshow('inc',incx)
#slpx=tc.display0(slp,600,600,0.0,1.0)
#cv2.imshow('slp',slpx)

#---------------------------------
# SAT Image Input
#-------------------------------
if fscene.find('ETM')!=-1 : tm=cv2.imread('sat7.tif',0)
if fscene.find('AVN')!=-1 : tm=cv2.imread('sat4.tif',0)
if fscene.find('OLI')!=-1 : tm=cv2.imread('sat9.tif',0)


jaxa=cv2.imread('jaxa.tif',0)
print np.mean(jaxa),np.std(jaxa)
#jaxax=tc.display0(jaxa,600,600,0.0,10.0)
#cv2.imshow('jaxa',jaxax)

if type=='J':
    cls=tc.mclass(256*inc,256*slp,weight*jaxa,nmax)

# for unfying water region after k-means clustering
if type=='K':
    cls=tc.mclass(256*inc,256*slp,weight*jaxa,nmax)
    nmax2=np.max(cls)
    cls[np.where(jaxa==1)]=nmax2+1

if type=='I':
    cls=tc.mclass(256*inc,256*slp,weight*tm,nmax)

print np.min(cls),np.max(cls)

np.save(cls_name,cls)

#clsx=tc.display0(1.0*cls,600,600,0,np.max(cls))
#cv2.imshow('cls2',clsx)
#cv2.destroyAllWindows()


exit()


