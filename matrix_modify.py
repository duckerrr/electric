import numpy as np
from scipy.sparse import dok_matrix
from data_processing import data_processing

num = 1     #用于统计节点导纳矩阵修改次数

def modify_matrix(node_matrix, start_node, end_nodes, R, X, B, k, path):
    bus_data, branch_data, _ = data_processing(path=path)
    global num, new_matrix
    np.set_printoptions(threshold=np.inf)       #使矩阵完整输出
    #处理输入的节点编号及其对应的电阻，电抗，节点编号转为整型，电阻和电抗转成浮点类型
    row, col = node_matrix.shape
    start_node = process(start_node)      #调用process函数将数据分隔并以列表形式储存
    end_nodes = process(end_nodes)
    R = process(R)
    X = process(X)
    B = process(B)
    k = process(k)
    temp = []
    message = None
    [temp.append(abs(int(i))) for i in end_nodes]
    end_nodes_temp = temp        #将end_nodes转换成正整数临时使用
    max_node = int(max(end_nodes_temp))      #得到最大的节点编号，用于确定修改后的矩阵规格
    node1 = branch_data[branch_data[:, 2] == 2, 0]      #获取存在变压器的支路的一端节点编号
    node2 = branch_data[branch_data[:, 2] == 2, 1]      #获取存在变压器的支路的二端节点编号
    nodek = branch_data[branch_data[:, 2] == 2, 6]      #获取存在变压器的支路的变压器变比
    nodeB = branch_data[branch_data[:, 2] == 2, 5]      #获取存在变压器的支路的电纳
    transfer_branch = list(zip(node1, node2))       #用于储存含变压器的支路的两个端点节点编号
    signal = True  #用于判断修改是否成功
    for i in range(len(end_nodes)):
        if max_node > node_matrix.shape[0]:     #以新的矩阵尺寸建立矩阵并在相应位置赋上原矩阵的值
            new_matrix = dok_matrix((max_node, max_node), dtype=np.complex)
            new_matrix[:row, :row] = node_matrix
        else:
            new_matrix = node_matrix.copy()
        flag1 = (not k[i] == str(1)) and (not k[i] == str(0))      #判断新增支路是否含有变压器。若有，则将flag1置为True
        flag2 = (int(start_node[0]), abs(int(end_nodes[i]))) in transfer_branch or (abs(int(end_nodes[i])), int(start_node[0])) in transfer_branch
        if flag1:       #处理待增加支路含有变压器的情况
            new_matrix = add_transfer_branch(new_matrix, start_node[0], end_nodes[i], R[i], X[i], B[i], k[i])
        elif flag2:     #处理待删除支路含有变压器的情况
            new_matrix = reduce_transfer_branch(new_matrix, start_node[0], end_nodes[i], node1, node2, nodeB, nodek)
        else:           #若变化的支路中不含变压器，则调用no_transfer_branch函数
            new_matrix, signal = no_transfer_branch(new_matrix, start_node[0], end_nodes[i], R[i], X[i], B[i], branch_data)
            if signal == False:
                return node_matrix, signal
    num += 1
    return new_matrix, signal

def process(data):
    try:
        data = data.split()
        data = ','.join(data)
        return data.split(',')
    except:
        pass

def no_transfer_branch(new_matrix, start_node, end_node, R, X, B, branch_data):      #用于处理变化的支路中不含变压器时，节点导纳矩阵的变化
    branch_list = list(zip(branch_data[:, 0], branch_data[:, 1]))
    row = int(start_node) - 1
    col = abs(int(end_node)) - 1
    signal = True      #若signal为True，则表示存在待删减的支路，否则不存在
    if int(end_node) < 0:       #判断增加支路还是删减支路
        if new_matrix[row, col] == 0:       #若为删减支路，则判断是否存在该支路，若不存在，则结束函数
            signal = False
            return new_matrix, signal
        else:
            try:        #计算待删去支路在branch_data中的行索引，以便获得该支路的电纳值
                branch_index = branch_list.index((int(start_node), abs(int(end_node))))
            except:
                branch_index = branch_list.index((abs(int(end_node)), (int(start_node))))
            new_matrix[row, row] += new_matrix[row, col] - complex(0, branch_data[branch_index, 5])
            new_matrix[col, col] += new_matrix[row, col] - complex(0, branch_data[branch_index, 5])
            new_matrix[row, col] = new_matrix[col, row] = 0
    else:       #增加支路
        dn = 1 / complex(float(R), float(X))
        new_matrix[row, row] += dn + complex(0, float(B) / 2)
        new_matrix[col, col] += dn + complex(0, float(B) / 2)
        new_matrix[row, col] -= dn
        new_matrix[col, row] -= dn
    return new_matrix, signal


def add_transfer_branch(new_matrix, start_node, end_node, R, X, B, k):      #用于处理新增的支路中含有变压器时，节点导纳矩阵的变化
    dn = -1/complex(float(R), float(X))
    row = int(start_node) - 1
    col = abs(int(end_node)) - 1
    new_matrix[col, row] = dn * float(k)  # 在计算所得的位置赋上导纳值
    new_matrix[row, col] = dn * float(k)  # 由节点导纳矩阵的对称性，在对称位置赋值
    new_matrix[row, row] += -dn + complex(0, float(B) / 2)
    new_matrix[col, col] += -dn * float(k) ** 2 + complex(0, float(B) / 2)
    return new_matrix

#用于处理删减的支路中含有变压器时，节点导纳矩阵的变化
def reduce_transfer_branch(new_matrix, start_node, end_node, node1, node2, nodeB, nodek):
    nodes_list = list(zip(node1, node2))       #将存在变压器的支路的一端和二端节点编号以元组形式合并，并存储在列表里
    temp_index = nodes_list.index((int(start_node), abs(int(end_node))))
    tempB = nodeB[temp_index]
    tempk = nodek[temp_index]
    row = node1[temp_index]
    col = node2[temp_index]
    new_matrix[col, col] += new_matrix[row, col]*tempk - complex(0, tempB/2)
    new_matrix[row, row] -= complex(0, tempB/2)
    new_matrix[row, col] = 0
    new_matrix[col, row] = 0
    return new_matrix

