#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2018-09-03 14:51
# * Last modified : 2018-09-03 14:51
# * Filename      : data_loader.py
# * Description   : 
'''
'''
# **********************************************************
 
#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Shilin He'

import pandas as pd
import os
import numpy as np


def hdfs_data_loader(para):
	""" load the log sequence matrix and labels from the file path.

	Args:
	--------
	para: the parameters dictionary

	Returns:
	--------
	raw_data:  log sequences matrix
	label_data: labels matrix
	"""
	file_path = para['path'] + para['log_seq_file_name']
	label_path = para['path'] + para['label_file_name']
	# load log sequence matrix
	pre_df = pd.read_csv(file_path, nrows=1, header=None, delimiter=r'\s+')
	columns = pre_df.columns.tolist()
	# remove the last column of block name
	use_cols = columns[:-1]
	data_df = pd.read_csv(file_path, delimiter=r'\s+', header=None, usecols =use_cols, dtype =int)
	raw_data = data_df.as_matrix()
	# load lables
	label_df = pd.read_csv(label_path, delimiter=r'\s+', header=None, usecols = [0], dtype =int) # usecols must be a list
	label_data = label_df.as_matrix()
	print("The raw data shape is {} and label shape is {}".format(raw_data.shape, label_data.shape))
	assert raw_data.shape[0] == label_data.shape[0]
	print('The number of anomaly instances is %d' % sum(label_data))
	return raw_data, label_data


def bgl_data_loader(para):
	""" load the logs and the log_event_mapping from the file path.

	Args:
	--------
	para: the parameters dictionary

	Returns:
	--------
	raw_data: list of (label, time)
	event_mapping_data: a list of event index, where each row index indicates a corresponding log
	"""
	file_path = para['path'] + para['log_file_name']
	event_mapping_path = para['path'] + para['log_event_mapping']
	# load data #names:用于结果的列名列表，如果数据文件中没有列标题行，就需要执行header=None
	data_df = pd.read_csv(file_path, delimiter=r'\s+', header=None, names = ['label','time'], usecols = para['select_column']) #, parse_dates = [1], date_parser=dateparse)
	# convert to date time format
	data_df['time'] = pd.to_datetime(data_df['time'], format="%Y-%m-%d-%H.%M.%S.%f")
	# calculate the time interval since the start time
	data_df['seconds_since'] = (data_df['time']-data_df['time'][0]).dt.total_seconds().astype(int)
	# get the label for each log
	data_df['label'] = (data_df['label'] != '-').astype(int)
	raw_data = data_df[['label','seconds_since']].as_matrix()

	# load the event mapping list
	event_mapping = pd.read_csv(event_mapping_path, delimiter=r'\s+', header=None, usecols = [0], dtype =int)
	event_mapping_data = event_mapping.as_matrix()
	print("The raw data shape is {} and label shape is {}".format(raw_data.shape, event_mapping_data.shape))
	assert raw_data.shape[0] == event_mapping_data.shape[0]
	print('The number of anomaly logs is %d, but it requires further processing' % sum(raw_data[:, 0]))
	return raw_data, event_mapping_data





def new_data_loader(para,test_flag=0):
	""" load the logs and the log_event_mapping from the file path.
	 按照bgl的函数改的，不读取label了
	Args:
	--------
	para: the parameters dictionary

	Returns:
	--------
	raw_time: list of (time)
	event_mapping_data: a list of event index, where each row index indicates a corresponding log
	"""
	log_seq_file='train_log_seq_file'
	if test_flag==1:
		log_seq_file='test_log_seq_file'
		
	file_path = para['path'] + para[log_seq_file]
	event_mapping_path = para['path'] + para[log_seq_file]
	# load data #names:用于结果的列名列表，如果数据文件中没有列标题行，就需要执行header=None
	data_df = pd.read_csv(file_path, delimiter=r'\s+', header=None, names = ['time','tag'], usecols = [0,1]) #, parse_dates = [1], date_parser=dateparse)
	# # convert to date time format
	# data_df['time'] = pd.to_datetime(data_df['time'], format="%Y-%m-%d-%H.%M.%S.%f")
	# calculate the time interval since the start time
	data_df['time']=data_df['time'].astype(int)
	data_df['seconds_since'] = (data_df['time']-data_df['time'][0])
	# print 'ssss'

	# get the label for each log
	# data_df['label'] = (data_df['label'] != '-').astype(int)
	# raw_data = data_df[['label','seconds_since']].as_matrix()
	raw_time = data_df[['seconds_since']].as_matrix()

	# load the event mapping list
	event_mapping = pd.read_csv(event_mapping_path, delimiter=r'\s+', header=None, usecols = [0], dtype =int)
	event_mapping_data = data_df['tag'].as_matrix()
	print("The raw data shape is {}".format(raw_time.shape))
	assert raw_time.shape[0] == event_mapping_data.shape[0]
	# print('The number of anomaly logs is %d, but it requires further processing' % sum(raw_time[:, 0]))
	return raw_time, event_mapping_data


def new_preprocess_data(para, raw_data, event_mapping_data,test_flag=0):
	""" split logs into sliding windows, built an event count matrix and get the corresponding label
		
		根据bgl函数改写，本函数中没有label
		滑动窗口，每个窗口内的日志数量不一定相等
	Args:
	--------
	para: the parameters dictionary
	raw_data: list of (label, time)
	event_mapping_data: a list of event index, where each row index indicates a corresponding log

	Returns:
	--------
	event_count_matrix: event count matrix, where each row is an instance (log sequence vector)
	labels: a list of labels, 1 represents anomaly
	"""

	# create the directory for saving the sliding windows (start_index, end_index), which can be directly loaded in future running
	
	save_path='train_windows'
	if test_flag==1:
		save_path='test_windows'

	if not os.path.exists(para[save_path]):
		os.mkdir(para[save_path])
	log_size = raw_data.shape[0]
	sliding_file_path = para[save_path]+'sliding_'+str(para['window_size'])+'h_'+str(para['step_size'])+'h.csv'

	#=================divide into sliding windows=============#
	
	#start_end_index_list中每个tuple是每个窗口中元素的start_index跟end_index
	#其中 start是开始index，end是窗口结束的下一个index，end_index不属于本窗口，例如7~8表示7在窗口内，8~8表示该窗口没有日志
	start_end_index_list = [] # list of tuples, tuple contains two number, which represent the start and end of sliding time window
	time_data = raw_data[:,0]
	if True:
	# if not os.path.exists(sliding_file_path):
		# split into sliding window
		start_time = time_data[0]
		start_index = 0
		end_index = 0
		time_list = []
		# get the first start, end index, end time 通过这段代码，获得时间窗口的大小
		for cur_time in time_data:
			if  cur_time < start_time + para['window_size']*3600:
				end_index += 1
				end_time = cur_time #end_index不属于本窗口了，应该是属于下一个窗口
			else:
				start_end_pair=tuple((start_index,end_index))
				start_end_index_list.append(start_end_pair)
				break

		# move the start and end index until next sliding window
		while end_index < log_size:
			start_time = start_time + para['step_size']*3600
			end_time = end_time + para['step_size']*3600
			for i in range(start_index,end_index):
				if time_data[i] < start_time:
					i+=1
				else:
					break
			for j in range(end_index, log_size):
				if time_data[j] < end_time:
					j+=1
				else:
					break
			start_index = i
			end_index = j
			start_end_pair = tuple((start_index, end_index))
			start_end_index_list.append(start_end_pair)
			time_list.append((start_time,end_time))
		inst_number = len(start_end_index_list)
		print('there are %d instances (sliding windows) in this dataset\n'%inst_number)
		np.savetxt(sliding_file_path,start_end_index_list,delimiter=',',fmt='%d')
	else:
		print('Loading start_end_index_list from file')
		start_end_index_list = pd.read_csv(sliding_file_path, header=None).as_matrix()
		inst_number = len(start_end_index_list)
		print('there are %d instances (sliding windows) in this dataset' % inst_number)

	# get all the log indexes in each time window by ranging from start_index to end_index
	expanded_indexes_list=[] #list[list]，保存了每个时间窗口的sequence
	for t in range(inst_number): #时间窗口数量
		index_list = []
		expanded_indexes_list.append(index_list)
	for i in range(inst_number):
		start_index = start_end_index_list[i][0]
		end_index = start_end_index_list[i][1]
		for l in range(start_index, end_index):
			expanded_indexes_list[i].append(l)

	
	# event_mapping_data = [row[0] for row in event_mapping_data]
	event_num = len(list(set(event_mapping_data)))
	print('There are %d log events'%event_num)

	#=================get labels and event count of each sliding window =============#
	#对于bgl日志，只要该窗口内存在一条异常日志，就将该窗口当做是异常窗口。
	# labels = [] #labels是针对每一个时间窗口
	#event_count_matrix 是构建出的特征矩阵，每行是一个时间窗口，每列是每个模板的计数，即framework里的第三步
	event_count_matrix = np.zeros((inst_number,event_num))#(时间窗口数量,模板数量)
	for j in range(inst_number):
		# label = 0   #0 represent success, 1 represent failure
		for k in expanded_indexes_list[j]: #expanded_indexes_list保存了每个时间窗口的sequence，每个窗口一个List
			event_index = event_mapping_data[k]
			event_count_matrix[j, event_index] += 1
			# # if label_data[k]:
			# 	label = 1
			# 	continue
		# labels.append(label)
	# assert inst_number == len(labels)
	# print("Among all instances, %d are anomalies"%sum(labels))
	# assert event_count_matrix.shape[0] == len(labels)
	return event_count_matrix,time_list




def bgl_preprocess_data(para, raw_data, event_mapping_data):
	""" split logs into sliding windows, built an event count matrix and get the corresponding label
		滑动窗口，每个窗口内的日志数量不一定相等
	Args:
	--------
	para: the parameters dictionary
	raw_data: list of (label, time)
	event_mapping_data: a list of event index, where each row index indicates a corresponding log

	Returns:
	--------
	event_count_matrix: event count matrix, where each row is an instance (log sequence vector)
	labels: a list of labels, 1 represents anomaly
	"""

	# create the directory for saving the sliding windows (start_index, end_index), which can be directly loaded in future running
	time_list = [] 
	if not os.path.exists(para['save_path']):
		os.mkdir(para['save_path'])
	log_size = raw_data.shape[0]
	sliding_file_path = para['save_path']+'sliding_'+str(para['window_size'])+'h_'+str(para['step_size'])+'h.csv'

	#=================divide into sliding windows=============#
	
	#start_end_index_list中每个tuple是每个窗口中元素的start_index跟end_index
	#其中 start是开始index，end是窗口结束的下一个index，end_index不属于本窗口，例如7~8表示7在窗口内，8~8表示该窗口没有日志
	start_end_index_list = [] # list of tuples, tuple contains two number, which represent the start and end of sliding time window
	label_data, time_data = raw_data[:,0], raw_data[:, 1]
	if True:
	# if not os.path.exists(sliding_file_path):
		# split into sliding window
		start_time = time_data[0]
		start_index = 0
		end_index = 0

		# get the first start, end index, end time 通过这段代码，获得时间窗口的大小
		for cur_time in time_data:
			if  cur_time < start_time + para['window_size']*3600:
				end_index += 1
				end_time = cur_time #end_index不属于本窗口了，应该是属于下一个窗口
			else:
				start_end_pair=tuple((start_index,end_index))
				start_end_index_list.append(start_end_pair)
				break

		# move the start and end index until next sliding window
		while end_index < log_size:
			start_time = start_time + para['step_size']*3600
			end_time = end_time + para['step_size']*3600
			time_list.append((start_time,end_time))
			for i in range(start_index,end_index):
				if time_data[i] < start_time:
					i+=1
				else:
					break
			for j in range(end_index, log_size):
				if time_data[j] < end_time:
					j+=1
				else:
					break
			start_index = i
			end_index = j
			start_end_pair = tuple((start_index, end_index))
			start_end_index_list.append(start_end_pair)
		inst_number = len(start_end_index_list)
		print('there are %d instances (sliding windows) in this dataset\n'%inst_number)
		np.savetxt(sliding_file_path,start_end_index_list,delimiter=',',fmt='%d')
	else:
		print('Loading start_end_index_list from file')
		start_end_index_list = pd.read_csv(sliding_file_path, header=None).as_matrix()
		inst_number = len(start_end_index_list)
		print('there are %d instances (sliding windows) in this dataset' % inst_number)

	# get all the log indexes in each time window by ranging from start_index to end_index
	expanded_indexes_list=[] #list[list]，保存了每个时间窗口的sequence
	for t in range(inst_number): #时间窗口数量
		index_list = []
		expanded_indexes_list.append(index_list)
	for i in range(inst_number):
		start_index = start_end_index_list[i][0]
		end_index = start_end_index_list[i][1]
		for l in range(start_index, end_index):
			expanded_indexes_list[i].append(l)

	event_mapping_data = [row[0] for row in event_mapping_data]
	event_num = len(list(set(event_mapping_data)))
	print('There are %d log events'%event_num)

	#=================get labels and event count of each sliding window =============#
	#对于bgl日志，只要该窗口内存在一条异常日志，就将该窗口当做是异常窗口。
	labels = [] #labels是针对每一个时间窗口
	#event_count_matrix 是构建出的特征矩阵，每行是一个时间窗口，每列是每个模板的计数，即framework里的第三步
	event_count_matrix = np.zeros((inst_number,event_num))#(时间窗口数量,模板数量)
	for j in range(inst_number):
		label = 0   #0 represent success, 1 represent failure
		for k in expanded_indexes_list[j]: #expanded_indexes_list保存了每个时间窗口的sequence，每个窗口一个List
			event_index = event_mapping_data[k]
			event_count_matrix[j, event_index] += 1
			if label_data[k]:
				label = 1
				continue
		labels.append(label)
	assert inst_number == len(labels)
	print("Among all instances, %d are anomalies"%sum(labels))
	assert event_count_matrix.shape[0] == len(labels)
	return event_count_matrix, labels



