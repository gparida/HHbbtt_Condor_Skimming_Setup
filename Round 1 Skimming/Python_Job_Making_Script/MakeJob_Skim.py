#!/usr/bin/env python
#Essentially used when I want to skim multiple root files in a single job belonging to a background and then hadd them together
import os, sys,  imp, re, pprint, string
from optparse import OptionParser

# cms specific
import FWCore.ParameterSet.Config as cms

import time
import datetime
import os
import sys
from optparse import OptionParser

MYDIR=os.getcwd()
print MYDIR

background_names =[]
counter = 0
file = open("input_path.txt", 'r')
input_list=file.readlines()
input_path=[]
file.close()

for line in input_list:
	 input_path.append(line.strip())
	 line = line.strip()
	 background_names.append(line.split('/')[-1])
	 counter=counter+1

print background_names


#os.rmdir(MYDIR+'/Jobs')
os.system('rm -rf Jobs')
os.system('mkdir Jobs')
#os.system('rmdir Ganesh')



for i in range(len(background_names)):

	jobDir = MYDIR+'/Jobs/%s/'%str(background_names[i])
	os.system('mkdir %s'%jobDir)

	tmp_jobname="sub_%s.sh"%(str(background_names[i]))
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
	tmp_job.write("python runFile_skim_test_gp.py %s %s\n"%(str(input_path[i]),str(background_names[i]+"_skim_hadd_all.root")))
	tmp_job.write("xrdcp %s root://cmsxrootd.hep.wisc.edu//store/user/parida/HHbbtt_Background_Files/Round_1_Skim_Aug_3/.\n"%(str(background_names[i])+"_skim_hadd_all.root"))
	tmp_job.write("echo 'Job Completed Succesfully'")
	tmp_job.write("rm *.root\n")
	tmp_job.close()

	tmp_job.write("""#!/bin/sh

		 ulimit -S
		 source /cvmfs/cms.cern.ch/cmsset_default.sh
		 scramv1 project CMSSW CMSSW_10_6_25
		 cp -R PhysicsTools  CMSSW_10_6_25/src
		 cd CMSSW_10_6_25/src/PhysicsTools/NanoAODTools
		 eval `scramv1 runtime -sh`
		 scram b
		 cd Analysis""")

					 
	tmp_job.write("python runFile_skim_test_gp.py %s %s\n"%(str(input_path[i]),str(background_names[i]+"_skim_hadd_all.root")))
	tmp_job.write("xrdcp %s root://cmsxrootd.hep.wisc.edu//store/user/parida/HHbbtt_Background_Files/Round_1_Skim_Aug_3/.\n"%(str(background_names[i])+"_skim_hadd_all.root"))
	tmp_job.write("""echo 'Job Completed Succesfully
					 rm *.root""")

	os.system('chmod +x %s'%(jobDir+tmp_jobname))
	sub_total = open(jobDir+"condor_submit.jobb",'w')
	sub_total.write("x509userproxy = /tmp/x509up_u10104\n")
	sub_total.write("universe = vanilla\n")
	sub_total.write("Executable = sub_%s.sh\n"%(str(background_names[i])))
	sub_total.write("ShouldTransferFiles  = Yes\n")
	#sub_total.write("ShouldTransferFiles  = Yes\n")
	sub_total.write("requirements = HAS_CMS_HDFS\n")
	sub_total.write("+IsFastQueueJob      = True\n")
	sub_total.write("getenv               = True\n")
	sub_total.write("request_memory       = 8G\n")
	sub_total.write("request_disk         = 20G\n")
	sub_total.write("Transfer_Input_Files = /nfs_scratch/parida/Physics_Tools_NanoAOD_Tools_HHbbtt/Aug_1_test/CMSSW_10_6_25/src/PhysicsTools\n")
	sub_total.write("output               = $(Cluster)_$(Process)_skim.out\n")
	sub_total.write("error                = $(Cluster)_$(Process)_skim.err\n")
	sub_total.write("Log                  = $(Cluster)_$(Process)_skim.log\n")
	sub_total.write("Queue\n")
	sub_total.close()
	




