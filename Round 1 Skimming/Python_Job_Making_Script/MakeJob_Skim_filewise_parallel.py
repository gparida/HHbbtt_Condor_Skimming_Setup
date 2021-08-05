#!/usr/bin/env python
#Essentially used when I want to parallelize jobs per file, that is, run one root file per job.
#List of full paths of the files per background and output directory taken as input
import os, sys,  imp, re, pprint, string
from optparse import OptionParser

# cms specific
import FWCore.ParameterSet.Config as cms

import time
import datetime
import os
import sys

parser=OptionParser()
opts, args = parser.parse_args()

#parser.add_option("-l",dest="list",type="str",help="list of inputfiles with full path provided, the penultimate direcotry should be the Sample Name")
#parser.add_option("-o",dest="output",type="str",help="Path of Output_Files on hdfs starting from store/....")

MYDIR=os.getcwd()
print MYDIR

background_names =[]
rootfile_names=[]
counter = 0
file = open(str(args[0]), 'r')
input_list=file.readlines()
input_path=[]
file.close()

for line in input_list:
	 input_path.append(line.strip())
	 line = line.strip()
	 background_names.append(line.split('/')[-2])
	 rootfile_names.append((line.split('/')[-1]).split('.')[-2])
	 counter=counter+1


print(background_names)

##os.rmdir(MYDIR+'/Jobs')
os.system("rm -rf Jobs_%s"%str((background_names[0])))
os.system("mkdir Jobs_%s"%str(background_names[0]))
#os.mkdir(MYDIR,background_names[0])
#os.system('rm -rf Jobs_1')
#os.system('mkdir Jobs_1')
##os.system('rmdir Ganesh')
#


for i in range(len(rootfile_names)):

	jobDir = MYDIR+'/Jobs_%s/%s/'%(str(background_names[i]),str(background_names[i])+"_"+str(rootfile_names[i]))
	os.system('mkdir %s'%jobDir)

	tmp_jobname="sub_%s.sh"%(str(background_names[i])+"_"+str(rootfile_names[i]))
	tmp_job=open(jobDir+tmp_jobname,'w')
	tmp_job.write("#!/bin/sh\n")
	tmp_job.write("ulimit -S\n")
	tmp_job.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
	tmp_job.write("scramv1 project CMSSW CMSSW_10_6_25\n")
	tmp_job.write("cp -R PhysicsTools  CMSSW_10_6_25/src\n")
	tmp_job.write("cd CMSSW_10_6_25/src/PhysicsTools/NanoAODTools\n")
	tmp_job.write("eval `scramv1 runtime -sh`\n")
	tmp_job.write("scram b\n")
	tmp_job.write("cd Analysis\n")
	tmp_job.write("python runFile_skim_gp_filewise_parallel.py %s\n"%(str(input_path[i])))
	tmp_job.write("xrdcp %s root://cmsxrootd.hep.wisc.edu//%s/.\n"%(str(rootfile_names[i])+"_condor_skim.root",str(args[1])))
	tmp_job.write("echo 'Job Completed Succesfully'\n")
	tmp_job.write("rm *.root\n")
	tmp_job.close()
	os.system('chmod +x %s'%(jobDir+tmp_jobname))
#
#	tmp_job.write("""#!/bin/sh
					 
#
#		 ulimit -S
#		 source /cvmfs/cms.cern.ch/cmsset_default.sh
#		 scramv1 project CMSSW CMSSW_10_6_25
#		 cp -R PhysicsTools  CMSSW_10_6_25/src
#		 cd CMSSW_10_6_25/src/PhysicsTools/NanoAODTools
#		 eval `scramv1 runtime -sh`
#		 scram b
#		 cd Analysis""")
#
#					 
#	tmp_job.write("python runFile_skim_test_gp.py %s %s\n"%(str(input_path[i]),str(background_names[i]+"_skim_hadd_all.root")))
#	tmp_job.write("xrdcp %s root://cmsxrootd.hep.wisc.edu//store/user/parida/HHbbtt_Background_Files/Round_1_Skim_Aug_3/.\n"%(str(background_names[i])+"_skim_hadd_all.root"))
#	tmp_job.write("""echo 'Job Completed Succesfully
#					 rm *.root""")
#
#	os.system('chmod +x %s'%(jobDir+tmp_jobname))
#	sub_total = open(jobDir+"condor_submit.jobb",'w')
#	sub_total.write("x509userproxy = /tmp/x509up_u10104\n")
#	sub_total.write("universe = vanilla\n")
#	sub_total.write("Executable = sub_%s.sh\n"%(str(background_names[i])))
#	sub_total.write("ShouldTransferFiles  = Yes\n")
#	#sub_total.write("ShouldTransferFiles  = Yes\n")
#	sub_total.write("requirements = HAS_CMS_HDFS\n")
#	sub_total.write("+IsFastQueueJob      = True\n")
#	sub_total.write("getenv               = True\n")
#	sub_total.write("request_memory       = 8G\n")
#	sub_total.write("request_disk         = 20G\n")
#	sub_total.write("Transfer_Input_Files = /nfs_scratch/parida/Physics_Tools_NanoAOD_Tools_HHbbtt/Aug_1_test/CMSSW_10_6_25/src/PhysicsTools\n")
#	sub_total.write("output               = $(Cluster)_$(Process)_skim.out\n")
#	sub_total.write("error                = $(Cluster)_$(Process)_skim.err\n")
#	sub_total.write("Log                  = $(Cluster)_$(Process)_skim.log\n")
#	sub_total.write("Queue\n")
#	sub_total.close()
	
sub_total = open("condor_%s.jobb"%str(background_names[0]),'w')
sub_total.write("x509userproxy = /tmp/x509up_u10104\n")
sub_total.write("universe = vanilla\n")
sub_total.write("executable = $(filename)\n")
sub_total.write("ShouldTransferFiles  = Yes\n")
sub_total.write("requirements = HAS_CMS_HDFS\n")
sub_total.write("+IsFastQueueJob      = True\n")
sub_total.write("getenv               = True\n")
sub_total.write("request_memory       = 2G\n")
sub_total.write("request_disk         = 3G\n")
sub_total.write("Transfer_Input_Files = /nfs_scratch/parida/Physics_Tools_NanoAOD_Tools_HHbbtt/Aug_1_test/CMSSW_10_6_25/src/PhysicsTools\n")
sub_total.write("output               = $Fp(filename)skim.out\n")
sub_total.write("error                = $Fp(filename)skim.err\n")
sub_total.write("Log                  = $Fp(filename)skim.log\n")
sub_total.write("queue filename matching ("+MYDIR+"/Jobs_%s/*/*.sh)\n"%str(background_names[0]))






