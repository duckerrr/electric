import numpy as np


def data_processing(path):
    fl = open(path, 'r')  # 打开文件
    lines = fl.readlines()  # 按行读取文件
    bus_data = []  # 创建两个列表分别存储母线数据和支路数据
    branch_data = []
    flag1 = False  # 用两个bool类型的变量控制数据的读取  为True时代表读取，为False时代表不读取
    flag2 = False
    row_number = 0  #行数
    for line in lines:
        if row_number == 0:
            try:
                base_P = float(line[31:36])   #基准功率
            except Exception as e:
                base_P = None
                print(e)
            finally:
                row_number += 1
        if 'BUS DATA FOLLOWS' in line:  # 当行内出现'BUS DATA FOLLOWS'时将flag1置为True，从下一行开始读取
            flag1 = True
            continue
        elif line.strip() == '-999':  # 出现-999时表示一种类型数据读取完毕，将两个flag均置为False
            flag1 = False
            flag2 = False

        if flag1:
            temp_list = []
            temp_list.append(int(line[0:4].strip(' ')))   #第一个数据为母线号
            temp_list.append(int(line[25:26].strip(' ')))      #第二个数据为节点类型
            temp_list.append(float(line[27:32].strip(' ')))     #第三个数据为最终电压幅值
            temp_list.append(float(line[33:39].strip(' ')))     #第四个数据为电压最终相角
            temp_list.append(float(line[40:48].strip(' ')))     #第五个数据为有功负荷
            temp_list.append(float(line[49:58].strip(' ')))     #第六个数据为无功负荷
            temp_list.append(float(line[59:67].strip(' ')))     #第七个数据为发出有功
            temp_list.append(float(line[76:82].strip(' ')))     #第八个数据为基准电压
            temp_list.append(float(line[84:89].strip(' ')))     #第九个数据为期望电压
            temp_list.append(float(line[90:97].strip(' ')))     #第十个数据为最大无功或电压限制
            temp_list.append(float(line[98:105].strip(' ')))    #第十一个数据为最小无功
            temp_list.append(float(line[106:113].strip(' ')))   #第十二个数据为节点并联电导
            temp_list.append(float(line[114:121].strip(' ')))   #第十三个数据为并联电纳
            temp_list.append(float(line[67:76].strip(' ')))     #第十四个数据为发出无功
            bus_data.append(temp_list)

        if 'BRANCH DATA FOLLOWS' in line:  # 若行内出现'BRANCH DATA FOLLOWS'则从下一行开始读取数据
            flag2 = True
            continue
        if flag2:
            temp_list = []
            temp_list.append(int(line[0:4].strip(' ')))     #第一个数据为一端编号
            temp_list.append(int(line[5:9].strip(' ')))     #第二个数据为二端编号
            temp_list.append(int(line[18].strip(' ')))      #第三个数据为支路类型
            temp_list.append(float(line[19:28].strip(' '))) #第四个数据为电阻R
            temp_list.append(float(line[29:38].strip(' '))) #第五个数据为电抗X
            temp_list.append(float(line[40:50].strip(' '))) #第六个数据为电纳B
            temp_list.append(float(line[76:82].strip(' '))) #第七个数据为变压器最后变比
            branch_data.append(temp_list)
    np.set_printoptions(suppress=True)  # 取消数据的科学计数法表达
    bus_data = np.array(bus_data)
    branch_data = np.array(branch_data)
    # 根据母线数据的节点编号按升序对节点进行排列
    bus_data = bus_data[np.argsort(bus_data[:, 0])]
    # str_nddata1和str_nddata2为读取的数据，为字符串类型，需将其转成浮点数类型，并以ndarray类型储存
    fl.close()
    return bus_data, branch_data, base_P

