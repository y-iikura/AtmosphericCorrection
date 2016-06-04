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

#fold="TAU20M640_3"
#pushd TAU25
#pwd
os.chdir(fold)
tm1=np.load('ref1'+num+'.npy')
tc.jmax,tc.imax=tm1.shape
imax=tc.imax/2; jmax=tc.jmax/2
tm2=np.load('ref2'+num+'.npy')
tm3=np.load('ref3'+num+'.npy')
rc1=tc.percent(tm1,0.02,0.98); print rc1
rc2=tc.percent(tm2,0.02,0.98); print rc2
rc3=tc.percent(tm3,0.02,0.98); print rc3
csat=np.zeros((jmax,imax,3),np.uint8)
csat[:,:,0]=tc.display0(tm1,imax,jmax,rc1[0],rc1[1])
csat[:,:,1]=tc.display0(tm2,imax,jmax,rc2[0],rc2[1])
csat[:,:,2]=tc.display0(tm3,imax,jmax,rc3[0],rc3[1])
#csat[:,:,0]=tc.display0(tm1,imax,jmax,0.0,rc1[1])
#csat[:,:,1]=tc.display0(tm2,imax,jmax,0.0,rc2[1])
#csat[:,:,2]=tc.display0(tm3,imax,jmax,0.0,rc3[1])
#cv2.imshow('ref',csat)
#cv2.destroyWindow('ref')
cv2.imwrite('../'+fold+'_ref321x.png',csat)

tm1=np.load('tau1'+num+'.npy')
tm2=np.load('tau2'+num+'.npy')
tm3=np.load('tau3'+num+'.npy')
rc1=tc.percent(tm1,0.05,0.98); print rc1 
rc2=tc.percent(tm2,0.05,0.98); print rc2
rc3=tc.percent(tm3,0.05,0.98); print rc3
csat[:,:,0]=tc.display0(tm1,imax,jmax,0.0,tmax)
csat[:,:,1]=tc.display0(tm2,imax,jmax,0.0,tmax)
csat[:,:,2]=tc.display0(tm3,imax,jmax,0.0,tmax)
#cv2.imshow('tau',csat)
#cv2.destroyWindow('tau')
cv2.imwrite('../'+fold+'_tau321x.png',csat)
exit()
