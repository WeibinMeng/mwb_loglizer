#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2018-10-22 13:30
# * Last modified : 2018-12-10 12:45
# * Filename      : main_for_invariants_mining.py
# * Description   :
'''
'''
# **********************************************************
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import data_loader as data_loader
import algorithms as alg
import argparse
import evaluation as ev
import os
import numpy as np
from getWindowsTime import saveRawWinTime
if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--input_type', help='single seq or multi seq？', type=str, default='single')
        parser.add_argument('--dir', help='log seq dir.', type=str, default='./dir')
        parser.add_argument('--template', help='Template extraction result file.', type=str, default='log_sequence.csv')
        parser.add_argument('--label', help='Label file.', type=str, default='test.label')
        parser.add_argument('--window_size', help='Slide window size, unit: hour.', type=float, default=3)
        parser.add_argument('--step_size', help='Slide window step, unit: hour.', type=float, default=1)
        parser.add_argument('--epsilon', type=float, default=2)
        parser.add_argument('--threshold', type=float, default=0.98)
        parser.add_argument('--suffix', type=str, default='csv')
        parser.add_argument('--event_num', type=int, default=200)
        parser.add_argument('--result', type=str, default='results/')
        args = parser.parse_args()

        para = {
        'save_path': './time_windows/', # dir for saving sliding window data files to avoid splitting
        'window_size':args.window_size,                            # time window (unit: hour)
        'step_size': args.step_size,                             # step size (unit: hour)
        'epsilon':args.epsilon,                              # threshold for the step of estimating invariant space
        'threshold':args.threshold,                           # percentage of vector Xj in matrix satisfies the condition that |Xj*Vi|<epsilon
        'scale_list':[1,2,3],					    # list used to sacle the theta of float into integer
        'rawWindowsResult': 'rawWindowsResult.txt'
        }


        if args.input_type == 'single':
            #单个文件输入
            dl = data_loader.BizseerDataLoader(args.template, args.label)
            mi = alg.MiningInvariants()
            time_since, label, template_sequence = dl.get_log_time(), dl.get_label(), dl.get_template_sequence()
            event_count_matrix, labels = data_loader.preprocess(para, time_since, template_sequence, label)
            # print((event_count_matrix.shape))#np.concatenate
            mi.fit(event_count_matrix, para)
            pred, analyze_result = mi.predict_for_analyze(event_count_matrix, para, dl.start_time_ms)
            import json
            with open('anomaly.json', 'w') as f:
                f.write(json.dumps(analyze_result))
            saveRawWinTime(para,args.template,pred)
            # ev.evaluate(labels, pred)#如果全pred是0，可能会导致函数以为只有一个类别，报错，需要添加一个非0
        else:
            #多个文件输入
            suffix = args.suffix
            event_count_matrix_list = []
            filename_list = []
            event_count_matrix = ''
            mi = alg.MiningInvariants()
            for a,b,filenames in os.walk(args.dir):
                filenames = [filename for filename in filenames if suffix in filename]
                for filename in filenames:
                    filename = filename.split('.')[0]
                    print(args.dir+'/'+filename)
                    dl = data_loader.BizseerDataLoader(args.dir+'/'+filename+'.'+suffix, args.dir+'/'+filename+'.label')
                    # mi = alg.MiningInvariants()
                    time_since, template_sequence = dl.get_log_time(), dl.get_template_sequence()
                    cur_event_count_matrix = data_loader.nolabel_preprocess(para, time_since, template_sequence,event_num=args.event_num)
                    # event_count_matrix_list.append(event_count_matrix)
                    if event_count_matrix == '':
                        event_count_matrix = cur_event_count_matrix
                    else:
                        event_count_matrix = np.concatenate([event_count_matrix, cur_event_count_matrix])
                    print(event_count_matrix.shape)
            print('starting mining~~~~~~~~')
            mi.fit(event_count_matrix, para)
            #输出检测结果
            for a,b,filenames in os.walk(args.dir):
                filenames = [filename for filename in filenames if suffix in filename]
                for filename in filenames:
                    filename = filename.split('.')[0]
                    print(args.dir+'/'+filename)
                    dl = data_loader.BizseerDataLoader(args.dir+'/'+filename+'.'+suffix, args.dir+'/'+filename+'.label')
                    time_since, template_sequence = dl.get_log_time(), dl.get_template_sequence()
                    cur_event_count_matrix = data_loader.nolabel_preprocess(para, time_since, template_sequence,event_num=args.event_num)
                    pred, analyze_result = mi.predict_for_analyze(cur_event_count_matrix, para, dl.start_time_ms)
                    saveRawWinTime(para, args.dir+'/'+filename+'.'+suffix,pred,args.results+filename+'_rawWindowResult.txt')

            print('test')
            # saveRawWinTime(para,args.template,pred)







