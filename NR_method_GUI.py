import tkinter as tk
from PQ_sparse_resolve import PQ_resolve
import pandas as pd
from NR_method import NR_method


def butt1():        #从entry1中获取输入的文件地址
    global path
    path = entry1.get()

def butt2():        #在text1中展示最终的电压幅值及相角
    try:
        text1.delete('0.0', 'end')
    except Exception:
        pass
    num = entry2.get()
    U0, theta0, PQ_k, flag, new_node_matrix = PQ_resolve(int(num), path)
    number.append(PQ_k)
    # U_lasted = NR_method(U0, theta0)
    U_lasted, NR_k = NR_method(U0, theta0, path, flag, new_node_matrix)
    U_data.append(U_lasted)
    text1.insert('end', U_lasted)
    e.set(NR_k)

def save_data():        #将最终得到的电压幅值及相角以excel格式保存
    path0 = 'PQ迭代%s次.xlsx' % number[-1]
    writer = pd.ExcelWriter(path0)
    U_data[-1].to_excel(writer)
    writer.save()
    writer.close()

NR_k = 0
pd.set_option('display.max_columns', 500)       #设置使DataFrame完整输出
U_data = []
number = []
window = tk.Tk()
window.iconbitmap('elect.ico')
window.title('牛顿——拉夫逊——PQ分解算法')
window.geometry('900x600+350+100')
e = tk.StringVar()
e.set(NR_k)
label1 = tk.Label(window, text='文件路径', font=('微软雅黑', 14), width=10, heigh=2).grid(row=1, column=2)
entry1 = tk.Entry(window, width=25, font=('微软雅黑', 14))
entry1.grid(row=1, column=3)
button1 = tk.Button(window, text='确定', width=10, font=('微软雅黑', 14), command=butt1).place(x=500, y=15)
label2 = tk.Label(window, text='使用PQ分解法迭代', width=15, font=('微软雅黑', 14)).place(x=10, y=80)
entry2 = tk.Entry(window, width=5, font=('微软雅黑', 14))
entry2.place(x=190, y=80)
label3 = tk.Label(window, text='次,获得初值后再使用牛拉法进行迭代', font=('微软雅黑', 14)).place(x=220, y=80)
entry3 = tk.Entry(window, textvariable=e, state='disable', width=5, font=('微软雅黑', 14), justify='left')
entry3.place(x=540, y=80)
label4 = tk.Label(window, text='次后数据收敛', width=15, font=('微软雅黑', 14), justify='left').place(x=560, y=80)
button2 = tk.Button(window, text='确定', width=10, font=('微软雅黑', 14), command=butt2).place(x=720, y=70)
text1 = tk.Text(window, heigh=15, width=79, font=('微软雅黑', 14))
text1.place(x=10, y=120)
button3 = tk.Button(window, text='保存数据', font=('微软雅黑', 14), width=10, command=save_data).place(x=400, y=520)
window.mainloop()