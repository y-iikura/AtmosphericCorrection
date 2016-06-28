# 3/13/2016 copy from tcor_030525.py
# cd /Volumes/Transcend/SCAN_PROGRAM3
# python
import os
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
nstr=int(sys.argv[2])
nend=int(sys.argv[3])
dec=float(tdec)/10.0
model=subf[5]
print 'depth:',depth
print 'dec:',dec
print 'nmax:',nmax
print nstr,'-',nend

f=open(fold +'/aparm.txt')
text=f.readlines()
f.close()
    
el=tc.read_parm(text,'el',1)[0]
az=tc.read_parm(text,'az',1)[0]
nband=int(tc.read_parm(text,'nband',1)[0])
offset=tc.read_parm(text,'offset',nband)
gain=tc.read_parm(text,'gain',nband)
if fscene.find('OLI') == -1:
  penv=tc.read_parm(text,'penv',3)
else:
  penv=tc.read_parm(text,'penv',4)

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
#s_ang=np.load('sangle.npy')
#veg=np.ones(tc.imax*tc.jmax,dtype=np.uint16).reshape(tc.jmax,tc.imax)

#------------------------------
#    Main Processing
#------------------------------
if fscene.find('OLI') == -1:
  b_list=[1,2,3]
else:
  b_list=[1,2,3,4]
for band in b_list:
  print "#### Processing of Band"+str(band)+" ####"
  # tau-roh function for every pixel
  ut.cosb0=np.cos((90.0-el)*np.pi/180); ut.cosb0
  print "--- function list ---"
  f_list=np.load(fun_name+'_'+str(band)+'.npy')
  cls=np.load(cls_name+'.npy')
  os.chdir('../'+fold)
  tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  eref=penv[0]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  for n in range(nstr):
    print "--- "+str(n)+ " iteration ---"
    t_ref=np.load('ref'+str(band)+str(n)+'.npy')
    temp=np.where(t_ref==1.0)
    cls[temp]=-1
    eref=(1.0-dec)*eref+dec*tc.xmedian(t_ref,wsize[0])
    t_taux=np.load('tau'+str(band)+str(n)+'.npy')
    temp=np.where(t_taux==1.8)
    cls[temp]=-1
    tau=(1.0-dec)*tau+dec*tc.ymedian(t_taux,cls,wsize[1],twid[n])
    temp=np.where(cls==-1)
    print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
  cls=tc.mclass(256*inc,128*slp,256*256*t_ref,nmax)
  np.save('cls'+str(band),cls)
  iters=np.arange(nend-nstr)+nstr
  for iter in iters:
    print "--- "+str(iter)+ " iteration ---"
    print " > reflectance "
    ref=ut.mk_ref(tc.jmax,tc.imax,f_list,tau,eref)
    temp=np.where(ref==1.0)
    cls[temp]=-1
    if model == 'M' : cref=tc.aestm(ref,cls)
    elif model == 'P' : cref=tc.aesth(ref,20,cls)
    else : cref=tc.aest(ref,cls)
    print " > aerosol "
    eref=(1.0-dec)*eref+dec*tc.xmedian(ref,wsize[0])
    taux=ut.mk_tau(tc.jmax,tc.imax,f_list,eref,cref)
    temp=np.where(taux==1.8)
    cls[temp]=-1
    print " > median filter "
    tau=(1.0-dec)*tau+dec*tc.ymedian(taux,cls,wsize[1],twid[iter])
    temp=np.where(cls==-1) ; print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
    np.save('tau'+str(band)+str(iter),taux)
    np.save('ref'+str(band)+str(iter),ref)
    #temp=np.where(cls == -1)
    #np.save('cls'+str(band)+str(iter)+'x',temp)
  os.chdir('../DATA')

exit()

