from data_processing import data_processing
from build_note_matrix import buildmatrix
import numpy as np
from scipy.sparse import dok_matrix
from resolve_matrix import resolve_matrix
from sparse_matrix_solution import sparse_solution
#  'IEEE30BusSystemCDF.txt'


def PQ_resolve(num, path):
    bus_data, branch_data, base_P = data_processing(path)    #读取数据，a为母线数据，b为支路数据
    node_matrix = buildmatrix(path)       #调用函数建立节点导纳稀疏矩阵

    # 从节点导纳矩阵中分离不同类型节点对应的数据
    index3 = bus_data[:, 1] == 3   #平衡节点的行索引    均为bool值
    index2 = bus_data[:, 1] == 2   #PV节点的行索引
    index0 = bus_data[:, 1] == 0   #PQ节点的行索引
    #  获得不同类型节点在原矩阵中的索引
    ind0 = np.argwhere(index0)  #例：ind0为PQ节点在导纳矩阵中的行索引，为整型，其值为[2,3,5,6,8,9......]
    ind2 = np.argwhere(index2)
    ind3 = np.argwhere(index3)
    ind = np.concatenate((ind0, ind2, ind3), axis=0)    #ind储存按节点类型分类后，所形成的新矩阵的行对应的原矩阵行索引
    # 给定电压幅值和相角初始值，将PQ节点电压幅值和相角设为平衡节点的值，PV节点幅值设置为该节点最终电压，相角为平衡节点电压相角
    U0 = []
    for ii in range(len(bus_data)):
        if bus_data[ii, 1] == 0:
            U = bus_data[index3][0, 2]
        elif bus_data[ii, 1] == 2:
            U = bus_data[ii, 2]
        elif bus_data[ii, 1] == 3:
            U = bus_data[ii, 2]
        U0.append(U)
    U0 = np.array(U0).reshape(-1, 1)[ind].reshape(-1, 1)    #最终电压幅值初始值为一个列数组
    theta0 = []
    [theta0.append(bus_data[index3][0, 3]) for i in range(len(bus_data))]
    theta0 = np.array(theta0).reshape(-1, 1)    #最终电压相角初始值为一个列数组
    # 更新新导纳矩阵的索引    类型均为bool值########################################
    index3 = index3[ind][:, 0]  #平衡节点的索引
    index2 = index2[ind][:, 0]  #PV节点的索引
    index0 = index0[ind][:, 0]  #PQ节点的索引
    # 对原导纳矩阵排序 使得PQ PV 平衡节点分离，形成新导纳矩阵
    new_node_matrix = dok_matrix(node_matrix.shape, dtype=np.complex)
    for key, value in node_matrix.items():
        row = np.argwhere(ind == key[0])[:, 0]
        col = np.argwhere(ind == key[1])[:, 0]
        new_node_matrix[row, col] = value

    index = index0 + index2  # 获得待计算的△Pi/Ui的节点的索引

    # 建立B'和B''矩阵(B1对应B', B2对应B'')
    B1 = new_node_matrix[:sum(index), :sum(index)].imag
    B2 = new_node_matrix[:sum(index0), :sum(index0)].imag
    B1, diag1 = resolve_matrix(B1)
    B2, diag2 = resolve_matrix(B2)
    # 计算Pis和Qis
    P = (bus_data[:, 6] - bus_data[:, 4])[ind] / base_P
    Q = (bus_data[:, 13] - bus_data[:, 5])[ind] / base_P


    k1 = True  #用k1和k2控制循环是否结束，当两个均为False时，或迭代次数已达到指定值时结束循环
    k2 = True
    k = 0
    while k1 or k2:
        if k < num:
        # 计算△Pi/△Ui
            if k1:
                delta_P = []
                for i in range(len(bus_data)):
                    if index[i]:
                        bb = []
                        for j in range(len(bus_data)):
                            ang = theta0[i] - theta0[j]
                            bb.append((new_node_matrix[i, j].real * np.cos(ang * np.pi / 180) + new_node_matrix[i, j].imag * np.sin(
                                ang * np.pi / 180)) * U0[j, 0])
                        temp = P[i] - U0[i] * sum(bb)
                        delta_P.append(temp)
                delta_P = np.array(delta_P).reshape(-1, 1)   #将计算所得的△P转成列向量
                if max(np.abs(delta_P)) < 0.00001:  #给定收敛标准为0.00001,判断△P是否均已达到收敛标准
                    k1 = False                      #若△P满足收敛标准，则将k1置为False，若此时k2也为False则代表△P和△Q均已达到
                    if not k2:                      #收敛标准，可终止迭代并输出最终的U0和theta
                        break
                if k1:  #若k1为True，则需要计算相角变化量，即delta_theta
                    # 调用事先写好的函数，用稀疏矩阵求解法求解解修正方程
                    delta_theta = sparse_solution(B1, diag1, -delta_P/U0[index])/U0[index]*180/np.pi
                    # 更新电压相角
                    o = 0
                    for i in range(len(bus_data)):
                        if index[i]:
                            theta0[i] += delta_theta[o]
                            o += 1
                    k2 = True
            # 计算△Qi/△Ui
            if k2:  #若k2为True，则需要计算无功变化量
                #计算delta_Q
                delta_Q = []
                for i in range(len(bus_data)):
                    if index0[i]:
                        cc = []
                        for j in range(len(bus_data)):
                            ang = theta0[i] - theta0[j]
                            cc.append((new_node_matrix[i, j].real * np.sin(ang * np.pi / 180) - new_node_matrix[i, j].imag * np.cos(
                                ang * np.pi / 180)) * U0[j])
                        temp = Q[i] - sum(cc) * U0[i]
                        delta_Q.append(temp)
                delta_Q = np.array(delta_Q).reshape(-1, 1)  #将无功变化量转为列向量
                if max(np.abs(delta_Q)) < 0.00001:  #判断无功变化量delta_Q是否达到收敛标准
                    k2 = False  #若达到收敛标准，则将k2置为False，代表可不继续计算电压幅值
                    if not k1:  #若此时k1为False，则说明delta_P和delta_Q均已满足收敛标准，可终止迭代，并输出结果
                        break
                if k2:  #若k2为True,则需继续计算电压幅值变化量
                    #调用函数sparse_solution采用稀疏矩阵求解法求解delta_U
                    delta_U = sparse_solution(B2, diag2, -delta_Q / U0[index0])/U0[index0]
                    #更新电压幅值
                    l = 0
                    for i in range(len(U0)):
                        if index0[i]:
                            U0[i] = U0[i] + delta_U[l]
                            l += 1
                    k1 = True
            k += 1  #更新循环控制量
            print('第%s次PQ迭代完成' % k)
        else:
            break
    if not (k1 or k2):     #判断迭代终止的条件，情形一：delta_P和delta_Q均收敛，情形二：迭代次数已达到所给次数
        print('第%s次PQ迭代后，电压收敛,迭代终止。' % k)
        flag = False     #flag用于判断是否需要继续使用牛拉法迭代,若为False则不需要继续迭代
    else:
        print('经过%s次PQ迭代后，电压仍未收敛' % k)
        flag = True
    return U0, theta0, k, flag, new_node_matrix        #返回经迭代计算后的U0，theta0以及用以统计迭代次数的k
