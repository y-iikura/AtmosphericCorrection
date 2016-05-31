#!/usr/bin/env python
#coding:utf-8
import numpy as np
import subprocess
import math

# Subroutine for Parameter Setting
#  change_data(fin,tau_set,ref_set,high_set)
#  read_out(out) from output of 6s

solar=0.0
path_rad=0.0; back_rad=0.0; pixel_rad=0.0
dir_irad=0.0; sky_irad=0.0; env_irad=0.0
tau_rayl=0.0; tau_aero=0.0; tau_minor=0.0
sph_alb=0.0

smin=0.0; smax=0.0; sazm=0.0

def change_band(fin,fout,band):
    f=open(fin)
    lines=f.readlines()
    f.close()
    g=open(fout,'w')
    count=0
    for line in lines:
        if  count == 8:
            line = '  '+str(band)+"\n"
        g.write(line)
        count = count+1
    g.close()

def change_data(fin,tau_set,ref_set,high_set,sang_set,scale):
    f=open(fin)
    lines=f.readlines()
    f.close()
    g=open('temp','w')
    count=0
    L=lines[1].split()
    # 5/4/2016 
    tau=tau_set
    if scale!=0.0: 
      tau=tau_set*np.exp(-high_set/scale) # change tau with height
    for line in lines:
        if count == 1:
            if sang_set>=0:
                line = '  '+L[0]+' '+L[1]+' '+str(sang_set)+' '+str(sazm)+' '+L[4]+' '+L[5]+"\n"
            else:
                sang_set=sang_set*(-1)
                line = '  '+L[0]+' '+L[1]+' '+str(sang_set)+' '+str(sazm+180.0)+' '+L[4]+' '+L[5]+"\n"
        if count == 5:
            line = '  '+str(tau)+"\n"
        if count == 6:
            line = '  '+ str(-high_set)+"\n"
        if count == 12:
            line = '  '+str(ref_set)+"\n"
        g.write(line)
        count = count+1
    g.close()    


def read_out(out,check):
    global solar,path_rad,pixel_rad,back_rad,dir_irad,sky_irad,env_irad
    global tau_rayl,tau_aero,tau_minor,sph_alb
    outx=out.split("\n")
    count=0
    flag=0 ; flag2=0 ; flag3=0
    for line in outx:
	#print count,line
	if flag == 1:
            if check==1: print line
            word=line.split()
            path_rad=float(word[1])
            back_rad=float(word[2])
            pixel_rad=float(word[3])
            flag=0
	if flag2 == 1:
            if check==1: print line
            word=line.split()
            dir_irad=float(word[1])
            sky_irad=float(word[2])
            env_irad=float(word[3])
            flag2=0
	if flag3 == 1:
            if check==1: print line
            word=line.split()
            wfil=float(word[1])
            watt=float(word[2])
            solar=watt/wfil
            flag3=0
	if line.find("atm. intrin. rad.") != -1:
            flag = 1
 	if line.find("direct solar irr.") != -1:
            flag2 = 1
  	if line.find("int. funct filter") != -1:
            flag3 = 1
   	if line.find("spherical albedo") != -1:
            if check==1: print line
            word=line.split()
            sph_alb=float(word[6])
    	if line.find("optical depth total") != -1:
            if check==1: print line
            word=line.split()
            tau_rayl=float(word[4])
            tau_aero=float(word[5])
    	if line.find("global gas. trans.") != -1:
            if check==1: print line
            word=line.split()
            temp=float(word[6])
            tau_minor=-np.log(temp)
        count=count+1

# 5/4/2016
#def write_param(fin,fout,ref_set,imax,jmax,check):
def write_param(fin,fout,ref_set,imax,jmax,scale,check):
    g=open(fout,'w')
    for i in range(imax):
        #tau_set=0.1*float(i)
        tau_set=0.2*float(i)
        for j in range(jmax):
            high_set=0.5*float(j)
            for s in range(smin,smax):
                ss=s-smin
                sang_set=float(s)
                #print (tau_set, high_set,s)
                # 5/4/2016
                change_data(fin,tau_set,ref_set,high_set,sang_set,scale)
                # 5/172016
                #out=subprocess.check_output("cat temp | sixs2",shell=True)
                out=subprocess.check_output("cat temp | sixsV2.2",shell=True)
                read_out(out,check)
                g.write('******** '+str(i)+' '+str(j)+' '+str(ss)+' ********\n')
                print ('******** '+str(i)+' '+str(j)+' '+str(ss)+' ********')
                g.write(' '+str(tau_set)+' '+str(high_set)+' '+str(ref_set)+' '+str(sang_set)+'\n')
                line='{0: .2f} {1: .2f} {2: .2f} {3: .2f}'.format(solar,path_rad,back_rad,pixel_rad)
                line=line+'\n'
                g.write(line)
                line='{0: .2f} {1: .2f} {2: .2f}'.format(dir_irad,sky_irad,env_irad)
                line=line+'\n'
                g.write(line)
                line='{0: .5f} {1: .5f} {2: .5f} {3: .5f}'.format(sph_alb,tau_rayl,tau_aero,tau_minor)
                line=line+'\n'
                g.write(line)
    g.close()


