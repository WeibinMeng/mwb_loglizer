#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2018-10-22 11:18
# * Last modified : 2018-11-29 00:56
# * Filename      : convertLogSeq.py
# * Description   :
'''
    convert (timestamp logKey) into (timestamp,logKey,paramaterNum,p1,p2,...pn)
    从1开始,将多个log seq合并成一个template_set
'''
# **********************************************************
import os
input_dir = 'log_dir/' #原始seq文件
output_dir = 'dir/'	  #更新模板号后的seq文件
raw_to_new = {}
f_map = open('map.txt','w')
for a,b,filenames in os.walk(input_dir):
    for filename in filenames:
            if 'DS' in filename:
                continue
            # filename = '.'.join(filename.split(".")[:-1])+'.csv'
            seq_file = filename.split('.')[0]+'.csv'
            f = open(output_dir+seq_file,'w')
            label_file = filename.split('.')[0]+'.label'
            fl = open(output_dir+label_file, 'w')
            with open(input_dir+filename) as IN:
                for line in IN:
                    l = line.strip().split()
                    old_tag = l[1]
                    if old_tag not in raw_to_new:
                        raw_to_new[old_tag] = str(len(raw_to_new)+1) #模板号从1开始
                    new_tag = raw_to_new[old_tag]
                    f.writelines(l[0]+'000,'+new_tag+',0\n')
                    fl.writelines('0\n')
            f.close()

for k in raw_to_new:
    f_map.writelines(k+' '+raw_to_new[k]+'\n')

print('# of templates:',len(raw_to_new))




