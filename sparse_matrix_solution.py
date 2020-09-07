def sparse_solution(umatrix, diag, sol):   #umatrix为上三角矩阵，diag为由因子表分解所得的对角线元素值的列表，sol为节点对应的点位
    lmatrix = umatrix.T       #为上三角矩阵转为下三角矩阵
    # 前代计算
    for i in range(lmatrix.shape[1]):
        if lmatrix[i, i] != 0:     #若第i个节点的点位为0，则对相关节点点位无影响,不需计算
            key_list = []    #用于储存需要进行计算的元素所在的行索引
            for key in lmatrix[:, i].keys():
                if key[0] > i:
                    key_list.append(key[0])     #节点点位只直接影响以此节点为起点的终点点位
            for col in key_list:
                sol[col, 0] -= sol[i, 0] * lmatrix[col, i]      #更新节点点位
    # 规格化计算
    for j in range(sol.shape[0]):       #新点位为当前各点点位除以相应自边边权
        sol[j, 0] /= diag[j]
    # 回代计算
    for k in range(umatrix.shape[1])[::-1]:     #回代从编号最大的节点开始
        if umatrix[k, k] != 0:      #若改节点点位为0，则不需计算
            key_list = []
            for key in umatrix[:, k].keys():        #某节点点位只直接影响以此节点为终点节点点位
                if key[0] < k:
                    key_list.append(key[0])
            for col in key_list:        #更新节点点位，最终节点点位即为方程组的解
                sol[col, 0] -= sol[k, 0] * umatrix[col, k]
    return sol

