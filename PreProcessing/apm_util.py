#!/usr/bin/env python
# coding:utf-8
# cd /Volumes/Transcend/SCAN_PROGRAM2
# python

import os
import numpy as np
from numpy.linalg import inv
from osgeo import gdal

earth=6378137.0
xn=0.0 ; yn=0.0
hsat=0.0

def read_parm(text,parm,num):
    temp=filter(lambda x: x.find(parm)==2,text)
    temp1=temp[0].split()
    temp2=filter(lambda x: x.find("=")!=0,temp1)
    data=temp2[1:num+1]
    return map(lambda x:float(x),data)

def read_tif(fname):
  src = gdal.Open(fname, gdal.GA_Update)
  pdem = src.GetRasterBand(1)
  gt = src.GetGeoTransform()
  image = pdem.ReadAsArray()
  return [gt,image]

def xdist(xxx,yyy,pqinv):
    #xy=np.array([[xxx-xn],[yyy-yn]])
    xy=np.array([xxx-xn,yyy-yn])
    temp=pqinv.dot(xy)
    return temp[0]

def angle(px):
    a=px/earth
    s=(earth+hsat)*np.sin(a)
    c=(earth+hsat)*np.cos(a)
    f=np.arctan(s/(c-earth))
    return -np.degrees(f)

def sangle(xxx,yyy,pq):
    pqt = pq.T
    pqinv = inv(pqt)
    pxy=xdist(xxx,yyy,pqinv)
    return angle(pxy)

def s_file(xs,ye,jmax,imax,pq):
    res=[]
    for y in range(jmax):
        xx=xs+np.arange(imax)*30
        yy=ye-np.ones(imax)*30*y
        s_ang=sangle(xx,yy,pq)
        res.append(s_ang)
    res = np.array(res)
    return res.reshape(jmax,imax)


if __name__ == "__main__":

  f=open('gparm.txt')
  lines=f.readlines()
  f.close()

  sun_el=read_parm(lines,'el=',1)[0]
  sun_az=read_parm(lines,'az=',1)[0]
  pv=read_parm(lines,'pv=',2)
  qv=read_parm(lines,'qv=',2)
  pq=np.array([pv,qv])
  xn=read_parm(lines,'xn=',1)[0]
  yn=read_parm(lines,'yn=',1)[0]
  if fold.find('ETM')!=-1 : nband=6
  if fold.find('AVN')!=-1 : nband=4

  offset=read_parm(lines,'offset=',nband)
  gain=read_parm(lines,'gain=',nband)

