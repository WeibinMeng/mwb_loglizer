import os
import time
log_path='./BGL_2k.log'
seq_path='./seq_file.csv'

f=file('log_seqence.txt','w')
with open(seq_path) as seq_list:
	with open(log_path) as IN:
		for tag,line in zip(seq_list,IN):
			tag=tag.strip()
			l=line.strip().split()
			timeArray = time.strptime(l[4][:-7], "%Y-%m-%d-%H.%M.%S")
			timeStamp = int(time.mktime(timeArray))
			print timeStamp,tag
			f.writelines(str(timeStamp)+' '+str(tag)+'\n')
