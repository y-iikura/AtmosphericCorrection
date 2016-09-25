#cd /Users/iikura/Desktop/NEW_PROGRAM
#pyenv local anaconda-2.4.0
#cd /Users/iikura/Desktop/NEW_PROGRAM
#ipython

import numpy as np
import os
import cv2
import sys

fscene=os.getcwd()
os.chdir('../Utility')
cwd=os.getcwd()
sys.path.append(cwd)
import tcor_util as tc
os.chdir(fscene)

fold=sys.argv[1]
num=sys.argv[2]
tmax=float(sys.argv[3])
print fold,num,tmax

f=open(fold +'/aparm.txt')
text=f.readlines()
f.close()
temp=filter(lambda x: x.find('function_name')==0,text)[0]
fun_name=temp.split()[1]
mtau=float(fun_name[4:])/10.0
print fun_name,mtau

#exit()
dem=cv2.imread('DATA/dem.tif',-1)/1000.0
dem[dem < 0.0]=0.0
tc.jmax,tc.imax=dem.shape
imax=tc.imax/2; jmax=tc.jmax/2

#fold="MAR60P640"
#pwd
os.chdir(fold)

if fscene.find('OLI') ==-1:
  tm1=np.load('xtau1'+num+'.npy')
  tm2=np.load('xtau2'+num+'.npy')
  tm3=np.load('xtau3'+num+'.npy')
else:
  tm1=np.load('xtau2'+num+'.npy')
  tm2=np.load('xtau3'+num+'.npy')
  tm3=np.load('xtau4'+num+'.npy')

tm1=tc.hcor(tm1,dem,mtau)
tm2=tc.hcor(tm2,dem,mtau)
tm3=tc.hcor(tm3,dem,mtau)

tc.jmax,tc.imax=tm1.shape
imax=tc.imax/2; jmax=tc.jmax/2

rc1=tc.percent(tm1,0.01,0.98); print rc1 
rc2=tc.percent(tm2,0.01,0.98); print rc2
rc3=tc.percent(tm3,0.01,0.98); print rc3
csat=np.zeros((jmax,imax,3),np.uint8)
#csat[:,:,0]=tc.display0(tm1,imax,jmax,rc1[0],rc1[1])
#csat[:,:,1]=tc.display0(tm2,imax,jmax,rc2[0],rc2[1])
#csat[:,:,2]=tc.display0(tm3,imax,jmax,rc3[0],rc3[1])
csat[:,:,0]=tc.display0(tm1,imax,jmax,0.0,tmax)
csat[:,:,1]=tc.display0(tm2,imax,jmax,0.0,tmax)
csat[:,:,2]=tc.display0(tm3,imax,jmax,0.0,tmax)
#cv2.imshow('tau',csat)
#cv2.destroyWindow('tau')

if fscene.find('OLI') ==-1:
  cv2.imwrite('../'+fold+'_tau321z.png',csat)
else:
  cv2.imwrite('../'+fold+'_tau432z.png',csat)

exit()

