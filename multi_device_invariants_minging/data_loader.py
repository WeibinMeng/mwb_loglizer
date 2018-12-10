# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pandas as pd
import os
import numpy as np


class DataLoader(object):
	def __init__(self, dataset_name):
		self.dataset_name = dataset_name
	def get_template_sequence(self):
		return None
	def get_log_time(self):
		return None
	def get_label(self):
		return None
	def __str__(self):
		return self.dataset_name


class BGLDataLoader(DataLoader):
	def __init__(self, log_file, log_template_file):
		super(BGLDataLoader, self).__init__('BGL')
		self.log_file = log_file
		self.log_template_file = log_template_file
		self.__read_data__()
	def __read_data__(self):
		data_df = pd.read_csv(self.log_file, delimiter=r'\s+', header=None, names=['label', 'time'], usecols=[0, 4])
		data_df['time'] = pd.to_datetime(data_df['time'], format="%Y-%m-%d-%H.%M.%S.%f")
		data_df['time_since'] = (data_df['time'] - data_df['time'][0]).dt.total_seconds().astype(int)
		data_df['label'] = (data_df['label'] != '-').astype(int)
		self.label = data_df[['label']].values.ravel()
		self.time_since = data_df[['time_since']].values.ravel()

		# load the event mapping list
		log_template_df = pd.read_csv(self.log_template_file, delimiter=r'\s+', header=None, dtype=int)
		self.template_sequence = log_template_df.values.ravel()

		print("The raw data shape is {} and label shape is {}".format(self.time_since.shape, self.template_sequence.shape))
		print('The number of anomaly logs is %d, but it requires further processing' % sum(self.label))

	def get_template_sequence(self):
		return self.template_sequence
	def get_log_time(self):
		return self.time_since
	def get_label(self):
		return self.label


class BizseerDataLoader(DataLoader):
	def __init__(self, log_template_file, label_file=None):
		super(BizseerDataLoader, self).__init__('Bizseer')
		self.log_template_file = log_template_file
		self.label_file = label_file
		self.__read_data__()
	def __read_data__(self):
		template_sequence = []
		time_since = []
		with open(self.log_template_file, 'r') as f:
			ltf = f.read().split('\n')[:-1]
		start_time = int(ltf[0].split(',')[0])
		self.start_time_ms = start_time
		for row in ltf:
			# print(row)
			splits = row.split(',')
			# start at 1
			template_sequence.append(int(splits[1]) - 1)
			time_since.append((int(splits[0]) - start_time) // 1000)
			# print((int(splits[0]) - start_time) // 1000, start_time)
			# print('')
		self.template_sequence = np.array(template_sequence)
		self.time_since = np.array(time_since)

		if self.label_file is not None:
			with open(self.label_file, 'r') as f:
				lf = f.read().split('\n')[:-1]
				self.labels = np.array(list(map(int, lf)), dtype=int)
		
		print(self.labels.shape, self.template_sequence.shape)
		assert(self.labels.shape[0] == self.template_sequence.shape[0])

	def get_template_sequence(self):
		return self.template_sequence
	def get_log_time(self):
		return self.time_since
	def get_label(self):
		return self.labels


def preprocess(para, time_data, event_mapping_data, label_data,event_num=0):
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
	if not os.path.exists(para['save_path']):
		os.mkdir(para['save_path'])
	log_size = time_data.shape[0]
	sliding_file_path = para['save_path']+'sliding_'+str(para['window_size'])+'h_'+str(para['step_size'])+'h.csv'

	#=================divide into sliding windows=============#
	
	#start_end_index_list中每个tuple是每个窗口中元素的start_index跟end_index
	#其中 start是开始index，end是窗口结束的下一个index，end_index不属于本窗口，例如7~8表示7在窗口内，8~8表示该窗口没有日志
	start_end_index_list = [] # list of tuples, tuple contains two number, which represent the start and end of sliding time window
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
		import time

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
			# start_time_s=time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(float(time_data[start_index])))
			# end_time_s=	time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(float(time_data[end_index])))
			# print('start_index,end_index',start_time_s,end_time_s)
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

	# event_num = len(list(set(event_mapping_data)))
	if event_num == 0:
		event_num = np.max(event_mapping_data) + 1
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

def nolabel_preprocess(para, time_data, event_mapping_data,event_num=0):
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
	if not os.path.exists(para['save_path']):
		os.mkdir(para['save_path'])
	log_size = time_data.shape[0]
	sliding_file_path = para['save_path']+'sliding_'+str(para['window_size'])+'h_'+str(para['step_size'])+'h.csv'

	#=================divide into sliding windows=============#
	
	#start_end_index_list中每个tuple是每个窗口中元素的start_index跟end_index
	#其中 start是开始index，end是窗口结束的下一个index，end_index不属于本窗口，例如7~8表示7在窗口内，8~8表示该窗口没有日志
	start_end_index_list = [] # list of tuples, tuple contains two number, which represent the start and end of sliding time window
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
		import time

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
			# start_time_s=time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(float(time_data[start_index])))
			# end_time_s=	time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(float(time_data[end_index])))
			# print('start_index,end_index',start_time_s,end_time_s)
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

	# event_num = len(list(set(event_mapping_data)))
	if event_num == 0:
		event_num = np.max(event_mapping_data) + 1
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
	
	return event_count_matrix

