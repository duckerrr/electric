import numpy as np
import data_processing
from scipy.sparse import dok_matrix

def buildmatrix(path):
    bus_data, branch_data, base_P = data_processing.data_processing(path)  #读取数据
    a = int(max(bus_data[:, 0]))  #确定节点导纳矩阵的规格
    node_matrix = dok_matrix((a, a), dtype=np.complex)  #建立一个a行a列的dok_matrix空矩阵
    for line in branch_data:
        zk = np.complex(line[3], line[4])  # 读取电阻与电抗数据计算得到阻抗
        dn = -1 / zk  # 计算互导纳
        row = int(line[0]) - 1  # 计算该导纳所在的行
        col = int(line[1]) - 1  # 计算该导纳所在的列
        if line[2] == 0:        #不含变压器的支路
            node_matrix[col, row] = dn   #在计算所得的位置赋上导纳值
            node_matrix[row, col] = dn   #由节点导纳矩阵的对称性，在对称位置赋值
            node_matrix[row, row] += -dn + complex(0, line[5] / 2)      #更新对角元素值：-互导纳值+导纳/2
            node_matrix[col, col] += -dn + complex(0, line[5] / 2)
        elif line[2] == 2:      #含变压器的支路
            k = line[6]        #k为变比  归算到变比为1的一侧
            node_matrix[col, row] = dn * k  # 在计算所得的位置赋上导纳值
            node_matrix[row, col] = dn * k  # 由节点导纳矩阵的对称性，在对称位置赋值
            node_matrix[row, row] += -dn + complex(0, line[5] / 2)
            node_matrix[col, col] += -dn * k ** 2 + complex(0, line[5] / 2)
    for j in range(a):      #考虑节点并联导纳后，对节点导纳矩阵对角元素进行更新
        node_matrix[j, j] += complex(bus_data[j, 11], bus_data[j, 12])
    return node_matrix

