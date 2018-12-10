#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2018-10-17 23:37
# * Last modified : 2018-10-22 14:41
# * Filename      : getWindowsTime.py
# * Description   :
'''
'''
# **********************************************************
import time
import datetime
import os

def getRawTime(windows_size,step_size,seq_file,prediction):
    time_list = []
    with open(seq_file) as IN:
        for line in IN:
            l = line.strip().split()
            t = int(l[0])
            #print(t)
            time_list.append(t)

    start = time_list[0]
    end = time_list[-1]
    windows_len = int(end - start - 3600*windows_size) / (3600*step_size) + 1
    #print(windows_len)

    result_list = []
    with open(prediction) as IN:
        for line in IN:
            l = line.strip().split()
            t = int(l[0])
            result_list.append(t)
    f = open(prediction,'w')
    for i,r in enumerate(result_list):
        cur_start = float(start + i*step_size*3600)
        cur_end = float((cur_start)+windows_size*3600)
        cur_start_format = time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(cur_start))
        cur_end_format = time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(cur_end))
        f.writelines(str(cur_start_format)+' '+str(cur_end_format)+' '+str(r)+'\n')
    # os.remove(prediction)


def saveRawWinTime(para,seq_file,pred,output = 'rawWindowsResult.txt'):#windows_size,step_size,seq_file,prediction):
    windows_size = para['window_size']
    step_size = para['step_size']
    # output = para['rawWindowsResult']
    time_list = []
    with open(seq_file) as IN:
        for line in IN:
            l = line.strip().split(',')
            t = int(l[0][:-3])
            #print(t)
            time_list.append(t)

    start = time_list[0]
    end = time_list[-1]
    windows_len = int(end - start - 3600*windows_size) / (3600*step_size) + 1
    #print(windows_len)

    result_list = pred
    # with open(prediction) as IN:
    #     for line in IN:
    #         l = line.strip().split()
    #         t = int(l[0])
    #         result_list.append(t)
    f = open(output,'w')
    for i,r in enumerate(result_list):
        cur_start = float(start + i*step_size*3600)
        cur_end = float((cur_start)+windows_size*3600)
        cur_start_format = time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(cur_start))
        cur_end_format = time.strftime('%Y-%m-%d_%H:%M:%S',time.gmtime(cur_end))
        f.writelines(str(cur_start_format)+' '+str(cur_end_format)+' '+str(r)+'\n')


if __name__ =='__main__':
    windows_size = 3
    step_size = 1
    seq_file = 'log_seqence.txt'
    prediction = 'prediction.txt'
    output = 'new_prediction.txt'
    getRawTime(windows_size,step_size,seq_file,prediction)
