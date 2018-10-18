**本代码修改自 [https://github.com/logpai/loglizer](https://github.com/logpai/loglizer) ，原论文：[He S, Zhu J, He P, et al. Experience Report: System Log Analysis for Anomaly Detection[C]// IEEE, International Symposium on Software Reliability Engineering. IEEE, 2016:207-218.](https://ieeexplore.ieee.org/document/7774521)，我为了自己做实验做了些小的修改。**


# 日志异常检测的通用做法分为四步：
	1、日志收集 
	2、日志处理(模板化) 
	3、特征提取  
	4、异常检测
	
(我给出了2000条的样例日志序列，本身的异常特征可能不太明显，因为有监督的准确率也不高。)

# 每个文件的作用：
## logParsing.py:
*	功能：提取日志模板，并且将原日志文件转换成模板序列(log sequence)
* 输入：原始的日志，每一条日志一行，例如 “1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.675872 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected” （即BGL_2k.log文件）
* 输出：1.日志模板文件
	     2.log sequence (tag范围是从0开始，range(template_bnum))

## classifiers_bgl.py:
* 功能：有监督的异常检测，基于sklearn工具包，分别实现了决策树，SVM和逻辑回归异常检测。
* 输入：
	1. 原始日志文件（即BGL_2k.log文件）
	2. 上一步得到的log sequence （即seq_file.csv文件）
	3. 标注，在这个程序中，标注是原始日志文件(BGL_2k.log)的第一列。这个标注是对每条日志做的标注，如果一个窗口内存在异常的日志，则认为这个窗口为异常。（文中：In BGL data, 348,460 log messages are labeled as failures, and a log sequence is marked as an anomaly if any failure logs exist in that sequence.）
	4. 其他数值型的参数
* 输出: precision recall fscore，查看具体哪个时间窗口有异常可以修改一下代码，目前没有展示。


## log_clustering_bgl.py:
   * 功能：实现了微软log clustering算法，通过日志来做异常检测。
   * 输入：
	   1. 原始日志文件（即BGL_2k.log文件）
	   2. 上一步得到的log sequence （即seq_file.csv文件）
	   3. 标注，在这个程序中，标注是原始日志文件(BGL_2k.log)的第一列。这个标注是对每条日志做的标注，如果一个窗口内存在异常的日志，则认为这个窗口为异常。（文中：In BGL data, 348,460 log messages are labeled as failures, and a log sequence is marked as an anomaly if any failure logs exist in that sequence.）
	   4. 其他数值型的参数
   * 输出: precision recall fscore，查看具体哪个时间窗口有异常可以修改一下代码，目前没有展示。

## PCA_bgl.py:
   * 功能：实现了通过PCA做日志异常检测的功能。
   * 输入：
      1. 原始日志文件（即BGL_2k.log文件）
	  2. 上一步得到的log sequence （即seq_file.csv文件）
	  3. 标注，在这个程序中，标注是原始日志文件(BGL_2k.log)的第一列。这个标注是对每条日志做的标注，如果一个窗口内存在异常的日志，则认为这个窗口为异常。（文中：In BGL data, 348,460 log messages are labeled as failures, and a log sequence is marked as an anomaly if any failure logs exist in that sequence.）
	4. 其他数值型的参数
  * 输出: precision recall fscore，查看具体哪个时间窗口有异常可以修改一下代码，目前没有展示。


## mining_invariants_bgl.py:
   * 功能：实现了ATC‘10的mining invariants。
   * 输入：
    1. 原始日志文件（即BGL_2k.log文件）
 	2. 上一步得到的log sequence （即seq_file.csv文件）
	3. 标注，在这个程序中，标注是原始日志文件(BGL_2k.log)的第一列。这个标注是对每条日志做的标注，如果一个窗口内存在异常的日志，则认为这个窗口为异常。（文中：In BGL data, 348,460 log messages are labeled as failures, and a log sequence is marked as an anomaly if any failure logs exist in that sequence.）
	4. 其他数值型的参数
* 输出: precision recall fscore，查看具体哪个时间窗口有异常可以修改一下代码，目前没有展示。	

## nolabel_mining_invariants.py:
 * 功能：我将mining invariants算法拆分成了train跟detect两部分，可以训练完之后，对实时数据做检测，并且可以输出每个时间窗口对应的检测结果
 * 输出：test数据的时间窗口的开始、结束时间 以及异常检测结果



# 个人看法
* classifiers_bgl.py :有监督学习  决策树、逻辑回归、SVM，速度最快
* log_clustering_bgl.py: 半监督？（需要有部分label作为输入），速度最慢
* PCA_bgl.py: 无监督，在给出的样例数据中，准确率为0....
* mining_invariants_bgl.py: 无监督、速度可以、准确率也可以

