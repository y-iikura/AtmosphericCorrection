import numpy as np
import subprocess
from scipy import interpolate
from scipy import ndimage
import cv2

t_set=0.0; h_set=0.0; r_set=0.0; solar=0.0
path_rad=0.0; back_rad=0.0; pixel_rad=0.0
dir_irad=0.0; sky_irad=0.0; env_irad=0.0
tau_rayl=0.0; tau_aero=0.0; tau_minor=0.0
sph_alb=0.0

fpath_rad=0.0; fback_rad=0.0; fpixel_rad=0.0
fdir_irad=0.0; fsky_irad=0.0; fenv_irad=0.0
ftau_rayl=0.0; ftau_aero=0.0; ftau_minor=0.0
fsph_alb=0.0

dtau=0.0; dheight=0.0; smin=0
cosb0=0.0; r_set0=0.0

def read_data(fin,ntau,nhigh,nterm,nsang):
    f=open(fin,'r')
    text=f.read()
    f.close()
    lines=text.split('\n')
    xlines=[x.split() for x in lines if x.find('****') == -1]
    xlines=xlines[0:4*ntau*nhigh*nsang]
    data=[]
    for line in xlines:
        temp=[float(x) for x in line]
        data.extend(temp)
    return np.array(data).reshape(ntau*nhigh*nsang,nterm)

def set_data(data,ntau,nhigh,nsang):
    global t_set,h_set,r_set,s_set
    global solar,path_rad,pixel_rad,back_rad,dir_irad,sky_irad,env_irad
    global tau_rayl,tau_aero,tau_minor,sph_alb
    global dtau,dheight,r_set0,smin
    t_set=data[:,0].reshape(ntau,nhigh,nsang)
    dtau=t_set[1,0,0]-t_set[0,0,0]
    h_set=data[:,1].reshape(ntau,nhigh,nsang)
    dheight=h_set[0,1,0]-h_set[0,0,0]
    r_set=data[:,2].reshape(ntau,nhigh,nsang)
    r_set0=r_set[0,0,0]
    s_set=data[:,3].reshape(ntau,nhigh,nsang)
    smin=s_set[0,0,0]
    solar=data[:,4].reshape(ntau,nhigh,nsang)
    path_rad=data[:,5].reshape(ntau,nhigh,nsang)
    back_rad=data[:,6].reshape(ntau,nhigh,nsang)
    pixel_rad=data[:,7].reshape(ntau,nhigh,nsang)
    dir_irad=data[:,8].reshape(ntau,nhigh,nsang)
    sky_irad=data[:,9].reshape(ntau,nhigh,nsang)
    env_irad=data[:,10].reshape(ntau,nhigh,nsang)
    sph_alb=data[:,11].reshape(ntau,nhigh,nsang)
    tau_rayl=data[:,12].reshape(ntau,nhigh,nsang)
    tau_aero=data[:,13].reshape(ntau,nhigh,nsang)
    tau_minor=data[:,14].reshape(ntau,nhigh,nsang)
    print dtau,dheight,r_set0,smin


def reflectance(rad,cosb,t_setx,height,r_setx,s_setx,sang):
    n=len(t_set)    
    ttmp=[x/dtau for x in t_setx]
    htmp=[height/dheight for x in t_setx]
    stmp=[sang-x for x in s_setx]
    path=ndimage.map_coordinates(path_rad,[ttmp,htmp,stmp]).reshape(n,1)
    back=ndimage.map_coordinates(back_rad,[ttmp,htmp,stmp]).reshape(n,1)
    pixel=ndimage.map_coordinates(pixel_rad,[ttmp,htmp,stmp]).reshape(n,1)
    dir=ndimage.map_coordinates(dir_irad,[ttmp,htmp,stmp]).reshape(n,1)
    sky=ndimage.map_coordinates(sky_irad,[ttmp,htmp,stmp]).reshape(n,1)
    env=ndimage.map_coordinates(env_irad,[ttmp,htmp,stmp]).reshape(n,1)
    sph=ndimage.map_coordinates(sph_alb,[ttmp,htmp,stmp]).reshape(n,1)
    rayl=ndimage.map_coordinates(tau_rayl,[ttmp,htmp,stmp]).reshape(n,1)
    aero=ndimage.map_coordinates(tau_aero,[ttmp,htmp,stmp]).reshape(n,1)
    minor=ndimage.map_coordinates(tau_minor,[ttmp,htmp,stmp]).reshape(n,1)
    dir=dir*cosb/cosb0
    #print dir
    back=back*(1-r_set0*sph)*r_setx/(1-r_setx*sph)/r_set0
    #print back
    env=env*(1-r_set0*sph)*r_setx/(1-r_setx*sph)/r_set0
    odep=rayl+aero+minor
    S=np.cos(np.pi*sang/180)
    return np.pi*(rad-path-back)/(dir+sky+env)*np.exp(odep/S)

def fref(rad,cosb,height,t_setx,r_setx,s_setx,sang):
    ref=reflectance(rad,cosb,t_setx,height,r_setx,s_setx,sang)
    return interpolate.RectBivariateSpline(t_setx,r_setx,ref)


def iestimate(res,ref1):
    res=res.reshape(4)
    res[3]=res[3]-ref1
    p=np.poly1d(res)
    #kai=[np.real(z) for z in p.r if np.imag(z) == 0 and 0 < np.real(z) < 1.0] 
    # 2016/3/25 
    #kai=[np.real(z) for z in p.r if np.imag(z) == 0 and 0 < np.real(z) < 1.4] 
    # 2016/5/25 
    kai=[np.real(z) for z in p.r if np.imag(z) == 0 ] 
    xkai=np.nan
    if len(kai)==1:
       xkai=kai[0]
       if xkai < 0.0 : xkai=0.0
       if xkai > 1.8 : xkai=1.8 
    return xkai

def mk_list(jmax,imax,tmx,inc,dem,sang):
    f_list=[]
    t_setx=t_set[:,0,0] 
    #r_setx=t_set[:,0,0]
    r_setx=np.array([0.0,0.2,0.4,0.6,0.8,1.0])
    nlen=len(t_setx)
    s_setx=smin*np.ones(nlen)
    t=cv2.getTickCount() 
    for j in range(jmax):
        temp=[]
        for i in range(imax):
            frefx=fref(tmx[j,i],inc[j,i],dem[j,i]/1000.0,t_setx,r_setx,s_setx,sang[j,i])
            temp=temp+[frefx]
        if j % 100 == 0: print j,(cv2.getTickCount()-t)/cv2.getTickFrequency()
        f_list=f_list+[temp]
    return f_list


def mk_ref(jmax,imax,f_list,tau,eref):
    ref=np.zeros(imax*jmax).reshape(jmax,imax)
    #t=cv2.getTickCount() 
    for j in range(jmax):
        for i in range(imax):
            fref=f_list[j][i]
	    temp=fref(tau[j,i],eref[j,i])
            if temp < 0.0 : temp = 0.0
            if temp > 1.0 : temp = 1.0
            ref[j,i] = temp
        #if j % 100 == 0: print j,(cv2.getTickCount()-t)/cv2.getTickFrequency()
    print np.mean(ref),np.std(ref)
    return ref
    
def mk_tau(jmax,imax,f_list,eref,cref):
    taux=np.zeros(imax*jmax).reshape(jmax,imax)
    x=t_set 
    #t=cv2.getTickCount() 
    for j in range(jmax):
        for i in range(imax):
            fref=f_list[j][i]
            res=np.polyfit(x,fref(x,eref[j,i]),3) # 3rd order
	    taux[j,i]=iestimate(res,cref[j,i])
        #if j % 100 == 0: print i,(cv2.getTickCount()-t)/cv2.getTickFrequency()
    temp=np.where(np.isnan(taux)==True)
    print np.nanmean(taux),np.nanstd(taux),len(temp[0])
    return taux

