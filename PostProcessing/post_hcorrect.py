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
tmax=float(sys.argv[2])
print fold,tmax

dem=cv2.imread('DATA/dem.tif',-1)/1000.0
tc.jmax,tc.imax=dem.shape
imax=tc.imax/2; jmax=tc.jmax/2

#fold="MAR60P640"
#pwd
os.chdir(fold)

tm1=np.load('tau1y'+'.npy')
tm2=np.load('tau2y'+'.npy')
tm3=np.load('tau3y'+'.npy')
tm1=tc.hcor(tm1,dem,2.0)
tm2=tc.hcor(tm2,dem,2.0)
tm3=tc.hcor(tm3,dem,2.0)

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
cv2.imwrite('../'+fold+'_tau321z.png',csat)
exit()

