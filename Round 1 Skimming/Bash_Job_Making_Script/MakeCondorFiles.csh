#!/bin/sh

currentDir=${PWD}
outDir=${3}
#export CMSSW_RELEASE_BASE=/cvmfs/cms.cern.ch/slc6_amd64_gcc630/cms/cmssw/CMSSW_9_4_1/
export CMSSW_RELEASE_BASE=/cvmfs/cms.cern.ch/slc7_amd64_gcc630/cms/cmssw/CMSSW_10_6_25/
cat> $outDir/Job_${2}.sh<<EOF
#!/bin/sh
source /cvmfs/cms.cern.ch/cmsset_default.sh 
cd $CMSSW_RELEASE_BASE
eval `scramv1 runtime -sh`
cd \${_CONDOR_SCRATCH_DIR}
python ${1} 
ls
xrdcp hadd_test_post_proc.root root://cmsxrootd.hep.wisc.edu//store/user/parida/Skim_test_output/.
#cd PhysicsTools/NanoAODTools/scripts
#python PhysicsTools/NanoAODTools/scripts/haddnano.py out.root *.root 

EOF

chmod 775 $outDir/Job_${2}.sh
cat > $outDir/condor_${2}<<EOF
x509userproxy = /tmp/x509up_u10104
universe = vanilla
Executable = $outDir/Job_${2}.sh
Notification         = never
#WhenToTransferOutput = On_Exit
#ShouldTransferFiles  = yes
#Requirements = (TARGET.UidDomain == "hep.wisc.edu" && TARGET.HAS_CMS_HDFS && OpSysAndVer == "CENTOS7" && TARGET.Arch == "X86_64" && (MY.RequiresSharedFS=!=true || TARGET.HasAFS_OSG) && (TARGET.OSG_major =!= undefined || TARGET.IS_GLIDEIN=?=true) && IsSlowSlot=!=true)
requirements = HAS_CMS_HDFS
#on_exit_remove       = (ExitBySignal == FALSE && (ExitCode == 0 || ExitCode == 42 || NumJobStarts>3))
+IsFastQueueJob      = True
getenv               = True
request_memory       = 4G
request_disk         = 5G
#transfer_output_remaps = "out.root = out.root"

#OutputDestination = ${outdir}
#Initialdir = Out_${2}         
Transfer_Input_Files = ${currentDir}/${1} , ${currentDir}/skim_test_gp.py , ${currentDir}/keep_and_drop.txt , /nfs_scratch/parida/Physics_Tools_NanoAOD_Tools_HHbbtt/Aug_1_test/CMSSW_10_6_25/src/PhysicsTools 
#transfer_output_files = out.root
#transfer_output_remaps = "boostedTauReNano_2016_MC_cff-F6DC0DC3-C33C-7144-AA0B-B62F2B58352F_Condor_Skim_Done.root  = /hdfs/store/user/parida/Skim_test_output/out1.root; boostedTauReNano_2016_MC_cff-FEA06C3A-BA11-F44F-ADCD-C140C76E52CC_Condor_Skim_Done.root = /hdfs/store/user/parida/Skim_test_output/out2.root"

#transfer_output_remaps = "boostedTauReNano_2016_MC_*.root  = /hdfs/store/user/parida/Skim_test_output/*.root"

output               = $outDir/\$(Cluster)_\$(Process)_${2}.out
error                = $outDir/\$(Cluster)_\$(Process)_${2}.err
Log                  = $outDir/\$(Cluster)_\$(Process)_${2}.log
Queue
EOF

condor_submit $outDir/condor_${2}

