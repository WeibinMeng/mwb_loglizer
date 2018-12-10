####运行：
* 从1开始,将多个机器的template sequence合并成同一个：convertLogSeq.py。
 * log_dir/ 原始文件夹	
 * 	其中input\_dir参数是存储原始template seqs的dir文件夹，即将多个机器的原始模板序列存放在该文件夹中。
 *  output\_dir是统一模板号后的seqs文件夹。同时也会自动生成对应文件的全0的label文件，即使不做evaluation，也需要有个label文件作为输入。
 *  该脚本运行完之后会输出总的模板数量，需要记录下来，用于--event_num参数的输入。
 *  输出的"map.txt"是统一模板号之后，新模板号与原模板号的对应关系。
* 从**单一机器**的template sequence中学习invariants model：python main\_for\_invariants_mining.py --input\_type single --template log\_sequence.csv --label test.label
* 使用**多个机器**的日志学习统一模型：
	* python  main\_for\_invariants\_mining.py --input\_type multi --dir dir/
	* 如果想测试有异常的情况，可以将dir/替换成dir_back/，后者文件夹中存在的log seq有异常


####参数说明：
* --windows_size：时间窗口大小，默认是3小时 
* --step_size： 步长大小，默认是1小时 
* --template： template sequence的地址，**模板编号从1开始**，文件以"**,**"分隔(csv/txt文件)，样例数据的一行为”1117838571000,1,0“ 其中第一列为毫秒级时间戳，第二列为模板号(从1开始)，第三列为该条日志中变量数量，0表示没有参数.（若第三列为n,n>0，则后面需要再跟n列，依次是变量值，例如“1117838571000,1,1,1117838571”），**转换操作可以参考converLogSeq.py文件**。（针对于单一机器模型的参数）
* --label： template sequence对应的label，**如果只用于异常检测**，不做evaluation的话，此文件只需要是一个template sequence行数相等的文件，每行是0即可。（针对于单一机器模型的参数）
* --event_num： 模板数量，如果要用多个log seq来训练模型，一定要手动输入总模板的数量（针对于多个机器模型的参数）。
* --dir: 更新模板号后的template seq文件，格式与--template文件一样。（针对于多个机器模型的参数）
* --suffix： 是dir中seq文件的后缀名（针对于多个机器模型的参数）
* --result： 存放按时间窗口异常检测的结果的文件夹



#### 备注：
* **invariants即异常检测结果输出到了控制台中，如需保存，可以重定向输出**。
* threshold的定义【符合invariants规则的窗口数占所有非零窗口数的比例】
* 对非零元素的限制在algorithms.py，both_nonzero_min_support是两个都非零最少的窗口数，both_nonzero_min_fraction是两个都非零窗口数占至少一个非零窗口数的比例，两个限制是and关系
* template seq的序号是从1开始的
* 时间区间用dict{index:[logs]}时，一定要考虑滑动窗口，即可能多个窗口共享同一批日志，不能加break
<!--map.txt 统一后的序号
log_dir/ 原始文件夹-->
<!--dir/   要处理的文件夹，重新排序的全量seq-->


