from scipy.optimize import minimize
from build_note_matrix import buildmatrix
import numpy as np
from data_processing import data_processing
import pandas as pd

#从文件中读取数据
path0 = input('请输入母线数据文件路径')
path1 = input('请输入节点约束数据文件路径')
F_data = []
limit_data = []
fl = open(path1, 'r')
lines = fl.readlines()
flag1 = False
flag2 = False
for line in lines:
    if 'F_data' in line:
        flag1 = True
        continue
    if 'limit_data' in line:
        flag2 = True
        continue
    if line.strip() == '-999':
        flag1 = False
        flag2 = False
    if flag1:
        temp = (int(line[0:3].strip()), float(line[3:8].strip()), float(line[8:15].strip()), float(line[17:25].strip()))
        F_data.append(temp)
    if flag2:
        temp = (int(line[0:3].strip()), float(line[4:9].strip()), float(line[11:17].strip()), float(line[18:23].strip()), float(line[25:29].strip()))
        limit_data.append(temp)
F_data = np.array(F_data)       #将数据转为ndarray形式储存
limit_data = np.array(limit_data)       #将约束范围以ndarray形式储存
limit_data = limit_data[np.argsort(limit_data[:, 0])]
bus_data, _, base_P = data_processing(path0)    #调用程序得到母线数据和基准功率
node_matrix = buildmatrix(path0)        #调用程序得到节点导纳矩阵
data_row = len(F_data)
bus_row = len(bus_data)
cons = ()

#未知数排列为PG（1-k),Q(1-k),U(1-n),theta(1-n),即x的0-k为发电机有功出力， k-2k为无功，2k+1-2k+n为电压幅值，2k+n+1-2k+2n为电压相角
#构建目标函数
def fun(x):
    F = 0
    for i in range(data_row):
        for j in range(F_data.shape[1]-1):
            F += F_data[i, j+1] * x[int(F_data[i, 0]-1)] ** j
    return F

#用于计算  Vi∑Vj(Gij*cos(θ) + Bij*sin(θ))
def cal_P(x, start):
    summ = 0
    P_i = start
    x_i = int(2*data_row+bus_row+P_i-1)
    for j in range(bus_row):
        x_j = int(2 * data_row + bus_row + j)
        ang = x[x_i] - x[x_j]
        summ += x[2*data_row+j]*(node_matrix[P_i-1, j].real*np.cos(ang*np.pi/180) + node_matrix[P_i-1, j].imag*np.sin(ang*np.pi/180))
    summ = summ * x[int(2*data_row+P_i-1)]
    return summ

#用于计算  Vi∑Vj(Gij*sin(θ) - Bij*cos(θ))
def cal_Q(x, start):
    summ = 0
    Q_i = start
    x_i = int(2 * data_row + bus_row + Q_i - 1)
    for j in range(bus_row):
        x_j = int(2 * data_row + bus_row + j)
        ang = x[x_i] - x[x_j]
        summ += x[2 * data_row + j] * (node_matrix[Q_i - 1, j].real * np.sin(ang * np.pi / 180) - node_matrix[Q_i - 1, j].imag * np.cos(ang * np.pi / 180))
    summ = summ * x[int(2 * data_row + Q_i - 1)]
    return summ


for i in range(data_row):  #发电机有功约束
    temp_dict1 = {}
    temp_dict2 = {}
    index = np.argwhere(limit_data[:, 0] == F_data[i, 0])[0][0]     #得到发电机节点编号在约束数据中的行索引
    temp_dict1['type'] = 'ineq'
    temp_dict1['fun'] = lambda x, i = i, index = index: x[int(F_data[i, 0]-1)] - limit_data[index, 1]
    temp_dict2['type'] = 'ineq'
    temp_dict2['fun'] = lambda x, i = i, index = index: -x[int(F_data[i, 0]-1)] + limit_data[index, 2]
    cons = (*cons, temp_dict1, temp_dict2)

for i in range(data_row):  #发电机无功约束
    temp_dict1 = {}
    temp_dict2 = {}
    temp_dict1['type'] = 'ineq'
    temp_dict1['fun'] = lambda x, i = i: x[int(data_row+F_data[i, 0]-1)] - bus_data[i, 10]/base_P
    temp_dict2['type'] = 'ineq'
    temp_dict2['fun'] = lambda x, i = i: -x[int(data_row+F_data[i, 0]-1)] + bus_data[i, 9]/base_P
    cons = (*cons, temp_dict1, temp_dict2)

for i in range(bus_row):  #所有节点的电压不等式约束
    temp_dict1 = {}
    temp_dict2 = {}
    index = np.argwhere(limit_data[:, 0] == i + 1)[0][0]        #得到发电机节点编号在约束数据中的行索引
    temp_dict1['type'] = 'ineq'
    temp_dict1['fun'] = lambda x, i = i, index = index: x[int(data_row*2+i)] - limit_data[index, 3]
    temp_dict2['type'] = 'ineq'
    temp_dict2['fun'] = lambda x, i = i, index = index: -x[int(data_row*2+i)] + limit_data[index, 4]
    cons = (*cons, temp_dict1, temp_dict2)

for i in range(data_row):  #所有发电机的等式约束
    temp_dict1 = {}
    temp_dict2 = {}
    temp_dict1['type'] = 'eq'
    temp_dict1['fun'] = lambda x, i=i: x[int(F_data[i, 0]-1)] - bus_data[np.argwhere(bus_data[:, 0] == F_data[i, 0])[0][0], 4]/base_P - cal_P(x, F_data[i, 0])
    temp_dict2['type'] = 'eq'
    temp_dict2['fun'] = lambda x, i=i: x[int(F_data[i, 0]+data_row-1)] - bus_data[np.argwhere(bus_data[:, 0] == F_data[i, 0])[0][0], 5]/base_P + cal_Q(x, F_data[i, 0])
    cons = (*cons, temp_dict1, temp_dict2)

#获得非发电机节点的节点编号
node = bus_data[:, 0]
for i in F_data[:, 0]:
    node = np.delete(node, np.argwhere(node == i)[0][0])

for i in node:   #非发电机节点的等式约束
    temp_dict1 = {}
    temp_dict2 = {}
    temp_dict1['type'] = 'eq'
    temp_dict1['fun'] = lambda x, i=i: bus_data[np.argwhere(bus_data[:, 0] == i)[0][0], 4]/base_P + cal_P(x, i)
    temp_dict2['type'] = 'eq'
    temp_dict2['fun'] = lambda x, i=i: bus_data[np.argwhere(bus_data[:, 0] == i)[0][0], 5]/base_P - cal_Q(x, i)
    cons = (*cons, temp_dict1, temp_dict2)

x0 = np.ones(2*bus_row+2*data_row).reshape(1, -1)
res = minimize(fun, x0, method='SLSQP', constraints=cons)
#便于更直接地展示结果，将不同数据数据分离，以excel格式储存
PG = res.x[0:data_row]
Q = res.x[data_row:data_row*2]
U = res.x[data_row*2:data_row*2+bus_row]
theta = res.x[-bus_row:]
columns1 = ['%s号节点' % str(int(i)) for i in F_data[:, 0]]
P_U = pd.DataFrame([PG, Q], index=['PG', 'Q'], columns=columns1)
columns2 = ['%s号节点' % str(i+1) for i in range(bus_row)]
U_theta = pd.DataFrame([U, theta], index=['U', 'θ'], columns=columns2)
path = '火电厂负荷经济分配结果.xlsx'
writer = pd.ExcelWriter(path)
P_U.to_excel(writer, '有功和无功出力')
U_theta.to_excel(writer, '节点电压幅值与相角')
writer.save()
writer.close()
