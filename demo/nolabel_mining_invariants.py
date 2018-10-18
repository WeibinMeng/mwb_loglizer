#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2018-05-25 00:15
# * Last modified : 2018-09-03 15:08
# * Filename      : mining_invariants_bgl.py
# * Description   :
'''
  Changed from Shilin He (github: https://github.com/logpai/loglizer)
'''
# **********************************************************

import sys
sys.path.append('../')

from utils import data_loader as data_loader
from models import mining_invariants as mi
from getWindowsTime import getRawTime

path='./'
train_log_seq_file='log_seqence.txt'
test_log_seq_file='log_seqence.txt'
train_windows= 'train_time_windows/'
test_windows= 'test_time_windows/'
prediction_file='prediction.txt'

para = {
'path':'./', # directory for input data
'train_log_seq_file':train_log_seq_file,
'test_log_seq_file':test_log_seq_file,
# 'log_file_name':'BGL_2k.log', # filename for log data file
# 'log_event_mapping':'seq_file.csv', # filename for log-event mapping. A list of event index, where each row represents a log
'train_windows': train_windows, # dir for saving sliding window data files to avoid splitting
'test_windows':test_windows,
# 'select_column':[0,4], # select the corresponding columns (label and time) in the raw log file
'window_size':3,                            # time window (unit: hour)
'step_size': 1,                             # step size (unit: hour)
'epsilon':2.0,                              # threshold for the step of estimating invariant space
'threshold':0.98,                           # percentage of vector Xj in matrix satisfies the condition that |Xj*Vi|<epsilon
'scale_list':[1,2,3],					    # list used to sacle the theta of float into integer
'stop_invar_num':3,                          # stop if the invariant length is larger than stop_invar_num. None if not given
'prediction_file':prediction_file
}

if __name__ == '__main__':
	# data_loader.new_data_loader(para)
	#train_data
	since_time_train, event_mapping_data_train = data_loader.new_data_loader(para)
	event_count_matrix_train,time_list_train = data_loader.new_preprocess_data(para, since_time_train, event_mapping_data_train)
	#test_data
	since_time_test, event_mapping_data_test = data_loader.new_data_loader(para,test_flag=1)
	event_count_matrix_test,time_list_test = data_loader.new_preprocess_data(para, since_time_test, event_mapping_data_test,test_flag=1)

	r = mi.estimate_invar_spce(para, event_count_matrix_train)
	invar_dict = mi.invariant_search(para, event_count_matrix_train, r)
	mi.detect(para,event_count_matrix_test, invar_dict,time_list_test)
	# mi.evaluate(event_count_matrix, invar_dict, labels)
	getRawTime(para['window_size'],para['step_size'],test_log_seq_file,prediction_file)
