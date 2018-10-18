#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2018-05-24 10:33
# * Last modified : 2018-05-25 00:28
# * Filename      : logParsing.py
# * Description   :
'''

	add a function about generating log sequences
'''
# **********************************************************

#In this demo, the rawlog.log file is the HDFS data set logs.
#If you want to test on other data sets or using other parsers, please modify the parameters in this file or in the parser source file

from LogSig import *

RawLogPath = './'
RawLogFile = 'BGL_2k.log'
OutputPath = './'+RawLogFile[:-4]+'_template_results/'
seq_file='seq_file.csv'
#Note: you need to set some other parameters when you try other parsers or data sets
#For example, the structured columns "removeCol" (e.g., timestamp column) that will be removed before parsing. For each data set, the structure columns are different. Wrong removeCol may result in wrong parsing results.
#All parameter setting in our experiments are attached as comments.
para=Para(path=RawLogPath, logname=RawLogFile, savePath=OutputPath)

myparser=LogSig(para)
time=myparser.mainProcess()

print ('The running time of LogSig is', time)

#generate total log sequence
import os

input_line=0
output_line=0
total_temp=0
temp_index_dir={} # a dictionary for 'template_num' : 'index in log seq'
with open(RawLogPath+RawLogFile) as IN:
    for line in IN:
        input_line+=1


for a,b,filenames in os.walk(OutputPath):
	for filename in filenames:
            if 'template' in filename:
                cur_temp=filename[8:][:-4]
                print cur_temp
                total_temp+=1
                temp_index_dir[cur_temp]=set()
                with open(OutputPath+filename) as IN:
                    for line in IN:
                        temp_index_dir[cur_temp].add(int(line.strip()))
                        output_line+=1

f=file(OutputPath+seq_file,'w')
for i in range(input_line):
    cur_i=i+1
    for temp in range(total_temp):
        cur_temp=str(temp+1)
        if cur_i in temp_index_dir[cur_temp]:
            #the template index in loglizer is begin from 0 !!!!
            f.writelines(str(temp)+'\n')
            break

print '# of input:',input_line
print '# of output:',output_line


#Parameters

#IPLoM
# =====For BGL=====
# 	ct = 0.4
# 	lowerBound = 0.01
# 	removeCol = [0,1,2,3,4,5,6,7,8]
#   regL = ['core\.[0-9]*']
#
# =====For HPC=====
# 	ct = 0.175
# 	lowerBound = 0.25
# 	removeCol = [0]
#   regL = ['([0-9]+\.){3}[0-9]']

# =====For HDFS=====
# 	ct = 0.35
# 	lowerBound = 0.25
# 	removeCol = [0,1,2,3,4]
#   regL = ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
#
# =====For Zookeeper=====
# 	ct = 0.4
# 	lowerBound = 0.7
# 	removeCol = [0,1,2,3,4,5]
#   regL = ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)']
#
# =====For Proxifier=====
# 	ct = 0.6
# 	lowerBound = 0.25
# 	removeCol = [0,1,3,4]
#   regL = []

#LogSig
#**********************PARAMETERS SETTING**************************************************
# Replace the parameters of def __init__ with the following ones according to the dataset.
# Please be noted that part of the codes in function termpairGene need to be altered according to the dataset
#******************************************************************************************
# =====For BGL=====
# (self,path='../Data/2kBGL/',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6,7,8,9],regular=True,
# rex=['core\.[0-9]*'],savePath='./results_2kBGL/',saveFileName='template',groupNum=100):# line 66,change the regular expression replacement code
# =====For Proxifier=====
# (self,path='../Data/2kProxifier/',logname='rawlog.log',removable=True,removeCol=[0,1,2,4,5],regular=True,
# rex=[''],savePath='./results_2kProxifier/',saveFileName='template',groupNum=6):
# =====For Zookeeper=====
# (self,path='../Data/2kZookeeper/',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6],regular=True,
# rex=['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results_2kZookeeper/',saveFileName='template',groupNum=46):
# =====For HDFS=====
# (self,path='../Data/2kHDFS/',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5],regular=True,
# rex=['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results_2kHDFS/',saveFileName='template',groupNum=14):
# =====For HPC=====
# (self,path='../Data/2kHPC/',logname='rawlog.log',removable=True,removeCol=[0,1],regular=True,
# rex=['([0-9]+\.){3}[0-9]'],savePath='./results_2kHPC/',saveFileName='template',groupNum=51):# line 67,change the regular expression replacement code
#******************************************************************************************

#LKE
#**********************PARAMETERS SETTING**************************************************
# Replace the parameters of def __init__ with the following ones according to the dataset.
# Please be noted that part of the codes in function termpairGene need to be altered according to the dataset
#******************************************************************************************
# =====For BGL=====
# (self,path='../Sca/',dataName='Sca_BGL600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6,7,8,9],threshold2=5,regular=True,
# rex=['core\.[0-9]*'],savePath='./results/',saveFileName='template'):# line 67,change the regular expression replacement code
# =====For Proxifier=====
# (self,path='../Sca/',dataName='Sca_Proxifier600',logname='rawlog.log',removable=True,removeCol=[0,1,2,4,5],regular=True,threshold2=2,
# rex=[''],savePath='./results/',saveFileName='template'):
# =====For Zookeeper=====
# (self,path='../Sca/',dataName='Sca_Zookeeper600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5,6],threshold2=2,regular=True,
# rex=['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results/',saveFileName='template'):
# =====For HDFS=====
# (self,path='../Sca/',dataName='Sca_SOSP600',logname='rawlog.log',removable=True,removeCol=[0,1,2,3,4,5],threshold2=3,regular=True,
# rex=['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],savePath='./results/',saveFileName='template'):
# =====For HPC=====
# (self,path='../Sca/',dataName='Sca_HPC600',logname='rawlog.log',removable=True,removeCol=[0,1],threshold2=4,regular=True,
# rex=['([0-9]+\.){3}[0-9]'],savePath='./results/',saveFileName='template'):# line 67,change the regular expression replacement code
#******************************************************************************************

#SLCT
#For SOSP: support is 12,False
#For HPC: support is 49, True
#For BGL: support is 5, True
#For Proxifier: support is 29, True
#For Zookeeper: support is 9, True
