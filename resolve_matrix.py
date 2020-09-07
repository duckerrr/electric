from scipy.sparse import dok_matrix, triu


def resolve_matrix(matrix_UP):
    matrix_UP = triu(dok_matrix(matrix_UP), format='dok')   #将需要进行因子表分解的稀疏矩阵变为上三角矩阵(列索引大于行索引)
    diag = []  #用于储存最后的对角矩阵的对角线元素
    for i in range(matrix_UP.shape[0]):
        diag.append(matrix_UP[i, i])
        key_list = []
        for key in matrix_UP[i].keys():   #保存第i行中需要进行消去计算的元素所在列的索引
            col = key[1]
            if col > i:
                key_list.append(col)
        matrix_UP[i, i + 1:] /= matrix_UP[i, i]  # 对第i行的元素进行规格化计算
        if i != matrix_UP.shape[0]-1:   #对除最后一行外的需消去计算的元素进行消去计算
            for col1 in key_list:
                for col2 in key_list:
                    if col2 >= col1:
                        matrix_UP[col1, col2] = matrix_UP[col1, col2] - \
                                                matrix_UP[i, col1] * matrix_UP[i, col2] * matrix_UP[i, i]
        matrix_UP[i, i] = 1     #将对角线元素赋值为1
    return matrix_UP, diag