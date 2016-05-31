# cd /Volumes/Transcend/SCAN_PROGRAM3
# python

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
depth=float(subf[3:5])/100
nmax=int(subf[6:])
itmax=int(sys.argv[2])
dec=float(tdec)/10.0
model=subf[5]
print 'depth:',depth
print 'dec:',dec
print 'nmax:',nmax


f=open(fold +'/aparm.txt')
text=f.readlines()
f.close()
    
el=tc.read_parm(text,'el',1)[0]
az=tc.read_parm(text,'az',1)[0]
nband=int(tc.read_parm(text,'nband',1)[0])
offset=tc.read_parm(text,'offset',nband)
gain=tc.read_parm(text,'gain',nband)
penv=tc.read_parm(text,'penv',3)
depth=tc.read_parm(text,'depth',1)[0]
wsize=tc.read_parm(text,'wsize',2)
wsize=[int(x) for x in wsize]
dec=tc.read_parm(text,'dec',1)[0]
twid=tc.read_parm(text,'twid',15)
cls_name=text[-1][:-1]
fun_name=text[-2][:-1]
ut.r_set0=float(text[-3][:-1])
ntau,nhigh,nsang=text[-4].split()
ut.t_set=np.arange(int(ntau))*0.2

print cls_name
print fun_name
print ut.r_set0
print ut.t_set
os.chdir('DATA')


#------------------------------
#    Main Processing
#------------------------------
for band in [1,2,3]:
  print "#### Processing of Band"+str(band)+" ####"
  ut.cosb0=np.cos((90.0-el)*np.pi/180); ut.cosb0
  print "--- function list ---"
  f_list=np.load(fun_name+'_'+str(band)+'.npy')
  cls=np.load(cls_name+'.npy')
  tc.jmax,tc.imax=cls.shape
  os.chdir('../'+fold)
  temp=[x for x in os.listdir('.') if x.find('cls'+str(band))==0]
  m=len(temp)
  if m == 0 :
    tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
    eref=penv[0]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
    iters=range(itmax)
  else:
    tau=np.load('tau'+str(band)+str(m-1)+'.npy')
    eref=np.load('ref'+str(band)+str(m-1)+'.npy')
    cls=np.load('cls'+str(band)+str(m-1)+'.npy')
    iters=np.arange(itmax-m)+m
  for iter in iters:
    print "--- "+str(iter)+ " iteration ---"
    print " > reflectance "
    ref=ut.mk_ref(tc.jmax,tc.imax,f_list,tau,eref)
    temp=np.where(ref==1.0)
    cls[temp]=-1
    if iter < 3 : 
      cref=tc.aesth(ref,20,cls)
    else:
      if model == 'M' : cref=tc.aestm(ref,cls)
      elif model == 'P' : cref=tc.aesth(ref,20,cls)
      else : cref=tc.aest(ref,cls)
    print " > aerosol "
    taux=ut.mk_tau(tc.jmax,tc.imax,f_list,eref,cref)
    temp=np.where(taux==1.8)
    cls[temp]=-1
    print " > median filter "
    eref=(1.0-dec)*eref+dec*tc.xmedian(ref,wsize[0])
    tau=(1.0-dec)*tau+dec*tc.ymedian(taux,cls,wsize[1],twid[iter])
    temp=np.where(cls==-1) ; print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
    np.save('tau'+str(band)+str(iter),tau)
    np.save('ref'+str(band)+str(iter),eref)
    np.save('cls'+str(band)+str(iter),cls)
  if itmax > m :
    np.save('tau'+str(band)+'x',taux)
    np.save('eref'+str(band)+'x',ref)
  os.chdir('../DATA')

exit()

