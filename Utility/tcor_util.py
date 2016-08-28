import numpy as np
import cv2
#from osgeo import gdal
import scipy.cluster

imax=1200
jmax=1200

def read_parm(text,parm):
    temp=filter(lambda x: x.find(parm)==2,text)
    temp1=temp[0].split()
    temp2=filter(lambda x: x.find("=")!=0,temp1)
    data=temp2[1:]
    return map(lambda x:float(x),data)

#def read_tif(fname):
#    src = gdal.Open(fname, gdal.GA_Update)
#    pdem = src.GetRasterBand(1)
#    image = pdem.ReadAsArray()
#    return image

def img_prop(x):
    print x.shape,x.dtype,x.min(),x.max()

def incident(dem,el,az,dx,dy):
    el=np.pi*el/180 ; az=np.pi*az/180
#    imax,jmax=dem.shape
    a=(np.roll(dem,-1,1)-np.roll(dem,1,1))/dx/2
    a[:,0]=a[:,1] ; a[:,imax-1]=a[:,imax-2] 
    b=(np.roll(dem,1,0)-np.roll(dem,-1,0))/dy/2
    b[0,:]=b[1,:] ; b[jmax-1,:]=b[jmax-2,:]
    temp=-a*np.cos(el)*np.sin(az)-b*np.cos(el)*np.cos(az)+np.sin(el)
    return temp/np.sqrt(1+a**2+b**2)

def slope(dem,dx,dy):
    a=(np.roll(dem,-1,1)-np.roll(dem,1,1))/dx/2
    a[:,0]=a[:,1] ; a[:,imax-1]=a[:,imax-2] 
    b=(np.roll(dem,1,0)-np.roll(dem,-1,0))/dy/2
    b[0,:]=b[1,:] ; b[jmax-1,:]=b[jmax-2,:]
    return np.sqrt(a**2+b**2)

def display0(image,imax0,jmax0,dmin,dmax):
    imgx=cv2.resize(image,(imax0,jmax0))
    imgy=255.0*(imgx-dmin)/(dmax-dmin)
    imgy[imgy>255]=255
    imgy[imgy<0]=0
    return np.uint8(imgy)

def display(wname,image,imax0,jmax0,dmin,dmax):
    imgx=cv2.resize(image,(imax0,jmax0))
    imgy=255.0*(imgx-dmin)/(dmax-dmin)
    imgy[imgy>255]=255
    imgy[imgy<0]=0
    cv2.imshow(wname,np.uint8(imgy))

def percent(img,pmin,pmax):
#    imax,jmax=img.shape
    tsort=np.sort(img.flatten())
    low=pmin*imax*jmax
    high=pmax*imax*jmax
    return [float(tsort[low]),float(tsort[high])]
    
def sconv(tm,min,max,dmax):
    if min == max : max=max+1
    tmx=dmax*(np.float32(tm)-min)/(max-min)
    tmx[tmx > (dmax-1)]=dmax-1
    tmx[tmx < 0]=0
    return np.uint8(tmx)

def mclass(cls1,cls2,cls3,nmax):
    num=imax*jmax
    cls1x=np.float32(cls1.reshape(num))
    cls2x=np.float32(cls2.reshape(num))
    cls3x=np.float32(cls3.reshape(num))
    data=np.array([[cls1x],[cls2x],[cls3x]])
    data=data.reshape(3,num)
    data=np.transpose(data)
    datax=data[::100,:]
    t=cv2.getTickCount()
    codebook, destortion = scipy.cluster.vq.kmeans(datax, nmax, iter=10, thresh=1e-05)
    print (cv2.getTickCount()-t)/cv2.getTickFrequency()
    t=cv2.getTickCount()
    code, dist = scipy.cluster.vq.vq(data, codebook)
    print (cv2.getTickCount()-t)/cv2.getTickFrequency()
    return code.reshape(jmax,imax)

def aestp(ref,per,cls):
#    imax,jmax=tmx.shape#    ktemp=np.zeros(imax*jmax).reshape(imax,jmax)
    ktemp=ref.copy()
    d0=np.max(cls)    for i in range(d0+1):
        temp=np.where(cls==i)
        cnt=temp[0].shape
        if cnt[0] != 0:
            nper=int(per*cnt[0])
            tref=ref[temp]
            stmx=np.sort(tref)            ktemp[temp]=stmx[nper]
        else: ktemp[temp]=ref[temp]
    return ktemp

def aestm(ref,cls):
#    imax,jmax=tmx.shape#    ktemp=np.zeros(imax*jmax).reshape(imax,jmax)
    ktemp=ref.copy()
    d0=np.max(cls)    for i in range(d0+1):
        temp=np.where(cls==i)
        cnt=temp[0].shape
        if cnt[0] != 0:
            ktemp[temp]=np.median(ref[temp])
        else: ktemp[temp]=ref[temp]
    return ktemp

def aest(ref,cls):
#    imax,jmax=tmx.shape#    ktemp=np.zeros(imax*jmax).reshape(imax,jmax)
    ktemp=ref.copy()
    d0=np.max(cls)    for i in range(d0+1):
        temp=np.where(cls==i)
        cnt=temp[0].shape
        if cnt[0] != 0:
            ktemp[temp]=np.mean(ref[temp])
        else: ktemp[temp]=ref[temp]
    return ktemp


def mode(values):
    result = []
    n_c = {}
    for value in values:
        n_c[value] = n_c.get(value, 0) + 1
    m = max(n_c.values())
    for n, c in n_c.items():
        if c == m:
            result.append(n)
    return np.mean(result)

def aesth(ref,con,cls):
#    imax,jmax=tmx.shape#    ktemp=np.zeros(imax*jmax).reshape(imax,jmax)
    ktemp=ref.copy()
    d0=np.max(cls)
    # 5/6/2016    #for i in range(d0):
    for i in range(d0+1):
        temp=np.where(cls==i)
        cnt=temp[0].shape
        cnt0=cnt[0]
        if cnt0 > 20:
            tref=ref[temp]
            min=np.min(tref)
            max=np.max(tref)
            # 5/6/2016
            if cnt0 > 2000: cnt0=2000
            trefx=sconv(tref,min,max,cnt0/con)
            ktemp[temp]=float(con)*(max-min)*mode(trefx)/cnt0+min
        else: ktemp[temp]=ref[temp]
    return ktemp


def xmedian(ref,mwid):
    temp=np.isnan(ref)
    tmean=np.nanmean(ref)
    ref[temp]=tmean
    ref2=cv2.blur(ref,(mwid,mwid))
    ref[temp]=ref2[temp]
    tempx=np.uint8(255*ref)
    return cv2.medianBlur(tempx,mwid)/255.0

def ymedian0(aero,cls,mwid):
    temp=np.isnan(aero)
    tmean=np.nanmean(aero)
    aero[temp]=tmean
    aero2=cv2.blur(aero,(mwid,mwid))
    aero[temp]=aero2[temp]
    tempx=np.uint8(100*aero)
    aerox=cv2.medianBlur(tempx,mwid)/100.0
    return aerox

def ymedian(aero,cls,mwid,twid):
    temp=np.isnan(aero)
    tmean=np.nanmean(aero)
    aero[temp]=tmean
    aero2=cv2.blur(aero,(mwid,mwid))
    aero[temp]=aero2[temp]
    # 4/28/2016
    #tempx=np.uint8(255*aero)
    tempx=np.uint8(100*aero)
    #aerox=cv2.medianBlur(tempx,mwid)/255.0
    aerox=cv2.medianBlur(tempx,mwid)/100.0
    ptemp=np.where(np.abs(aero-aerox) > twid)
    cls[ptemp]=-1
    return aerox

def hcor(tau,dem,h0):
    taux=tau*np.exp(-dem/h0)
    return taux