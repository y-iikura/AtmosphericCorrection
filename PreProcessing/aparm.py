#!/usr/bin/env python
# coding:utf-8
# cd /Volumes/Transcend/SCAN_PROGRAM2
# python PROGRAM/aparm.py SceneFolderName

import os
import numpy as np
import sys

os.chdir('PreProcessing')
import apm_util as ut
print "* read aparm.txt template"
f=open('aparm_template.txt')
lines=f.readlines()
f.close()

f=open('bparm_template.txt')
lines3=f.readlines()
f.close()

os.chdir('..')
fold=sys.argv[1]
print "* Target folder : "+fold
os.chdir(fold)

print "* read gparm.txt"
f=open('gparm.txt')
lines2=f.readlines()
f.close()

sun_el=ut.read_parm(lines2,'el=',1)[0]
sun_az=ut.read_parm(lines2,'az=',1)[0]
pv=ut.read_parm(lines2,'pv=',2)
qv=ut.read_parm(lines2,'qv=',2)
pq=np.array([pv,qv])
ut.xn=ut.read_parm(lines2,'xn=',1)[0]
ut.yn=ut.read_parm(lines2,'yn=',1)[0]
ut.hsat=ut.read_parm(lines2,'hsat=',1)[0]
if fold.find('ETM')!=-1 :
  nband=6
  btext='  BAND1 BAND2 BAND3 BAND4 BAND5 BAND7\n'

if fold.find('AVN')!=-1 : 
  nband=4
  btext='  BAND1 BAND2 BAND3 BAND4\n'

if fold.find('OLI')!=-1 : 
  nband=8
  btext='  BAND1 BAND2 BAND3 BAND4 BAND5 BAND6 BAND7 BAND9\n'

offset=ut.read_parm(lines2,'offset=',nband)
gain=ut.read_parm(lines2,'gain=',nband)


#ut.sangle(69165.0+ut.xn,0.0+ut.yn,pq)
#ut.sangle(-69165.0+ut.xn,0.0+ut.yn,pq)

#5/7/2016 for ETM03052510732_S
gt,image=ut.read_tif('DATA/jaxa.tif')
#gt,image=ut.read_tif('DATA/dem.tif')

jmax,imax=image.shape
xs=gt[0]
ye=gt[3]
dx=gt[1]
dy=-gt[5]

print "* calculate scan angle"
#ss2=ut.s_file2(xs,ye,imax,jmax,pq)
ss=ut.s_file(xs,ye,jmax,imax,pq)

np.save('DATA/sangle',ss)

scan=90.0+np.arccos(pv[0])*180/np.pi
smin=round(np.min(ss),2)
smax=round(np.max(ss),2)

year=int(fold[3:5])+2000
mon=int(fold[5:7])
day=int(fold[7:9])

print "* write aparm.txt "
g=open('aparm.txt','w')
for line in lines:
  if line.find('el =') != -1:
    line = '  el =   ' + format(sun_el,'7.2f') +'\n'
  if line.find('az =') != -1:
    line = '  az =   ' + format(sun_az,'7.2f') +'\n'
  if line.find('nband =') != -1:
    line = '  nband =   ' + str(nband) +'\n'
  if line.find('BAND1') != -1:
    line = btext
  if line.find('offset =') != -1:
    line = '  offset =   '
    for i in range(nband):
	line = line + '{0}  '.format(offset[i])
    line = line + '\n'
  if line.find('gain =') != -1:
    line = '  gain =   '
    for i in range(nband):
        line = line + '{0}  '.format(gain[i])
    line = line + '\n'
  #if line.find('penv') != -1 and fold.find('OLI') != -1 :
  # line = '  penv =   0.06 0.06 0.06 0.06\n'
  #print line
  g.write(line)

g.write('scan angle:\n')
g.write('  min = '+str(smin)+'\n')
g.write('  max = '+str(smax)+'\n')
g.write('  saz = '+str(round(scan,2))+'\n')
g.write('observation day:\n')
g.write('  year = '+str(year)+'\n')
g.write('  mon = '+str(mon)+'\n')
g.write('  day = '+str(day)+'\n')

for line in lines3:
   if line.find('tau =')!= -1:
      ntau=len(line.split())-2
   if line.find('height =')!= -1:
      nhigh=len(line.split())-2
   g.write(line) 

nsang=int(np.ceil(smax)+1)-int(np.floor(smin))
g.write("number of parameter:\n")
g.write('  nprm = '+str(ntau)+' '+str(nhigh)+' '+str(nsang)+'\n')
g.close()

exit()


