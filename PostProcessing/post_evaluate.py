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

fscene=os.getcwd()
os.chdir('../Utility')
cwd=os.getcwd()
sys.path.append(cwd)
import rtc_util as ut
import tcor_util as tc

os.chdir(fscene)

#----------------------------
#  Initialize
#----------------------------
print "#### Initialize ####"
# parameter input

fold=sys.argv[1]
subf,tdec=fold.split('_')
#depth=float(subf[3:5])/100
nmax=int(subf[6:])
itmax=int(sys.argv[2])
itmax2=int(sys.argv[3])
#dec=float(tdec)/10.0
model=subf[5]
#print 'depth:',depth
#print 'dec:',dec
print 'nmax:',nmax


f=open(fold +'/aparm.txt')
text=f.readlines()
f.close()
    
el=tc.read_parm(text,'el')[0]
az=tc.read_parm(text,'az')[0]
nband=int(tc.read_parm(text,'nband')[0])
offset=tc.read_parm(text,'offset')
gain=tc.read_parm(text,'gain')
nprm=tc.read_parm(text,'nprm')
ut.r_set0=tc.read_parm(text,'ref')[0]
penv=tc.read_parm(text,'penv')

depth=tc.read_parm(text,'depth')[0]
temp=tc.read_parm(text,'wsize')
wsize=[int(x) for x in temp]
dec=tc.read_parm(text,'dec')
twid=tc.read_parm(text,'twid')
temp=filter(lambda x: x.find('class_name')==0,text)[0]
cls_name=temp.split()[1]
temp=filter(lambda x: x.find('function_name')==0,text)[0]
fun_name=temp.split()[1]
#ut.r_set0=float(text[-3][:-1])
#ntau,nhigh,nsang=text[-4].split()
ntau=int(nprm[0])
nhigh=int(nprm[1])
nsang=int(nprm[2])
ut.t_set=np.array(tc.read_parm(text,'tau'))
#ut.t_set=np.arange(int(ntau))*0.2

print cls_name
print fun_name
print ut.r_set0
print ut.t_set
print ntau,nhigh,nsang


#exit()
os.chdir('DATA')

#------------------------------
# DEM Input and INC Calculation
#------------------------------
# dem input and calc inc
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
if fscene.find('OLI')==-1:
  tm1=cv2.imread('sat1.tif',0)
  tm2=cv2.imread('sat2.tif',0)
  tm3=cv2.imread('sat3.tif',0)
  tm_list=[tm1,tm2,tm3]
  num_list=[1,2,3]
else:
  tm1=cv2.imread('band1.tif',-1)
  tm2=cv2.imread('band2.tif',-1)
  tm3=cv2.imread('band3.tif',-1)
  tm4=cv2.imread('band4.tif',-1)
  tm_list=[tm1,tm2,tm3,tm4]
  num_list=[1,2,3,4]

ut.cosb0=np.cos((90.0-el)*np.pi/180)
print ut.cosb0

nterm=15
fname=fun_name[1:]

#------------------------------
#    Main Processing
#------------------------------
#for band in zip([1],[tm1]):
iters=range(itmax)
for (band,tm) in zip(num_list,tm_list):
  print "#### Processing of Band "+str(band)+" ####"
  tmx=gain[band-1]*tm+offset[band-1]
  data=ut.read_data(fname+'_'+str(band)+'.txt',ntau,nhigh,nterm,nsang)
  ut.set_data(data,ntau,nhigh,nsang)
  cls=np.load(cls_name+'.npy')
  os.chdir('..')
  os.chdir(fold)
  tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  tau0=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  eref=penv[0]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  ref0=penv[0]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  for iter in iters:
    print "--- "+str(iter)+ " iteration ---"
    t_ref=np.load('ref'+str(band)+str(iter)+'.npy')
    temp=np.where(t_ref==1.0)
    cls[temp]=-1
    eref=(1.0-dec[iter])*eref+dec[iter]*tc.xmedian(t_ref,wsize[0])
    t_taux=np.load('tau'+str(band)+str(iter)+'.npy')
    temp=np.where(t_taux==1.8)
    cls[temp]=-1
    tau=(1.0-dec[iter])*tau+dec[iter]*tc.ymedian(t_taux,cls,wsize[1],twid[iter])
    temp=np.where(cls==-1)
    print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
    #tau=np.load('tau'+str(band)+str(iter)+'.npy')
    #eref=np.load('eref'+str(band)+str(iter)+'.npy')
    #ref=np.load('ref'+str(band)+str(iter)+'.npy')
    rad=ut.mk_rad(tc.jmax,tc.imax,inc,dem,s_ang,tau,t_ref,eref)
    dif=rad-tmx
    print "* reflectance *"
    print np.max(t_ref),np.min(t_ref),np.mean(t_ref),np.std(t_ref),np.std((t_ref-ref0))
    ref0=t_ref
    print "* optical depth *"
    print np.max(t_taux),np.min(t_taux),np.mean(t_taux),np.std(t_taux),np.std((t_taux-tau0))
    tau0=t_taux
    print "* radiance difference *"
    print np.max(dif),np.min(dif),np.mean(dif),np.std(dif)
    #np.save('rad'+str(band)+str(iter),rad)

  cls=np.load('cls'+str(band)+'.npy')
  iters=range(itmax2)
  dec0=0.2
  for iter in iters:
    print "--- "+str(iter)+ " iteration ---"
    t_ref=np.load('xref'+str(band)+str(iter)+'.npy')
    temp=np.where(t_ref==1.0)
    cls[temp]=-1
    eref=(1.0-dec0)*eref+dec0*tc.xmedian(t_ref,wsize[0])
    t_taux=np.load('xtau'+str(band)+str(iter)+'.npy')
    temp=np.where(t_taux==1.8)
    cls[temp]=-1
    tau=(1.0-dec0)*tau+dec0*tc.ymedian(t_taux,cls,wsize[1],twid[iter])
    temp=np.where(cls==-1)
    print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
    #tau=np.load('tau'+str(band)+str(iter)+'.npy')
    #eref=np.load('eref'+str(band)+str(iter)+'.npy')
    #ref=np.load('ref'+str(band)+str(iter)+'.npy')
    rad=ut.mk_rad(tc.jmax,tc.imax,inc,dem,s_ang,tau,t_ref,eref)
    dif=rad-tmx
    print "* reflectance *"
    print np.max(t_ref),np.min(t_ref),np.mean(t_ref),np.std(t_ref),np.std((t_ref-ref0))
    ref0=t_ref
    print "* optical depth *"
    print np.max(t_taux),np.min(t_taux),np.mean(t_taux),np.std(t_taux),np.std((t_taux-tau0))
    tau0=t_taux
    print "* radiance difference *"
    print np.max(dif),np.min(dif),np.mean(dif),np.std(dif)
    #np.save('rad'+str(band)+str(iter),rad)

  os.chdir('../DATA')
exit()
