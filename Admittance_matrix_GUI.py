import tkinter as tk
from build_note_matrix import buildmatrix
from matrix_modify import modify_matrix
import matrix_modify
import pandas


class GUI(tk.Tk):
# IEEE30BusSystemCDF.txt
    def __init__(self):
        super(GUI, self).__init__()
        self.all_node_matrix = []
        self.set_window()

    def set_window(self):
        self.iconbitmap('elect.ico')
        self.title('节点导纳矩阵的生成及修改')
        self.geometry('900x600+400+100')
        self.pathlb = tk.Label(self, text='文件路径', font=('微软雅黑', 14), width=15, heigh=2).grid(row=1, column=1)
        self.pathentry = tk.Entry(width=20, font=('微软雅黑', 14))
        self.pathentry.place(x=170, y=8)
        self.surepath = tk.Button(self, text='确认路径', width=10, heigh=2, command=self.get_path).place(x=450, y=7)
        self.stnode = tk.Label(self, text='起始节点', font=('微软雅黑', 14), width=10, heigh=2).grid(row=2, column=1)
        self.stentry = tk.Entry(width=10, font=('微软雅黑', 14))
        self.stentry.place(x=170, y=68)
        self.ednodes = tk.Label(self, text='末端节点', font=('微软雅黑', 14), width=10, heigh=2).place(x=300, y=55)
        self.edentry = tk.Entry(width=10, font=('微软雅黑', 14))
        self.edentry.place(x=420, y=68)
        self.klabel = tk.Label(self, text='变压器变比', font=('微软雅黑', 14), width=10, heigh=2).place(x=570, y=55)
        self.kentry = tk.Entry(width=10, font=('微软雅黑', 14))
        self.kentry.place(x=700, y=68)
        self.Rlabel = tk.Label(self, text='导线电阻', font=('微软雅黑', 14), width=10, heigh=2).grid(row=3, column=1)
        self.Rentry = tk.Entry(width=10, font=('微软雅黑', 14))
        self.Rentry.place(x=170, y=126)
        self.Xlabel = tk.Label(self, text='导线电抗', font=('微软雅黑', 14), width=10, heigh=2).place(x=300, y=113)
        self.Xentry = tk.Entry(width=10, font=('微软雅黑', 14))
        self.Xentry.place(x=420, y=126)
        self.Blabel = tk.Label(self, text='导线对地电纳', font=('微软雅黑', 14), width=10, heigh=2).place(x=570, y=113)
        self.Bentry = tk.Entry(width=10, font=('微软雅黑', 14))
        self.Bentry.place(x=700, y=126)
        self.sure_modify = tk.Button(self, text='确认修改', width=10, heigh=2, command=self.modify).place(x=410, y=175)
        self.old_lable = tk.Label(self, text='原始节点导纳矩阵', width=13, heigh=1, font=('微软雅黑', 14)).place(x=140, y=200)
        self.new_lable = tk.Label(self, text='修改后的节点导纳矩阵', width=15, heigh=1, font=('微软雅黑', 14)).place(x=600, y=200)
        self.old_disp = tk.Text(self, heigh=20, width=60)
        self.old_disp.place(x=15, y=230)
        self.new_disp = tk.Text(self, heigh=20, width=60)
        self.new_disp.place(x=460, y=230)
        self.save_button = tk.Button(self, text='保存数据', width=10, heigh=2, command=self.save_maxtrix).place(x=410, y=520)
        self.e = tk.StringVar()
        self.nodes_number = 0
        self.e.set(self.nodes_number)
        self.node_label = tk.Label(self, text='当前节点数目为', font=('微软雅黑', 14), width=15, heigh=2).place(x=560, y=1)
        self.node_entry =tk.Entry(self, textvariable=self.e, state='disable', width=5, font=('微软雅黑', 14), justify='left')
        self.node_entry.place(x=730, y=15)

    def get_path(self):   #在text中展示数据
        self.path = self.pathentry.get()
        node_matrix = buildmatrix(self.path)
        self.all_node_matrix.append(node_matrix)
        self.old_disp.insert('end', node_matrix.toarray())
        self.e.set(node_matrix.shape[0])



    def save_maxtrix(self):     #保存节点导纳矩阵
        if matrix_modify.num == 1:
            file_path = '原始导纳矩阵.xlsx'
        else:
            file_path = '第%s次修改后的矩阵.xlsx' % str(matrix_modify.num - 1)
        roww = self.all_node_matrix[-1].shape[0]
        index = []
        [index.append('%s号节点' % str(i+1)) for i in range(roww)]
        b = pandas.DataFrame(self.all_node_matrix[-1].toarray(), index=index, columns=index)
        r, c = b.shape
        for q in range(r):
            for p in range(c):
                b.iloc[q, p] = str(b.iloc[q, p]).strip('()')
        writer = pandas.ExcelWriter(file_path)
        b.to_excel(writer)
        writer.save()
        writer.close()


    def modify(self):        #展示增加节点后的节点导纳矩阵
        try:
            self.new_disp.delete('0.0', 'end')
        except Exception:
            pass
        start_node = self.stentry.get()
        end_nodes = self.edentry.get()
        R = self.Rentry.get()
        X = self.Xentry.get()
        B = self.Bentry.get()
        k = self.kentry.get()
        self.stentry.delete(0, 'end')
        self.edentry.delete(0, 'end')
        self.Rentry.delete(0, 'end')
        self.Xentry.delete(0, 'end')
        self.Bentry.delete(0, 'end')
        self.kentry.delete(0, 'end')
        if k == '':
            k = '1'
        if R == '':
            R = '1'
        if B == '':
            B = '1'
        if X == '':
            X = '1'
        data1, signal = modify_matrix(node_matrix=self.all_node_matrix[-1], start_node=start_node, end_nodes=end_nodes, R=R, X=X, B=B, k=k, path=self.path)
        self.e.set(data1.shape[0])
        if signal == True:
            self.all_node_matrix.append(data1)
            self.new_disp.insert('end', data1.toarray())
        else:
            self.new_disp.insert('end', '待删除支路不存在，修改节点导纳矩阵取消，请重新输入数据')



if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()