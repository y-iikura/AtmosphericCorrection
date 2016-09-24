#!/usr/bin/env python
# coding:utf-8
# cd /Volunes/Transcend/SCAN_PROGRAM3
# python PROGRAM/sixs_parm.py SceneFolderName AerosolType ScaleHeight
# 	SceneFolderName: ETM02052110732, AVN0309172800 ...
#	AerosolType: Mar(itime), Con(tinental), Urb(an) ...
#       ScaleHeight: 2(km), 0 for non vertical profile ...
#


import numpy as np
import os
import sys

os.chdir('PreProcessing')
import sixs_util as six
f=open('6s_template.txt','r')
lines=f.readlines()
f.close()


# Calculation of Atmospheric Parameters by 6S

fold=sys.argv[1]
atype=sys.argv[2]
scale=sys.argv[3]
fname='DATA/'+atype+scale
scale=float(scale)/10.0
print fold,atype,fname,scale
if atype=='Con': type=1
if atype=='Mar': type=2
if atype=='Urb': type=3

#ref_set=0.3
#imax=int(sys.argv[4])
#jmax=int(sys.argv[5])
#print ref_set,imax,jmax

os.chdir('../'+fold)

f=open('aparm.txt','r')
lines2=f.readlines()
f.close()

for line in lines2:
  if line.find('el') == 2:
	el=float(line.split()[2])
  if line.find('az') == 2:
	az=float(line.split()[2])
  if line.find('min') == 2:
	smin=float(line.split()[2])
  if line.find('max') == 2:
	smax=float(line.split()[2])
  if line.find('saz') == 2:
	sazm=float(line.split()[2])
  if line.find('mon') == 2:
	mon=int(line.split()[2])
  if line.find('day') == 2:
	day=int(line.split()[2])
  if line.find('number') == 2:
	number=[int(data) for data in line.split()[2:]]
  if line.find('tau') == 2:
	tau=[float(data) for data in line.split()[2:]]
  if line.find('height') == 2:
	height=[float(data) for data in line.split()[2:]]
  if line.find('ref') == 2:
	ref_set=float(line.split()[2])
  print line,

#ref_set=float(lines2[-2])
print ref_set
print number
print tau
print height
print el,az,smin,smax,sazm,mon,day

#exit()

six.smin=int(np.floor(smin))
six.smax=int(np.ceil(smax)+1)
six.sazm=sazm


el=90.0-el
if smin > 0.0 : 
  sazm2=sazm
  sel=smin
else:
  sazm2=sazm+180.0
  sel=-smin

geomet='  {0} {1} {2} {3} {4} {5}\n'.format(el,az,sel,sazm2,mon,day)

g=open('w1.txt','w')
count=0
for line in lines:
  if count == 1:
    line = geomet
  if count == 3:
    line = '  '+str(type)+'\n'
  count = count+1
  print line,
  g.write(line)

g.close()

#exit()

# for sixs version SV1.1 & SV1.2 => ~/bin/sixs2
#if fold.find('ETM')!=-1 : band0=137
#if fold.find('OLI')!=-1 : band0=165
#if fold.find('AVN')!=-1 : band0=200
# for sixs version SV2.1 & SV2.2=>~/bin/sixsV2.2

for band in number[0:]:
  print '*** band'+str(band-number[0]+1)+' ***'
  six.change_band('w1.txt','w1x.txt',band)
  fnamex=fname+'_'+str(band-number[0]+1)+'.txt'
  six.write_param('w1x.txt',fnamex,ref_set,tau,height,scale,0)

exit()


band=2
six.change_band('w1.txt','w1x.txt',band+band0)
fnamex=fname+'_'+str(band+1)+'.txt'
six.write_param('w1x.txt',fnamex,ref_set,imax,jmax,scale,0)


