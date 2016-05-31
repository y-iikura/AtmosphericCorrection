# cd /Volumes/Transcend/SCAN_PROGRAM3
#python

import os
import os.path as path
import sys
import cv2
import numpy as np
import subprocess
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import axes3d
from scipy import interpolate
#import copy

os.chdir('ETM03052510732')
fold=os.getcwd()
os.chdir('..')
cwd=os.getcwd()
sys.path.append(cwd)
import rtc_util as ut
import tcor_util as tc
os.chdir(fold)

fold2=os.getcwd()
os.chdir('../../PROGRAM')
reload(tc)
os.chdir(fold2)
#----------------------------
#  Initialize
#----------------------------
print "#### Initialize ####"
# parameter input

#fold=sys.argv[1]
#fold='NEW65M320_3'
fold='Mar65P320_5'
subf,tdec=fold.split('_')
depth=float(subf[3:5])/100
cls_name='cls'+subf[6:]+'.npy'
nmax=int(subf[6:])
#itmax=int(sys.argv[2])
itmax=5
dec=float(tdec)/10.0
model=subf[5]
print 'depth:',depth
print 'dec:',dec
print cls_name
print 'nmax:',nmax

#subf='TAU60M1280_3'

#line='mkdir '+ fold
#subprocess.call(line,shell=True)
#f=open('aparm.txt')
#lines=f.readlines()
#f.close()

#g=open(fold + '/aparm.txt','w')
#for line in lines:
#  if line.find('depth =') != -1:
#    line = '  depth =   ' + str(depth) +'\n'
#  if line.find('dec =') != -1:
#    line = '  dec =     ' + str(dec) +'\n'
#  print line,
#  g.write(line)

#g.close()


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
#tm4=tc.read_tif('sat4.tif')
#tm5=tc.read_tif('sat5.tif')
#tm7=tc.read_tif('sat7.tif')
tm1=cv2.imread('sat1.tif',0)
tm2=cv2.imread('sat2.tif',0)
tm3=cv2.imread('sat3.tif',0)
tm4=cv2.imread('sat4.tif',0)
tm5=cv2.imread('sat5.tif',0)
tm7=cv2.imread('sat7.tif',0)

jaxa=cv2.imread('jaxa.tif',0)

f=open('dep_height_sangle01.txt')
lines=f.readlines()
f.close()
n_line=len(lines)
temp=lines[n_line-5].split()[1:4]
print temp
ntau=int(temp[0])+1
nhigh=int(temp[1])+1
nsang=int(temp[2])+1
temp=lines[n_line-4].split()[2]
ut.r_set0=float(temp)
print ntau,nhigh,nsang,ut.r_set0

nterm=15

#------------------------------
#    Processing of Band 1
#------------------------------
print "#### Processing of Band 1 ####"
#ntau=10; nhigh=10; nterm=15
#data=ut.read_data('dep_height_sangle01.txt',ntau,nhigh,nterm,nsang)
#ut.set_data(data,ntau,nhigh,nsang)

# initial data
#ut.r_set0=data[0,2]; ut.r_set0
ut.cosb0=np.cos((90.0-el)*np.pi/180); ut.cosb0
tmx=gain[0]*tm1+offset[0]

# tau-roh function for every pixel
print "--- function list ---"
f_list=np.load('f_band1.npy')

cls=np.load(cls_name)

tc.display('jaxa',jaxa,600,600,0.0,10.0)
tc.display('cls',cls.astype(np.int16),600,600,0.0,320.0)
#---------------------------------------------
# Iteration estimation of reflectance for the image
#--------------------------------------------
os.chdir('../'+fold)

m=9

tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
eref=penv[0]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)

tau=np.load('tau1'+str(m-1)+'.npy')
eref=np.load('ref1'+str(m-1)+'.npy')
cls=np.load('cls1'+str(m-1)+'.npy')
iters=np.arange(itmax-m)+m

iter=0
print "--- "+str(iter)+ " iteration ---"
print " > reflectance "
ref=ut.mk_ref(tc.jmax,tc.imax,f_list,tau,eref)
tc.display('refx',ref,600,600,0.0,0.1)
cref=tc.aesth(ref,20,cls)
tc.display('crefx',cref,600,600,0.0,0.1)

cref=tc.aestm(ref,cls)
tc.display('cref2',cref,600,600,0.0,0.1)

cref=tc.aest(ref,cls)
tc.display('cref3',cref,600,600,0.0,0.1)

#cref=tc.aest(ref,cls)
print " > aerosol "
taux=ut.mk_tau(tc.jmax,tc.imax,f_list,eref,cref)
tc.display('taux',taux,600,600,0.0,1.0)

print " > median filter "
eref=(1.0-dec)*eref+dec*tc.xmedian(ref,wsize[0])
tau=(1.0-dec)*tau+dec*tc.ymedian(taux,cls,wsize[1],twid[iter])
temp=np.where(cls==-1) ; print 100.0*len(temp[0])/float(tc.imax*tc.jmax)

np.save('tau1'+str(iter),tau)
np.save('ref1'+str(iter),eref)
  np.save('cls1'+str(iter),cls)

iter=iter+1

tc.display('cls',cls.astype(np.int16),600,600,0.0,640.0)
tc.display('cls',cls.astype(np.int16),600,600,0.0,1.0)

cv2.destroyAllWindows()



if itmax > m :
  np.save('tau1x',taux)
  np.save('ref1x',ref)

os.chdir('../DATA')

for value in trefx: n_c[value] = n_c.get(value, 0) + 1

#------------------------------
#    Processing of Band 2
#------------------------------
print "#### Processing of Band 2 ####"
#ntau=10; nhigh=10; nterm=15
data=ut.read_data('dep_height_sangle02.txt',ntau,nhigh,nterm,nsang)
ut.set_data(data,ntau,nhigh,nsang)

# initial data
ut.r_set0=data[0,2]; ut.r_set0
ut.cosb0=np.cos((90.0-el)*np.pi/180); ut.cosb0
tmx=gain[1]*tm2+offset[1]

# tau-roh function for every pixel
print "--- function list ---"
if path.exists('f_band2.npy') == True:
    f_list=np.load('f_band2.npy')
else:
    t=cv2.getTickCount() 
    f_list=ut.mk_list(tc.jmax,tc.imax,tmx,inc,dem,s_ang)
    print (cv2.getTickCount()-t)/cv2.getTickFrequency()
    np.save('f_band2',f_list)

if path.exists(cls_name) == True:
    cls=np.load(cls_name)
else:
   cls=tc.mclass(256*inc,256*slp,20*jaxa,nmax)
   nmax2=np.max(cls)
   cls[np.where(jaxa==1)]=nmax2+1
   np.save(cls_name)


#---------------------------------------------
# Iteration estimation of reflectance for the image
#--------------------------------------------
os.chdir('../'+fold)
temp=[x for x in os.listdir('.') if x.find('cls2')==0]
m=len(temp)

if m == 0 :
  tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  eref=penv[0]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  iters=range(itmax)
else:
  tau=np.load('tau2'+str(m-1)+'.npy')
  eref=np.load('ref2'+str(m-1)+'.npy')
  cls=np.load('cls2'+str(m-1)+'.npy')
  iters=np.arange(itmax-m)+m

for iter in iters:
  print "--- "+str(iter)+ " iteration ---"
  print " > reflectance "
  ref=ut.mk_ref(tc.jmax,tc.imax,f_list,tau,eref)
  if iter < 3 : 
    cref=tc.aesth(ref,20,cls)
  else:
    if model == 'M' : cref=tc.aestm(ref,cls)
    elif model == 'P' : cref=tc.aesth(ref,20,cls)
    else : cref=tc.aest(ref,cls)
  print " > aerosol "
  taux=ut.mk_tau(tc.jmax,tc.imax,f_list,eref,cref)
  print " > median filter "
  eref=(1.0-dec)*eref+dec*tc.xmedian(ref,wsize[0])
  tau=(1.0-dec)*tau+dec*tc.ymedian(taux,cls,wsize[1],twid[iter])
  temp=np.where(cls==-1) ; print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
  np.save('tau2'+str(iter),tau)
  np.save('ref2'+str(iter),eref)
  np.save('cls2'+str(iter),cls)

if itmax > m :
  np.save('tau2x',taux)
  np.save('ref2x',ref)

os.chdir('../DATA')

#------------------------------
#    Processing of Band 3
#------------------------------
print "#### Processing of Band 3 ####"
#ntau=10; nhigh=10; nterm=15
data=ut.read_data('dep_height_sangle03B.txt',ntau,nhigh,nterm,nsang)
ut.set_data(data,ntau,nhigh,nsang)

# initial data
ut.r_set0=data[0,2]; ut.r_set0
ut.cosb0=np.cos((90.0-el)*np.pi/180); ut.cosb0
tmx=gain[2]*tm3+offset[2]

# tau-roh function for every pixel
print "--- function list ---"

if path.exists('f_band3.npy') == True:
    f_list=np.load('f_band.npy')
else:
    t=cv2.getTickCount() 
    f_list=ut.mk_list(tc.jmax,tc.imax,tmx,inc,dem,s_ang)
    print (cv2.getTickCount()-t)/cv2.getTickFrequency()
    np.save('f_band3',f_list)

if path.exists(cls_name) == True:
    cls=np.load(cls_name)
else:
   cls=tc.mclass(256*inc,256*slp,20*jaxa,nmax)
   nmax2=np.max(cls)
   cls[np.where(jaxa==1)]=nmax2+1
   np.save(cls_name)

#---------------------------------------------
# Iteration estimation of reflectance for the image
#--------------------------------------------
os.chdir('../'+fold)
temp=[x for x in os.listdir('.') if x.find('cls3')==0]
m=len(temp)

if m == 0 :
  tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  eref=penv[0]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  iters=range(itmax)
else:
  tau=np.load('tau3'+str(m-1)+'.npy')
  eref=np.load('ref3'+str(m-1)+'.npy')
  cls=np.load('cls3'+str(m-1)+'.npy')
  iters=np.arange(itmax-m)+m

for iter in iters:
  print "--- "+str(iter)+ " iteration ---"
  print " > reflectance "
  ref=ut.mk_ref(tc.jmax,tc.imax,f_list,tau,eref)
  if iter < 3 : 
    cref=tc.aesth(ref,20,cls)
  else:
    if model == 'M' : cref=tc.aestm(ref,cls)
    elif model == 'P' : cref=tc.aesth(ref,20,cls)
    else : cref=tc.aest(ref,cls)
  print " > aerosol "
  taux=ut.mk_tau(tc.jmax,tc.imax,f_list,eref,cref)
  print " > median filter "
  eref=(1.0-dec)*eref+dec*tc.xmedian(ref,wsize[0])
  tau=(1.0-dec)*tau+dec*tc.ymedian(taux,cls,wsize[1],twid[iter])
  temp=np.where(cls==-1) ; print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
  np.save('tau3'+str(iter),tau)
  np.save('ref3'+str(iter),eref)
  np.save('cls3'+str(iter),cls)

if itmax > m :
  np.save('tau3x',taux)
  np.save('ref3x',ref)

os.chdir('../DATA')

exit()
