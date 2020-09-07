from data_processing import data_processing
import numpy as np
from scipy.sparse import dok_matrix
import pandas as pd


def NR_method(U0, theta0, path, flag, new_node_matrix):
    bus_data, branch_data, base_P = data_processing(path)  # 读取数据
    # node_matrix = buildmatrix(path)  # 建立节点导纳矩阵

    # 从节点导纳矩阵中分离不同类型节点对应的数据
    index3 = bus_data[:, 1] == 3  # 平衡节点的行索引    均为bool值
    index2 = bus_data[:, 1] == 2  # PV节点的行索引
    index0 = bus_data[:, 1] == 0  # PQ节点的行索引
    #  获得不同类型节点在原矩阵中的索引
    ind0 = np.argwhere(index0)  ##例：ind0为PQ节点在导纳矩阵中的行索引，为整型，其值为[2,3,5,6,8,9......]
    ind2 = np.argwhere(index2)
    ind3 = np.argwhere(index3)
    ind = np.concatenate((ind0, ind2, ind3), axis=0)  # ind储存按节点类型分类后，新数据在原数据中的索引

    # 更新新导纳矩阵的索引  bool值，用于统计PQ、PV平衡节点个数
    index3 = index3[ind][:, 0]  # 平衡节点的索引
    index2 = index2[ind][:, 0]  # PV节点的索引
    index0 = index0[ind][:, 0]  # PQ节点的索引

    index = index0 + index2  # 需计算的△Pi/Ui的节点的索引
    PQPV_sum = sum(index)  # 计算PQ和PV节点的总数目，用于创建Jacobian矩阵
    PQ_sum = sum(index0)  # 计算PQ节点的数目，用于创建Jacobian矩阵

    # 计算Pis和Qis
    P = (bus_data[:, 6] - bus_data[:, 4])[ind] / base_P
    Q = (bus_data[:, 13] - bus_data[:, 5])[ind] / base_P
    k = 0  # k用于统计迭代次数
    if flag:
        while True:  # 开始进行迭代
            # 计算△P
            delta_P = []
            Pi = []
            for i in range(len(bus_data)):
                if index[i]:
                    bb = []
                    for j in range(len(bus_data)):
                        ang = theta0[i] - theta0[j]
                        bb.append((new_node_matrix[i, j].real * np.cos(ang * np.pi / 180) + new_node_matrix[i, j].imag * np.sin(
                            ang * np.pi / 180)) * U0[j, 0])
                    temp = P[i] - U0[i] * sum(bb)
                    Pi.append(U0[i] * sum(bb))
                    delta_P.append(temp)
            Pi = np.array(Pi).reshape(-1, 1)  # 保存Pi，用于计算Jacobian矩阵元素值
            delta_P = np.array(delta_P).reshape(-1, 1)
            # 计算△Q
            delta_Q = []
            Qi = []
            for i in range(len(bus_data)):
                if index0[i]:
                    cc = []
                    for j in range(len(bus_data)):
                        ang = theta0[i] - theta0[j]
                        cc.append((new_node_matrix[i, j].real * np.sin(ang * np.pi / 180) - new_node_matrix[i, j].imag * np.cos(
                            ang * np.pi / 180)) * U0[j])
                    temp = Q[i] - sum(cc) * U0[i]
                    Qi.append(sum(cc) * U0[i])
                    delta_Q.append(temp)
            [Qi.append(0) for i in range(PQPV_sum - PQ_sum)]
            Qi = np.array(Qi).reshape(-1, 1)  # 保存Qi，用于建立Jacobian矩阵
            delta_Q = np.array(delta_Q).reshape(-1, 1)
            # 建立Jacobian矩阵
            J = dok_matrix((PQPV_sum + PQ_sum, PQPV_sum + PQ_sum))
            # 建立H矩阵
            for i in range(PQPV_sum):
                for j in range(PQPV_sum):
                    ang = (theta0[i] - theta0[j]) * np.pi / 180
                    if i != j:
                        J[i, j] = -U0[i] * U0[j] * (new_node_matrix[i, j].real * np.sin(ang) -
                                                    new_node_matrix[i, j].imag * np.cos(ang))
                    else:
                        J[i, i] = pow(U0[i], 2) * new_node_matrix[i, i].imag + Qi[i, 0]
            # 建立N矩阵
            for i in range(PQPV_sum):
                for j in range(PQ_sum):
                    ang = theta0[i] - theta0[j]
                    if i != j:
                        J[i, j + PQPV_sum] = -U0[i] * U0[j] * (new_node_matrix[i, j].real * np.cos(ang * np.pi / 180) +
                                                               new_node_matrix[i, j].imag * np.sin(ang * np.pi / 180))
                    else:
                        J[i, i + PQPV_sum] = -pow(U0[i], 2) * new_node_matrix[i, i].real - Pi[i, 0]
            # 建立K矩阵
            for i in range(PQ_sum):
                for j in range(PQPV_sum):
                    ang = theta0[i] - theta0[j]
                    if i != j:
                        J[i + PQPV_sum, j] = U0[i] * U0[j] * (new_node_matrix[i, j].real * np.cos(ang * np.pi / 180) +
                                                              new_node_matrix[i, j].imag * np.sin(ang * np.pi / 180))
                    else:
                        J[i + PQPV_sum, i] = pow(U0[i], 2) * new_node_matrix[i, i].real - Pi[i, 0]
            # 建立L矩阵
            for i in range(PQ_sum):
                for j in range(PQ_sum):
                    ang = theta0[i] - theta0[j]
                    if i != j:
                        J[i + PQPV_sum, j + PQPV_sum] = -U0[i] * U0[j] * (new_node_matrix[i, j].real * np.sin(ang * np.pi / 180) -
                                                                          new_node_matrix[i, j].imag * np.cos(ang * np.pi / 180))
                    else:
                        J[i + PQPV_sum, i + PQPV_sum] = pow(U0[i], 2) * new_node_matrix[i, i].imag - Qi[i, 0]

            delta_PQ = np.append(delta_P, delta_Q, axis=0)
            soulu = np.dot(-np.linalg.inv(J.toarray()), delta_PQ)  # 解修正方程
            delta_UU = (np.diag(U0[:PQ_sum]) * soulu[PQPV_sum:, 0]).reshape(-1, 1)
            delta_thetaa = (soulu[:PQPV_sum, 0] * 180 / np.pi).reshape(-1, 1)
            # 更新电压幅值和相角
            U0[:PQ_sum] += delta_UU
            theta0[:PQPV_sum] += delta_thetaa
            k += 1
            if max(abs(np.concatenate(
                    (delta_P, delta_Q, delta_UU)))) < 1e-5:  # 将收敛标准定为0.00001，若delta_P,delta_Q和 delta_UU均达到收敛标准，则结束迭代并输出结果
                break
            print('第%s次牛拉法迭代完成' % k)
        print('迭代%s次后数据达到收敛标准' % k)
    node_ID = []
    [node_ID.append('%s号节点' % str(i)) for i in range(1, new_node_matrix.shape[0] + 1)]
    U_lasted = pd.DataFrame(columns=node_ID, index=['电压标幺值', '电压/KV', '相角/°'])
    j = 0
    for i in ind:  # 按照节点原编号对数据进行还原(即按降序对节点编号进行排列)
        U_lasted.iloc[0, i] = U0[j]  # 保存电压标幺值
        U_lasted.iloc[1, i] = U0[j] * bus_data[i, 7]  # 将节点电压标幺值转为有名值并保存
        U_lasted.iloc[2, i] = theta0[j]
        j += 1
    return U_lasted, k  # 返回一个DataFrame的数据，内容为所有节点对应的电压幅值及相角

